# 🎰 Lotto Stats Web App

A Python Flask app that fetches Lotto Max, Lotto 6/49, and Daily Grand results, tracks number frequencies, and supports secure user authentication with JWT.

---

## 🔧 Features

- ✅ Scrapes official lotto result pages
- 🔐 JWT-based login and registration
- 📊 Tracks frequency of drawn numbers
- 🕒 Background scheduler checks draw times (every 1 minute)
- 💾 Stores data in MySQL database
- 🔁 API-protected routes for fetching data

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Database:** MySQL
- **Scraping:** BeautifulSoup
- **Auth:** JWT (PyJWT)
- **Scheduler:** APScheduler
- **Config:** python-dotenv

---

## 🚀 Setup Instructions

### 1. Clone the Project

```bash
git clone https://github.com/yourusername/lotto-project.git
cd lotto-project
```

### 2. Create `.env` File

Inside the root folder:

```env
SECRET_KEY=your_secret_key_here
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_db_password
DB_NAME=lotto_db
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up the MySQL Database

Create the database manually or via script:

```sql
CREATE DATABASE lotto_db;
```

Create a `users` table:

```sql
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);
```

### 5. Run the App

```bash
python main.py
```

---

## 🔐 Authentication Endpoints

### ➕ Register

`POST /auth/register`

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

### 🔑 Login

`POST /auth/login`

```json
{
  "email": "user@example.com",
  "password": "yourpassword"
}
```

Returns:

```json
{
  "message": "Login successful",
  "token": "JWT_TOKEN_HERE"
}
```

Use the token in future requests:

```
Authorization: Bearer JWT_TOKEN_HERE
```

---

## 🎯 Lottery Routes

### Get Current Lotto Data

`GET /lottery`

Headers:

```
Authorization: Bearer JWT_TOKEN_HERE
```

### Get Stats

`GET /statistics`

---

## 🕒 Draw Schedule (Canada / Alberta Time)

| Lottery       | Draw Days           | Time     |
|---------------|---------------------|----------|
| Lotto Max     | Tuesday, Friday     | 10:30 PM |
| Lotto 6/49    | Wednesday, Saturday | 10:30 PM |
| Daily Grand   | Monday, Thursday    | 10:30 PM |

The scheduler runs every minute and checks whether to trigger a draw within a 2-hour window.

---

## 📌 Notes

- Test routes using Postman or Axios.
- Don't forget to pass the JWT in your `Authorization` header.
- This app is designed to run continuously (hosted or locally) for accurate scraping and scheduling.

---

## 🪪 License

MIT License

---

## 🤝 Contributions

Pull requests and issues are welcome!