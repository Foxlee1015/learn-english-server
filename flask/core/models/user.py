import os
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import event
from werkzeug.security import generate_password_hash, check_password_hash
from core.database import db
from core.models.base import BaseModel

APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
dotenv_path = os.path.join(APP_ROOT, ".env")
load_dotenv(dotenv_path)


class User(BaseModel):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(100), nullable=False)
    login_try_count = db.Column(db.Integer, default=0)
    role_id = db.Column(
        db.Integer, db.ForeignKey("user_role.id", ondelete="SET NULL"), default=3
    )
    created_datetime = db.Column(db.DateTime, default=datetime.now())

    protected_columns = ["password"]

    def __init__(self, username, email, password, role_id, **kwargs):
        self.username = username
        self.email = email
        self.role_id = role_id
        self.set_password(password)

    def __repr__(self):
        return self._repr(
            id=self.id,
            username=self.username,
            email=self.email,
        )

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def add_login_try_count(self):
        self.login_try_count += 1
        db.session.commit()

    def is_admin(self):
        if self.role_id == int(os.getenv("ADMIN_ROLE_ID")):
            return True
        return False

    def is_manager(self):
        if self.role_id == int(os.getenv("MANAGER_ROLE_ID")):
            return True
        return False


@event.listens_for(User.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    initial_users = [
        User(
            os.getenv("ADMIN_USER_NAME"),
            os.getenv("ADMIN_USER_EMAIL"),
            os.getenv("ADMIN_USER_PASSWORD"),
            os.getenv("ADMIN_ROLE_ID"),
        ),
        User(
            os.getenv("CRAWLER_USER_NAME"),
            os.getenv("CRAWLER_USER_EMAIL"),
            os.getenv("CRAWLER_USER_PASSWORD"),
            os.getenv("ADMIN_ROLE_ID"),
        ),
    ]
    db.session.add_all(initial_users)
    db.session.commit()
