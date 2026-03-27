# 🚀 Production Deployment Guide

This guide covers deploying the Enterprise Credit Risk Engine to production environments.

## Pre-Deployment Checklist

### ✅ Security

- [ ] Change default admin credentials in `config.py`
- [ ] Change Flask `SECRET_KEY` to a strong random value
- [ ] Remove or restrict demo user accounts
- [ ] Enable HTTPS/SSL
- [ ] Add rate limiting
- [ ] Implement CSRF protection
- [ ] Set up firewall rules
- [ ] Configure CORS if needed
- [ ] Add input validation and sanitization
- [ ] Set up logging and monitoring

### ✅ Configuration

- [ ] Set `FLASK_ENV=production`
- [ ] Configure proper database (if migrating from CSV)
- [ ] Set up backup strategy for data files
- [ ] Configure email service for notifications
- [ ] Set up CDN for static files (optional)
- [ ] Configure proper session management
- [ ] Set up environment variables

### ✅ Performance

- [ ] Use production WSGI server (Gunicorn/Waitress)
- [ ] Configure multiple workers
- [ ] Set up load balancing (if needed)
- [ ] Enable caching
- [ ] Optimize static file serving
- [ ] Set up database connection pooling (if using DB)

### ✅ Monitoring

- [ ] Set up application monitoring
- [ ] Configure error tracking (e.g., Sentry)
- [ ] Set up uptime monitoring
- [ ] Configure log aggregation
- [ ] Set up performance monitoring

## Deployment Options

### Option 1: Traditional Server (Linux)

#### Prerequisites

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3.8 python3-pip python3-venv nginx -y
```

#### Application Setup

```bash
# Create application directory
sudo mkdir -p /var/www/credit_risk_engine
cd /var/www/credit_risk_engine

# Copy application files
# (Upload your files here)

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install gunicorn

# Train models
python train_models.py

# Create service user
sudo useradd -r -s /bin/false creditrisk
sudo chown -R creditrisk:creditrisk /var/www/credit_risk_engine
```

#### Systemd Service

Create `/etc/systemd/system/creditrisk.service`:

```ini
[Unit]
Description=Credit Risk Engine
After=network.target

[Service]
User=creditrisk
Group=creditrisk
WorkingDirectory=/var/www/credit_risk_engine
Environment="PATH=/var/www/credit_risk_engine/venv/bin"
ExecStart=/var/www/credit_risk_engine/venv/bin/gunicorn \
    --workers 4 \
    --bind 127.0.0.1:8000 \
    --timeout 300 \
    --access-logfile /var/log/creditrisk/access.log \
    --error-logfile /var/log/creditrisk/error.log \
    app:app

Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Create log directory
sudo mkdir -p /var/log/creditrisk
sudo chown creditrisk:creditrisk /var/log/creditrisk

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable creditrisk
sudo systemctl start creditrisk
sudo systemctl status creditrisk
```

#### Nginx Configuration

Create `/etc/nginx/sites-available/creditrisk`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL Configuration (use Let's Encrypt)
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;

    # Static files
    location /static {
        alias /var/www/credit_risk_engine/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/creditrisk /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

#### SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

### Option 2: Docker Deployment

#### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Train models
RUN python train_models.py

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "300", "app:app"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./data:/app/data
      - ./models:/app/models
      - ./logs:/app/logs
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./static:/usr/share/nginx/html/static
      - ./certs:/etc/nginx/certs
    depends_on:
      - web
    restart: unless-stopped
```

#### Build and Run

```bash
# Build image
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

---

### Option 3: Cloud Platforms

#### AWS Elastic Beanstalk

1. Install EB CLI:
```bash
pip install awsebcli
```

2. Create `.ebextensions/python.config`:
```yaml
option_settings:
  aws:elasticbeanstalk:container:python:
    WSGIPath: app:app
```

3. Deploy:
```bash
eb init -p python-3.8 credit-risk-engine
eb create production-env
eb deploy
```

#### Heroku

1. Create `Procfile`:
```
web: gunicorn --timeout 300 app:app
```

2. Deploy:
```bash
heroku create credit-risk-engine
git push heroku main
heroku open
```

#### Google Cloud Run

1. Build and deploy:
```bash
gcloud run deploy credit-risk-engine \
    --source . \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated
```

---

## Environment Variables

Create `.env` file (don't commit this!):

```bash
FLASK_ENV=production
SECRET_KEY=your-super-secret-key-change-this
ADMIN_USERNAME=your_admin
ADMIN_PASSWORD=your_secure_password

# Optional
DATABASE_URL=postgresql://user:pass@host/db
REDIS_URL=redis://host:6379
SENTRY_DSN=https://...
```

Load in application:

```python
# In config.py
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-key')
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')
```

---

## Database Migration (Optional)

### Migrate from CSV to PostgreSQL

```python
# migration_script.py
import pandas as pd
from sqlalchemy import create_engine

# Read CSV
df = pd.read_csv('data/user_applications.csv')

# Connect to database
engine = create_engine('postgresql://user:pass@host/db')

# Write to database
df.to_sql('applications', engine, if_exists='replace', index=False)
```

---

## Monitoring Setup

### Application Monitoring (Example with Sentry)

```bash
pip install sentry-sdk[flask]
```

```python
# In app.py
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

### Health Check Endpoint

```python
# In app.py
@app.route('/health')
def health_check():
    return {'status': 'healthy', 'models_loaded': models_loaded}
```

---

## Backup Strategy

### Automated Backups

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups"

# Backup data
tar -czf $BACKUP_DIR/data_$DATE.tar.gz data/
tar -czf $BACKUP_DIR/models_$DATE.tar.gz models/

# Keep only last 30 days
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
```

Add to crontab:
```bash
0 2 * * * /path/to/backup.sh
```

---

## Performance Optimization

### Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/cached')
@cache.cached(timeout=300)
def cached_route():
    return expensive_operation()
```

### Connection Pooling

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

---

## Maintenance

### Model Retraining

Schedule periodic retraining:

```bash
# retrain.sh
#!/bin/bash
cd /var/www/credit_risk_engine
source venv/bin/activate
python train_models.py
sudo systemctl restart creditrisk
```

Add to crontab (monthly):
```bash
0 3 1 * * /path/to/retrain.sh
```

### Log Rotation

Configure `/etc/logrotate.d/creditrisk`:

```
/var/log/creditrisk/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 creditrisk creditrisk
    sharedscripts
    postrotate
        systemctl reload creditrisk > /dev/null 2>&1 || true
    endscript
}
```

---

## Troubleshooting Production Issues

### Check Logs

```bash
# Application logs
sudo journalctl -u creditrisk -f

# Nginx logs
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### Check Service Status

```bash
sudo systemctl status creditrisk
sudo systemctl status nginx
```

### Monitor Resources

```bash
htop
df -h
free -m
```

---

## Security Best Practices

1. **Keep software updated**
2. **Use strong passwords**
3. **Enable firewall**
4. **Regular security audits**
5. **Implement rate limiting**
6. **Use HTTPS only**
7. **Sanitize all inputs**
8. **Regular backups**
9. **Monitor logs**
10. **Have incident response plan**

---

## Support & Maintenance

For ongoing support:
- Monitor application logs
- Set up alerting
- Regular backups
- Security updates
- Performance monitoring
- User feedback collection

---

**Your application is now production-ready! 🚀**
