#!/usr/bin/env python3
"""
File Copy Utility - Preserves folder hierarchy when copying files
Supports both simple copying and advanced features like filtering and progress tracking
"""

import os
import shutil
import argparse
from pathlib import Path
from typing import List, Optional, Callable
import fnmatch
import time

class FileCopyUtility:
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.copied_files = 0
        self.total_files = 0
        self.copied_size = 0
        self.total_size = 0

    def count_files(self, source_dir: str, patterns: Optional[List[str]] = None) -> tuple:
        """Count total files and size for progress tracking"""
        total_files = 0
        total_size = 0
        
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                if self._should_copy_file(file, patterns):
                    file_path = os.path.join(root, file)
                    try:
                        total_size += os.path.getsize(file_path)
                        total_files += 1
                    except (OSError, IOError):
                        continue
        
        return total_files, total_size

    def _should_copy_file(self, filename: str, patterns: Optional[List[str]] = None) -> bool:
        """Check if file should be copied based on patterns"""
        if not patterns:
            return True
        
        for pattern in patterns:
            if fnmatch.fnmatch(filename.lower(), pattern.lower()):
                return True
        return False

    def _update_progress(self, file_path: str, file_size: int):
        """Update progress and call callback if provided"""
        self.copied_files += 1
        self.copied_size += file_size
        
        if self.progress_callback:
            progress_percent = (self.copied_files / self.total_files) * 100 if self.total_files > 0 else 0
            self.progress_callback(self.copied_files, self.total_files, progress_percent, file_path)

    def copy_with_hierarchy(self, source: str, destination: str, 
                          file_patterns: Optional[List[str]] = None,
                          exclude_patterns: Optional[List[str]] = None,
                          preserve_timestamps: bool = True,
                          dry_run: bool = False) -> dict:
        """
        Copy files from source to destination preserving folder hierarchy
        
        Args:
            source: Source directory path
            destination: Destination directory path
            file_patterns: List of patterns to include (e.g., ['*.txt', '*.py'])
            exclude_patterns: List of patterns to exclude
            preserve_timestamps: Whether to preserve file modification times
            dry_run: If True, only simulate the copy operation
            
        Returns:
            Dictionary with operation statistics
        """
        source_path = Path(source).resolve()
        dest_path = Path(destination).resolve()
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source directory does not exist: {source}")
        
        if not source_path.is_dir():
            raise NotADirectoryError(f"Source is not a directory: {source}")
        
        # Count files for progress tracking
        self.total_files, self.total_size = self.count_files(str(source_path), file_patterns)
        self.copied_files = 0
        self.copied_size = 0
        
        stats = {
            'files_copied': 0,
            'files_skipped': 0,
            'dirs_created': 0,
            'errors': [],
            'total_size': 0
        }
        
        print(f"{'[DRY RUN] ' if dry_run else ''}Copying from: {source_path}")
        print(f"{'[DRY RUN] ' if dry_run else ''}Copying to: {dest_path}")
        print(f"Total files to process: {self.total_files}")
        print(f"Total size: {self.total_size / (1024*1024):.2f} MB")
        print("-" * 50)
        
        for root, dirs, files in os.walk(source_path):
            # Calculate relative path from source
            rel_path = Path(root).relative_to(source_path)
            target_dir = dest_path / rel_path
            
            # Create directory structure
            if not dry_run:
                target_dir.mkdir(parents=True, exist_ok=True)
                if not target_dir.exists():
                    stats['dirs_created'] += 1
            else:
                print(f"Would create directory: {target_dir}")
                stats['dirs_created'] += 1
            
            # Copy files
            for file in files:
                source_file = Path(root) / file
                target_file = target_dir / file
                
                # Check if file should be copied
                should_copy = True
                
                if file_patterns and not self._should_copy_file(file, file_patterns):
                    should_copy = False
                
                if exclude_patterns and self._should_copy_file(file, exclude_patterns):
                    should_copy = False
                
                if not should_copy:
                    stats['files_skipped'] += 1
                    continue
                
                try:
                    file_size = source_file.stat().st_size
                    
                    if not dry_run:
                        # Copy the file
                        shutil.copy2(source_file, target_file)
                        
                        # Preserve timestamps if requested
                        if preserve_timestamps:
                            shutil.copystat(source_file, target_file)
                    else:
                        print(f"Would copy: {source_file} -> {target_file}")
                    
                    stats['files_copied'] += 1
                    stats['total_size'] += file_size
                    
                    # Update progress
                    self._update_progress(str(source_file), file_size)
                    
                except (OSError, IOError) as e:
                    error_msg = f"Error copying {source_file}: {str(e)}"
                    stats['errors'].append(error_msg)
                    print(f"ERROR: {error_msg}")
        
        return stats

def print_progress(copied_files: int, total_files: int, percent: float, current_file: str):
    """Simple progress callback function"""
    bar_length = 30
    filled_length = int(bar_length * percent / 100)
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    
    print(f'\rProgress: |{bar}| {percent:.1f}% ({copied_files}/{total_files}) - {Path(current_file).name}', 
          end='', flush=True)

def main():
    parser = argparse.ArgumentParser(description='Copy files while preserving folder hierarchy')
    parser.add_argument('source', help='Source directory')
    parser.add_argument('destination', help='Destination directory')
    parser.add_argument('--include', nargs='+', help='File patterns to include (e.g., *.txt *.py)')
    parser.add_argument('--exclude', nargs='+', help='File patterns to exclude')
    parser.add_argument('--no-timestamps', action='store_true', help='Do not preserve timestamps')
    parser.add_argument('--dry-run', action='store_true', help='Simulate the operation without copying')
    parser.add_argument('--quiet', action='store_true', help='Suppress progress output')
    
    args = parser.parse_args()
    
    # Create utility instance
    progress_callback = None if args.quiet else print_progress
    utility = FileCopyUtility(progress_callback)
    
    try:
        start_time = time.time()
        
        stats = utility.copy_with_hierarchy(
            source=args.source,
            destination=args.destination,
            file_patterns=args.include,
            exclude_patterns=args.exclude,
            preserve_timestamps=not args.no_timestamps,
            dry_run=args.dry_run
        )
        
        end_time = time.time()
        
        # Print completion status
        print("\n" + "=" * 50)
        print(f"{'DRY RUN ' if args.dry_run else ''}COPY OPERATION COMPLETED")
        print("=" * 50)
        print(f"Files copied: {stats['files_copied']}")
        print(f"Files skipped: {stats['files_skipped']}")
        print(f"Directories created: {stats['dirs_created']}")
        print(f"Total size: {stats['total_size'] / (1024*1024):.2f} MB")
        print(f"Time taken: {end_time - start_time:.2f} seconds")
        
        if stats['errors']:
            print(f"Errors: {len(stats['errors'])}")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"  - {error}")
            if len(stats['errors']) > 5:
                print(f"  ... and {len(stats['errors']) - 5} more errors")
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return 1
    
    return 0

# Simple usage example
def simple_copy_example():
    """Simple example of how to use the utility programmatically"""
    utility = FileCopyUtility()
    
    try:
        stats = utility.copy_with_hierarchy(
            source="/path/to/source",
            destination="/path/to/destination",
            file_patterns=["*.txt", "*.py"],  # Only copy text and Python files
            exclude_patterns=["*.tmp", "*.log"]  # Exclude temporary files
        )
        print(f"Copied {stats['files_copied']} files successfully!")
    except Exception as e:
        print(f"Copy failed: {e}")

if __name__ == "__main__":
    exit(main())