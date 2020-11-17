# AES 256 encryption/decryption using pycrypto library
 
import base64
from Cryptodome.Cipher import AES
from Cryptodome import Random
from Cryptodome.Protocol.KDF import PBKDF2

import my_settings
 
BLOCK_SIZE = 16
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
unpad = lambda s: s[:-ord(s[len(s) - 1:])]
 

def get_private_key(random):
    salt = my_settings.SECRET.get('salt')
    kdf = PBKDF2(random, salt, 64, 1000)
    key = kdf[:32]
    return key
 
 
def encrypt(info, random):
    private_key = get_private_key(random)
    raw = pad(raw).encode('utf-8')
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return base64.b64encode(iv + cipher.encrypt(raw))
 
 
def decrypt(enc, random):
    private_key = get_private_key(random)
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = AES.new(private_key, AES.MODE_CBC, iv)
    return unpad(cipher.decrypt(enc[16:]))
 
 
