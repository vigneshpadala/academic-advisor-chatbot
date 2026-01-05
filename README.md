# 🎓 Academic Advisor Chatbot (Django)

A smart **Academic Advisor Chatbot** built using **Django** that helps students access academic information such as profiles, results, and guidance through a conversational web interface.

This project simulates a real-world academic assistant for students and demonstrates backend logic, Django architecture, and chatbot-style interactions.

---

## 🚀 Features

- 💬 Chat-based academic assistant
- 👤 Student profile information support
- 📊 Academic results & semester details
- 🧠 Rule-based intelligent responses
- 🔐 Secure Django backend with CSRF protection
- 🌐 Clean and responsive web UI
- 🗂 Modular and scalable Django project structure

---

## 🛠 Tech Stack

**Backend**
- Python
- Django

**Frontend**
- HTML
- CSS
- JavaScript

**Database**
- SQLite (default Django database)

**Version Control**
- Git & GitHub

**Deployment Support**
- Render / Railway (Backend)

---

## ⚙️ Installation & Setup

### Prerequisites

- Python 3.10+
- pip
- Git

---

### Backend Setup (Django)

1. **Clone the repository**
```bash
git clone https://github.com/vigneshpadala/academic-advisor-chatbot.git

2️⃣ Navigate to Project Folder
cd academic-advisor-chatbot

3️⃣ Create Virtual Environment
python -m venv venv

4️⃣ Activate Virtual Environment
Windows
venv\Scripts\activate

Mac / Linux
source venv/bin/activate

5️⃣ Install Dependencies
pip install -r requirements.txt

6️⃣ Apply Migrations
python manage.py migrate

✅ App runs at:
http://127.0.0.1:8000/



📖 Usage
Open browser and visit:

cpp
Copy code
http://127.0.0.1:8000/
Start chatting with the Academic Advisor Bot

You can ask about:

Student profile

Academic results

Semester details

General academic help

The chatbot responds dynamically based on implemented logic

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
Push the code to GitHub

Connect the repository to Render or Railway

Build Command
bash
Copy code
pip install -r requirements.txt
Start Command
bash
Copy code
gunicorn chatbot_project.wsgi
Add required environment variables if needed

Deploy 🚀

🔮 Future Improvements
🤖 AI-powered chatbot (OpenAI / LLM integration)

🔐 Student authentication (login & signup)

📊 Database-backed real student academic results

📱 Fully mobile-responsive UI

🧠 NLP-based query understanding

🎓 Admin dashboard for academic management

👨‍💻 Author
Vignesh Padala
📍 Hyderabad, India
🔗 GitHub: https://github.com/vigneshpadala



