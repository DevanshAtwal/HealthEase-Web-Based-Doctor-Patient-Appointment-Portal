
from flask import Blueprint, request, jsonify, redirect, abort, session
from models.user_model import User
from models.doctor_model import Doctor
from models.appointment_model import Appointment
from models.slot_model import Slot
from utils.db import db

admin_bp = Blueprint('admin', __name__)


def _get_request_user():
    # Prefer server-side session user if present
    try:
        if session and session.get('user_id') and session.get('role') == 'admin':
            return int(session.get('user_id'))
    except Exception:
        pass

    # Fallback: try header, query or JSON user id
    uid = request.headers.get('X-User-Id') or request.args.get('user_id')
    if not uid:
        try:
            data = request.get_json(silent=True) or {}
            uid = data.get('user_id') or data.get('admin_id')
        except Exception:
            uid = None
    try:
        return int(uid) if uid is not None else None
    except Exception:
        return None


def require_admin(fn):
    def wrapper(*args, **kwargs):
        user_id = _get_request_user()
        if not user_id:
            return jsonify({'error': 'admin user id required'}), 401
        user = User.query.get(user_id)
        if not user or user.role != 'admin':
            return jsonify({'error': 'admin privileges required'}), 403
        return fn(*args, **kwargs)

    wrapper.__name__ = fn.__name__
    return wrapper


@admin_bp.route('/')
def dashboard():
    # Serve frontend admin dashboard if available
    return redirect('/site/ADMIN/admin_dashboard.html')


# --- Doctor management APIs ---
@admin_bp.route('/api/doctors', methods=['GET'])
@require_admin
def list_doctors():
    doctors = Doctor.query.all()
    result = []
    for d in doctors:
        result.append({
            'id': d.id,
            'user_id': d.user_id,
            'name': d.user.name if d.user else None,
            'email': d.user.email if d.user else None,
            'specialty': d.specialty,
            'mobile': d.mobile,
            'education': d.education,
            'fee': str(d.fee) if d.fee is not None else None,
            'hospital': d.hospital,
        })
    return jsonify(result)


@admin_bp.route('/api/doctors', methods=['POST'])
@require_admin
def create_doctor():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    specialty = data.get('specialty')
    if not all([email, password, specialty]):
        return jsonify({'error': 'email, password and specialty required'}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email already exists'}), 400
    try:
        user = User(email=email, name=name, role='doctor')
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        doctor = Doctor(user_id=user.id, specialty=specialty)
        doctor.mobile = data.get('mobile')
        doctor.education = data.get('education')
        doctor.fee = data.get('fee')
        doctor.hospital = data.get('hospital')
        db.session.add(doctor)
        db.session.commit()
        return jsonify({'message': 'doctor created', 'doctor_id': doctor.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'failed to create doctor', 'details': str(e)}), 500


@admin_bp.route('/api/doctors/<int:doctor_id>', methods=['PUT'])
@require_admin
def update_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    data = request.get_json() or {}
    # Update doctor fields
    if 'specialty' in data:
        doctor.specialty = data.get('specialty')
    for field in ('mobile', 'education', 'fee', 'hospital', 'bio'):
        if field in data:
            setattr(doctor, field, data.get(field))
    # Optionally update linked user
    if 'name' in data or 'email' in data:
        user = doctor.user
        if 'name' in data:
            user.name = data.get('name')
        if 'email' in data:
            if User.query.filter(User.email == data.get('email'), User.id != user.id).first():
                return jsonify({'error': 'email already in use'}), 400
            user.email = data.get('email')
    try:
        db.session.commit()
        return jsonify({'message': 'doctor updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'update failed', 'details': str(e)}), 500


@admin_bp.route('/api/doctors/<int:doctor_id>', methods=['DELETE'])
@require_admin
def delete_doctor(doctor_id):
    doctor = Doctor.query.get_or_404(doctor_id)
    try:
        # delete linked user will cascade to doctor due to FK ondelete
        user = doctor.user
        if user:
            db.session.delete(user)
        else:
            db.session.delete(doctor)
        db.session.commit()
        return jsonify({'message': 'doctor deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'delete failed', 'details': str(e)}), 500


# --- Patient management APIs ---
@admin_bp.route('/api/patients', methods=['GET'])
@require_admin
def list_patients():
    users = User.query.filter_by(role='patient').all()
    return jsonify([{'id': u.id, 'name': u.name, 'email': u.email, 'mobile': u.mobile} for u in users])


@admin_bp.route('/api/patients/<int:user_id>', methods=['PUT'])
@require_admin
def update_patient(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'patient':
        return jsonify({'error': 'user is not a patient'}), 400
    data = request.get_json() or {}
    for field in ('name', 'email', 'mobile', 'address', 'age'):
        if field in data:
            setattr(user, field, data.get(field))
    try:
        db.session.commit()
        return jsonify({'message': 'patient updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'update failed', 'details': str(e)}), 500


@admin_bp.route('/api/patients/<int:user_id>', methods=['DELETE'])
@require_admin
def delete_patient(user_id):
    user = User.query.get_or_404(user_id)
    if user.role != 'patient':
        return jsonify({'error': 'user is not a patient'}), 400
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'patient deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'delete failed', 'details': str(e)}), 500


# --- Appointment management ---
@admin_bp.route('/api/appointments', methods=['GET'])
@require_admin
def list_appointments():
    appts = Appointment.query.order_by(Appointment.created_at.desc()).all()
    out = []
    for a in appts:
        out.append({
            'id': a.id,
            'patient_id': a.patient_id,
            'patient_name': a.patient.name if a.patient else None,
            'doctor_id': a.doctor_id,
            'doctor_specialty': a.doctor.specialty if a.doctor else None,
            'slot_id': a.slot_id,
            'status': a.status,
            'created_at': a.created_at.isoformat() if a.created_at else None,
        })
    return jsonify(out)


@admin_bp.route('/api/appointments/<int:appt_id>', methods=['PUT'])
@require_admin
def update_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    data = request.get_json() or {}
    if 'status' in data:
        appt.status = data.get('status')
    if 'slot_id' in data:
        appt.slot_id = data.get('slot_id')
    try:
        db.session.commit()
        return jsonify({'message': 'appointment updated'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'update failed', 'details': str(e)}), 500


@admin_bp.route('/api/appointments/<int:appt_id>', methods=['DELETE'])
@require_admin
def delete_appointment(appt_id):
    appt = Appointment.query.get_or_404(appt_id)
    try:
        db.session.delete(appt)
        db.session.commit()
        return jsonify({'message': 'appointment deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'delete failed', 'details': str(e)}), 500


# --- Slot management ---
@admin_bp.route('/api/slots', methods=['GET'])
@require_admin
def list_slots():
    slots = Slot.query.order_by(Slot.start_time).all()
    return jsonify([{
        'id': s.id,
        'doctor_id': s.doctor_id,
        'start_time': s.start_time.isoformat() if s.start_time else None,
        'end_time': s.end_time.isoformat() if s.end_time else None,
        'is_available': s.is_available,
    } for s in slots])


@admin_bp.route('/api/slots', methods=['POST'])
@require_admin
def create_slot():
    data = request.get_json() or {}
    doctor_id = data.get('doctor_id')
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    if not all([doctor_id, start_time, end_time]):
        return jsonify({'error': 'doctor_id, start_time and end_time required'}), 400
    try:
        from datetime import datetime
        st = datetime.fromisoformat(start_time)
        et = datetime.fromisoformat(end_time)
        slot = Slot(doctor_id=doctor_id, start_time=st, end_time=et, is_available=bool(data.get('is_available', True)))
        db.session.add(slot)
        db.session.commit()
        return jsonify({'message': 'slot created', 'slot_id': slot.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'create failed', 'details': str(e)}), 500


@admin_bp.route('/api/slots/<int:slot_id>', methods=['DELETE'])
@require_admin
def delete_slot(slot_id):
    slot = Slot.query.get_or_404(slot_id)
    try:
        db.session.delete(slot)
        db.session.commit()
        return jsonify({'message': 'slot deleted'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'delete failed', 'details': str(e)}), 500

