# 💈 Bergas API - Barbershop Management System

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.3+-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/Status-Production-success)](https://bergas-api.muzaaqi.my.id)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

**The backbone of Bergas Barbershop ecosystem.** Secure, scalable, and fully documented REST API for seamless integration with barbershop management operations.

🌐 **Live API:** [bergas-api.muzaaqi.my.id](https://bergas-api.muzaaqi.my.id)  
🖥️ **Frontend Repository:** [barber-app-fe](https://github.com/muzaaqi/barber-app-fe)

---

## 📖 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Project Structure](#-project-structure)
- [Getting Started](#-getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Running the Application](#running-the-application)
- [API Documentation](#-api-documentation)
- [Authentication](#-authentication)
- [Deployment](#-deployment)
- [Contributing](#-contributing)
- [License](#-license)

---

## ✨ Features

### 👤 User Management
- **Authentication & Authorization** - Secure JWT-based authentication
- **User Profiles** - Comprehensive customer and barber profiles
- **Role-Based Access Control** - Admin, Barber, and Customer roles
- **Account Management** - Registration, login, password reset

### 🛍️ Product Catalog
- **Inventory Management** - Track barbershop products and supplies
- **Pricing Control** - Dynamic pricing and discount management
- **Stock Levels** - Real-time stock monitoring
- **Product Images** - Multi-image upload with Cloudflare R2 storage

### ✂️ Service Booking
- **Real-Time Scheduling** - Live availability checking for haircuts
- **Appointment Management** - Create, update, cancel bookings
- **Service Transactions** - Complete payment and booking flow
- **WebSocket Support** - Real-time booking updates

### 📊 Additional Features
- **Dashboard Analytics** - Revenue reports and business insights
- **Real-Time Notifications** - WebSocket-based live updates
- **Interactive API Docs** - Swagger UI documentation
- **Database Migration** - Version-controlled schema management
- **File Storage** - AWS S3-compatible storage with boto3

---

## 🛠 Tech Stack

### Backend Framework
- **Flask 2.3+** - Lightweight and flexible Python web framework
- **Python 3.9+** - Core programming language
- **Gevent** - High-performance coroutine-based networking library

### Database & ORM
- **MySQL** - Relational database
- **Flask-SQLAlchemy** - SQL toolkit and ORM
- **Flask-Migrate** - Database migration tool (Alembic wrapper)
- **PyMySQL** - Pure Python MySQL driver

### Storage & File Management
- **Boto3** - AWS SDK for Python (S3-compatible storage)
- **Cloudflare R2** - Object storage for images and media files

### Security & Authentication
- **Flask-JWT-Extended** - JWT authentication for Flask
- **Cryptography** - Secure password hashing and encryption

### Real-Time Communication
- **Flask-SocketIO** - WebSocket support for real-time features
- **Gevent** - Asynchronous event handling

### API Documentation
- **Flasgger** - Swagger UI integration for Flask

### Additional Tools
- **Flask-CORS** - Cross-Origin Resource Sharing support
- **python-dotenv** - Environment variable management

---

## 📁 Project Structure

```
barber-app-be/
│
├── app/                      # Main application package
│   ├── controllers/          # API route handlers & business logic
│   ├── models/              # SQLAlchemy models
│   ├── modules/             # Reusable utilities & helpers
│   ├── docs/                # API documentation schemas
│   ├── templates/           # HTML templates
│   └── __init__.py
│
├── migrations/              # Database migration files (Alembic)
│
├── main.py                  # Application entry point & Flask setup
├── config.py                # Configuration settings & env variables
├── r2_config.py             # Cloudflare R2/S3 storage configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
├── .gitignore              # Git ignore rules
└── README.md               # This file
```

### Key Components

- **`main.py`** - Initializes Flask application, registers blueprints, and configures middleware
- **`config.py`** - Centralized configuration management using environment variables
- **`r2_config.py`** - Handles Cloudflare R2/S3 connection and file upload operations
- **`app/controllers/`** - Contains all API endpoint definitions organized by resource
- **`app/models/`** - Database models using SQLAlchemy ORM
- **`app/modules/`** - Shared utilities like authentication, validation, and helpers
- **`migrations/`** - Database migration files managed by Flask-Migrate

---

## 🚀 Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** - Python package installer (comes with Python)
- **MySQL 5.7+** or **MariaDB** - Database server
- **Git** - Version control system
- **Cloudflare R2 Account** - For file storage (optional, S3-compatible)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/muzaaqi/barber-app-be.git
cd barber-app-be
```

2. **Create virtual environment**

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

### Configuration

1. **Create environment file**

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

2. **Configure environment variables**

Edit `.env` file with your settings:

```env
# Application Settings
FLASK_APP=main.py
FLASK_ENV=development
SECRET_KEY=your-super-secret-key-here-change-this
DEBUG=True

# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost:3306/bergas_db
# Or separate components:
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_username
DB_PASSWORD=your_password
DB_NAME=bergas_db

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ACCESS_TOKEN_EXPIRES=3600  # in seconds (1 hour)

# CORS Settings
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# AWS S3 / Cloudflare R2 Configuration
AWS_ACCESS_KEY_ID=your-access-key-id
AWS_SECRET_ACCESS_KEY=your-secret-access-key
AWS_REGION=auto
S3_BUCKET_NAME=bergas-media
S3_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
S3_PUBLIC_URL=https://your-bucket-url.r2.dev

# SocketIO Configuration
SOCKETIO_MESSAGE_QUEUE=redis://localhost:6379/0  # Optional
SOCKETIO_CORS_ALLOWED_ORIGINS=*

# Application URLs
FRONTEND_URL=http://localhost:3000
API_BASE_URL=http://localhost:5000
```

3. **Initialize database**

```bash
# Create database
mysql -u root -p
CREATE DATABASE bergas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;

# Initialize Flask-Migrate
flask db init  # Only first time

# Create initial migration
flask db migrate -m "Initial migration"

# Apply migration to database
flask db upgrade
```

### Running the Application

**Development Mode** (with auto-reload and debugging):

```bash
# Using Flask CLI
flask run --host=0.0.0.0 --port=5000

# Or using Python
python main.py
```

**Production Mode** (with Gevent):

```bash
# Using Gunicorn with Gevent worker
gunicorn --worker-class gevent --workers 4 --bind 0.0.0.0:5000 main:app

# Or with gevent-websocket for SocketIO
gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
  --workers 1 --bind 0.0.0.0:5000 main:app
```

The API will be available at: `http://localhost:5000`

---

## 📚 API Documentation

### Interactive Documentation

Once the server is running, access interactive Swagger UI documentation:

- **Swagger UI:** `http://localhost:5000/apidocs`
- **API Spec (JSON):** `http://localhost:5000/apispec_1.json`

The documentation is automatically generated using **Flasgger** and provides:
- Interactive API testing interface
- Request/response schemas
- Authentication examples
- Error code descriptions

### Documentation Portal

Visit the production landing page for the developer portal:
- **Developer Portal:** [bergas-api.muzaaqi.my.id](https://bergas-api.muzaaqi.my.id)

---

## 🔐 Authentication

This API uses **JWT (JSON Web Tokens)** via Flask-JWT-Extended for authentication.

### How to Authenticate

1. **Register or Login** to get an access token:

```bash
curl -X POST "http://localhost:5000/api/user/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "yourpassword"
  }'
```

2. **Response will contain a token:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "role": "customer"
  }
}
```

3. **Use the token in subsequent requests:**

```bash
curl -X GET "http://localhost:5000/api/user/me" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Protected Endpoints

Protected endpoints require JWT token in the Authorization header:

```
Authorization: Bearer <your-access-token>
```

### Token Refresh

Use refresh token to get a new access token without re-login:

```bash
curl -X POST "http://localhost:5000/api/user/refresh" \
  -H "Authorization: Bearer <your-refresh-token>"
```

---

## 🌐 Deployment

### Production Checklist

Before deploying to production:

- [ ] Set `FLASK_ENV=production` and `DEBUG=False`
- [ ] Use strong `SECRET_KEY` and `JWT_SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
- [ ] Configure production MySQL database with proper credentials
- [ ] Set up SSL/HTTPS certificate (Let's Encrypt)
- [ ] Configure proper CORS origins (remove wildcards)
- [ ] Enable rate limiting middleware
- [ ] Set up monitoring and logging (Sentry, DataDog, etc.)
- [ ] Configure automatic database backups
- [ ] Use proper WSGI server (Gunicorn with Gevent)
- [ ] Set up reverse proxy (Nginx or Caddy)
- [ ] Test all endpoints thoroughly

### Deployment Options

#### Option 1: VPS (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-venv nginx mysql-server -y

# Clone and setup
git clone https://github.com/muzaaqi/barber-app-be.git
cd barber-app-be
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn gevent

# Setup database
sudo mysql_secure_installation
sudo mysql -e "CREATE DATABASE bergas_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

# Run migrations
flask db upgrade

# Create systemd service
sudo nano /etc/systemd/system/bergas-api.service
```

**Systemd service file:**
```ini
[Unit]
Description=Bergas API
After=network.target mysql.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/barber-app-be
Environment="PATH=/var/www/barber-app-be/venv/bin"
ExecStart=/var/www/barber-app-be/venv/bin/gunicorn \
  --worker-class gevent \
  --workers 4 \
  --bind 127.0.0.1:5000 \
  --access-logfile /var/log/bergas-api/access.log \
  --error-logfile /var/log/bergas-api/error.log \
  main:app

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start bergas-api
sudo systemctl enable bergas-api

# Configure Nginx
sudo nano /etc/nginx/sites-available/bergas-api
```

**Nginx configuration:**
```nginx
server {
    listen 80;
    server_name bergas-api.muzaaqi.my.id;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /socket.io {
        proxy_pass http://127.0.0.1:5000/socket.io;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

```bash
# Enable site and restart Nginx
sudo ln -s /etc/nginx/sites-available/bergas-api /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Setup SSL with Certbot
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d bergas-api.muzaaqi.my.id
```

#### Option 2: Docker

**Dockerfile:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn gevent

# Copy application
COPY . .

# Run migrations and start server
CMD flask db upgrade && \
    gunicorn --worker-class gevent \
    --workers 4 \
    --bind 0.0.0.0:5000 \
    main:app
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    build: .
    ports:
      - "5000:5000"
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      - ./migrations:/app/migrations

  db:
    image: mysql:8.0
    environment:
      MYSQL_ROOT_PASSWORD: rootpassword
      MYSQL_DATABASE: bergas_db
    volumes:
      - mysql_data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  mysql_data:
```

```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f api
```

#### Option 3: Cloud Platforms

- **Railway:** `railway up` or connect via GitHub
- **Heroku:** `git push heroku main` (with Procfile)
- **Render:** Connect GitHub repo in dashboard
- **DigitalOcean App Platform:** Deploy from GitHub
- **AWS Elastic Beanstalk:** Use eb CLI

**Current Production:** Deployed at [bergas-api.muzaaqi.my.id](https://bergas-api.muzaaqi.my.id)

---

## 🗄️ Database Management

### Migrations

Using Flask-Migrate (Alembic):

```bash
# Create a new migration
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback last migration
flask db downgrade

# Show migration history
flask db history

# Show current revision
flask db current
```

### Backup Database

```bash
# Backup
mysqldump -u username -p bergas_db > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore
mysql -u username -p bergas_db < backup_20241228_120000.sql
```

---

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
4. **Push to the branch** (`git push origin feature/AmazingFeature`)
5. **Open a Pull Request**

### Coding Standards

- Follow **PEP 8** style guide for Python code
- Write clear **docstrings** for all functions and classes
- Add **type hints** where applicable
- Write **unit tests** for new features
- Update Swagger documentation when adding new endpoints
- Use meaningful commit messages

### Testing

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Developer

**Muzaaqi**

- 🌐 Website: [muzaaqi.my.id](https://muzaaqi.my.id)
- 💼 GitHub: [@muzaaqi](https://github.com/muzaaqi)
- 📧 Email: admin@bergas.com

---

## 🔗 Related Projects

- **Frontend Application:** [barber-app-fe](https://github.com/muzaaqi/barber-app-fe)
- **API Documentation:** [bergas-api.muzaaqi.my.id](https://bergas-api.muzaaqi.my.id)

---

## 📞 Support

Need help? Here's how to get support:

- 📖 **Documentation:** Check the [API docs](https://bergas-api.muzaaqi.my.id)
- 🐛 **Bug Reports:** [Create an issue](https://github.com/muzaaqi/barber-app-be/issues)
- 💬 **Questions:** [Open a discussion](https://github.com/muzaaqi/barber-app-be/discussions)
- 📧 **Email:** admin@bergas.com

---

## 🙏 Acknowledgments

- **Flask** - For the micro web framework
- **Cloudflare** - For reliable R2 storage
- **Python Community** - For amazing tools and libraries

---

<div align="center">

**Built with ❤️ by Muzaaqi**

⭐ Star this repo if you find it helpful!

</div>