#!/usr/bin/env python3
"""
AI Subtitle Translator
Translates .srt subtitle files between languages using local Ollama
"""

import re
import argparse
import os
import requests
import json
from typing import List, Tuple
from dataclasses import dataclass

@dataclass
class SubtitleEntry:
    """Represents a single subtitle entry"""
    index: int
    start_time: str
    end_time: str
    text: str

class SubtitleTranslator:
    def __init__(self, ollama_url: str = "http://localhost:11434", model: str = "gemma3:12b"):
        """Initialize the translator with Ollama settings"""
        self.ollama_url = ollama_url
        self.model = model
    
    def parse_srt(self, file_path: str) -> List[SubtitleEntry]:
        """Parse SRT file and return list of subtitle entries"""
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Split by double newlines to separate entries
        entries = re.split(r'\n\s*\n', content.strip())
        subtitles = []
        
        for entry in entries:
            lines = entry.strip().split('\n')
            if len(lines) >= 3:
                index = int(lines[0])
                time_line = lines[1]
                text = '\n'.join(lines[2:])
                
                # Parse time format: 00:00:20,000 --> 00:00:24,400
                time_match = re.match(r'(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})', time_line)
                if time_match:
                    start_time, end_time = time_match.groups()
                    subtitles.append(SubtitleEntry(index, start_time, end_time, text))
        
        return subtitles
    
    def translate_text(self, text: str, target_language: str, source_language: str = "auto") -> str:
        """Translate text using local Ollama"""
        try:
            prompt = f"""Translate the following subtitle text to {target_language}. 
Keep the same tone and style. Preserve line breaks if present.
Only return the translated text, nothing else.

Text to translate: {text}"""
            
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            }
            
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["response"].strip()
            else:
                print(f"Ollama API error: {response.status_code}")
                return text
                
        except Exception as e:
            print(f"Translation error: {e}")
            return text  # Return original text if translation fails
    
    def translate_subtitles(self, subtitles: List[SubtitleEntry], target_language: str, 
                          source_language: str = "auto", batch_size: int = 5) -> List[SubtitleEntry]:
        """Translate all subtitle entries"""
        translated_subtitles = []
        
        print(f"Translating {len(subtitles)} subtitle entries to {target_language}...")
        
        for i in range(0, len(subtitles), batch_size):
            batch = subtitles[i:i + batch_size]
            print(f"Processing batch {i//batch_size + 1}/{(len(subtitles) + batch_size - 1)//batch_size}")
            
            for subtitle in batch:
                translated_text = self.translate_text(
                    subtitle.text, target_language, source_language
                )
                translated_subtitles.append(SubtitleEntry(
                    subtitle.index,
                    subtitle.start_time,
                    subtitle.end_time,
                    translated_text
                ))
        
        return translated_subtitles
    
    def write_srt(self, subtitles: List[SubtitleEntry], output_path: str):
        """Write subtitles to SRT file"""
        with open(output_path, 'w', encoding='utf-8') as file:
            for subtitle in subtitles:
                file.write(f"{subtitle.index}\n")
                file.write(f"{subtitle.start_time} --> {subtitle.end_time}\n")
                file.write(f"{subtitle.text}\n\n")
        
        print(f"Translated subtitles saved to: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='AI Subtitle Translator using local Ollama')
    parser.add_argument('input_file', help='Input SRT file path')
    parser.add_argument('target_language', help='Target language (e.g., Spanish, French, German)')
    parser.add_argument('-o', '--output', help='Output file path (default: input_translated.srt)')
    parser.add_argument('-s', '--source', default='auto', help='Source language (default: auto-detect)')
    parser.add_argument('--model', default='llama3.1', help='Ollama model to use (default: llama3.1)')
    parser.add_argument('--url', default='http://localhost:11434', help='Ollama server URL (default: http://localhost:11434)')
    
    args = parser.parse_args()
    
    # Set output file path
    if not args.output:
        base_name = os.path.splitext(args.input_file)[0]
        args.output = f"{base_name}_{args.target_language.lower()}.srt"
    
    # Initialize translator
    translator = SubtitleTranslator(ollama_url=args.url, model=args.model)
    
    try:
        # Parse input file
        print(f"Parsing SRT file: {args.input_file}")
        subtitles = translator.parse_srt(args.input_file)
        print(f"Found {len(subtitles)} subtitle entries")
        
        # Translate subtitles
        translated_subtitles = translator.translate_subtitles(
            subtitles, args.target_language, args.source
        )
        
        # Write output file
        translator.write_srt(translated_subtitles, args.output)
        print("Translation completed successfully!")
        
    except FileNotFoundError:
        print(f"Error: Input file '{args.input_file}' not found")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()