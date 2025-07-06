import struct
import sys
import re
from dataclasses import dataclass
from typing import Optional, Dict, List, Tuple, Any

@dataclass
class GPSData:
    datetime: str
    latitude: float
    longitude: float
    speed: float
    track: Optional[float] = None
    altitude: Optional[float] = None
    magnetic_variation: Optional[str] = None
    accelerometer: Optional[Tuple[float, float, float]] = None

class LigoGPSParser:
    def __init__(self, gps_quadrant: Optional[str] = None, verbose: int = 0):
        self.gps_quadrant = gps_quadrant.upper() if gps_quadrant else None
        self.verbose = verbose
        self.knots_to_kph = 1.852
        self.gps_scales = {
            1: 1.524855137,
            2: 1.456027985,
            3: 1.15368
        }
        self.cipher_info: Dict[str, Any] = {
            'cache': [],
            'next': {},
            'decipher': None
        }
    
    def _cleanup_cipher(self):
        if self.cipher_info.get('next'):
            print('Warning: Not enough GPS points to determine cipher for decoding LIGOGPSINFO')
        self.cipher_info = {
            'cache': [],
            'next': {},
            'decipher': None
        }
    
    def _unfuzz_coords(self, lat: float, lon: float, scale: float) -> Tuple[float, float]:
        """Unfuzz the coordinates using the LIGO algorithm"""
        lat2 = int(lat / 10) * 10
        lon2 = int(lon / 10) * 10
        return (lat2 + (lon - lon2) * scale, lon2 + (lat - lat2) * scale)
    
    def _decrypt_ligo_gps(self, data: bytes) -> Optional[bytes]:
        """Decrypt LIGOGPSINFO record (starting with "####")"""
        if len(data) < 8:
            return None
            
        num = struct.unpack_from('<I', data, 4)[0]
        if num < 4:
            return None
        if num > 0x84:
            num = 0x84
            
        in_data = list(data[8:8+num])
        out_data = []
        
        while in_data:
            b = in_data.pop(0)
            steering_bits = b & 0xe0
            
            if steering_bits >= 0xc0:
                if len(in_data) < 4:
                    return None
                out_data.append((in_data.pop(0) | (b & 0x01)) ^ 0x20)
                out_data.append((in_data.pop(0) | (b & 0x02)) ^ 0x20)
                out_data.append((in_data.pop(0) | (b & 0x0c)) ^ 0x20)
                out_data.append((in_data.pop(0) ^ 0x20) | (b & 0x30))
                
            elif steering_bits >= 0x40:
                if len(in_data) < 3:
                    return None
                    
                if steering_bits == 0x40:
                    out_data.append(0x20)
                    out_data.append((in_data.pop(0) | (b & 0x01)) ^ 0x20)
                    out_data.append((in_data.pop(0) | (b & 0x06)) ^ 0x20)
                    out_data.append((in_data.pop(0) | (b & 0x18)) ^ 0x20)
                elif steering_bits == 0x60:
                    out_data.append((in_data.pop(0) | (b & 0x03)) ^ 0x20)
                    out_data.append(0x20)
                    out_data.append((in_data.pop(0) | (b & 0x04)) ^ 0x20)
                    out_data.append((in_data.pop(0) | (b & 0x18)) ^ 0x20)
                elif steering_bits == 0x80:
                    out_data.append((in_data.pop(0) | (b & 0x03)) ^ 0x20)
                    out_data.append((in_data.pop(0) | (b & 0x0c)) ^ 0x20)
                    out_data.append(0x20)
                    out_data.append((in_data.pop(0) | (b & 0x10)) ^ 0x20)
                else:
                    out_data.append((in_data.pop(0) | (b & 0x01)) ^ 0x20)
                    out_data.append((in_data.pop(0) | (b & 0x06)) ^ 0x20)
                    out_data.append((in_data.pop(0) | (b & 0x18)) ^ 0x20)
                    out_data.append(0x20)
                    
            elif steering_bits == 0x00:
                if len(in_data) < 1:
                    return None
                out_data.append(in_data.pop(0) | (b & 0x13))
            else:
                return None
        
        return bytes(out_data)
    
    def _order_cipher_digits(self, ch: str, next_map: Dict[str, List[str]], 
                           order: List[str], did: Optional[Dict[str, bool]] = None) -> bool:
        if did is None:
            did = {}
            
        while next_map.get(ch):
            if len(order) < 10:
                if did.get(ch):
                    break
            else:
                if len(order) == 10 and ch == order[0]:
                    return True
                break
                
            order.append(ch)
            did[ch] = True
            
            if len(next_map[ch]) == 1:
                ch = next_map[ch][0]
                continue
                
            n = len(order) - 1
            for next_ch in next_map[ch]:
                new_did = did.copy()
                if self._order_cipher_digits(next_ch, next_map, order, new_did):
                    return True
                order = order[:n]
                
            break
            
        return False
    
    def _decipher_ligo_gps(self, data_str: str, no_fuzz: bool = False) -> Optional[GPSData]:
        """Decipher and parse LIGOGPSINFO record (starting with "####")"""
        # Check if this looks like an enciphered string
        match = re.match(r'^####.{4}([0-_])[0-_]{3}/[0-_]{2}/[0-_]{2} ..([0-_])..([0-_]).([0-_])', data_str)
        if not match or match.group(2) != match.group(3):
            # print("Matched LIGOGPSINFO format error")
            return None
            
        if not self.cipher_info.get('decipher'):
            self.cipher_info['cache'].append(data_str)
            next_map = self.cipher_info['next']
            
            millennium, colon, ch2 = match.group(1), match.group(2), match.group(4)
            ch1 = self.cipher_info.get('ch1')
            self.cipher_info['ch1'] = ch2
            
            if ch1 is None or ch1 == ch2:
                return None
                
            if ch1 in next_map:
                if ch2 not in next_map[ch1]:
                    next_map[ch1].append(ch2)
            else:
                next_map[ch1] = [ch2]
                
            if len(next_map) < 10:
                return None
                
            if len(next_map) > 10:
                self.cipher_info['next'] = {}
                return None
                
            order = []
            if not self._order_cipher_digits(ch1, next_map, order):
                return None
                
            # Find index of enciphered "2" in ordered array
            two = None
            for i, ch in enumerate(order):
                if ch == millennium:
                    two = i
                    break
                    
            if two is None:
                print('Warning: Problem deciphering LIGOGPSINFO')
                return None
                
            del self.cipher_info['next']
            decipher = {colon: ':'}
            
            for i in range(10):
                ch = order[(i + two - 2 + 10) % 10]
                decipher[ch] = chr(i + 0x30)
                
            # Determine lat/lon quadrant from signs if available
            quadrant_match = re.search(r' ([0-_])%s(-?).*? ([0-_])%s(-?)' % (colon, colon), data_str)
            if quadrant_match:
                ns_ch, ns_sign, ew_ch, ew_sign = quadrant_match.groups()
                decipher[ns_ch] = 'S' if ns_sign else 'N'
                decipher[ew_ch] = 'W' if ew_sign else 'E'
                
                if not ns_sign and not ew_sign:
                    if self.gps_quadrant and len(self.gps_quadrant) == 2:
                        decipher[ns_ch] = self.gps_quadrant[0].upper()
                        decipher[ew_ch] = self.gps_quadrant[1].upper()
                    else:
                        print('Warning: May need to set GPSQuadrant option (eg. "NW")')
            
            # Fill in unknown entries with '?'
            for c in range(0x30, 0x60):
                ch = chr(c)
                if ch not in decipher:
                    decipher[ch] = '?'
                    
            self.cipher_info['decipher'] = decipher
            
            # Process cached data
            data_str = self.cipher_info['cache'].pop(0)
            
        decipher = self.cipher_info['decipher']
        pre = data_str[4:8]
        data_str = data_str[8:].rstrip('\0')
        deciphered = ''.join([decipher.get(c, c) for c in data_str])
        
        if self.verbose > 1:
            print(f"(Deciphered: {pre.encode('latin1').hex()} {deciphered})")
            
        return self._parse_ligo_gps(pre + deciphered, no_fuzz)
    
    def _parse_ligo_gps(self, data_str: str, no_fuzz: bool = False) -> Optional[GPSData]:
        
        """Parse decrypted/deciphered LIGOGPSINFO record"""
        # Example: "....2022/09/19 12:45:24 N:31.285065 W:124.759483 46.93 km/h x:-0.000 y:-0.000 z:-0.000"
        pattern = r'^.{4}(\S+ \S+)\s+([NS?]):(-?)([.\d]+)\s+([EW?]):(-?)([\.\d]+)\s+([.\d]+)'
        match = re.match(pattern, data_str)
        if not match:
            print('Warning: LIGOGPSINFO format error')
            # sys.exit(1)
            return None
            
        time, lat_ref, lat_neg, lat, lon_ref, lon_neg, lon, speed = match.groups()
        
        print(f"Parsing LIGOGPSINFO: {data_str}")
        flags = 0x01 if no_fuzz else 0
        speed_scale = self.knots_to_kph if not (flags & 0x01) else 1
        
        # Convert time format from YYYY/MM/DD to YYYY:MM:DD
        time = time.replace('/', ':')
        
        # Check for DDMM.MMMMMM format and convert to DD.DDDDDD if necessary
        if re.match(r'^\d{3}', lat):
            lat_deg = float(lat[:2])
            lat_min = float(lat[2:])
            lat = lat_deg + lat_min / 60
            
            lon_deg = float(lon[:3])
            lon_min = float(lon[3:])
            lon = lon_deg + lon_min / 60
            
            speed_scale = 1  # Speed wasn't scaled in this format
        
        if not (flags & 0x01) or True:
            scale = self.gps_scales.get(1, 1)  # Default to scale 1 if not specified
            lat, lon = self._unfuzz_coords(float(lat), float(lon), scale)
        else:
            lat, lon = float(lat), float(lon)
            
        # Final sanity check
        if abs(lat) > 90 or abs(lon) > 180:
            print('Warning: LIGOGPSINFO coordinates out of range')
            return None
            
        # Apply sign based on reference or negative sign
        lat *= -1 if (lat_neg or lat_ref == 'S') else 1
        lon *= -1 if (lon_neg or lon_ref == 'W') else 1
        speed = float(speed) * speed_scale
        
        # Parse optional fields
        track = None
        track_match = re.search(r'\bA:(\S+)', data_str)
        if track_match:
            track = float(track_match.group(1))
            
        altitude = None
        alt_match = re.search(r'\bH:(\S+)', data_str)
        if alt_match:
            altitude = float(alt_match.group(1))
            
        mag_var = None
        mag_match = re.search(r'\bM:(\S+)', data_str)
        if mag_match:
            mag_var = mag_match.group(1)
            
        accel = None
        accel_match = re.search(r'x:(\S+)\s+y:(\S+)\s+z:(\S+)', data_str)
        if accel_match:
            accel = (
                float(accel_match.group(1)),
                float(accel_match.group(2)),
                float(accel_match.group(3)))
        print(f"Parsed GPS data: Time={time}, Lat={lat}, Lon={lon}, Speed={speed}, Track={track}, Altitude={altitude}, MagVar={mag_var}, Accel={accel}")
        return GPSData(
            datetime=time,
            latitude=lat,
            longitude=lon,
            speed=speed,
            track=track,
            altitude=altitude,
            magnetic_variation=mag_var,
            accelerometer=accel
        )
    
    def parse_ligo_gps(self, data: bytes, no_fuzz: bool = False) -> List[GPSData]:
        """Parse a single block of LIGOGPS data"""
        results = []
        
        try:
            block_str = data.decode('latin1', errors='replace')
            
            # Check if this is encrypted/encoded data (starts with ####)
            if data.startswith(b'####'):
                # Try to decipher first
                deciphered = self._decipher_ligo_gps(block_str, no_fuzz)
                if deciphered:
                    results.append(deciphered)
                    if self.verbose > 0:
                        print(f"Deciphered GPS data: {deciphered}")
                    return results
                    
                # If deciphering didn't work, try decrypting
                decrypted = self._decrypt_ligo_gps(data)
                print(f"Decrypted GPS data: {decrypted[4:]}")
                # decrypted = decrypted[1:] if decrypted else None
                if decrypted:
                    if self.verbose > 1:
                        index = struct.unpack('<I', decrypted[:4])[0]
                        print(f"(Decrypted: {index} {decrypted[4:].decode('latin1', errors='replace')})")
                    parsed = self._parse_ligo_gps(decrypted.decode('latin1', errors='replace'), no_fuzz)
                    if parsed:
                        results.append(parsed)
                    return results
                    
            # Check for plaintext format (starts with date pattern)
            elif re.match(r'^.{4}\d{4}/\d{2}/\d{2}', block_str):
                # Non-encrypted format
                block_str = block_str.rstrip('\0')
                parsed = self._parse_ligo_gps(block_str, True)  # Not fuzzed
                if parsed:
                    results.append(parsed)
                    return results
                    
            else:
                print("Warning: Unrecognized GPS data format")
                
        except Exception as e:
            print(f"Error processing GPS data: {e}")
        
        return results


def extract_and_decode_gps_data(f, entries):
    """Extract GPS data from the located entries and decode it"""
    parser = LigoGPSParser(verbose=0)
    all_gps_data = []
    
    for i, (offset, length) in enumerate(entries):
        f.seek(offset)
        
        # Read box header
        box_size = read_uint32(f)
        box_type = f.read(4)
        
        try:
            box_type_str = box_type.decode('ascii')
        except UnicodeDecodeError:
            box_type_str = str(box_type)

        # Read the box data
        if box_type == b'free':
            print("Found 'free' box containing GPS data")
            gps_data = f.read(box_size - 8)
        else:
            print("Found non-standard GPS data box")
            f.seek(offset)
            gps_data = f.read(length)

        # Check for LIGOGPSINFO header
        ligo_start = gps_data.find(b'LIGOGPSINFO')
        # print(f"LIGOGPSINFO header found at position: {ligo_start}")
        if ligo_start >= 0:
            # print(f"Found LIGOGPSINFO at offset {ligo_start} in GPS data")
            # The actual GPS data starts after the header
            ligo_data = gps_data[ligo_start + 20 : ]
            # Parse the LIGO GPS data
            gps_records = parser.parse_ligo_gps(ligo_data)
            all_gps_data.extend(gps_records)
            
            # Print the parsed data
            # for record in gps_records:
            #     print(f"\nGPS Record:")
            #     print(f"  Time: {record.datetime}")
            #     print(f"  Latitude: {record.latitude:.6f}, Longitude: {record.longitude:.6f}")
            #     print(f"  Speed: {record.speed:.2f} km/h")
            #     if record.track is not None:
            #         print(f"  Track: {record.track:.1f}°")
            #     if record.altitude is not None:
            #         print(f"  Altitude: {record.altitude:.1f} m")
            #     if record.accelerometer is not None:
            #         print(f"  Accelerometer: X={record.accelerometer[0]:.3f}, Y={record.accelerometer[1]:.3f}, Z={record.accelerometer[2]:.3f}")
        else:
            print("Non-LIGO GPS data format found")
            
    return all_gps_data

def find_box(f, target_box):
    """Find a box in the MP4 file and return its position and size"""
    while True:
        pos = f.tell()
        try:
            size = read_uint32(f)
            box_type = f.read(4).decode('ascii')
        except:
            return None, None  # End of file or error
        
        if box_type == target_box:
            return pos, size
        
        # Skip to next box
        f.seek(pos + size)

def read_uint32(f, endian='>'):
    """Read a 32-bit unsigned integer from file with specified endianness"""
    return struct.unpack(endian + 'I', f.read(4))[0]


def parse_gps_box(f, gps_pos, gps_size):
    """Parse the GPS box to get GPS data locations"""
    f.seek(gps_pos + 8)  # Skip box header
    
    version = read_uint32(f)
    if version != 0x00000101:
        print(f"Warning: Unexpected GPS version {hex(version)}")
    
    num_entries = read_uint32(f)
    print(f"Found {num_entries} GPS data entries")
    
    entries = []
    for _ in range(num_entries):
        offset = read_uint32(f)
        length = read_uint32(f)
        entries.append((offset, length))
    
    return entries




def main(input_file):
    with open(input_file, 'rb') as f:
        # Find the moov box
        moov_pos, moov_size = find_box(f, 'moov')
        if moov_pos is None:
            print("Error: moov box not found")
            return
        
        # Within moov, find the gps box (note the space)
        f.seek(moov_pos + 8)  # Skip moov box header
        gps_pos, gps_size = find_box(f, 'gps ')
        if gps_pos is None:
            print("Error: gps box not found")
            return
        
        # Parse the gps box to get GPS data locations
        entries = parse_gps_box(f, gps_pos, gps_size)
        
        # Extract and decode the GPS data
        gps_data = extract_and_decode_gps_data(f, entries)
        
        # You can now work with the parsed GPS data
        print(f"\nFound {len(gps_data)} GPS records in total")

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python extract_gps.py <input.mp4>")
        sys.exit(1)
    
    main(sys.argv[1])