from pathlib import Path
import os
import json
from dotenv import load_dotenv
from langchain.schema import Document
from langchain_huggingface.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma

from pathlib import Path
import shutil

load_dotenv()
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
    
# Initialize embeddings
model_name = "sentence-transformers/all-mpnet-base-v2"  
embeddings = HuggingFaceEmbeddings(model_name=model_name)

# Create or load vector store
vector_store = Chroma(
    collection_name="example_collection",
    embedding_function=embeddings,
    persist_directory="./chroma_langchain_db",
)

def news_embedding(data_file, week_tag=None):
    if not data_file.exists():
        raise FileNotFoundError(f"Data file not found: {data_file}")

    with open(data_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Extract week tag from filename if not provided
    if week_tag is None:
        week_tag = data_file.stem.replace("week-", "").replace("combined-week-", "")

    # Get all existing links in the vector store
    # Use metadata 'link' to detect duplicates
    existing_links = set()
    try:
        # Chroma stores metadata in _collection internally
        existing_metadatas = vector_store._collection.get()["metadatas"]
        for meta in existing_metadatas:
            if meta and meta.get("link"):  # Added None check
                existing_links.add(meta["link"])
    except Exception:
        pass  # First run, nothing exists yet

    docs_to_add = []
    for item in data.get("articles", []):
        source = item.get('source', 'Unknown')
        content = f"title: {item['title']} | summary: {item['summary']} | link: {item['link']} | source: {source}"
        if item['link'] in existing_links:
            print(f"Already exists: {item['title']}")
        else:
            print(f"New: {item['title']}")
            docs_to_add.append(Document(
                page_content=content,
                metadata={
                    "link": item['link'],
                    "week": week_tag,
                    "title": item['title'],
                    "source": source
                }
            ))

    if docs_to_add:
        vector_store.add_documents(docs_to_add)
        print(f"Added {len(docs_to_add)} new documents to vector store.")
    else:
        print("No new documents to add.")

    print(f"Vector store saved to: {os.path.abspath('./chroma_langchain_db')}")

def get_week_tag():
    """Get current week tag"""
    from datetime import datetime
    year, week, _ = datetime.now().isocalendar()
    return f"{year}-W{week:02d}"

def load_all_articles():
    """Load all available articles from data directory"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    all_articles = []
    
    print(f"Looking for data files in: {data_dir}")
    
    # Load general news file
    general_file = data_dir / "mit_ai_news.json"
    if general_file.exists():
        print(f"Loading general news from: {general_file}")
        with open(general_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle both list format and object with articles key
            if isinstance(data, list):
                articles = data
            else:
                articles = data.get("articles", [])
            
            for article in articles:
                article["week"] = "all"
                all_articles.append(article)
        print(f"Loaded {len(articles)} articles from general news")
    
    # Load combined weekly files first (preferred - includes all sources)
    combined_files = list(data_dir.glob("combined-week-*.json"))
    print(f"Found {len(combined_files)} combined weekly files")
    
    for file_path in combined_files:
        week_name = file_path.stem.replace("combined-week-", "")
        print(f"Loading combined week {week_name} from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle both list format and object with articles key
            if isinstance(data, list):
                articles = data
            else:
                articles = data.get("articles", [])
            
            for article in articles:
                article["week"] = week_name
                all_articles.append(article)
        print(f"Loaded {len(articles)} articles from combined week {week_name}")
    
    # Load individual weekly files (fallback)
    weekly_files = list(data_dir.glob("week-*.json"))
    print(f"Found {len(weekly_files)} individual weekly files")
    
    for file_path in weekly_files:
        week_name = file_path.stem.replace("week-", "")
        # Skip if we already loaded this week from combined files
        if any(f"combined-week-{week_name}.json" in str(f) for f in combined_files):
            print(f"Skipping individual week {week_name} (already loaded from combined file)")
            continue
            
        print(f"Loading individual week {week_name} from: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Handle both list format and object with articles key
            if isinstance(data, list):
                articles = data
            else:
                articles = data.get("articles", [])
            
            for article in articles:
                article["week"] = week_name
                all_articles.append(article)
        print(f"Loaded {len(articles)} articles from individual week {week_name}")
    
    print(f"Total articles loaded: {len(all_articles)}")
    return all_articles

def initialize_vector_store():
    """Initialize vector store with all available articles"""
    try:
        # Check if vector store already has data
        try:
            existing_count = vector_store._collection.count()
            if existing_count > 0:
                print(f"Vector store already initialized with {existing_count} documents")
                return
        except Exception:
            pass
        
        all_articles = load_all_articles()
        if not all_articles:
            print("No articles found to embed")
            return
        
        docs_to_add = []
        for article in all_articles:
            # Get summary or description, fallback to content if neither exists
            summary = article.get('summary') or article.get('description') or article.get('content', '')[:500] + "..."
            source = article.get('source', 'Unknown')
            content = f"title: {article['title']} | summary: {summary} | link: {article['link']} | source: {source}"
            docs_to_add.append(Document(
                page_content=content,
                metadata={
                    "link": article['link'],
                    "week": article['week'],
                    "title": article['title'],
                    "source": source
                }
            ))
        
        if docs_to_add:
            vector_store.add_documents(docs_to_add)
            print(f"Added {len(docs_to_add)} documents to vector store.")
        else:
            print("No documents to add.")
            
    except Exception as e:
        print(f"Error initializing vector store: {e}")
        # Don't raise the exception in production
        import traceback
        traceback.print_exc()

# Only run if this script is executed directly
if __name__ == "__main__":
    # Initialize vector store with all available articles instead of hardcoded week
    initialize_vector_store()


# FIXED: Proper confidence calculation for cosine distance
def distance_to_confidence(distance):
    # Convert cosine distance to cosine similarity
    # Cosine distance: 0 = identical, 2 = completely opposite
    cosine_similarity = 1 - distance
    # Ensure confidence is between 0 and 1
    return max(0, min(1, cosine_similarity))


# Example query
query = "VaxSeer flu vaccine AI"  
docs_scores = vector_store.similarity_search_with_score(query, k=2)

threshold = 0.25 

# Filter results based on threshold
filtered_results = [
    (doc, distance_to_confidence(score)) 
    for doc, score in docs_scores
    if distance_to_confidence(score) >= threshold
]

# Deduplicate by link
unique_links = set()
deduped_results = []
for doc, confidence in filtered_results:
    # Extract link robustly
    try:
        parts = {}
        for item in doc.page_content.split(" | "):
            if ": " in item:
                key, value = item.split(": ", 1)
                parts[key] = value
        link = parts.get("link", None)
    except Exception:
        link = None

    if link and link not in unique_links:
        unique_links.add(link)
        deduped_results.append((parts, confidence))

# Handle no results case
if not deduped_results:
    print("No results found")
else:
    for i, (parts, confidence) in enumerate(deduped_results, start=1):
        print(f"\nResult {i}:")
        print("Title:", parts.get("title", "Unknown"))
        print("Summary:", parts.get("summary", "Unknown"))
        print("Link:", parts.get("link", "Unknown"))
        print("Confidence:", round(confidence, 3))
