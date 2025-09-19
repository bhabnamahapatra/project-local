import argparse
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

from openai import collect_openai_metrics
from copilot import collect_copilot_metrics
from cursor import collect_cursor_metrics
from claude import collect_claude_metrics

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('collector.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def run_collect(days_back: int = 7, collect_openai: bool = True, collect_copilot: bool = True,
               collect_claude: bool = True, collect_cursor: bool = True) -> dict:
    """Run all enabled collectors"""
    try:
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days_back - 1)

        # Format dates for different API requirements
        since = start_date.isoformat()
        until = end_date.isoformat()

        results = {}

        # OpenAI Metrics
        if collect_openai:
            try:
                result = collect_openai_metrics(start_date=since, end_date=until)
                logger.info("✅ OpenAI metrics collected successfully")
                results['openai'] = {"success": True}
            except Exception as e:
                logger.error(f"❌ Error collecting OpenAI metrics: {str(e)}")
                results['openai'] = {"success": False, "error": str(e)}

        # Copilot Metrics
        if collect_copilot:
            try:
                result = collect_copilot_metrics(start_date=since, end_date=until)
                logger.info("✅ Copilot metrics collected successfully")
                results['copilot'] = {"success": True}
            except Exception as e:
                logger.error(f"❌ Error collecting Copilot metrics: {str(e)}")
                results['copilot'] = {"success": False, "error": str(e)}

        # Claude Metrics
        if collect_claude:
            try:
                result = collect_claude_metrics(start_date=since, end_date=until)
                logger.info("✅ Claude metrics collected successfully")
                results['claude'] = {"success": True}
            except Exception as e:
                logger.error(f"❌ Error collecting Claude metrics: {str(e)}")
                results['claude'] = {"success": False, "error": str(e)}

        # Cursor Metrics
        if collect_cursor:
            try:
                result = collect_cursor_metrics(start_date=since, end_date=until)
                logger.info("✅ Cursor metrics collected successfully")
                results['cursor'] = {"success": True}
            except Exception as e:
                logger.error(f"❌ Error collecting Cursor metrics: {str(e)}")
                results['cursor'] = {"success": False, "error": str(e)}

        # Log summary
        success_count = sum(1 for r in results.values() if r.get('success', False))
        total_count = len([k for k, v in locals().items() if k.startswith('collect_') and v])
        logger.info(f"Metrics collection completed. {success_count}/{total_count} collectors succeeded.")

        return {
            "success": success_count == total_count,
            "results": results,
            "summary": {
                "total_collectors": total_count,
                "successful_collectors": success_count,
                "collection_timestamp": datetime.utcnow().isoformat()
            }
        }

    except Exception as e:
        logger.error(f"❌ Critical error in collection process: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "results": results if 'results' in locals() else {}
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Collect metrics from various AI services')
    parser.add_argument("--days", type=int, default=7, help="Number of days to collect data for")
    parser.add_argument("--openai", action="store_true", help="Collect OpenAI metrics")
    parser.add_argument("--copilot", action="store_true", help="Collect GitHub Copilot metrics")
    parser.add_argument("--claude", action="store_true", help="Collect Claude metrics")
    parser.add_argument("--cursor", action="store_true", help="Collect Cursor metrics")
    parser.add_argument("--once", action="store_true", help="Run collector only once and exit")
    parser.add_argument("--interval", type=int, default=1800, help="Collection interval in seconds (default: 1800)")

    args = parser.parse_args()

    # If no specific service is selected, collect from all
    collect_all = not (args.openai or args.copilot or args.claude or args.cursor)
    collect_openai = args.openai or collect_all
    collect_copilot = args.copilot or collect_all
    collect_claude = args.claude or collect_all
    collect_cursor = args.cursor or collect_all

    logger.info(
        f"Starting collector with configuration: days_back={args.days}, "
        f"openai={collect_openai}, copilot={collect_copilot}, "
        f"claude={collect_claude}, cursor={collect_cursor}"
    )

    if args.once:
        result = run_collect(
            days_back=args.days,
            collect_openai=collect_openai,
            collect_copilot=collect_copilot,
            collect_claude=collect_claude,
            collect_cursor=collect_cursor
        )
        print(f"Collection completed: {result['success']}")
    else:
        while True:
            try:
                result = run_collect(
                    days_back=args.days,
                    collect_openai=collect_openai,
                    collect_copilot=collect_copilot,
                    collect_claude=collect_claude,
                    collect_cursor=collect_cursor
                )
                logger.info(f"Collection cycle completed. Success: {result['success']}")
                logger.info(f"Sleeping for {args.interval} seconds before next collection...")
                time.sleep(args.interval)
            except KeyboardInterrupt:
                logger.info("Collector stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in collection loop: {str(e)}")
                logger.info("Retrying in 60 seconds...")
                time.sleep(60)
