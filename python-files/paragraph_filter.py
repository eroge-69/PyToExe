import os
import re

# =============================================
# ||     Keyword-Based Paragraph Extractor     ||
# =============================================

def extract_paragraphs_with_keywords(file_path, keywords):
    if not os.path.isfile(file_path):
        print("\033[91m[ERROR]\033[0m File not found: {}".format(file_path))
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Determine paragraph separator based on file extension
    is_html = file_path.lower().endswith('.html')
    if is_html:
        paragraphs = re.split(r'(</pre></div>)', text, flags=re.IGNORECASE)
    else:
        paragraphs = re.split(r'(?:\n\s*\n)|(?:\n-{3,}\n)', text)

    count_mode = input("\033[94mCount keyword only once per paragraph? (yes/no):\033[0m ").strip().lower()
    count_once = count_mode in ["yes", "y"]

    match_all_keywords = input("\033[94mShould a paragraph contain ALL keywords to match? (yes/no):\033[0m ").strip().lower() in ["yes", "y"]

    matched_paragraphs = []
    keyword_total_count = 0

    if is_html:
        combined_paragraphs = []
        i = 0
        while i < len(paragraphs):
            if i + 1 < len(paragraphs) and re.match(r'</pre></div>', paragraphs[i+1], re.IGNORECASE):
                combined = paragraphs[i].strip() + paragraphs[i+1]
                combined_paragraphs.append(combined)
                i += 2
            else:
                combined_paragraphs.append(paragraphs[i].strip())
                i += 1
        paragraphs = combined_paragraphs

    for para in paragraphs:
        clean_para = para.strip()
        keyword_matches = {kw: re.findall(re.escape(kw), clean_para, re.IGNORECASE) for kw in keywords}

        if match_all_keywords:
            if all(matches for matches in keyword_matches.values()):
                keyword_total_count += 1 if count_once else sum(len(m) for m in keyword_matches.values())
                matched_paragraphs.append(clean_para)
        else:
            if any(matches for matches in keyword_matches.values()):
                keyword_total_count += 1 if count_once else sum(len(m) for m in keyword_matches.values())
                matched_paragraphs.append(clean_para)

    if not matched_paragraphs:
        print("\033[93m[INFO]\033[0m No paragraphs found containing the specified keyword(s).")
        return

    separator = "\n" + "-" * 68 + "\n"
    output_text = separator.join(matched_paragraphs)
    output_text += "\n\nTotal occurrences of keywords: {}\n".format(keyword_total_count)

    base_dir = os.path.dirname(os.path.abspath(file_path))
    output_filename = "error.html" if is_html else "error.txt"
    output_path = os.path.join(base_dir, output_filename)

    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(output_text)

    print("\033[92m[SUCCESS]\033[0m Matching paragraphs saved to: {}".format(output_path))
    print("\033[96m[STATS]\033[0m Total paragraphs matched: {}".format(len(matched_paragraphs)))
    print("\033[96m[STATS]\033[0m Total occurrences of keywords: {}".format(keyword_total_count))

# ===============================
# ||        Main Entry         ||
# ===============================

if __name__ == "__main__":
    file_path = input("\033[95mEnter path to text file (or HTML file):\033[0m ").strip()
    keywords_input = input("\033[95mEnter keyword(s) to search (comma-separated):\033[0m ").strip()
    keywords = [kw.strip() for kw in keywords_input.split(',') if kw.strip()]
    extract_paragraphs_with_keywords(file_path, keywords)
