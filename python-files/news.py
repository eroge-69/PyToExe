import feedparser
import requests
from bs4 import BeautifulSoup
import os
from elevenlabs.client import ElevenLabs
from elevenlabs import play
import re

# ==============================================================================
# Python News Bulletin Generator
#
# Description:
# This script fetches the latest news from the ABC News Australia RSS feed,
# filters out sports stories, uses BeautifulSoup to extract clean article text,
# summarizes it with the Gemini API, and then generates a final audio file
# with the ElevenLabs API.
#
# Requirements:
# - Python 3
# - The following Python libraries: feedparser, beautifulsoup4, requests, elevenlabs
#   Install them with: pip install feedparser beautifulsoup4 requests elevenlabs
#
# - A Google Gemini API Key for summarization.
# - An ElevenLabs API key for text-to-speech.
#
# Usage:
# 1. Make sure you have installed the required libraries.
# 2. Set your API keys in the configuration section below.
# 3. Run the script from your terminal: python generate_news.py
#
# ==============================================================================

# --- Configuration ---

# --- API Keys (Replace with your actual keys) ---
# It's recommended to set these as environment variables for better security.
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "sk_c956b847512f214dc336c4de4744f14f1882db306d4cfcb2")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCDTQnZbi3sjjZm1G-CkWyC3YfZhrLF1p4")

# --- Script Configuration ---
NEWS_RSS_URL = "http://www.abc.net.au/news/feed/51120/rss.xml"
OUTPUT_FILENAME = "news_bulletin.mp3"
HEADLINE_COUNT = 5
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36"
ELEVENLABS_VOICE_ID = "2EiwWnXFnvU5JabPnv8n" # Voice ID for Clyde

# Keywords to identify and exclude sports stories (case-insensitive)
SPORT_KEYWORDS = [
    'afl', 'nrl', 'cricket', 'footy', 'matildas', 'socceroos', 'wallabies', 
    'rugby', 'netball', 'motorsport', 'grand prix', 'olympics', 'commonwealth games',
    'supercars', 'a-league', 'w-league', 'bbl', 'wbbl', 'ashes'
]


# --- Functions ---

def print_message(message):
    """Prints a styled message to the console."""
    print("--------------------------------------------------")
    print(message)
    print("--------------------------------------------------")

def is_sports_story(title):
    """Checks if a story title contains any sport-related keywords."""
    for keyword in SPORT_KEYWORDS:
        if re.search(r'\b' + re.escape(keyword) + r'\b', title, re.IGNORECASE):
            return True
    return False

def fetch_article_urls(rss_url, count):
    """Fetches, filters out sports stories, and returns the latest article URLs."""
    print(f"Fetching RSS feed from: {rss_url}")
    try:
        feed = feedparser.parse(rss_url)
        
        non_sport_urls = []
        for entry in feed.entries:
            if not is_sports_story(entry.title):
                non_sport_urls.append(entry.link)
                if len(non_sport_urls) >= count:
                    break # Stop once we have enough headlines
        
        if len(non_sport_urls) < count:
            print(f"⚠️ WARNING: Found only {len(non_sport_urls)} non-sport stories.")

        if not non_sport_urls:
            print("❌ ERROR: Could not find any non-sport entries in the RSS feed.")
            return []
            
        return non_sport_urls

    except Exception as e:
        print(f"❌ ERROR: Failed to fetch or parse RSS feed. Reason: {e}")
        return []

def extract_text_with_beautifulsoup(url):
    """Extracts the main article text from a URL using BeautifulSoup."""
    print(f"  - Extracting text from: {url}")
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status() # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')

        # This is a common structure for ABC news articles.
        # We look for a specific element that contains the article body.
        article_body = soup.find('div', attrs={'data-component': 'ArticleBody'})

        if not article_body:
            # Fallback for different article structures
            article_body = soup.find('article')

        if article_body:
            # Get all paragraph texts and join them
            paragraphs = article_body.find_all('p')
            full_text = ' '.join(p.get_text(strip=True) for p in paragraphs)
            return full_text
        else:
            print("  - WARNING: Could not find a specific article body element. Falling back to generic text extraction.")
            return soup.get_text(separator=' ', strip=True)

    except requests.exceptions.RequestException as e:
        print(f"  - ❌ WARNING: Failed to fetch article URL. Reason: {e}")
    except Exception as e:
        print(f"  - ❌ WARNING: An error occurred during text extraction. Reason: {e}")
    return None


def summarize_text_with_gemini(text_to_summarize):
    """Summarizes the given text using the Google Gemini API."""
    print("  - Summarizing with Gemini API...")
    if not text_to_summarize:
        return None

    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={GEMINI_API_KEY}"

    # Truncate text to avoid exceeding API limits
    truncated_text = text_to_summarize[:15000]

    prompt = f"Summarize the following news article in a maximum of two sentences, focusing on the key information: {truncated_text}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(api_url, json=payload, headers=headers, timeout=20)
        response.raise_for_status()
        response_json = response.json()
        
        # Safely access the summary text
        summary = response_json.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        if summary:
            return summary.strip()
        else:
            print("  - ❌ WARNING: Gemini API response did not contain a valid summary.")
            print(f"  - Raw Gemini Response: {response_json}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  - ❌ WARNING: Gemini API request failed. Reason: {e}")
    except (IndexError, KeyError) as e:
        print(f"  - ❌ WARNING: Could not parse Gemini response. Malformed JSON? Reason: {e}")
    return None


def generate_and_save_audio(script_text, output_filename):
    """Generates audio from text using the ElevenLabs API and saves it to a file."""
    if not script_text:
        print("❌ ERROR: No script text provided to generate audio.")
        return False
        
    print(f"\nConstructing final audio for bulletin...")
    try:
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        # CORRECTED METHOD: Use the client.text_to_speech.convert() method
        audio_stream = client.text_to_speech.convert(
            voice_id=ELEVENLABS_VOICE_ID,
            text=script_text,
            model_id="eleven_multilingual_v2" # A high-quality model
        )

        # Save the audio stream to a file
        with open(output_filename, "wb") as f:
            for chunk in audio_stream:
                f.write(chunk)
        
        print(f"✅ Success! News bulletin saved as {output_filename}")
        return True

    except Exception as e:
        print(f"❌ ERROR: Failed to generate audio with ElevenLabs. Reason: {e}")
        return False


def main():
    """Main function to orchestrate the news bulletin generation."""
    print_message("Starting Python News Bulletin Generation")

    article_urls = fetch_article_urls(NEWS_RSS_URL, HEADLINE_COUNT)
    if not article_urls:
        print("Exiting due to failure in fetching article URLs.")
        return

    full_news_script = "Hi, this is Clyde bringing you the very latest news headlines. "
    summaries_added = 0

    for url in article_urls:
        article_text = extract_text_with_beautifulsoup(url)
        if article_text:
            summary = summarize_text_with_gemini(article_text)
            if summary:
                print(f"  - Summary added.")
                full_news_script += summary + " "
                summaries_added += 1

    if summaries_added == 0:
        print("\nNo summaries could be generated. Aborting audio creation.")
        return

    full_news_script += "And that's how the World is right now. Keep smiling. Give someone a hug. I'm Clyde, and that was your Great Southern FM Headlines."
    
    print("\n--- FINAL SCRIPT ---")
    print(full_news_script)
    print("--------------------")

    generate_and_save_audio(full_news_script, OUTPUT_FILENAME)


if __name__ == "__main__":
    main()

