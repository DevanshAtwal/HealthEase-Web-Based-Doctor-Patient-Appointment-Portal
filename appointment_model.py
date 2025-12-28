from utils.db import db
from datetime import datetime
from sqlalchemy import CheckConstraint, UniqueConstraint


class Appointment(db.Model):
    __tablename__ = 'appointments'
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id', ondelete='CASCADE'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('slots.id'))
    reason = db.Column(db.Text)
    patient_mobile = db.Column(db.String(30))
    patient_city = db.Column(db.String(120))
    patient_age = db.Column(db.Integer)
    status = db.Column(db.String(30), default='scheduled', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        CheckConstraint("status IN ('scheduled','completed','cancelled','no-show','rescheduled')", name='chk_appointment_status'),
        UniqueConstraint('slot_id', name='uq_appointments_slot'),
    )

    patient = db.relationship('User', backref='appointments')
    doctor = db.relationship('Doctor', backref='appointments')

    def __repr__(self):
        return f'<Appointment {self.id} {self.status}>'
