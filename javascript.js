// script.js

document.addEventListener('DOMContentLoaded', () => {
  // ---- LOGIN PAGE ----
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    console.log("Login form found ✅"); // debug check

    loginForm.addEventListener('submit', (e) => {
      e.preventDefault();
      alert("Login successful!");
      window.location.href = "book-appointment.html"; // redirect to patient portal
    });
  }

  // ---- DOCTOR REGISTRATION PAGE ----
  const doctorForm = document.getElementById('doctor-form');
  if (doctorForm) {
    doctorForm.addEventListener('submit', (e) => {
      e.preventDefault();
      alert("Doctor registered successfully!");
      window.location.href = "login.html"; // redirect after signup
    });
  }

  // ---- BOOK APPOINTMENT PAGE ----
  const appointmentForm = document.getElementById('appointment-form');
  if (appointmentForm) {
    appointmentForm.addEventListener('submit', (e) => {
      e.preventDefault();
      alert("Appointment booked successfully!");
      appointmentForm.reset();
    });
  }
});
