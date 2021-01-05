from server.common.database import db, User


def create_debug_admin():
    # noinspection PyUnresolvedReferences
    if not User.query.filter_by(email="admin@debug.com").first():
        user = User(first_name="Debug",
                    last_name="Admin",
                    email="admin@debug.com",
                    password="AdminPazz69",
                    role="admin")
        db.session.add(user)
        db.session.commit()
