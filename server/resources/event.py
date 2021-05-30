from datetime import datetime

from flask_jwt_extended import get_current_user

from server.common.database import Event as EventModel
from server.common.database import db
from server.common.rest import Resource
from server.common.schema import EventSchema, EventFilterSchema
from server.common.util import AuthorisationError
from server.common.util.decorators import tag, marshal_with, jwt_required, params, transactional, use_kwargs
from server.common.util.enums import Role


@tag('event')
@params(event_id='The id of the Event')
class Event(Resource):

    @marshal_with(EventSchema, code=200)
    def get(self, event_id):
        """
        ## Get the event with the id event_id
        """
        return EventModel.query.get_or_404(event_id)

    @jwt_required()
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
        for k, v in kwargs.items():
            setattr(event, k, v)
        return event

    @jwt_required()
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
        for k, v in kwargs.items():
            setattr(event, k, v)
        return event

    @jwt_required()
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


@tag('event')
class Events(Resource):
    __child__ = Event

    @use_kwargs(EventFilterSchema, location='query')
    @marshal_with(EventSchema(many=True), code=200)
    def get(self, start: datetime = None, end: datetime = None):
        """
        ## Get all events between start and end
        """
        filters = []
        if not start:
            start = datetime.now()
        if not end:
            now = datetime.now()
            year, month = divmod(now.month + 1, 12)
            if month == 0:
                month = 12
                year = year - 1
            end = now.replace(year=now.year + year, month=month)
        filters.append(EventModel.start < end)
        filters.append(EventModel.end > start)
        return EventModel.query.filter(*filters).all()

    @jwt_required()
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
