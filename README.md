

# 🧠 Fact Checking Forum

This project was developed as part of my academic coursework to explore **full-stack web app development** using Flask and PostgreSQL.  
It focuses on creating a platform where students can post academic queries, verified faculty can respond, and administrators can ensure moderation — reducing misinformation in educational spaces.

---

## 🚀 Project Overview

**Fact Checking Forum** is a role-based academic information validation system designed to ensure clarity and accuracy in student-faculty communication.

It currently includes:
- A working **frontend interface** (HTML, CSS, JavaScript)
- A **Flask backend** integrated with **PostgreSQL**
- Role-based authentication for Students, Faculty, and Admins

---

## 🏗️ Tech Stack

| Layer | Technology |
|--------|-------------|
| **Frontend** | HTML5, CSS3, JavaScript |
| **Backend** | Python (Flask Framework) |
| **Database** | PostgreSQL |
| **Authentication** | Flask-JWT-Extended (JWT-based login system) |
| **Version Control** | Git + GitHub |

---

## ⚙️ Key Features

### 👩‍🎓 Student
- Post academic queries  
- View faculty responses  
- Track personal query history  

### 👨‍🏫 Faculty
- View student queries  
- Post multiple verified responses  
- Manage their own responses  

### 🧑‍💼 Admin
- Add, suspend, and delete users  
- Remove inappropriate queries/responses  
- Monitor system activity  

---

## 🕒 Recent Updates
✅ Added timestamps for queries and responses  
✅ Queries auto-delete associated responses when removed  
✅ Tabbed navigation for “Pending” and “Responded” queries  
✅ Clean UI notifications instead of pop-ups  
✅ Strengthened authentication and role-checking logic  

---

## 💾 Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/&lt;your-username&gt;/Fact-Checking-Forum.git
cd Fact-Checking-Forum
```

### 2️⃣ Create a virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Setup PostgreSQL
```sql
CREATE DATABASE fact_forum;
CREATE USER gokul WITH PASSWORD 'yourpassword';
GRANT ALL PRIVILEGES ON DATABASE fact_forum TO gokul;
```

Then update this line in **app.py**:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://gokul:yourpassword@localhost/fact_forum'
```

### 5️⃣ Run the backend
```bash
python3 app.py
```

Access it on:
👉 http://127.0.0.1:5050

---

## 📁 Folder Structure

```
Fact Checking Forum/
├── app.py
├── models.py
├── routes/
│   ├── auth_routes.py
│   ├── query_routes.py
├── index.html
├── .gitignore
└── README.md
```

---

## 🌱 Personal Notes

I built this project to deepen my understanding of **backend integration, role-based access, and database connectivity**.  
It started as a simple front-end prototype but evolved into a **full-stack educational tool** that reflects real-world web engineering practices.

This project helped me explore **authentication flows, Flask architecture, and PostgreSQL operations**, which I plan to extend later with AI-powered misinformation detection.

---

## 👨‍💻 Author

**Gokulakrishnan M**  
🎓 B.Tech Computer Science Student  
📍 Kanchipuram, Tamil Nadu  
📧 [your.email@example.com]  
🌐 [https://github.com/&lt;your-username&gt;](https://github.com/&lt;your-username&gt;)

---

