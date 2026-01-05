# 🎓 Academic Advisor Chatbot

An **Academic Advisor Chatbot** built using **Django** that helps students access academic-related information such as profiles, results, and guidance through a conversational interface.

This project is designed to simulate a real academic assistant that responds to student queries in a simple and interactive way.

---

## 🚀 Features

- 👤 Student profile display
- 📊 Academic results support
- 💬 Chat-based interaction
- 🧠 Rule-based / logic-driven responses
- 🌐 Web-based interface
- 🔐 CSRF protection enabled
- 🗂 Clean and scalable Django project structure

---


## 🛠 Tech Stack

- **Backend:** Python, Django  
- **Frontend:** HTML, CSS, JavaScript  
- **Database:** SQLite (default Django DB)  
- **Version Control:** Git & GitHub  

---

## 📁 Project Structure

chatbot_project/
│
├── chatbot_app/
| |
│ ├── migrations/
| |
│ ├── templates/
| |
│ ├── static/
| |
│ ├── views.py
| |
│ ├── models.py
| |
│ └── urls.py
│
|
├── chatbot_project/
| |
│ ├── settings.py
| |
│ ├── urls.py
| |
│ └── wsgi.py
│
├── manage.py
|
├── requirements.txt
|
└── README.md

---

## ⚙️ How It Works

1. User opens the chatbot in the browser.
2. Student enters a query (example: profile, results).
3. JavaScript sends the message to Django backend.
4. Django processes the request and generates a response.
5. The chatbot replies dynamically on the UI.

---

