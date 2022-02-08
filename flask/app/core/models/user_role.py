import os

from sqlalchemy import event

from app.core.database import db
from app.core.models.base import BaseModel


class UserRole(BaseModel):
    __tablename__ = "user_role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(120))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return self._repr(id=self.id, name=self.name, description=self.description)


@event.listens_for(UserRole.__table__, "after_create")
def insert_initial_values(*args, **kwargs):
    user_roles = [
        UserRole(
            os.getenv("ADMIN_ROLE_NAME"),
            os.getenv("ADMIN_ROLE_DESCRIPTION"),
        ),
        UserRole(
            os.getenv("MANAGER_ROLE_NAME"),
            os.getenv("MANAGER_ROLE_DESCRIPTION"),
        ),
        UserRole(
            os.getenv("GENERAL_ROLE_NAME"),
            os.getenv("GENERAL_ROLE_DESCRIPTION"),
        ),
    ]
    db.session.add_all(user_roles)
    db.session.commit()
