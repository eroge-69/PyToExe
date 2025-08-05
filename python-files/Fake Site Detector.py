import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
import numpy as np
import random
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from urllib.parse import urlparse

class FakeSiteDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Fake Site Detector")
        self.root.geometry("500x600")
        self.root.configure(bg='#f0f0f0')
        
        self.seed = 30
        random.seed(self.seed)
        np.random.seed(self.seed)
        
        # Built-in whitelist of trusted domains (hidden from GUI)
        self.whitelist = {
            'google.com', 'www.google.com', 'gmail.com', 'www.gmail.com',
            'facebook.com', 'www.facebook.com', 'meta.com', 'www.meta.com',
            'instagram.com', 'www.instagram.com',
            'twitter.com', 'www.twitter.com', 'x.com', 'www.x.com',
            'youtube.com', 'www.youtube.com',
            'amazon.com', 'www.amazon.com',
            'microsoft.com', 'www.microsoft.com',
            'apple.com', 'www.apple.com',
            'linkedin.com', 'www.linkedin.com',
            'github.com', 'www.github.com',
            'stackoverflow.com', 'www.stackoverflow.com',
            'reddit.com', 'www.reddit.com',
            'wikipedia.org', 'www.wikipedia.org', 'en.wikipedia.org',
            'yahoo.com', 'www.yahoo.com',
            'netflix.com', 'www.netflix.com',
            'spotify.com', 'www.spotify.com',
            'dropbox.com', 'www.dropbox.com',
            'paypal.com', 'www.paypal.com',
            'ebay.com', 'www.ebay.com',
            'cnn.com', 'www.cnn.com',
            'bbc.com', 'www.bbc.com', 'bbc.co.uk', 'www.bbc.co.uk',
            'nytimes.com', 'www.nytimes.com',
            'adobe.com', 'www.adobe.com',
            'salesforce.com', 'www.salesforce.com',
            'zoom.us', 'www.zoom.us',
            'slack.com', 'www.slack.com',
            'discord.com', 'www.discord.com',
            'twitch.tv', 'www.twitch.tv',
            'pinterest.com', 'www.pinterest.com',
            'tiktok.com', 'www.tiktok.com',
            'snapchat.com', 'www.snapchat.com',
            'whatsapp.com', 'www.whatsapp.com',
            'telegram.org', 'www.telegram.org'
        }
        
        # Initialize model variables
        self.vectorizer = None
        self.model = None
        self.train_accuracy = None
        self.test_accuracy = None
        
        self.setup_gui()
        self.train_model()

    def extract_domain(self, url):
        """Extract domain from URL for whitelist checking"""
        try:
            # Add protocol if missing
            if not url.startswith(('http://', 'https://')):
                url = 'http://' + url
            
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Remove port if present
            if ':' in domain:
                domain = domain.split(':')[0]
            
            return domain
        except:
            return None

    def is_whitelisted(self, url):
        """Check if URL is in the trusted whitelist"""
        domain = self.extract_domain(url)
        if domain:
            return domain in self.whitelist
        return False

    def customtkns(self, t):
        tkns_byslash = str(t.encode("utf-8")).split("/")
        total_tokens = []
        for i in tkns_byslash:
            tokens = str(i).split("-")
            tkns_bydot = []
            for j in range(0,len(tokens)):
                temp_tkns = str(tokens[j]).split(".")
                tkns_bydot = tkns_bydot + temp_tkns
            total_tokens = total_tokens + tokens + tkns_bydot
        
        total_tokens = list(set(total_tokens))
        if "com" in total_tokens:
            total_tokens.remove("com")
        elif "http:" in total_tokens:
            total_tokens.remove("http:")
        
        return total_tokens

    def setup_gui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(main_frame, text="Fake Site Detector",
                               font=('Arial', 20, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Accuracy Display Frame
        accuracy_frame = ttk.LabelFrame(main_frame, text="Model Performance", padding="10")
        accuracy_frame.grid(row=1, column=0, columnspan=3, pady=10, sticky=(tk.W, tk.E))
        
        self.accuracy_label = ttk.Label(accuracy_frame, text="Training model...",
                                       font=('Arial', 11))
        self.accuracy_label.grid(row=0, column=0, sticky=tk.W)
        
        # URL input
        ttk.Label(main_frame, text="Enter URL:", font=('Arial', 12)).grid(row=2, column=0, sticky=tk.W, pady=5)
        
        self.url_entry = ttk.Entry(main_frame, width=50, font=('Arial', 10))
        self.url_entry.grid(row=3, column=0, columnspan=3, pady=5, sticky=(tk.W, tk.E))
        
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.paste_button = ttk.Button(button_frame, text="Paste",
                                      command=self.paste_url)
        self.paste_button.grid(row=0, column=0, padx=(0, 10))
        
        self.clear_button = ttk.Button(button_frame, text="Clear",
                                      command=self.clear_url)
        self.clear_button.grid(row=0, column=1, padx=(0, 10))
        
        self.analyze_button = ttk.Button(button_frame, text="Analyze URL",
                                        command=self.analyze_url)
        self.analyze_button.grid(row=0, column=2)
        
        # Result display
        self.result_text = tk.Text(main_frame, height=12, width=60,
                                  font=('Arial', 10), wrap=tk.WORD)
        self.result_text.grid(row=5, column=0, columnspan=2, pady=10)
        
        # Scrollbar for text
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=self.result_text.yview)
        scrollbar.grid(row=5, column=2, sticky=(tk.N, tk.S))
        self.result_text.configure(yscrollcommand=scrollbar.set)
        
        # Status label
        self.status_label = ttk.Label(main_frame, text="Training model...",
                                     font=('Arial', 10))
        self.status_label.grid(row=6, column=0, columnspan=3, pady=10)

    def paste_url(self):
        try:
            # Get text from clipboard
            clipboard_text = self.root.clipboard_get()
            # Clear current entry and insert clipboard text
            self.url_entry.delete(0, tk.END)
            self.url_entry.insert(0, clipboard_text.strip())
            self.status_label.config(text="URL pasted from clipboard")
        except tk.TclError:
            # Handle case where clipboard is empty or contains non-text data
            messagebox.showwarning("Paste Error", "No text found in clipboard")
            self.status_label.config(text="Paste failed: No text in clipboard")

    def clear_url(self):
        # Clear the URL entry field
        self.url_entry.delete(0, tk.END)
        # Optionally clear the results as well
        self.result_text.delete(1.0, tk.END)
        self.status_label.config(text="URL field and results cleared")

    def train_model(self):
        try:
            # Load and prepare data
            df = pd.read_csv("urls.csv")
            df[df["label"] == "good"] = df[df["label"] == "good"].sample(n = 5000, random_state=self.seed)
            df[df["label"] == "bad"] = df[df["label"] == "bad"].sample(n = 5000, random_state=self.seed)
            df.dropna(inplace=True)
            df.reset_index(drop=True, inplace=True)
            df = df.sample(frac=1, random_state=self.seed).reset_index(drop=True)
            df = np.array(df)
            random.shuffle(df)
            
            x = [d[0] for d in df]
            y = [d[1] for d in df]
            
            # Train model
            self.vectorizer = TfidfVectorizer(tokenizer=self.customtkns)
            X = self.vectorizer.fit_transform(x)
            
            xtrain, xtest, ytrain, ytest = train_test_split(X, y, test_size=0.2, random_state=self.seed)
            
            self.model = DecisionTreeClassifier(random_state=self.seed)
            self.model.fit(xtrain, ytrain)
            
            # Calculate Accuracies
            train_predictions = self.model.predict(xtrain)
            test_predictions = self.model.predict(xtest)
            
            self.train_accuracy = accuracy_score(ytrain, train_predictions)
            self.test_accuracy = accuracy_score(ytest, test_predictions)
            
            # Update GUI with accuracy information
            accuracy_text = f"Training Accuracy: {self.train_accuracy:.4f} ({self.train_accuracy*100:.2f}%)\n"
            accuracy_text += f"Test Accuracy: {self.test_accuracy:.4f} ({self.test_accuracy*100:.2f}%)"
            self.accuracy_label.config(text=accuracy_text)
            
            # Performance report
            performance_report = f"=== Decision Tree Classifier PERFORMANCE ===\n"
            performance_report += f"Training Accuracy: {self.train_accuracy*100:.2f}%\n"
            performance_report += f"Test Accuracy: {self.test_accuracy*100:.2f}%\n"
            performance_report += f"Training samples: {len(ytrain)}\n"
            performance_report += f"Test samples: {len(ytest)}\n\n"
            performance_report += "Model ready for URL analysis!"
            
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, performance_report)
            
            self.status_label.config(text="Model ready! Enter a URL to analyze.")
            
        except Exception as e:
            self.status_label.config(text=f"Error loading model: {str(e)}")
            self.accuracy_label.config(text=f"Training failed: {str(e)}")
            messagebox.showerror("Error", f"Failed to load model: {str(e)}")

    def analyze_url(self):
        url = self.url_entry.get().strip()
        
        if not url:
            messagebox.showwarning("Warning", "Please enter a URL")
            return
        
        try:
            # First check whitelist (hidden from user)
            if self.is_whitelisted(url):
                result = f"✅ SAFE: {url}\n"
                result += f"This URL is from a verified trusted website.\n"
                result += f"Confidence: 100.0%\n\n"
                result += f"Model Performance:\n"
                result += f"Training Accuracy: {self.train_accuracy*100:.2f}%\n"
                result += f"Test Accuracy: {self.test_accuracy*100:.2f}%"
                
                self.result_text.delete(1.0, tk.END)
                self.result_text.insert(tk.END, result)
                self.result_text.config(fg='green')
                return
            
            # If not whitelisted, use ML model
            if self.model is None or self.vectorizer is None:
                messagebox.showerror("Error", "Model not loaded")
                return
            
            # Predict using ML model
            get_url = [url]
            predict_url = self.vectorizer.transform(get_url)
            value = self.model.predict(predict_url)[0]
            prediction_proba = self.model.predict_proba(predict_url)[0]
            
            # Display result with confidence
            confidence = max(prediction_proba) * 100
            
            if value == "good":
                result = f"✅ SAFE: {url}\n"
                result += f"The entered URL appears to be safe.\n"
                result += f"Confidence: {confidence:.1f}%\n\n"
                self.result_text.config(fg='green')
            elif value == "bad":
                result = f"⚠️ WARNING: {url}\n"
                result += f"The entered URL appears to be fake/malicious.\n"
                result += f"Confidence: {confidence:.1f}%\n\n"
                self.result_text.config(fg='red')
            else:
                result = f"❓ UNKNOWN: Unable to classify {url}\n\n"
                self.result_text.config(fg='orange')
            
            # Add model performance info
            result += f"Model Performance:\n"
            result += f"Training Accuracy: {self.train_accuracy*100:.2f}%\n"
            result += f"Test Accuracy: {self.test_accuracy*100:.2f}%"
            
            # Clear previous results and show new one
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, result)
            
        except Exception as e:
            messagebox.showerror("Error", f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FakeSiteDetectorGUI(root)
    root.mainloop()
