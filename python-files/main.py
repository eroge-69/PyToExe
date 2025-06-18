# Necessary python package imports
import csv
import json
import joblib


# List of whitelisted addresses (JAC associated)
jac_addresses = [
    'jac-recruitment.jp',
    'jac-international.jp',
    'vp.jacgroup.jp',
    'ccc.jacgroup.jp'
]


# Initializing output jsons
jac = {

}
non_jac = {

}


# Filename classification ML
vectorizer, clf = joblib.load('clf.pkl')

def ml_classification(filepath):
    filename = filepath.rsplit("/", 1)[1].rsplit(".",1)[0]
    X_new = vectorizer.transform([filename])
    prediction = clf.predict(X_new)
    return prediction[0]
    

def main():
    # Opening the csv file containing m365 logs
    with open('m365_logs.csv', mode='r', errors='ignore', encoding='utf-8') as infile:
        csvFile = csv.DictReader(infile)

        # Parsing through each log
        for line in csvFile:
            audit_data = json.loads(line['AuditData'])

            # Detecting file download operation
            if line['Operation'] == 'FileDownloaded':
                try:
                    address_suffix = line['UserId'].split('@')[1]
                except:
                    continue
  
                # Detecting if file download was from a non-JAC mail address
                if address_suffix not in jac_addresses and not line['UserId'].endswith("rpo-solutions.com#ext#@jacrecruitmentjp.onmicrosoft.com"):
                    # If user not in output dict, add them in
                    if line['UserId'] not in non_jac:
                        init = {
                            'file_downloads_count': 0,
                            'file_downloads': [],
                            'file_uploads_count': 0,
                            'file_uploads': [],
                            'IPs_used_count': 0,
                            'IPs_used': []
                        }
                        non_jac[line['UserId']] = init

                    # Append data from current log to output dict
                    non_jac[line['UserId']]['file_downloads_count'] += 1
                    file_download_info = {
                        'time': line['CreationDate'],
                        'platform': audit_data['AppAccessContext']['ClientAppName'],
                        'URL': audit_data['ObjectId'],
                        'filename': audit_data['ObjectId'].rsplit("/", 1)[1],
                        'filename_classification': ml_classification(audit_data['ObjectId']),
                        'IP_used': audit_data['ClientIP']
                    }
                    non_jac[line['UserId']]['file_downloads'].append(file_download_info)
                    if audit_data['ClientIP'] not in non_jac[line['UserId']]['IPs_used']:
                        non_jac[line['UserId']]['IPs_used'].append(audit_data['ClientIP'])
                        non_jac[line['UserId']]['IPs_used_count'] += 1
                    
                else:    
                     # If user not in output dict, add them in
                    if line['UserId'] not in jac:
                        init = {
                            'file_downloads_count': 0,
                            'file_downloads': [],
                            'file_uploads_count': 0,
                            'file_uploads': [],
                            'IPs_used_count': 0,
                            'IPs_used': []
                        }
                        jac[line['UserId']] = init

                    # Append data from current log to output dict
                    jac[line['UserId']]['file_downloads_count'] += 1
                    file_download_info = {
                        'time': line['CreationDate'],
                        'platform': audit_data['AppAccessContext']['ClientAppName'],
                        'URL': audit_data['ObjectId'],
                        'filename': audit_data['ObjectId'].rsplit("/", 1)[1],
                        'filename_classification': ml_classification(audit_data['ObjectId']),
                        'IP_used': audit_data['ClientIP']
                    }
                    jac[line['UserId']]['file_downloads'].append(file_download_info)
                    if audit_data['ClientIP'] not in jac[line['UserId']]['IPs_used']:
                        jac[line['UserId']]['IPs_used'].append(audit_data['ClientIP'])
                        jac[line['UserId']]['IPs_used_count'] += 1


            # Detecting file upload operation
            if line['Operation'] == 'FileUploaded' and line['UserId'] != 'app@sharepoint':
                try:
                    address_suffix = line['UserId'].split('@')[1]
                except:
                    continue
  
                # Detecting if file upload was from a non-JAC mail address
                if address_suffix not in jac_addresses:
                    # If user not in output dict, add them in
                    if line['UserId'] not in non_jac:
                        init = {
                            'file_downloads_count': 0,
                            'file_downloads': [],
                            'file_uploads_count': 0,
                            'file_uploads': [],
                            'IPs_used_count': 0,
                            'IPs_used': []
                        }
                        non_jac[line['UserId']] = init

                    # Append data from current log to output dict
                    non_jac[line['UserId']]['file_uploads_count'] += 1
                    file_upload_info = {
                        'time': line['CreationDate'],
                        'platform': audit_data['AppAccessContext']['ClientAppName'],
                        'URL': audit_data['ObjectId'],
                        'filename': audit_data['ObjectId'].rsplit("/", 1)[1],
                        'filename_classification': ml_classification(audit_data['ObjectId']),
                        'IP_used': audit_data['ClientIP']
                    }
                    non_jac[line['UserId']]['file_uploads'].append(file_upload_info)
                    if audit_data['ClientIP'] not in non_jac[line['UserId']]['IPs_used']:
                        non_jac[line['UserId']]['IPs_used'].append(audit_data['ClientIP'])
                        non_jac[line['UserId']]['IPs_used_count'] += 1
                    
                else:    
                     # If user not in output dict, add them in
                    if line['UserId'] not in jac:
                        init = {
                            'file_downloads_count': 0,
                            'file_downloads': [],
                            'file_uploads_count': 0,
                            'file_uploads': [],
                            'IPs_used_count': 0,
                            'IPs_used': []
                        }
                        jac[line['UserId']] = init

                    # Append data from current log to output dict
                    jac[line['UserId']]['file_uploads_count'] += 1
                    file_upload_info = {
                        'time': line['CreationDate'],
                        'platform': audit_data['AppAccessContext']['ClientAppName'],
                        'URL': audit_data['ObjectId'],
                        'filename': audit_data['ObjectId'].rsplit("/", 1)[1],
                        'filename_classification': ml_classification(audit_data['ObjectId']),
                        'IP_used': audit_data['ClientIP']
                    }
                    jac[line['UserId']]['file_uploads'].append(file_upload_info)
                    if audit_data['ClientIP'] not in jac[line['UserId']]['IPs_used']:
                        jac[line['UserId']]['IPs_used'].append(audit_data['ClientIP'])
                        jac[line['UserId']]['IPs_used_count'] += 1



    #with open("jac.json", "w", encoding="UTF-8") as file:
        # Sort based on reverse of Values
        #val_based_rev = {k: v for k, v in sorted(jac.items(), key=lambda item: item[1]["file_downloads_count"], reverse=True)}
        #json.dump(val_based_rev, file, indent=4)

    with open("non-jac.json", "w", encoding="UTF-8") as file:
        # Sort based on reverse of Values
        val_based_rev = {k: v for k, v in sorted(non_jac.items(), key=lambda item: item[1]["file_downloads_count"], reverse=True)}
        json.dump(val_based_rev, file, indent=4)

    with open("critical_logs.txt", "w", encoding="UTF-8") as outfile:
        val_based_rev = {k: v for k, v in sorted(non_jac.items(), key=lambda item: item[1]["file_downloads_count"], reverse=True)}
        
        outstr = ""

        for email, details in val_based_rev.items():
            critical_counter = 0
            other_counter = 0
            outstr += "ユーザー名： " + email +  "\n\n" + "機密ファイルダウンロード:" + "\n"
            for file in details['file_downloads']:
                if file['filename_classification'] == 1.0:
                    critical_counter += 1
                    for k, v in file.items():
                        outstr +=  "\n" + str(k) + ": " + str(v)
                    outstr += "\n"

            if critical_counter == 0:
                outstr += "このユーザーは機密ファイルをダウンロードされませんでした。\n"

            outstr += "\n他のダウンロード:" + "\n"
            for file in details['file_downloads']:
                if file['filename_classification'] == 0.0:
                    other_counter += 1
                    for k, v in file.items():
                        outstr +=  "\n" + str(k) + ": " + str(v)
                    outstr += "\n"

            if other_counter == 0:
                outstr += "他のファイルのダウンロードはありません。\n"

            outstr += "---------------------------------------------------------------------------------" + "\n" + "\n"

        outfile.write(outstr)

if __name__ == "__main__":
    main()