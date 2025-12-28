from utils.db import db
from sqlalchemy import UniqueConstraint, Index


class Doctor(db.Model):
    __tablename__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    specialty = db.Column(db.String(120), nullable=False)
    bio = db.Column(db.Text)
    mobile = db.Column(db.String(30))
    education = db.Column(db.String(255))
    fee = db.Column(db.Numeric(10, 2))
    hospital = db.Column(db.String(255))

    user = db.relationship('User', backref=db.backref('doctor_profile', uselist=False))

    __table_args__ = (
        Index('ix_doctors_specialty', 'specialty'),
        UniqueConstraint('user_id', name='uq_doctors_user_id'),
    )

    def __repr__(self):
        return f'<Doctor {self.id} - {self.specialty}>'
