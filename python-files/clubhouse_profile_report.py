# clubhouse_profile_report.py

import csv
import json

def load_profiles_from_csv(file_path):
    profiles = []
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            profiles.append(row)
    return profiles

def generate_report(profiles):
    report = {
        'total_profiles': len(profiles),
        'verified_users': 0,
        'followers_distribution': {},
        'top_users_by_followers': []
    }

    for profile in profiles:
        followers = int(profile.get('followers', 0))
        verified = profile.get('verified', 'false').lower() == 'true'

        if verified:
            report['verified_users'] += 1

        # Followers distribution
        if followers < 100:
            key = '<100'
        elif followers < 1000:
            key = '100-999'
        elif followers < 10000:
            key = '1K-9.9K'
        else:
            key = '10K+'

        if key not in report['followers_distribution']:
            report['followers_distribution'][key] = 0
        report['followers_distribution'][key] += 1

    # Sort top users
    sorted_profiles = sorted(profiles, key=lambda x: int(x.get('followers', 0)), reverse=True)
    report['top_users_by_followers'] = sorted_profiles[:5]

    return report

def save_report_to_json(report, output_path):
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=4)

def main():
    input_csv = 'clubhouse_profiles.csv'  # Replace with your actual CSV file
    output_json = 'clubhouse_profile_report.json'

    profiles = load_profiles_from_csv(input_csv)
    report = generate_report(profiles)
    save_report_to_json(report, output_json)

    print("Report generated and saved to", output_json)

if __name__ == '__main__':
    main()
