#!/usr/bin/env python3
"""
Deploy Market Analysis System

Quick setup script for the market analysis functionality.
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def run_command(command, description):
    """Run a shell command with error handling"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"   stdout: {e.stdout}")
        if e.stderr:
            print(f"   stderr: {e.stderr}")
        return False

def check_file_exists(filepath, description):
    """Check if a file exists"""
    if Path(filepath).exists():
        print(f"✅ {description} exists: {filepath}")
        return True
    else:
        print(f"❌ {description} missing: {filepath}")
        return False

def check_mcp_config():
    """Check MCP configuration"""
    print("\n🔍 Checking MCP Configuration...")
    
    # Check for MCP config file
    mcp_config_paths = [
        ".kiro/settings/mcp.json",
        os.path.expanduser("~/.kiro/settings/mcp.json")
    ]
    
    config_found = False
    for config_path in mcp_config_paths:
        if Path(config_path).exists():
            print(f"✅ Found MCP config: {config_path}")
            config_found = True
            
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    
                if 'mcpServers' in config:
                    servers = config['mcpServers']
                    print(f"   Configured servers: {list(servers.keys())}")
                    
                    # Check for CoinEx server
                    if any('coinex' in server.lower() for server in servers.keys()):
                        print("✅ CoinEx MCP server configured")
                    else:
                        print("⚠️  CoinEx MCP server not found in config")
                        
            except Exception as e:
                print(f"❌ Error reading MCP config: {e}")
            break
    
    if not config_found:
        print("❌ No MCP configuration found")
        print("   Please set up MCP configuration first")
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")
    
    directories = [
        "logs",
        "exports",
        "scraper/static/js",
        "scraper/templates",
        "scraper/api"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory ready: {directory}")

def check_dependencies():
    """Check Python dependencies"""
    print("\n📦 Checking dependencies...")
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "asyncio",
        "requests"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ {package} installed")
        except ImportError:
            print(f"❌ {package} missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        print("   Install with: pip install " + " ".join(missing_packages))
        return False
    
    return True

def verify_files():
    """Verify all required files exist"""
    print("\n📄 Verifying files...")
    
    required_files = [
        ("scraper/templates/market_analysis.html", "Market Analysis HTML template"),
        ("scraper/static/js/market_analysis.js", "Market Analysis JavaScript"),
        ("scraper/api/market_analysis_routes.py", "Market Analysis API routes"),
        ("trade_risk_analyzer/market_monitoring/futures_analyzer.py", "Futures Analyzer"),
        ("trade_risk_analyzer/market_monitoring/mcp_client.py", "MCP Client"),
        ("test_market_analysis_system.py", "Test script"),
        ("MARKET_ANALYSIS_GUIDE.md", "Documentation")
    ]
    
    all_files_exist = True
    for filepath, description in required_files:
        if not check_file_exists(filepath, description):
            all_files_exist = False
    
    return all_files_exist

def test_system():
    """Run basic system tests"""
    print("\n🧪 Running system tests...")
    
    # Test MCP connection
    if Path("test_coinex_mcp.py").exists():
        print("Testing MCP connection...")
        if run_command("python test_coinex_mcp.py", "MCP connection test"):
            print("✅ MCP connection working")
        else:
            print("⚠️  MCP connection test failed - check configuration")
    
    # Test imports
    print("Testing Python imports...")
    test_imports = [
        "from scraper.api.market_analysis_routes import router",
        "from trade_risk_analyzer.market_monitoring.futures_analyzer import FuturesAnalyzer",
        "from trade_risk_analyzer.market_monitoring.mcp_client import MCPClient"
    ]
    
    for import_test in test_imports:
        try:
            exec(import_test)
            print(f"✅ Import successful: {import_test.split('import')[1].strip()}")
        except Exception as e:
            print(f"❌ Import failed: {import_test}")
            print(f"   Error: {e}")

def main():
    """Main deployment function"""
    print("=" * 80)
    print("🚀 Market Analysis System Deployment")
    print("=" * 80)
    
    # Check current directory
    if not Path("scraper").exists():
        print("❌ Please run this script from the project root directory")
        return False
    
    success = True
    
    # Step 1: Setup directories
    setup_directories()
    
    # Step 2: Check dependencies
    if not check_dependencies():
        success = False
    
    # Step 3: Verify files
    if not verify_files():
        success = False
    
    # Step 4: Check MCP configuration
    if not check_mcp_config():
        success = False
    
    # Step 5: Test system
    if success:
        test_system()
    
    print("\n" + "=" * 80)
    if success:
        print("🎉 Market Analysis System Deployment Complete!")
        print("=" * 80)
        print("\n📋 Next Steps:")
        print("1. Start the web server:")
        print("   python run_web_server.py")
        print("\n2. Open your browser and visit:")
        print("   http://localhost:8000/market-analysis")
        print("\n3. Configure monitoring settings and start analysis")
        print("\n4. Run comprehensive tests:")
        print("   python test_market_analysis_system.py")
        print("\n📚 Documentation:")
        print("   See MARKET_ANALYSIS_GUIDE.md for detailed usage instructions")
    else:
        print("❌ Deployment encountered issues")
        print("=" * 80)
        print("\n🔧 Please fix the issues above and run the deployment again")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Deployment interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Deployment failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)