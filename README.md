🚨 Emergency Request Management System

A web-based Emergency Request Management System developed using Django. This project allows users to submit and manage emergency requests through an intuitive interface. The application includes location support using Google Maps, media upload capabilities, and request tracking features.

📌 Project Overview

This project was developed as part of a learning experience with the Django framework. The goal was to create a platform where emergency situations can be reported, tracked, and managed efficiently.

✨ Features
Create and manage emergency requests
Upload media files related to emergencies
Location integration with Google Maps
User-friendly web interface
SQLite database integration
Django-based backend architecture
🛠️ Technologies Used
Python
Django
HTML
CSS
JavaScript
SQLite
Google Maps API
📂 Project Structure
Plain Text
emergency_request/
│
├── core/
├── emergency_project/
├── media/
│ └── emergency_requests/
├── manage.py
├── db.sqlite3
└── README.md
🚀 Installation
Prerequisites
Python 3.x
pip
Git
Clone the Repository
Shell
git clone https://github.com/ameniajlani-cell/emergency_request.git
cd emergency_request
Create a Virtual Environment
Shell
python -m venv venv

Activate it:

Windows

Shell
venv\Scripts\activate

Linux/macOS

Shell
source venv/bin/activate
Install Dependencies
Shell
pip install -r requirements.txt
Run Migrations
Shell
python manage.py migrate
 
Start the Development Server
Shell
python manage.py runserver

Open:

Plain Text
http://127.0.0.1:8000/
🗺️ Google Maps Configuration

This project includes Google Maps integration. Configure your Google Maps API key according to the project setup instructions before running location-based features.

👥 Team Members
Ameni Ajlani
Malak Sridi
🎯 Learning Outcomes

Through this project, the team gained practical experience with:

Django Framework
Database Management
CRUD Operations
Web Application Development
API Integration
Collaborative Development using Git and GitHub
📜 License

This project is intended for educational and learning purposes.
