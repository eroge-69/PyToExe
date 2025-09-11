import os
from moviepy import VideoFileClip, concatenate_videoclips

def add_intro_to_videos():
    current_folder = os.path.dirname(os.path.abspath(__file__))
    intro_path = os.path.join(current_folder, "intro.mp4")

    if not os.path.exists(intro_path):
        print("❌ intro.mp4 not found in the same folder as the program!")
        return

    # Load intro once
    intro_clip = VideoFileClip(intro_path)

    for filename in os.listdir(current_folder):
        if filename.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')) and filename != "intro.mp4":
            video_path = os.path.join(current_folder, filename)
            print(f"Processing: {filename}")

            try:
                main_clip = VideoFileClip(video_path)

                # Concatenate intro + main video
                final_clip = concatenate_videoclips([intro_clip, main_clip])

                # Save output with new name
                output_path = os.path.join(
                    current_folder,
                    f"{os.path.splitext(filename)[0]}_with_intro.mp4"
                )
                final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")

                # Cleanup
                main_clip.close()
                final_clip.close()

            except Exception as e:
                print(f"❌ Failed with {filename}: {e}")

    intro_clip.close()
    print("✅ All videos processed.")

if __name__ == "__main__":
    add_intro_to_videos()
