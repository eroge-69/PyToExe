import numpy as np
from scipy.io import wavfile
import os
import tempfile
from scipy import signal
import subprocess
from datetime import datetime
from collections import defaultdict
import time
import json

def load_config():
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config file: {str(e)}")
        return None

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def get_video_duration(video_path):
    try:
        ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
        command = [ffmpeg_path, '-i', video_path]
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        stderr_output = stderr.decode()
        
        for line in stderr_output.split('\n'):
            if "Duration:" in line:
                time_str = line.split("Duration:")[1].split(",")[0].strip()
                h, m, s = time_str.split(':')
                duration = float(h) * 3600 + float(m) * 60 + float(s)
                return duration
                
        print(f"Could not find duration in output: {stderr_output}")
        return None
            
    except Exception as e:
        print(f"Error getting video duration: {str(e)}")
        return None

def extract_audio(video_path, output_path):
    try:
        video_path = os.path.normpath(video_path)
        output_path = os.path.normpath(output_path)
        
        print(f"Processing file: {video_path}")
        
        ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
        command = [
            ffmpeg_path,
            '-i', video_path,
            '-vn',
            '-acodec', 'pcm_s16le',
            '-ac', '1',
            '-ar', '44100',
            '-y',
            output_path
        ]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"FFmpeg error: {stderr.decode()}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error extracting audio: {str(e)}")
        return False

def cut_video_segment(video_path, output_path, start_time, duration, padding=5):
    try:
        # Adjust start time and duration with padding
        padded_start = max(0, start_time - padding)  # Don't go below 0
        padded_duration = duration + (padding * 2)  # Add padding to both ends
        
        ffmpeg_path = os.path.join(os.path.dirname(__file__), 'ffmpeg.exe')
        command = [
            ffmpeg_path,
            '-ss', str(padded_start),
            '-i', video_path,
            '-t', str(padded_duration),
            '-c', 'copy',
            '-y',
            output_path
        ]
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            print(f"Error cutting video: {stderr.decode()}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error cutting video: {str(e)}")
        return False

def create_fingerprint(audio_data, sample_rate, config):
    """Create audio fingerprint with overlapping windows"""
    print("\nCreating fingerprint...")
    print("Analyzing audio patterns...")
    
    chunk_size = config['audio_processing']['chunk_size']
    overlap = config['audio_processing']['overlap']
    
    fingerprints = defaultdict(list)
    total_chunks = (len(audio_data) - chunk_size) // (chunk_size - overlap)
    last_update = time.time()
    
    for i in range(0, len(audio_data) - chunk_size, chunk_size - overlap):
        if time.time() - last_update > 1:
            progress = (i / len(audio_data)) * 100
            print(f"Progress: {progress:.1f}%")
            last_update = time.time()
            
        chunk = audio_data[i:i + chunk_size]
        
        # Get frequency data
        freqs = np.abs(np.fft.rfft(chunk))
        
        # Find peak frequencies
        peak_indices = signal.find_peaks(freqs, height=np.mean(freqs))[0]
        if len(peak_indices) > 0:
            # Take top 3 peaks
            top_peaks = sorted([(freqs[j], j) for j in peak_indices], reverse=True)[:3]
            
            # Create hash from peak frequencies
            freq_hash = hash(tuple(sorted(f for _, f in top_peaks)))
            fingerprints[freq_hash].append(i)
    
    print("Fingerprint created!")
    return fingerprints

def remove_duplicate_matches(matches, config):
    """Remove duplicate matches that are too close in time and filter out negative timestamps"""
    if not matches:
        return []
        
    time_threshold = config['matching']['time_threshold']
    
    # Filter out negative timestamps first
    positive_matches = [match for match in matches if match[0] >= 0]
    
    if not positive_matches:
        return []
    
    # Sort matches by timestamp
    sorted_matches = sorted(positive_matches, key=lambda x: x[0])
    
    # Group matches that are close in time
    unique_matches = []
    current_group = [sorted_matches[0]]
    
    for match in sorted_matches[1:]:
        last_match = current_group[-1]
        time_diff = abs(match[0] - last_match[0])
        
        if time_diff <= time_threshold:
            # Add to current group if within threshold
            current_group.append(match)
        else:
            # Process current group and start new group
            best_match = max(current_group, key=lambda x: x[1])  # Take highest confidence
            unique_matches.append(best_match)
            current_group = [match]
    
    # Add the last group's best match
    best_match = max(current_group, key=lambda x: x[1])
    unique_matches.append(best_match)
    
    return unique_matches

def find_matches_in_video(sample_video_path, video_path, sample_duration, config):
    try:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_sample_audio:
            sample_audio_path = temp_sample_audio.name
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_video_audio:
            video_audio_path = temp_video_audio.name

        print("\nExtracting audio from sample video...")
        if not extract_audio(sample_video_path, sample_audio_path):
            print("Failed to extract audio from sample video")
            return []

        print("\nExtracting audio from target video...")
        if not extract_audio(video_path, video_audio_path):
            print("Failed to extract audio from target video")
            return []

        print("Loading audio files...")
        sample_rate, sample_audio = wavfile.read(sample_audio_path)
        _, video_audio = wavfile.read(video_audio_path)
        
        os.unlink(sample_audio_path)
        os.unlink(video_audio_path)
        
        print("Processing audio data...")
        if len(sample_audio.shape) > 1:
            sample_audio = sample_audio.mean(axis=1)
        if len(video_audio.shape) > 1:
            video_audio = video_audio.mean(axis=1)
        
        # Create fingerprints
        print("\nCreating sample fingerprint...")
        sample_fingerprints = create_fingerprint(sample_audio, sample_rate, config)
        
        print("\nCreating video fingerprint...")
        video_fingerprints = create_fingerprint(video_audio, sample_rate, config)
        
        print("\nMatching fingerprints...")
        best_match = None
        best_confidence = 0
        max_count = 0
        match_counts = defaultdict(int)
        
        print("Looking for matching patterns...")
        for hash_val, sample_times in sample_fingerprints.items():
            if hash_val in video_fingerprints:
                for s_time in sample_times:
                    for v_time in video_fingerprints[hash_val]:
                        offset = v_time - s_time
                        if offset >= 0:
                            match_counts[offset] += 1
                            if match_counts[offset] > max_count:
                                max_count = match_counts[offset]
        
        # Find the single best match
        if match_counts:
            threshold = max_count * config['matching']['threshold']
            confidence_threshold = config['matching']['confidence_threshold']
            
            for offset, count in match_counts.items():
                if count > threshold:
                    timestamp = offset / sample_rate
                    if timestamp >= 0:
                        confidence = (count / max_count) * 100
                        if confidence >= confidence_threshold and confidence > best_confidence:
                            best_confidence = confidence
                            best_match = (timestamp, confidence)
        
        if best_match:
            timestamp, confidence = best_match
            minutes = int(timestamp // 60)
            seconds = int(timestamp % 60)
            print(f"\nFound match at: {minutes:02d}:{seconds:02d} (confidence: {confidence:.2f}%)")
            return [best_match]  # Return as list for compatibility with existing code
        
        return []
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return []

def move_to_processed(input_folder, video_file, config):
    """Move processed video to processed folder"""
    processed_dir = os.path.join(input_folder, config['directories'].get('processed', 'processed'))
    ensure_dir(processed_dir)
    
    source_path = os.path.join(input_folder, video_file)
    dest_path = os.path.join(processed_dir, video_file)
    
    try:
        os.rename(source_path, dest_path)
        print(f"Moved {video_file} to processed folder")
        return True
    except Exception as e:
        print(f"Error moving file to processed folder: {str(e)}")
        return False

def extract_timestamp_from_filename(filename):
    """Extract timestamp from filename like 365_NEWS_20250222_22_11_09_22_28_34"""
    try:
        parts = filename.split('_')
        # Get first part of name and first timestamp only
        prefix = '_'.join(parts[:2])  # 365_NEWS
        date = parts[2]  # 20250222
        hour = int(parts[3])  # 22
        minute = int(parts[4])  # 11
        second = int(parts[5])  # 09
        return prefix, date, hour, minute, second
    except Exception as e:
        print(f"Error parsing filename timestamp: {str(e)}")
        return None

def add_timestamps(filename, minutes, seconds):
    """Extract timestamp from filename and update it"""
    try:
        # Remove any existing _1, _2 etc suffixes first
        base_name = filename.split('_1')[0].split('_2')[0]  # Remove any existing numbered suffixes
        parts = base_name.split('_')
        
        # Get first part of name and first timestamp only
        prefix = '_'.join(parts[:2])  # e.g., ARY_NEWS
        date = parts[2]  # e.g., 20250225
        
        # Create new filename with updated timestamp
        new_filename = f"{prefix}_{date}_{minutes:02d}_{seconds:02d}.mp4"
        return new_filename
        
    except Exception as e:
        print(f"Error calculating new timestamp: {str(e)}")
        return filename

def process_folder(input_folder, sample_video_path, config):
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' not found!")
        return
    
    if not os.path.exists(sample_video_path):
        print(f"Error: Sample video file '{sample_video_path}' not found!")
        return
    
    # Get sample video duration
    sample_duration = get_video_duration(sample_video_path)
    if sample_duration is None:
        print("Error: Could not get sample video duration")
        return
        
    print(f"\nSample video duration: {sample_duration:.2f} seconds")
    
    # Create output directory
    output_dir = os.path.join(os.path.dirname(__file__), config['directories']['output'])
    ensure_dir(output_dir)
    
    print(f"\nUsing sample video: {sample_video_path}")
    print(f"Searching in folder: {input_folder}")
    print(f"Output directory: {output_dir}")
    
    supported_extensions = config['video']['supported_extensions']
    video_files = [f for f in os.listdir(input_folder) 
                   if any(f.lower().endswith(ext) for ext in supported_extensions)]
    
    if not video_files:
        print(f"No video files found in '{input_folder}'")
        return
    
    print(f"\nFound {len(video_files)} video files to process")
    print("\nProcessing videos...")
    print("===================")
    
    for video_file in video_files:
        video_path = os.path.join(input_folder, video_file)
        print(f"\nAnalyzing: {video_file}")
        
        matches = find_matches_in_video(sample_video_path, video_path, sample_duration, config)
        
        if matches:
            print(f"\nProcessing match in {video_file}")
            
            # We know there's only one match
            timestamp, confidence = matches[0]
            minutes = int(timestamp // 60)
            seconds = int(timestamp % 60)
            print(f"\nProcessing match at {minutes:02d}:{seconds:02d}")
            
            # Generate new filename with updated timestamp
            output_filename = add_timestamps(video_file, minutes, seconds)
            output_path = os.path.join(output_dir, output_filename)
            
            print("Cutting matched segment...")
            if cut_video_segment(video_path, output_path, timestamp, sample_duration, padding=5):
                print(f"Saved matched segment to: {output_filename}")
                print(f"Segment duration: {sample_duration + 10:.2f} seconds (including 5s padding on each end)")
            else:
                print("Failed to cut video segment")
        else:
            print("No matches found")
            
        # Move processed file regardless of matches
        move_to_processed(input_folder, video_file, config)

def main():
    print("Video Audio Matcher (FFmpeg Version)")
    print("===================================")
    
    # Load configuration
    config = load_config()
    if config is None:
        print("Failed to load configuration. Using default values.")
        return
    
    # Use paths relative to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    input_folder = os.path.join(script_dir, config['directories']['input'])
    sample_path = os.path.join(script_dir, config['directories']['sample'])
    
    if not os.path.exists(input_folder):
        print(f"Error: Input folder '{input_folder}' not found!")
        return
        
    if not os.path.exists(sample_path):
        print(f"Error: Sample path '{sample_path}' not found!")
        return
    
    # Handle sample path directory
    if os.path.isdir(sample_path):
        print(f"Looking for videos in sample path: {sample_path}")
        sample_files = [f for f in os.listdir(sample_path) 
                       if f.lower().endswith('.mp4')]
        if sample_files:
            print(f"Found sample video: {sample_files[0]}")
            sample_video = os.path.join(sample_path, sample_files[0])
        else:
            print(f"No mp4 files found in {sample_path}")
            return
    else:
        sample_video = sample_path
    
    print(f"Using input folder: {input_folder}")
    print(f"Using sample video: {sample_video}")
    
    ffmpeg_path = os.path.join(script_dir, 'ffmpeg.exe')
    if not os.path.exists(ffmpeg_path):
        print("Error: ffmpeg.exe not found in the current directory")
        return
        
    process_folder(input_folder, sample_video, config)

if __name__ == "__main__":
    main()
