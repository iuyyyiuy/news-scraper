# Deployment Checklist

Use this checklist to deploy the News Scraper web interface for your team.

## Pre-Deployment

### ✅ System Requirements

- [ ] Python 3.8 or higher installed
- [ ] pip package manager available
- [ ] Virtual environment created (recommended)
- [ ] Network access for team members (if needed)

### ✅ Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# Verify FastAPI and Uvicorn
pip list | grep -E "fastapi|uvicorn"
```

- [ ] All dependencies installed
- [ ] No installation errors

### ✅ File Verification

```bash
# Check all required files exist
ls scraper/web_api.py
ls scraper/templates/index.html
ls run_web_server.py
```

- [ ] Web API file exists
- [ ] HTML template exists
- [ ] Startup script exists

### ✅ Configuration

Edit `scraper/web_api.py` if needed:

```python
DEFAULT_CONFIG = {
    "target_url": "https://your-news-site.com",  # Update this
    "max_articles": 50,
    "request_delay": 2.0,
    "timeout": 30,
    "max_retries": 3,
    "selectors": {}  # Add custom selectors if needed
}
```

- [ ] Target URL configured
- [ ] Max articles set appropriately
- [ ] Request delay configured
- [ ] Custom selectors added (if needed)

## Testing

### ✅ Local Testing

```bash
# Start server
python run_web_server.py

# In another terminal, test health endpoint
curl http://localhost:5000/health
```

- [ ] Server starts without errors
- [ ] Health endpoint responds
- [ ] Web interface loads in browser
- [ ] Can submit a test search
- [ ] Progress updates work
- [ ] CSV download works

### ✅ API Testing

```bash
# Run API tests
python test_web_api.py
```

- [ ] All API tests pass
- [ ] No errors in output

### ✅ Session Management Testing

```bash
# Run session tests
python test_session_management.py
```

- [ ] All session tests pass
- [ ] No errors in output

## Deployment Options

### Option 1: Local Deployment (Single Computer)

**Best for**: Personal use or single-user scenarios

```bash
# Start server (localhost only)
python run_web_server.py
```

- [ ] Server running on localhost:5000
- [ ] Accessible at http://localhost:5000
- [ ] Documented for user

**Security**: ✅ Secure (localhost only)

---

### Option 2: Team Deployment (Local Network)

**Best for**: Small teams on same network

1. **Find your IP address:**
   ```bash
   # Mac/Linux
   ifconfig | grep "inet "
   
   # Windows
   ipconfig
   ```
   Example: `192.168.1.100`

2. **Start server with network access:**
   ```bash
   python run_web_server.py --host 0.0.0.0 --port 5000
   ```

3. **Share URL with team:**
   ```
   http://192.168.1.100:5000
   ```

**Checklist:**
- [ ] IP address identified
- [ ] Server started with --host 0.0.0.0
- [ ] Firewall allows port 5000
- [ ] Team members can access URL
- [ ] Multiple users tested simultaneously

**Security**: ⚠️ Accessible on network - ensure firewall configured

---

### Option 3: Production Deployment (Server)

**Best for**: Larger teams or permanent deployment

1. **Set up systemd service (Linux):**

   Create `/etc/systemd/system/news-scraper.service`:
   ```ini
   [Unit]
   Description=News Scraper Web Service
   After=network.target

   [Service]
   Type=simple
   User=your-user
   WorkingDirectory=/path/to/project
   Environment="PATH=/path/to/venv/bin"
   ExecStart=/path/to/venv/bin/python run_web_server.py --host 0.0.0.0 --port 5000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start service:**
   ```bash
   sudo systemctl enable news-scraper
   sudo systemctl start news-scraper
   sudo systemctl status news-scraper
   ```

**Checklist:**
- [ ] Service file created
- [ ] Service enabled
- [ ] Service starts automatically
- [ ] Logs accessible via journalctl
- [ ] Restart on failure configured

**Security**: ⚠️ Configure firewall, consider HTTPS, add authentication

---

### Option 4: Docker Deployment

**Best for**: Containerized environments

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   EXPOSE 5000
   
   CMD ["python", "run_web_server.py", "--host", "0.0.0.0", "--port", "5000"]
   ```

2. **Build and run:**
   ```bash
   docker build -t news-scraper .
   docker run -p 5000:5000 news-scraper
   ```

**Checklist:**
- [ ] Dockerfile created
- [ ] Image builds successfully
- [ ] Container runs
- [ ] Port mapping works
- [ ] Data persistence configured (if needed)

---

## Post-Deployment

### ✅ User Training

- [ ] Share Quick Start Guide with team
- [ ] Demonstrate basic usage
- [ ] Show example searches
- [ ] Explain CSV file format
- [ ] Provide support contact

**Documents to share:**
- `WEB_INTERFACE_QUICK_START.md` - For non-technical users
- `EXAMPLE_USAGE.md` - For real-world scenarios
- `README.md` - For general information

### ✅ Monitoring

Set up monitoring for:

- [ ] Server uptime
- [ ] Error logs
- [ ] Disk space (for CSV files)
- [ ] Memory usage
- [ ] Active sessions

**Log locations:**
- Application logs: Check console output or `--log-file` location
- System logs: `/var/log/syslog` or `journalctl -u news-scraper`

### ✅ Maintenance

Schedule regular maintenance:

- [ ] Weekly: Check logs for errors
- [ ] Weekly: Clean up old CSV files
- [ ] Monthly: Update dependencies
- [ ] Monthly: Review and update CSS selectors
- [ ] Quarterly: Review usage patterns

**Maintenance commands:**
```bash
# Check for old sessions
curl http://localhost:5000/api/sessions

# Clean up old sessions
curl -X DELETE http://localhost:5000/api/sessions/cleanup

# Update dependencies
pip install --upgrade -r requirements.txt
```

### ✅ Backup

Set up backups for:

- [ ] Configuration files
- [ ] Custom CSS selectors
- [ ] Scraped data (if needed)
- [ ] User documentation

**Backup script example:**
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
tar -czf backup_${DATE}.tar.gz \
  scraper/web_api.py \
  scraper/templates/ \
  example_config.json \
  *.md
```

## Security Checklist

### ✅ Network Security

- [ ] Firewall configured
- [ ] Only necessary ports open
- [ ] HTTPS configured (for production)
- [ ] Rate limiting enabled
- [ ] DDoS protection (if public-facing)

### ✅ Application Security

- [ ] Input validation enabled
- [ ] Session IDs are secure (UUID v4)
- [ ] Old sessions cleaned up automatically
- [ ] Error messages don't leak sensitive info
- [ ] Dependencies up to date

### ✅ Data Security

- [ ] Scraped data stored securely
- [ ] Access logs maintained
- [ ] Data retention policy defined
- [ ] Backup encryption (if needed)
- [ ] GDPR compliance (if applicable)

## Troubleshooting

### Common Issues

**Server won't start:**
```bash
# Check if port is in use
lsof -i :5000

# Try different port
python run_web_server.py --port 8000
```

**Can't access from other computers:**
```bash
# Check firewall
sudo ufw status  # Linux
# Or check Windows Firewall settings

# Verify server is listening on 0.0.0.0
netstat -an | grep 5000
```

**High memory usage:**
```bash
# Check active sessions
curl http://localhost:5000/api/sessions

# Clean up old sessions
curl -X DELETE http://localhost:5000/api/sessions/cleanup

# Restart server
sudo systemctl restart news-scraper
```

## Support

### For Users

- Quick Start Guide: `WEB_INTERFACE_QUICK_START.md`
- Example Usage: `EXAMPLE_USAGE.md`
- FAQ: See README.md

### For Administrators

- Technical Guide: `WEB_INTERFACE_GUIDE.md`
- API Documentation: http://localhost:5000/docs
- Implementation Details: `IMPLEMENTATION_COMPLETE.md`

### Getting Help

1. Check the documentation
2. Review logs for errors
3. Test with curl commands
4. Check GitHub issues (if applicable)
5. Contact development team

## Rollback Plan

If deployment fails:

1. **Stop the service:**
   ```bash
   # Systemd
   sudo systemctl stop news-scraper
   
   # Docker
   docker stop news-scraper
   
   # Manual
   Ctrl+C or kill process
   ```

2. **Restore from backup:**
   ```bash
   tar -xzf backup_YYYYMMDD.tar.gz
   ```

3. **Revert to previous version:**
   ```bash
   git checkout previous-version
   pip install -r requirements.txt
   ```

4. **Test before redeploying:**
   ```bash
   python test_web_api.py
   python test_session_management.py
   ```

## Success Criteria

Deployment is successful when:

- [ ] Server starts without errors
- [ ] Web interface loads in browser
- [ ] Users can submit searches
- [ ] Progress updates work in real-time
- [ ] CSV files download correctly
- [ ] Multiple users can use simultaneously
- [ ] No critical errors in logs
- [ ] Team members trained
- [ ] Documentation distributed
- [ ] Monitoring in place

## Sign-Off

- [ ] Deployment completed by: ________________
- [ ] Date: ________________
- [ ] Tested by: ________________
- [ ] Approved by: ________________

---

**Congratulations!** Your News Scraper web interface is now deployed and ready for use! 🎉
