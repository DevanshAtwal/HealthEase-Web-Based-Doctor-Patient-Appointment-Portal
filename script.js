const loginBtn = document.getElementById('loginBtn');
const findBtn = document.getElementById('findBtn');
const loginModal = document.getElementById('loginModal');
const registerModal = document.getElementById('registerModal');
const closeBtns = document.querySelectorAll('.close');
const registerLink = document.getElementById('registerLink');
const userTypeSelect = document.getElementById('userType');
const patientFields = document.getElementById('patientFields');
const doctorFields = document.getElementById('doctorFields');

loginBtn.onclick = () => loginModal.style.display = 'flex';
findBtn.onclick = () => window.location.href = "find_doctor.html";
registerLink.onclick = () => {
  loginModal.style.display = 'none';
  registerModal.style.display = 'flex';
};

userTypeSelect.onchange = () => {
  if (userTypeSelect.value === 'doctor') {
    doctorFields.style.display = 'block';
    patientFields.style.display = 'none';
  } else {
    doctorFields.style.display = 'none';
    patientFields.style.display = 'block';
  }
};

closeBtns.forEach(btn => btn.onclick = () => {
  loginModal.style.display = 'none';
  registerModal.style.display = 'none';
});

window.onclick = (e) => {
  if (e.target === loginModal || e.target === registerModal) {
    loginModal.style.display = 'none';
    registerModal.style.display = 'none';
  }
};
