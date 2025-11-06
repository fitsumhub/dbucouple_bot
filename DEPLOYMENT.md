# 🚀 Professional Deployment Guide

Complete guide for deploying your University Connect Bot in production.

## 📋 Pre-Deployment Checklist

- [ ] All features tested
- [ ] Environment variables configured
- [ ] Database backups enabled
- [ ] Logging configured
- [ ] Error handling verified
- [ ] Rate limiting configured
- [ ] Admin IDs set

## 🔧 Environment Configuration

Create a `.env` file with production settings:

```env
# Required
BOT_TOKEN=your_production_bot_token

# Database
DB_PATH=university_connect.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60
RATE_LIMIT_BAN_DURATION=300

# Admin (comma-separated user IDs)
ADMIN_IDS=123456789,987654321

# Backup Settings
BACKUP_ENABLED=true
BACKUP_INTERVAL_HOURS=24
BACKUP_RETENTION_DAYS=7
```

## 🖥️ Production Deployment Options

### Option 1: VPS (Virtual Private Server)

**Recommended Providers:**
- DigitalOcean
- AWS EC2
- Google Cloud Compute
- Azure VM

**Setup Steps:**

1. **SSH into server:**
   ```bash
   ssh user@your-server-ip
   ```

2. **Install Python:**
   ```bash
   sudo apt update
   sudo apt install python3.9 python3-pip
   ```

3. **Clone repository:**
   ```bash
   git clone your-repo-url
   cd university_connect_bot
   ```

4. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

5. **Configure environment:**
   ```bash
   cp env.example .env
   nano .env  # Edit with production values
   ```

6. **Run with systemd (recommended):**

   Create `/etc/systemd/system/university-bot.service`:
   ```ini
   [Unit]
   Description=University Connect Telegram Bot
   After=network.target

   [Service]
   Type=simple
   User=your-username
   WorkingDirectory=/path/to/university_connect_bot
   Environment="PATH=/usr/bin:/usr/local/bin"
   ExecStart=/usr/bin/python3 bot.py
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

   Enable and start:
   ```bash
   sudo systemctl enable university-bot
   sudo systemctl start university-bot
   sudo systemctl status university-bot
   ```

### Option 2: Docker Deployment

**Create `Dockerfile`:**
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "bot.py"]
```

**Create `docker-compose.yml`:**
```yaml
version: '3.8'

services:
  bot:
    build: .
    container_name: university-bot
    restart: always
    env_file:
      - .env
    volumes:
      - ./university_connect.db:/app/university_connect.db
      - ./logs:/app/logs
      - ./backups:/app/backups
```

**Run:**
```bash
docker-compose up -d
```

### Option 3: Cloud Platforms

#### Heroku
1. Install Heroku CLI
2. Create `Procfile`:
   ```
   worker: python bot.py
   ```
3. Deploy:
   ```bash
   heroku create your-bot-name
   heroku config:set BOT_TOKEN=your_token
   git push heroku main
   ```

#### Railway
1. Connect GitHub repository
2. Set environment variables
3. Deploy automatically

## 🔒 Security Best Practices

1. **Environment Variables:**
   - Never commit `.env` file
   - Use strong, unique bot tokens
   - Rotate tokens regularly

2. **Database Security:**
   - Regular backups
   - Secure file permissions
   - Consider encryption for sensitive data

3. **Rate Limiting:**
   - Configure appropriate limits
   - Monitor for abuse
   - Adjust based on usage

4. **Admin Access:**
   - Limit admin IDs
   - Use strong authentication
   - Monitor admin actions

## 📊 Monitoring & Maintenance

### Health Checks

Use `/health` command to check bot status:
- Database connectivity
- Table integrity
- Connection pool status

### Admin Commands

Admins can use:
- `/admin stats` - Bot statistics
- `/admin users` - User count
- `/admin user <id>` - User info
- `/admin reset <id>` - Reset rate limit

### Logs

Monitor logs regularly:
```bash
# View logs
tail -f logs/bot.log

# Search for errors
grep ERROR logs/bot.log

# Check recent activity
tail -n 100 logs/bot.log
```

### Database Maintenance

**Automatic:**
- Daily optimization
- Scheduled backups
- Old backup cleanup

**Manual:**
```python
from utils.database_utils import backup_database, optimize_database

# Create backup
backup_database()

# Optimize database
optimize_database()
```

## 🚨 Error Handling

The bot includes:
- Global error handler
- Graceful shutdown
- Automatic restarts (with systemd)
- Error logging
- User-friendly error messages

## 📈 Performance Optimization

1. **Database:**
   - Indexes on frequently queried columns
   - Regular VACUUM operations
   - Connection pooling

2. **Rate Limiting:**
   - Prevents abuse
   - Reduces server load
   - Improves stability

3. **Caching:**
   - Consider Redis for production
   - Cache frequently accessed data

## 🔄 Updates & Rollbacks

### Updating Bot

1. Stop bot:
   ```bash
   sudo systemctl stop university-bot
   ```

2. Backup database:
   ```bash
   cp university_connect.db backups/before-update.db
   ```

3. Pull updates:
   ```bash
   git pull origin main
   pip install -r requirements.txt
   ```

4. Start bot:
   ```bash
   sudo systemctl start university-bot
   ```

### Rollback

1. Stop bot
2. Restore database backup
3. Revert code changes
4. Restart bot

## 📞 Support & Troubleshooting

### Common Issues

**Bot not starting:**
- Check logs: `journalctl -u university-bot`
- Verify token is correct
- Check database permissions

**High memory usage:**
- Review rate limiting
- Check for memory leaks
- Optimize database

**Database errors:**
- Check disk space
- Verify file permissions
- Restore from backup if needed

### Getting Help

1. Check logs first
2. Review error messages
3. Test with `/health` command
4. Use admin commands for diagnostics

---

**Ready for Production! 🚀**

