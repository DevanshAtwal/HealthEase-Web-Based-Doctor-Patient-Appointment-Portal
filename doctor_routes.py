from flask import Blueprint, redirect

doctor_bp = Blueprint('doctor', __name__)


@doctor_bp.route('/')
def dashboard():
    return redirect('/site/DOCTOR/doctor_dashboard.html')
