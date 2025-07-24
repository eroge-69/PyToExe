#!/usr/bin/env python3
import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.utils import resample
from sklearn.calibration import CalibratedClassifierCV
import joblib
import imaplib
import email
from email.header import decode_header
import ssl
import threading
import time
from datetime import datetime, timedelta
import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import hashlib
import json
from collections import defaultdict
import logging
import os
import random
import sqlite3
import dns.resolver
import spf # pyspf
import dkim # dkimpy
from email.utils import parseaddr, parsedate_to_datetime
from bs4 import BeautifulSoup

# --- Dynamic Package Installation ---
def import_or_install(package, import_name=None):
    import_name = import_name or package
    try:
        return __import__(import_name)
    except ImportError:
        print(f"Package '{package}' not found. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"Successfully installed '{package}'.")
            return __import__(import_name)
        except Exception as e:
            print(f"Failed to install '{package}': {e}")
            sys.exit(1) # Exit if essential package cannot be installed

# Ensure ttkbootstrap is imported first for styling
try:
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.tooltip import ToolTip
except ImportError:
    print("ttkbootstrap not found. Installing...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ttkbootstrap"])
    import ttkbootstrap as ttk
    from ttkbootstrap.constants import *
    from ttkbootstrap.tooltip import ToolTip

# --- Configuration ---
# Configure logging for the application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='spoofhawk.log',
    filemode='a'  # Append to log file
)
logger = logging.getLogger('SpoofHawk')

# --- Global Constants ---
# Pre-defined list of known domains with their reputation and age (simulated)
KNOWN_DOMAINS = {
    'gmail.com': {'domain_reputation': 0.95, 'domain_age': 9855},
    'google.com': {'domain_reputation': 0.95, 'domain_age': 9855},
    'yahoo.com': {'domain_reputation': 0.90, 'domain_age': 10950},
    'outlook.com': {'domain_reputation': 0.90, 'domain_age': 7300},
    'microsoft.com': {'domain_reputation': 0.95, 'domain_age': 7300},
    'ine.com': {'domain_reputation': 0.85, 'domain_age': 3650},
    'email.ine.com': {'domain_reputation': 0.85, 'domain_age': 3650},
    'squarespace.com': {'domain_reputation': 0.90, 'domain_age': 7300},
    'simplilearnmailer.com': {'domain_reputation': 0.85, 'domain_age': 3650},
    'canva.com': {'domain_reputation': 0.90, 'domain_age': 3650},
    'durable.co': {'domain_reputation': 0.80, 'domain_age': 1825},
    'instagram.com': {'domain_reputation': 0.90, 'domain_age': 7300},
    'grammarly.com': {'domain_reputation': 0.85, 'domain_age': 3650},
    'mail.grammarly.com': {'domain_reputation': 0.85, 'domain_age': 3650},
    'gemini.com': {'domain_reputation': 0.90, 'domain_age': 3650},
    'replit.com': {'domain_reputation': 0.80, 'domain_age': 1825},
    'easeus.com': {'domain_reputation': 0.85, 'domain_age': 3650},
    'indusface.com': {'domain_reputation': 0.85, 'domain_age': 3650},
    'email.indusface.com': {'domain_reputation': 0.85, 'domain_age': 3650},
    'google-gemini-noreply@google.com': {'domain_reputation': 0.95, 'domain_age': 9855},
    'facebook.com': {'domain_reputation': 0.95, 'domain_age': 7300},
    'twitter.com': {'domain_reputation': 0.90, 'domain_age': 6000},
    'x.com': {'domain_reputation': 0.90, 'domain_age': 6000},
    'pipedrive.com': {'domain_reputation': 0.85, 'domain_age': 4000},
    'pentest-tools.com': {'domain_reputation': 0.80, 'domain_age': 2500},
    'jobleads.com': {'domain_reputation': 0.80, 'domain_age': 3000},
    'okx.com': {'domain_reputation': 0.80, 'domain_age': 1500},
    'anthropic.com': {'domain_reputation': 0.85, 'domain_age': 1000},
}

# Keywords often found in suspicious emails
SUSPICIOUS_KEYWORDS = [
    'password', 'login', 'account', 'verify', 'urgent', 'security alert',
    'suspended', 'action required', 'confirm', 'update', 'limited time',
    'click here', 'verify account', 'unauthorized access', 'invoice', 'payment',
    'bank', 'credit card', 'transaction', 'delivery', 'shipment', 'refund',
    'prize', 'lottery', 'winner', 'claim', 'inheritance', 'tax', 'IRS', 'HMRC'
]

# Keywords indicating urgency, often used in phishing
URGENCY_KEYWORDS = [
    'immediately', 'asap', 'right away', 'deadline', 'last chance',
    'expiring soon', 'limited offer', 'act now', 'don\'t miss out', 'final warning'
]

# Keywords common in marketing emails
MARKETING_KEYWORDS = [
    'offer', 'discount', 'sale', 'promotion', 'limited time', 'exclusive',
    'free', 'bonus', 'save', 'deal', 'coupon', 'newsletter', 'updates'
]

# Common legitimate redirect domains (can be expanded)
LEGIT_REDIRECT_DOMAINS = [
    'click.email.com', 'track.email.com', 'link.email.com', # Generic
    'hubspotemail.net', 'mktg.email', 'sendgrid.net', 'mailchimp.com', # ESPs
    't.co', 'bit.ly', 'ow.ly', # URL shorteners (can be abused, but also legitimate)
    # Add specific domains for known senders, e.g.,
    'bounce.simplilearnmailer.com', 'r991880.easeus.com', 'bounce.replit.com',
    'mail.instagram.com', 'bf10x.hubspotemail.net' # From your examples
]

# --- Helper for GridSearchCV Progress ---
class GridSearchCVProgressCallback:
    """
    A callback class for GridSearchCV to update a Tkinter progress bar.
    Designed to be pickleable by not directly referencing Tkinter widgets,
    instead updating a thread-safe Tkinter variable and scheduling GUI updates.
    """
    def __init__(self, root_after_method, progress_var, total_steps, start_value):
        """
        Initializes the callback.
        :param root_after_method: The `root.after` method from the main Tkinter thread.
        :param progress_var: A Tkinter DoubleVar to update the progress bar.
        :param total_steps: Total number of steps for GridSearchCV.
        :param start_value: The starting percentage for the progress bar.
        """
        self.root_after_method = root_after_method
        self.progress_var = progress_var
        self.total_steps = total_steps
        self.current_step = 0
        self.start_value = start_value
        # Cap at 90% before final evaluation to show completion
        self.step_increment = (90 - start_value) / total_steps

    def __call__(self, *args, **kwargs):
        """
        This method is called by GridSearchCV after each iteration.
        It updates the progress variable and schedules a GUI update.
        """
        self.current_step += 1
        progress_value = self.start_value + (self.current_step * self.step_increment)
        # Update the Tkinter variable directly (thread-safe for simple types)
        self.progress_var.set(min(progress_value, 90))
        # Schedule a no-op on the main thread to force update_idletasks
        # This ensures the GUI updates even if the mainloop is busy.
        self.root_after_method(0, lambda: None)

# --- EmailSpoofDetector Core Logic ---
class EmailSpoofDetector:
    """
    Core class for email spoof detection, handling model training,
    feature extraction, prediction, and persistence.
    """
    def __init__(self):
        self.model = None
        self.model_file = "spoofhawk_model.pkl"
        self.performance_metrics = {}
        # Stores mean/std for feature normalization/outlier detection
        self.feature_stats = {}
        self.dns_resolver = dns.resolver.Resolver()
        # Set short timeouts for DNS queries to prevent blocking
        self.dns_resolver.timeout = 3
        self.dns_resolver.lifetime = 3
        # Cache for DNS/WHOIS lookups to improve performance
        self.domain_cache = {}

    def load_model(self) -> bool:
        """
        Loads the pre-trained model, performance metrics, and feature statistics.
        :return: True if model and associated files are loaded successfully, False otherwise.
        """
        try:
            if os.path.exists(self.model_file):
                self.model = joblib.load(self.model_file)
                logger.info("Pre-trained model loaded successfully.")

                metrics_file = 'spoofhawk_performance.json'
                if os.path.exists(metrics_file):
                    with open(metrics_file, 'r') as f:
                        self.performance_metrics = json.load(f)
                    logger.info("Performance metrics loaded.")

                stats_file = 'spoofhawk_feature_stats.json'
                if os.path.exists(stats_file):
                    with open(stats_file, 'r') as f:
                        self.feature_stats = json.load(f)
                    logger.info("Feature stats loaded.")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to load model or metrics: {str(e)}", exc_info=True)
            return False

    def save_model(self, model, metrics, feature_stats) -> bool:
        """
        Saves the trained model, performance metrics, and feature statistics to disk.
        :param model: The trained scikit-learn model.
        :param metrics: Dictionary of performance metrics.
        :param feature_stats: Dictionary of feature statistics (mean/std).
        :return: True if saved successfully, False otherwise.
        """
        try:
            joblib.dump(model, self.model_file)
            with open('spoofhawk_performance.json', 'w') as f:
                json.dump(metrics, f, indent=4)
            with open('spoofhawk_feature_stats.json', 'w') as f:
                json.dump(feature_stats, f, indent=4)
            logger.info("Model, metrics, and feature stats saved.")
            return True
        except Exception as e:
            logger.error(f"Failed to save model or metrics: {str(e)}", exc_info=True)
            return False

    def get_all_possible_features(self) -> list:
        """
        Returns a comprehensive list of all features the model can potentially use.
        This list defines the expected columns for the training data.
        """
        return [
            'header_count', 'subject_length', 'num_recipients', 'body_length',
            'has_attachments', 'is_marketing', 'suspicious_keywords',
            'spf_pass', 'dkim_pass', 'dmarc_pass', 'arc_seal_valid',
            'domain_reputation', 'time_sent',
            'from_return_path_mismatch', 'reply_to_inconsistency',
            'num_received_headers', 'urgency_keywords',
            'ip_blacklisted', 'num_links', 'num_images', 'reply_to_diff',
            'subject_entropy', 'html_content_ratio', 'hidden_content', 'url_redirects',
            'sender_ip_blacklisted', 'unusual_header_order', 'missing_headers',
            'spf_alignment', 'dkim_alignment', 'authentication_results_mismatch',
            'is_known_domain', 'suspicious_tld', 'registry_creation_date_suspicious', 'blacklisted_domain'
        ]

    def compute_feature_stats(self, df: pd.DataFrame, feature_cols: list) -> dict:
        """
        Computes mean and standard deviation for numeric features in the DataFrame.
        These statistics are used for later normalization or outlier detection.
        :param df: The DataFrame containing the features.
        :param feature_cols: List of feature columns to compute statistics for.
        :return: A dictionary of feature statistics.
        """
        stats = {}
        for col in feature_cols:
            if col in df.columns and pd.api.types.is_numeric_dtype(df[col]):
                stats[col] = {
                    'mean': df[col].mean(),
                    # Avoid division by zero for features with no variance
                    'std': df[col].std() if df[col].std() > 0 else 0.01
                }
            else:
                logger.warning(f"Feature '{col}' not found or not numeric in dataset for stats computation.")
        self.feature_stats = stats
        return stats

    def train_model_core(self, dataset_path: str, selected_features: list, progress_callback) -> dict:
        """
        Core model training logic, designed to be run in a separate thread.
        Updates progress via the provided callback.
        :param dataset_path: Path to the training dataset (CSV or Excel).
        :param selected_features: List of features to use for training.
        :param progress_callback: A callable to update training progress in the GUI.
        :return: A dictionary of performance metrics after training.
        :raises ValueError: If dataset is invalid or missing required columns.
        """
        try:
            progress_callback(value=10, message="Loading data...")
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
            elif dataset_path.endswith(('.xls', '.xlsx')):
                df = pd.read_excel(dataset_path)
            else:
                raise ValueError("Unsupported dataset format. Please use CSV or Excel.")

            if 'is_spoofed' not in df.columns:
                raise ValueError("Missing required column: 'is_spoofed' in dataset.")
            if df['is_spoofed'].nunique() < 2:
                raise ValueError("The 'is_spoofed' column must contain at least two unique values (0 and 1) for training.")

            # Filter features to only include those present in the loaded DataFrame
            available_cols = [col for col in selected_features if col in df.columns]
            if not available_cols:
                raise ValueError("No selected features available in dataset after filtering. Check dataset columns or feature selection.")

            initial_rows = len(df)
            # Drop rows with any missing values in the selected features or target
            df.dropna(subset=available_cols + ['is_spoofed'], inplace=True)
            if len(df) < initial_rows:
                logger.info(f"Dropped {initial_rows - len(df)} rows with missing values during training data preparation.")
            if df.empty:
                raise ValueError("Dataset is empty after dropping rows with missing values. Cannot train model.")

            # Compute feature stats before balancing and splitting
            computed_feature_stats = self.compute_feature_stats(df, available_cols)

            df_majority = df[df.is_spoofed == 0]
            df_minority = df[df.is_spoofed == 1]

            if len(df_minority) == 0:
                raise ValueError("Dataset contains no 'spoofed' (1) samples. Cannot train a binary classification model.")
            if len(df_majority) == 0:
                raise ValueError("Dataset contains no 'legitimate' (0) samples. Cannot train a binary classification model.")

            progress_callback(value=20, message="Balancing dataset (Upsampling minority class)...")
            # Upsample minority class to balance the dataset
            df_minority_upsampled = resample(
                df_minority, replace=True, n_samples=len(df_majority), random_state=42
            )
            df_balanced = pd.concat([df_majority, df_minority_upsampled])
            logger.info(f"Dataset balanced: Majority {len(df_majority)}, Minority (upsampled) {len(df_minority_upsampled)}")

            X = df_balanced[available_cols]
            y = df_balanced['is_spoofed']

            progress_callback(value=30, message="Splitting data into training and testing sets...")
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, stratify=y, random_state=42
            )
            logger.info(f"Data split: Train samples {len(X_train)}, Test samples {len(X_test)}")

            progress_callback(value=40, message="Training model with GridSearchCV (this may take a while)...")
            # Hyperparameter grid for RandomForestClassifier
            param_grid = {
                'n_estimators': [100, 200],
                'max_depth': [10, 20, None], # None means nodes are expanded until all leaves are pure
                'min_samples_split': [2, 5],
                'min_samples_leaf': [1, 2],
                'max_features': ['sqrt', 'log2']
            }

            rf = RandomForestClassifier(
                oob_score=True, random_state=42, class_weight='balanced_subsample', n_jobs=-1
            )
            # Stratified K-Fold cross-validation to maintain class distribution
            cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

            # Calculate total steps for GridSearchCV progress feedback
            total_grid_steps = len(param_grid['n_estimators']) * \
                               len(param_grid['max_depth']) * \
                               len(param_grid['min_samples_split']) * \
                               len(param_grid['min_samples_leaf']) * \
                               len(param_grid['max_features']) * \
                               cv.get_n_splits()

            # Initialize the GridSearchCV progress callback
            grid_search_callback = GridSearchCVProgressCallback(
                progress_callback.root_after_method, # Pass the root.after method from the GUI
                progress_callback.progress_var,      # Pass the Tkinter DoubleVar for progress
                total_grid_steps,
                40 # Start value for GridSearchCV progress (from 40% to 90%)
            )

            # GridSearchCV for hyperparameter tuning. n_jobs=-1 enables parallelism.
            grid_search = GridSearchCV(rf, param_grid, cv=cv, scoring='f1', n_jobs=-1, verbose=1)
            # Fit the GridSearchCV. The progress callback is handled internally by the wrapper.
            grid_search.fit(X_train, y_train)

            progress_callback(value=90, message="Calibrating classifier for better probability estimates...")
            # Calibrate the classifier for more reliable probability predictions
            self.model = CalibratedClassifierCV(grid_search.best_estimator_, method='isotonic', cv='prefit')
            self.model.fit(X_train, y_train)
            logger.info("Model calibrated successfully.")

            progress_callback(value=95, message="Evaluating model performance...")
            y_pred = self.model.predict(X_test)

            # Compute and store performance metrics
            metrics = {
                'accuracy': accuracy_score(y_test, y_pred),
                'precision': precision_score(y_test, y_pred, zero_division=0),
                'recall': recall_score(y_test, y_pred, zero_division=0),
                'f1_score': f1_score(y_test, y_pred, zero_division=0),
                'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
                'classification_report': classification_report(y_test, y_pred, zero_division=0, output_dict=True),
                'feature_columns': available_cols # Store features used for training
            }
            logger.info(f"Model evaluation complete. Accuracy: {metrics['accuracy']:.2f}")

            # Save the trained model, metrics, and feature stats
            self.save_model(self.model, metrics, computed_feature_stats)
            self.performance_metrics = metrics # Update detector's metrics
            self.feature_stats = computed_feature_stats # Update detector's feature stats

            progress_callback(value=100, message="Training complete!")
            return metrics

        except Exception as e:
            logger.error(f"Training failed: {str(e)}", exc_info=True)
            progress_callback(value=0, message=f"Training failed: {str(e)}")
            raise

    def predict(self, features_df: pd.DataFrame) -> tuple[int, float]:
        """
        Makes a prediction using the loaded model.
        Ensures the input DataFrame has the same columns as the trained model.
        :param features_df: DataFrame containing features for prediction.
        :return: A tuple (prediction_label, spoof_probability).
        :raises RuntimeError: If model is not loaded or feature columns are inconsistent.
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Please train or load a model first.")

        expected_features = self.performance_metrics.get('feature_columns', [])
        if not expected_features:
            raise RuntimeError("Model's feature columns not found. Retrain the model.")

        # Reindex the input DataFrame to match the order of expected features
        # Fill missing features with 0.0 to ensure consistent input to the model
        features_df = features_df.reindex(columns=expected_features, fill_value=0.0)

        prediction = self.model.predict(features_df)[0]
        # Probability of being spoofed (class 1)
        proba = self.model.predict_proba(features_df)[0][1]
        return prediction, proba

    def extract_features(self, email_msg: email.message.Message, spf_threshold: float, dkim_threshold: float, dmarc_threshold: float) -> dict:
        """
        Extracts comprehensive features from an email message for spoof detection.
        This method processes various parts of the email including headers, body,
        and performs authentication checks.
        :param email_msg: The email.message.Message object to extract features from.
        :param spf_threshold: Threshold for SPF pass score.
        :param dkim_threshold: Threshold for DKIM pass score.
        :param dmarc_threshold: Threshold for DMARC pass score.
        :return: A dictionary of extracted features, or None if extraction fails.
        """
        # Initialize all possible features to 0.0
        features = {col: 0.0 for col in self.get_all_possible_features()}

        try:
            # --- Basic Header & Sender Info ---
            from_header = email_msg.get("From", "")
            _, from_address = parseaddr(from_header)
            domain_match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', from_address)
            sender_domain = domain_match.group(1).lower() if domain_match else None

            receiver_domain = ""
            # Attempt to find the recipient domain from various headers
            for header_name in ["To", "Delivered-To", "X-Original-To", "Envelope-To"]:
                if email_msg.get(header_name):
                    _, to_address = parseaddr(email_msg[header_name])
                    match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', to_address)
                    if match:
                        receiver_domain = match.group(1).lower()
                        break

            # Normalize header count (e.g., max 50 headers)
            features['header_count'] = min(len(email_msg.items()) / 50, 1.0)

            subject = self._decode_header(email_msg.get("Subject", ""))
            # Normalize subject length (e.g., max 100 chars)
            features['subject_length'] = min(len(subject) / 100, 1.0)
            if subject:
                # Calculate Shannon entropy of the subject
                prob = defaultdict(float)
                for char in subject:
                    prob[char] += 1
                total_chars = len(subject)
                entropy = 0
                if total_chars > 0:
                    for char_prob in prob.values():
                        p = char_prob / total_chars
                        if p > 0:
                            entropy -= p * np.log2(p)
                # Normalize subject entropy (e.g., max entropy 5.0 for typical text)
                features['subject_entropy'] = min(entropy / 5.0, 1.0)

            to_recipients = email_msg.get("To", "").split(",")
            cc_recipients = email_msg.get("CC", "").split(",") if email_msg.get("CC") else []
            # Normalize number of recipients (e.g., max 10 recipients)
            features['num_recipients'] = min((len(to_recipients) + len(cc_recipients)) / 10, 1.0)

            # --- Body Content Processing ---
            body_plain = ""
            body_html = ""
            num_links = 0
            num_images = 0
            features['has_attachments'] = 0
            extracted_links = set()

            for part in email_msg.walk():
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)

                if payload:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        decoded_payload = payload.decode(charset, errors='replace')

                        if content_type == "text/plain":
                            body_plain += decoded_payload
                        elif content_type == "text/html":
                            body_html += decoded_payload
                            soup = BeautifulSoup(decoded_payload, 'html.parser')
                            # Extract all links from HTML
                            for link_tag in soup.find_all('a', href=True):
                                extracted_links.add(link_tag['href'])
                            # Detect hidden content patterns (more specific)
                            # Look for zero font size, display:none, or very similar foreground/background colors
                            if re.search(r'font-size\s*:\s*0(px)?', decoded_payload, re.IGNORECASE) or \
                               re.search(r'display\s*:\s*none', decoded_payload, re.IGNORECASE) or \
                               re.search(r'visibility\s*:\s*hidden', decoded_payload, re.IGNORECASE) or \
                               re.search(r'color\s*:\s*#([0-9a-fA-F]{6})\s*;\s*background-color\s*:\s*#\1', decoded_payload, re.IGNORECASE):
                                features['hidden_content'] = 1

                    except Exception as e:
                        logger.debug(f"Failed to decode email part: {e}")

                if content_type.startswith("image/"):
                    num_images += 1
                # Check for attachments
                if "attachment" in str(part.get("Content-Disposition", "")):
                    features['has_attachments'] = 1

            # Combine plain and HTML text for keyword analysis
            full_body_text = body_plain + BeautifulSoup(body_html, 'html.parser').get_text() if body_html else body_plain
            # Log-normalize body length (e.g., max 10000 chars)
            features['body_length'] = np.log10(len(full_body_text) + 1) / 4.0

            total_body_len = len(body_html) + len(body_plain)
            features['html_content_ratio'] = len(body_html) / (total_body_len + 1e-6) if total_body_len > 0 else 0

            num_links = len(extracted_links)
            # Log-normalize number of links (e.g., max 100 links)
            features['num_links'] = np.log10(num_links + 1) / 2.0

            # Check for URL redirects (more nuanced logic)
            features['url_redirects'] = 0 # Reset to 0
            if sender_domain:
                for link in extracted_links:
                    link_domain_match = re.search(r'https?://(?:www\.)?([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', link)
                    if link_domain_match:
                        link_domain = link_domain_match.group(1).lower()
                        # Check if link domain is different from sender domain AND not a known legitimate redirect domain
                        # or not a subdomain of the sender domain
                        is_subdomain = link_domain.endswith("." + sender_domain) or link_domain == sender_domain
                        is_legit_redirect = any(link_domain.endswith(f".{d}") or link_domain == d for d in LEGIT_REDIRECT_DOMAINS)

                        if not is_subdomain and not is_legit_redirect:
                            features['url_redirects'] = 1
                            break

            # Normalize number of images (e.g., max 5 images)
            features['num_images'] = min(num_images / 5.0, 1.0)

            # --- Content Keyword Analysis ---
            lower_full_body = full_body_text.lower()
            features['is_marketing'] = 1 if any(re.search(r'\b' + re.escape(kw) + r'\b', lower_full_body) for kw in MARKETING_KEYWORDS) else 0
            # Score based on proportion of suspicious keywords found
            features['suspicious_keywords'] = sum(1 for kw in SUSPICIOUS_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', lower_full_body)) / len(SUSPICIOUS_KEYWORDS)
            # Score based on proportion of urgency keywords found
            features['urgency_keywords'] = sum(1 for kw in URGENCY_KEYWORDS if re.search(r'\b' + re.escape(kw) + r'\b', lower_full_body)) / len(URGENCY_KEYWORDS)

            # --- Authentication Checks ---
            received_headers = email_msg.get_all("Received", []) or []
            sender_ip = None
            # Extract the last external sender IP from Received headers
            for header in reversed(received_headers):
                ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', header)
                if ip_match:
                    sender_ip = ip_match.group(0)
                    break
                else:
                    ip_match = re.search(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]', header)
                    if ip_match:
                        sender_ip = ip_match.group(1)
                        break

            return_path = email_msg.get("Return-Path", "") or email_msg.get("ReturnPath", "")
            envelope_sender = return_path.strip("<>") if return_path else ""

            # Evaluate SPF, DKIM, DMARC, ARC using a dedicated helper method
            auth_features = self._evaluate_authentication(email_msg, sender_ip, sender_domain, envelope_sender, receiver_domain, spf_threshold, dkim_threshold, dmarc_threshold)
            features.update(auth_features)

            # --- Header Consistency & IP Reputation ---
            return_path_domain_match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', envelope_sender)
            # Check for mismatch between From: domain and Return-Path domain
            if return_path_domain_match and sender_domain:
                rp_domain = return_path_domain_match.group(1).lower()
                if rp_domain != sender_domain and not rp_domain.endswith("." + sender_domain) and not sender_domain.endswith("." + rp_domain):
                    features['from_return_path_mismatch'] = 1

            reply_to_header = email_msg.get("Reply-To", "")
            # Check for inconsistency between From: domain and Reply-To domain
            if reply_to_header:
                _, reply_to_address = parseaddr(reply_to_header)
                reply_to_domain_match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', reply_to_address)
                if reply_to_domain_match and sender_domain:
                    rt_domain = reply_to_domain_match.group(1).lower()
                    if rt_domain != sender_domain and not rt_domain.endswith("." + sender_domain) and not sender_domain.endswith("." + rt_domain):
                        features['reply_to_inconsistency'] = 1
            features['reply_to_diff'] = features['reply_to_inconsistency'] # Alias for consistency

            # Normalize number of received headers (e.g., max 10 hops)
            features['num_received_headers'] = min(len(received_headers) / 10, 1.0)

            # Check for unusual header order (e.g., Date after Subject)
            header_order = [h.lower() for h in email_msg.keys()]
            try:
                date_idx = header_order.index('date') if 'date' in header_order else -1
                subject_idx = header_order.index('subject') if 'subject' in header_order else -1
                if date_idx != -1 and subject_idx != -1 and date_idx < subject_idx:
                    features['unusual_header_order'] = 1
            except ValueError:
                pass # Header not found

            # Check for missing critical headers
            critical_headers = ['From', 'To', 'Date', 'Message-ID', 'Subject']
            missing_count = sum(1 for h in critical_headers if not email_msg.get(h))
            features['missing_headers'] = missing_count / len(critical_headers)

            # Check sender IP against DNS-based blacklists (DNSBL)
            if sender_ip:
                reversed_ip = '.'.join(reversed(sender_ip.split('.')))
                try:
                    # Use domain cache to avoid repeated DNS lookups
                    if sender_ip not in self.domain_cache:
                        self.domain_cache[sender_ip] = {}
                        # Query Spamhaus ZEN DNSBL
                        answers = self.dns_resolver.resolve(f"{reversed_ip}.zen.spamhaus.org", 'A')
                        self.domain_cache[sender_ip]['blacklisted'] = True if answers else False

                    if self.domain_cache[sender_ip].get('blacklisted', False):
                        features['sender_ip_blacklisted'] = 1
                        features['ip_blacklisted'] = 1 # Alias for consistency
                    else:
                        features['sender_ip_blacklisted'] = 0
                        features['ip_blacklisted'] = 0
                    # Ensure cache entry is always set, even if not blacklisted
                    self.domain_cache[sender_ip] = {'blacklisted': self.domain_cache[sender_ip].get('blacklisted', False)}
                except dns.resolver.NXDOMAIN:
                    # Not found in DNSBL, so not blacklisted
                    features['sender_ip_blacklisted'] = 0
                    features['ip_blacklisted'] = 0
                    self.domain_cache[sender_ip] = {'blacklisted': False}
                except Exception as e:
                    logger.debug(f"DNSBL lookup failed for {sender_ip}: {e}")
                    features['sender_ip_blacklisted'] = 0
                    features['ip_blacklisted'] = 0
                    self.domain_cache[sender_ip] = {'blacklisted': False}

            # --- Domain Reputation & Age ---
            if sender_domain:
                if sender_domain in KNOWN_DOMAINS:
                    features['domain_reputation'] = KNOWN_DOMAINS[sender_domain]['domain_reputation']
                    features['is_known_domain'] = 1
                else:
                    # Default reputation for unknown domains
                    features['domain_reputation'] = 0.5
                    features['is_known_domain'] = 0

                # Check for suspicious Top-Level Domains (TLDs)
                suspicious_tlds = ['xyz', 'top', 'gq', 'cf', 'pro', 'loan', 'click', 'bid', 'win', 'zip', 'mov']
                if any(sender_domain.endswith(f".{tld}") for tld in suspicious_tlds):
                    features['suspicious_tld'] = 1

                # Note: registry_creation_date_suspicious and blacklisted_domain
                # are currently only generated in the synthetic dataset.
                # Real-time lookup would require WHOIS, which is slow/rate-limited.

            # Extract time of day email was sent (normalized)
            try:
                date_str = email_msg.get("Date", "")
                if date_str:
                    dt = parsedate_to_datetime(date_str)
                    if dt:
                        features['time_sent'] = dt.hour / 24.0
            except Exception:
                features['time_sent'] = 0.0 # Default if date parsing fails

            return features
        except Exception as e:
            logger.error(f"Feature extraction failed for email: {email_msg.get('Subject', 'N/A')}. Error: {str(e)}", exc_info=True)
            return None

    def _evaluate_authentication(self, email_msg: email.message.Message, sender_ip: str, sender_domain: str, envelope_sender: str, receiver_domain: str, spf_threshold: float, dkim_threshold: float, dmarc_threshold: float) -> dict:
        """
        Performs enhanced email authentication checks (SPF, DKIM, DMARC, ARC)
        with active DNS lookups and alignment checks.
        :param email_msg: The email.message.Message object.
        :param sender_ip: The IP address of the sending server.
        :param sender_domain: The domain from the From: header.
        :param envelope_sender: The domain from the Return-Path header.
        :param receiver_domain: The domain of the recipient.
        :param spf_threshold: Threshold for SPF pass score.
        :param dkim_threshold: Threshold for DKIM pass score.
        :param dmarc_threshold: Threshold for DMARC pass score.
        :return: A dictionary of authentication-related features.
        """
        features = {
            'spf_pass': 0.0, 'dkim_pass': 0.0, 'dmarc_pass': 0.0, 'arc_seal_valid': 0,
            'spf_alignment': 0, 'dkim_alignment': 0, 'authentication_results_mismatch': 0
        }

        # --- SPF (Sender Policy Framework) ---
        spf_result = "none" # Default to none
        try:
            # Use envelope_sender for SPF check, as it's the domain used for SPF
            spf_domain = envelope_sender.split('@')[-1] if '@' in envelope_sender else envelope_sender
            if sender_ip and spf_domain and receiver_domain:
                spf_result, explanation = spf.check2(sender_ip, spf_domain, receiver_domain, strict=True)
                logger.debug(f"SPF check for {spf_domain} (IP: {sender_ip}): result={spf_result}, explanation={explanation}")
            else:
                logger.debug(f"Skipping SPF check due to missing info: IP={sender_ip}, SPF_Domain={spf_domain}, Receiver_Domain={receiver_domain}")
        except Exception as e:
            logger.warning(f"SPF evaluation error for {envelope_sender} from {sender_ip}: {e}", exc_info=True)
            spf_result = "permerror" # Treat exceptions as a failure state

        # Map SPF results to numerical scores
        if spf_result == 'pass':
            features['spf_pass'] = 1.0
        elif spf_result in ['neutral', 'none']:
            features['spf_pass'] = 0.5
        elif spf_result == 'softfail':
            features['spf_pass'] = 0.3
        else: # fail, temperror, permerror, etc.
            features['spf_pass'] = 0.0

        # SPF alignment check (Return-Path domain vs. From domain)
        # Normalize domains for comparison (remove subdomains if necessary for strict alignment)
        def get_base_domain(full_domain):
            parts = full_domain.split('.')
            if len(parts) > 2 and parts[-2] in ['co', 'com', 'net', 'org', 'gov', 'edu']: # Handle .co.uk etc.
                return ".".join(parts[-3:]) if len(parts) > 3 and parts[-3] in ['co'] else ".".join(parts[-2:])
            return ".".join(parts[-2:]) if len(parts) >= 2 else full_domain

        from_base_domain = get_base_domain(sender_domain) if sender_domain else None
        rp_base_domain = get_base_domain(spf_domain) if spf_domain else None

        if from_base_domain and rp_base_domain:
            # Alignment if base domains are identical or envelope sender is a subdomain of From domain
            if rp_base_domain == from_base_domain or spf_domain.endswith("." + sender_domain):
                features['spf_alignment'] = 1
            else:
                features['spf_alignment'] = 0
        else:
            features['spf_alignment'] = 0
        logger.debug(f"SPF Alignment: From_Domain={sender_domain}, RP_Domain={spf_domain}, Alignment={features['spf_alignment']}")


        # --- DKIM (DomainKeys Identified Mail) ---
        dkim_pass = 0.0
        dkim_alignment = 0
        dkim_signature = email_msg.get("DKIM-Signature")
        if dkim_signature:
            try:
                # dkimpy expects the raw message bytes
                d = dkim.DKIM(email_msg.as_bytes())
                if d.verify():
                    dkim_pass = 1.0
                    dkim_domain_bytes = d.get_domain()
                    if dkim_domain_bytes:
                        dkim_domain = dkim_domain_bytes.decode('utf-8').lower()
                        # DKIM alignment if signing domain matches From domain or is a subdomain
                        if sender_domain and (dkim_domain == sender_domain or dkim_domain.endswith("." + sender_domain)):
                            dkim_alignment = 1
                        logger.debug(f"DKIM Verification: PASS. Signing Domain: {dkim_domain}, From Domain: {sender_domain}, Alignment: {dkim_alignment}")
                    else:
                        logger.warning("DKIM verification passed but could not extract signing domain.")
                else:
                    logger.debug(f"DKIM verification failed for {sender_domain}.")
            except Exception as e:
                logger.warning(f"DKIM verification error for {sender_domain}: {e}", exc_info=True)
        else:
            logger.debug("No DKIM-Signature header found.")
        features['dkim_pass'] = dkim_pass
        features['dkim_alignment'] = dkim_alignment

        # --- DMARC (Domain-based Message Authentication, Reporting & Conformance) ---
        dmarc_record = self._get_dmarc_record(sender_domain)
        dmarc_policy = self._evaluate_dmarc_policy(dmarc_record)
        features['dmarc_policy'] = dmarc_policy # Store policy (e.g., 'none', 'quarantine', 'reject')

        # DMARC pass requires either SPF or DKIM to pass AND align
        spf_aligned_pass = (features['spf_pass'] >= spf_threshold) and (features['spf_alignment'] == 1)
        dkim_aligned_pass = (features['dkim_pass'] >= dkim_threshold) and (features['dkim_alignment'] == 1)
        features['dmarc_pass'] = 1.0 if (spf_aligned_pass or dkim_aligned_pass) else 0.0
        logger.debug(f"DMARC Pass: SPF Aligned Pass={spf_aligned_pass}, DKIM Aligned Pass={dkim_aligned_pass}, DMARC Pass={features['dmarc_pass']}")


        # --- ARC (Authenticated Received Chain) ---
        arc_seals = email_msg.get_all("ARC-Seal", [])
        arc_valid = 0
        if arc_seals:
            # Check if any ARC-Seal indicates a valid chain (cv=pass)
            for seal in arc_seals:
                if "cv=pass" in seal.lower():
                    arc_valid = 1
                    break
            else:
                logger.debug(f"ARC-Seal present but no 'cv=pass' found: {arc_seals}")
        features['arc_seal_valid'] = arc_valid
        logger.debug(f"ARC Seal Valid: {arc_valid}")

        # --- Authentication-Results Header Consistency ---
        # Check if the Authentication-Results header (if present) matches our findings
        auth_results_header = email_msg.get("Authentication-Results", "")
        if auth_results_header:
            reported_spf_pass = "spf=pass" in auth_results_header.lower()
            reported_dkim_pass = "dkim=pass" in auth_results_header.lower()
            reported_dmarc_pass = "dmarc=pass" in auth_results_header.lower()

            # Mismatch if our calculated pass status differs from the reported one
            # This is a heuristic, as different servers might interpret results slightly differently
            our_spf_pass = (features['spf_pass'] >= spf_threshold)
            our_dkim_pass = (features['dkim_pass'] >= dkim_threshold)
            our_dmarc_pass = (features['dmarc_pass'] >= dmarc_threshold)

            if (reported_spf_pass != our_spf_pass) or \
               (reported_dkim_pass != our_dkim_pass) or \
               (reported_dmarc_pass != our_dmarc_pass):
                features['authentication_results_mismatch'] = 1
                logger.debug(f"Auth-Results Mismatch: Reported SPF={reported_spf_pass} vs Our SPF={our_spf_pass}, Reported DKIM={reported_dkim_pass} vs Our DKIM={our_dkim_pass}, Reported DMARC={reported_dmarc_pass} vs Our DMARC={our_dmarc_pass}")
            else:
                features['authentication_results_mismatch'] = 0
                logger.debug("Auth-Results consistent with our findings.")
        else:
            logger.debug("No Authentication-Results header found.")

        return features

    def _evaluate_spf(self, sender_ip: str, envelope_sender_domain: str, receiver_domain: str) -> str:
        """
        Performs an SPF check with retries and detailed logging.
        :param sender_ip: The IP address of the sending server.
        :param envelope_sender_domain: The domain from the Return-Path header (or extracted from it).
        :param receiver_domain: The domain of the recipient.
        :return: The SPF result string (e.g., 'pass', 'fail', 'none').
        """
        if not sender_ip or not envelope_sender_domain or not receiver_domain:
            logger.debug(f"Cannot perform SPF check due to missing data: IP={sender_ip}, SenderDomain={envelope_sender_domain}, ReceiverDomain={receiver_domain}")
            return "none" # Cannot determine, so treat as neutral/none

        try:
            # Use domain cache for SPF results to avoid repeated lookups for the same triplet
            cache_key = f"spf_{sender_ip}_{envelope_sender_domain}_{receiver_domain}"
            if cache_key in self.domain_cache:
                logger.debug(f"SPF result from cache for {envelope_sender_domain}: {self.domain_cache[cache_key]}")
                return self.domain_cache[cache_key]

            result, explanation = spf.check2(sender_ip, envelope_sender_domain, receiver_domain, strict=True)
            logger.debug(f"SPF check for {envelope_sender_domain} (IP: {sender_ip}): result={result}, explanation={explanation}")
            self.domain_cache[cache_key] = result
            return result
        except Exception as e:
            logger.warning(f"SPF check error for {envelope_sender_domain} from {sender_ip}: {e}", exc_info=True)
            return "permerror" # Treat exceptions as a permanent error/failure state

    def _get_dmarc_record(self, domain: str) -> str | None:
        """
        Retrieves the DMARC TXT record for a given domain using DNS lookup.
        :param domain: The domain to query for.
        :return: The DMARC record string if found, None otherwise.
        """
        if not domain:
            return None
        try:
            query_name = f"_dmarc.{domain}"
            # Use domain cache for DMARC records
            if query_name in self.domain_cache:
                logger.debug(f"DMARC record from cache for {domain}: {self.domain_cache[query_name]}")
                return self.domain_cache[query_name]

            answers = self.dns_resolver.resolve(query_name, 'TXT')
            txt_records = [str(r).strip('"') for r in answers]
            for record in txt_records:
                if record.lower().startswith("v=dmarc1"):
                    self.domain_cache[query_name] = record
                    return record
            logger.debug(f"No valid DMARC record found for {domain}.")
            self.domain_cache[query_name] = None # Cache absence
            return None
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer) as e:
            logger.debug(f"No DMARC record found for {query_name}: {e}")
            self.domain_cache[query_name] = None
            return None
        except dns.exception.Timeout:
            logger.warning(f"DNS timeout retrieving DMARC record for {query_name}.")
            self.domain_cache[query_name] = None # Cache as not found for this attempt
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve DMARC record for {query_name}: {e}", exc_info=True)
            self.domain_cache[query_name] = None
            return None

    def _evaluate_dmarc_policy(self, dmarc_record: str | None) -> str:
        """
        Parses a DMARC record string and returns the policy enforcement level.
        :param dmarc_record: The DMARC record string.
        :return: The DMARC policy ('none', 'quarantine', 'reject'), defaults to 'none'.
        """
        if not dmarc_record:
            return "none"
        try:
            match = re.search(r"p=([a-zA-Z]+)", dmarc_record)
            if match:
                policy = match.group(1).lower()
                if policy in ['none', 'quarantine', 'reject']:
                    return policy
            return "none" # Default if policy not found or invalid
        except Exception as e:
            logger.debug(f"Failed to parse DMARC record policy: {e}")
            return "none"

    def _decode_header(self, header_value: str) -> str:
        """
        Decodes a potentially encoded email header (e.g., Subject, From).
        Handles various encodings specified in RFC 2047.
        :param header_value: The raw header string.
        :return: The decoded header string.
        """
        decoded_string = ""
        try:
            decoded_parts = decode_header(header_value)
            for s, charset in decoded_parts:
                if isinstance(s, bytes):
                    # Decode bytes using specified charset or utf-8 as fallback
                    decoded_string += s.decode(charset or 'utf-8', errors='ignore')
                else:
                    decoded_string += s # Already a string
        except Exception as e:
            logger.warning(f"Failed to decode header '{header_value}': {e}")
            decoded_string = header_value # Fallback to original if decoding fails
        return decoded_string

    def check_email_authentication(self, email_msg: email.message.Message, spf_threshold: float = 0.7, dkim_threshold: float = 0.7, dmarc_threshold: float = 0.7) -> dict:
        """
        Performs a comprehensive authentication check on an email message and returns
        a consolidated dictionary of results.

        :param email_msg: The email.message.Message object to check.
        :param spf_threshold: The score threshold for SPF to be considered 'PASS'.
        :param dkim_threshold: The score threshold for DKIM to be considered 'PASS'.
        :param dmarc_threshold: The score threshold for DMARC to be considered 'PASS'.
        :return: A dictionary containing the authentication results.
        """
        try:
            from_header = email_msg.get("From", "")
            _, from_address = parseaddr(from_header)
            domain_match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', from_address)
            sender_domain = domain_match.group(1).lower() if domain_match else None

            receiver_domain = ""
            for header_name in ["To", "Delivered-To", "X-Original-To", "Envelope-To"]:
                if email_msg.get(header_name):
                    _, to_address = parseaddr(email_msg[header_name])
                    match = re.search(r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', to_address)
                    if match:
                        receiver_domain = match.group(1).lower()
                        break

            received_headers = email_msg.get_all("Received", []) or []
            sender_ip = None
            for header in reversed(received_headers):
                ip_match = re.search(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', header)
                if ip_match:
                    sender_ip = ip_match.group(0)
                    break
                else:
                    ip_match = re.search(r'\[(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\]', header)
                    if ip_match:
                        sender_ip = ip_match.group(1)
                        break

            return_path = email_msg.get("Return-Path", "") or email_msg.get("ReturnPath", "")
            envelope_sender = return_path.strip("<>") if return_path else ""

            auth_features = self._evaluate_authentication(
                email_msg, sender_ip, sender_domain, envelope_sender, receiver_domain,
                spf_threshold, dkim_threshold, dmarc_threshold
            )

            # Consolidate results for easier interpretation
            results = {
                "spf_result": "PASS" if auth_features.get('spf_pass', 0) >= spf_threshold else "FAIL",
                "spf_score": auth_features.get('spf_pass', 0),
                "spf_alignment": "Aligned" if auth_features.get('spf_alignment', 0) == 1 else "Not Aligned",
                "dkim_result": "PASS" if auth_features.get('dkim_pass', 0) >= dkim_threshold else "FAIL",
                "dkim_score": auth_features.get('dkim_pass', 0),
                "dkim_alignment": "Aligned" if auth_features.get('dkim_alignment', 0) == 1 else "Not Aligned",
                "dmarc_result": "PASS" if auth_features.get('dmarc_pass', 0) >= dmarc_threshold else "FAIL",
                "dmarc_policy": auth_features.get('dmarc_policy', 'none'),
                "arc_result": "PASS" if auth_features.get('arc_seal_valid', 0) == 1 else "FAIL",
                "authentication_results_header_mismatch": "Yes" if auth_features.get('authentication_results_mismatch', 0) == 1 else "No",
                "sender_ip": sender_ip if sender_ip else "N/A",
                "sender_domain": sender_domain if sender_domain else "N/A",
                "envelope_sender": envelope_sender if envelope_sender else "N/A",
                "receiver_domain": receiver_domain if receiver_domain else "N/A"
            }
            return results
        except Exception as e:
            logger.error(f"Error during email authentication check: {e}", exc_info=True)
            return {"error": f"Authentication check failed: {str(e)}"}


# --- EmailSpoofDetectorApp GUI ---
class EmailSpoofDetectorApp:
    """
    Tkinter GUI application for Email Spoof Detection (SpoofHawk).
    Manages user interface, model training, email analysis, and real-time monitoring.
    """
    def __init__(self, root: tk.Tk):
        """
        Initializes the main application window and components.
        :param root: The root Tkinter window.
        """
        self.root = root
        self.root.title("SpoofHawk: Advanced Email Spoof Detection")
        self.root.geometry("1400x1000")
        self.style = ttk.Style("darkly") # Use ttkbootstrap theme

        self.detector = EmailSpoofDetector()

        # Model and monitoring variables
        self.model = None # Reference to detector.model after loading/training
        self.model_file = self.detector.model_file
        self.default_dataset_file = "default_dataset.csv"
        self.dataset_dir = "datasets"
        self.monitoring_active = False
        self.last_checked = None # Timestamp of last email check during monitoring
        self.email_stats = defaultdict(int) # Statistics for analyzed emails
        self.processed_email_hashes = set() # To avoid re-processing emails in monitoring
        self.mail_connection = None # IMAP connection object
        # Threads for background operations
        self.monitoring_thread = None
        self.fetch_thread = None
        self.analysis_thread = None
        self.training_thread = None

        # Blacklist and whitelist for manual overrides
        self.blacklist = set() # Stores email hashes
        self.whitelist = set() # Stores email hashes
        self.blacklist_patterns = [] # Stores regex patterns
        self.whitelist_patterns = [] # Stores regex patterns

        # Feature options (BooleanVar for GUI checkboxes)
        self.feature_options = {
            "Header Analysis": tk.BooleanVar(value=True),
            "Content Analysis": tk.BooleanVar(value=True),
            "SPF/DKIM/DMARC": tk.BooleanVar(value=True),
            "ARC Validation": tk.BooleanVar(value=True),
            "Metadata Analysis": tk.BooleanVar(value=True)
        }

        # Database for persistent storage of blacklist/whitelist
        self.db_file = "spoofhawk.db"
        self.init_database()

        # Tkinter variables for GUI elements
        self.dataset_path = tk.StringVar(value="")
        self.training_status_text = tk.StringVar(value="Status: Ready")
        self.training_progress_var = tk.DoubleVar(value=0) # For progress bar
        # Authentication thresholds, adjustable by user
        self.spf_threshold = ttk.DoubleVar(value=0.7)
        self.dkim_threshold = ttk.DoubleVar(value=0.7)
        self.dmarc_threshold = ttk.DoubleVar(value=0.7)

        # Create necessary directories
        os.makedirs(self.dataset_dir, exist_ok=True)

        # Check for and generate default dataset if missing
        self.check_default_dataset()

        # Build the GUI
        self.create_widgets()

        # Load model and lists on application startup
        self.load_model_and_lists()

        # Bind window close event to cleanup resources
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """
        Handles the window closing event. Stops monitoring, disconnects IMAP,
        and destroys the Tkinter root window.
        """
        if self.monitoring_active:
            self.toggle_monitoring() # Stop monitoring gracefully
        if self.mail_connection:
            self.disconnect_imap() # Disconnect IMAP if still connected
        self.root.destroy()
        logger.info("SpoofHawk application closed.")

    def init_database(self):
        """
        Initializes the SQLite database for persistent storage of blacklist/whitelist entries.
        Creates tables if they don't exist.
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                c = conn.cursor()
                c.execute('''CREATE TABLE IF NOT EXISTS blacklist
                            (type TEXT, value TEXT UNIQUE, pattern BOOLEAN, created_at TIMESTAMP)''')
                c.execute('''CREATE TABLE IF NOT EXISTS whitelist
                            (type TEXT, value TEXT UNIQUE, pattern BOOLEAN, created_at TIMESTAMP)''')
                conn.commit()
            logger.info("Database initialized successfully.")
        except sqlite3.Error as e:
            logger.error(f"Database initialization failed: {e}", exc_info=True)
            messagebox.showerror("Error", f"Database initialization failed: {e}")

    def load_lists(self):
        """
        Loads blacklist and whitelist entries (hashes and patterns) from the database
        into application memory.
        """
        try:
            self.blacklist.clear()
            self.whitelist.clear()
            self.blacklist_patterns.clear()
            self.whitelist_patterns.clear()

            with sqlite3.connect(self.db_file) as conn:
                c = conn.cursor()
                c.execute("SELECT type, value, pattern FROM blacklist")
                for row in c.fetchall():
                    if row[2]: # If it's a pattern
                        self.blacklist_patterns.append(row[1])
                    else: # If it's an email hash
                        self.blacklist.add(row[1])

                c.execute("SELECT type, value, pattern FROM whitelist")
                for row in c.fetchall():
                    if row[2]: # If it's a pattern
                        self.whitelist_patterns.append(row[1])
                    else: # If it's an email hash
                        self.whitelist.add(row[1])
            logger.info("Blacklist and Whitelist loaded from database.")
        except sqlite3.Error as e:
            logger.error(f"Failed to load lists from database: {e}", exc_info=True)

    def save_list_entry(self, table: str, type_: str, value: str, is_pattern: bool):
        """
        Saves a single entry (hash or pattern) to the specified blacklist or whitelist table in the database.
        Uses INSERT OR IGNORE to prevent duplicate entries.
        :param table: 'blacklist' or 'whitelist'.
        :param type_: 'email_hash' or 'pattern'.
        :param value: The hash string or regex pattern.
        :param is_pattern: Boolean indicating if the value is a regex pattern.
        """
        try:
            with sqlite3.connect(self.db_file) as conn:
                c = conn.cursor()
                c.execute(f"INSERT OR IGNORE INTO {table} (type, value, pattern, created_at) VALUES (?, ?, ?, ?)",
                         (type_, value, is_pattern, datetime.now()))
                conn.commit()
            logger.info(f"Saved '{value}' to {table}.")
        except sqlite3.Error as e:
            logger.error(f"Failed to save to {table}: {e}", exc_info=True)

    def check_default_dataset(self):
        """
        Checks if the default synthetic dataset exists. If not, it generates a new one.
        """
        default_path = os.path.join(self.dataset_dir, self.default_dataset_file)
        if not os.path.exists(default_path):
            logger.info("Default dataset not found. Generating a new one.")
            self.generate_default_dataset()
        else:
            self.dataset_path.set(default_path)
            logger.info(f"Default dataset found at: {default_path}")

    def generate_default_dataset(self):
        """
        Generates a synthetic default dataset with a mix of legitimate and spoofed emails
        and various features. This dataset is used for initial model training if no
        other dataset is provided.
        """
        try:
            logger.info("Generating enhanced default dataset...")
            feature_cols = self.detector.get_all_possible_features()
            all_cols = list(set(feature_cols + ['is_spoofed']))
            num_records = 5000
            data = {col: [] for col in all_cols}

            for _ in range(num_records):
                # Randomly assign spoofed status, with a bias towards legitimate
                is_spoofed = random.choices([0, 1], weights=[0.7, 0.3])[0]
                is_marketing = random.random() < 0.3 and not is_spoofed

                # Simulate authentication results based on spoofed status
                # More realistic simulation:
                # Legitimate emails mostly pass, but some might fail (e.g., misconfiguration)
                # Spoofed emails mostly fail, but some might pass (e.g., weak SPF, compromised account)
                if is_spoofed:
                    spf_pass = random.choices([0.0, 0.3, 0.5, 1.0], weights=[0.6, 0.2, 0.1, 0.1])[0] # More fails for spoofed
                    dkim_pass = random.choices([0.0, 1.0], weights=[0.7, 0.3])[0] # More fails for spoofed
                    spf_alignment = 0 if spf_pass < 0.7 else random.randint(0,1) # Alignment more likely to fail if SPF fails
                    dkim_alignment = 0 if dkim_pass < 0.7 else random.randint(0,1) # Alignment more likely to fail if DKIM fails
                    authentication_results_mismatch = random.choices([0, 1], weights=[0.3, 0.7])[0] # More mismatches for spoofed
                    arc_pass = random.choices([0, 1], weights=[0.8, 0.2])[0] # Less likely to have valid ARC
                else: # Legitimate
                    spf_pass = random.choices([0.0, 0.5, 1.0], weights=[0.1, 0.1, 0.8])[0] # Mostly passes
                    dkim_pass = random.choices([0.0, 1.0], weights=[0.1, 0.9])[0] # Mostly passes
                    spf_alignment = 1 if spf_pass > 0.7 else random.randint(0,1) # Mostly aligned if SPF passes
                    dkim_alignment = 1 if dkim_pass > 0.7 else random.randint(0,1) # Mostly aligned if DKIM passes
                    authentication_results_mismatch = random.choices([0, 1], weights=[0.9, 0.1])[0] # Mostly consistent
                    arc_pass = random.choices([0, 1], weights=[0.2, 0.8])[0] # More likely to have valid ARC

                # DMARC pass depends on SPF/DKIM aligned pass
                dmarc_pass = 1.0 if ((spf_pass >= 0.7 and spf_alignment == 1) or (dkim_pass >= 0.7 and dkim_alignment == 1)) else 0.0


                # Simulate various header and content features
                header_count = random.randint(5, 30) / 30
                subject_length = random.randint(10, 120) / 100
                subject_entropy = random.uniform(0.5, 1.0) if is_spoofed else random.uniform(0.1, 0.8)
                num_recipients = random.randint(1, 10) / 10

                body_length = np.log10(random.randint(100, 10000) + 1) / 4.0
                has_attachments = random.randint(0, 1) if is_spoofed else random.randint(0, 1)

                # Hidden content: more likely in spoofed, but can be in legitimate marketing
                if is_spoofed:
                    hidden_content = random.choices([0, 1], weights=[0.3, 0.7])[0]
                else:
                    hidden_content = random.choices([0, 1], weights=[0.8, 0.2])[0] # Less likely for legitimate

                html_content_ratio = random.uniform(0.0, 1.0)

                # URL redirects: more likely in spoofed, but also in legitimate marketing
                if is_spoofed:
                    url_redirects = random.choices([0, 1], weights=[0.2, 0.8])[0]
                else:
                    url_redirects = random.choices([0, 1], weights=[0.5, 0.5])[0] # Can be present in legitimate

                suspicious_keywords_val = random.randint(0, 3) / 5 if is_spoofed else random.randint(0, 1) / 5
                is_marketing_val = 1 if is_marketing else 0
                urgency_keywords_val = random.randint(0, 2) / 5 if is_spoofed else random.randint(0, 1) / 5

                # Simulate domain reputation and age
                domain_age = random.randint(30, 10000) / 10000
                domain_reputation = random.uniform(0.2, 0.7) if is_spoofed else random.uniform(0.7, 1.0)
                time_sent = random.randint(0, 23) / 24
                is_known_domain = 0 if is_spoofed else 1
                suspicious_tld = 1 if is_spoofed and random.random() < 0.3 else 0
                registry_creation_date_suspicious = 1 if is_spoofed and random.random() < 0.2 else 0
                blacklisted_domain = 1 if is_spoofed and random.random() < 0.1 else 0

                from_return_path_mismatch = random.randint(0, 1) if is_spoofed else 0
                reply_to_inconsistency = random.randint(0, 1) if is_spoofed else 0
                num_received_headers = random.randint(1, 15) / 15
                sender_ip_blacklisted = random.randint(0, 1) if is_spoofed else 0
                unusual_header_order = random.randint(0,1) if is_spoofed else 0
                missing_headers = random.randint(0,1) if is_spoofed else 0

                num_links = np.log10(random.randint(0, 15) + 1) / 2.0
                num_images = random.randint(0, 10) / 10
                reply_to_diff = reply_to_inconsistency

                # Populate data dictionary for all possible features
                for col in all_cols:
                    if col == 'is_spoofed': data[col].append(is_spoofed)
                    elif col == 'header_count': data[col].append(header_count)
                    elif col == 'subject_length': data[col].append(subject_length)
                    elif col == 'subject_entropy': data[col].append(subject_entropy)
                    elif col == 'num_recipients': data[col].append(num_recipients)
                    elif col == 'body_length': data[col].append(body_length)
                    elif col == 'has_attachments': data[col].append(has_attachments)
                    elif col == 'is_marketing': data[col].append(is_marketing_val)
                    elif col == 'suspicious_keywords': data[col].append(suspicious_keywords_val)
                    elif col == 'spf_pass': data[col].append(spf_pass)
                    elif col == 'dkim_pass': data[col].append(dkim_pass)
                    elif col == 'dmarc_pass': data[col].append(dmarc_pass)
                    elif col == 'arc_seal_valid': data[col].append(arc_pass)
                    elif col == 'domain_reputation': data[col].append(domain_reputation)
                    elif col == 'time_sent': data[col].append(time_sent)
                    elif col == 'from_return_path_mismatch': data[col].append(from_return_path_mismatch)
                    elif col == 'reply_to_inconsistency': data[col].append(reply_to_inconsistency)
                    elif col == 'num_received_headers': data[col].append(num_received_headers)
                    elif col == 'urgency_keywords': data[col].append(urgency_keywords_val)
                    elif col == 'ip_blacklisted': data[col].append(sender_ip_blacklisted)
                    elif col == 'num_links': data[col].append(num_links)
                    elif col == 'num_images': data[col].append(num_images)
                    elif col == 'reply_to_diff': data[col].append(reply_to_diff)
                    elif col == 'html_content_ratio': data[col].append(html_content_ratio)
                    elif col == 'hidden_content': data[col].append(hidden_content)
                    elif col == 'url_redirects': data[col].append(url_redirects)
                    elif col == 'sender_ip_blacklisted': data[col].append(sender_ip_blacklisted)
                    elif col == 'unusual_header_order': data[col].append(unusual_header_order)
                    elif col == 'missing_headers': data[col].append(missing_headers)
                    elif col == 'spf_alignment': data[col].append(spf_alignment)
                    elif col == 'dkim_alignment': data[col].append(dkim_alignment)
                    elif col == 'authentication_results_mismatch': data[col].append(authentication_results_mismatch)
                    elif col == 'is_known_domain': data[col].append(is_known_domain)
                    elif col == 'suspicious_tld': data[col].append(suspicious_tld)
                    elif col == 'registry_creation_date_suspicious': data[col].append(registry_creation_date_suspicious)
                    elif col == 'blacklisted_domain': data[col].append(blacklisted_domain)
                    else:
                        data[col].append(0.0) # Default for any unhandled new features

            df = pd.DataFrame(data)
            default_path = os.path.join(self.dataset_dir, self.default_dataset_file)
            df.to_csv(default_path, index=False)
            logger.info(f"Generated enhanced default dataset: {default_path}")
            self.dataset_path.set(default_path)
            messagebox.showinfo("Success", "Default dataset generated successfully!")
        except Exception as e:
            logger.error(f"Failed to generate default dataset: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to generate default dataset: {str(e)}")

    def show_status(self, message: str):
        """
        Displays a status message in the GUI's training tab.
        This method is thread-safe as it uses `root.after` to update the GUI.
        :param message: The status message to display.
        """
        self.root.after(0, lambda: self.training_status_text.set(message))
        self.root.after(0, self.root.update_idletasks) # Force GUI update

    def create_widgets(self):
        """
        Creates and lays out all the Tkinter widgets for the application's GUI.
        Organizes widgets into notebooks and frames for a structured interface.
        """
        try:
            self.notebook = ttk.Notebook(self.root, style="primary.TNotebook")
            self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

            # Create main tabs
            self.training_frame = ttk.Frame(self.notebook)
            self.analysis_frame = ttk.Frame(self.notebook)
            self.monitoring_frame = ttk.Frame(self.notebook)
            self.performance_frame = ttk.Frame(self.notebook)
            self.settings_frame = ttk.Frame(self.notebook)

            # Add tabs to the notebook
            self.notebook.add(self.training_frame, text="Model Training")
            self.notebook.add(self.analysis_frame, text="Email Analysis")
            self.notebook.add(self.monitoring_frame, text="Real-Time Monitoring")
            self.notebook.add(self.performance_frame, text="Performance Metrics")
            self.notebook.add(self.settings_frame, text="Settings")

            # --- Training Tab Layout ---
            training_pane = ttk.PanedWindow(self.training_frame, orient=tk.VERTICAL)
            training_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Dataset selection section
            dataset_frame = ttk.LabelFrame(training_pane, text="Dataset", bootstyle="primary")
            training_pane.add(dataset_frame, weight=1)

            ttk.Label(dataset_frame, text="Dataset Path:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            entry_widget = ttk.Entry(dataset_frame, textvariable=self.dataset_path, width=50, state='readonly')
            entry_widget.grid(row=0, column=1, padx=5, pady=5)
            ToolTip(entry_widget, "Select a CSV or Excel file containing training data")

            ttk.Button(dataset_frame, text="Browse", command=self.browse_dataset).grid(row=0, column=2, padx=5)

            # Feature selection section
            features_frame = ttk.LabelFrame(training_pane, text="Feature Selection", bootstyle="primary")
            training_pane.add(features_frame, weight=1)

            feature_groups = {
                "Authentication": ["SPF/DKIM/DMARC", "ARC Validation"],
                "Content & Structure": ["Header Analysis", "Content Analysis", "Metadata Analysis"]
            }

            row_idx = 0
            for group_name, features_in_group in feature_groups.items():
                ttk.Label(features_frame, text=f"--- {group_name} ---", bootstyle="info").grid(row=row_idx, column=0, columnspan=3, pady=5, sticky="w")
                row_idx += 1
                for i, feature in enumerate(features_in_group):
                    if feature not in self.feature_options:
                        self.feature_options[feature] = tk.BooleanVar(value=True) # Ensure BooleanVar exists
                    ttk.Checkbutton(features_frame, text=feature, variable=self.feature_options[feature], bootstyle="round-toggle").grid(row=row_idx + i // 3, column=i % 3, padx=5, pady=5, sticky="w")
                row_idx += (len(features_in_group) + 2) // 3 # Advance row index for next group

            # Training control section
            control_frame = ttk.Frame(training_pane)
            training_pane.add(control_frame, weight=1)

            ttk.Label(control_frame, textvariable=self.training_status_text).pack(pady=5)
            ttk.Button(control_frame, text="Train Model", command=self.train_model, bootstyle="success").pack(pady=10)
            self.training_progress = ttk.Progressbar(control_frame, orient=tk.HORIZONTAL, length=400, mode='determinate', bootstyle="success-striped", variable=self.training_progress_var)
            self.training_progress.pack(pady=10)

            # --- Analysis Tab Layout ---
            analysis_pane = ttk.PanedWindow(self.analysis_frame, orient=tk.HORIZONTAL)
            analysis_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Email connection and fetch controls
            conn_frame = ttk.LabelFrame(analysis_pane, text="Email Connection", bootstyle="primary")
            analysis_pane.add(conn_frame, weight=1)

            ttk.Label(conn_frame, text="IMAP Server:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.imap_server = ttk.Combobox(conn_frame, values=["imap.gmail.com", "imap.mail.yahoo.com", "imap.outlook.com", "outlook.office365.com"], bootstyle="secondary")
            self.imap_server.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            self.imap_server.set("imap.gmail.com")

            ttk.Label(conn_frame, text="Username:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            self.username = ttk.Entry(conn_frame)
            self.username.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

            ttk.Label(conn_frame, text="Password/App Password:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
            self.password = ttk.Entry(conn_frame, show="*") # Hide password input
            self.password.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

            ttk.Label(conn_frame, text="Number of Emails:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
            self.email_count = ttk.Spinbox(conn_frame, from_=1, to=100, width=5)
            self.email_count.grid(row=3, column=1, padx=5, pady=5, sticky="w")
            self.email_count.set(10)

            ttk.Button(conn_frame, text="Fetch Emails", command=self.fetch_emails, bootstyle="primary").grid(row=4, column=0, pady=10, sticky="ew")
            ttk.Button(conn_frame, text="Analyze All", command=self.analyze_all_emails, bootstyle="primary").grid(row=4, column=1, pady=10, sticky="ew")

            conn_frame.grid_columnconfigure(1, weight=1) # Allow column 1 to expand

            # Email listbox and controls
            email_frame = ttk.LabelFrame(analysis_pane, text="Emails", bootstyle="primary")
            analysis_pane.add(email_frame, weight=2)

            self.email_listbox = tk.Listbox(email_frame, height=20, width=60, selectmode=tk.SINGLE, font=('TkDefaultFont', 10))
            self.email_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
            self.email_listbox.bind('<Double-Button-1>', self.open_email_popup) # Double-click to open details

            email_controls = ttk.Frame(email_frame)
            email_controls.pack(fill=tk.X, pady=5)
            ttk.Button(email_controls, text="Blacklist", command=self.blacklist_selected_email, bootstyle="danger").pack(side=tk.LEFT, padx=5, expand=True)
            ttk.Button(email_controls, text="Whitelist", command=self.whitelist_selected_email, bootstyle="success").pack(side=tk.LEFT, padx=5, expand=True)
            ttk.Button(email_controls, text="Remove from List", command=self.remove_selected_list, bootstyle="warning").pack(side=tk.LEFT, padx=5, expand=True)

            # Analysis results display
            results_frame = ttk.LabelFrame(analysis_pane, text="Analysis Results", bootstyle="primary")
            analysis_pane.add(results_frame, weight=3)

            self.result_text = scrolledtext.ScrolledText(results_frame, height=20, width=80, state=tk.DISABLED, font=('TkDefaultFont', 10))
            self.result_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # --- Monitoring Tab Layout ---
            monitor_pane = ttk.PanedWindow(self.monitoring_frame, orient=tk.VERTICAL)
            monitor_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Monitoring settings
            monitor_settings = ttk.LabelFrame(monitor_pane, text="Monitoring Settings", bootstyle="primary")
            monitor_pane.add(monitor_settings, weight=1)

            ttk.Label(monitor_settings, text="Check Interval (min):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.interval = ttk.Spinbox(monitor_settings, from_=0.1, to=60.0, increment=0.1, width=5, format="%.1f")
            self.interval.grid(row=0, column=1, padx=5, pady=5, sticky="w")
            self.interval.set(0.5) # Default check every 30 seconds

            self.auto_quarantine = tk.BooleanVar(value=True)
            ttk.Checkbutton(monitor_settings, text="Auto-Quarantine", variable=self.auto_quarantine, bootstyle="round-toggle").grid(row=0, column=2, padx=5, pady=5, sticky="w")

            self.notify_admin = tk.BooleanVar(value=True)
            ttk.Checkbutton(monitor_settings, text="Notify Admin", variable=self.notify_admin, bootstyle="round-toggle").grid(row=0, column=3, padx=5, pady=5, sticky="w")

            self.monitor_button = ttk.Button(monitor_settings, text="Start Monitoring", command=self.toggle_monitoring, bootstyle="success")
            self.monitor_button.grid(row=1, column=0, pady=10, sticky="ew")

            self.status_label = ttk.Label(monitor_settings, text="Monitoring: OFF")
            self.status_label.grid(row=1, column=1, columnspan=3, pady=10, sticky="w")

            monitor_settings.grid_columnconfigure(1, weight=1)

            # Monitoring log display
            monitor_log = ttk.LabelFrame(monitor_pane, text="Monitoring Log", bootstyle="primary")
            monitor_pane.add(monitor_log, weight=3)

            self.monitor_text = scrolledtext.ScrolledText(monitor_log, height=25, width=100, state=tk.DISABLED, font=('TkDefaultFont', 10))
            self.monitor_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # --- Performance Metrics Tab Layout ---
            performance_pane = ttk.PanedWindow(self.performance_frame, orient=tk.VERTICAL)
            performance_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Model performance metrics display
            metrics_frame = ttk.LabelFrame(performance_pane, text="Model Performance", bootstyle="primary")
            performance_pane.add(metrics_frame, weight=2)

            self.metrics_text = scrolledtext.ScrolledText(metrics_frame, height=15, width=80, state=tk.DISABLED, font=('TkDefaultFont', 10))
            self.metrics_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Matplotlib figure for Confusion Matrix
            self.figure, self.ax = plt.subplots(figsize=(6, 4))
            self.canvas = FigureCanvasTkAgg(self.figure, master=metrics_frame)
            self.canvas_widget = self.canvas.get_tk_widget()
            self.canvas_widget.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Email analysis statistics display
            stats_frame = ttk.LabelFrame(performance_pane, text="Email Analysis Statistics", bootstyle="primary")
            performance_pane.add(stats_frame, weight=1)

            self.stats_text = scrolledtext.ScrolledText(stats_frame, height=8, width=80, state=tk.DISABLED, font=('TkDefaultFont', 10))
            self.stats_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # --- Settings Tab Layout ---
            settings_pane = ttk.PanedWindow(self.settings_frame, orient=tk.VERTICAL)
            settings_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Blacklist management
            blacklist_frame = ttk.LabelFrame(settings_pane, text="Blacklist Management", bootstyle="primary")
            settings_pane.add(blacklist_frame, weight=1)

            ttk.Label(blacklist_frame, text="Add Pattern (Regex):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.blacklist_pattern_entry = ttk.Entry(blacklist_frame, width=40)
            self.blacklist_pattern_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            ttk.Button(blacklist_frame, text="Add", command=self.add_blacklist_pattern).grid(row=0, column=2, padx=5, pady=5)

            # Whitelist management
            whitelist_frame = ttk.LabelFrame(settings_pane, text="Whitelist Management", bootstyle="primary")
            settings_pane.add(whitelist_frame, weight=1)

            ttk.Label(whitelist_frame, text="Add Pattern (Regex):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            self.whitelist_pattern_entry = ttk.Entry(whitelist_frame, width=40)
            self.whitelist_pattern_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            ttk.Button(whitelist_frame, text="Add", command=self.add_whitelist_pattern).grid(row=0, column=2, padx=5, pady=5)

            # List import/export
            list_io_frame = ttk.LabelFrame(settings_pane, text="List Import/Export", bootstyle="primary")
            settings_pane.add(list_io_frame, weight=1)

            ttk.Button(list_io_frame, text="Export Lists", command=self.export_lists).grid(row=0, column=0, padx=5, pady=5, sticky="ew")
            ttk.Button(list_io_frame, text="Import Lists", command=self.import_lists).grid(row=0, column=1, padx=5, pady=5, sticky="ew")

            # Authentication thresholds adjustment
            auth_thresholds_frame = ttk.LabelFrame(settings_pane, text="Authentication Thresholds", bootstyle="primary")
            settings_pane.add(auth_thresholds_frame, weight=1)

            ttk.Label(auth_thresholds_frame, text="SPF Pass Threshold:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
            ttk.Scale(auth_thresholds_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.spf_threshold, length=200, command=lambda s: self.spf_threshold.set(round(float(s), 2))).grid(row=0, column=1, padx=5, pady=5, sticky="ew")
            ttk.Label(auth_thresholds_frame, textvariable=self.spf_threshold, width=4).grid(row=0, column=2, padx=5, pady=5, sticky="w")

            ttk.Label(auth_thresholds_frame, text="DKIM Pass Threshold:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
            ttk.Scale(auth_thresholds_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.dkim_threshold, length=200, command=lambda s: self.dkim_threshold.set(round(float(s), 2))).grid(row=1, column=1, padx=5, pady=5, sticky="ew")
            ttk.Label(auth_thresholds_frame, textvariable=self.dkim_threshold, width=4).grid(row=1, column=2, padx=5, pady=5, sticky="w")

            ttk.Label(auth_thresholds_frame, text="DMARC Pass Threshold:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
            ttk.Scale(auth_thresholds_frame, from_=0.0, to=1.0, orient=tk.HORIZONTAL, variable=self.dmarc_threshold, length=200, command=lambda s: self.dmarc_threshold.set(round(float(s), 2))).grid(row=2, column=1, padx=5, pady=5, sticky="ew")
            ttk.Label(auth_thresholds_frame, textvariable=self.dmarc_threshold, width=4).grid(row=2, column=2, padx=5, pady=5, sticky="w")

            # Configure column weights for frames in settings tab
            for frame in [blacklist_frame, whitelist_frame, list_io_frame, auth_thresholds_frame]:
                frame.grid_columnconfigure(1, weight=1)

            logger.info("GUI widgets created successfully.")
        except Exception as e:
            logger.critical(f"Failed to create GUI: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to create GUI: {str(e)}")
            raise

    def open_email_popup(self, event):
        """
        Opens a new Toplevel window to display detailed information about a selected email,
        including raw headers, plain text body, HTML body, and extracted features.
        :param event: Tkinter event object (e.g., double-click).
        """
        try:
            selection = self.email_listbox.curselection()
            if not selection:
                return
            idx = selection[0]
            email_data = self.emails[idx]
            msg = email_data['message']

            body_plain = ""
            body_html = ""
            # Extract plain and HTML parts of the email body
            for part in msg.walk():
                content_type = part.get_content_type()
                payload = part.get_payload(decode=True)
                if payload:
                    try:
                        charset = part.get_content_charset() or 'utf-8'
                        decoded_payload = payload.decode(charset, errors='replace')
                        if content_type == "text/plain":
                            body_plain += decoded_payload
                        elif content_type == "text/html":
                            body_html += decoded_payload
                    except Exception:
                        pass # Ignore decoding errors for parts

            popup = tk.Toplevel(self.root)
            popup.title(f"Email Details: {email_data['subject'][:70]}...")
            popup.geometry("1000x700")
            popup.transient(self.root) # Make popup transient to main window
            popup.grab_set() # Grab focus, block interaction with main window

            detail_notebook = ttk.Notebook(popup)
            detail_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

            # Headers tab
            headers_frame = ttk.Frame(detail_notebook)
            detail_notebook.add(headers_frame, text="Headers")
            headers_text = scrolledtext.ScrolledText(headers_frame, wrap=tk.WORD, state=tk.DISABLED, font=('TkDefaultFont', 9))
            headers_text.pack(fill=tk.BOTH, expand=True)
            headers_text.config(state=tk.NORMAL)
            headers_text.insert(tk.END, f"Subject: {email_data['subject']}\n")
            headers_text.insert(tk.END, f"From: {email_data['from']}\n")
            headers_text.insert(tk.END, f"Date: {email_data['date']}\n\n")
            headers_text.insert(tk.END, "Raw Headers:\n")
            for k, v in msg.items():
                headers_text.insert(tk.END, f"{k}: {v}\n")
            headers_text.config(state=tk.DISABLED)

            # Plain Text Body tab
            plain_frame = ttk.Frame(detail_notebook)
            detail_notebook.add(plain_frame, text="Plain Text Body")
            plain_text = scrolledtext.ScrolledText(plain_frame, wrap=tk.WORD, state=tk.DISABLED, font=('TkDefaultFont', 9))
            plain_text.pack(fill=tk.BOTH, expand=True)
            plain_text.config(state=tk.NORMAL)
            plain_text.insert(tk.END, body_plain)
            plain_text.config(state=tk.DISABLED)

            # HTML Body tab
            html_frame = ttk.Frame(detail_notebook)
            detail_notebook.add(html_frame, text="HTML Body")
            html_text = scrolledtext.ScrolledText(html_frame, wrap=tk.WORD, state=tk.DISABLED, font=('TkDefaultFont', 9))
            html_text.pack(fill=tk.BOTH, expand=True)
            html_text.config(state=tk.NORMAL)
            html_text.insert(tk.END, body_html)
            html_text.config(state=tk.DISABLED)

            # Extracted Features display
            features_frame = ttk.LabelFrame(popup, text="Extracted Features", bootstyle="secondary")
            features_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
            feature_text = scrolledtext.ScrolledText(features_frame, height=10, state=tk.DISABLED, font=('TkDefaultFont', 9))
            feature_text.pack(fill=tk.BOTH, expand=True)

            # Extract features for the selected email and display them
            features = self.detector.extract_features(msg, self.spf_threshold.get(), self.dkim_threshold.get(), self.dmarc_threshold.get())
            if features:
                feature_text.config(state=tk.NORMAL)
                for feat, value in features.items():
                    feature_text.insert(tk.END, f"- {feat}: {value:.4f}\n")
                feature_text.config(state=tk.DISABLED)
            else:
                feature_text.config(state=tk.NORMAL)
                feature_text.insert(tk.END, "Feature extraction failed for this email.\n")
                feature_text.config(state=tk.DISABLED)

            # Authentication Results display
            auth_results_frame = ttk.LabelFrame(popup, text="Authentication Results", bootstyle="secondary")
            auth_results_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
            auth_results_text = scrolledtext.ScrolledText(auth_results_frame, height=8, state=tk.DISABLED, font=('TkDefaultFont', 9))
            auth_results_text.pack(fill=tk.BOTH, expand=True)

            auth_results = self.detector.check_email_authentication(msg, self.spf_threshold.get(), self.dkim_threshold.get(), self.dmarc_threshold.get())
            if auth_results:
                auth_results_text.config(state=tk.NORMAL)
                for key, value in auth_results.items():
                    auth_results_text.insert(tk.END, f"- {key}: {value}\n")
                auth_results_text.config(state=tk.DISABLED)
            else:
                auth_results_text.config(state=tk.NORMAL)
                auth_results_text.insert(tk.END, "Authentication check failed for this email.\n")
                auth_results_text.config(state=tk.DISABLED)


            popup.wait_window() # Wait for popup to close before returning control
            logger.info(f"Opened email details popup for: {email_data['subject']}")
        except Exception as e:
            logger.error(f"Failed to open email popup: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to open email: {str(e)}")

    def browse_dataset(self):
        """
        Opens a file dialog to allow the user to select a training dataset file (CSV or Excel).
        Updates the dataset path variable.
        """
        try:
            filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("Excel files", "*.xlsx")])
            if filename:
                self.dataset_path.set(filename)
                logger.info(f"Selected dataset: {filename}")
        except Exception as e:
            logger.error(f"Failed to browse dataset: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to browse dataset: {str(e)}")

    def load_model_and_lists(self):
        """
        Loads the pre-trained machine learning model and the blacklist/whitelist
        from disk on application startup. Updates GUI status accordingly.
        """
        model_loaded = self.detector.load_model()
        if model_loaded:
            self.model = self.detector.model # Update GUI's reference to the model
            self.show_status("Status: Pre-trained model loaded successfully.")
            self.update_performance_tab() # Display loaded model's performance
        else:
            self.show_status("Status: No pre-trained model found. Please train a model.")
            # If no model, set default dataset path if it exists
            default_path = os.path.join(self.dataset_dir, self.default_dataset_file)
            if os.path.exists(default_path):
                self.dataset_path.set(default_path)
        self.load_lists() # Load blacklist/whitelist from DB

    def get_selected_features_for_training(self) -> list:
        """
        Constructs a list of features to be used for model training based on
        the user's selections in the "Feature Selection" checkboxes.
        Ensures only valid features from the detector's comprehensive list are included.
        :return: A list of selected feature names.
        """
        selected_features = []
        all_possible_features = self.detector.get_all_possible_features()

        if self.feature_options["Header Analysis"].get():
            selected_features.extend([
                'header_count', 'subject_length', 'num_recipients', 'time_sent',
                'from_return_path_mismatch', 'reply_to_inconsistency',
                'num_received_headers', 'unusual_header_order', 'missing_headers',
                'subject_entropy'
            ])
        if self.feature_options["Content Analysis"].get():
            selected_features.extend([
                'body_length', 'has_attachments', 'is_marketing', 'suspicious_keywords',
                'urgency_keywords', 'num_links', 'num_images', 'html_content_ratio',
                'hidden_content', 'url_redirects'
            ])
        if self.feature_options["SPF/DKIM/DMARC"].get():
            selected_features.extend([
                'spf_pass', 'dkim_pass', 'dmarc_pass', 'spf_alignment', 'dkim_alignment',
                'authentication_results_mismatch'
            ])
        if self.feature_options["ARC Validation"].get():
            selected_features.append('arc_seal_valid')
        if self.feature_options["Metadata Analysis"].get():
            selected_features.extend([
                'domain_reputation', 'ip_blacklisted', 'sender_ip_blacklisted',
                'is_known_domain', 'suspicious_tld', 'registry_creation_date_suspicious',
                'blacklisted_domain'
            ])

        # Filter out duplicates and ensure they are in the master list of possible features
        final_features = [f for f in list(set(selected_features)) if f in all_possible_features]
        return final_features

    def train_model(self):
        """
        Initiates the model training process in a separate thread to keep the GUI responsive.
        Performs initial validation checks before starting the training thread.
        """
        dataset_path = self.dataset_path.get()
        if not dataset_path or not os.path.exists(dataset_path):
            messagebox.showerror("Error", "No valid dataset selected or file does not exist.")
            return

        if self.training_thread and self.training_thread.is_alive():
            messagebox.showwarning("Warning", "Model training is already in progress. Please wait.")
            return

        selected_features = self.get_selected_features_for_training()
        if not selected_features:
            messagebox.showerror("Error", "No features selected for training. Please select at least one feature category.")
            return

        # Define a simple progress update function for the thread
        # This function will be called by the training thread to update GUI elements
        def update_progress(value: float, message: str):
            self.training_progress_var.set(value)
            self.training_status_text.set(message)
            self.root.update_idletasks() # Force GUI update

        # Pass root.after to the callback for thread-safe GUI updates
        # This is crucial for GridSearchCVProgressCallback to update the GUI
        grid_search_root_after = self.root.after

        # Start the training process in a new thread
        self.training_thread = threading.Thread(
            target=self._train_model_thread_wrapper,
            args=(dataset_path, selected_features, update_progress, grid_search_root_after),
            daemon=True # Daemon thread exits when main program exits
        )
        self.training_thread.start()
        logger.info("Model training started in a new thread.")

    def _train_model_thread_wrapper(self, dataset_path: str, selected_features: list, update_progress_gui, root_after_method):
        """
        Wrapper function for the core training logic. This function is executed
        in a separate thread and handles calling the detector's training method
        and updating the GUI upon completion or failure.
        :param dataset_path: Path to the training dataset.
        :param selected_features: List of features for training.
        :param update_progress_gui: Callback function to update GUI progress.
        :param root_after_method: The `root.after` method for thread-safe GUI updates.
        """
        try:
            # Create a local callback object that wraps the GUI update function
            # and provides the necessary Tkinter variables/methods to GridSearchCVProgressCallback.
            class LocalProgressCallback:
                def __init__(self, update_gui_func, progress_var_ref, root_after_ref):
                    self.update_gui_func = update_gui_func
                    self.progress_var = progress_var_ref
                    self.root_after_method = root_after_ref

                def __call__(self, value, message):
                    self.update_gui_func(value, message)

            local_progress_callback = LocalProgressCallback(update_progress_gui, self.training_progress_var, root_after_method)

            # Call the core training method from the detector
            metrics = self.detector.train_model_core(dataset_path, selected_features, local_progress_callback)
            self.model = self.detector.model # Update GUI's reference to the trained model
            # Schedule GUI update on the main thread after training completes
            self.root.after(0, lambda: self._training_complete_gui(metrics))
        except Exception as e:
            # Schedule GUI update on the main thread if training fails
            self.root.after(0, lambda: self._training_failed_gui(str(e)))

    def _training_complete_gui(self, metrics: dict):
        """
        Updates the GUI after a successful model training.
        :param metrics: Dictionary of performance metrics from the training.
        """
        self.training_progress_var.set(100)
        status_text = (
            f"Status: Training complete!\n"
            f"Accuracy: {metrics['accuracy']:.2f}\n"
            f"F1-Score: {metrics['f1_score']:.2f}"
        )
        self.training_status_text.set(status_text)
        self.update_performance_tab() # Refresh performance metrics tab
        messagebox.showinfo("Success", "Model trained successfully!")
        logger.info("Model training completed successfully.")

    def _training_failed_gui(self, error_message: str):
        """
        Updates the GUI after a model training failure.
        :param error_message: The error message to display.
        """
        self.training_progress_var.set(0)
        self.training_status_text.set(f"Status: Training failed: {error_message}")
        messagebox.showerror("Error", f"Training failed: {error_message}\nCheck 'spoofhawk.log' for details.")
        logger.error(f"Training failed: {error_message}")

    def fetch_emails(self):
        """
        Initiates fetching emails from the IMAP server in a separate thread.
        Performs validation of IMAP credentials.
        """
        imap_server = self.imap_server.get().strip()
        username = self.username.get().strip()
        password = self.password.get().strip()

        if not imap_server or not username or not password:
            messagebox.showerror("Error", "Please provide IMAP server, username, and password.")
            return

        if self.fetch_thread and self.fetch_thread.is_alive():
            messagebox.showwarning("Warning", "Email fetching is already in progress. Please wait.")
            return

        self.fetch_thread = threading.Thread(target=self._fetch_emails_thread, args=(imap_server, username, password), daemon=True)
        self.fetch_thread.start()
        logger.info("Email fetching started in a new thread.")

    def _fetch_emails_thread(self, imap_server: str, username: str, password: str):
        """
        Internal method for fetching emails from the IMAP server.
        This method runs in a separate thread.
        Fetches a specified number of the latest emails from the INBOX.
        :param imap_server: IMAP server address.
        :param username: IMAP username.
        :param password: IMAP password/app password.
        """
        try:
            self.show_status("Status: Connecting to IMAP server...")
            context = ssl.create_default_context()
            mail = imaplib.IMAP4_SSL(imap_server, ssl_context=context)
            mail.login(username, password)
            mail.select("INBOX")
            self.mail_connection = mail # Store connection for potential reuse/disconnection

            self.show_status("Status: Searching for emails...")
            status, messages = mail.search(None, "ALL") # Search all emails
            if status != "OK":
                raise Exception(f"Failed to search emails: {messages[0].decode()}")

            email_ids = messages[0].split()
            num_emails_to_fetch = min(int(self.email_count.get()), len(email_ids))
            # Fetch the latest emails
            latest_email_ids = email_ids[-num_emails_to_fetch:] if num_emails_to_fetch > 0 else []

            self.root.after(0, lambda: self.email_listbox.delete(0, tk.END)) # Clear listbox
            self.emails = [] # Store fetched email data

            self.show_status(f"Status: Fetching {len(latest_email_ids)} emails...")
            for i, email_id in enumerate(latest_email_ids):
                if not self.fetch_thread.is_alive(): # Allow thread to be stopped
                    break
                status, msg_data = mail.fetch(email_id, "(RFC822)") # Fetch full email content
                if status != "OK":
                    logger.warning(f"Failed to fetch email ID: {email_id}. Skipping.")
                    continue

                raw_email = msg_data[0][1]
                email_message = email.message_from_bytes(raw_email)

                subject = self.detector._decode_header(email_message.get("Subject", "No Subject"))
                from_ = email_message.get("From", "Unknown Sender")
                date = email_message.get("Date", "Unknown Date")

                email_data = {
                    'id': email_id.decode('utf-8'),
                    'message': email_message,
                    'subject': subject,
                    'from': from_,
                    'date': date,
                    'raw': raw_email # Store raw email for hashing
                }
                self.emails.append(email_data)

                # Update listbox on the main thread
                self.root.after(0, lambda from_addr=from_, subj=subject, dt=date: self.email_listbox.insert(tk.END, f"{dt} | From: {from_addr} | Subject: {subj[:50]}..."))
                self.root.after(0, lambda: self.email_listbox.see(tk.END)) # Scroll to end

            mail.logout()
            self.show_status(f"Status: Fetched {len(self.emails)} emails successfully.")
            self.root.after(0, lambda: messagebox.showinfo("Success", f"Fetched {len(self.emails)} emails."))
            logger.info(f"Fetched {len(self.emails)} emails from {imap_server}.")
        except Exception as e:
            self.show_status("Status: Email fetching failed.")
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to fetch emails: {str(e)}"))
            logger.error(f"Failed to fetch emails: {str(e)}", exc_info=True)
        finally:
            self.mail_connection = None # Clear connection after use

    def analyze_all_emails(self):
        """
        Initiates the analysis of all fetched emails using the trained model
        and blacklist/whitelist rules. Runs in a separate thread.
        """
        if not hasattr(self, 'emails') or not self.emails:
            messagebox.showwarning("Warning", "No emails fetched yet to analyze!")
            return

        if self.detector.model is None:
            messagebox.showerror("Error", "No trained model found. Please train a model first.")
            return

        if self.analysis_thread and self.analysis_thread.is_alive():
            messagebox.showwarning("Warning", "Email analysis is already in progress. Please wait.")
            return

        self.analysis_thread = threading.Thread(target=self._analyze_all_emails_thread, daemon=True)
        self.analysis_thread.start()
        logger.info("Email analysis started in a new thread.")

    def _analyze_all_emails_thread(self):
        """
        Internal method for analyzing emails. This method runs in a separate thread.
        It applies blacklist/whitelist rules and then uses the ML model for detection.
        """
        try:
            # Prepare result text area on main thread
            self.root.after(0, lambda: self.result_text.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.result_text.delete(1.0, tk.END))
            self.root.after(0, lambda: self.result_text.insert(tk.END, "=== SPOOFHAWK ANALYSIS RESULTS ===\n\n"))
            self.email_stats = defaultdict(int) # Reset stats for new analysis

            expected_features = self.detector.performance_metrics.get('feature_columns', [])
            if not expected_features:
                self.root.after(0, lambda: self.result_text.insert(tk.END, "Error: Model features not defined. Please train the model first.\n"))
                self.root.after(0, lambda: self.result_text.config(state=tk.DISABLED))
                logger.error("Analysis failed: Model features not defined.")
                return

            self.show_status(f"Status: Analyzing {len(self.emails)} emails...")
            for i, email_data in enumerate(self.emails):
                if not self.analysis_thread.is_alive(): # Allow thread to be stopped
                    break

                email_hash = hashlib.sha256(email_data['raw']).hexdigest()
                from_address_lower = email_data['from'].lower()
                subject_lower = email_data['subject'].lower()

                result_message = ""
                # Check against whitelist patterns first (higher priority)
                is_whitelisted_by_pattern = any(re.search(re.escape(pattern), from_address_lower) or re.search(re.escape(pattern), subject_lower) for pattern in self.whitelist_patterns)
                # Check against blacklist patterns
                is_blacklisted_by_pattern = any(re.search(re.escape(pattern), from_address_lower) or re.search(re.escape(pattern), subject_lower) for pattern in self.blacklist_patterns)

                if is_whitelisted_by_pattern:
                    result_message = f"WHITELISTED (Pattern Match)"
                    self.email_stats['whitelisted'] += 1
                elif is_blacklisted_by_pattern:
                    result_message = f"BLACKLISTED (Pattern Match)"
                    self.email_stats['blacklisted'] += 1
                elif email_hash in self.blacklist:
                    result_message = f"BLACKLISTED (Hash Match)"
                    self.email_stats['blacklisted'] += 1
                elif email_hash in self.whitelist:
                    result_message = f"WHITELISTED (Hash Match)"
                    self.email_stats['whitelisted'] += 1
                else:
                    # If not in lists, use ML model
                    features = self.detector.extract_features(email_data['message'], self.spf_threshold.get(), self.dkim_threshold.get(), self.dmarc_threshold.get())
                    if not features:
                        result_message = f"Failed to extract features for: {email_data['subject']}"
                        logger.warning(f"Feature extraction failed for email: {email_data['subject']}")
                    else:
                        feature_values_df = pd.DataFrame([features])
                        prediction, proba = self.detector.predict(feature_values_df)

                        if prediction == 1:
                            self.email_stats['spoofed'] += 1
                            result_message = f"⚠️ SUSPICIOUS EMAIL DETECTED ⚠️ (Spoof Probability: {proba:.2%})"
                        else:
                            self.email_stats['legitimate'] += 1
                            result_message = f"✅ LEGITIMATE EMAIL ✅ (Legit Probability: {1-proba:.2%})"

                        # Add detailed authentication results
                        result_message += "\n\nAuthentication Results:\n"
                        auth_results = self.detector.check_email_authentication(email_data['message'], self.spf_threshold.get(), self.dkim_threshold.get(), self.dmarc_threshold.get())
                        if auth_results:
                            for key, value in auth_results.items():
                                result_message += f"- {key}: {value}\n"
                        else:
                            result_message += "- Authentication check failed.\n"

                        # Highlight suspicious feature outliers
                        suspicious_features_detected = []
                        for feat, value in features.items():
                            stats = self.detector.feature_stats.get(feat)
                            # Check if feature value is significantly outside the training data's mean +/- 3*std
                            if stats and (value > stats['mean'] + 3*stats['std'] or value < stats['mean'] - 3*stats['std']):
                                suspicious_features_detected.append(feat)

                        if suspicious_features_detected:
                            result_message += f"\nSuspicious Feature Outliers: {', '.join(suspicious_features_detected)}\n"

                        # Display key features
                        result_message += "\nFeature Details (Selected):\n"
                        key_features_to_display = [
                            'subject_length', 'body_length', 'num_links', 'suspicious_keywords',
                            'domain_reputation', 'from_return_path_mismatch', 'reply_to_inconsistency',
                            'sender_ip_blacklisted', 'suspicious_tld', 'hidden_content', 'url_redirects',
                            'spf_pass', 'dkim_pass', 'dmarc_pass', 'arc_seal_valid',
                            'spf_alignment', 'dkim_alignment', 'authentication_results_mismatch'
                        ]
                        for feat in key_features_to_display:
                            if feat in features:
                                result_message += f"- {feat}: {features[feat]:.4f}\n"

                # Update result text area on main thread
                self.root.after(0, lambda msg=result_message, subj=email_data['subject'], frm=email_data['from'], dt=email_data['date']:
                                self.result_text.insert(tk.END, f"Email: {subj}\nFrom: {frm}\nDate: {dt}\n{msg}\n{'-'*50}\n"))
                self.root.after(0, lambda: self.result_text.see(tk.END))

            self.root.after(0, lambda: self.result_text.config(state=tk.DISABLED))
            self.root.after(0, self.update_stats_display) # Update statistics
            self.show_status("Status: Email analysis complete.")
            logger.info(f"Analyzed {len(self.emails)} emails.")
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {str(e)}"))
            self.root.after(0, lambda: self.result_text.config(state=tk.DISABLED))
            self.show_status("Status: Email analysis failed.")
            logger.error(f"Email analysis failed: {str(e)}", exc_info=True)

    def connect_imap(self) -> bool:
        """
        Establishes an IMAP connection using the provided credentials.
        :return: True if connection is successful, False otherwise.
        """
        imap_server = self.imap_server.get().strip()
        username = self.username.get().strip()
        password = self.password.get().strip()

        if not imap_server or not username or not password:
            self.update_monitor_text("Error: IMAP server, username, or password not provided.")
            return False

        try:
            context = ssl.create_default_context()
            mail = imaplib.IMAP4_SSL(imap_server, ssl_context=context)
            mail.login(username, password)
            mail.select("INBOX")
            self.mail_connection = mail
            logger.info(f"Successfully connected to IMAP server: {imap_server}")
            return True
        except imaplib.IMAP4.error as e:
            logger.error(f"IMAP connection failed: {e}", exc_info=True)
            self.update_monitor_text(f"IMAP connection failed: {str(e)}. Check credentials and server.")
            self.disconnect_imap() # Ensure connection is closed on failure
            return False
        except Exception as e:
            logger.error(f"Unexpected error during IMAP connection: {e}", exc_info=True)
            self.update_monitor_text(f"Unexpected IMAP connection error: {str(e)}")
            self.disconnect_imap()
            return False

    def disconnect_imap(self):
        """
        Disconnects from the IMAP server if a connection is active.
        """
        if self.mail_connection:
            try:
                self.mail_connection.logout()
                logger.info("IMAP connection logged out.")
            except Exception as e:
                logger.warning(f"Error during IMAP logout: {e}", exc_info=True)
            finally:
                self.mail_connection = None

    def toggle_monitoring(self):
        """
        Toggles the real-time email monitoring on or off.
        Handles starting and stopping the monitoring thread and IMAP connection.
        """
        try:
            if self.monitoring_active:
                # Stop monitoring
                self.monitoring_active = False
                self.monitor_button.config(text="Start Monitoring", bootstyle="success")
                self.status_label.config(text="Monitoring: OFF")
                self.processed_email_hashes.clear() # Clear processed hashes on stop
                self.disconnect_imap()
                logger.info("Monitoring stopped.")
                self.update_monitor_text("Monitoring stopped.")
            else:
                # Start monitoring
                if not self.imap_server.get() or not self.username.get() or not self.password.get():
                    messagebox.showerror("Error", "Please enter email credentials for monitoring.")
                    return
                if self.detector.model is None:
                    messagebox.showerror("Error", "No trained model found. Please train a model first.")
                    return

                # Attempt initial connection before starting thread
                if not self.connect_imap():
                    messagebox.showerror("Error", "Failed to establish initial IMAP connection. Monitoring cannot start.")
                    return

                self.monitoring_active = True
                self.monitor_button.config(text="Stop Monitoring", bootstyle="danger")
                self.status_label.config(text="Monitoring: ON")

                self.monitoring_thread = threading.Thread(target=self._monitor_emails_thread, daemon=True)
                self.monitoring_thread.start()
                logger.info("Monitoring started.")
                self.update_monitor_text("Monitoring started.")
        except Exception as e:
            messagebox.showerror("Error", f"Monitoring toggle failed: {str(e)}")
            logger.error(f"Monitoring toggle failed: {str(e)}", exc_info=True)

    def _monitor_emails_thread(self):
        """
        Internal method for real-time email monitoring. This method runs in a separate thread.
        It periodically checks for new unseen emails, analyzes them, and takes actions
        like quarantining or notifying based on detection results.
        """
        self.last_checked = datetime.now()
        max_emails_per_cycle = 50 # Limit emails processed per cycle to prevent overload

        while self.monitoring_active:
            try:
                # Reconnect if connection is lost
                if not self.mail_connection:
                    self.update_monitor_text("Attempting to reconnect to IMAP...")
                    for i in range(3): # Retry reconnection
                        if self.connect_imap():
                            self.update_monitor_text("Reconnected to IMAP.")
                            break
                        else:
                            wait_time = 2 ** i * 5 # Exponential backoff
                            self.update_monitor_text(f"Reconnection failed. Retrying in {wait_time} seconds.")
                            time.sleep(wait_time)
                    if not self.mail_connection:
                        self.update_monitor_text("Failed to reconnect after multiple attempts. Monitoring paused.")
                        self.root.after(0, self.toggle_monitoring) # Stop monitoring via GUI
                        return

                now = datetime.now()
                check_interval_seconds = float(self.interval.get()) * 60

                # Check for new emails only after the specified interval
                if (now - self.last_checked).total_seconds() >= check_interval_seconds:
                    self.update_monitor_text(f"Checking emails at {now.strftime('%Y-%m-%d %H:%M:%S')}...")

                    try:
                        self.mail_connection.noop() # Keep connection alive
                        status, messages = self.mail_connection.search(None, "UNSEEN") # Search for unseen emails
                    except imaplib.IMAP4.error as imap_err:
                        self.update_monitor_text(f"IMAP connection error during search: {imap_err}. Reconnecting...")
                        logger.error(f"IMAP connection error during search: {imap_err}", exc_info=True)
                        self.disconnect_imap() # Force disconnect to trigger reconnect logic
                        continue

                    if status != "OK":
                        self.update_monitor_text(f"Error searching emails: {messages[0].decode()}. Reconnecting...")
                        logger.error(f"Error searching emails: {messages[0].decode()}")
                        self.disconnect_imap()
                        continue

                    email_ids = messages[0].split()
                    if not email_ids:
                        self.update_monitor_text("No new unseen emails.")
                        self.last_checked = now # Reset last checked time even if no new emails
                        time.sleep(check_interval_seconds) # Sleep for full interval
                        continue

                    # Process only the latest `max_emails_per_cycle` emails
                    emails_to_process = email_ids[-max_emails_per_cycle:]
                    self.update_monitor_text(f"Found {len(emails_to_process)} new email(s) to process.")

                    for email_id in emails_to_process:
                        if not self.monitoring_active: # Check flag again in loop
                            break

                        status, msg_data = self.mail_connection.fetch(email_id, "(RFC822)")
                        if status != "OK":
                            logger.warning(f"Failed to fetch full email ID: {email_id}. Skipping.")
                            continue

                        raw_email = msg_data[0][1]
                        email_hash = hashlib.sha256(raw_email).hexdigest()

                        # Skip if already processed in this monitoring session
                        if email_hash in self.processed_email_hashes:
                            self.mail_connection.store(email_id, '+FLAGS', '\\Seen') # Mark as seen
                            continue
                        self.processed_email_hashes.add(email_hash)

                        email_message = email.message_from_bytes(raw_email)

                        subject = self.detector._decode_header(email_message.get("Subject", "No Subject"))
                        from_address = email_message.get("From", "Unknown Sender")
                        from_address_lower = from_address.lower()
                        subject_lower = subject.lower()

                        # Apply blacklist/whitelist rules
                        is_whitelisted_by_pattern = any(re.search(re.escape(pattern), from_address_lower) or re.search(re.escape(pattern), subject_lower) for pattern in self.whitelist_patterns)
                        is_blacklisted_by_pattern = any(re.search(re.escape(pattern), from_address_lower) or re.search(re.escape(pattern), subject_lower) for pattern in self.blacklist_patterns)

                        if is_whitelisted_by_pattern:
                            self.update_monitor_text(f"WHITELISTED (Pattern): From: {from_address} | {subject[:50]}...")
                            self.email_stats['whitelisted'] += 1
                        elif is_blacklisted_by_pattern:
                            self.update_monitor_text(f"BLACKLISTED (Pattern): From: {from_address} | {subject[:50]}...")
                            self.email_stats['blacklisted'] += 1
                            if self.auto_quarantine.get():
                                self._quarantine_email(email_id, "Pattern Match")
                        elif email_hash in self.blacklist:
                            self.update_monitor_text(f"BLACKLISTED (Hash): From: {from_address} | {subject[:50]}...")
                            self.email_stats['blacklisted'] += 1
                        elif email_hash in self.whitelist:
                            self.update_monitor_text(f"WHITELISTED (Hash): From: {from_address} | {subject[:50]}...")
                            self.email_stats['whitelisted'] += 1
                        else:
                            # Use ML model for detection
                            features = self.detector.extract_features(email_message, self.spf_threshold.get(), self.dkim_threshold.get(), self.dmarc_threshold.get())
                            if features and self.detector.model:
                                feature_values_df = pd.DataFrame([features])
                                prediction, proba = self.detector.predict(feature_values_df)

                                if prediction == 1:
                                    self.email_stats['spoofed'] += 1
                                    self.update_monitor_text(f"⚠️ SUSPICIOUS: From: {from_address} | {subject[:50]}... (Prob: {proba:.2%})")
                                    if self.auto_quarantine.get():
                                        self._quarantine_email(email_id, "ML Model")
                                    if self.notify_admin.get():
                                        self.notify_administrator(email_message, proba)
                                else:
                                    self.email_stats['legitimate'] += 1
                                    self.update_monitor_text(f"✅ Legitimate: From: {from_address} | {subject[:50]}... (Prob: {1-proba:.2%})")
                            else:
                                self.update_monitor_text(f"Skipped analysis for From: {from_address} | {subject[:50]}... (feature extraction failed or model not loaded)")
                                logger.warning(f"Monitoring skipped email: {subject[:50]}... (features/model issue)")

                        self.mail_connection.store(email_id, '+FLAGS', '\\Seen') # Mark email as seen after processing

                    self.last_checked = now # Update last checked time after processing cycle
                    self.root.after(0, self.update_stats_display) # Update stats on GUI

                # Sleep for the remaining time of the interval
                remaining_sleep_time = check_interval_seconds - (datetime.now() - self.last_checked).total_seconds()
                if remaining_sleep_time > 0:
                    time.sleep(remaining_sleep_time)
                else:
                    time.sleep(1) # Avoid busy-waiting if processing took longer than interval

            except imaplib.IMAP4.error as imap_err:
                self.update_monitor_text(f"IMAP error during monitoring: {imap_err}. Attempting to reconnect.")
                logger.error(f"IMAP error during monitoring: {imap_err}", exc_info=True)
                self.disconnect_imap()
                time.sleep(10) # Wait before attempting reconnect
            except Exception as e:
                self.update_monitor_text(f"Monitoring error: {str(e)}")
                logger.error(f"Monitoring error: {str(e)}", exc_info=True)
                self.disconnect_imap()
                time.sleep(30) # Longer wait for general errors

    def _quarantine_email(self, email_id: bytes, reason: str = ""):
        """
        Moves a detected suspicious email to a 'Quarantine' IMAP folder
        and marks it for deletion from the INBOX.
        :param email_id: The IMAP email ID (bytes).
        :param reason: The reason for quarantining (e.g., "ML Model", "Pattern Match").
        """
        try:
            # Check if Quarantine folder exists, create if not
            status, mailboxes = self.mail_connection.list("", "INBOX.Quarantine")
            # mailboxes[0] will be empty if folder does not exist
            if status != 'OK' or not mailboxes[0]:
                self.mail_connection.create("INBOX.Quarantine")
                logger.info("Created INBOX.Quarantine folder.")

            self.mail_connection.copy(email_id, "INBOX.Quarantine") # Copy to Quarantine
            self.mail_connection.store(email_id, '+FLAGS', '\\Deleted') # Mark for deletion
            self.mail_connection.expunge() # Permanently delete marked emails
            self.update_monitor_text(f"Email quarantined (Reason: {reason}).")
            logger.info(f"Email ID {email_id.decode()} quarantined. Reason: {reason}")
        except Exception as e:
            self.update_monitor_text(f"Quarantine error: {str(e)}")
            logger.error(f"Quarantine error for email ID {email_id.decode()}: {e}", exc_info=True)

    def notify_administrator(self, email_msg: email.message.Message, confidence: float):
        """
        Simulates sending an alert notification to an administrator about a suspicious email.
        In a real-world scenario, this would involve sending an actual email or API call.
        :param email_msg: The suspicious email message object.
        :param confidence: The spoof probability from the model.
        """
        try:
            subject = self.detector._decode_header(email_msg.get("Subject", "No Subject"))
            from_ = email_msg.get("From", "Unknown Sender")
            date = email_msg.get("Date", "Unknown Date")

            notification = (
                f"Subject: SpoofHawk Security Alert: Suspicious Email Detected\n"
                f"From: SpoofHawk <noreply@spoofhawk.local>\n"
                f"To: Admin <admin@example.com>\n\n" # Placeholder admin email
                f"A suspicious email has been detected by SpoofHawk with a spoof probability of {confidence:.2%}:\n\n"
                f"Subject: {subject}\n"
                f"From: {from_}\n"
                f"Date: {date}\n"
                f"Action Taken: {'Quarantined' if self.auto_quarantine.get() else 'Flagged'}\n\n"
                f"Please review this email in the 'INBOX.Quarantine' folder if auto-quarantine is enabled."
            )

            self.update_monitor_text("📧 Alert sent to admin (simulated).")
            logger.info(f"Admin alert simulated for: {subject}")
            logger.debug(f"Admin notification content:\n{notification}")
        except Exception as e:
            logger.error(f"Admin notification error: {str(e)}", exc_info=True)

    def update_monitor_text(self, message: str):
        """
        Updates the monitoring log text area in a thread-safe manner.
        :param message: The message to append to the log.
        """
        self.root.after(0, lambda: self._update_monitor_text_gui(message))

    def _update_monitor_text_gui(self, message: str):
        """
        Actual GUI update for the monitoring log.
        """
        try:
            self.monitor_text.config(state=tk.NORMAL)
            self.monitor_text.insert(tk.END, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
            self.monitor_text.see(tk.END) # Scroll to the end
            self.monitor_text.config(state=tk.DISABLED)
        except Exception as e:
            logger.error(f"Monitor text GUI update failed: {str(e)}", exc_info=True)

    def update_performance_tab(self):
        """
        Updates the "Performance Metrics" tab with the latest model performance
        metrics and a confusion matrix visualization.
        """
        try:
            self.metrics_text.config(state=tk.NORMAL)
            self.metrics_text.delete(1.0, tk.END)

            performance_metrics = self.detector.performance_metrics
            if not performance_metrics:
                self.metrics_text.insert(tk.END, "No performance metrics available. Train the model first.\n")
                self.metrics_text.config(state=tk.DISABLED)
                return

            self.metrics_text.insert(tk.END, "=== MODEL PERFORMANCE METRICS ===\n\n")
            self.metrics_text.insert(tk.END, f"Accuracy: {performance_metrics.get('accuracy', 0):.4f}\n")
            self.metrics_text.insert(tk.END, f"Precision: {performance_metrics.get('precision', 0):.4f}\n")
            self.metrics_text.insert(tk.END, f"Recall: {performance_metrics.get('recall', 0):.4f}\n")
            self.metrics_text.insert(tk.END, f"F1-Score: {performance_metrics.get('f1_score', 0):.4f}\n\n")
            self.metrics_text.insert(tk.END, "=== CLASSIFICATION REPORT ===\n")
            report_dict = performance_metrics.get('classification_report', {})
            report_str = ""
            if report_dict:
                for label, metrics in report_dict.items():
                    if isinstance(metrics, dict):
                        report_str += f"{label}:\n"
                        for metric_name, value in metrics.items():
                            if isinstance(value, float):
                                report_str += f"  {metric_name}: {value:.2f}\n"
                            else:
                                report_str += f"  {metric_name}: {value}\n"
                    else:
                        report_str += f"{label}: {metrics:.2f}\n"
            self.metrics_text.insert(tk.END, report_str if report_str else 'N/A')
            self.metrics_text.config(state=tk.DISABLED)

            # Plot Confusion Matrix
            self.ax.clear()
            cm = np.array(performance_metrics.get('confusion_matrix', [[0,0],[0,0]]))
            self.ax.matshow(cm, cmap='Blues')
            self.ax.set_xlabel('Predicted Label')
            self.ax.set_ylabel('True Label')
            self.ax.set_title('Confusion Matrix')
            self.ax.set_xticks([0, 1])
            self.ax.set_yticks([0, 1])
            self.ax.set_xticklabels(['Legitimate', 'Spoofed'])
            self.ax.set_yticklabels(['Legitimate', 'Spoofed'])
            # Add text annotations for confusion matrix values
            for (i, j), val in np.ndenumerate(cm):
                self.ax.text(j, i, f'{val}', ha='center', va='center', color='black', fontsize=12)
            self.figure.tight_layout()
            self.canvas.draw() # Redraw the canvas
            logger.info("Performance tab updated.")
        except Exception as e:
            logger.error(f"Failed to update performance tab: {str(e)}", exc_info=True)
            messagebox.showerror("Error", f"Failed to update performance tab: {str(e)}")

    def update_stats_display(self):
        """
        Updates the "Email Analysis Statistics" display with counts of
        legitimate, suspicious, blacklisted, and whitelisted emails.
        """
        try:
            self.stats_text.config(state=tk.NORMAL)
            self.stats_text.delete(1.0, tk.END)
            self.stats_text.insert(tk.END, "=== EMAIL ANALYSIS STATISTICS ===\n\n")
            total = sum(self.email_stats.values())
            self.stats_text.insert(tk.END, f"Total Emails Processed: {total}\n")
            self.stats_text.insert(tk.END, f"Legitimate Emails: {self.email_stats.get('legitimate', 0)}\n")
            self.stats_text.insert(tk.END, f"Suspicious Emails: {self.email_stats.get('spoofed', 0)}\n")
            self.stats_text.insert(tk.END, f"Blacklisted Emails: {self.email_stats.get('blacklisted', 0)}\n")
            self.stats_text.insert(tk.END, f"Whitelisted Emails: {self.email_stats.get('whitelisted', 0)}\n")
            if total > 0:
                spoofed_percentage = (self.email_stats.get('spoofed', 0) / total) * 100
                self.stats_text.insert(tk.END, f"\nSpoofed Percentage: {spoofed_percentage:.2f}%\n")
            self.stats_text.config(state=tk.DISABLED)
            logger.info("Email statistics display updated.")
        except Exception as e:
            logger.error(f"Failed to update stats display: {str(e)}", exc_info=True)

    def blacklist_selected_email(self):
        """
        Adds the SHA256 hash of the currently selected email to the blacklist.
        This prevents future analysis of this exact email.
        """
        try:
            selection = self.email_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "No email selected to blacklist.")
                return
            idx = selection[0]
            email_data = self.emails[idx]
            email_hash = hashlib.sha256(email_data['raw']).hexdigest()
            self.blacklist.add(email_hash)
            self.save_list_entry("blacklist", "email_hash", email_hash, False)
            messagebox.showinfo("Blacklist", "Email hash added to blacklist.")
            logger.info(f"Email hash {email_hash} blacklisted.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to blacklist email: {str(e)}")
            logger.error(f"Failed to blacklist email: {str(e)}", exc_info=True)

    def whitelist_selected_email(self):
        """
        Adds the SHA256 hash of the currently selected email to the whitelist.
        This ensures this exact email is always considered legitimate.
        """
        try:
            selection = self.email_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "No email selected to whitelist.")
                return
            idx = selection[0]
            email_data = self.emails[idx]
            email_hash = hashlib.sha256(email_data['raw']).hexdigest()
            self.whitelist.add(email_hash)
            self.save_list_entry("whitelist", "email_hash", email_hash, False)
            messagebox.showinfo("Whitelist", "Email hash added to whitelist.")
            logger.info(f"Email hash {email_hash} whitelisted.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to whitelist email: {str(e)}")
            logger.error(f"Failed to whitelist email: {str(e)}", exc_info=True)

    def remove_selected_list(self):
        """
        Removes the SHA256 hash of the currently selected email from both
        the blacklist and whitelist databases.
        """
        try:
            selection = self.email_listbox.curselection()
            if not selection:
                messagebox.showwarning("Warning", "No email selected to remove from lists.")
                return
            idx = selection[0]
            email_data = self.emails[idx]
            email_hash = hashlib.sha256(email_data['raw']).hexdigest()

            removed_from_blacklist = False
            removed_from_whitelist = False

            with sqlite3.connect(self.db_file) as conn:
                c = conn.cursor()
                c.execute("DELETE FROM blacklist WHERE value = ?", (email_hash,))
                if c.rowcount > 0:
                    removed_from_blacklist = True
                    if email_hash in self.blacklist:
                        self.blacklist.remove(email_hash)

                c.execute("DELETE FROM whitelist WHERE value = ?", (email_hash,))
                if c.rowcount > 0:
                    removed_from_whitelist = True
                    if email_hash in self.whitelist:
                        self.whitelist.remove(email_hash)
                conn.commit()

            if removed_from_blacklist and removed_from_whitelist:
                messagebox.showinfo("Info", "Email hash removed from both blacklist and whitelist.")
                logger.info(f"Email hash {email_hash} removed from both lists.")
            elif removed_from_blacklist:
                messagebox.showinfo("Info", "Email hash removed from blacklist.")
                logger.info(f"Email hash {email_hash} removed from blacklist.")
            elif removed_from_whitelist:
                messagebox.showinfo("Info", "Email hash removed from whitelist.")
                logger.info(f"Email hash {email_hash} removed from whitelist.")
            else:
                messagebox.showinfo("Info", "Email hash was not found in blacklist or whitelist.")
                logger.info(f"Email hash {email_hash} not found in lists for removal.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove from list: {str(e)}")
            logger.error(f"Failed to remove from list: {str(e)}", exc_info=True)

    def add_blacklist_pattern(self):
        """
        Adds a user-defined regex pattern to the blacklist.
        Patterns are used for broader matching (e.g., sender domain, subject keywords).
        """
        try:
            pattern = self.blacklist_pattern_entry.get().strip()
            if pattern:
                try:
                    re.compile(pattern) # Validate regex pattern
                except re.error:
                    messagebox.showerror("Error", "Invalid regex pattern. Please enter a valid regular expression.")
                    return

                if pattern in self.blacklist_patterns:
                    messagebox.showwarning("Warning", "Pattern already exists in blacklist.")
                    return

                self.blacklist_patterns.append(pattern)
                self.save_list_entry("blacklist", "pattern", pattern, True)
                self.blacklist_pattern_entry.delete(0, tk.END)
                messagebox.showinfo("Success", "Blacklist pattern added.")
                logger.info(f"Blacklist pattern '{pattern}' added.")
            else:
                messagebox.showwarning("Warning", "Pattern cannot be empty.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add blacklist pattern: {str(e)}")
            logger.error(f"Failed to add blacklist pattern: {str(e)}", exc_info=True)

    def add_whitelist_pattern(self):
        """
        Adds a user-defined regex pattern to the whitelist.
        Patterns are used for broader matching (e.g., sender domain, subject keywords).
        """
        try:
            pattern = self.whitelist_pattern_entry.get().strip()
            if pattern:
                try:
                    re.compile(pattern) # Validate regex pattern
                except re.error:
                    messagebox.showerror("Error", "Invalid regex pattern. Please enter a valid regular expression.")
                    return

                if pattern in self.whitelist_patterns:
                    messagebox.showwarning("Warning", "Pattern already exists in whitelist.")
                    return

                self.whitelist_patterns.append(pattern)
                self.save_list_entry("whitelist", "pattern", pattern, True)
                self.whitelist_pattern_entry.delete(0, tk.END)
                messagebox.showinfo("Success", "Whitelist pattern added.")
                logger.info(f"Whitelist pattern '{pattern}' added.")
            else:
                messagebox.showwarning("Warning", "Pattern cannot be empty.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add whitelist pattern: {str(e)}")
            logger.error(f"Failed to add whitelist pattern: {str(e)}", exc_info=True)

    def export_lists(self):
        """
        Exports the current blacklist and whitelist (hashes and patterns) to a JSON file.
        Allows the user to choose the save location.
        """
        try:
            data = {
                'blacklist_hashes': list(self.blacklist),
                'whitelist_hashes': list(self.whitelist),
                'blacklist_patterns': self.blacklist_patterns,
                'whitelist_patterns': self.whitelist_patterns
            }
            filename = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
            if filename:
                with open(filename, 'w') as f:
                    json.dump(data, f, indent=4)
                messagebox.showinfo("Success", f"Lists exported successfully to {os.path.basename(filename)}.")
                logger.info(f"Lists exported to {filename}.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export lists: {str(e)}")
            logger.error(f"Failed to export lists: {str(e)}", exc_info=True)

    def import_lists(self):
        """
        Imports blacklist and whitelist entries from a selected JSON file.
        Clears existing lists and populates them from the file, then updates the database.
        """
        try:
            filename = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
            if filename:
                with open(filename, 'r') as f:
                    data = json.load(f)

                # Clear current in-memory lists
                self.blacklist.clear()
                self.whitelist.clear()
                self.blacklist_patterns.clear()
                self.whitelist_patterns.clear()

                # Populate from imported data
                self.blacklist.update(data.get('blacklist_hashes', []))
                self.whitelist.update(data.get('whitelist_hashes', []))
                self.blacklist_patterns.extend(data.get('blacklist_patterns', []))
                self.whitelist_patterns.extend(data.get('whitelist_patterns', []))

                # Update database to reflect imported lists
                with sqlite3.connect(self.db_file) as conn:
                    c = conn.cursor()
                    c.execute("DELETE FROM blacklist") # Clear existing DB entries
                    c.execute("DELETE FROM whitelist")

                    # Insert imported entries into DB
                    for item in data.get('blacklist_hashes', []):
                        self.save_list_entry("blacklist", "email_hash", item, False)
                    for item in data.get('whitelist_hashes', []):
                        self.save_list_entry("whitelist", "email_hash", item, False)
                    for item in data.get('blacklist_patterns', []):
                        self.save_list_entry("blacklist", "pattern", item, True)
                    for item in data.get('whitelist_patterns', []):
                        self.save_list_entry("whitelist", "pattern", item, True)
                    conn.commit()

                messagebox.showinfo("Success", f"Lists imported successfully from {os.path.basename(filename)}.")
                logger.info(f"Lists imported from {filename}.")
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid JSON file format.")
            logger.error(f"Invalid JSON file format during import: {filename}", exc_info=True)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import lists: {str(e)}")
            logger.error(f"Failed to import lists: {str(e)}", exc_info=True)

# --- Main Execution ---
if __name__ == "__main__":
    try:
        # Create the main Tkinter window with a ttkbootstrap theme
        root = ttk.Window(themename="darkly")
        app = EmailSpoofDetectorApp(root)
        root.mainloop() # Start the Tkinter event loop
    except Exception as e:
        # Log critical errors that prevent the application from starting
        logger.critical(f"Application failed to start: {str(e)}", exc_info=True)
        print(f"CRITICAL ERROR: Application failed to start. Check spoofhawk.log for details: {str(e)}")
