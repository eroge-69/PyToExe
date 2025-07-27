import os
import re
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TALB, TPE1, TPE2, error, TRCK, APIC, TDRC, TYER

# Supported image formats for album art
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png']

def set_album_artist(folder):
    """Sets the Album Artist tag (TPE2) based on the presence of different artists in an album."""
    for root, dirs, files in os.walk(folder):
        # Use a set to track unique artists in the current album
        unique_artists = set()
        mp3_files = []

        # First pass: Collect artists and mp3 files
        for file in files:
            if file.lower().endswith('.mp3'):
                mp3_file_path = os.path.join(root, file)
                mp3_files.append(mp3_file_path)
                try:
                    # Load the MP3 file
                    audio = MP3(mp3_file_path, ID3=ID3)
                    # Add the artist to the set of unique artists
                    artist = audio.get('TPE1')
                    if artist:
                        unique_artists.add(artist.text[0])  # Get the artist name as a string
                except error:
                    print(f"Error reading {mp3_file_path}")
                except Exception as e:
                    print(f"Unexpected error reading {mp3_file_path}: {e}")

        # Determine the Album Artist based on unique artists
        album_artist = "Various Artists" if len(unique_artists) > 1 else unique_artists.pop() if unique_artists else None
        
        # Second pass: Set the Album Artist for each mp3 file
        for mp3_file_path in mp3_files:
            try:
                audio = MP3(mp3_file_path, ID3=ID3)
                if album_artist:
                    audio['TPE2'] = TPE2(encoding=3, text=album_artist)  # Set Album Artist
                    audio.save()  # Save changes
                    print(f"Set Album Artist for {mp3_file_path} to '{album_artist}'")
            except error:
                print(f"Error updating {mp3_file_path}")
            except Exception as e:
                print(f"Unexpected error updating {mp3_file_path}: {e}")
                
def find_image(folder):
    """Finds an image file in the given folder (preferably 'cover.jpg' or 'folder.jpg')."""
    for file in os.listdir(folder):
        if file.lower() in ['cover.jpg', 'folder.jpg']:
            return os.path.join(folder, file)
    for file in os.listdir(folder):
        if file.lower().endswith(tuple(IMAGE_EXTENSIONS)):
            return os.path.join(folder, file)
    return None

def get_year_from_tags(audio):
    """Extracts the year from the ID3 tags (TDRC or TYER)."""
    if 'TDRC' in audio.tags:
        return audio.tags['TDRC'].text[0]  # Get the first year if multiple are present
    elif 'TYER' in audio.tags:
        return audio.tags['TYER'].text[0]
    return None

def clear_year_tags(audio):
    """Clears the Year tag (TDRC or TYER) from the audio file."""
    if 'TDRC' in audio.tags:
        del audio.tags['TDRC']
    if 'TYER' in audio.tags:
        del audio.tags['TYER']

def set_mp3_tags(file_path, artist, album, title, track_number, image_data, clear_year=False):
    """Sets the artist, album, title, track number, and album art tags for an MP3 file."""
    try:
        audio = MP3(file_path, ID3=ID3)
        
        # Add ID3 tag if not present
        if audio.tags is None:
            audio.add_tags()

        # Set the title, artist, album, and track number
        audio['TIT2'] = TIT2(encoding=3, text=title)  # Track title
        audio['TPE1'] = TPE1(encoding=3, text=artist) # Artist
        audio['TALB'] = TALB(encoding=3, text=album)  # Album
        if track_number:
            audio['TRCK'] = TRCK(encoding=3, text=str(track_number))  # Track number

        # Clear the Year tag if specified
        if clear_year:
            clear_year_tags(audio)

        # Add album art if image data is available
        if image_data:
            audio['APIC'] = APIC(
                encoding=3,  # 3 is for UTF-8
                mime='image/jpeg',  # Assuming it's a JPEG, but this can be changed
                type=3,  # 3 is for the album cover front
                desc='Cover',
                data=image_data
            )

        # Save the changes to the file
        audio.save()
        print(f"Tags set for {file_path}")

    except Exception as e:
        print(f"Error setting tags for {file_path}: {e}")

def process_mp3_file(file_path, folder_name, image_path, clear_year):
    """Process a single MP3 file, setting tags based on the filename and folder name."""
    filename = os.path.basename(file_path)
    # Regular expression to match files like "10. Claudio Simonetti - Confusion (Reprise).mp3"
    # or "4. Jae Hyung - I'll be here - lost.mp3"
    match = re.match(r'(\d+)\.\s*(.+?)\s*-\s*(.+)\s*-\s*(.+)\.mp3', filename)
    
    if match:
        # For filenames with two hyphens (track. artist - partial title - full title)
        track_number = match.group(1)
        artist = match.group(2)
        title = f"{match.group(3)} - {match.group(4)}"  # Combine the two title parts
    else:
        # Try the original pattern for single-hyphen filenames
        match = re.match(r'(\d+)\.\s*(.+?)\s*-\s*(.+)\.mp3', filename)
        if match:
            track_number = match.group(1)
            artist = match.group(2)
            title = match.group(3)
        else:
            # Fallback: assume no track number and filename format is "Artist - Title.mp3"
            match = re.match(r'(.+?)\s*-\s*(.+)\.mp3', filename)
            if match:
                track_number = None
                artist = match.group(1)
                title = match.group(2)
            else:
                print(f"Filename format not recognized: {filename}")
                return

    # Get the album name from the folder name
    album = os.path.basename(folder_name)

    # Read the image file if available
    image_data = None
    if image_path:
        with open(image_path, 'rb') as img_file:
            image_data = img_file.read()

    # Set the tags for the MP3 file
    set_mp3_tags(file_path, artist, album, title, track_number, image_data, clear_year)

def process_music_folder(root_folder):
    """Process all MP3 files in the given folder and its subfolders."""
    for foldername, subfolders, filenames in os.walk(root_folder):
        # Find an image in the folder
        image_path = find_image(foldername)

        # Check if the folder contains MP3 files with multiple years
        years = set()
        mp3_files = []
        for filename in filenames:
            if filename.lower().endswith('.mp3'):
                file_path = os.path.join(foldername, filename)
                try:
                    audio = MP3(file_path, ID3=ID3)
                    year = get_year_from_tags(audio)
                    if year:
                        years.add(year)
                    mp3_files.append(file_path)
                except error:
                    print(f"Error reading {file_path}")
                except Exception as e:
                    print(f"Unexpected error reading {file_path}: {e}")

        # Determine if we need to clear the Year tag
        clear_year = len(years) > 1  # Clear Year tag if multiple years are found

        # Process each MP3 file in the folder
        for file_path in mp3_files:
            process_mp3_file(file_path, foldername, image_path, clear_year)

if __name__ == "__main__":
    # Get the folder path from environment variable or command line argument
    music_folder = os.getenv('Folders') or os.getenv('folders')
    
    if not music_folder:
        print("Error: No folder specified. Please set the 'Folders' environment variable.")
        exit(1)
    
    music_folder = music_folder.strip('"').strip("'")
    
    # Process all albums in the main music folder
    set_album_artist(music_folder)
    process_music_folder(music_folder)