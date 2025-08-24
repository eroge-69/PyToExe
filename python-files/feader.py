#!/usr/bin/env python3
"""
Feader - A Simple RSS Reader (Two-Pane Layout)
"""

import feedparser
import requests
import json
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime
import threading
import webbrowser
from urllib.parse import urlparse
import os

class Feader:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Feader - RSS Reader")
        self.root.geometry("1200x700")
        
        # Initialize JSON storage
        self.data_file = 'feader_data.json'
        self.load_data()
        
        # Create GUI
        self.create_gui()
        
        # Load feeds on startup
        self.refresh_feeds()
    
    def load_data(self):
        """Load data from JSON file"""
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
        else:
            self.data = {
                'feeds': {},
                'articles': {},
                'next_feed_id': 1,
                'next_article_id': 1
            }
    
    def save_data(self):
        """Save data to JSON file"""
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def create_gui(self):
        """Create the two-pane GUI"""
        # Create main paned window
        main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Left panel (1/3 width)
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)
        
        # Feeds section
        feeds_frame = ttk.LabelFrame(left_frame, text="Feeds")
        feeds_frame.pack(fill=tk.X, pady=(0,10))
        
        # Feed buttons
        btn_frame = ttk.Frame(feeds_frame)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Button(btn_frame, text="Add Feed", command=self.add_feed).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(btn_frame, text="Refresh", command=self.refresh_feeds_threaded).pack(side=tk.LEFT, padx=(0,5))
        ttk.Button(btn_frame, text="Remove", command=self.remove_feed).pack(side=tk.LEFT)
        
        # Feeds listbox
        self.feeds_listbox = tk.Listbox(feeds_frame, height=6)
        self.feeds_listbox.pack(fill=tk.X, padx=5, pady=(0,5))
        self.feeds_listbox.bind('<<ListboxSelect>>', self.on_feed_select)
        
        # Articles section
        articles_frame = ttk.LabelFrame(left_frame, text="Articles")
        articles_frame.pack(fill=tk.BOTH, expand=True)
        
        # Show all articles button
        ttk.Button(articles_frame, text="Show All Articles", command=self.show_all_articles).pack(pady=5)
        
        # Articles listbox with scrollbar
        articles_list_frame = ttk.Frame(articles_frame)
        articles_list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0,5))
        
        self.articles_listbox = tk.Listbox(articles_list_frame)
        articles_scrollbar = ttk.Scrollbar(articles_list_frame, orient=tk.VERTICAL, command=self.articles_listbox.yview)
        self.articles_listbox.configure(yscrollcommand=articles_scrollbar.set)
        
        self.articles_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        articles_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.articles_listbox.bind('<<ListboxSelect>>', self.on_article_select)
        
        # Right panel (2/3 width) for article content
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=2)
        
        # Article title
        self.article_title_var = tk.StringVar()
        self.article_title_var.set("Select an article to read")
        title_label = ttk.Label(right_frame, textvariable=self.article_title_var, font=('Arial', 14, 'bold'), wraplength=600)
        title_label.pack(anchor=tk.W, pady=(0,10))
        
        # Article link
        self.article_link_var = tk.StringVar()
        link_label = ttk.Label(right_frame, textvariable=self.article_link_var, font=('Arial', 9), foreground='blue', cursor='hand2')
        link_label.pack(anchor=tk.W, pady=(0,10))
        link_label.bind('<Button-1>', self.open_article_link)
        
        # Article content
        text_frame = ttk.Frame(right_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.article_text = tk.Text(text_frame, wrap=tk.WORD, font=('Arial', 11), state=tk.DISABLED)
        text_scrollbar = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.article_text.yview)
        self.article_text.configure(yscrollcommand=text_scrollbar.set)
        
        self.article_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        text_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Store article data for selected item
        self.current_article_data = {}
    
    def add_feed(self):
        """Add a new RSS feed"""
        url = simpledialog.askstring("Add Feed", "Enter RSS feed URL:")
        if not url:
            return
        
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        
        try:
            self.status_var.set("Fetching feed...")
            self.root.update()
            
            feed = feedparser.parse(url)
            if feed.bozo and not feed.entries:
                messagebox.showerror("Error", "Invalid RSS feed URL")
                return
            
            title = feed.feed.get('title', urlparse(url).netloc)
            
            # Check if feed exists
            for feed_data in self.data['feeds'].values():
                if feed_data['url'] == url:
                    messagebox.showinfo("Info", "Feed already exists")
                    return
            
            # Add feed
            feed_id = str(self.data['next_feed_id'])
            self.data['feeds'][feed_id] = {
                'title': title,
                'url': url,
                'added_date': datetime.now().isoformat()
            }
            self.data['next_feed_id'] += 1
            self.save_data()
            
            self.load_feeds_list()
            self.fetch_feed_articles(url, feed_id)
            self.show_all_articles()
            
            self.status_var.set(f"Added feed: {title}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add feed: {str(e)}")
            self.status_var.set("Ready")
    
    def remove_feed(self):
        """Remove selected feed"""
        selection = self.feeds_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Select a feed to remove")
            return
        
        feed_title = self.feeds_listbox.get(selection[0])
        
        if messagebox.askyesno("Confirm", f"Remove '{feed_title}'?"):
            # Find and remove feed
            feed_id_to_remove = None
            for feed_id, feed_data in self.data['feeds'].items():
                if feed_data['title'] == feed_title:
                    feed_id_to_remove = feed_id
                    break
            
            if feed_id_to_remove:
                del self.data['feeds'][feed_id_to_remove]
                self.data['articles'] = {k: v for k, v in self.data['articles'].items() 
                                       if v['feed_id'] != feed_id_to_remove}
                self.save_data()
                
                self.load_feeds_list()
                self.show_all_articles()
                self.status_var.set(f"Removed: {feed_title}")
    
    def load_feeds_list(self):
        """Load feeds into listbox"""
        self.feeds_listbox.delete(0, tk.END)
        feeds = sorted(self.data['feeds'].values(), key=lambda x: x['title'])
        
        for feed in feeds:
            self.feeds_listbox.insert(tk.END, feed['title'])
    
    def on_feed_select(self, event):
        """Show articles from selected feed"""
        selection = self.feeds_listbox.curselection()
        if not selection:
            return
        
        feed_title = self.feeds_listbox.get(selection[0])
        
        # Find feed id
        feed_id = None
        for fid, feed_data in self.data['feeds'].items():
            if feed_data['title'] == feed_title:
                feed_id = fid
                break
        
        if feed_id:
            self.load_articles_for_feed(feed_id)
    
    def show_all_articles(self):
        """Show all articles from all feeds in chronological order"""
        self.feeds_listbox.selection_clear(0, tk.END)
        self.load_all_articles()
    
    def load_articles_for_feed(self, feed_id):
        """Load articles for specific feed"""
        articles = [article for article in self.data['articles'].values() 
                   if article['feed_id'] == feed_id]
        self._populate_articles_list(articles)
    
    def load_all_articles(self):
        """Load all articles from all feeds"""
        articles = list(self.data['articles'].values())
        self._populate_articles_list(articles)
    
    def _populate_articles_list(self, articles):
        """Helper to populate articles listbox"""
        self.articles_listbox.delete(0, tk.END)
        
        # Sort by date (newest first)
        articles.sort(key=lambda x: x.get('pub_date', ''), reverse=True)
        
        for i, article in enumerate(articles):
            title = article['title']
            read_marker = "" if article.get('read', False) else "● "
            
            # Get feed name
            feed_name = ""
            feed_data = self.data['feeds'].get(article['feed_id'])
            if feed_data:
                feed_name = f"[{feed_data['title']}] "
            
            display_text = f"{read_marker}{feed_name}{title}"
            self.articles_listbox.insert(tk.END, display_text)
            
            # Store article data
            self.articles_listbox.insert(tk.END, "")  # This gets replaced
            self.articles_listbox.delete(tk.END)
            
        # Store articles for reference
        self.current_articles = articles
    
    def on_article_select(self, event):
        """Handle article selection"""
        selection = self.articles_listbox.curselection()
        if not selection or not hasattr(self, 'current_articles'):
            return
        
        article_index = selection[0]
        if article_index >= len(self.current_articles):
            return
        
        article = self.current_articles[article_index]
        self.show_article(article)
        
        # Mark as read
        article['read'] = True
        self.data['articles'][article['id']]['read'] = True
        self.save_data()
        
        # Update display to remove unread marker
        current_text = self.articles_listbox.get(article_index)
        if current_text.startswith("● "):
            new_text = current_text[2:]  # Remove unread marker
            self.articles_listbox.delete(article_index)
            self.articles_listbox.insert(article_index, new_text)
            self.articles_listbox.selection_set(article_index)
    
    def show_article(self, article):
        """Display article content"""
        self.article_title_var.set(article['title'])
        self.article_link_var.set(article.get('link', ''))
        
        self.article_text.config(state=tk.NORMAL)
        self.article_text.delete(1.0, tk.END)
        
        # Get feed name
        feed_data = self.data['feeds'].get(article['feed_id'])
        feed_name = feed_data['title'] if feed_data else "Unknown Feed"
        
        content = f"Source: {feed_name}\n"
        content += f"Date: {article.get('pub_date', 'Unknown')[:19]}\n\n"
        content += article.get('description', 'No content available')
        
        self.article_text.insert(1.0, content)
        self.article_text.config(state=tk.DISABLED)
        
        self.current_article_data = article
    
    def open_article_link(self, event):
        """Open article link in browser"""
        link = self.article_link_var.get()
        if link:
            webbrowser.open(link)
    
    def fetch_feed_articles(self, feed_url, feed_id):
        """Fetch articles from RSS feed"""
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries:
                title = entry.get('title', 'No title')
                link = entry.get('link', '')
                description = entry.get('description', entry.get('summary', ''))
                pub_date = entry.get('published', datetime.now().isoformat())
                
                # Check if article exists
                exists = any(article['title'] == title and article['feed_id'] == feed_id 
                           for article in self.data['articles'].values())
                
                if not exists:
                    article_id = str(self.data['next_article_id'])
                    self.data['articles'][article_id] = {
                        'id': article_id,
                        'feed_id': feed_id,
                        'title': title,
                        'link': link,
                        'description': description,
                        'pub_date': pub_date,
                        'read': False
                    }
                    self.data['next_article_id'] += 1
            
            self.save_data()
            
        except Exception as e:
            print(f"Error fetching {feed_url}: {e}")
    
    def refresh_feeds(self):
        """Refresh all feeds"""
        for feed_id, feed_data in self.data['feeds'].items():
            self.fetch_feed_articles(feed_data['url'], feed_id)
        
        self.load_feeds_list()
        self.show_all_articles()
        
        feed_count = len(self.data['feeds'])
        unread_count = sum(1 for article in self.data['articles'].values() if not article['read'])
        self.status_var.set(f"Refreshed {feed_count} feeds - {unread_count} unread")
    
    def refresh_feeds_threaded(self):
        """Refresh feeds in background"""
        self.status_var.set("Refreshing...")
        thread = threading.Thread(target=self.refresh_feeds)
        thread.daemon = True
        thread.start()
    
    def run(self):
        """Start GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle app closing"""
        self.save_data()
        self.root.destroy()

def main():
    print("Starting Feader...")
    
    feader = Feader()
    
    # Add sample feeds if none exist
    if not feader.data['feeds']:
        sample_feeds = [
            ("BBC News", "http://feeds.bbci.co.uk/news/rss.xml"),
            ("TechCrunch", "https://techcrunch.com/feed/"),
        ]
        
        for title, url in sample_feeds:
            try:
                feed_id = str(feader.data['next_feed_id'])
                feader.data['feeds'][feed_id] = {
                    'title': title,
                    'url': url,
                    'added_date': datetime.now().isoformat()
                }
                feader.data['next_feed_id'] += 1
                feader.fetch_feed_articles(url, feed_id)
            except:
                pass
        
        feader.save_data()
        feader.load_feeds_list()
        feader.show_all_articles()
    
    feader.run()

if __name__ == "__main__":
    main()