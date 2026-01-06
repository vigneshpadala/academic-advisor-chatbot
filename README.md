### Backend Setup (Django)

1. **Clone the repository**
bash
git clone https://github.com/vigneshpadala/academic-advisor-chatbot.git

2️. Navigate to Project Folder
cd academic-advisor-chatbot

3️. Create Virtual Environment
python -m venv venv


### A

4️.Activate Virtual Environment
Windows
venv\Scripts\activate

Mac / Linux
source venv/bin/activate

5. Install Dependencies
pip install -r requirements.txt

6️. Apply Migrations
python manage.py migrate

✅ App runs at:
http://127.0.0.1:8000/

---

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
cpp
Copy code
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



