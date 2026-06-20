import base64
import secrets

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from app.config import settings


def _get_key() -> bytes:
    key = settings.encryption_key.encode("utf-8")
    if len(key) < 32:
        key = key.ljust(32, b"\x00")
    return key[:32]


def encrypt(plaintext: str) -> str:
    key = _get_key()
    iv = secrets.token_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(plaintext.encode("utf-8"), 16))
    return base64.b64encode(iv + encrypted).decode("utf-8")


def decrypt(ciphertext: str) -> str:
    key = _get_key()
    raw = base64.b64decode(ciphertext)
    iv, encrypted = raw[:16], raw[16:]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = unpad(cipher.decrypt(encrypted), 16)
    return plaintext.decode("utf-8")
