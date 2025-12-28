from flask import Blueprint, request, jsonify, redirect, url_for, session
from models.user_model import User
from models.doctor_model import Doctor
from utils.db import db
from urllib.parse import urlencode

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        # Redirect to the frontend login page served via /site/
        return redirect('/site/login.html')

    # POST (API) - accept JSON for API calls
    data = request.get_json() or {}
    role = data.get('role')
    password = data.get('password')

    if role not in ('patient', 'doctor', 'admin'):
        return jsonify({'error': 'role must be patient, doctor, or admin'}), 400
    if not password:
        return jsonify({'error': 'password required'}), 400

    user = None
    # Patient: login by mobile stored on User
    if role == 'patient':
        mobile = data.get('mobile')
        if not mobile:
            return jsonify({'error': 'mobile required for patient login'}), 400
        user = User.query.filter_by(mobile=mobile, role='patient').first()

    # Doctor: login by mobile stored on Doctor profile
    elif role == 'doctor':
        mobile = data.get('mobile')
        if not mobile:
            return jsonify({'error': 'mobile required for doctor login'}), 400
        doctor = Doctor.query.filter_by(mobile=mobile).first()
        if doctor:
            user = doctor.user

    # Admin: login by email
    else:  # admin
        email = data.get('email')
        if not email:
            return jsonify({'error': 'email required for admin login'}), 400
        user = User.query.filter_by(email=email, role='admin').first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'invalid credentials'}), 401

    # Set server-side session (safer than storing password client-side)
    session.clear()
    session['user_id'] = user.id
    session['role'] = user.role

    return jsonify({'message': 'login successful', 'user_id': user.id, 'role': user.role, 'name': user.name})


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Redirect to the frontend register page served via /site/
        return redirect('/site/register.html')

    # POST (API) - accept JSON
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        return jsonify({'error': 'email and password required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'email already in use'}), 400

    user = User(email=email, name=data.get('name'))
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return jsonify({'message': 'user created', 'user_id': user.id}), 201


@auth_bp.route('/register/patient', methods=['POST'])
def register_patient():
    """Handle patient registration form submission."""
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        mobile = request.form.get('mobile', '').strip()
        address = request.form.get('address', '').strip()
        age = request.form.get('age')
        gender = request.form.get('gender', '').strip()

        try:
            age = int(age) if age else None
        except Exception:
            age = None

        if not all([name, email, password, mobile]):
            return redirect('/site/register.html?error=All+fields+are+required')

        if User.query.filter_by(email=email).first():
            return redirect('/site/register.html?error=Email+already+registered')

        user = User(email=email, name=name, role='patient')
        user.mobile = mobile or None
        user.address = address or None
        try:
            user.age = int(age) if age else None
        except Exception:
            user.age = None
        user.gender = gender or None
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect('/site/login.html?success=Registration+successful!+Please+login.')
    except Exception as e:
        db.session.rollback()
        error_msg = str(e).replace('\n', ' ')[:50]  # Truncate and remove newlines
        return redirect(f'/site/register.html?error=Registration+failed')


@auth_bp.route('/register/doctor', methods=['POST'])
def register_doctor():
    """Handle doctor registration form submission."""
    try:
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        mobile = request.form.get('mobile', '').strip()
        education = request.form.get('education', '').strip()
        speciality = request.form.get('speciality', '').strip()
        slots = request.form.get('slots', '').strip()
        fee = request.form.get('fee', '').strip()
        hospital = request.form.get('hospital', '').strip()

        if not all([name, email, password, mobile, education, speciality]):
            return redirect('/site/register.html?error=All+required+fields+must+be+filled')

        if User.query.filter_by(email=email).first():
            return redirect('/site/register.html?error=Email+already+registered')

        # Create user account for doctor
        user = User(email=email, name=name, role='doctor')
        # store mobile on the user as well so doctors can login by mobile
        user.mobile = mobile or None
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        # Create doctor profile linked to user
        bio_parts = []
        if education:
            bio_parts.append(f"Education: {education}")
        if hospital:
            bio_parts.append(f"Hospital: {hospital}")
        if fee:
            bio_parts.append(f"Fee: {fee}")
        if slots:
            bio_parts.append(f"Slots: {slots}")
        
        doctor = Doctor(
            user_id=user.id,
            specialty=speciality,
            bio=' | '.join(bio_parts)
        )
        doctor.mobile = mobile or None
        doctor.education = education or None
        doctor.fee = fee or None
        doctor.hospital = hospital or None
        db.session.add(doctor)
        db.session.commit()

        return redirect('/site/login.html?success=Doctor+registration+successful!+Please+login.')
    except Exception as e:
        db.session.rollback()
        return redirect('/site/register.html?error=Registration+failed')
