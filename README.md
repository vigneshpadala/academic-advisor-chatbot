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

## ⚙️ How It Works

1. User opens the chatbot in the browser.
2. Student enters a query (example: profile, results).
3. JavaScript sends the message to Django backend.
4. Django processes the request and generates a response.
5. The chatbot replies dynamically on the UI.

---


## 🧪 Run Project Locally (localhost)

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/vigneshpadala/academic-advisor-chatbot.git

###2️⃣ Go to Project Folder
cd academic-advisor-chatbot

###3️⃣ Create Virtual Environment (Recommended)
python -m venv venv

##Activate:
##Windows
venv\Scripts\activate

##Mac/Linux
source venv/bin/activate

###4️⃣ Install Dependencies
pip install -r requirements.txt

##5️⃣ Apply Migrations
python manage.py migrate

##6️⃣ Run the Server
python manage.py runserver
(or)
py manage.py runserver

##7️⃣ Open in Browser
http://127.0.0.1:8000/

---


📌 How to Use
Open the chatbot page

Enter student-related queries

Get instant academic responses


