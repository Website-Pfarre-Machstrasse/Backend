from datetime import datetime
from typing import Union

from flask_apispec import use_kwargs
from flask_jwt_extended import get_current_user
from marshmallow import fields

from common.database import db
from common.rest import Resource
from common.schema import EventSchema
from common.util import ServerError
from common.util.decorators import tag, marshal_with, jwt_required
from server.common.database import Event as EventModel


@tag('event')
class Events(Resource):

    @use_kwargs({'start': fields.DateTime(required=False),
                 'end': fields.DateTime(required=False)}, location='query')
    @marshal_with(EventSchema(many=True), code=200)
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

    @jwt_required
    @use_kwargs(EventSchema)
    @marshal_with(EventSchema, code=201)
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


@tag('event')
class Event(Resource):

    @marshal_with(EventSchema, code=200)
    def get(self, event_id):
        return EventModel.query.get_or_404(event_id)

    @jwt_required
    @use_kwargs(EventSchema(partial=True))
    @marshal_with(EventSchema, code=200)
    def put(self, event_id, **kwargs):
        event = EventModel.query.get_or_404(event_id)
        try:
            event.__dict__.update(kwargs)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            raise ServerError(e)
        return event

    @jwt_required
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
