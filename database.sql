-- Database: healthease

CREATE DATABASE Healthease;
USE Healthease;

-- Patients Table
CREATE TABLE patient (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    address VARCHAR(255),
    email VARCHAR(100) UNIQUE,
    mobile VARCHAR(15),
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255),
    age INT,
    gender VARCHAR(10)
);

-- Doctors Table
CREATE TABLE doctor (
    id INT AUTO_INCREMENT PRIMARY KEY,
    fullname VARCHAR(100) NOT NULL,
    contact VARCHAR(15),
    specialization VARCHAR(100),
    education VARCHAR(100),
    hospital VARCHAR(100),
    location VARCHAR(100),
    fee DECIMAL(10,2),
    time_slots VARCHAR(100),
    username VARCHAR(50) UNIQUE,
    password VARCHAR(255)
);

-- Appointments Table
CREATE TABLE appointment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT,
    doctor_id INT,
    patient_name VARCHAR(100),
    mobile VARCHAR(15),
    age INT,
    gender VARCHAR(10),
    address VARCHAR(255),
    disease VARCHAR(255),
    appointment_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patient(id),
    FOREIGN KEY(doctor_id) REFERENCES doctor(id)
);
