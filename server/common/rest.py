from flask_apispec import Ref as BaseRef
from flask_apispec.views import MethodResource
from flask_restful import Resource as RestfulResource
from marshmallow import Schema
from sqlalchemy.orm import Session

from common.util import marshal_with, use_kwargs, transactional, autodoc


class Ref(BaseRef):
    def __init__(self, key, *args, **kwargs):
        super(Ref, self).__init__(key)
        self.args = args
        self.kwargs = kwargs

    def resolve(self, obj):
        resolved = super(Ref, self).resolve(obj)
        if issubclass(resolved, Schema):
            if self.args or self.kwargs:
                return resolved(*self.args, **self.kwargs)
        return resolved


class Resource(MethodResource, RestfulResource):
    def __init_subclass__(cls, **kwargs):
        return autodoc(cls)


class BasicCollectionResource(Resource):
    schema = None
    model = None
    db_session = None  # type: Session

    @marshal_with(Ref('schema', many=True), code=200)
    def get(self):
        return self.model.query.all()

    @use_kwargs(Ref('schema'))
    @marshal_with(Ref('schema', many=True), code=201)
    @transactional(db_session)
    def post(self, *, _transaction, **kwargs):
        obj = self.model(**kwargs)
        _transaction.session.add(obj)


class BasicResource(Resource):
    schema = None
    model = None
    db_session = None  # type: Session

    @marshal_with(Ref('schema'), code=200)
    def get(self, *args):
        return self.model.query.get_or_404(args)

    @use_kwargs(Ref('schema', partial=True))
    @marshal_with(Ref('schema'), code=200)
    @transactional(db_session)
    def patch(self, *args, _transaction, **kwargs):
        obj = self.model.query.get_or_404(args)
        obj.__dict__.update(**kwargs)
        return obj, 200

    # @use_kwargs(Ref('schema'))
    # @marshal_with(Ref('schema'), code=200)
    # @marshal_with(Ref('schema'), code=201)
    # @transactional(db_session)
    # def put(self, *args, _transaction, **kwargs):
    #     obj = self.model.query.get(args)
    #     if obj:
    #         obj.__dict__.update(**kwargs)
    #         return obj, 200
    #     else:
    #         obj = self.model(**kwargs)
    #         _transaction.session.add(obj)
    #         return obj, 201

    @marshal_with(None, code=204)
    @transactional(db_session)
    def delete(self, *args, _transaction):
        obj = self.model.query.get_or_404(args)
        _transaction.session.delete(obj)
        return {}, 204
