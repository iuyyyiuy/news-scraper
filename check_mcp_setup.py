"""
Check MCP Setup and Provide Installation Instructions
"""

import subprocess
import sys


def check_uvx():
    """Check if uvx is installed"""
    try:
        result = subprocess.run(['uvx', '--version'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("✅ uvx is installed")
            print(f"   Version: {result.stdout.strip()}")
            return True
        else:
            print("❌ uvx command failed")
            return False
    except FileNotFoundError:
        print("❌ uvx is not installed")
        return False
    except Exception as e:
        print(f"❌ Error checking uvx: {e}")
        return False


def check_coinex_mcp():
    """Check if CoinEx MCP server is accessible"""
    try:
        result = subprocess.run(
            ['uvx', 'coinex-mcp-server', '--help'],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print("✅ CoinEx MCP server is accessible")
            return True
        else:
            print("❌ CoinEx MCP server not accessible")
            return False
    except Exception as e:
        print(f"❌ Error checking CoinEx MCP: {e}")
        return False


def print_installation_instructions():
    """Print installation instructions"""
    print("\n" + "="*60)
    print("INSTALLATION INSTRUCTIONS")
    print("="*60 + "\n")
    
    print("To analyze ZEROLEND market, you need to install UV:\n")
    
    print("Option 1: Using the install script (Recommended)")
    print("-" * 60)
    print("curl -LsSf https://astral.sh/uv/install.sh | sh\n")
    
    print("Option 2: Using Homebrew (macOS)")
    print("-" * 60)
    print("brew install uv\n")
    
    print("Option 3: Using pip")
    print("-" * 60)
    print("pip install uv\n")
    
    print("After installation:")
    print("-" * 60)
    print("1. Restart your terminal or run: source ~/.zshrc")
    print("2. Verify: uvx --version")
    print("3. Run: python analyze_zerolend_market.py\n")


def main():
    print("\n" + "="*60)
    print("MCP SETUP CHECK")
    print("="*60 + "\n")
    
    print("Checking MCP dependencies...\n")
    
    uvx_ok = check_uvx()
    
    if uvx_ok:
        print()
        coinex_ok = check_coinex_mcp()
        
        if coinex_ok:
            print("\n" + "="*60)
            print("✅ ALL CHECKS PASSED")
            print("="*60 + "\n")
            print("You can now run: python analyze_zerolend_market.py\n")
            return 0
    
    print_installation_instructions()
    
    print("="*60)
    print("For more details, see: ZEROLEND_ANALYSIS_SETUP.md")
    print("="*60 + "\n")
    
    return 1


if __name__ == "__main__":
    sys.exit(main())
