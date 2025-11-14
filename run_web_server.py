#!/usr/bin/env python
"""
Web server startup script for the news scraper.

This script starts the FastAPI web server that provides a user-friendly
interface for scraping news articles.
"""
import argparse
import sys
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='News Scraper Web Server',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start server on default port (localhost:5000)
  python run_web_server.py
  
  # Start server on custom port
  python run_web_server.py --port 8000
  
  # Allow access from network (use with caution)
  python run_web_server.py --host 0.0.0.0 --port 5000
  
  # Enable auto-reload for development
  python run_web_server.py --reload
        """
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='127.0.0.1',
        help='Host to bind to (default: 127.0.0.1 for localhost only)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=5000,
        help='Port to bind to (default: 5000)'
    )
    
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Enable auto-reload for development (watches for file changes)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--workers',
        type=int,
        default=1,
        help='Number of worker processes (default: 1)'
    )
    
    return parser.parse_args()


def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import fastapi
        import uvicorn
        logger.info("✓ FastAPI and Uvicorn are installed")
        return True
    except ImportError as e:
        logger.error("✗ Missing required dependencies")
        logger.error("Please install them with: pip install fastapi uvicorn")
        return False


def check_templates():
    """Check if template files exist."""
    template_path = Path("scraper/templates/index.html")
    if not template_path.exists():
        logger.warning(f"⚠ Template file not found: {template_path}")
        logger.warning("The web interface may not work correctly")
        return False
    logger.info("✓ Template files found")
    return True


def display_startup_info(host: str, port: int):
    """Display startup information."""
    print("\n" + "=" * 70)
    print("NEWS SCRAPER WEB SERVER")
    print("=" * 70)
    print(f"Server starting on: http://{host}:{port}")
    
    if host == "127.0.0.1" or host == "localhost":
        print(f"\n📱 Access the web interface at:")
        print(f"   http://localhost:{port}")
        print(f"\n🔒 Server is only accessible from this computer (secure)")
    else:
        print(f"\n📱 Access the web interface at:")
        print(f"   http://{host}:{port}")
        print(f"   http://localhost:{port}")
        print(f"\n⚠️  WARNING: Server is accessible from the network!")
        print(f"   Make sure your firewall is configured properly.")
    
    print(f"\n📚 API Documentation:")
    print(f"   http://localhost:{port}/docs")
    print(f"\n💡 Tips:")
    print(f"   - Press Ctrl+C to stop the server")
    print(f"   - Share the URL with your teammates")
    print(f"   - Check logs for scraping progress")
    print("=" * 70)
    print()


def main():
    """Main entry point."""
    args = parse_arguments()
    
    # Set logging level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    logger.info("Starting News Scraper Web Server...")
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    # Check templates
    check_templates()
    
    # Display startup info
    display_startup_info(args.host, args.port)
    
    try:
        # Import uvicorn here to avoid import errors if not installed
        import uvicorn
        
        # Start the server
        uvicorn.run(
            "scraper.web_api:app",
            host=args.host,
            port=args.port,
            reload=args.reload,
            log_level=args.log_level.lower(),
            workers=args.workers if not args.reload else 1,
            access_log=True
        )
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Server stopped by user")
        print("Shutting down gracefully...")
        return 0
    
    except Exception as e:
        logger.error(f"Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
