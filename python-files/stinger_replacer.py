import os
import re
from datetime import datetime

def identify_files():
    """Εύρεση αρχείων playlist και διαφημίσεων"""
    txt_files = [f for f in os.listdir() if f.lower().endswith('.txt')]
    
    playlist_file = None
    ads_file = None
    
    for file in txt_files:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Playlist: Περιέχει "STINGER" και "END OF HOUR PLAYLIST"
            if 'STINGER' in content and 'END OF HOUR PLAYLIST' in content:
                playlist_file = file
            # Ads: Περιέχει γραμμές με μόνο ώρα (π.χ. "07:35")
            elif re.search(r'^\d{2}:\d{2}$', content, re.MULTILINE):
                ads_file = file
                
    return playlist_file, ads_file

def process_files(playlist_file, ads_file):
    """Επεξεργασία αρχείων και αντικατάσταση STINGER"""
    # 1. Ομαδοποίηση δεδομένων ανά ώρα από το αρχείο διαφημίσεων
    hour_pattern = re.compile(r'^\d{2}:\d{2}$')
    hours_data = {}
    current_hour = None
    
    with open(ads_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if hour_pattern.match(line):
                current_hour = line
                hours_data[current_hour] = []
            elif current_hour and line:
                hours_data[current_hour].append(line)
    
    # 2. Επεξεργασία playlist
    output_lines = []
    current_hour_playlist = None
    stinger_count = 0
    
    with open(playlist_file, 'r', encoding='utf-8') as f:
        for line in f:
            line_stripped = line.strip()
            
            # Ανίχνευση ώρας
            if hour_pattern.match(line_stripped):
                current_hour_playlist = line_stripped
                stinger_count = 0
                output_lines.append(line.rstrip())  # Διατήρηση κενών
            
            # Ανίχνευση STINGER (με/χωρίς κενά)
            elif "STINGER" in line_stripped:
                stinger_count += 1
                
                if current_hour_playlist:
                    # 1ο STINGER: ίδια ώρα
                    if stinger_count == 1:
                        if current_hour_playlist in hours_data:
                            output_lines.extend(hours_data[current_hour_playlist])
                        else:
                            output_lines.append("STINGER")
                    
                    # 2ο STINGER: επόμενη ώρα :35
                    elif stinger_count == 2:
                        hour_part = current_hour_playlist.split(':')[0]
                        next_hour = f"{hour_part}:35"
                        
                        if next_hour in hours_data:
                            output_lines.extend(hours_data[next_hour])
                        else:
                            output_lines.append("STINGER")
                else:
                    output_lines.append(line_stripped)
            
            else:
                output_lines.append(line_stripped)
    
    # 3. Αποθήκευση νέου αρχείου με ημερομηνία
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"PLAYLIST_{timestamp}.TXT"
    
    with open(output_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))
    
    return output_filename

# Κύριο πρόγραμμα
if __name__ == "__main__":
    playlist, ads = identify_files()
    
    if not playlist or not ads:
        print("Δεν βρέθηκαν τα απαραίτητα αρχεία!")
        print("Βεβαιωθείτε ότι υπάρχουν αρχεία .txt με:")
        print("- Playlist: 'STINGER' και 'END OF HOUR PLAYLIST'")
        print("- Διαφημίσεις: γραμμές με ώρες (π.χ. '07:35')")
    else:
        print(f"Βρέθηκε playlist: {playlist}")
        print(f"Βρέθηκε αρχείο διαφημίσεων: {ads}")
        
        result_file = process_files(playlist, ads)
        print(f"Ολοκληρώθηκε! Το νέο playlist αποθηκεύτηκε στο: {result_file}")
