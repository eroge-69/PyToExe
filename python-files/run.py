import time
from datetime import datetime
import feedparser
import os
import re
import requests
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import google.auth.transport.requests
import pytz
import json
from pytrends.request import TrendReq
import logging

# -------- CONFIG ----------
RSS_URL = "https://www.space.com/feeds/all"
CLIENT_SECRET_JSON = {
    "installed": {
        "client_id": "1051833345706-aicqjoca19vo2vhp635v88sd70b84a5g.apps.googleusercontent.com",
        "project_id": "salah-tracker2",
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_secret": "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",
        "redirect_uris": ["http://localhost"]
    }
}
BLOG_ID = "3067547514393972941"
CHECK_INTERVAL = 10 * 60  # seconds
OPENROUTER_API_KEY = "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"
OPENROUTER_MODEL = "openai/gpt-oss-20b:free"
CLIENT_SECRET_FILE = "client_secret.json"
SCOPES = ['https://www.googleapis.com/auth/blogger']
PYTRENDS_LANG = "en-US"
PYTRENDS_TIMEOUT = 10
# --------------------------

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def print_status(msg):
    print(f"⏳ {msg}")

def print_success(msg):
    print(f"✅ {msg}")

def authenticate():
    print_status("Starting Google authentication...")
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            with open(CLIENT_SECRET_FILE, "w") as f:
                json.dump(CLIENT_SECRET_JSON, f)
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            os.remove(CLIENT_SECRET_FILE)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    print_success("Google authenticated successfully.")
    return creds

def get_trending_keywords(seed_terms=None, topn=10):
    print_status("Fetching trending keywords from Google Trends...")
    try:
        pytrends = TrendReq(hl=PYTRENDS_LANG, tz=0, timeout=(PYTRENDS_TIMEOUT, PYTRENDS_TIMEOUT))
        candidates = []
        try:
            trending_df = pytrends.trending_searches(pn='global')
            trending = trending_df[0].astype(str).tolist() if not trending_df.empty else []
        except Exception:
            trending = []

        seed_terms = seed_terms or ["space", "nasa", "astronomy"]
        for term in seed_terms:
            try:
                pytrends.build_payload([term], timeframe='now 7-d')
                related = pytrends.related_queries().get(term, {})
                rising = related.get('rising', None)
                top = related.get('top', None)
                if rising is not None:
                    candidates += rising['query'].astype(str).tolist()[:10]
                if top is not None:
                    candidates += top['query'].astype(str).tolist()[:10]
            except Exception:
                continue

        candidates += trending
        filtered = []
        seen = set()
        for kw in candidates:
            kw = kw.strip()
            if not kw or kw.lower() in seen:
                continue
            seen.add(kw.lower())
            if len(kw.split()) >= 3 or len(kw) > 20:
                filtered.append(kw)
            else:
                if len(filtered) < topn // 2 and 10 < len(kw) <= 20:
                    filtered.append(kw)
        print_success(f"Fetched {len(filtered[:topn])} trending keywords.")
        return filtered[:topn] if filtered else [t for t in seed_terms][:topn]
    except Exception as e:
        logging.warning(f"Pytrends failed: {e}")
        return seed_terms[:topn]

def get_full_article_content(url):
    print_status(f"Fetching full article content from {url}")
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
        soup = BeautifulSoup(response.content, 'html.parser')
        article = soup.find('article') or soup.find('main') or soup

        # Extract paragraphs and images preserving order
        content_blocks = []
        for elem in article.descendants:
            if elem.name in ['p', 'h2', 'h3', 'ul', 'ol', 'li']:
                content_blocks.append(str(elem))
            elif elem.name == 'img' and elem.get('src'):
                # Add alt text if missing
                if not elem.get('alt'):
                    elem['alt'] = "Space image related to article"
                content_blocks.append(str(elem))
        full_content = ''.join(content_blocks)
        print_success("Article content with images fetched.")
        return full_content
    except Exception as e:
        logging.warning(f"Error fetching full article: {e}")
        return "<p>Full article could not be loaded.</p>"

def extract_labels(entry):
    categories = entry.get("tags", [])
    labels = [tag['term'] for tag in categories if 'term' in tag]
    return labels if labels else ["space"]

def call_openrouter_system(user_prompt, temperature=0.2, max_tokens=1200):
    print_status("Calling OpenRouter AI...")
    try:
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": OPENROUTER_MODEL,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant that outputs clean text or HTML as requested."},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, data=json.dumps(payload), timeout=60)
        return resp.json()
    except Exception as e:
        logging.warning(f"OpenRouter call failed: {e}")
        return None

def get_lsi_keywords_via_ai(seed_keywords, max_lsi=6):
    print_status("Generating LSI keywords via AI...")
    prompt = (
        "Given these seed keywords: \n" + ", ".join(seed_keywords) +
        "\nReturn a JSON array of the top " + str(max_lsi) +
        " LSI (latent semantic) keyword phrases (short, 2-4 words) that are relevant and low competition."
    )
    res = call_openrouter_system(prompt, temperature=0.2, max_tokens=400)
    try:
        if res and 'choices' in res and res['choices']:
            text = res['choices'][0]['message']['content']
            match = re.search(r"\[.*?\]", text, re.DOTALL)
            if match:
                arr = json.loads(match.group(0))
                print_success(f"Received {len(arr)} LSI keywords.")
                return [a.strip() for a in arr][:max_lsi]
            lines = [l.strip('- ').strip() for l in text.splitlines() if l.strip()][:max_lsi]
            print_success(f"Received {len(lines)} LSI keywords.")
            return lines
    except Exception as e:
        logging.warning(f"Parsing LSI failed: {e}")
    return seed_keywords[:max_lsi]

def generate_faqs_via_ai(article_text, main_keywords, max_faq=5):
    print_status("Generating FAQ section via AI...")
    prompt = (
        "Read the article content and generate up to " + str(max_faq) +
        " frequently asked questions (Q&A) that real users might ask. Return a JSON array of objects {\"question\":..., \"answer\":...}. "
        "Make answers concise (30-80 words) and include main keywords naturally.\n\nArticle:\n" + article_text
    )
    res = call_openrouter_system(prompt, temperature=0.2, max_tokens=800)
    try:
        if res and 'choices' in res and res['choices']:
            text = res['choices'][0]['message']['content']
            match = re.search(r"\[.*\]", text, re.DOTALL)
            if match:
                faqs = json.loads(match.group(0))
                print_success(f"Generated {len(faqs)} FAQs.")
                return faqs
            faqs = []
            lines = [l.strip() for l in text.splitlines() if l.strip()]
            q = None
            for line in lines:
                if line.lower().startswith('q:') or line.endswith('?'):
                    q = line.lstrip('Q:q:').strip()
                elif q:
                    faqs.append({"question": q, "answer": line})
                    q = None
                if len(faqs) >= max_faq:
                    break
            print_success(f"Generated {len(faqs)} FAQs.")
            return faqs
    except Exception as e:
        logging.warning(f"Parsing FAQs failed: {e}")
    return []

def rewrite_article_full_seo(content, keywords_list, lsi_list, faq_html_snippet, internal_html, source_link):
    print_status("Requesting full SEO rewrite from OpenRouter with images preserved...")
    try:
        kw_text = ", ".join(keywords_list[:8])
        lsi_text = ", ".join(lsi_list)
        prompt = (
            "You are an expert science journalist and SEO editor.\n"
            "Rewrite the following article HTML into a single clean HTML block optimized for Google search.\n"
            "IMPORTANT: Preserve all <img> tags exactly with proper alt text describing the image related to the content.\n"
            "Use main keywords: " + kw_text + ".\n"
            "Use these LSI keywords: " + lsi_text + ".\n"
            "Create proper headings, intro, body, conclusion.\n"
            "Add FAQ section and JSON-LD schema.\n"
            "Insert related posts HTML:\n" + internal_html + "\n"
            "Add a source link at the end.\n"
            "Keep HTML clean without inline styles or scripts.\n\n"
            "Article content:\n" + content + "\n\n"
            "FAQ section:\n" + faq_html_snippet
        )

        res = call_openrouter_system(prompt, temperature=0.25, max_tokens=3000)
        if res and 'choices' in res and res['choices']:
            html_output = res['choices'][0]['message']['content']
            match = re.search(r"<html.*?>.*?</html>", html_output, re.DOTALL | re.IGNORECASE)
            print_success("SEO rewrite completed.")
            return match.group(0) if match else html_output
    except Exception as e:
        logging.warning(f"Rewrite failed: {e}")
    return None

def sanitize_html(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup.find_all(['style', 'script', 'iframe', 'center']):
        tag.decompose()
    for tag in soup.find_all(True):
        for attr in ['style', 'class', 'id', 'align']:
            tag.attrs.pop(attr, None)
    return str(soup)

def create_post(service, blog_id, title, content, labels=None):
    try:
        print_status(f"Publishing post: {title}")
        post = {
            "kind": "blogger#post",
            "title": title,
            "content": content,
            "labels": labels or []
        }
        result = service.posts().insert(blogId=blog_id, body=post, isDraft=False).execute()
        print_success(f"Published post URL: {result.get('url')}")
        return result.get('url')
    except Exception as e:
        logging.warning(f"Failed to publish '{title}': {e}")
        return None

def is_today(published_parsed):
    if not published_parsed:
        return False
    published_date = datetime(*published_parsed[:6], tzinfo=pytz.utc).astimezone(pytz.timezone('Asia/Karachi'))
    today = datetime.now(pytz.timezone('Asia/Karachi')).date()
    return published_date.date() == today

def load_posted_titles():
    today = datetime.now(pytz.timezone('Asia/Karachi')).strftime('%Y-%m-%d')
    if os.path.exists("posted_today.json"):
        with open("posted_today.json", "r") as f:
            data = json.load(f)
            if data.get("date") == today:
                return set(data.get("titles", []))
    return set()

def save_posted_titles(titles):
    today = datetime.now(pytz.timezone('Asia/Karachi')).strftime('%Y-%m-%d')
    with open("posted_today.json", "w") as f:
        json.dump({"date": today, "titles": list(titles)}, f)

def get_recent_posts(service, blog_id, max_results=50):
    try:
        posts = service.posts().list(blogId=blog_id, maxResults=max_results).execute()
        items = posts.get('items', []) if posts else []
        return [(p.get('title', ''), p.get('url', '')) for p in items]
    except Exception as e:
        logging.warning(f"Failed fetching recent posts: {e}")
        return []

def build_internal_links(recent_posts, keywords, max_links=3):
    links = []
    found = 0
    for title, url in recent_posts:
        if not title or not url:
            continue
        t = title.lower()
        for kw in keywords:
            if kw.lower() in t and found < max_links:
                links.append(f"<li><a href='{url}' target='_blank'>{title}</a></li>")
                found += 1
                break
        if found >= max_links:
            break
    if links:
        return "<aside><h3>Related on this blog</h3><ul>" + "".join(links) + "</ul></aside>"
    return ""

def main_loop():
    print("🚀 Tool created by Hasnain Iqbal — SEO God Mode Auto Poster 🚀")
    creds = authenticate()
    service = build('blogger', 'v3', credentials=creds)
    posted_titles_today = load_posted_titles()
    logging.info("SEO GOD MODE Auto Poster started...")

    trending_seed = ["space", "nasa", "astronomy"]
    while True:
        print_status(f"Checking feed at {datetime.now(pytz.timezone('Asia/Karachi'))} ...")
        feed = feedparser.parse(RSS_URL)
        new_posts_found = False

        trending_keywords = get_trending_keywords(seed_terms=trending_seed, topn=10)
        logging.info(f"Trending keywords: {trending_keywords}")

        recent_posts = get_recent_posts(service, BLOG_ID, max_results=50)

        for entry in feed.entries:
            try:
                if not is_today(entry.get('published_parsed')):
                    continue
                title = entry.title.strip()
                if title in posted_titles_today:
                    continue
                link = entry.link
                print_status(f"Processing article: {title}")

                full_content = get_full_article_content(link)

                lsi = get_lsi_keywords_via_ai(trending_keywords[:4], max_lsi=6)
                faqs = generate_faqs_via_ai(full_content, trending_keywords[:3], max_faq=4)
                faq_html = ""
                if faqs:
                    faq_html += "<section><h2>Frequently Asked Questions</h2><dl>"
                    for f in faqs:
                        q = f.get('question')
                        a = f.get('answer')
                        faq_html += f"<dt>{q}</dt><dd>{a}</dd>"
                    faq_html += "</dl></section>"

                internal_html = build_internal_links(recent_posts, trending_keywords, max_links=3)

                rewritten = None
                retry = 0
                while not rewritten and retry < 3:
                    rewritten = rewrite_article_full_seo(full_content + f"<p>Source: {link}</p>", trending_keywords, lsi, faq_html, internal_html, link)
                    if not rewritten:
                        retry += 1
                        logging.warning("Rewrite failed — retrying...")
                        time.sleep(5)

                if not rewritten:
                    logging.warning("Skipping due to rewrite failure.")
                    continue

                cleaned_html = sanitize_html(rewritten)

                cleaned_html += f"\n<p><a href='{link}' target='_blank' rel='nofollow'>Original Source</a></p>"

                soup = BeautifulSoup(cleaned_html, 'html.parser')
                final_title_tag = soup.find('title')
                final_title = final_title_tag.text.strip() if final_title_tag else title

                labels = extract_labels(entry)
                post_url = create_post(service, BLOG_ID, final_title, str(soup), labels)
                if post_url:
                    posted_titles_today.add(title)
                    save_posted_titles(posted_titles_today)
                    new_posts_found = True

            except Exception as e:
                logging.warning(f"Error processing entry '{entry.title if 'title' in entry else 'N/A'}': {e}")

        if not new_posts_found:
            print_status("No new posts found.")
        print_status(f"Waiting {CHECK_INTERVAL // 60} minutes before next check...\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
