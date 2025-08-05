#!/usr/bin/env python3
"""
LinkedIn Multi-Account Comment Bot

This program allows multiple LinkedIn accounts to comment on posts automatically.
It supports proxy rotation, account management, and result tracking.

Requirements:
- accounts.txt: Contains LinkedIn account credentials
- links.txt: Contains LinkedIn post URLs to comment on
- proxies.txt: Contains proxy configurations (optional)
- comments.txt: Contains random comments to use

Author: Manus AI Assistant
"""

import os
import sys
import time
import random
import logging
import tempfile
import shutil
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager


@dataclass
class Account:
    """Represents a LinkedIn account"""
    email: str
    password: str
    proxy: Optional[str] = None


@dataclass
class Proxy:
    """Represents a proxy configuration"""
    host: str
    port: str
    username: Optional[str] = None
    password: Optional[str] = None


@dataclass
class CommentResult:
    """Represents the result of a comment attempt"""
    account_email: str
    post_url: str
    comment_text: str
    success: bool
    error_message: Optional[str] = None
    timestamp: str = ""


class LinkedInCommenter:
    """Main class for LinkedIn commenting automation"""
    
    def __init__(self):
        self.setup_logging()
        self.accounts: List[Account] = []
        self.post_links: List[str] = []
        self.proxies: List[Proxy] = []
        self.comments: List[str] = []
        self.results: List[CommentResult] = []
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format=\'%(asctime)s - %(levelname)s - %(message)s\',
            handlers=[
                logging.FileHandler(\'linkedin_bot.log\'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def load_accounts(self, filename: str = \'accounts.txt\') -> bool:
        """Load LinkedIn accounts from file"""
        try:
            if not os.path.exists(filename):
                self.logger.error(f"Accounts file {filename} not found")
                return False
                
            with open(filename, \'r\', encoding=\'utf-8\') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith(\'#\'):
                        parts = line.split(\':\')
                        if len(parts) >= 2:
                            email = parts[0].strip()
                            password = parts[1].strip()
                            self.accounts.append(Account(email=email, password=password))
                        else:
                            self.logger.warning(f"Invalid account format on line {line_num}: {line}")
                            
            self.logger.info(f"Loaded {len(self.accounts)} accounts")
            return len(self.accounts) > 0
            
        except Exception as e:
            self.logger.error(f"Error loading accounts: {str(e)}")
            return False
            
    def load_post_links(self, filename: str = \'links.txt\') -> bool:
        """Load LinkedIn post URLs from file"""
        try:
            if not os.path.exists(filename):
                self.logger.error(f"Links file {filename} not found")
                return False
                
            with open(filename, \'r\', encoding=\'utf-8\') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith(\'#\'):
                        if \'linkedin.com\' in line:
                            self.post_links.append(line)
                        else:
                            self.logger.warning(f"Invalid LinkedIn URL: {line}")
                            
            self.logger.info(f"Loaded {len(self.post_links)} post links")
            return len(self.post_links) > 0
            
        except Exception as e:
            self.logger.error(f"Error loading post links: {str(e)}")
            return False
            
    def load_proxies(self, filename: str = \'proxies.txt\') -> bool:
        """Load proxy configurations from file"""
        try:
            if not os.path.exists(filename):
                self.logger.info(f"Proxies file {filename} not found, continuing without proxies")
                return True
                
            with open(filename, \'r\', encoding=\'utf-8\') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if line and not line.startswith(\'#\'):
                        parts = line.split(\':\')
                        if len(parts) >= 2:
                            host = parts[0].strip()
                            port = parts[1].strip()
                            username = parts[2].strip() if len(parts) > 2 else None
                            password = parts[3].strip() if len(parts) > 3 else None
                            self.proxies.append(Proxy(host=host, port=port, username=username, password=password))
                        else:
                            self.logger.warning(f"Invalid proxy format on line {line_num}: {line}")
                            
            self.logger.info(f"Loaded {len(self.proxies)} proxies")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading proxies: {str(e)}")
            return True  # Continue without proxies
            
    def load_comments(self, filename: str = \'comments.txt\') -> bool:
        """Load comment templates from file"""
        try:
            if not os.path.exists(filename):
                # Create default comments if file doesn\'t exist
                default_comments = [
                    "Great insights! Thanks for sharing.",
                    "Very informative post. I learned something new today.",
                    "Excellent points made here. Really appreciate the perspective.",
                    "This is exactly what I needed to read today. Thank you!",
                    "Fantastic content as always. Keep up the great work!",
                    "Really valuable information. Thanks for taking the time to share.",
                    "Love this perspective on the topic. Very well articulated.",
                    "This resonates with me completely. Great post!",
                    "Brilliant insights! This adds a lot of value to the discussion.",
                    "Thank you for sharing your expertise on this matter."
                ]
                
                with open(filename, \'w\', encoding=\'utf-8\') as f:
                    for comment in default_comments:
                        f.write(comment + \'\n\')
                        
                self.comments = default_comments
                self.logger.info(f"Created default comments file with {len(default_comments)} comments")
            else:
                with open(filename, \'r\', encoding=\'utf-8\') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith(\'#\'):
                            self.comments.append(line)
                            
                self.logger.info(f"Loaded {len(self.comments)} comments")
                
            return len(self.comments) > 0
            
        except Exception as e:
            self.logger.error(f"Error loading comments: {str(e)}")
            return False
            
    def create_driver(self, proxy: Optional[Proxy] = None) -> Optional[webdriver.Chrome]:
        """Create Chrome WebDriver with optional proxy"""
        user_data_dir = None
        try:
            user_data_dir = tempfile.mkdtemp()
            chrome_options = Options()
            chrome_options.add_argument(\'--no-sandbox\')
            chrome_options.add_argument(\'--disable-dev-shm-usage\')
            chrome_options.add_argument(\'--disable-blink-features=AutomationControlled\')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option(\'useAutomationExtension\', False)
            chrome_options.add_argument(\'--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36\')
            chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
            
            # Add proxy if provided
            if proxy:
                if proxy.username and proxy.password:
                    chrome_options.add_argument(f\'--proxy-server=http://{proxy.username}:{proxy.password}@{proxy.host}:{proxy.port}\')
                else:
                    chrome_options.add_argument(f\'--proxy-server=http://{proxy.host}:{proxy.port}\')
                    
            service = Service(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Execute script to hide automation
            driver.execute_script("Object.defineProperty(navigator, \'webdriver\', {get: () => undefined})")
            
            return driver
            
        except Exception as e:
            self.logger.error(f"Error creating driver: {str(e)}")
            return None
            
        finally:
            # Ensure the temporary directory is cleaned up even if driver creation fails
            if user_data_dir and os.path.exists(user_data_dir):
                shutil.rmtree(user_data_dir)
            
    def login_to_linkedin(self, driver: webdriver.Chrome, account: Account) -> bool:
        """Login to LinkedIn with given account"""
        try:
            self.logger.info(f"Logging in with account: {account.email}")
            
            # Navigate to LinkedIn login page
            driver.get(\'https://www.linkedin.com/login\')
            time.sleep(random.uniform(2, 4))
            
            # Find and fill email field
            email_field = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, \'username\'))
            )
            email_field.clear()
            email_field.send_keys(account.email)
            time.sleep(random.uniform(1, 2))
            
            # Find and fill password field
            password_field = driver.find_element(By.ID, \'password\')
            password_field.clear()
            password_field.send_keys(account.password)
            time.sleep(random.uniform(1, 2))
            
            # Click login button
            login_button = driver.find_element(By.XPATH, \'//button[@type="submit"]\')
            login_button.click()
            
            # Wait for login to complete
            time.sleep(random.uniform(3, 5))
            
            # Check if login was successful
            if \'feed\' in driver.current_url or \'mynetwork\' in driver.current_url:
                self.logger.info(f"Successfully logged in as {account.email}")
                return True
            else:
                self.logger.error(f"Login failed for {account.email}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error during login for {account.email}: {str(e)}")
            return False
            
    def comment_on_post(self, driver: webdriver.Chrome, post_url: str, comment_text: str) -> bool:
        """Comment on a LinkedIn post"""
        try:
            self.logger.info(f"Commenting on post: {post_url}")
            
            # Navigate to post
            driver.get(post_url)
            time.sleep(random.uniform(3, 5))
            
            # Scroll down to load comments section
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/2);")
            time.sleep(random.uniform(2, 3))
            
            # Find comment button/box
            comment_selectors = [
                \'//button[contains(@class, "comments-comment-box__cta")]\',
                \'//div[contains(@class, "comments-comment-texteditor")]\',
                \'//div[@role="textbox"]\',
                \'//button[contains(text(), "Comment")]\'
            ]
            
            comment_element = None
            for selector in comment_selectors:
                try:
                    comment_element = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
                    
            if not comment_element:
                self.logger.error("Could not find comment box")
                return False
                
            # Click to open comment box
            comment_element.click()
            time.sleep(random.uniform(1, 2))
            
            # Find the actual text input
            text_input_selectors = [
                \'//div[@role="textbox"]\',
                \'//div[contains(@class, "ql-editor")]\',
                \'//div[contains(@class, "comments-comment-texteditor__content-wrapper")]//div[@role="textbox"]\'
            ]
            
            text_input = None
            for selector in text_input_selectors:
                try:
                    text_input = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
                    
            if not text_input:
                self.logger.error("Could not find text input for comment")
                return False
                
            # Type the comment
            text_input.click()
            time.sleep(random.uniform(0.5, 1))
            text_input.send_keys(comment_text)
            time.sleep(random.uniform(1, 2))
            
            # Find and click post button
            post_button_selectors = [
                \'//button[contains(@class, "comments-comment-box__submit-button")]\',
                \'//button[contains(text(), "Post")]\',
                \'//button[@type="submit"]\'
            ]
            
            post_button = None
            for selector in post_button_selectors:
                try:
                    post_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except TimeoutException:
                    continue
                    
            if not post_button:
                self.logger.error("Could not find post button")
                return False
                
            post_button.click()
            time.sleep(random.uniform(2, 4))
            
            self.logger.info(f"Successfully commented on post: {post_url}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error commenting on post {post_url}: {str(e)}")
            return False
            
    def save_results(self, filename: str = \'results.txt\'):
        """Save results to file"""
        try:
            with open(filename, \'w\', encoding=\'utf-8\') as f:
                f.write(f"LinkedIn Comment Bot Results - {datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}\n")
                f.write("=" * 80 + "\n\n")
                
                successful = sum(1 for result in self.results if result.success)
                failed = len(self.results) - successful
                
                f.write(f"Summary:\n")
                f.write(f"Total attempts: {len(self.results)}\n")
                f.write(f"Successful: {successful}\n")
                f.write(f"Failed: {failed}\n")
                
                if len(self.results) > 0:
                    f.write(f"Success rate: {(successful/len(self.results)*100):.1f}%\n\n")
                else:
                    f.write("Success rate: N/A\n\n")
                
                f.write("Detailed Results:\n")
                f.write("-" * 40 + "\n")
                
                for i, result in enumerate(self.results, 1):
                    status = "SUCCESS" if result.success else "FAILED"
                    f.write(f"{i}. [{status}] {result.account_email}\n")
                    f.write(f"   Post: {result.post_url}\n")
                    f.write(f"   Comment: {result.comment_text[:100]}...\n")
                    f.write(f"   Time: {result.timestamp}\n")
                    if not result.success and result.error_message:
                        f.write(f"   Error: {result.error_message}\n")
                    f.write("\n")
                    
            self.logger.info(f"Results saved to {filename}")
            
        except Exception as e:
            self.logger.error(f"Error saving results: {str(e)}")
            
    def run(self):
        """Main execution method"""
        self.logger.info("Starting LinkedIn Comment Bot")
        
        # Load all required data
        if not self.load_accounts():
            self.logger.error("Failed to load accounts. Exiting.")
            return
            
        if not self.load_post_links():
            self.logger.error("Failed to load post links. Exiting.")
            return
            
        if not self.load_comments():
            self.logger.error("Failed to load comments. Exiting.")
            return
            
        self.load_proxies()  # Optional, won\'t exit on failure
        
        # Process each account
        for account_index, account in enumerate(self.accounts):
            self.logger.info(f"Processing account {account_index + 1}/{len(self.accounts)}: {account.email}")
            
            # Assign proxy if available
            proxy = None
            if self.proxies and account_index < len(self.proxies):
                proxy = self.proxies[account_index]
                self.logger.info(f"Using proxy: {proxy.host}:{proxy.port}")
                
            # Create driver
            driver = self.create_driver(proxy)
            if not driver:
                self.logger.error(f"Failed to create driver for {account.email}")
                continue
                
            try:
                # Login to LinkedIn
                if not self.login_to_linkedin(driver, account):
                    self.logger.error(f"Failed to login for {account.email}")
                    continue
                    
                # Comment on a maximum of 2 posts
                comments_made = 0
                for post_url in self.post_links:
                    if comments_made >= 2:
                        self.logger.info(f"Reached maximum comments (2) for {account.email}. Moving to next account.")
                        break

                    comment_text = random.choice(self.comments)
                    timestamp = datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')
                    
                    success = self.comment_on_post(driver, post_url, comment_text)
                    
                    result = CommentResult(
                        account_email=account.email,
                        post_url=post_url,
                        comment_text=comment_text,
                        success=success,
                        timestamp=timestamp,
                        error_message=None if success else "Comment failed"
                    )
                    
                    self.results.append(result)
                    
                    if success:
                        comments_made += 1

                    # Random delay between comments
                    time.sleep(random.uniform(10, 20))
                    
            except Exception as e:
                self.logger.error(f"Error processing account {account.email}: {str(e)}")
                
            finally:
                if driver:
                    driver.quit()
                
            # Delay between accounts
            if account_index < len(self.accounts) - 1:
                delay = random.uniform(30, 60)
                self.logger.info(f"Waiting {delay:.1f} seconds before next account...")
                time.sleep(delay)
                
        # Save results
        self.save_results()
        self.logger.info("LinkedIn Comment Bot completed")


def main():
    """Main entry point"""
    try:
        bot = LinkedInCommenter()
        bot.run()
    except KeyboardInterrupt:
        print("\nBot stopped by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")


if __name__ == "__main__":
    main()

