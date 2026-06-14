# Deployment Guide: MediPredict AI

This guide describes how to deploy the MediPredict AI platform to a production environment (such as an Ubuntu VPS) using a secure configuration with Gunicorn, Nginx, and MySQL.

---

## 1. System Requirements

- **Server OS**: Ubuntu 22.04 LTS or similar Linux distribution
- **Web Server**: Nginx
- **Application Gateway**: Gunicorn (Green Unicorn WSGI)
- **Database**: MySQL Server 8.0+

---

## 2. Server Setup & Dependencies

Update your system packages and install the necessary system dependencies:
```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3-pip python3-dev python3-venv mysql-server nginx git -y
```

---

## 3. Database Production Setup

Secure your MySQL installation and create the database and user:
```bash
sudo mysql_secure_installation
```
Log in to the MySQL shell:
```bash
sudo mysql -u root -p
```
Run the following SQL commands to set up the database:
```sql
CREATE DATABASE medipredict CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'medipredict_user'@'localhost' IDENTIFIED BY 'a_secure_database_password';
GRANT ALL PRIVILEGES ON medipredict.* TO 'medipredict_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

## 4. Application Configuration

Clone your repository to the server (e.g., in `/var/www/medipredict/`) and set up your environment:
```bash
cd /var/www/
sudo git clone https://github.com/yourusername/medipredict.git
cd medipredict

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create your production `.env` file:
```bash
nano .env
```
Add the production settings:
```ini
SECRET_KEY=generate_a_long_cryptographic_random_string
DB_USER=medipredict_user
DB_PASSWORD=a_secure_database_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=medipredict

# Production SMTP Config
MAIL_SERVER=smtp.sendgrid.net
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=apikey
MAIL_PASSWORD=your_smtp_api_key
MAIL_DEFAULT_SENDER=noreply@yourdomain.com
```

---

## 5. Train Machine Learning Models
Train the models in the production environment:
```bash
python3 train_models.py
```
This generates the serialized models in `/var/www/medipredict/models/` and seeds the database performance tables.

---

## 6. Configure Gunicorn Service

Create a systemd service file to manage Gunicorn:
```bash
sudo nano /etc/systemd/system/medipredict.service
```
Paste the service configuration:
```ini
[Unit]
Description=Gunicorn instance to serve MediPredict AI
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/medipredict
Environment="PATH=/var/www/medipredict/venv/bin"
ExecStart=/var/www/medipredict/venv/bin/gunicorn --workers 3 --bind unix:medipredict.sock -m 007 app:app

[Install]
WantedBy=multi-user.target
```
Start and enable the service:
```bash
sudo systemctl start medipredict
sudo systemctl enable medipredict
```

---

## 7. Configure Nginx Reverse Proxy

Create an Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/medipredict
```
Paste the server configuration (replace `yourdomain.com` with your actual domain or server IP):
```nginx
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/medipredict/medipredict.sock;
    }

    location /static/ {
        alias /var/www/medipredict/static/;
    }

    # Enable client max body size for report downloads
    client_max_body_size 10M;
}
```
Enable the site and restart Nginx:
```bash
sudo ln -s /etc/nginx/sites-available/medipredict /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 8. Configure Firewall (Optional)

Allow standard HTTP and HTTPS traffic through the firewall:
```bash
sudo ufw allow 'Nginx Full'
```

---

## 9. Security (SSL/TLS Setup)

Secure your traffic with a free SSL certificate from Let's Encrypt using Certbot:
```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```
Follow the prompts to enable HTTPS redirects. Your MediPredict AI application is now securely deployed and live!
