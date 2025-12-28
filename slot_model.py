from utils.db import db
from datetime import datetime
from sqlalchemy import CheckConstraint, UniqueConstraint, Index


class Slot(db.Model):
    __tablename__ = 'slots'
    id = db.Column(db.Integer, primary_key=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    is_available = db.Column(db.Boolean, default=True, nullable=False)

    doctor = db.relationship('Doctor', backref='slots')

    __table_args__ = (
        CheckConstraint('end_time > start_time', name='chk_slot_times'),
        UniqueConstraint('doctor_id', 'start_time', 'end_time', name='uq_slots_doctor_time'),
        Index('ix_slots_doctor_start', 'doctor_id', 'start_time'),
    )

    def __repr__(self):
        return f'<Slot {self.id} {self.start_time} -> {self.end_time}>'
