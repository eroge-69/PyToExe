from pytube import YouTube

# Ask user for the YouTube video URL
url = input("Enter the YouTube video URL: ")

# Create YouTube object
yt = YouTube(url)

# Display video title and author
print(f"Title: {yt.title}")
print(f"Author: {yt.author}")

# Get the highest resolution stream
stream = yt.streams.get_highest_resolution()

# Download the video
print("Downloading...")
stream.download()  # By default, saves to current directory
print("Download complete!")