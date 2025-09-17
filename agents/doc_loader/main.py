
import os
import json
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from news_loader import *
from techmeme_loader import *
from unified_news_loader import *
from pathlib import Path
from datetime import datetime, timedelta
import time

load_dotenv()
OPEN_AI_KEY = os.environ.get("OPENAI_API_KEY")

llm = ChatOpenAI(model="gpt-4o-mini", api_key=OPEN_AI_KEY)
output_parser = StrOutputParser()
rss_url = "https://news.mit.edu/topic/mitartificial-intelligence2-rss.xml"

def _sleep_until(target_dt: datetime):
    """Sleep until the specified datetime (local time)."""
    now = datetime.now()
    seconds = (target_dt - now).total_seconds()
    if seconds > 0:
        time.sleep(seconds)

def _next_run_datetime(hour: int, minute: int = 0) -> datetime:
    """Get the next datetime (today or tomorrow) at the specified local time."""
    now = datetime.now()
    candidate = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if candidate <= now:
        candidate = candidate + timedelta(days=1)
    return candidate

def main():
    """Main function to run the news processing pipeline"""
    try:
        # Get current week tag
        current_week = get_week_tag()
        print(f"🕐 Current week: {current_week}")
        print("=" * 50)
        
        # Step 1: Fetch and process news from all sources
        print("📰 Step 1: Fetching news from all sources...")
        sources_summary = load_all_news_sources(max_articles_per_source=5)
        
        # Check if we got any new articles from any source
        has_new_articles = any("Success" in status for status in sources_summary.values())
        if has_new_articles:
            print("✅ New articles fetched from news sources")
        else:
            print("⚠️  No new articles found from any source")

        # Step 2: Tag articles with week information
        print("\n🏷️  Step 2: Tagging articles with week information...")
        tag_weekly_articles()
        print("✅ Weekly tagging completed")

        # Step 3: Generate combined weekly JSON with summaries from all sources
        print(f"\n📅 Step 3: Generating combined weekly summary for {current_week}...")
        create_combined_weekly_data(current_week)
        print("✅ Combined weekly JSON with summaries completed")


        print(f"\n🎉 Pipeline completed successfully for week {current_week}!")

    except Exception as e:
        print(f"❌ Error in main function: {e}")
        import traceback
        traceback.print_exc()


def run_daily(hour: int = 7, minute: int = 0):
    """Run the pipeline every day in the morning at the given local time.

    Defaults to 07:00 local time. Adjust hour/minute if needed.
    """
    print("=" * 50)
    print(f"⏰ Daily scheduler started. Will run every day at {hour:02d}:{minute:02d} (local time).")
    print("Press Ctrl+C to stop.")
    print("=" * 50)
    try:
        while True:
            next_run = _next_run_datetime(hour, minute)
            print(f"🕗 Next run scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
            _sleep_until(next_run)
            print("\n🚀 Starting scheduled run...")
            try:
                main()
            except Exception as run_err:
                print(f"❌ Scheduled run failed: {run_err}")
            # After run, schedule the next day
            # Small sleep to avoid tight loop in case run finished exactly at boundary
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Daily scheduler stopped by user.")


if __name__ == "__main__":
    import sys
    
    # Handle command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "auto":
            # Run the full automated pipeline
            main()
        elif command == "daily":
            # Run the pipeline every morning at a specified time
            # Usage examples:
            #   python3 main.py daily            -> runs at 07:00
            #   python3 main.py daily 8         -> runs at 08:00
            #   python3 main.py daily 6 30      -> runs at 06:30
            hour = 7
            minute = 0
            if len(sys.argv) >= 3:
                try:
                    hour = int(sys.argv[2])
                except ValueError:
                    pass
            if len(sys.argv) >= 4:
                try:
                    minute = int(sys.argv[3])
                except ValueError:
                    pass
            run_daily(hour=hour, minute=minute)
        elif command == "news":
            # Only run news processing (steps 1-3)
            print("🕐 Running news processing only...")
            current_week = get_week_tag()
            print(f"Current week: {current_week}")
            
            # Step 1: Fetch and process news from all sources
            print("📰 Step 1: Fetching news from all sources...")
            sources_summary = load_all_news_sources(max_articles_per_source=5)
            
            # Check if we got any new articles from any source
            has_new_articles = any("Success" in status for status in sources_summary.values())
            if has_new_articles:
                print("✅ New articles fetched from news sources")
            else:
                print("⚠️  No new articles found from any source")
            
            # Step 2: Tag articles with week information
            print("\n🏷️  Step 2: Tagging articles with week information...")
            tag_weekly_articles()
            print("✅ Weekly tagging completed")
            
            # Step 3: Generate combined weekly JSON with summaries from all sources
            print(f"\n📅 Step 3: Generating combined weekly summary for {current_week}...")
            create_combined_weekly_data(current_week)
            print("✅ Combined weekly JSON with summaries completed")
            
            
        elif command == "week":
            # Process a specific week
            if len(sys.argv) < 3:
                print("❌ Please specify week tag (e.g., 2025-W35)")
                print("Usage:")
                print("  python3 main.py week <week-tag>")
                sys.exit(1)
            
            week_tag = sys.argv[2]
            print(f"🕐 Processing specific week: {week_tag}")
            
            # Generate combined weekly summary for specified week from all sources
            print(f"📅 Generating combined weekly summary for {week_tag}...")
            create_combined_weekly_data(week_tag)
            print("✅ Combined weekly summary generated")
            
                
        elif command == "fetch":
            # Only fetch from all news sources
            print("📰 Fetching from all news sources...")
            sources_summary = load_all_news_sources(max_articles_per_source=10)
            print("✅ Fetch completed")
            
        elif command == "combined":
            # Create combined weekly file
            week_tag = sys.argv[2] if len(sys.argv) > 2 else None
            if week_tag:
                print(f"🔄 Creating combined weekly file for {week_tag}...")
                create_combined_weekly_data(week_tag)
            else:
                print("🔄 Creating combined weekly file for current week...")
                create_combined_weekly_data()
            print("✅ Combined weekly file created")
            
        elif command == "list":
            # List available weeks
            list_available_weeks()
                
        else:
            print("Usage:")
            print("  python3 main.py auto          - Run full automated pipeline (all sources)")
            print("  python3 main.py daily [h] [m] - Run daily at h:m (default 07:00)")
            print("  python3 main.py news          - Run news processing only (all sources)")
            print("  python3 main.py week <week>   - Process specific week (all sources)")
            print("  python3 main.py fetch         - Fetch from all news sources only")
            print("  python3 main.py combined      - Create combined weekly file")
            print("  python3 main.py list          - List available weeks")
            sys.exit(1)
    else:
        # Default: run full automated pipeline
        main()