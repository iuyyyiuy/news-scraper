#!/bin/bash
"""
Bulletproof One-Click Deployment Script for Digital Ocean Droplet 143.198.219.220
This script does everything automatically with comprehensive error checking
"""

set -e  # Exit on any error

echo "🚀 Starting Bulletproof Deployment to Digital Ocean Droplet"
echo "=========================================================="

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Error handling function
handle_error() {
    print_error "Error occurred in step: $1"
    print_error "Command failed: $2"
    exit 1
}

# Step 1: Check if running as root
print_info "Step 1: Checking permissions..."
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root (use sudo)"
    exit 1
fi
print_status "Running as root"

# Step 2: Update system and install dependencies
print_info "Step 2: Installing system dependencies..."
apt update || handle_error "System update" "apt update"
apt install -y git python3 python3-pip curl wget unzip || handle_error "Package installation" "apt install"
print_status "System dependencies installed"

# Step 3: Check Python version
print_info "Step 3: Checking Python version..."
python3 --version || handle_error "Python check" "python3 --version"
pip3 --version || handle_error "Pip check" "pip3 --version"
print_status "Python and pip are working"

# Step 4: Set up project directory
print_info "Step 4: Setting up project directory..."
cd /opt || handle_error "Directory navigation" "cd /opt"

# Remove existing directory if it exists
if [ -d "news-scraper" ]; then
    print_warning "Removing existing news-scraper directory..."
    rm -rf news-scraper || handle_error "Directory cleanup" "rm -rf news-scraper"
fi

# Clone repository with error handling
print_info "Cloning repository from GitHub..."
if ! git clone https://github.com/iuyyyiuy/news-scraper.git; then
    print_error "Git clone failed. Trying alternative method..."
    # Alternative: download as ZIP
    wget https://github.com/iuyyyiuy/news-scraper/archive/main.zip || handle_error "Download" "wget"
    unzip main.zip || handle_error "Unzip" "unzip main.zip"
    mv news-scraper-main news-scraper || handle_error "Rename" "mv news-scraper-main news-scraper"
    rm main.zip
    print_status "Repository downloaded as ZIP"
else
    print_status "Repository cloned successfully"
fi

# Enter directory
cd news-scraper || handle_error "Enter directory" "cd news-scraper"
print_status "Entered project directory: $(pwd)"

# Step 5: Verify critical files exist
print_info "Step 5: Verifying critical files..."
critical_files=(
    "automated_news_scheduler.py"
    "setup_digital_ocean_scheduler.sh"
    "requirements.txt"
    ".env.example"
    "scraper/core/database_manager.py"
    "scraper/core/multi_source_scraper.py"
)

for file in "${critical_files[@]}"; do
    if [ ! -f "$file" ]; then
        handle_error "File verification" "Missing critical file: $file"
    fi
done
print_status "All critical files verified"

# Step 6: Create environment file
print_info "Step 6: Creating environment file..."
cp .env.example .env || handle_error "Environment file creation" "cp .env.example .env"
print_status "Environment file created"

# Step 7: Install Python dependencies with virtual environment (fixes PEP 668 issue)
print_info "Step 7: Setting up Python virtual environment..."

# Create virtual environment to bypass PEP 668 restrictions
python3 -m venv venv || handle_error "Virtual environment creation" "python3 -m venv venv"
source venv/bin/activate || handle_error "Virtual environment activation" "source venv/bin/activate"

# Now install dependencies in virtual environment
pip install --upgrade pip || handle_error "Pip upgrade in venv" "pip install --upgrade pip"

# Install requirements with retry logic
for i in {1..3}; do
    if pip install -r requirements.txt; then
        print_status "Python dependencies installed successfully in virtual environment"
        break
    else
        print_warning "Attempt $i failed, retrying..."
        if [ $i -eq 3 ]; then
            handle_error "Python dependencies" "pip install -r requirements.txt"
        fi
        sleep 2
    fi
done

# Create activation script for easy use
cat > activate_env.sh << 'EOF'
#!/bin/bash
cd /opt/news-scraper
source venv/bin/activate
echo "✅ Virtual environment activated"
echo "📋 You can now run: python3 automated_news_scheduler.py"
EOF
chmod +x activate_env.sh

# Step 8: Test core imports in virtual environment
print_info "Step 8: Testing core imports in virtual environment..."
source venv/bin/activate
python3 -c "
import sys
sys.path.append('.')
try:
    from scraper.core.database_manager import DatabaseManager
    from scraper.core.multi_source_scraper import MultiSourceScraper
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
" || handle_error "Core imports" "Python import test"

# Step 9: Make scripts executable
print_info "Step 9: Making scripts executable..."
chmod +x setup_digital_ocean_scheduler.sh || handle_error "Make executable" "chmod +x setup_digital_ocean_scheduler.sh"
chmod +x automated_news_scheduler.py || handle_error "Make executable" "chmod +x automated_news_scheduler.py"
chmod +x check_scheduler_status.py || handle_error "Make executable" "chmod +x check_scheduler_status.py"
print_status "Scripts made executable"

# Step 10: Set proper ownership
print_info "Step 10: Setting proper ownership..."
chown -R www-data:www-data /opt/news-scraper || handle_error "Set ownership" "chown -R www-data:www-data /opt/news-scraper"
print_status "Ownership set to www-data"

print_status "🎉 Bulletproof deployment preparation completed!"
echo ""
echo "📋 NEXT STEPS (IMPORTANT):"
echo "=========================================="
echo "1. Edit environment file with your credentials:"
echo "   nano /opt/news-scraper/.env"
echo ""
echo "2. Add your Supabase credentials:"
echo "   SUPABASE_URL=https://your-project.supabase.co"
echo "   SUPABASE_KEY=your_supabase_anon_key"
echo "   DEEPSEEK_API_KEY=your_deepseek_key  # Optional"
echo ""
echo "3. Activate virtual environment and test:"
echo "   cd /opt/news-scraper"
echo "   source venv/bin/activate"
echo "   python3 automated_news_scheduler.py"
echo ""
echo "4. Set up systemd service (after testing):"
echo "   sudo ./setup_digital_ocean_scheduler.sh"
echo ""
echo "🔧 Quick Command Sequence:"
echo "cd /opt/news-scraper && nano .env"
echo "source venv/bin/activate"
echo "python3 automated_news_scheduler.py"
echo ""
print_status "System is ready for configuration! Virtual environment bypasses PEP 668 restrictions."