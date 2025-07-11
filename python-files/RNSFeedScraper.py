import re
import pandas as pd
from playwright.sync_api import sync_playwright
import time

def debug_pagination_structure(page):
    """Debug the pagination HTML structure to find correct selectors"""
    print("\n" + "="*60)
    print("🔍 DEBUGGING PAGINATION STRUCTURE")
    print("="*60)
    
    # Look for common pagination containers
    pagination_containers = [
        '.pagination', '.pager', '.page-nav', '.page-navigation', 
        '[class*="pagination"]', '[class*="pager"]', '[class*="page"]'
    ]
    
    for container in pagination_containers:
        try:
            elements = page.query_selector_all(container)
            if elements:
                print(f"\n📍 Found pagination container: {container}")
                for i, element in enumerate(elements):
                    html = element.inner_html()
                    print(f"   Container {i+1} HTML: {html[:200]}...")
        except:
            continue
    
    # Look for any elements containing "Next" or "Previous"
    next_elements = page.query_selector_all('*:has-text("Next"), *:has-text("next"), *[class*="next"], *[id*="next"]')
    if next_elements:
        print(f"\n🔍 Found {len(next_elements)} elements with 'Next':")
        for i, element in enumerate(next_elements):
            try:
                tag = element.evaluate('el => el.tagName')
                classes = element.get_attribute('class') or ''
                text = element.inner_text()[:50]
                disabled = element.get_attribute('disabled')
                aria_disabled = element.get_attribute('aria-disabled')
                is_visible = element.is_visible()
                print(f"   {i+1}. Tag: {tag}, Classes: '{classes}', Text: '{text}', Disabled: {disabled}, Visible: {is_visible}")
            except Exception as e:
                print(f"   {i+1}. Error getting element info: {e}")
    
    # Look for page numbers
    page_numbers = page.query_selector_all('*:has-text("1"), *:has-text("2"), *:has-text("3")')
    if page_numbers:
        print(f"\n🔢 Found potential page number elements: {len(page_numbers)}")
        for i, element in enumerate(page_numbers[:5]):  # Show first 5
            try:
                tag = element.evaluate('el => el.tagName')
                classes = element.get_attribute('class') or ''
                text = element.inner_text()[:20]
                is_visible = element.is_visible()
                print(f"   {i+1}. Tag: {tag}, Classes: '{classes}', Text: '{text}', Visible: {is_visible}")
            except Exception as e:
                print(f"   {i+1}. Error getting element info: {e}")
    
    # Let's also look for the bottom of the page where pagination typically is
    print(f"\n🔍 Looking for pagination at bottom of page...")
    try:
        # Get the bottom part of the page
        bottom_elements = page.query_selector_all('footer, .footer, [class*="pagination"], nav:last-of-type, div:last-of-type')
        for i, element in enumerate(bottom_elements[-3:]):  # Last 3 elements
            try:
                html = element.inner_html()
                if 'next' in html.lower() or 'previous' in html.lower() or any(num in html for num in ['1', '2', '3']):
                    print(f"   Bottom element {i+1} (potential pagination): {html[:300]}...")
            except:
                continue
    except Exception as e:
        print(f"   Error checking bottom elements: {e}")

def scrape_current_page(page):
    """Scrape data from the current page"""
    page.wait_for_selector('table tbody tr')
    
    rows = page.query_selector_all('table tbody tr')
    page_data = []
    
    for row in rows:
        cells = row.query_selector_all('td')
        if len(cells) < 3:
            continue
            
        raw_cells = [cell.inner_text().strip() for cell in cells]
        
        # Initialize with defaults
        time_text = ""
        date_text = ""
        title_text = ""
        tidm_text = ""
        company_text = ""
        category_text = ""
        
        # Analyze each cell and assign based on content patterns
        for i, cell_content in enumerate(raw_cells):
            
            # Check for time pattern
            if re.match(r'\d{2}:\d{2}:\d{2}', cell_content) and not time_text:
                time_match = re.match(r'(\d{2}:\d{2}:\d{2})(?:\s+([A-Z0-9]+))?', cell_content)
                if time_match:
                    time_text = time_match.group(1)
                    if time_match.group(2):
                        tidm_text = time_match.group(2)
            
            # Check for date pattern
            elif re.match(r'\d{1,2}\s+\w{3}\s+\d{4}', cell_content) and not date_text:
                date_text = cell_content
            
            # Check for TIDM pattern (short alphanumeric)
            elif re.match(r'^[A-Z0-9]{2,6}$', cell_content) and not tidm_text:
                tidm_text = cell_content
            
            # Check for category pattern
            elif cell_content in ['Holding(s) in company', 'Miscellaneous', 'Trading updates', 'Capital structure', 'Corporate updates', 'IRB', 'Director/PDMR dealings', 'Results'] and not category_text:
                category_text = cell_content
            
            # Long text could be company+title combination
            elif len(cell_content) > 20 and not title_text and not company_text:
                # Try to split company and title
                patterns = [
                    r'^([A-Za-z\s&.-]*?(?:PLC|plc|Limited|Ltd|Group|Corp|Inc|B\.V\.))\s*([A-Z].*)',
                    r'^([A-Za-z\s&.-]*?[a-z])\s+([A-Z][A-Za-z\s\-:,()]*)',
                ]
                
                parsed = False
                for pattern in patterns:
                    match = re.match(pattern, cell_content)
                    if match:
                        company_text = match.group(1).strip()
                        title_text = match.group(2).strip()
                        parsed = True
                        break
                
                if not parsed:
                    # Fallback: look for keywords to split
                    keywords = r'\b(Holding|Transaction|Statement|Report|Notification|Update|Publication|Director|PDMR|Financial|Results)\b'
                    split_match = re.search(keywords, cell_content, re.IGNORECASE)
                    if split_match:
                        company_text = cell_content[:split_match.start()].strip()
                        title_text = cell_content[split_match.start():].strip()
                    else:
                        title_text = cell_content
        
        # Add category inference if not found
        if not category_text and title_text:
            title_lower = title_text.lower()
            if 'holding' in title_lower or 'shareholding' in title_lower:
                category_text = 'Holding(s) in company'
            elif 'director' in title_lower or 'pdmr' in title_lower:
                category_text = 'Director/PDMR dealings'
            elif 'transaction' in title_lower and 'own shares' in title_lower:
                category_text = 'Capital structure'
            elif 'results' in title_lower or 'financial' in title_lower:
                category_text = 'Results'
            elif any(word in title_lower for word in ['update', 'statement', 'report']):
                category_text = 'Corporate updates'
            else:
                category_text = 'General'
        
        page_data.append({
            'Time': time_text,
            'Date': date_text,
            'Title': title_text,
            'TIDM': tidm_text,
            'Company': company_text,
            'Category': category_text
        })
    
    return page_data

def find_and_click_next_button(page):
    """Find and click the Next button using comprehensive selectors"""
    print("\n🔍 Looking for Next button...")
    
    # First, let's see all elements that might be clickable pagination controls
    clickable_elements = page.query_selector_all('button, a, div[onclick], span[onclick], [role="button"]')
    print(f"Found {len(clickable_elements)} potentially clickable elements")
    
    # Look for elements that might be pagination
    potential_next_buttons = []
    for element in clickable_elements:
        try:
            if element.is_visible():
                text = element.inner_text().strip().lower()
                classes = (element.get_attribute('class') or '').lower()
                aria_label = (element.get_attribute('aria-label') or '').lower()
                
                # Check if this might be a Next button
                if (('next' in text and len(text) < 20) or 
                    'next' in classes or 
                    'next' in aria_label or
                    ('>' in text and len(text) < 5) or
                    '→' in text or
                    'arrow-right' in classes or
                    'chevron-right' in classes):
                    
                    potential_next_buttons.append({
                        'element': element,
                        'text': element.inner_text()[:30],
                        'classes': element.get_attribute('class') or '',
                        'aria_label': element.get_attribute('aria-label') or '',
                        'tag': element.evaluate('el => el.tagName'),
                        'disabled': element.get_attribute('disabled') is not None or 
                                   'disabled' in classes or 
                                   element.get_attribute('aria-disabled') == 'true'
                    })
        except:
            continue
    
    if potential_next_buttons:
        print(f"\n🎯 Found {len(potential_next_buttons)} potential Next buttons:")
        for i, btn in enumerate(potential_next_buttons):
            print(f"   {i+1}. Tag: {btn['tag']}, Text: '{btn['text']}', Classes: '{btn['classes']}', Disabled: {btn['disabled']}")
        
        # Try to click the first enabled one
        for btn in potential_next_buttons:
            if not btn['disabled']:
                try:
                    print(f"\n✅ Attempting to click: '{btn['text']}' (Classes: {btn['classes']})")
                    
                    # Scroll element into view first
                    btn['element'].scroll_into_view_if_needed()
                    time.sleep(0.5)
                    
                    # Try to click
                    btn['element'].click()
                    print("✅ Click successful!")
                    
                    # Wait for navigation
                    time.sleep(2)
                    page.wait_for_load_state('networkidle', timeout=10000)
                    time.sleep(1)
                    
                    return True
                    
                except Exception as e:
                    print(f"❌ Click failed: {e}")
                    continue
            else:
                print(f"⚠️  Button is disabled: '{btn['text']}'")
    
    # If no obvious Next buttons found, try comprehensive selectors
    print("\n🔍 Trying comprehensive selector list...")
    
    selectors = [
        # Text-based selectors (most reliable)
        'button:has-text("Next")', 'a:has-text("Next")', 'span:has-text("Next")',
        'button:has-text(">")', 'a:has-text(">")', 'span:has-text(">")',
        
        # Class-based selectors
        '.next:not(.disabled)', '[class*="next"]:not([class*="disabled"])',
        '.page-next', '.pagination-next', '.pager-next',
        
        # Specific pagination patterns
        '.pagination button:not(.disabled):last-child',
        '.pagination a:not(.disabled):last-child',
        '.pager button:not(.disabled):last-child',
        
        # Icon-based
        'button [class*="arrow-right"]', 'button [class*="chevron-right"]',
        'a [class*="arrow-right"]', 'a [class*="chevron-right"]',
        
        # Fallback patterns
        'nav button:last-child:not(.disabled)',
        'nav a:last-child:not(.disabled)'
    ]
    
    for selector in selectors:
        try:
            elements = page.query_selector_all(selector)
            for element in elements:
                if element.is_visible():
                    # Double-check it's not disabled
                    classes = (element.get_attribute('class') or '').lower()
                    if ('disabled' not in classes and 
                        element.get_attribute('disabled') is None and
                        element.get_attribute('aria-disabled') != 'true'):
                        
                        try:
                            print(f"✅ Trying selector: {selector}")
                            element.scroll_into_view_if_needed()
                            time.sleep(0.5)
                            element.click()
                            print("✅ Click successful!")
                            
                            time.sleep(2)
                            page.wait_for_load_state('networkidle', timeout=10000)
                            time.sleep(1)
                            
                            return True
                        except Exception as e:
                            print(f"❌ Click failed: {e}")
                            continue
        except:
            continue
    
    print("❌ No working Next button found")
    return False

def main():
    url = "https://www.ticker.app/lse/rns"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print(f"Loading page: {url}")
        page.goto(url)
        
        # Wait for initial content to load
        page.wait_for_selector('table tbody tr')
        page.wait_for_timeout(5000)
        
        # Debug pagination structure on first page
        debug_pagination_structure(page)
        
        all_data = []
        page_number = 1
        
        print("\n" + "="*80)
        print("MULTI-PAGE DATA EXTRACTION")
        print("="*80)
        
        while True:
            print(f"\n📄 Scraping page {page_number}...")
            
            # Scrape current page
            try:
                page_data = scrape_current_page(page)
                if page_data:
                    all_data.extend(page_data)
                    print(f"   ✅ Extracted {len(page_data)} records from page {page_number}")
                else:
                    print(f"   ⚠️  No data found on page {page_number}")
                    break
            except Exception as e:
                print(f"   ❌ Error scraping page {page_number}: {e}")
                break
            
            # Try to find and click Next button
            print(f"\n🔄 Attempting to navigate to page {page_number + 1}...")
            
            if find_and_click_next_button(page):
                page_number += 1
                
                # Verify we're on a new page
                try:
                    page.wait_for_selector('table tbody tr', timeout=10000)
                    time.sleep(2)
                    print(f"✅ Successfully navigated to page {page_number}")
                except:
                    print("⚠️  Timeout waiting for next page to load")
                    break
            else:
                print(f"🏁 No more pages available. Finished scraping {page_number} pages.")
                break
            
            # Safety limit
            if page_number > 50:
                print("⚠️  Safety limit reached (50 pages). Stopping.")
                break
        
        browser.close()
        
        if all_data:
            # Save all data to Excel
            df = pd.DataFrame(all_data)
            df.to_excel('ticker_announcements_complete.xlsx', index=False)
            
            print("\n" + "="*80)
            print("📊 COMPLETE EXTRACTION SUMMARY")
            print("="*80)
            print(f"✅ Total pages scraped: {page_number}")
            print(f"✅ Total records extracted: {len(all_data)}")
            print(f"✅ Data saved to: ticker_announcements_complete.xlsx")
            
            # Quality assessment
            valid_times = sum(1 for item in all_data if item['Time'] and re.match(r'\d{2}:\d{2}:\d{2}$', item['Time']))
            valid_dates = sum(1 for item in all_data if item['Date'] and re.match(r'\d{1,2}\s+\w{3}\s+\d{4}$', item['Date']))
            valid_tidms = sum(1 for item in all_data if item['TIDM'] and re.match(r'^[A-Z0-9]{2,6}$', item['TIDM']))
            valid_companies = sum(1 for item in all_data if item['Company'] and len(item['Company']) > 2)
            valid_titles = sum(1 for item in all_data if item['Title'] and len(item['Title']) > 2)
            valid_categories = sum(1 for item in all_data if item['Category'])
            
            total = len(all_data)
            print(f"\n📈 QUALITY METRICS:")
            print(f"   Times: {valid_times}/{total} ({valid_times/total*100:.1f}%)")
            print(f"   Dates: {valid_dates}/{total} ({valid_dates/total*100:.1f}%)")
            print(f"   TIDMs: {valid_tidms}/{total} ({valid_tidms/total*100:.1f}%)")
            print(f"   Companies: {valid_companies}/{total} ({valid_companies/total*100:.1f}%)")
            print(f"   Titles: {valid_titles}/{total} ({valid_titles/total*100:.1f}%)")
            print(f"   Categories: {valid_categories}/{total} ({valid_categories/total*100:.1f}%)")
            
            # Show sample data
            print(f"\n📋 SAMPLE DATA:")
            for i, item in enumerate(all_data[:5]):
                print(f"{i+1}. {item['Time']} | {item['Date']} | {item['TIDM']} | {item['Company'][:30]} | {item['Title'][:40]}")
        
        else:
            print("❌ No data extracted")

if __name__ == "__main__":
    main()

