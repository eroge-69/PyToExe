from pytube import YouTube
from moviepy.editor import VideoFileClip
import os
import zipfile

def download_youtube_video(url, output_path="video.mp4"):
    try:
        yt = YouTube(url)
        stream = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
        stream.download(filename=output_path)
        print(f"Downloaded video to {output_path}")
        return output_path
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

def split_and_process_video(video_path, clip_duration=70, output_dir="clips"):
    try:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        video = VideoFileClip(video_path)
        duration = video.duration
        clips = []
        for start_time in range(0, int(duration), clip_duration):
            end_time = min(start_time + clip_duration, duration)
            clip = video.subclip(start_time, end_time)
            clip = clip.fx(lambda clip: clip.fx(vfx.mirror_x))
            clip = clip.resize((1080, 1920))
            clip_path = os.path.join(output_dir, f"clip_{start_time//60:02d}_{start_time%60:02d}.mp4")
            clip.write_videofile(clip_path, codec="libx264", audio_codec="aac")
            clips.append(clip_path)
            print(f"Created clip: {clip_path}")
        video.close()
        return clips
    except Exception as e:
        print(f"Error processing video: {e}")
        return []

def create_zip(clips, zip_name="clips.zip"):
    try:
        with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for clip in clips:
                zipf.write(clip, os.path.basename(clip))
        print(f"Created ZIP file: {zip_name}")
        return zip_name
    except Exception as e:
        print(f"Error creating ZIP: {e}")
        return None

def main():
    url = input("Enter YouTube video URL: ")
    if not url:
        print("No URL provided. Exiting.")
        return
    
    print("Starting video processing...")
    video_path = download_youtube_video(url)
    if video_path:
        clips = split_and_process_video(video_path)
        if clips:
            zip_path = create_zip(clips)
            if zip_path:
                print(f"Success! Clips saved in {zip_path}")
            else:
                print("Failed to create ZIP file.")
        else:
            print("No clips were created.")
    else:
        print("Failed to download video.")

if __name__ == "__main__":
    main()