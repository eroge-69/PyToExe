import cv2
import numpy as np
import pyautogui
import time
import datetime
import os

def create_screen_recorder(output_file="output.avi", fps=20.0, resolution=None, codec="XVID"):
    """
    Creates a screen recorder that saves the recording to a video file.

    Args:
        output_file (str, optional):  The name of the output video file (e.g., "output.avi", "recording.mp4").
                                       Defaults to "output.avi".  Choose the extension based on the codec.
        fps (float, optional): Frames per second.  Higher FPS results in smoother video but larger file size.
                               Defaults to 20.0.
        resolution (tuple, optional):  The resolution of the screen to record (width, height).
                                        If None, it defaults to the current screen resolution.
                                        Defaults to None.
        codec (str, optional): Video codec to use.  "XVID" is a good default that usually works well.  
                                  Other options include "MJPG" (less compression, larger file size), 
                                  and depending on your system and OpenCV version, potentially "H264", "AVC1".
                                  Defaults to "XVID".

    Returns:
        None. Saves the recording to a file.
    """

    if resolution is None:
        resolution = (pyautogui.size())  # Get current screen resolution

    fourcc = cv2.VideoWriter_fourcc(*codec) # Define the codec
    out = cv2.VideoWriter(output_file, fourcc, fps, resolution)

    print(f"Recording started.  Press Ctrl+C to stop.")
    print(f"Output file: {output_file}")
    print(f"Resolution: {resolution}")
    print(f"FPS: {fps}")
    print(f"Codec: {codec}")

    try:
        while True:
            img = pyautogui.screenshot()  # Take a screenshot
            frame = np.array(img)         # Convert to numpy array
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # Convert RGB to BGR for OpenCV
            out.write(frame)               # Write the frame to the video
            # Optionally, add a small delay to control CPU usage (e.g., time.sleep(0.01))
            # This is usually not necessary, but can help if your CPU is maxing out.

    except KeyboardInterrupt:
        print("Recording stopped.")
    finally:
        out.release()                     # Release the VideoWriter object
        cv2.destroyAllWindows()          # Close any open OpenCV windows (not strictly necessary here)


if __name__ == "__main__":
    # Example usage
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_filename = f"screen_recording_{timestamp}.avi"  # Or use .mp4 if your codec supports it.

    create_screen_recorder(output_file=output_filename, fps=20.0)
    # You can customize the parameters like this:
    # create_screen_recorder(output_file="my_recording.avi", fps=30.0, resolution=(1920, 1080), codec="XVID")