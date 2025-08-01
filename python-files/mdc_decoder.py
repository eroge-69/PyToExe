#!/usr/bin/env python3
"""
MDC Decoder - Standalone Audio Monitoring System
Listens to PC audio input, decodes MDC signaling, and logs to spreadsheet
"""

import pyaudio
import numpy as np
import csv
import sqlite3
import json
import threading
import time
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import configparser
from dataclasses import dataclass
from typing import Optional, List, Dict
import signal
import sys

@dataclass
class MDCData:
    timestamp: datetime
    mdc_id: str
    alias: Optional[str] = None
    signal_strength: float = 0.0
    raw_data: str = ""

class MDCDecoder:
    """MDC (Motorola Data Communications) decoder implementation"""
    
    def __init__(self):
        # MDC uses 1200 baud AFSK (Audio Frequency Shift Keying)
        # Mark frequency: 1200 Hz, Space frequency: 1800 Hz
        self.sample_rate = 22050
        self.mark_freq = 1200
        self.space_freq = 1800
        self.baud_rate = 1200
        self.samples_per_bit = self.sample_rate // self.baud_rate
        
        # MDC packet structure
        self.sync_pattern = [0, 1, 0, 1, 0, 1, 0, 1]  # Simplified sync
        self.packet_length = 112  # MDC packet is 112 bits
        
    def decode_audio_buffer(self, audio_data: np.ndarray) -> List[MDCData]:
        """Decode MDC packets from audio buffer"""
        try:
            # Convert to float and normalize
            if audio_data.dtype == np.int16:
                audio_data = audio_data.astype(np.float32) / 32768.0
            
            # Apply bandpass filter for MDC frequencies
            filtered_audio = self._bandpass_filter(audio_data)
            
            # Demodulate AFSK to digital bits
            digital_bits = self._afsk_demodulate(filtered_audio)
            
            # Look for MDC packets
            packets = self._find_mdc_packets(digital_bits)
            
            # Parse packets to MDC data
            mdc_data_list = []
            for packet in packets:
                mdc_data = self._parse_mdc_packet(packet)
                if mdc_data:
                    mdc_data_list.append(mdc_data)
            
            return mdc_data_list
            
        except Exception as e:
            print(f"Error decoding audio: {e}")
            return []
    
    def _bandpass_filter(self, audio_data: np.ndarray) -> np.ndarray:
        """Simple bandpass filter for MDC frequencies"""
        # This is a simplified implementation
        # In production, use scipy.signal for proper filtering
        return audio_data
    
    def _afsk_demodulate(self, audio_data: np.ndarray) -> np.ndarray:
        """Demodulate AFSK audio to digital bits"""
        # Simplified AFSK demodulation
        # Calculate correlation with mark and space frequencies
        t = np.arange(len(audio_data)) / self.sample_rate
        
        # Generate reference signals
        mark_ref = np.sin(2 * np.pi * self.mark_freq * t)
        space_ref = np.sin(2 * np.pi * self.space_freq * t)
        
        # Correlate with references (simplified)
        window_size = self.samples_per_bit
        bits = []
        
        for i in range(0, len(audio_data) - window_size, window_size):
            window = audio_data[i:i + window_size]
            mark_corr = np.abs(np.mean(window * mark_ref[i:i + window_size]))
            space_corr = np.abs(np.mean(window * space_ref[i:i + window_size]))
            
            # Bit decision
            bits.append(1 if mark_corr > space_corr else 0)
        
        return np.array(bits)
    
    def _find_mdc_packets(self, digital_bits: np.ndarray) -> List[np.ndarray]:
        """Find MDC packets in digital bit stream"""
        packets = []
        
        # Look for sync patterns
        for i in range(len(digital_bits) - self.packet_length):
            # Check for sync pattern (simplified)
            potential_sync = digital_bits[i:i + len(self.sync_pattern)]
            if self._matches_sync(potential_sync):
                # Extract potential packet
                packet = digital_bits[i:i + self.packet_length]
                if len(packet) == self.packet_length:
                    packets.append(packet)
        
        return packets
    
    def _matches_sync(self, bits: np.ndarray) -> bool:
        """Check if bits match sync pattern"""
        if len(bits) != len(self.sync_pattern):
            return False
        matches = sum(1 for a, b in zip(bits, self.sync_pattern) if a == b)
        return matches >= len(self.sync_pattern) * 0.8  # 80% match threshold
    
    def _parse_mdc_packet(self, packet: np.ndarray) -> Optional[MDCData]:
        """Parse MDC packet to extract ID and other data"""
        try:
            # Convert bits to bytes (simplified)
            # MDC packet structure varies, this is a basic implementation
            
            # Skip sync and extract data portion
            data_bits = packet[8:72]  # Assuming data is in middle portion
            
            # Convert to hex string for MDC ID
            mdc_id = self._bits_to_hex(data_bits[:16])  # First 16 bits as ID
            
            # Calculate signal strength (simplified)
            signal_strength = float(np.mean(packet))
            
            return MDCData(
                timestamp=datetime.now(),
                mdc_id=mdc_id,
                signal_strength=signal_strength,
                raw_data=self._bits_to_hex(data_bits)
            )
            
        except Exception as e:
            print(f"Error parsing MDC packet: {e}")
            return None
    
    def _bits_to_hex(self, bits: np.ndarray) -> str:
        """Convert bit array to hexadecimal string"""
        # Pad to multiple of 4
        padded_bits = np.pad(bits, (0, (4 - len(bits) % 4) % 4), 'constant')
        
        hex_chars = []
        for i in range(0, len(padded_bits), 4):
            nibble = padded_bits[i:i+4]
            value = int(''.join(map(str, nibble)), 2)
            hex_chars.append(f"{value:X}")
        
        return ''.join(hex_chars)

class AudioMonitor:
    """Audio input monitoring and processing"""
    
    def __init__(self, callback):
        self.callback = callback
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.running = False
        self.buffer_size = 4096
        self.sample_rate = 22050
        
    def start_monitoring(self, device_index=None):
        """Start audio monitoring"""
        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.buffer_size,
                stream_callback=self._audio_callback
            )
            
            self.running = True
            self.stream.start_stream()
            print("Audio monitoring started")
            
        except Exception as e:
            print(f"Error starting audio monitoring: {e}")
            raise
    
    def stop_monitoring(self):
        """Stop audio monitoring"""
        self.running = False
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.audio.terminate()
        print("Audio monitoring stopped")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Audio stream callback"""
        if self.running:
            # Convert audio data to numpy array
            audio_array = np.frombuffer(in_data, dtype=np.int16)
            
            # Call the processing callback
            threading.Thread(
                target=self.callback,
                args=(audio_array,),
                daemon=True
            ).start()
        
        return (None, pyaudio.paContinue)
    
    def get_audio_devices(self):
        """Get list of available audio input devices"""
        devices = []
        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                devices.append({
                    'index': i,
                    'name': device_info['name'],
                    'channels': device_info['maxInputChannels']
                })
        return devices

class DataLogger:
    """Data logging and management"""
    
    def __init__(self, db_path="mdc_logs.db", csv_path="mdc_logs.csv"):
        self.db_path = db_path
        self.csv_path = csv_path
        self.aliases = {}
        self.init_database()
        self.load_aliases()
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mdc_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                mdc_id TEXT,
                alias TEXT,
                signal_strength REAL,
                raw_data TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp ON mdc_logs(timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_mdc_id ON mdc_logs(mdc_id)
        ''')
        
        conn.commit()
        conn.close()
    
    def load_aliases(self, alias_file="mdc_aliases.json"):
        """Load MDC ID to alias mappings"""
        try:
            if os.path.exists(alias_file):
                with open(alias_file, 'r') as f:
                    self.aliases = json.load(f)
                print(f"Loaded {len(self.aliases)} aliases")
            else:
                # Create default alias file
                self.aliases = {
                    "1234": "Unit 1",
                    "5678": "Unit 2",
                    "ABCD": "Command"
                }
                self.save_aliases(alias_file)
        except Exception as e:
            print(f"Error loading aliases: {e}")
            self.aliases = {}
    
    def save_aliases(self, alias_file="mdc_aliases.json"):
        """Save alias mappings to file"""
        try:
            with open(alias_file, 'w') as f:
                json.dump(self.aliases, f, indent=2)
        except Exception as e:
            print(f"Error saving aliases: {e}")
    
    def log_mdc_data(self, mdc_data: MDCData):
        """Log MDC data to database and CSV"""
        # Check for alias
        alias = self.aliases.get(mdc_data.mdc_id, "")
        mdc_data.alias = alias
        
        # Log to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO mdc_logs (timestamp, mdc_id, alias, signal_strength, raw_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            mdc_data.timestamp,
            mdc_data.mdc_id,
            mdc_data.alias,
            mdc_data.signal_strength,
            mdc_data.raw_data
        ))
        
        conn.commit()
        conn.close()
        
        # Log to CSV
        self._log_to_csv(mdc_data)
        
        print(f"Logged MDC: {mdc_data.mdc_id} ({mdc_data.alias or 'Unknown'}) at {mdc_data.timestamp}")
    
    def _log_to_csv(self, mdc_data: MDCData):
        """Log data to CSV file"""
        file_exists = os.path.exists(self.csv_path)
        
        with open(self.csv_path, 'a', newline='') as f:
            writer = csv.writer(f)
            
            if not file_exists:
                # Write header
                writer.writerow(['Timestamp', 'MDC_ID', 'Alias', 'Signal_Strength', 'Raw_Data'])
            
            writer.writerow([
                mdc_data.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                mdc_data.mdc_id,
                mdc_data.alias or '',
                f"{mdc_data.signal_strength:.2f}",
                mdc_data.raw_data
            ])
    
    def cleanup_old_data(self, days=7):
        """Remove data older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Clean database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM mdc_logs WHERE timestamp < ?', (cutoff_date,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        print(f"Cleaned up {deleted_count} old records")
        
        # Note: CSV cleanup would require rewriting the entire file
        # For now, we'll keep CSV as archive and only clean database
    
    def get_recent_logs(self, limit=100):
        """Get recent log entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT timestamp, mdc_id, alias, signal_strength
            FROM mdc_logs
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results

class MDCMonitorGUI:
    """Tkinter GUI for MDC Monitor"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MDC Monitor")
        self.root.geometry("800x600")
        
        self.decoder = MDCDecoder()
        self.audio_monitor = AudioMonitor(self.process_audio)
        self.data_logger = DataLogger()
        
        self.monitoring = False
        self.selected_device = None
        
        self.create_widgets()
        self.setup_cleanup_timer()
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_widgets(self):
        """Create GUI widgets"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Audio device selection
        device_frame = ttk.LabelFrame(main_frame, text="Audio Device", padding="5")
        device_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.device_var = tk.StringVar()
        self.device_combo = ttk.Combobox(device_frame, textvariable=self.device_var, state="readonly")
        self.device_combo.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        refresh_btn = ttk.Button(device_frame, text="Refresh", command=self.refresh_devices)
        refresh_btn.grid(row=0, column=1)
        
        device_frame.columnconfigure(0, weight=1)
        
        # Control buttons
        control_frame = ttk.Frame(main_frame)
        control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.start_btn = ttk.Button(control_frame, text="Start Monitoring", command=self.toggle_monitoring)
        self.start_btn.grid(row=0, column=0, padx=(0, 10))
        
        aliases_btn = ttk.Button(control_frame, text="Edit Aliases", command=self.edit_aliases)
        aliases_btn.grid(row=0, column=1, padx=(0, 10))
        
        export_btn = ttk.Button(control_frame, text="Export CSV", command=self.export_csv)
        export_btn.grid(row=0, column=2)
        
        # Status
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var)
        status_label.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Log display
        log_frame = ttk.LabelFrame(main_frame, text="Recent Detections", padding="5")
        log_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Treeview for log display
        columns = ('Time', 'MDC ID', 'Alias', 'Signal')
        self.log_tree = ttk.Treeview(log_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.log_tree.heading(col, text=col)
            self.log_tree.column(col, width=150)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_tree.yview)
        self.log_tree.configure(yscrollcommand=scrollbar.set)
        
        self.log_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configure main grid weights
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Initialize
        self.refresh_devices()
        self.refresh_log_display()
    
    def refresh_devices(self):
        """Refresh audio device list"""
        try:
            devices = self.audio_monitor.get_audio_devices()
            device_names = [f"{d['index']}: {d['name']}" for d in devices]
            
            self.device_combo['values'] = device_names
            if device_names:
                self.device_combo.current(0)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to refresh devices: {e}")
    
    def toggle_monitoring(self):
        """Start/stop monitoring"""
        if not self.monitoring:
            try:
                device_text = self.device_var.get()
                if not device_text:
                    messagebox.showwarning("Warning", "Please select an audio device")
                    return
                
                device_index = int(device_text.split(':')[0])
                self.audio_monitor.start_monitoring(device_index)
                
                self.monitoring = True
                self.start_btn.config(text="Stop Monitoring")
                self.status_var.set("Monitoring active...")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to start monitoring: {e}")
        else:
            self.audio_monitor.stop_monitoring()
            self.monitoring = False
            self.start_btn.config(text="Start Monitoring")
            self.status_var.set("Monitoring stopped")
    
    def process_audio(self, audio_data):
        """Process audio data for MDC signals"""
        try:
            mdc_data_list = self.decoder.decode_audio_buffer(audio_data)
            
            for mdc_data in mdc_data_list:
                self.data_logger.log_mdc_data(mdc_data)
                
                # Update GUI in main thread
                self.root.after(0, self.refresh_log_display)
                
        except Exception as e:
            print(f"Error processing audio: {e}")
    
    def refresh_log_display(self):
        """Refresh the log display"""
        try:
            # Clear existing items
            for item in self.log_tree.get_children():
                self.log_tree.delete(item)
            
            # Get recent logs
            logs = self.data_logger.get_recent_logs(50)
            
            for log in logs:
                timestamp, mdc_id, alias, signal_strength = log
                self.log_tree.insert('', 0, values=(
                    timestamp,
                    mdc_id,
                    alias or 'Unknown',
                    f"{signal_strength:.2f}"
                ))
                
        except Exception as e:
            print(f"Error refreshing log display: {e}")
    
    def edit_aliases(self):
        """Open alias editor dialog"""
        AliasEditor(self.root, self.data_logger)
    
    def export_csv(self):
        """Export data to CSV file"""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if filename:
                # Copy current CSV to new location
                import shutil
                shutil.copy2(self.data_logger.csv_path, filename)
                messagebox.showinfo("Success", f"Data exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")
    
    def setup_cleanup_timer(self):
        """Setup automatic data cleanup"""
        def cleanup():
            self.data_logger.cleanup_old_data(7)
            # Schedule next cleanup in 24 hours
            self.root.after(24 * 60 * 60 * 1000, cleanup)
        
        # Initial cleanup and schedule
        cleanup()
    
    def on_closing(self):
        """Handle application closing"""
        if self.monitoring:
            self.audio_monitor.stop_monitoring()
        self.root.destroy()
    
    def run(self):
        """Run the GUI application"""
        self.root.mainloop()

class AliasEditor:
    """Dialog for editing MDC aliases"""
    
    def __init__(self, parent, data_logger):
        self.data_logger = data_logger
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit MDC Aliases")
        self.dialog.geometry("500x400")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.create_widgets()
        self.load_aliases()
    
    def create_widgets(self):
        """Create dialog widgets"""
        main_frame = ttk.Frame(self.dialog, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        ttk.Label(main_frame, text="MDC ID to Alias Mappings:").pack(anchor=tk.W, pady=(0, 10))
        
        # Treeview for aliases
        columns = ('MDC ID', 'Alias')
        self.alias_tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=15)
        
        for col in columns:
            self.alias_tree.heading(col, text=col)
            self.alias_tree.column(col, width=200)
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.alias_tree.yview)
        self.alias_tree.configure(yscrollcommand=scrollbar.set)
        
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        self.alias_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Entry fields
        entry_frame = ttk.Frame(main_frame)
        entry_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(entry_frame, text="MDC ID:").grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.mdc_entry = ttk.Entry(entry_frame, width=15)
        self.mdc_entry.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Label(entry_frame, text="Alias:").grid(row=0, column=2, sticky=tk.W, padx=(0, 5))
        self.alias_entry = ttk.Entry(entry_frame, width=25)
        self.alias_entry.grid(row=0, column=3, padx=(0, 10))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Add/Update", command=self.add_alias).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Delete", command=self.delete_alias).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(button_frame, text="Save & Close", command=self.save_and_close).pack(side=tk.RIGHT)
        
        # Bind double-click to edit
        self.alias_tree.bind('<Double-1>', self.on_item_select)
    
    def load_aliases(self):
        """Load aliases into tree view"""
        for item in self.alias_tree.get_children():
            self.alias_tree.delete(item)
        
        for mdc_id, alias in self.data_logger.aliases.items():
            self.alias_tree.insert('', tk.END, values=(mdc_id, alias))
    
    def add_alias(self):
        """Add or update alias"""
        mdc_id = self.mdc_entry.get().strip().upper()
        alias = self.alias_entry.get().strip()
        
        if not mdc_id or not alias:
            messagebox.showwarning("Warning", "Please enter both MDC ID and Alias")
            return
        
        self.data_logger.aliases[mdc_id] = alias
        self.load_aliases()
        
        # Clear entries
        self.mdc_entry.delete(0, tk.END)
        self.alias_entry.delete(0, tk.END)
    
    def delete_alias(self):
        """Delete selected alias"""
        selection = self.alias_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an alias to delete")
            return
        
        item = self.alias_tree.item(selection[0])
        mdc_id = item['values'][0]
        
        if mdc_id in self.data_logger.aliases:
            del self.data_logger.aliases[mdc_id]
            self.load_aliases()
    
    def on_item_select(self, event):
        """Handle item selection for editing"""
        selection = self.alias_tree.selection()
        if selection:
            item = self.alias_tree.item(selection[0])
            mdc_id, alias = item['values']
            
            self.mdc_entry.delete(0, tk.END)
            self.mdc_entry.insert(0, mdc_id)
            
            self.alias_entry.delete(0, tk.END)
            self.alias_entry.insert(0, alias)
    
    def save_and_close(self):
        """Save aliases and close dialog"""
        self.data_logger.save_aliases()
        self.dialog.destroy()

def main():
    """Main application entry point"""
    # Handle Ctrl+C gracefully
    def signal_handler(sig, frame):
        print('\nShutting down...')
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Create and run GUI application
        app = MDCMonitorGUI()
        app.run()
        
    except KeyboardInterrupt:
        print('\nShutting down...')
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()