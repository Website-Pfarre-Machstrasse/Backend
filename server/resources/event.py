from datetime import datetime, date, timedelta
from typing import Union

from flask_apispec import marshal_with, use_kwargs
from flask_jwt_extended import jwt_required, get_current_user
from marshmallow import fields

from common.database import db
from common.rest import Resource
from common.util import ServerError
from server.common.database import Event as EventModel


class Events(Resource):
    method_decorators = {'post': [jwt_required]}

    @use_kwargs({'start': fields.DateTime(required=False),
                 'end': fields.DateTime(required=False)}, location='query')
    @marshal_with(EventModel.__marshmallow__(many=True))
    def get(self, start: Union[datetime, None] = None, end: Union[datetime, None] = None):
        filters = []
        if not start:
            start = datetime.now()
        filters.append(EventModel.start > start)
        if not end:
            now = datetime.now()
            year, month = divmod(now.month + 1, 12)
            if month == 0:
                month = 12
                year = year - 1
            end = now.replace(year=now.year + year, month=month)
        filters.append(EventModel.end < end)
        return EventModel.query.filter(*filters).all()

    @use_kwargs(EventModel.__marshmallow__)
    @marshal_with(EventModel.__marshmallow__, code=201)
    def post(self, **kwargs):
        event = EventModel(**kwargs)
        event.author = get_current_user().id
        try:
            db.session.add(event)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return event, 201


class Event(Resource):
    method_decorators = {'put': [jwt_required], 'delete': [jwt_required]}

    @marshal_with(EventModel.__marshmallow__, code=200)
    def get(self, event_id):
        return EventModel.query.get_or_404(event_id)

    @use_kwargs(EventModel.__marshmallow__(partial=True))
    @marshal_with(EventModel.__marshmallow__, code=200)
    def put(self, event_id, **kwargs):
        event = EventModel.query.get_or_404(event_id)
        try:
            event.__dict__.update(kwargs)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return event

    @marshal_with(None, code=204)
    def delete(self, event_id):
        event = EventModel.query.get_or_404(event_id)
        try:
            db.session.delete(event)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return {}, 204
