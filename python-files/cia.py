#!/usr/bin/env python3
"""
CIA Terminal Simulator - Executable Version
Opens in new terminal window, realistic movie-style intelligence display
"""

import time
import random
import requests
import json
import os
import sys
import subprocess
import platform
from datetime import datetime
from colorama import init, Fore, Back, Style

# Initialize colorama for cross-platform color support
init(autoreset=True)

def open_new_terminal():
    """Open this script in a new terminal window"""
    current_script = os.path.abspath(__file__)
    system = platform.system()
    
    try:
        if system == "Windows":
            subprocess.Popen(f'start cmd /k python "{current_script}"', shell=True)
        elif system == "Darwin":  # macOS
            subprocess.Popen(['osascript', '-e', f'tell app "Terminal" to do script "python3 \\"{current_script}\\""'])
        else:  # Linux
            subprocess.Popen(['gnome-terminal', '--', 'python3', current_script])
        
        # Exit the current process since we opened a new window
        sys.exit(0)
    except:
        # If we can't open a new window, just run in current terminal
        pass

class CIATerminal:
    def __init__(self):
        self.operation_count = 1
        self.last_news_check = 0
        self.last_market_check = 0
        self.last_date_display = 0
        self.lines_since_date = 0
        
        # News headline pools
        self.news_headlines = []
        self.last_news_fetch = 0
        
        # Expanded operation pools for variety
        self.quick_ops = [
            "Network heartbeat - Sector {grid}",
            "Satellite ping - {location}",
            "Database sync complete",
            "Firewall status nominal",
            "Encryption keys rotated",
            "Backup verification passed",
            "System health check",
            "Traffic analysis - {subnet}",
            "Signal strength optimal",
            "Connection pool refreshed",
            "Cache purged successfully",
            "Authentication tokens valid",
            "Monitoring sweep complete",
            "Network topology mapped",
            "Threat signatures updated"
        ]
        
        self.detailed_ops = [
            ("Comprehensive signals intelligence analysis initiated across seventeen monitoring stations worldwide including Menwith Hill, Waihopai, and Pine Gap facilities", "Intercepted communications span 847 unique encryption protocols with partial decryption achieved on 23% of high-priority targets", "Natural language processing algorithms detected 1,247 threat-related keywords across monitored channels in past 72 hours", "Voice pattern recognition systems identified three persons of interest with 97.3% biometric confidence matching existing database entries", "Geolocation triangulation places primary subject within 500-meter radius of strategic infrastructure in hostile territory", "Cross-referencing intercepted metadata with known terrorist financing networks reveals potential operational timeline within 96-hour window", "PRIORITY INTELLIGENCE REQUIREMENT: Real-time surveillance teams deployed to intercept subject before operational window closes"),
            
            ("Advanced persistent threat investigation analyzing sophisticated nation-state sponsored cyber intrusion across critical infrastructure networks", "Network forensics reveals previously unknown zero-day exploit targeting industrial control systems with custom malware exhibiting advanced evasion techniques", "Code signature analysis indicates development by team with access to classified vulnerability research and nation-state level resources", "Infrastructure investigation traces command and control servers through seventeen countries using advanced obfuscation and proxy techniques", "Digital fingerprinting matches specific coding patterns, encryption methods, and operational procedures to known Advanced Persistent Threat group designated APT-47", "Defensive countermeasures activated across all partner critical infrastructure including power grids, water treatment facilities, and transportation networks", "Coordination with international cyber defense organizations initiated including Five Eyes alliance, NATO Cooperative Cyber Defence Centre, and European Cyber Crime Centre", "RECOMMENDATION: Immediate diplomatic engagement through established intelligence sharing protocols and consideration of proportional cyber response measures"),
            
            ("Geospatial intelligence fusion operation commencing with integration of multi-source collection platforms including synthetic aperture radar, hyperspectral imaging, and signals intelligence", "Satellite constellation KEYHOLE-12, LACROSSE-5, and commercial imagery sources providing continuous real-time overhead surveillance of area of operations", "Ground-moving target indicator systems tracking forty-seven vehicles of interest including armored personnel carriers, mobile communications units, and suspected weapons transport", "Hyperspectral analysis reveals concealed underground facilities with electromagnetic signatures consistent with command and control infrastructure", "Change detection algorithms comparing imagery over six-month period indicate significant infrastructure development and defensive preparations", "Human intelligence assets reporting increased security presence, unusual communication patterns, and accelerated operational tempo at facility of interest", "Pattern-of-life analysis suggests imminent operational activity with estimated timeline of 48-72 hours based on historical behavioral patterns", "Intelligence assessment with confidence level HIGH forwarded to Joint Intelligence Operations Center and National Security Council for immediate action"),
            
            ("Comprehensive financial intelligence investigation targeting complex transnational money laundering operation spanning twenty-three jurisdictions across four continents", "Blockchain analysis algorithms processing over 2.3 million cryptocurrency transactions revealing sophisticated laundering scheme utilizing multiple privacy coins and mixing services", "Traditional banking records analysis covering shell company network encompassing forty-seven entities across twelve offshore financial centers", "Transaction pattern analysis utilizing artificial intelligence and machine learning algorithms indicates total monetary movement exceeding $347 million over eighteen-month period", "Correlation with known terrorist financing methods suggests potential funding for large-scale operational activities with estimated capability for major infrastructure attack", "International cooperation requested through Financial Action Task Force, Egmont Group, and bilateral intelligence sharing agreements", "Asset freezing recommendations submitted to Treasury Department, European Banking Authority, and partner financial intelligence units", "URGENT: Coordinated international law enforcement action recommended within 72-hour window to prevent completion of suspected terrorist financing operation"),
            
            ("Multi-domain behavioral analytics engine processing comprehensive social media intelligence data from global monitoring network encompassing 247 platforms and communication channels", "Advanced natural language processing and sentiment analysis algorithms analyzing 12.7 million social media posts, forum discussions, and private communications over 30-day period", "Machine learning models identifying coordinated inauthentic behavior patterns suggesting state-sponsored disinformation campaign targeting democratic institutions", "Network topology mapping reveals sophisticated bot farm infrastructure utilizing 89,000 synthetic accounts across multiple platforms with centralized command structure", "Geolocation analysis of suspicious account activity traces coordination nodes to three distinct geographical regions associated with known information warfare units", "Content analysis reveals strategic narrative themes designed to exploit existing social divisions and undermine confidence in electoral processes", "Attribution assessment with moderate-to-high confidence points to state-sponsored psychological operations unit with historical patterns matching current operational signatures", "RECOMMENDATION: Immediate platform notification, coordinated account suspension actions, and comprehensive briefing for National Security Council and Congressional oversight committees"),
            
            ("Biometric correlation system processing facial recognition data from global surveillance network encompassing 1,847 million facial images collected over 72-hour period from partner agency databases", "Advanced convolutional neural network algorithms achieving 98.7% accuracy on partial face matches even with significant occlusion, aging, or disguise attempts", "Cross-referencing biometric results with immigration databases, criminal records, Interpol notices, terrorist watch lists, and intelligence agency person-of-interest files", "Subject of primary interest identified with 96.4% confidence utilizing fusion of facial recognition, gait analysis, and voice pattern matching from multiple sensor platforms", "Real-time tracking utilizing urban surveillance camera network, mobile device geolocation, and financial transaction monitoring across metropolitan area", "Last confirmed sighting places subject entering diplomatic quarter with known associations to hostile intelligence services and history of operational activity", "Field surveillance teams notified and positioned for visual confirmation while maintaining operational security and avoiding diplomatic incidents", "CRITICAL: Subject assessed as immediate threat to national security with potential for imminent operational activity requiring immediate neutralization or apprehension"),
            
            ("Quantum cryptography vulnerability assessment examining next-generation encryption protocols and post-quantum cryptographic implementations currently protecting classified communications", "Theoretical mathematical analysis utilizing advanced supercomputing resources suggests potential weakness in lattice-based cryptographic schemes under specific attack conditions", "Distributed computing simulation running 250,000 attack scenarios against current key exchange methods using hybrid classical-quantum computational approaches", "Research collaboration with university partners, defense contractors, and international allies yielding promising attack vectors against NIST-approved post-quantum algorithms", "Estimated timeline for practical cryptographic break ranges from 18-24 months with current computational resources and 12-18 months with planned quantum computing upgrades", "Assessment indicates potential vulnerability of allied nation communications, financial networks, and critical infrastructure protected by current encryption standards", "IMMEDIATE RECOMMENDATION: Accelerated development of next-generation post-quantum security measures and coordinated transition plan for partner organizations", "Classified briefing scheduled with NSA Cryptographic Research Division, CIA Science and Technology Directorate, and Five Eyes cryptographic working group")
        ]
        
        self.progress_ops = [
            "Deep learning neural network training",
            "Cryptographic hash analysis", 
            "Satellite image processing",
            "Voice pattern recognition",
            "DNA sequence comparison",
            "Financial fraud detection",
            "Social network mapping",
            "Predictive threat modeling",
            "Behavioral analysis compilation",
            "Strategic intelligence synthesis"
        ]

    def get_timestamp(self):
        return datetime.now().strftime("[%H:%M]")
    
    def get_date(self):
        return datetime.now().strftime("%Y-%m-%d")
    
    def print_line(self, message, highlight_word=None, highlight_color=Fore.GREEN):
        timestamp = self.get_timestamp()
        if highlight_word:
            # Replace the highlight word with colored version
            colored_word = f"{highlight_color}{highlight_word}{Style.RESET_ALL}"
            message = message.replace(highlight_word, colored_word)
        
        print(f"{Fore.WHITE}{timestamp} {message}{Style.RESET_ALL}")
        self.lines_since_date += 1
    
    def show_date_header(self):
        if time.time() - self.last_date_display > 300 or self.lines_since_date > 25:  # Every 5 minutes or 25 lines
            date_str = self.get_date()
            print(f"\n{Fore.CYAN}{'='*50}")
            print(f"{Style.BRIGHT}{Fore.CYAN}OPERATIONAL DATE: {date_str}")
            print(f"{'='*50}{Style.RESET_ALL}\n")
            self.last_date_display = time.time()
            self.lines_since_date = 0
    
    def generate_fake_data(self):
        return {
            'subnet': f"10.{random.randint(1,254)}.{random.randint(1,254)}.0",
            'ip': f"{random.randint(172,192)}.{random.randint(16,31)}.{random.randint(1,255)}.{random.randint(1,254)}",
            'port': random.choice([22, 80, 443, 8080, 3389, 21, 25, 53, 110, 995, 1433, 3306]),
            'location': random.choice(["CONUS-EAST", "CONUS-WEST", "OCONUS-PAC", "EMEA-NORTH", "LATAM-SUR"]),
            'grid': f"{random.choice(['ALPHA', 'BRAVO', 'CHARLIE', 'DELTA', 'ECHO', 'FOXTROT'])}-{random.randint(10,99)}"
        }
    
    def show_progress_operation(self, operation):
        self.print_line(f"{operation}...")
        
        # Progress in stages with realistic pauses
        stages = ["INITIALIZING", "PROCESSING", "ANALYZING", "FINALIZING"]
        
        for i, stage in enumerate(stages):
            time.sleep(random.uniform(1, 3))
            percent = ((i + 1) / len(stages)) * 100
            bar_filled = "█" * int(percent // 5)
            bar_empty = "░" * (20 - int(percent // 5))
            
            # Overwrite with padding to clear previous text
            bar_line = f"{operation} [{bar_filled}{bar_empty}] {percent:.0f}% - {stage}     "
            print(f"\r{self.get_timestamp()} {Fore.WHITE}{bar_line}{Style.RESET_ALL}", end="", flush=True)
        
        print()  # New line
        
        # Final status with highlight
        final_status = random.choice(["COMPLETE", "SUCCESS", "VERIFIED", "NOMINAL"])
        self.print_line(f"{operation} - {final_status}", final_status, Fore.GREEN)
        self.lines_since_date += 2
    
    def fetch_real_data(self):
        current_time = time.time()
        
        # Fetch fresh headlines every 10 minutes
        if current_time - self.last_news_fetch > 600:
            self.news_headlines = []  # Clear old headlines
            
            # Method 1: Grab multiple BBC headlines
            try:
                response = requests.get("https://feeds.bbci.co.uk/news/world/rss.xml", timeout=8)
                if response.status_code == 200:
                    content = response.text
                    import re
                    titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>', content)
                    
                    if titles and len(titles) > 1:
                        # Get up to 8 BBC headlines (skip first one which is "BBC News")
                        for title in titles[1:9]:
                            if len(title) > 15 and not any(skip in title.upper() for skip in ['BBC NEWS', 'RSS']):
                                self.news_headlines.append(title.strip()[:120])  # Increased from 75 to 120
            except Exception as e:
                pass
            
            # Method 2: Add Reddit headlines to the pool
            try:
                response = requests.get("https://www.reddit.com/r/worldnews.json", 
                                      headers={'User-Agent': 'Intelligence-Terminal/1.0'}, timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'children' in data['data']:
                        # Get up to 6 Reddit headlines
                        reddit_count = 0
                        for post in data['data']['children']:
                            if reddit_count >= 6:
                                break
                            if 'data' in post and 'title' in post['data']:
                                title = post['data']['title']
                                if not any(skip in title.upper() for skip in ['LIVE THREAD', '/R/', 'MEGATHREAD']) and len(title) > 20:
                                    self.news_headlines.append(title[:75])
                                    reddit_count += 1
            except Exception as e:
                pass
            
            # If we got some headlines, update fetch time
            if self.news_headlines:
                self.last_news_fetch = current_time
            
            # Add fallback headlines if we got nothing
            if not self.news_headlines:
                self.news_headlines = [
                    "Global surveillance networks detect encrypted traffic surge across multiple regions",
                    "Satellite imagery confirms unusual infrastructure development in monitored zones", 
                    "Social media analysis identifies coordinated disinformation campaign targeting democratic processes",
                    "Financial intelligence reports suspicious cross-border cryptocurrency transactions exceeding $50M",
                    "Communications intercepts suggest state-sponsored cyber operations planning phase acceleration",
                    "Geospatial analysis confirms military vehicle concentrations near strategic border crossings",
                    "Human intelligence assets report increased security presence at critical infrastructure facilities"
                ]
                self.last_news_fetch = current_time
        
        # Show a random headline every 2 minutes (slowed down)
        if current_time - self.last_news_check > 120 and self.news_headlines:
            headline = random.choice(self.news_headlines)
            self.print_line(f"OSINT: {headline}", "OSINT", Fore.YELLOW)
            self.last_news_check = current_time
        
        # Market data every 3 minutes (slowed down from 90 seconds)
        if current_time - self.last_market_check > 180:
            try:
                # Try the most reliable crypto API
                response = requests.get("https://api.coinbase.com/v2/exchange-rates?currency=BTC", timeout=8)
                if response.status_code == 200:
                    data = response.json()
                    if 'data' in data and 'rates' in data['data'] and 'USD' in data['data']['rates']:
                        price = float(data['data']['rates']['USD'])
                        daily_change = random.uniform(-3.0, 3.0)
                        change_str = f"{'+' if daily_change >= 0 else ''}{daily_change:.1f}%"
                        
                        self.print_line(f"FININT: BTC ${int(price):,} ({change_str}) - Real-time market data updated", "FININT", Fore.CYAN)
                        self.last_market_check = current_time
                        return
            except Exception as e:
                pass
            
            # Try alternative crypto API
            try:
                response = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    if 'bpi' in data and 'USD' in data['bpi']:
                        price = data['bpi']['USD']['rate_float']
                        daily_change = random.uniform(-2.5, 2.5)
                        change_str = f"{'+' if daily_change >= 0 else ''}{daily_change:.1f}%"
                        
                        self.print_line(f"FININT: BTC ${int(price):,} ({change_str}) - Market surveillance active", "FININT", Fore.CYAN)
                        self.last_market_check = current_time
                        return
            except Exception as e:
                pass
            
            # Fallback market data
            price = random.randint(45000, 120000)  # Wide range for any time period
            change = random.choice(["+", "-"]) + f"{random.uniform(0.5, 4.0):.1f}%"
            self.print_line(f"FININT: BTC ${price:,} ({change}) - Market analysis systems operational", "FININT", Fore.CYAN)
            self.last_market_check = current_time
    
    def run_operation(self):
        self.show_date_header()
        fake_data = self.generate_fake_data()
        
        # Operation type probabilities - adding concatenated reports
        op_choice = random.choices(
            ['quick', 'detailed', 'scan_data', 'concatenated', 'progress', 'alert', 'data_feed'],
            weights=[20, 5, 35, 20, 10, 5, 5]
        )[0]
        
        if op_choice == 'quick':
            message = random.choice(self.quick_ops).format(**fake_data)
            if random.random() < 0.3:  # 30% chance of status highlight
                status_words = ["complete", "nominal", "passed", "valid", "optimal", "successful"]
                for word in status_words:
                    if word in message.lower():
                        self.print_line(message, word.upper(), Fore.GREEN)
                        return
            self.print_line(message)
            
        elif op_choice == 'detailed':
            op_sequence = random.choice(self.detailed_ops)
            # Only show first 3-4 lines instead of all 7-8
            lines_to_show = random.randint(3, 4)
            
            for i, line in enumerate(op_sequence[:lines_to_show]):
                if i == 0:
                    self.print_line(line)
                else:
                    time.sleep(random.uniform(0.5, 1.0))
                    # Highlight key status words
                    highlight_words = ["identified", "complete", "verified", "confirmed", "detected", "found", "activated", "transmitted"]
                    highlighted = False
                    for word in highlight_words:
                        if word in line.lower():
                            self.print_line(f"  └─ {line}", word, Fore.YELLOW)
                            highlighted = True
                            break
                    if not highlighted:
                        self.print_line(f"  └─ {line}")
        
        elif op_choice == 'concatenated':
            # Build long concatenated intelligence reports with lots of data
            intel_components = {
                'collection': [
                    f"SIGINT collection from monitoring stations MENWITH-HILL, WAIHOPAI, PINE-GAP processing {random.randint(15000,45000)} intercepts per hour",
                    f"HUMINT assets across {random.randint(47,89)} countries reporting enhanced operational tempo with {random.randint(230,890)} status updates received",
                    f"GEOINT satellite constellation including KEYHOLE-{random.randint(10,15)}, LACROSSE-{random.randint(3,7)} providing continuous overhead surveillance coverage",
                    f"MASINT sensors detecting unusual electromagnetic signatures across {random.randint(12,35)} monitoring stations with {random.randint(85,98)}% confidence",
                    f"OSINT analysis processing {random.uniform(2.1, 8.7):.1f}M social media posts, {random.randint(45000,125000)} news articles, and {random.randint(890,3400)} forum discussions"
                ],
                'targets': [
                    f"tracking {random.randint(47,189)} high-value targets across {random.randint(15,28)} operational theaters with real-time geolocation accuracy within {random.randint(5,50)} meters",
                    f"monitoring {random.randint(350,750)} persons of interest utilizing facial recognition with {random.randint(94,99)}.{random.randint(1,9)}% biometric confidence matching",
                    f"analyzing communication patterns from {random.randint(23,67)} suspected operational cells with {random.randint(15000,85000)} intercepted transmissions under cryptanalysis",
                    f"correlating financial transactions totaling ${random.randint(150,850)}M across {random.randint(23,45)} jurisdictions involving {random.randint(890,2400)} shell company entities"
                ],
                'analysis': [
                    f"quantum-enhanced cryptanalysis achieving {random.randint(78,94)}% success rate on intercepted traffic using {random.randint(512,2048)}-qubit processing arrays",
                    f"AI pattern recognition algorithms processing {random.randint(850,2500)}TB raw intelligence data with {random.randint(92,98)}.{random.randint(1,9)}% threat detection accuracy",
                    f"behavioral analytics correlating {random.uniform(1.5,8.5):.1f}M data points across {random.randint(180,480)} days revealing {random.randint(23,89)} significant anomalies",
                    f"network topology analysis mapping {random.randint(150000,850000)} nodes with {random.uniform(2.1,15.7):.1f}M active connections flagging {random.randint(47,234)} suspicious clusters"
                ],
                'assessment': [
                    f"threat correlation matrix indicates {random.randint(78,95)}% probability of coordinated activity within {random.randint(24,168)}-hour operational window",
                    f"pattern analysis suggests coordination between {random.randint(5,23)} distinct cells with estimated combined operational capability for tier-{random.randint(1,3)} infrastructure targeting",
                    f"financial flow acceleration detected with {random.randint(340,890)}% increase in suspicious transactions over past {random.randint(72,240)} hours indicating imminent operational phase",
                    f"communications frequency analysis reveals {random.randint(150,450)}% surge in encrypted traffic matching historical pre-operational signatures with {random.randint(85,97)}% confidence"
                ],
                'response': [
                    f"IMMEDIATE: rapid response teams deployed to coordinates {random.uniform(35.0,45.0):.4f}N, {random.uniform(-125.0,-75.0):.4f}W with {random.randint(15,45)}-minute ETA",
                    f"PRIORITY: asset protection protocols activated for {random.randint(12,28)} critical infrastructure facilities including power grid, water treatment, and transportation hubs",
                    f"URGENT: diplomatic channels engaged through {random.randint(5,15)} allied intelligence services for coordinated response utilizing established Article-{random.randint(3,7)} protocols",
                    f"CRITICAL: field operatives repositioned based on updated threat assessment with {random.randint(23,67)} personnel relocated to forward operating positions"
                ]
            }
            
            # Build 1 massive concatenated line with progressive typing effect
            report_parts = []
            report_parts.append(random.choice(intel_components['collection']))
            report_parts.append(random.choice(intel_components['targets']))
            report_parts.append(random.choice(intel_components['analysis']))
            report_parts.append(random.choice(intel_components['assessment']))
            report_parts.append(random.choice(intel_components['response']))
            
            # Start the line with timestamp
            current_line = f"{self.get_timestamp()} {Fore.WHITE}"
            print(current_line, end="", flush=True)
            
            # Add each part progressively with pauses
            for i, part in enumerate(report_parts):
                if i > 0:
                    current_line += " >> "
                    print(" >> ", end="", flush=True)
                    time.sleep(random.uniform(0.3, 0.8))
                
                # Type out this part
                print(part, end="", flush=True)
                time.sleep(random.uniform(0.8, 1.5))
            
            # Add final metadata
            final_metadata = f" >> Cross-correlation confidence: {random.randint(87,99)}% >> Intelligence dissemination: {'IMMEDIATE' if random.random() < 0.3 else 'PRIORITY'} >> Classification: TOP SECRET//SCI//NOFORN//{'GAMMA' if random.random() < 0.2 else 'ORCON'} >> Distribution: {'EYES ONLY' if random.random() < 0.4 else 'AUTHORIZED PERSONNEL'} >> Reference: INTEL-{random.randint(100000,999999)}-{random.randint(10,99)}"
            
            print(" >> ", end="", flush=True)
            time.sleep(random.uniform(0.3, 0.7))
            
            # Highlight key words in the metadata
            if "IMMEDIATE" in final_metadata:
                highlighted_metadata = final_metadata.replace("IMMEDIATE", f"{Fore.RED}IMMEDIATE{Fore.WHITE}")
            elif "CRITICAL" in final_metadata:
                highlighted_metadata = final_metadata.replace("CRITICAL", f"{Fore.RED}CRITICAL{Fore.WHITE}")
            elif "PRIORITY" in final_metadata:
                highlighted_metadata = final_metadata.replace("PRIORITY", f"{Fore.YELLOW}PRIORITY{Fore.WHITE}")
            else:
                highlighted_metadata = final_metadata
            
            print(highlighted_metadata, end="")
            print(f"{Style.RESET_ALL}")  # End the line
            
            self.lines_since_date += 1
            # FUBAR-style scanning data with lots of colorful technical lines
            scan_types = ['ALGORITHM', 'NETWORK', 'BIOMETRIC', 'SIGNAL', 'CRYPTO', 'FORENSIC']
            scan_type = random.choice(scan_types)
            
            self.print_line(f"SCANNING {scan_type} DATA", scan_type, Fore.CYAN)
            
            # Generate 5-12 lines of technical scanning data
            num_lines = random.randint(5, 12)
            
            for _ in range(num_lines):
                time.sleep(random.uniform(0.2, 0.8))
                
                # Mix of different technical data types
                line_type = random.choice(['hash', 'ip', 'crypto', 'bio', 'coord', 'freq', 'code'])
                
                if line_type == 'hash':
                    hash_val = ''.join(random.choices('0123456789abcdef', k=random.randint(8, 16)))
                    status = random.choice(['OK', 'VERIFIED', 'MATCH', 'DECODED'])
                    self.print_line(f"hash_{random.randint(1000,9999)}: {hash_val} - {status}", status, Fore.GREEN)
                    
                elif line_type == 'ip':
                    ip = f"{random.randint(10,192)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,254)}"
                    port = random.choice([22, 80, 443, 8080, 3389, 1433])
                    status = random.choice(['OPEN', 'FILTERED', 'SECURE', 'MONITOR'])
                    self.print_line(f"scan_ip: {ip}:{port} [{status}] rtt: {random.randint(12,450)}ms", status, Fore.YELLOW)
                    
                elif line_type == 'crypto':
                    algo = random.choice(['AES256', 'RSA4096', 'ECC521', 'ChaCha20'])
                    strength = random.randint(85, 99)
                    self.print_line(f"crypto_analysis: {algo} strength: {strength}% vuln_check: PASSED", "PASSED", Fore.GREEN)
                    
                elif line_type == 'bio':
                    confidence = random.randint(75, 98)
                    match_id = f"BIO_{random.randint(100000,999999)}"
                    self.print_line(f"biometric_scan: {match_id} confidence: {confidence}% - MATCHED", "MATCHED", Fore.CYAN)
                    
                elif line_type == 'coord':
                    lat = random.uniform(25.0, 49.0)
                    lon = random.uniform(-125.0, -65.0)
                    accuracy = random.randint(5, 50)
                    self.print_line(f"geoloc: {lat:.4f},{lon:.4f} accuracy: ±{accuracy}m CONFIRMED", "CONFIRMED", Fore.BLUE)
                    
                elif line_type == 'freq':
                    freq = random.randint(88, 2400)
                    power = random.randint(-80, -20)
                    self.print_line(f"signal_{freq}MHz: {power}dBm mod: {random.choice(['FM', 'AM', 'PSK', 'QAM'])} - INTERCEPTED", "INTERCEPTED", Fore.RED)
                    
                elif line_type == 'code':
                    func_name = random.choice(['decrypt', 'parse', 'validate', 'compress', 'analyze'])
                    result = random.choice(['SUCCESS', 'COMPLETE', 'VERIFIED', 'PROCESSED'])
                    exec_time = random.randint(12, 890)
                    self.print_line(f"exec_{func_name}(): {result} [{exec_time}ms] mem_usage: {random.randint(15,85)}%", result, Fore.GREEN)
                    
            # End with summary
            time.sleep(random.uniform(0.5, 1.0))
            total_items = random.randint(150, 850)
            flagged = random.randint(3, 25)
            self.print_line(f"SCAN COMPLETE: {total_items} items processed, {flagged} flagged for review", "COMPLETE", Fore.GREEN)
            
        elif op_choice == 'progress':
            operation = random.choice(self.progress_ops)
            self.show_progress_operation(operation)
            
        elif op_choice == 'alert':
            alerts = [
                ("PRIORITY ALERT: Anomalous network activity detected in secure zone", "ALERT", Fore.RED),
                ("WARNING: Authentication failures exceed normal threshold", "WARNING", Fore.YELLOW),
                ("NOTICE: Scheduled system maintenance in T-minus 6 hours", "NOTICE", Fore.CYAN),
                ("STATUS UPDATE: All monitoring systems operating within normal parameters", "STATUS", Fore.GREEN),
                ("THREAT ASSESSMENT: Elevated risk level maintained for financial sector", "THREAT", Fore.RED)
            ]
            alert_msg, highlight, color = random.choice(alerts)
            self.print_line(alert_msg, highlight, color)
            
        elif op_choice == 'data_feed':
            self.fetch_real_data()
    
    def display_startup(self):
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"{Fore.RED}{Style.BRIGHT}")
        print("CLASSIFIED INTELLIGENCE OPERATIONS TERMINAL")
        print("UNAUTHORIZED ACCESS STRICTLY PROHIBITED")
        print("SECURITY CLEARANCE: TOP SECRET//SCI//NOFORN")
        print("DEFENSE INTELLIGENCE AGENCY - JOINT OPERATIONS CENTER")
        print(f"{Style.RESET_ALL}\n")
        
        time.sleep(1)
        
        startup_sequence = [
            ("Booting secure kernel", "SUCCESS", Fore.GREEN),
            ("Loading cryptographic modules", "LOADED", Fore.GREEN),
            ("Establishing encrypted channels", "CONNECTED", Fore.GREEN),
            ("Authenticating user credentials", "VERIFIED", Fore.GREEN),
            ("Initializing monitoring protocols", "ACTIVE", Fore.GREEN)
        ]
        
        for msg, status, color in startup_sequence:
            self.print_line(f"{msg}...", status, color)
            time.sleep(random.uniform(0.5, 1.2))
        
        print(f"\n{Fore.CYAN}{Style.BRIGHT}SYSTEM READY - BEGINNING OPERATIONS MONITORING{Style.RESET_ALL}\n")
        time.sleep(1)
    
    def run(self):
        try:
            self.display_startup()
            
            while True:
                self.run_operation()
                
                # Realistic variable delays
                delay_type = random.choices(['quick', 'normal', 'long'], weights=[20, 60, 20])[0]
                
                if delay_type == 'quick':
                    delay = random.uniform(1, 3)
                elif delay_type == 'normal':
                    delay = random.uniform(3, 8)
                else:  # long pause for realism
                    delay = random.uniform(8, 20)
                
                time.sleep(delay)
                
        except KeyboardInterrupt:
            print(f"\n\n{Fore.RED}[SYSTEM SHUTDOWN INITIATED]{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}[SECURE CONNECTION TERMINATED]{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[OPERATIONAL LOG ARCHIVED]{Style.RESET_ALL}")

if __name__ == "__main__":
    # Check if we should open in new terminal (only if not already launched)
    if len(sys.argv) == 1 and "LAUNCHED_FROM_SCRIPT" not in os.environ:
        os.environ["LAUNCHED_FROM_SCRIPT"] = "1"
        open_new_terminal()
    else:
        # We're in the new terminal or running directly
        terminal = CIATerminal()
        terminal.run()