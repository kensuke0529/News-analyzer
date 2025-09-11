"""
Unified News Loader - Handles multiple news sources including MIT AI News and Techmeme
"""
import os
import json
import sys
from datetime import datetime
from pathlib import Path

# Import individual loaders
from news_loader import (
    fetch_mit_news, 
    
    get_week_tag, 
    get_articles_for_week as get_mit_articles_for_week,
    save_weekly_articles_with_summary as save_mit_weekly_articles,
    tag_weekly_articles as tag_mit_weekly_articles
)
from techmeme_loader import (
    fetch_techmeme_news,
    get_articles_for_week as get_techmeme_articles_for_week,
    save_weekly_articles_with_summary as save_techmeme_weekly_articles
)

def load_all_news_sources(max_articles_per_source=10):
    """Load news from all configured sources"""
    print("=" * 60)
    print("UNIFIED NEWS LOADER - Fetching from all sources")
    print("=" * 60)
    
    all_articles = []
    sources_summary = {}
    
    # Fetch from MIT AI News
    print("\n📰 Fetching MIT AI News...")
    try:
        mit_data = fetch_mit_news(max_articles=max_articles_per_source)
        if mit_data.get("news_text"):
            sources_summary["MIT AI News"] = "✅ Success"
        else:
            sources_summary["MIT AI News"] = "⚠️ No new articles"
    except Exception as e:
        print(f"❌ Error fetching MIT AI News: {e}")
        sources_summary["MIT AI News"] = f"❌ Error: {e}"
    
    # Fetch from Techmeme
    print("\n📰 Fetching Techmeme News...")
    try:
        techmeme_data = fetch_techmeme_news(max_articles=max_articles_per_source)
        if techmeme_data.get("news_text"):
            sources_summary["Techmeme"] = "✅ Success"
        else:
            sources_summary["Techmeme"] = "⚠️ No new articles"
    except Exception as e:
        print(f"❌ Error fetching Techmeme News: {e}")
        sources_summary["Techmeme"] = f"❌ Error: {e}"
    
    # Print summary
    print("\n" + "=" * 60)
    print("FETCH SUMMARY:")
    for source, status in sources_summary.items():
        print(f"  {source}: {status}")
    print("=" * 60)
    
    return sources_summary

def create_combined_weekly_data(week_tag=None):
    """Create a combined weekly JSON file with articles from all sources"""
    if week_tag is None:
        week_tag = get_week_tag()
    
    print(f"\n🔄 Creating combined weekly data for {week_tag}...")
    
    # Get articles from all sources
    all_articles = []
    
    # MIT AI News articles
    try:
        mit_articles = get_mit_articles_for_week(week_tag)
        for article in mit_articles:
            article["source"] = "MIT AI News"
        all_articles.extend(mit_articles)
        print(f"  📰 MIT AI News: {len(mit_articles)} articles")
    except Exception as e:
        print(f"  ❌ Error loading MIT articles: {e}")
    
    # Techmeme articles
    try:
        techmeme_articles = get_techmeme_articles_for_week(week_tag)
        for article in techmeme_articles:
            article["source"] = "Techmeme"
        all_articles.extend(techmeme_articles)
        print(f"  📰 Techmeme: {len(techmeme_articles)} articles")
    except Exception as e:
        print(f"  ❌ Error loading Techmeme articles: {e}")
    
    if not all_articles:
        print(f"  ⚠️ No articles found for week {week_tag}")
        return
    
    # Generate summaries for articles that don't have them
    from news_loader import summarize_news, parse_article_date
    articles_with_summaries = []
    
    for article in all_articles:
        if not article.get("summary"):
            print(f"  📝 Generating summary for: {article.get('title', 'Unknown')}")
            summary_obj = summarize_news(
                article.get("title", ""),
                article.get("content", ""),
                article.get("link", ""),
                article.get("date", ""),
                article.get("week"),
                save_to_file=False
            )
            article["summary"] = summary_obj.get("summary", "")
        
        articles_with_summaries.append(article)
    
    # Sort all articles by date (newest first)
    articles_with_summaries.sort(key=lambda x: parse_article_date(x.get("date", "")) or datetime.min, reverse=True)
    
    # Create combined weekly structure
    from news_loader import get_week_start_end
    start_of_week, end_of_week = get_week_start_end()
    
    combined_data = {
        "week": week_tag,
        "start_of_week": start_of_week.isoformat(),
        "end_of_week": end_of_week.isoformat(),
        "article_count": len(articles_with_summaries),
        "sources": list(set(article.get("source", "Unknown") for article in articles_with_summaries)),
        "articles": articles_with_summaries
    }
    
    # Save combined file
    output_file = f"../../data/combined-week-{week_tag}.json"
    os.makedirs("../../data", exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(combined_data, f, ensure_ascii=False, indent=4)
    
    print(f"  ✅ Combined weekly data saved: {output_file}")
    print(f"  📊 Total articles: {len(articles_with_summaries)}")
    print(f"  📰 Sources: {', '.join(combined_data['sources'])}")
    
    return combined_data

def process_all_sources_for_week(week_tag=None):
    """Process all sources and create individual weekly files plus combined file"""
    if week_tag is None:
        week_tag = get_week_tag()
    
    print(f"\n🔄 Processing all sources for week {week_tag}...")
    
    # Process MIT AI News
    print("\n📰 Processing MIT AI News...")
    try:
        save_mit_weekly_articles(week_tag)
    except Exception as e:
        print(f"  ❌ Error processing MIT AI News: {e}")
    
    # Process Techmeme
    print("\n📰 Processing Techmeme...")
    try:
        save_techmeme_weekly_articles(week_tag)
    except Exception as e:
        print(f"  ❌ Error processing Techmeme: {e}")
    
    # Create combined file
    print("\n🔄 Creating combined weekly file...")
    try:
        create_combined_weekly_data(week_tag)
    except Exception as e:
        print(f"  ❌ Error creating combined file: {e}")

def list_available_weeks():
    """List all available weeks across all sources"""
    print("\n📅 Available weeks across all sources:")
    
    data_dir = Path("../../data")
    if not data_dir.exists():
        print("  ❌ Data directory not found")
        return
    
    # Check for different weekly file types
    weekly_files = {
        "MIT AI News": [],
        "Techmeme": [],
        "Combined": []
    }
    
    for file_path in data_dir.glob("week-*.json"):
        week_tag = file_path.stem.replace("week-", "")
        weekly_files["MIT AI News"].append((week_tag, file_path))
    
    for file_path in data_dir.glob("techmeme-week-*.json"):
        week_tag = file_path.stem.replace("techmeme-week-", "")
        weekly_files["Techmeme"].append((week_tag, file_path))
    
    for file_path in data_dir.glob("combined-week-*.json"):
        week_tag = file_path.stem.replace("combined-week-", "")
        weekly_files["Combined"].append((week_tag, file_path))
    
    # Display results
    for source, files in weekly_files.items():
        if files:
            print(f"\n  📰 {source}:")
            for week_tag, file_path in sorted(files, reverse=True):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        article_count = len(data.get("articles", []))
                        print(f"    {week_tag}: {article_count} articles")
                except Exception as e:
                    print(f"    {week_tag}: Error reading file ({e})")
        else:
            print(f"\n  📰 {source}: No weekly files found")

def main():
    """Main function to handle command line arguments"""
    if len(sys.argv) < 2:
        print("Unified News Loader - Manage multiple news sources")
        print("\nUsage:")
        print("  python3 unified_news_loader.py fetch                    - Fetch from all sources")
        print("  python3 unified_news_loader.py process [week]           - Process specific week (default: current)")
        print("  python3 unified_news_loader.py combined [week]          - Create combined weekly file")
        print("  python3 unified_news_loader.py list                     - List available weeks")
        print("  python3 unified_news_loader.py tag                      - Tag all articles with week info")
        print("\nExamples:")
        print("  python3 unified_news_loader.py fetch")
        print("  python3 unified_news_loader.py process 2025-W35")
        print("  python3 unified_news_loader.py combined 2025-W35")
        return
    
    command = sys.argv[1].lower()
    
    if command == "fetch":
        load_all_news_sources()
        
    elif command == "process":
        week_tag = sys.argv[2] if len(sys.argv) > 2 else None
        process_all_sources_for_week(week_tag)
        
    elif command == "combined":
        week_tag = sys.argv[2] if len(sys.argv) > 2 else None
        create_combined_weekly_data(week_tag)
        
    elif command == "list":
        list_available_weeks()
        
    elif command == "tag":
        print("Tagging MIT AI News articles with week information...")
        tag_mit_weekly_articles()
        print("✅ Week tagging completed")
        
    else:
        print(f"❌ Unknown command: {command}")
        print("Run without arguments to see usage information")

if __name__ == "__main__":
    main()
