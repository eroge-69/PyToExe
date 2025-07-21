import os
import re
import sys # 'sys' मॉड्यूल को import करें

# --- PyInstaller द्वारा बनाए गए EXE के लिए सही पथ निर्धारित करें ---
# यह कोड पता लगाता है कि स्क्रिप्ट को PyInstaller द्वारा बनाई गई EXE फ़ाइल के रूप में चलाया जा रहा है या नहीं।
# यदि हाँ, तो यह EXE फ़ाइल की डायरेक्टरी को 'application_path' के रूप में सेट करता है।
# यदि नहीं (यानी, इसे एक सामान्य .py स्क्रिप्ट के रूप में चलाया जा रहा है), तो यह वर्तमान स्क्रिप्ट फ़ाइल की डायरेक्टरी को सेट करता है।
if getattr(sys, 'frozen', False):
    # यदि PyInstaller द्वारा संकलित EXE के रूप में चल रहा है
    application_path = os.path.dirname(sys.executable)
else:
    # यदि सामान्य .py स्क्रिप्ट के रूप में चल रहा है
    application_path = os.path.dirname(os.path.abspath(__file__))
# --- PyInstaller लॉजिक समाप्त ---

# 'Working Folder' का पूरा पथ अब 'application_path' पर आधारित होगा।
# यह सुनिश्चित करता है कि 'Working Folder' हमेशा EXE फ़ाइल के साथ उसी डायरेक्टरी में हो।
target_folder_path = os.path.join(application_path, 'Working Folder')

# सुनिश्चित करें कि 'Working Folder' मौजूद है।
if not os.path.isdir(target_folder_path):
    # यदि फोल्डर मौजूद नहीं है, तो उसे बनाएं।
    # 'exist_ok=True' यह सुनिश्चित करता है कि यदि फोल्डर पहले से मौजूद है तो कोई त्रुटि न हो।
    try:
        os.makedirs(target_folder_path, exist_ok=True)
        print(f"'{target_folder_path}' फोल्डर बनाया गया है।")
        print("कृपया इस फोल्डर में अपनी फ़ाइलें डालें जिनका नाम आप बदलना चाहते हैं।")
        print("फ़ाइलें डालने के बाद, नाम बदलने की प्रक्रिया शुरू करने के लिए इस प्रोग्राम को दोबारा चलाएं।")
    except OSError as e:
        print(f"फोल्डर '{target_folder_path}' बनाने में त्रुटि हुई: {e}")
    sys.exit() # फोल्डर बनाने के बाद प्रोग्राम से बाहर निकलें, ताकि यूज़र फ़ाइलें डाल सके।
else:
    # यदि फोल्डर मौजूद है, तो नाम बदलने की प्रक्रिया शुरू करें।
    print(f"फोल्डर '{target_folder_path}' में नाम बदलने की प्रक्रिया शुरू हो रही है...")
    renamed_count = 0

    # फोल्डर में मौजूद सभी फाइलों की लिस्ट प्राप्त करें।
    for filename in os.listdir(target_folder_path):
        # रेगुलर एक्सप्रेशन पैटर्न को परिभाषित करें:
        # यह पैटर्न 'prefix_number.extension' फॉर्मेट वाली फ़ाइलों को मैच करने के लिए डिज़ाइन किया गया है।
        # (.+?)   : फ़ाइल नाम का कोई भी कैरेक्टर (नॉन-ग्रीडी) जो अंडरस्कोर से पहले आता है (यह प्रीफिक्स है)।
        # _       : अंडरस्कोर कैरेक्टर।
        # (\d+)   : एक या अधिक डिजिट्स (0-9) जो अंडरस्कोर के बाद आते हैं (यह नंबर है)।
        # \.      : डॉट कैरेक्टर (एक्सटेंशन से पहले)।
        # (.*?)$  : फ़ाइल एक्सटेंशन (नॉन-ग्रीडी, अंत तक)।
        match = re.match(r'(.+?)_(\d+)\.(.*?)$', filename, re.IGNORECASE)

        if match: # अगर फ़ाइल नाम पैटर्न से मैच होता है
            try:
                # रेगुलर एक्सप्रेशन से नंबर पार्ट (दूसरा ग्रुप) और एक्सटेंशन (तीसरा ग्रुप) निकालें।
                number_part = match.group(2)
                original_extension = match.group(3)

                # नया फ़ाइल नाम बनाएं: '1.jpg', '2.pdf', '3.txt' आदि।
                new_filename = f"{number_part}.{original_extension}"

                # पूरी पुरानी फ़ाइल का पथ और नई फ़ाइल का पथ बनाएं।
                old_file_path = os.path.join(target_folder_path, filename)
                new_file_path = os.path.join(target_folder_path, new_filename)

                # फ़ाइल का नाम बदलें, लेकिन तभी जब पुराना और नया नाम अलग हो।
                if old_file_path != new_file_path:
                    os.rename(old_file_path, new_file_path)
                    print(f"'{filename}' का नाम बदलकर '{new_filename}' कर दिया गया।")
                    renamed_count += 1
                else:
                    # यदि फ़ाइल का नाम पहले से ही सही फॉर्मेट में है (जैसे 1.jpg), तो उसे नज़रअंदाज़ करें।
                    print(f"'{filename}' का नाम बदलने की आवश्यकता नहीं है (पहले से ही सही फॉर्मेट में)।")

            except Exception as e:
                # नाम बदलते समय किसी भी त्रुटि को पकड़ें और प्रिंट करें।
                print(f"'{filename}' का नाम बदलते समय एक त्रुटि हुई: {e}")
        else:
            # अगर फ़ाइल नाम पैटर्न से मैच नहीं करता, तो उसे नज़रअंदाज़ करें।
            print(f"'{filename}' को नजरअंदाज किया गया क्योंकि यह अपेक्षित नाम पैटर्न से मेल नहीं खाता।")

    print(f"\nकुल {renamed_count} फ़ाइलों का नाम सफलतापूर्वक बदला गया।")
    print("प्रक्रिया पूरी हुई।")