"""
Command-line interface for the news scraper.
"""
import argparse
import sys
import signal
from typing import Optional

from scraper.core.config import load_config
from scraper.core.scraper import ScraperController
from scraper.core.logger import setup_logging
from scraper.core.models import Config


def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='News Website Scraper - Extract articles from news websites',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape with URL and defaults
  python -m scraper.main --url https://example.com/news
  
  # Scrape with custom settings
  python -m scraper.main --url https://example.com/news --max-articles 20 --output articles.json
  
  # Use configuration file
  python -m scraper.main --config config.json
  
  # Enable debug logging
  python -m scraper.main --url https://example.com/news --log-level DEBUG --log-file scraper.log
        """
    )
    
    # Configuration options
    parser.add_argument(
        '--url',
        type=str,
        help='Target URL to scrape (required unless using --config)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to JSON configuration file'
    )
    
    parser.add_argument(
        '--max-articles',
        type=int,
        default=10,
        help='Maximum number of articles to scrape (default: 10)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default='scraped_articles.json',
        help='Output file path (default: scraped_articles.json)'
    )
    
    parser.add_argument(
        '--output-format',
        type=str,
        choices=['json', 'csv'],
        default='json',
        help='Output format (default: json)'
    )
    
    parser.add_argument(
        '--delay',
        type=float,
        default=2.0,
        help='Delay between requests in seconds (default: 2.0)'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=30,
        help='Request timeout in seconds (default: 30)'
    )
    
    parser.add_argument(
        '--retries',
        type=int,
        default=3,
        help='Maximum number of retry attempts (default: 3)'
    )
    
    parser.add_argument(
        '--keywords',
        type=str,
        nargs='+',
        help='Filter articles by keywords (space-separated)'
    )
    
    # Logging options
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    parser.add_argument(
        '--log-file',
        type=str,
        help='Path to log file (optional, logs to console by default)'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress console output (only log to file if --log-file is specified)'
    )
    
    # Filtering options
    parser.add_argument(
        '--days',
        type=int,
        help='Only scrape articles from the last N days (e.g., --days 7 for last week)'
    )
    
    return parser.parse_args()


def create_config_from_args(args: argparse.Namespace) -> Config:
    """
    Create Config object from command-line arguments.
    
    Args:
        args: Parsed command-line arguments
        
    Returns:
        Config object
        
    Raises:
        ValueError: If required arguments are missing
    """
    # Load from config file if provided
    if args.config:
        config = load_config(args.config)
        
        # Override with command-line arguments if provided
        if args.url:
            config.target_url = args.url
        if args.max_articles != 10:  # Check if not default
            config.max_articles = args.max_articles
        if args.output != 'scraped_articles.json':
            config.output_path = args.output
        if args.output_format != 'json':
            config.output_format = args.output_format
        if args.delay != 2.0:
            config.request_delay = args.delay
        if args.timeout != 30:
            config.timeout = args.timeout
        if args.retries != 3:
            config.max_retries = args.retries
        if args.keywords:
            config.keywords = args.keywords
            
        return config
    
    # Create config from command-line arguments
    if not args.url:
        raise ValueError("--url is required when not using --config")
    
    config = Config(
        target_url=args.url,
        max_articles=args.max_articles,
        request_delay=args.delay,
        output_format=args.output_format,
        output_path=args.output,
        timeout=args.timeout,
        max_retries=args.retries,
        selectors={},
        keywords=args.keywords if args.keywords else []
    )
    
    config.validate()
    return config


def display_progress_header(config: Config) -> None:
    """
    Display scraping session header.
    
    Args:
        config: Configuration object
    """
    print("\n" + "=" * 70)
    print("NEWS SCRAPER")
    print("=" * 70)
    print(f"Target URL:      {config.target_url}")
    print(f"Max Articles:    {config.max_articles}")
    print(f"Output File:     {config.output_path}")
    print(f"Output Format:   {config.output_format}")
    print(f"Request Delay:   {config.request_delay}s")
    print("=" * 70)
    print()


def display_results(result) -> None:
    """
    Display scraping results summary.
    
    Args:
        result: ScrapingResult object
    """
    print("\n" + "=" * 70)
    print("SCRAPING RESULTS")
    print("=" * 70)
    print(f"Articles Found:    {result.total_articles_found}")
    print(f"Articles Scraped:  {result.articles_scraped}")
    print(f"Articles Failed:   {result.articles_failed}")
    print(f"Duration:          {result.duration_seconds:.2f} seconds")
    
    if result.errors:
        print(f"\nErrors ({len(result.errors)}):")
        for i, error in enumerate(result.errors[:5], 1):
            print(f"  {i}. {error}")
        if len(result.errors) > 5:
            print(f"  ... and {len(result.errors) - 5} more errors")
    
    print("=" * 70)
    
    # Display success/failure message
    if result.articles_scraped > 0:
        print(f"\n✅ Successfully scraped {result.articles_scraped} article(s)")
    else:
        print("\n❌ No articles were scraped")


def signal_handler(signum, frame):
    """
    Handle keyboard interrupt gracefully.
    
    Args:
        signum: Signal number
        frame: Current stack frame
    """
    print("\n\n⚠️  Scraping interrupted by user")
    print("Exiting gracefully...")
    sys.exit(0)


def main() -> int:
    """
    Main entry point for the CLI.
    
    Returns:
        Exit code (0 for success, 1 for error)
    """
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Parse arguments
        args = parse_arguments()
        
        # Set up logging
        setup_logging(
            log_level=args.log_level,
            log_file=args.log_file,
            console_output=not args.quiet
        )
        
        # Create configuration
        config = create_config_from_args(args)
        
        # Display progress header (if not quiet)
        if not args.quiet:
            display_progress_header(config)
        
        # Parse keywords if provided (already a list from nargs='+')
        keywords_list = args.keywords if args.keywords else None
        if keywords_list and not args.quiet:
            print(f"Keyword Filter:  {', '.join(keywords_list)}")
        
        # Display date filter if provided
        if args.days and not args.quiet:
            print(f"Date Filter:     Last {args.days} days")
            print("=" * 70)
            print()
        
        # Create and run scraper with filters
        scraper = ScraperController(
            config,
            days_filter=args.days,
            keywords_filter=keywords_list
        )
        result = scraper.scrape()
        
        # Display results (if not quiet)
        if not args.quiet:
            display_results(result)
            print(f"\n📄 Results saved to: {config.output_path}\n")
        
        # Return success if at least one article was scraped
        return 0 if result.articles_scraped > 0 else 1
        
    except ValueError as e:
        print(f"\n❌ Configuration Error: {e}", file=sys.stderr)
        return 1
    
    except FileNotFoundError as e:
        print(f"\n❌ File Error: {e}", file=sys.stderr)
        return 1
    
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
