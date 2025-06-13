import sys
import os
import feedparser
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QTextBrowser, QMainWindow,
    QPushButton, QLineEdit, QLabel, QHBoxLayout, QCheckBox, QFileDialog,
    QListWidget, QListWidgetItem, QMessageBox, QInputDialog
)
from PyQt5.QtCore import QTimer, Qt
try:
    from playsound import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False

DEFAULT_FEEDS = [
    "https://www.independent.co.uk/travel/rss"
]
DEFAULT_KEYWORDS = ["airline", "airport", "attack", "security", "flight", "aviation"]
ALERT_SOUND = "alert.wav"
REFRESH_INTERVAL_MS = 5 * 60 * 1000  # 5 minutes

def resource_path(relative_path):
    # Get absolute path to resource, works for dev and for PyInstaller .exe
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def fetch_rss(feed_url):
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        title = entry.title
        link = entry.link
        date_published = entry.published if 'published' in entry else ''
        summary = entry.summary if "summary" in entry else ""
        articles.append({
            "title": title,
            "link": link,
            "summary": summary,
            "published": date_published,
        })
    return articles

def article_matches(article, keywords):
    text = (article["title"] + " " + article["summary"]).lower()
    for word in keywords:
        if word.lower() in text:
            return word
    return None

class NewsTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout()
        self.browser = QTextBrowser()
        self.layout.addWidget(self.browser)
        self.setLayout(self.layout)
        self.articles = []
        self.keywords = []
        self.show_only_matches = False
        self.search_query = ""
        self.color_map = {}

    def set_articles(self, articles, keywords, color_map, show_only_matches, search_query):
        self.articles = articles
        self.keywords = keywords
        self.show_only_matches = show_only_matches
        self.color_map = color_map
        self.search_query = search_query.lower()
        self.refresh_view()

    def refresh_view(self):
        html = ""
        for article in self.articles:
            matched_word = article_matches(article, self.keywords)
            is_match = matched_word is not None
            search_hit = self.search_query in (article["title"] + " " + article["summary"]).lower()
            if self.search_query and not search_hit:
                continue
            if self.show_only_matches and not is_match:
                continue
            color = self.color_map.get(matched_word, "#fff7d6") if is_match else ""
            style = f"background-color:{color};" if color else ""
            pubdate = f"<br><i>{article['published']}</i>" if article['published'] else ""
            html += (
                f"<p style='{style}'>"
                f"<b><a href='{article['link']}'>{article['title']}</a></b>{pubdate}<br>"
                f"<small>{article['summary']}</small></p><hr>"
            )
        if not html:
            html = "<i>No news found.</i>"
        self.browser.setHtml(html)
        self.browser.setOpenExternalLinks(True)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Travel News Bot (RSS, Advanced)")
        self.setMinimumSize(1000, 800)

        self.feeds = list(DEFAULT_FEEDS)
        self.keywords = list(DEFAULT_KEYWORDS)
        self.color_map = {
            "airline": "#ffecb3",
            "airport": "#b3e5fc",
            "attack": "#ffcdd2",
            "security": "#dcedc8",
            "flight": "#fff9c4",
            "aviation": "#e1bee7",
        }
        self.show_only_matches = False
        self.search_query = ""
        self.bookmarks = []

        self.articles = []
        self.first_alert = True  # <-- FIXED: now set before refresh_news

        self.init_ui()
        self.refresh_news()
        self.setup_autorefresh()

    def init_ui(self):
        # Top controls layout
        top_layout = QHBoxLayout()

        # Feed list
        self.feed_list = QListWidget()
        for url in self.feeds:
            self.feed_list.addItem(url)
        self.feed_list.setMaximumWidth(320)
        self.feed_list.setSelectionMode(QListWidget.SingleSelection)

        add_feed_btn = QPushButton("Add Feed")
        add_feed_btn.clicked.connect(self.add_feed)
        remove_feed_btn = QPushButton("Remove Feed")
        remove_feed_btn.clicked.connect(self.remove_feed)

        # Keywords
        self.keyword_input = QLineEdit(", ".join(self.keywords))
        self.keyword_input.setPlaceholderText("alert keywords, comma-separated")
        update_keywords_btn = QPushButton("Update Keywords")
        update_keywords_btn.clicked.connect(self.update_keywords)

        # Show only matches checkbox
        self.show_only_matches_cb = QCheckBox("Show only matching articles")
        self.show_only_matches_cb.stateChanged.connect(self.toggle_show_only_matches)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search articles...")
        self.search_bar.textChanged.connect(self.set_search_query)

        # Refresh button
        refresh_btn = QPushButton("Refresh Now")
        refresh_btn.clicked.connect(self.refresh_news)

        # Bookmarks button
        self.bookmarks_btn = QPushButton("Bookmarks")
        self.bookmarks_btn.clicked.connect(self.show_bookmarks)

        # Export button
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_to_csv)

        # Layout for feed controls
        feed_ctrl_layout = QVBoxLayout()
        feed_ctrl_layout.addWidget(QLabel("News Feeds"))
        feed_ctrl_layout.addWidget(self.feed_list)
        feed_ctrl_layout.addWidget(add_feed_btn)
        feed_ctrl_layout.addWidget(remove_feed_btn)

        # Layout for other controls
        ctrl_layout = QVBoxLayout()
        ctrl_layout.addWidget(QLabel("Keywords"))
        ctrl_layout.addWidget(self.keyword_input)
        ctrl_layout.addWidget(update_keywords_btn)
        ctrl_layout.addWidget(self.show_only_matches_cb)
        ctrl_layout.addWidget(self.search_bar)
        ctrl_layout.addWidget(refresh_btn)
        ctrl_layout.addWidget(self.bookmarks_btn)
        ctrl_layout.addWidget(export_btn)
        ctrl_layout.addStretch()

        top_layout.addLayout(feed_ctrl_layout)
        top_layout.addLayout(ctrl_layout)

        # News display tab
        self.news_tab = NewsTab()

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addLayout(top_layout)
        main_layout.addWidget(self.news_tab)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # Context menu/bookmark on click
        self.news_tab.browser.anchorClicked.connect(self.on_article_clicked)

    def add_feed(self):
        text, ok = QInputDialog.getText(self, "Add RSS Feed", "Feed URL:")
        if ok and text.strip():
            url = text.strip()
            if url not in self.feeds:
                self.feeds.append(url)
                self.feed_list.addItem(url)
                self.refresh_news()

    def remove_feed(self):
        selected = self.feed_list.currentRow()
        if selected >= 0:
            url = self.feeds.pop(selected)
            self.feed_list.takeItem(selected)
            self.refresh_news()

    def update_keywords(self):
        self.keywords = [word.strip() for word in self.keyword_input.text().split(",") if word.strip()]
        self.refresh_news()

    def toggle_show_only_matches(self, state):
        self.show_only_matches = (state == Qt.Checked)
        self.refresh_news()

    def set_search_query(self, text):
        self.search_query = text
        self.refresh_news()

    def refresh_news(self):
        articles = []
        for url in self.feeds:
            try:
                articles += fetch_rss(url)
            except Exception as e:
                print(f"Failed to fetch {url}: {e}")
        # Remove duplicates (by link)
        seen = set()
        unique_articles = []
        for art in articles:
            if art["link"] not in seen:
                unique_articles.append(art)
                seen.add(art["link"])
        # Sort by published date, fallback to earliest
        def article_key(a):
            try:
                dt = datetime.strptime(a["published"], "%a, %d %b %Y %H:%M:%S %Z")
            except Exception:
                dt = datetime.min
            return (dt, a["title"])
        unique_articles.sort(key=article_key, reverse=True)
        self.articles = unique_articles
        alert = any(article_matches(a, self.keywords) for a in self.articles)
        self.news_tab.set_articles(self.articles, self.keywords, self.color_map, self.show_only_matches, self.search_query)
        if alert and not self.first_alert:
            self.play_alert()
        self.first_alert = False

    def setup_autorefresh(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_news)
        self.timer.start(REFRESH_INTERVAL_MS)

    def play_alert(self):
        sound_path = resource_path(ALERT_SOUND)
        if PLAYSOUND_AVAILABLE and os.path.exists(sound_path):
            playsound(sound_path)
        else:
            QMessageBox.information(self, "Alert", "Matching article found (sound unavailable)!")

    def on_article_clicked(self, url):
        link = url.toString()
        article = next((a for a in self.articles if a["link"] == link), None)
        if not article:
            return
        msg = QMessageBox(self)
        msg.setWindowTitle("Article Details")
        msg.setTextFormat(Qt.RichText)
        msg.setText(f"<b>{article['title']}</b><br><i>{article['published']}</i><br><a href='{article['link']}'>{article['link']}</a><br><br>{article['summary']}")
        bookmark_btn = msg.addButton("Bookmark", QMessageBox.ActionRole)
        msg.addButton("Close", QMessageBox.RejectRole)
        msg.exec_()
        if msg.clickedButton() == bookmark_btn:
            self.bookmark_article(article)

    def bookmark_article(self, article):
        if article not in self.bookmarks:
            self.bookmarks.append(article)
            QMessageBox.information(self, "Bookmark", "Article bookmarked!")

    def show_bookmarks(self):
        if not self.bookmarks:
            QMessageBox.information(self, "Bookmarks", "No bookmarks yet.")
            return
        bookmarks_html = ""
        for art in self.bookmarks:
            bookmarks_html += (
                f"<p><b><a href='{art['link']}'>{art['title']}</a></b><br>"
                f"<i>{art['published']}</i><br>"
                f"<small>{art['summary']}</small></p><hr>"
            )
        msg = QMessageBox(self)
        msg.setWindowTitle("Bookmarked Articles")
        msg.setTextFormat(Qt.RichText)
        msg.setText(bookmarks_html)
        msg.exec_()

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export Articles", "", "CSV Files (*.csv)")
        if not path:
            return
        import csv
        try:
            with open(path, "w", newline='', encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Title", "Link", "Published", "Summary"])
                for a in self.articles:
                    writer.writerow([a["title"], a["link"], a["published"], a["summary"]])
            QMessageBox.information(self, "Export", f"Exported articles to {path}")
        except Exception as e:
            QMessageBox.warning(self, "Export Failed", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())