from utils.db import db
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import CheckConstraint, Index


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='patient')
    name = db.Column(db.String(120))
    mobile = db.Column(db.String(30), index=True)
    gender = db.Column(db.String(20))
    address = db.Column(db.Text)
    age = db.Column(db.Integer)

    __table_args__ = (
        CheckConstraint('age IS NULL OR age >= 0', name='chk_users_age_nonnegative'),
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.email}>'
