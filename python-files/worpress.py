import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import json
import os
import re
import time
from urllib.error import URLError, HTTPError
from html.parser import HTMLParser

class FormParser(HTMLParser):
    """Custom HTML parser to extract forms and their fields"""
    
    def __init__(self):
        super().__init__()
        self.forms = []
        self.current_form = None
        self.in_form = False
        self.current_form_has_files = False
        
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'form':
            self.in_form = True
            self.current_form_has_files = False
            attrs_dict = dict(attrs)
            self.current_form = {
                'action': attrs_dict.get('action', ''),
                'method': attrs_dict.get('method', 'GET').upper(),
                'enctype': attrs_dict.get('enctype', ''),
                'fields': [],
                'file_fields': [],
                'has_file_upload': False
            }
            
        elif self.in_form and tag.lower() in ['input', 'textarea', 'select']:
            attrs_dict = dict(attrs)
            field_type = attrs_dict.get('type', 'text').lower()
            field_name = attrs_dict.get('name', '')
            field_id = attrs_dict.get('id', '')
            field_placeholder = attrs_dict.get('placeholder', '')
            field_required = 'required' in [attr[0] for attr in attrs]
            field_accept = attrs_dict.get('accept', '')
            field_multiple = 'multiple' in [attr[0] for attr in attrs]
            
            if field_name:  # Only add fields with names
                field_info = {
                    'tag': tag.lower(),
                    'type': field_type,
                    'name': field_name,
                    'id': field_id,
                    'placeholder': field_placeholder,
                    'required': field_required
                }
                
                # Check if this is a file upload field
                if field_type == 'file':
                    self.current_form_has_files = True
                    file_field_info = field_info.copy()
                    file_field_info.update({
                        'accept': field_accept,
                        'multiple': field_multiple,
                        'accepted_file_types': self.parse_accept_attribute(field_accept)
                    })
                    self.current_form['file_fields'].append(file_field_info)
                
                self.current_form['fields'].append(field_info)
    
    def handle_endtag(self, tag):
        if tag.lower() == 'form' and self.in_form:
            self.in_form = False
            if self.current_form and self.current_form['fields']:
                # Mark if form has file upload capability
                self.current_form['has_file_upload'] = self.current_form_has_files
                self.forms.append(self.current_form)
            self.current_form = None
            self.current_form_has_files = False
    
    def parse_accept_attribute(self, accept_attr):
        """Parse the accept attribute to identify file types"""
        if not accept_attr:
            return []
        
        file_types = []
        accept_values = [val.strip() for val in accept_attr.split(',')]
        
        for val in accept_values:
            if val.startswith('.'):
                file_types.append(val)
            elif '/' in val:
                file_types.append(val)
        
        return file_types

class WordPressSitemapAnalyzer:
    """Main analyzer class for WordPress sitemaps and forms"""
    
    def __init__(self, website_url, delay=1):
        self.website_url = self.normalize_url(website_url)
        self.delay = delay
        self.session_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.site_name = self.extract_site_name(self.website_url)
        self.base_dir = self.site_name
        self.sitemaps_data = {}
        self.forms_data = {}
        self.file_forms_data = {}  # New: Store forms with file upload capability
        
        # Debug print to see what we're getting
        print(f"Original URL: {website_url}")
        print(f"Normalized URL: {self.website_url}")
        print(f"Site name: '{self.site_name}'")
        print(f"Base directory: '{self.base_dir}'")
        
        # Create directory structure
        self.setup_directories()
    
    def normalize_url(self, url):
        """Normalize URL by adding https:// if missing"""
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url.rstrip('/')
    
    def extract_site_name(self, url):
        """Extract site name from URL for folder naming"""
        parsed = urllib.parse.urlparse(url)
        domain = parsed.netloc
        if not domain:  # Handle case where URL might not have protocol
            domain = url.replace('http://', '').replace('https://', '').split('/')[0]
        
        # Remove www. and replace dots/special chars with underscores
        domain = re.sub(r'^www\.', '', domain)
        domain = re.sub(r'[^\w\-]', '_', domain)
        
        # Ensure we have a valid directory name
        if not domain or domain.strip() == '':
            domain = 'website_analysis'
        
        return domain
    
    def setup_directories(self):
        """Create necessary directories"""
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)
        print(f"Created directory: {self.base_dir}")
    
    def make_request(self, url, timeout=10):
        """Make HTTP request with error handling"""
        try:
            req = urllib.request.Request(url, headers=self.session_headers)
            with urllib.request.urlopen(req, timeout=timeout) as response:
                return response.read().decode('utf-8', errors='ignore')
        except (URLError, HTTPError, Exception) as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def find_sitemap_urls(self):
        """Find all sitemap URLs starting from main sitemap.xml"""
        main_sitemap_url = f"{self.website_url}/sitemap_index.xml"
        print(f"Starting with main sitemap: {main_sitemap_url}")
        
        all_sitemaps = set()
        to_process = [main_sitemap_url]
        processed = set()
        
        while to_process:
            current_url = to_process.pop(0)
            if current_url in processed:
                continue
                
            processed.add(current_url)
            print(f"Processing sitemap: {current_url}")
            
            content = self.make_request(current_url)
            if not content:
                continue
                
            try:
                root = ET.fromstring(content)
                
                # Handle sitemap index files
                sitemap_elements = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}sitemap')
                if sitemap_elements:
                    print(f"Found sitemap index with {len(sitemap_elements)} sitemaps")
                    for sitemap_elem in sitemap_elements:
                        loc_elem = sitemap_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                        if loc_elem is not None:
                            sitemap_url = loc_elem.text.strip()
                            if sitemap_url not in processed:
                                to_process.append(sitemap_url)
                                all_sitemaps.add(sitemap_url)
                
                # Handle regular sitemap files
                url_elements = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
                if url_elements:
                    print(f"Found regular sitemap with {len(url_elements)} URLs")
                    all_sitemaps.add(current_url)
                
            except ET.ParseError as e:
                print(f"XML parsing error for {current_url}: {e}")
                continue
            
            time.sleep(self.delay)
        
        return list(all_sitemaps)
    
    def extract_urls_from_sitemap(self, sitemap_url):
        """Extract all URLs from a sitemap"""
        content = self.make_request(sitemap_url)
        if not content:
            return []
        
        try:
            root = ET.fromstring(content)
            urls = []
            
            # Extract URLs from sitemap
            url_elements = root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}url')
            for url_elem in url_elements:
                loc_elem = url_elem.find('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
                if loc_elem is not None:
                    urls.append(loc_elem.text.strip())
            
            return urls
            
        except ET.ParseError as e:
            print(f"XML parsing error for {sitemap_url}: {e}")
            return []
    
    def analyze_page_for_forms(self, page_url):
        """Analyze a page for forms"""
        print(f"Analyzing page for forms: {page_url}")
        content = self.make_request(page_url)
        
        if not content:
            return []
        
        parser = FormParser()
        try:
            parser.feed(content)
            return parser.forms
        except Exception as e:
            print(f"Error parsing HTML for {page_url}: {e}")
            return []
    
    def save_sitemaps_data(self):
        """Save sitemaps data to JSON file"""
        sitemap_file = os.path.join(self.base_dir, 'sitemap.xml.json')
        try:
            with open(sitemap_file, 'w', encoding='utf-8') as f:
                json.dump(self.sitemaps_data, f, indent=2, ensure_ascii=False)
            print(f"Sitemaps data saved to: {sitemap_file}")
        except Exception as e:
            print(f"Error saving sitemaps data: {e}")
    
    def save_file_forms_data(self):
        """Save file upload forms data to JSON file"""
        forms_file = os.path.join(self.base_dir, 'forms.file.json')
        try:
            with open(forms_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_forms_data, f, indent=2, ensure_ascii=False)
            print(f"File upload forms data saved to: {forms_file}")
        except Exception as e:
            print(f"Error saving file forms data: {e}")
    
    def save_forms_data(self):
        """Save forms data to JSON file"""
        forms_file = os.path.join(self.base_dir, 'forms.json')
        try:
            with open(forms_file, 'w', encoding='utf-8') as f:
                json.dump(self.forms_data, f, indent=2, ensure_ascii=False)
            print(f"Forms data saved to: {forms_file}")
        except Exception as e:
            print(f"Error saving forms data: {e}")
    
    def save_file_forms_data(self):
        """Save file upload forms data to JSON file"""
        forms_file = os.path.join(self.base_dir, 'forms.file.json')
        try:
            with open(forms_file, 'w', encoding='utf-8') as f:
                json.dump(self.file_forms_data, f, indent=2, ensure_ascii=False)
            print(f"File upload forms data saved to: {forms_file}")
        except Exception as e:
            print(f"Error saving file forms data: {e}")
    
    def categorize_file_upload_form(self, forms):
        """Categorize and enhance file upload form data"""
        file_forms = []
        
        for form in forms:
            if form.get('has_file_upload', False):
                # Enhanced form data with file upload analysis
                enhanced_form = form.copy()
                
                # Analyze file field capabilities
                file_capabilities = {
                    'supports_pdf': False,
                    'supports_images': False,
                    'supports_documents': False,
                    'supports_any_file': False,
                    'multiple_files': False
                }
                
                for file_field in form.get('file_fields', []):
                    accepted_types = file_field.get('accepted_file_types', [])
                    
                    if file_field.get('multiple', False):
                        file_capabilities['multiple_files'] = True
                    
                    if not accepted_types:  # No accept attribute means any file type
                        file_capabilities['supports_any_file'] = True
                        file_capabilities['supports_pdf'] = True
                        file_capabilities['supports_images'] = True
                        file_capabilities['supports_documents'] = True
                    else:
                        for file_type in accepted_types:
                            file_type_lower = file_type.lower()
                            
                            # Check for PDF support
                            if 'pdf' in file_type_lower or file_type_lower == '.pdf' or file_type_lower == 'application/pdf':
                                file_capabilities['supports_pdf'] = True
                            
                            # Check for image support
                            if ('image' in file_type_lower or 
                                file_type_lower in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg']):
                                file_capabilities['supports_images'] = True
                            
                            # Check for document support
                            if (file_type_lower in ['.doc', '.docx', '.txt', '.rtf', '.odt'] or
                                'document' in file_type_lower or 'text' in file_type_lower):
                                file_capabilities['supports_documents'] = True
                
                enhanced_form['file_capabilities'] = file_capabilities
                file_forms.append(enhanced_form)
        
        return file_forms
    
    def run_analysis(self):
        """Run the complete analysis"""
        print(f"Starting analysis for: {self.website_url}")
        print("=" * 50)
        
        # Step 1: Find all sitemap URLs
        print("Step 1: Finding all sitemap URLs...")
        sitemap_urls = self.find_sitemap_urls()
        
        if not sitemap_urls:
            print("No sitemaps found!")
            return
        
        print(f"Found {len(sitemap_urls)} sitemap(s)")
        
        # Step 2: Process each sitemap and collect URLs
        print("\nStep 2: Processing sitemaps and collecting URLs...")
        all_page_urls = []
        
        for sitemap_url in sitemap_urls:
            print(f"Processing: {sitemap_url}")
            urls = self.extract_urls_from_sitemap(sitemap_url)
            
            # Store sitemap data
            self.sitemaps_data[sitemap_url] = {
                'url_count': len(urls),
                'urls': urls
            }
            
            all_page_urls.extend(urls)
            time.sleep(self.delay)
        
        # Save sitemaps data
        self.save_sitemaps_data()
        
        # Remove duplicates
        unique_urls = list(set(all_page_urls))
        print(f"Found {len(unique_urls)} unique URLs to analyze")
        
        # Step 3: Analyze each URL for forms
        print("\nStep 3: Analyzing URLs for forms...")
        pages_with_forms = 0
        pages_with_file_forms = 0
        total_forms = 0
        total_file_forms = 0
        
        for i, page_url in enumerate(unique_urls, 1):
            print(f"Progress: {i}/{len(unique_urls)} - Checking: {page_url}")
            
            forms = self.analyze_page_for_forms(page_url)
            
            if forms:
                pages_with_forms += 1
                total_forms += len(forms)
                
                # Store all forms
                self.forms_data[page_url] = {
                    'form_count': len(forms),
                    'forms': forms
                }
                
                # Check for file upload forms
                file_forms = self.categorize_file_upload_form(forms)
                if file_forms:
                    pages_with_file_forms += 1
                    total_file_forms += len(file_forms)
                    
                    self.file_forms_data[page_url] = {
                        'file_form_count': len(file_forms),
                        'forms': file_forms
                    }
                    
                    print(f"  ✓ Found {len(forms)} form(s) ({len(file_forms)} with file upload)")
                else:
                    print(f"  ✓ Found {len(forms)} form(s)")
            
            time.sleep(self.delay)
        
        # Save forms data
        self.save_forms_data()
        self.save_file_forms_data()
        
        # Step 4: Summary
        print("\n" + "=" * 50)
        print("ANALYSIS COMPLETE")
        print("=" * 50)
        print(f"Website: {self.website_url}")
        print(f"Total sitemaps found: {len(sitemap_urls)}")
        print(f"Total URLs analyzed: {len(unique_urls)}")
        print(f"Pages with forms: {pages_with_forms}")
        print(f"Total forms found: {total_forms}")
        print(f"Pages with file upload forms: {pages_with_file_forms}")
        print(f"Total file upload forms found: {total_file_forms}")
        print(f"Results saved in: {self.base_dir}/")
        print("  - sitemap.xml.json (sitemap data)")
        print("  - forms.json (all forms data)")
        print("  - forms.file.json (file upload forms data)")

def main():
    """Main function to run the analyzer"""
    print("WordPress Sitemap and Form Analyzer")
    print("=" * 40)
    
    # Get website URL from user
    website_url = input("Enter the WordPress website URL: ").strip()
    
    if not website_url:
        print("Error: Please provide a valid website URL")
        return
    
    # Optional: Get delay between requests
    delay_input = input("Enter delay between requests in seconds (default: 1): ").strip()
    try:
        delay = float(delay_input) if delay_input else 1.0
    except ValueError:
        delay = 1.0
    
    # Create and run analyzer
    analyzer = WordPressSitemapAnalyzer(website_url, delay)
    analyzer.run_analysis()

if __name__ == "__main__":
    main()