#!/usr/bin/env python3
"""
scene_matcher.py - Prototype tool to help map cut points from a reference (edited) video
onto an original source video and output a Premiere-compatible XML sequence with matching cuts.

IMPORTANT (prototype):
 - Requires ffmpeg available in PATH.
 - Requires Python packages: Pillow
 - This is a heuristic prototype: it extracts frames at a fixed rate (default 1 fps), computes a simple
   perceptual "avg hash" per frame and then matches reference frames to original frames by Hamming distance.
 - The generated XML is a basic Premiere XML that places cuts at the matched timecodes. Manual review in PR is required.
 - This tool is intended to assist a half-automatic workflow — you must still inspect and fine-tune the sequence.

Usage (example):
  python scene_matcher.py --reference edited.mp4 --original original.mp4 --fps 1 --out timeline.xml

Author: prototype by ChatGPT assistant
"""

import argparse
import os
import subprocess
import tempfile
from PIL import Image
import math

def ensure_ffmpeg():
    """Check ffmpeg availability"""
    try:
        subprocess.check_output(["ffmpeg", "-version"], stderr=subprocess.STDOUT)
    except Exception as e:
        raise RuntimeError("ffmpeg not found in PATH. Please install ffmpeg and ensure it's available in PATH.") from e

def extract_frames(video_path, dest_dir, fps=1):
    os.makedirs(dest_dir, exist_ok=True)
    pattern = os.path.join(dest_dir, "frame_%06d.jpg")
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vf", f"fps={fps}",
        "-q:v", "2",
        pattern
    ]
    subprocess.check_call(cmd)
    frames = sorted([os.path.join(dest_dir, f) for f in os.listdir(dest_dir) if f.lower().endswith(".jpg")])
    return frames

def average_hash(image_path, hash_size=8):
    """Compute a simple average hash (aHash). Returns an integer representing bits."""
    img = Image.open(image_path).convert("L").resize((hash_size, hash_size), Image.LANCZOS)
    pixels = list(img.getdata())
    avg = sum(pixels) / len(pixels)
    bits = 0
    for i, p in enumerate(pixels):
        if p >= avg:
            bits |= (1 << i)
    return bits

def hamming_distance(a, b):
    x = a ^ b
    return bin(x).count("1")

def match_frames(ref_hashes, orig_hashes, max_distance=10):
    """For each hash in ref_hashes, find best match index in orig_hashes"""
    mapping = []
    for i, rh in enumerate(ref_hashes):
        best_j = None
        best_d = None
        for j, oh in enumerate(orig_hashes):
            d = hamming_distance(rh, oh)
            if best_d is None or d < best_d:
                best_d = d
                best_j = j
        mapping.append((i, best_j, best_d))
    return mapping

def seconds_to_timecode(sec, framerate=30):
    total_frames = int(round(sec * framerate))
    hours = total_frames // (3600 * framerate)
    mins = (total_frames % (3600 * framerate)) // (60 * framerate)
    secs = (total_frames % (60 * framerate)) // framerate
    frames = total_frames % framerate
    return f"{hours:02d}:{mins:02d}:{secs:02d}:{frames:02d}"

def generate_premiere_xml(mapping, ref_fps, orig_fps, out_xml_path, ref_frame_count, orig_frame_count):
    """Create a very simple XML sequence with cuts at matched frame timestamps.
       The XML format here is a minimal illustrative Premiere XML. You will likely need to adjust it for complex projects."""
    # Compute timecodes (in seconds) for each reference frame and matched original frame
    ref_times = [i / ref_fps for i in range(ref_frame_count)]
    orig_times = [j / orig_fps for j in range(orig_frame_count)]
    # Build sequence as series of clips with lengths equal to the difference between consecutive ref timecodes
    clips = []
    for idx, (ref_i, orig_j, dist) in enumerate(mapping):
        start = ref_times[ref_i]
        # end is next frame start or +1/ref_fps for last
        if ref_i + 1 < len(ref_times):
            end = ref_times[ref_i + 1]
        else:
            end = start + (1.0 / ref_fps)
        duration = end - start
        orig_start = orig_times[orig_j]
        clips.append({
            "ref_index": ref_i,
            "orig_index": orig_j,
            "orig_start": orig_start,
            "duration": duration,
            "distance": dist
        })
    # Build a minimal XML sequence (this is not a full Premiere project, but many users can import such simple XMLs)
    xml_parts = []
    xml_parts.append('<?xml version="1.0" encoding="UTF-8"?>')
    xml_parts.append('<xmeml version="4">')
    xml_parts.append('  <sequence>')
    xml_parts.append('    <name>Matched Sequence</name>')
    xml_parts.append('    <duration>{}</duration>'.format(len(clips)))
    xml_parts.append('    <media>')
    xml_parts.append('      <video>')
    xml_parts.append('        <track>')
    for c in clips:
        xml_parts.append('          <clipitem id="clip_{0}">'.format(c["ref_index"]))
        xml_parts.append('            <name>clip_{0}</name>'.format(c["ref_index"]))
        xml_parts.append('            <start>{:.3f}</start>'.format(c["orig_start"]))
        xml_parts.append('            <end>{:.3f}</end>'.format(c["orig_start"] + c["duration"]))
        xml_parts.append('            <in>{:.3f}</in>'.format(c["orig_start"]))
        xml_parts.append('            <out>{:.3f}</out>'.format(c["orig_start"] + c["duration"]))
        xml_parts.append('            <file id="file_{0}">'.format(c["orig_index"]))
        xml_parts.append('              <name>original_source</name>')
        xml_parts.append('            </file>')
        xml_parts.append('          </clipitem>')
    xml_parts.append('        </track>')
    xml_parts.append('      </video>')
    xml_parts.append('    </media>')
    xml_parts.append('  </sequence>')
    xml_parts.append('</xmeml>')
    xml_text = "\n".join(xml_parts)
    with open(out_xml_path, "w", encoding="utf-8") as f:
        f.write(xml_text)
    print(f"Wrote XML to: {out_xml_path} (import this into Premiere and relink the media manually)")

def main():
    parser = argparse.ArgumentParser(description="Prototype scene matcher: generate cut mapping and a simple Premiere XML.")
    parser.add_argument("--reference", required=True, help="Reference edited video (the one you want to copy cuts from)")
    parser.add_argument("--original", required=True, help="Original source video (the full raw footage)")
    parser.add_argument("--fps", type=float, default=1.0, help="Frame extraction rate (frames per second) for hashing; higher -> more accuracy but slower")
    parser.add_argument("--out", default="matched_timeline.xml", help="Output XML path (Premiere-importable)")
    parser.add_argument("--max-distance", type=int, default=12, help="Max hamming distance allowed for a match (informational)")
    args = parser.parse_args()

    ensure_ffmpeg()

    with tempfile.TemporaryDirectory() as dref, tempfile.TemporaryDirectory() as dorig:
        print("Extracting frames from reference...")
        ref_frames = extract_frames(args.reference, dref, fps=args.fps)
        print(f"Found {len(ref_frames)} reference frames.")
        print("Extracting frames from original...")
        orig_frames = extract_frames(args.original, dorig, fps=args.fps)
        print(f"Found {len(orig_frames)} original frames.")

        if not ref_frames or not orig_frames:
            print("No frames extracted. Check inputs and ffmpeg.")
            return

        print("Hashing reference frames...")
        ref_hashes = [average_hash(p) for p in ref_frames]
        print("Hashing original frames...")
        orig_hashes = [average_hash(p) for p in orig_frames]

        print("Matching frames...")
        mapping = match_frames(ref_hashes, orig_hashes, max_distance=args.max_distance)
        # Print a small report
        for ref_i, orig_j, dist in mapping[:20]:
            print(f"ref frame {ref_i} -> orig frame {orig_j} (hamming={dist})")
        # Write XML
        generate_premiere_xml(mapping, ref_fps=args.fps, orig_fps=args.fps, out_xml_path=args.out,
                              ref_frame_count=len(ref_frames), orig_frame_count=len(orig_frames))
        print("Done. IMPORTANT: open the XML in Premiere, relink 'original_source' to your original file, and manually review sequence.")

if __name__ == "__main__":
    main()
