from pytube import YouTube

link = input("Enter Youtube Link : ").strip()
print("Downloading . . .")
try:
    yt = YouTube(link)
    yt.streams.get_highest_resolution().download()
    print("Video Downloaded Successfully!")
except Exception as e:
    print(f"Error: {e}")