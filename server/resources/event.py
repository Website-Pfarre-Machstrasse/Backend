from datetime import datetime
from typing import Union

from flask_jwt_extended import get_current_user

from common.database import db
from common.database.user import Role
from common.rest import Resource
from common.schema import EventSchema, EventFilterSchema
from common.util import AuthorisationError
from common.util.decorators import tag, marshal_with, jwt_required, params, transactional, use_kwargs
from server.common.database import Event as EventModel


@tag('event')
class Events(Resource):

    @use_kwargs(EventFilterSchema, location='query')
    @marshal_with(EventSchema(many=True), code=200)
    def get(self, start: Union[datetime, None] = None, end: Union[datetime, None] = None):
        """
        ## Get all events between start and end
        """
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
    @transactional(db.session)
    def post(self, _transaction, **kwargs):
        """
        ## Add a new event
        ***Requires Authentication***
        """
        event = EventModel(**kwargs)
        _transaction.session.add(event)
        return event, 201


@tag('event')
@params(event_id='The id of the Event')
class Event(Resource):

    @marshal_with(EventSchema, code=200)
    def get(self, event_id):
        """
        ## Get the event with the id event_id
        """
        return EventModel.query.get_or_404(event_id)

    @jwt_required
    @use_kwargs(EventSchema)
    @marshal_with(EventSchema, code=200)
    def put(self, event_id, **kwargs):
        """
        ## Modify the event with the id event_id
        ***Requires Authentication***
        """
        event = EventModel.query.get_or_404(event_id)
        user = get_current_user()
        if event.owner is not user and user.role != Role.admin:
            raise AuthorisationError('You are not allowed to delete this media')
        event.__dict__.update(kwargs)
        return event

    @jwt_required
    @use_kwargs(EventSchema(partial=True))
    @marshal_with(EventSchema, code=200)
    def patch(self, event_id, **kwargs):
        """
        ## Modify the event with the id event_id
        ***Requires Authentication***
        """
        event = EventModel.query.get_or_404(event_id)
        user = get_current_user()
        if event.owner is not user and user.role != Role.admin:
            raise AuthorisationError('You are not allowed to delete this media')
        event.__dict__.update(kwargs)
        return event

    @jwt_required
    @marshal_with(None, code=204)
    @transactional(db.session)
    def delete(self, event_id, _transaction):
        """
        ## Delete the event with the id event_id
        ***Requires Authentication***
        """
        event = EventModel.query.get_or_404(event_id)
        user = get_current_user()
        if event.owner is not user and user.role != Role.admin:
            raise AuthorisationError('You are not allowed to delete this media')
        _transaction.session.delete(event)
        return {}, 204
