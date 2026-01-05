🎓 Academic Advisor Chatbot (Django)

A smart Academic Advisor Chatbot built using Django that helps students access academic information such as profiles, results, and guidance through a conversational web interface.

This project simulates a real-world academic assistant for students and demonstrates backend logic, Django architecture, and chatbot-style interactions.


🚀 Features

💬 Chat-based academic assistant

👤 Student profile information support

📊 Academic results & semester details

🧠 Rule-based intelligent responses

🔐 Secure Django backend with CSRF protection

🌐 Clean and responsive web UI

🗂 Modular and scalable Django project structure


🛠 Tech Stack

Backend:

Python

Django

Frontend:

HTML

CSS

JavaScript

Database:

SQLite (default Django database)

Version Control:

Git & GitHub

Deployment Support:

Render / Railway (backend)


⚙️ Installation & Setup
Prerequisites

Python 3.10+

pip

Git


Backend Setup (Django)

Clone the repository

git clone https://github.com/vigneshpadala/academic-advisor-chatbot.git


Navigate to project folder

cd academic-advisor-chatbot


Create virtual environment

python -m venv venv


Activate virtual environment

Windows:

venv\Scripts\activate


Mac/Linux:

source venv/bin/activate


Install dependencies

pip install -r requirements.txt


Apply migrations

python manage.py migrate


Run development server

python manage.py runserver


✅ App runs at:

http://127.0.0.1:8000/


📖 Usage

Open browser and go to:

http://127.0.0.1:8000/


Start chatting with the Academic Advisor Bot

You can ask about:

Student profile

Academic results

Semester details

General academic help

Bot responds dynamically based on logic


📁 Project Structure
chatbot_project/
│
├── chatbot_app/
│   ├── migrations/
│   ├── templates/
│   ├── static/
│   ├── views.py
│   ├── models.py
│   └── urls.py
│
├── chatbot_project/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── manage.py
├── requirements.txt
└── README.md


🌐 Deployment
Backend Deployment (Render / Railway)
Push code to GitHub

Connect repository to Render or Railway

Set build command:

bash
Copy code
pip install -r requirements.txt
Start command:

bash
Copy code
gunicorn chatbot_project.wsgi
Add environment variables if required

Deploy 🚀




🔮 Future Improvements

🤖 AI-powered chatbot (OpenAI / LLM integration)

🔐 Student authentication (login & signup)

📊 Database-backed real student results

📱 Mobile responsive UI

🧠 NLP-based query understanding

🎓 Admin dashboard for academic management

👨‍💻 Author

Vignesh Padala
📍 Hyderabad, India
🔗 GitHub: https://github.com/vigneshpadala
