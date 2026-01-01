#!/bin/bash
"""
Digital Ocean Automated News Scheduler Setup
Sets up cron job to run news scraping every 4 hours
"""

set -e  # Exit on any error

echo "🚀 Setting up Digital Ocean Automated News Scheduler"
echo "=================================================="

# Configuration
PROJECT_DIR="/opt/news-scraper"
PYTHON_PATH="/usr/bin/python3"
LOG_DIR="/var/log/news-scraper"
USER="www-data"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi

# Create project directory if it doesn't exist
if [ ! -d "$PROJECT_DIR" ]; then
    print_warning "Creating project directory: $PROJECT_DIR"
    mkdir -p "$PROJECT_DIR"
    chown $USER:$USER "$PROJECT_DIR"
fi

# Create log directory
print_status "Creating log directory: $LOG_DIR"
mkdir -p "$LOG_DIR"
chown $USER:$USER "$LOG_DIR"

# Copy project files to deployment directory
print_status "Copying project files to $PROJECT_DIR"
cp -r . "$PROJECT_DIR/"
chown -R $USER:$USER "$PROJECT_DIR"

# Install Python dependencies
print_status "Installing Python dependencies"
cd "$PROJECT_DIR"
pip3 install -r requirements.txt

# Create systemd service for the scheduler
print_status "Creating systemd service"
cat > /etc/systemd/system/news-scheduler.service << EOF
[Unit]
Description=Automated News Scheduler
After=network.target

[Service]
Type=oneshot
User=$USER
WorkingDirectory=$PROJECT_DIR
Environment=PATH=/usr/bin:/usr/local/bin
ExecStart=$PYTHON_PATH automated_news_scheduler.py
StandardOutput=append:$LOG_DIR/scheduler.log
StandardError=append:$LOG_DIR/scheduler-error.log

[Install]
WantedBy=multi-user.target
EOF

# Create systemd timer for every 4 hours
print_status "Creating systemd timer (every 4 hours)"
cat > /etc/systemd/system/news-scheduler.timer << EOF
[Unit]
Description=Run News Scheduler every 4 hours
Requires=news-scheduler.service

[Timer]
OnCalendar=*-*-* 00,04,08,12,16,20:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

# Reload systemd and enable timer
print_status "Enabling systemd timer"
systemctl daemon-reload
systemctl enable news-scheduler.timer
systemctl start news-scheduler.timer

# Create cron job as backup (in case systemd is not preferred)
print_status "Creating cron job backup"
cat > /etc/cron.d/news-scheduler << EOF
# Automated News Scheduler - Every 4 hours
0 */4 * * * $USER cd $PROJECT_DIR && $PYTHON_PATH automated_news_scheduler.py >> $LOG_DIR/cron.log 2>&1
EOF

# Set proper permissions
chmod 644 /etc/cron.d/news-scheduler

# Create log rotation configuration
print_status "Setting up log rotation"
cat > /etc/logrotate.d/news-scheduler << EOF
$LOG_DIR/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $USER $USER
}
EOF

# Create monitoring script
print_status "Creating monitoring script"
cat > "$PROJECT_DIR/check_scheduler_status.py" << 'EOF'
#!/usr/bin/env python3
"""
Check News Scheduler Status
Monitors the automated news scheduler and reports status
"""

import subprocess
import sys
import os
from datetime import datetime, timedelta

def check_systemd_timer():
    """Check if systemd timer is active"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'news-scheduler.timer'], 
                              capture_output=True, text=True)
        return result.returncode == 0 and result.stdout.strip() == 'active'
    except:
        return False

def check_recent_logs():
    """Check if scheduler has run recently"""
    log_file = '/var/log/news-scraper/scheduler.log'
    if not os.path.exists(log_file):
        return False, "Log file not found"
    
    try:
        # Check if there's a log entry in the last 5 hours
        cutoff_time = datetime.now() - timedelta(hours=5)
        
        with open(log_file, 'r') as f:
            lines = f.readlines()
            
        for line in reversed(lines[-100:]):  # Check last 100 lines
            if 'Starting scheduled scrape' in line:
                # Extract timestamp (assuming format: YYYY-MM-DD HH:MM:SS)
                try:
                    timestamp_str = line.split(' - ')[0]
                    timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
                    if timestamp > cutoff_time:
                        return True, f"Last run: {timestamp_str}"
                except:
                    continue
        
        return False, "No recent runs found"
    except Exception as e:
        return False, f"Error reading logs: {e}"

def main():
    print("🔍 News Scheduler Status Check")
    print("=" * 40)
    
    # Check systemd timer
    timer_active = check_systemd_timer()
    print(f"Systemd Timer: {'✅ Active' if timer_active else '❌ Inactive'}")
    
    # Check recent logs
    recent_run, message = check_recent_logs()
    print(f"Recent Activity: {'✅' if recent_run else '❌'} {message}")
    
    # Check next scheduled run
    try:
        result = subprocess.run(['systemctl', 'list-timers', 'news-scheduler.timer'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'news-scheduler.timer' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        next_run = f"{parts[0]} {parts[1]}"
                        print(f"Next Scheduled: ⏰ {next_run}")
                    break
    except:
        print("Next Scheduled: ❓ Unable to determine")
    
    print("=" * 40)
    
    # Overall status
    if timer_active and recent_run:
        print("✅ Scheduler is working properly")
        return 0
    elif timer_active:
        print("⚠️  Timer active but no recent activity")
        return 1
    else:
        print("❌ Scheduler is not running")
        return 2

if __name__ == "__main__":
    sys.exit(main())
EOF

chmod +x "$PROJECT_DIR/check_scheduler_status.py"

# Create environment file template
print_status "Creating environment template"
cat > "$PROJECT_DIR/.env.template" << EOF
# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here

# DeepSeek AI API (Optional - for AI filtering)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Logging Level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
EOF

# Test the scheduler once
print_status "Testing scheduler (dry run)"
cd "$PROJECT_DIR"
sudo -u $USER $PYTHON_PATH -c "
import sys
sys.path.append('.')
from automated_news_scheduler import AutomatedNewsScheduler
scheduler = AutomatedNewsScheduler()
print('✅ Scheduler initialized successfully')
"

# Show status
print_status "Setup completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy your .env file to $PROJECT_DIR/.env"
echo "2. Test the scheduler: sudo -u $USER $PYTHON_PATH $PROJECT_DIR/automated_news_scheduler.py"
echo "3. Check status: $PYTHON_PATH $PROJECT_DIR/check_scheduler_status.py"
echo "4. View logs: tail -f $LOG_DIR/scheduler.log"
echo ""
echo "⏰ Schedule: Every 4 hours (00:00, 04:00, 08:00, 12:00, 16:00, 20:00 UTC)"
echo "📊 Target: 100 articles per run with enhanced duplicate detection"
echo "🤖 AI filtering: Enabled if DEEPSEEK_API_KEY is configured"
echo ""
echo "🔧 Management Commands:"
echo "  Start timer:  systemctl start news-scheduler.timer"
echo "  Stop timer:   systemctl stop news-scheduler.timer"
echo "  Check status: systemctl status news-scheduler.timer"
echo "  View logs:    journalctl -u news-scheduler.service -f"
echo ""
print_status "Digital Ocean Automated News Scheduler is ready!"