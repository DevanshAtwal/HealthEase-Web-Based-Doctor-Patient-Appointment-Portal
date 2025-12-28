from flask import Blueprint, redirect, render_template, request, jsonify
from utils.db import db
from models.appointment_model import Appointment
from models.user_model import User
from models.doctor_model import Doctor

patient_bp = Blueprint('patient', __name__)


@patient_bp.route('/')
def patient_index():
	# Redirect to frontend patient dashboard if available
	return redirect('/site/PATIENT/patient_dashboard.html')


@patient_bp.route('/book', methods=['GET', 'POST'])
def book_route():
	"""GET: redirect to frontend booking page. POST: accept JSON and create an appointment."""
	if request.method == 'GET':
		# preserve any query string (e.g. ?doctor=Name) when redirecting to the frontend
		qs = request.query_string.decode()
		target = '/site/PATIENT/book_appointment.html'
		if qs:
			target = f"{target}?{qs}"
		return redirect(target)

	# POST: create appointment
	data = request.get_json() or {}
	# Accept either IDs or friendly fields
	patient_id = data.get('patient_id')
	patient_email = data.get('patient_email')
	patient_name = data.get('patient_name')

	doctor_id = data.get('doctor_id')
	doctor_name = data.get('doctor_name') or data.get('doctor')

	slot_text = data.get('slot')
	reason = data.get('reason') or data.get('disease') or data.get('problem')

	# Resolve/create patient
	patient = None
	if patient_id:
		patient = User.query.get(patient_id)
	elif patient_email:
		patient = User.query.filter_by(email=patient_email).first()
		if not patient:
			patient = User(email=patient_email, name=patient_name, role='patient')
			# create a dummy password; user should reset via normal flow
			patient.set_password('changeme')
			db.session.add(patient)
			db.session.flush()
	elif patient_name:
		patient = User.query.filter_by(name=patient_name, role='patient').first()
		if not patient:
			# Create a patient record with generated email
			gen_email = f"{patient_name.replace(' ', '_').lower()}@local"
			patient = User(email=gen_email, name=patient_name, role='patient')
			patient.set_password('changeme')
			db.session.add(patient)
			db.session.flush()

	if not patient:
		return jsonify({'error': 'patient not found or could not be created'}), 400

	# Resolve doctor
	doctor = None
	if doctor_id:
		doctor = Doctor.query.get(doctor_id)
	elif doctor_name:
		# match by user's name linked to doctor profile
		user = User.query.filter_by(name=doctor_name).first()
		if user:
			doctor = Doctor.query.filter_by(user_id=user.id).first()

	if not doctor:
		return jsonify({'error': 'doctor not found (provide doctor_id or doctor_name)'}), 400

	# Create appointment record (slot resolution not implemented)
	# Capture patient contact data on the appointment as a snapshot
	patient_mobile = data.get('mobile') or data.get('patient_mobile')
	patient_city = data.get('city') or data.get('patient_city')
	patient_age = data.get('age') or data.get('patient_age')

	# If we have contact info, update the user record as well
	try:
		if patient_mobile:
			patient.mobile = patient_mobile
		if patient_city:
			patient.address = patient_city
		if patient_age:
			try:
				patient.age = int(patient_age)
			except Exception:
				pass
		db.session.add(patient)
		db.session.flush()
	except Exception:
		# ignore non-critical user updates
		pass

	appt = Appointment(
		patient_id=patient.id,
		doctor_id=doctor.id,
		reason=reason,
		patient_mobile=patient_mobile,
		patient_city=patient_city,
		patient_age=(int(patient_age) if patient_age and str(patient_age).isdigit() else None)
	)
	db.session.add(appt)
	db.session.commit()

	return jsonify({'message': 'appointment created', 'appointment_id': appt.id}), 201


@patient_bp.route('/book-template')
def book_template():
	"""Render the backend template version if you prefer server-side rendering."""
	return render_template('book_appointment.html')


@patient_bp.route('/appointments', methods=['GET'])
def list_appointments():
	"""Return appointments for a patient filtered by id, email or name.

	Query params supported: patient_id, patient_email, patient_name
	"""
	patient_id = request.args.get('patient_id')
	patient_email = request.args.get('patient_email')
	patient_name = request.args.get('patient_name')

	patient = None
	if patient_id:
		patient = User.query.get(patient_id)
	elif patient_email:
		patient = User.query.filter_by(email=patient_email).first()
	elif patient_name:
		patient = User.query.filter_by(name=patient_name, role='patient').first()

	if not patient:
		return jsonify({'appointments': []})

	appts = Appointment.query.filter_by(patient_id=patient.id).order_by(Appointment.created_at.desc()).all()
	result = []
	for a in appts:
		doctor_name = ''
		if a.doctor:
			if getattr(a.doctor, 'user', None):
				doctor_name = a.doctor.user.name or ''
		result.append({
			'id': a.id,
			'doctor_name': doctor_name,
			'reason': a.reason,
			'status': a.status,
			'created_at': a.created_at.isoformat(),
		})

	return jsonify({'appointments': result})


@patient_bp.route('/appointments/<int:appointment_id>/cancel', methods=['POST'])
def cancel_appointment(appointment_id):
	a = Appointment.query.get(appointment_id)
	if not a:
		return jsonify({'error': 'appointment not found'}), 404
	a.status = 'cancelled'
	db.session.commit()
	return jsonify({'message': 'appointment cancelled'})
