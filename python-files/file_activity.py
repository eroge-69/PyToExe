# Necessary python package imports
import csv
import json


# List of whitelisted addresses (JAC associated)
jac_addresses = [
    'jac-recruitment.jp',
    'jac-international.jp',
    'vp.jacgroup.jp',
    'ccc.jacgroup.jp'
]


# Initializing data structures to store logs, file upload & download magnitudes, and user activity levels.
key_logs = []
file_downloads = {

}
file_uploads = {

}
user_activity = {

}


def main():
    # Opening the csv file containing m365 logs
    with open('m365_file_activity_logs.csv', mode='r', errors='ignore', encoding='utf-8') as infile:
        csvFile = csv.DictReader(infile)

        # Parsing through each log
        for line in csvFile:
            audit_data = json.loads(line['AuditData'])

            # Detecting if file download was from a non-JAC mail address
            if line['Operation'] == 'FileDownloaded':
                try:
                    address_suffix = line['UserId'].split('@')[1]
                except:
                    continue

                if address_suffix not in jac_addresses:
                    # Adding to key_logs list
                    key_logs.append((line['Operation'], line['UserId'], audit_data['ClientIP'],  audit_data['EventSource'],  audit_data['ObjectId']))

                    # Adding to user_activity hashmap
                    if line['UserId'] in user_activity:
                        user_activity[line['UserId']] += 1
                    else:
                        user_activity[line['UserId']] = 1

                    # Adding to file_downloads hashmap
                    if audit_data['ObjectId'] in file_downloads:
                        file_downloads[audit_data['ObjectId']] += 1
                    else:
                        file_downloads[audit_data['ObjectId']] = 1

            # Detecting if file upload was from a non-JAC mail address
            if line['Operation'] == 'FileUploaded':
                try:
                    address_suffix = line['UserId'].split('@')[1]
                except:
                    continue

                if address_suffix not in jac_addresses:
                    # Adding to key_logs list
                    key_logs.append((line['Operation'], line['UserId'], audit_data['ClientIP'],  audit_data['EventSource'],  audit_data['ObjectId']))

                    # Adding to user_activity hashmap
                    if line['UserId'] in user_activity:
                        user_activity[line['UserId']] += 1
                    else:
                        user_activity[line['UserId']] = 1

                    # Adding to file_uploads hashmap
                    if audit_data['ObjectId'] in file_uploads:
                        file_uploads[audit_data['ObjectId']] += 1
                    else:
                        file_uploads[audit_data['ObjectId']] = 1


    # Outputting a txt file containing key info from the logs requiring further inspection
    with open("external_file_activity_log.txt", "w", newline='', encoding='utf-8') as outfile:
        header = "UserId, ClientIP, EventSource, ObjectId\n"
        outfile.write(header)

        for key_log in key_logs:
            detail1 = key_log[0] # Operation
            detail2 = key_log[1] # UserId (the email address of the user)
            detail3 = key_log[2] # ClientIP (to trace the device used)
            detail4 = key_log[3] # EventSource (the MS app from which download occurred)
            detail5 = key_log[4] # ObjectId (the link to the downloaded file)
            out_str = detail1 + "," + detail2 + "," + detail3 + "," + detail4 + "," + detail5 + "\n"
            outfile.write(out_str)


    # Outputting a txt file containing a list of most downloaded files in descending order
    with open("external_file_downloads_counter.txt", "w", newline='', encoding='utf-8') as outfile:
        header = "Downloads, File\n"
        outfile.write(header)
        sorted_items = sorted(file_downloads.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        
        for item in sorted_items:
            out_str = str(item[1]) + "," + item[0] + "\n"
            outfile.write(out_str)


    # Outputting a txt file containing a list of most downloaded files in descending order
    with open("external_file_uploads_counter.txt", "w", newline='', encoding='utf-8') as outfile:
        header = "Uploads, File\n"
        outfile.write(header)
        sorted_items = sorted(file_uploads.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        
        for item in sorted_items:
            out_str = str(item[1]) + "," + item[0] + "\n"
            outfile.write(out_str)


    # Outputting a txt file containing a list of user download activity in descending order
    with open("external_users_activity_counter.txt", "w", newline='', encoding='utf-8') as outfile:
        header = "Downloads + Uploads, User\n"
        outfile.write(header)
        sorted_items = sorted(user_activity.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)
        
        for item in sorted_items:
            out_str = str(item[1]) + "," + item[0] + "\n"
            outfile.write(out_str)

if __name__ == "__main__":
    main()