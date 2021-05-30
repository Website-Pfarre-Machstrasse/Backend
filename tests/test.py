import os
import tempfile

import pytest
from werkzeug.datastructures import Headers

from server import create_app
from server.common.database import db, User
from server.common.util.enums import Role


@pytest.fixture
def client():
    os.environ.setdefault('TESTING', '1')
    app = create_app()
    db_fd, app.config['DATABASE'] = tempfile.mkstemp()
    app.config['TESTING'] = True

    with app.test_client() as client:
        with app.app_context():
            db.create_all(app=app)
            with db.session.begin():
                admin = User(
                    first_name='Test',
                    last_name='Admin',
                    email='admin.email@test.com',
                    password='TestAdminPass',
                    role=Role.admin
                )
                db.session.add(admin)
                author = User(
                    first_name='Test',
                    last_name='Author',
                    email='author.email@test.com',
                    password='TestAuthorPass',
                    role=Role.author
                )
                db.session.add(author)
        yield client

    os.close(db_fd)
    os.unlink(app.config['DATABASE'])


def login(client, username, password):
    resp = client.post('/api/login',
                       json={'username': username, 'password': password})  # type: "TestResponse"
    assert resp.status_code == 200
    access_token = resp.json['access_token']
    refresh_token = resp.json['refresh_token']
    return access_token, refresh_token


def test_users(client):
    resp = client.get('/api/user')  # type: "TestResponse"
    assert resp.status_code == 401

    access_token, refresh_token = login(client, 'admin.email@test.com', 'TestAdminPass')

    headers = Headers({'Authorization': f'Bearer {access_token}'})

    resp = client.get('/api/user', headers=headers)  # type: "TestResponse"
    assert resp.status_code == 200
    assert len(resp.json) == 2

    resp = client.get('/api/self', headers=headers)  # type: "TestResponse"
    assert resp.status_code == 200
    assert resp.json['email'] == 'admin.email@test.com'
    uid = resp.json['id']

    resp = client.post('/api/refresh',
                       headers=Headers({'Authorization': f'Bearer {refresh_token}'}))  # type: "TestResponse"
    assert resp.status_code == 200
    assert (access_token := resp.json['access_token'])

    new_headers = Headers({'Authorization': f'Bearer {access_token}'})

    resp = client.get('/api/self', headers=new_headers)  # type: "TestResponse"
    assert resp.status_code == 200
    assert resp.json['email'] == 'admin.email@test.com'
    assert resp.json['id'] == uid

    resp = client.get(f'/api/user/{uid}')  # type: "TestResponse"
    assert resp.status_code == 200
    assert resp.json['email'] == 'admin.email@test.com'
    assert resp.json['id'] == uid

    resp = client.patch(f'/api/user/{uid}',
                        json={'first_name': 'New', 'password': 'NewPass'}, headers=headers)  # type: "TestResponse"
    assert resp.status_code == 200
    assert resp.json['email'] == 'admin.email@test.com'
    assert resp.json['id'] == uid
    assert resp.json['first_name'] == 'New'

    access_token, refresh_token = login(client, 'admin.email@test.com', 'NewPass')

    headers = Headers({'Authorization': f'Bearer {access_token}'})

    resp = client.get('/api/self', headers=headers)  # type: "TestResponse"
    assert resp.status_code == 200
    assert resp.json['email'] == 'admin.email@test.com'
    assert resp.json['id'] == uid
    assert resp.json['first_name'] == 'New'


def test_event(client):
    pass  # TODO


def test_gallery(client):
    pass  # TODO


def test_media(client):
    pass  # TODO


def test_content(client):
    pass  # TODO
