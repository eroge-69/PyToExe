import time
import json
import re
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
import google.generativeai as genai
from bs4 import BeautifulSoup

class RocketReachAutomationWithLLM:
    def __init__(self, gemini_api_key, headless=False, timeout=10):
        """
        Initialize the RocketReach automation tool with Gemini LLM extraction
        
        Args:
            gemini_api_key (str): Your Gemini API key
            headless (bool): Run browser in headless mode
            timeout (int): Default timeout for waiting operations
        """
        self.driver = None
        self.wait = None
        self.timeout = timeout
        self.setup_driver(headless)
        self.setup_gemini(gemini_api_key)
    
    def setup_gemini(self, api_key):
        """Setup Gemini API"""
        try:
            genai.configure(api_key=api_key)
            self.gemini_model = genai.GenerativeModel('gemini-1.5-flash')
            print("Gemini API configured successfully")
        except Exception as e:
            print(f"Error setting up Gemini API: {str(e)}")
            self.gemini_model = None
    
    def setup_driver(self, headless=False):
        """Setup Chrome WebDriver with options optimized for dynamic content"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        self.wait = WebDriverWait(self.driver, self.timeout)
        self.driver.maximize_window()
    
    def wait_for_dynamic_content(self, locator, timeout=None):
        """Wait for dynamic content to load with multiple fallback strategies"""
        if timeout is None:
            timeout = self.timeout
            
        wait = WebDriverWait(self.driver, timeout)
        
        try:
            element = wait.until(EC.visibility_of_element_located(locator))
            return element
        except TimeoutException:
            try:
                element = wait.until(EC.presence_of_element_located(locator))
                return element
            except TimeoutException:
                try:
                    return self.driver.find_element(*locator)
                except NoSuchElementException:
                    raise TimeoutException(f"Element {locator} not found after {timeout} seconds")
    
    def wait_for_page_load(self, timeout=None):
        """Wait for page to fully load including JavaScript"""
        if timeout is None:
            timeout = self.timeout
            
        wait = WebDriverWait(self.driver, timeout)
        wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
        
        try:
            wait.until(lambda driver: driver.execute_script("return typeof jQuery !== 'undefined' ? jQuery.active == 0 : true"))
        except:
            pass
        
        time.sleep(3)
    
    def scroll_to_element(self, element):
        """Scroll element into view"""
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(1)
    
    def safe_click(self, element, max_retries=3):
        """Safely click an element with retries for dynamic content"""
        for attempt in range(max_retries):
            try:
                self.scroll_to_element(element)
                element.click()
                return True
            except ElementClickInterceptedException:
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except:
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    else:
                        raise
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                else:
                    raise e
        return False
    
    def login(self, email, password):
        """Login to RocketReach"""
        try:
            print("Navigating to RocketReach login page...")
            self.driver.get("https://rocketreach.co/login")
            self.wait_for_page_load(timeout=10)
            
            # Check if already logged in
            dashboard_indicators = [
                "#person-search-input-field",
                "input[placeholder*='LinkedIn URL']",
                "input[placeholder*='Job Title']",
                "[data-testid='search-input']",
                ".search-input",
                "input[placeholder*='search']",
                ".dashboard",
                "nav[role='navigation']"
            ]
            
            for selector in dashboard_indicators:
                try:
                    element = self.wait_for_dynamic_content((By.CSS_SELECTOR, selector), timeout=5)
                    if element:
                        print(f"Already logged in! Found dashboard element: {selector}")
                        return True
                except TimeoutException:
                    continue
            
            print("Not logged in, proceeding with login...")
            time.sleep(3)
            
            # Find and fill email
            email_selectors = [
                "input[type='email']",
                "input[name='email']",
                "input[placeholder*='email' i]",
                "#email"
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = self.wait_for_dynamic_content((By.CSS_SELECTOR, selector), timeout=10)
                    print(f"Found email input with selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not email_input:
                raise Exception("Could not find email input field")
            
            email_input.clear()
            email_input.send_keys(email)
            time.sleep(1)
            
            # Find and fill password
            password_selectors = [
                "input[type='password']",
                "input[name='password']",
                "input[placeholder*='password' i]",
                "#password"
            ]
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = self.wait_for_dynamic_content((By.CSS_SELECTOR, selector), timeout=10)
                    break
                except TimeoutException:
                    continue
            
            if not password_input:
                raise Exception("Could not find password input field")
            
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(1)
            
            # Submit form
            submit_selectors = [
                "button[type='submit']",
                "input[type='submit']",
                ".login-submit",
                ".submit-btn"
            ]
            
            submit_button = None
            for selector in submit_selectors:
                try:
                    submit_button = self.wait_for_dynamic_content((By.CSS_SELECTOR, selector), timeout=5)
                    break
                except TimeoutException:
                    continue
            
            if submit_button:
                self.safe_click(submit_button)
            else:
                password_input.send_keys(Keys.RETURN)
            
            time.sleep(5)
            self.wait_for_page_load(timeout=10)
            
            # Verify login
            for attempt in range(3):
                current_url = self.driver.current_url.lower()
                if 'dashboard' in current_url or 'search' in current_url or (not 'login' in current_url):
                    return True
                
                for selector in dashboard_indicators:
                    try:
                        element = self.wait_for_dynamic_content((By.CSS_SELECTOR, selector), timeout=10)
                        if element and element.is_displayed():
                            return True
                    except TimeoutException:
                        continue
                
                if attempt < 2:
                    time.sleep(5)
            
            return False
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return False
    
    def search_linkedin_profile(self, linkedin_url):
        """Search for LinkedIn profile on RocketReach"""
        try:
            print(f"Searching for LinkedIn profile: {linkedin_url}")
            time.sleep(3)
            
            search_selectors = [
                "#person-search-input-field",
                "input[placeholder*='LinkedIn URL' i]",
                "input[placeholder*='Job Title' i]",
                "[data-testid='search-input']",
                ".search-input",
                "input[placeholder*='search' i]"
            ]
            
            search_input = None
            for selector in search_selectors:
                try:
                    search_input = self.wait_for_dynamic_content((By.CSS_SELECTOR, selector), timeout=15)
                    break
                except TimeoutException:
                    continue
            
            if not search_input:
                raise Exception("Could not find search input field")
            
            search_input.clear()
            time.sleep(2)
            search_input.send_keys(linkedin_url)
            time.sleep(3)
            
            # Submit search
            search_button_selectors = [
                "button[data-testid='search-button']",
                ".search-button",
                "button[type='submit']",
                ".search-btn"
            ]
            
            search_button = None
            for selector in search_button_selectors:
                try:
                    search_button = self.wait_for_dynamic_content((By.CSS_SELECTOR, selector), timeout=5)
                    break
                except TimeoutException:
                    continue
            
            if search_button:
                self.safe_click(search_button)
            else:
                search_input.send_keys(Keys.RETURN)
            
            self.wait_for_page_load(timeout=10)
            return True
            
        except Exception as e:
            print(f"Search error: {str(e)}")
            return False
    
    def try_click_contact_button(self):
        """Try to click 'Get Contact Info' button"""
        try:
            print("Looking for 'Get Contact Info' button...")
            
            contact_button_selectors = [
                "//button[contains(text(), 'Get Contact Info')]",
                "//button[contains(text(), 'Contact Info')]",
                "//button[contains(text(), 'Reveal')]",
                "//button[contains(text(), 'Unlock')]",
                "button.button-primary",
                "button[primary='true']"
            ]
            
            for selector in contact_button_selectors:
                try:
                    if selector.startswith("//"):
                        button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                    else:
                        button = WebDriverWait(self.driver, 5).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                        )
                    
                    print(f"Found contact button: {selector}")
                    self.safe_click(button)
                    time.sleep(8)
                    self.wait_for_page_load(timeout=10)
                    return True
                    
                except TimeoutException:
                    continue
            
            # Try searching through all buttons
            all_buttons = self.driver.find_elements(By.TAG_NAME, "button")
            for button in all_buttons:
                try:
                    text = button.text.lower()
                    if any(keyword in text for keyword in ['contact info', 'get contact', 'reveal', 'unlock']):
                        print(f"Found button by text: {button.text}")
                        self.safe_click(button)
                        time.sleep(8)
                        self.wait_for_page_load(timeout=10)
                        return True
                except:
                    continue
            
            print("Contact button not found - proceeding with current page content")
            return False
            
        except Exception as e:
            print(f"Error clicking contact button: {str(e)}")
            return False
    
    def comprehensive_page_scroll(self):
        """Comprehensive scrolling to trigger all dynamic content"""
        try:
            print("Performing comprehensive page scroll to load all content...")
            
            # Get page dimensions
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Multiple scroll patterns
            scroll_positions = []
            
            # Linear scroll positions
            for i in range(0, page_height, viewport_height // 3):
                scroll_positions.append(i)
            
            # Key positions
            scroll_positions.extend([
                0,
                page_height // 4,
                page_height // 2,
                page_height * 3 // 4,
                page_height
            ])
            
            # Remove duplicates and sort
            scroll_positions = sorted(list(set(scroll_positions)))
            
            for position in scroll_positions:
                self.driver.execute_script(f"window.scrollTo(0, {position});")
                time.sleep(2)
                
                # Check if new content loaded
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height > page_height:
                    page_height = new_height
                    print(f"Page height increased to {new_height}px")
            
            # Final scroll to bottom and back to top
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            self.driver.execute_script("window.scrollTo(0, 0);")
            time.sleep(2)
            
            print("Comprehensive scroll completed")
            
        except Exception as e:
            print(f"Error during comprehensive scroll: {str(e)}")
    
    def extract_page_content(self):
        """Extract comprehensive page content for LLM processing"""
        try:
            print("Extracting page content for LLM processing...")
            
            # Get page HTML
            page_source = self.driver.page_source
            
            # Get visible text
            visible_text = self.driver.find_element(By.TAG_NAME, "body").text
            
            # Get current URL and title
            current_url = self.driver.current_url
            page_title = self.driver.title
            
            # Extract all links
            links = []
            try:
                link_elements = self.driver.find_elements(By.TAG_NAME, "a")
                for link in link_elements:
                    href = link.get_attribute('href') or ''
                    text = link.text.strip()
                    if href or text:
                        links.append({
                            'href': href,
                            'text': text,
                            'classes': link.get_attribute('class') or '',
                            'data_testid': link.get_attribute('data-testid') or ''
                        })
            except Exception as e:
                print(f"Error extracting links: {str(e)}")
            
            # Use BeautifulSoup to clean HTML
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Remove script and style tags
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get clean text
            clean_text = soup.get_text()
            
            return {
                'url': current_url,
                'title': page_title,
                'html_source': page_source,
                'visible_text': visible_text,
                'clean_text': clean_text,
                'links': links,
                'extraction_timestamp': time.time()
            }
            
        except Exception as e:
            print(f"Error extracting page content: {str(e)}")
            return None
    
    def extract_contact_info_with_llm(self, page_content):
        """Use Gemini LLM to extract contact information from page content"""
        try:
            if not self.gemini_model:
                print("Gemini model not available")
                return None
            
            print("Using Gemini LLM to extract contact information...")
            
            # Prepare the prompt for Gemini
            prompt = f"""
You are an expert at extracting contact information from web page content. 
Analyze the following web page content and extract all available contact information.

URL: {page_content['url']}
Title: {page_content['title']}

LINKS FOUND ON PAGE:
{json.dumps(page_content['links'][:50], indent=2)}  # Limit to first 50 links

VISIBLE TEXT FROM PAGE:
{page_content['visible_text'][:8000]}  # Limit text to avoid token limits

TASK: Extract and return ONLY the following information in valid JSON format:

{{
    "emails": ["list of email addresses found"],
    "phones": ["list of phone numbers found"],
    "social_links": {{
        "linkedin": "LinkedIn URL if found",
        "twitter": "Twitter URL if found",
        "facebook": "Facebook URL if found",
        "instagram": "Instagram URL if found"
    }},
    "company_info": {{
        "company_name": "Company name if found",
        "job_title": "Job title if found",
        "location": "Location if found"
    }},
    "other_contact_info": ["any other contact information like websites, addresses, etc."],
    "confidence_score": "high/medium/low based on how confident you are about the extracted information"
}}

IMPORTANT RULES:
1. Only extract information that is clearly present in the content
2. For emails: Look for email addresses in mailto links or visible text
3. For phones: Look for phone numbers in tel links or visible text
4. Return valid JSON only - no additional text or explanations
5. If no information is found for a category, use empty arrays or empty strings
6. Be conservative - only extract information you're confident about
"""
            
            # Generate response from Gemini
            response = self.gemini_model.generate_content(prompt)
            
            # Parse the JSON response
            try:
                # Clean the response text (remove any markdown code blocks)
                response_text = response.text.strip()
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                contact_info = json.loads(response_text.strip())
                
                print(f"LLM extraction completed successfully")
                print(f"Emails found: {len(contact_info.get('emails', []))}")
                print(f"Phones found: {len(contact_info.get('phones', []))}")
                
                return contact_info
                
            except json.JSONDecodeError as e:
                print(f"Error parsing LLM response as JSON: {str(e)}")
                print(f"Raw response: {response.text[:500]}...")
                
                # Fallback: try to extract emails and phones using regex
                return self.fallback_extraction(page_content)
                
        except Exception as e:
            print(f"Error in LLM extraction: {str(e)}")
            return self.fallback_extraction(page_content)
    
    def fallback_extraction(self, page_content):
        """Fallback extraction using regex patterns"""
        try:
            print("Using fallback regex extraction...")
            
            # Combine all text sources
            all_text = f"{page_content['visible_text']} {page_content['clean_text']}"
            
            # Extract emails using regex
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = list(set(re.findall(email_pattern, all_text)))
            
            # Extract phones using regex
            phone_pattern = r'[\+]?[1-9]?[0-9]{7,15}'
            phones = list(set(re.findall(phone_pattern, all_text)))
            
            # Extract from links
            link_emails = []
            link_phones = []
            
            for link in page_content['links']:
                href = link.get('href', '')
                if href.startswith('mailto:'):
                    email = href.replace('mailto:', '').strip()
                    if email:
                        link_emails.append(email)
                elif href.startswith('tel:'):
                    phone = href.replace('tel:', '').strip()
                    if phone:
                        link_phones.append(phone)
            
            # Combine results
            all_emails = list(set(emails + link_emails))
            all_phones = list(set(phones + link_phones))
            
            return {
                'emails': all_emails,
                'phones': all_phones,
                'social_links': {},
                'company_info': {},
                'other_contact_info': [],
                'confidence_score': 'medium',
                'extraction_method': 'fallback_regex'
            }
            
        except Exception as e:
            print(f"Error in fallback extraction: {str(e)}")
            return {
                'emails': [],
                'phones': [],
                'social_links': {},
                'company_info': {},
                'other_contact_info': [],
                'confidence_score': 'low',
                'extraction_method': 'failed',
                'error': str(e)
            }
    
    def process_linkedin_url(self, linkedin_url, email=None, password=None):
        """Complete process with LLM extraction"""
        try:
            # Login if credentials provided
            if email and password:
                if not self.login(email, password):
                    return {'error': 'Login failed'}
            
            # Search for LinkedIn profile
            if not self.search_linkedin_profile(linkedin_url):
                return {'error': 'Search failed'}
            
            # Try to click contact info button
            button_clicked = self.try_click_contact_button()
            
            # Comprehensive scroll to load all content
            self.comprehensive_page_scroll()
            
            # Extract page content
            page_content = self.extract_page_content()
            if not page_content:
                return {'error': 'Failed to extract page content'}
            
            # Use LLM to extract contact information
            contact_info = self.extract_contact_info_with_llm(page_content)
            if not contact_info:
                return {'error': 'Failed to extract contact information'}
            
            # Add metadata
            contact_info['button_clicked'] = button_clicked
            contact_info['extraction_method'] = 'llm_extraction'
            contact_info['source_url'] = page_content['url']
            contact_info['page_title'] = page_content['title']
            contact_info['search_linkedin_url'] = linkedin_url
            
            return contact_info
            
        except Exception as e:
            return {'error': str(e)}
    
    def quit(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()
            print("Browser closed")

def main():
    """Example usage"""
    
    # Your API keys and credentials
    GEMINI_API_KEY = "AIzaSyBif8p8BhEEG1lfEUaKcgi8irXKqlg2ZDQ"  # Replace with your actual API key
    ROCKETREACH_EMAIL = "asc15.ljn@gmail.com"
    ROCKETREACH_PASSWORD = "Anurag@123"
    
    # LinkedIn URL to search
    linkedin_url = "https://www.linkedin.com/in/chloengassa/"
    
    automation = RocketReachAutomationWithLLM(
        gemini_api_key=GEMINI_API_KEY,
        headless=False
    )
    
    try:
        print("Starting RocketReach automation with LLM extraction...")
        
        # Process the LinkedIn URL
        result = automation.process_linkedin_url(
            linkedin_url, 
            ROCKETREACH_EMAIL, 
            ROCKETREACH_PASSWORD
        )
        
        # Print results
        print("\n" + "="*60)
        print("CONTACT INFORMATION EXTRACTED WITH LLM:")
        print("="*60)
        
        if 'error' in result:
            print(f"Error: {result['error']}")
        else:
            print(f"Extraction method: {result.get('extraction_method', 'unknown')}")
            print(f"Button clicked: {result.get('button_clicked', 'unknown')}")
            print(f"Confidence score: {result.get('confidence_score', 'unknown')}")
            print(f"Source URL: {result.get('source_url', 'unknown')}")
            
            emails = result.get('emails', [])
            print(f"\n📧 Emails found: {len(emails)}")
            for email in emails:
                print(f"  - {email}")
            
            phones = result.get('phones', [])
            print(f"\n📞 Phones found: {len(phones)}")
            for phone in phones:
                print(f"  - {phone}")
            
            social_links = result.get('social_links', {})
            print(f"\n🔗 Social Links:")
            for platform, link in social_links.items():
                if link:
                    print(f"  - {platform.title()}: {link}")
            
            company_info = result.get('company_info', {})
            print(f"\n🏢 Company Information:")
            for key, value in company_info.items():
                if value:
                    print(f"  - {key.replace('_', ' ').title()}: {value}")
            
            other_info = result.get('other_contact_info', [])
            if other_info:
                print(f"\n📋 Other Contact Info:")
                for info in other_info:
                    print(f"  - {info}")
            
            # Save results
            output_file = 'contact_info_llm.json'
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            print(f"\n💾 Results saved to {output_file}")
        
    except KeyboardInterrupt:
        print("\nProcess interrupted by user")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
    finally:
        automation.quit()

if __name__ == "__main__":
    main()