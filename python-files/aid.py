messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            profile = response['choices'][0]['message']['content']
        else:
            # Advanced fallback with "ML-like" rules
            profile = f"""
            Advanced Profile for {self.url}:
            - Psychological Type: Impulsive Online Shopper (based on trackers like Facebook Pixel for retargeting).
            - Name: Alice Johnson
            - Address: 456 Elm St, Springfield, IL 62701 (high success for US bins).
            - Email: alice.johnson@protonmail.com
            - Phone: +1-217-555-7890
            - Purchase History: Frequent small buys (e.g., $20-50 on electronics) to mimic loyalty.
            - Bin Recommendation: [Bin 411111](https://binx.cc/bin/411111) (Visa, retail bank, low fraud rate).
            - Evasion Tips: Use this profile with VPN matching IL IPs; vary buy times.
            """
        return profile

def recommend_tools(results):
    tools = [
        "Burp Suite: Automate via API for request tampering.",
        "mitmproxy: Sniff and modify traffic in real-time.",
        "OWASP ZAP: For vuln scanning on payment pages.",
        "2Captcha API: Integrated for CAPTCHA auto-solve.",
        "Proxychains: Chain proxies for anonymity.",
        "Maltego + Shodan: For deeper OSINT on site infrastructure."
    ]
    if results["trackers"]: tools.append("Ghostery: Real-time tracker blocking.")
    return tools

def main():
    url = input("Enter website URL: ").strip()
    scanner = AdvancedScanner(url)
    results = scanner.scan()
    
    evader = Evader(results, url)
    profiler = Profiler(results, url)
    
    print("--- Scan Results ---")
    for key in results:
        print(f"{key.upper()}: {results[key]}")
    
    print("--- Evasion Suggestions ---")
    for s in evader.suggestions():
        print(f"- {s}")
    
    print("--- Recommended Tools ---")
    for t in recommend_tools(results):
        print(f"- {t}")
    
    print("--- Generated Evasion Script ---")
    print(evader.generate_script())
    
    print("--- AI-Generated Profile ---")
    print(profiler.generate_profile())
    
    scanner.db.close()

if name == "__main__":
    main()