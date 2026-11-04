import os
import base64
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag
from app.core.config import settings

class AESCipher:
    """
    AES-256-GCM Authenticated Encryption & Decryption Service.
    Protects sensitive fields at rest with per-record nonces and integrity tags.
    """
    
    def __init__(self, key_hex: Optional[str] = None):
        raw_key_hex = key_hex or settings.VAULT_MASTER_KEY_HEX
        self.key = bytes.fromhex(raw_key_hex)
        if len(self.key) != 32:
            raise ValueError(f"AES-256 requires a 32-byte key. Got {len(self.key)} bytes.")
        self.aesgcm = AESGCM(self.key)

    def encrypt(self, plaintext: str, associated_data: Optional[str] = None) -> Tuple[str, str]:
        """
        Encrypts a plaintext string using AES-256-GCM.
        
        Args:
            plaintext: The sensitive string to encrypt (e.g., PAN card or balance).
            associated_data: Optional context string (e.g. customer_code) to bind encryption to a specific record.
            
        Returns:
            Tuple of (ciphertext_base64, nonce_base64)
        """
        if not plaintext:
            return "", ""
            
        # 96-bit (12 bytes) cryptographically secure random nonce
        nonce = os.urandom(12)
        aad_bytes = associated_data.encode("utf-8") if associated_data else None
        
        # AESGCM encrypt appends the 16-byte authentication tag automatically
        ciphertext = self.aesgcm.encrypt(nonce, plaintext.encode("utf-8"), aad_bytes)
        
        return (
            base64.b64encode(ciphertext).decode("utf-8"),
            base64.b64encode(nonce).decode("utf-8")
        )

    def decrypt(self, ciphertext_b64: str, nonce_b64: str, associated_data: Optional[str] = None) -> str:
        """
        Decrypts an AES-256-GCM ciphertext and validates authentication tag.
        
        Args:
            ciphertext_b64: The base64-encoded ciphertext with tag.
            nonce_b64: The base64-encoded 12-byte nonce used during encryption.
            associated_data: Context string that must match the encryption context.
            
        Returns:
            Decrypted plaintext string.
            
        Raises:
            ValueError: If ciphertext or nonce is invalid or data was tampered with.
        """
        if not ciphertext_b64 or not nonce_b64:
            return ""
            
        try:
            ciphertext = base64.b64decode(ciphertext_b64.encode("utf-8"))
            nonce = base64.b64decode(nonce_b64.encode("utf-8"))
            aad_bytes = associated_data.encode("utf-8") if associated_data else None
            
            decrypted_bytes = self.aesgcm.decrypt(nonce, ciphertext, aad_bytes)
            return decrypted_bytes.decode("utf-8")
        except InvalidTag:
            raise ValueError("Integrity check failed: Ciphertext or Nonce was tampered with or key is invalid.")
        except Exception as e:
            raise ValueError(f"Decryption failed: {str(e)}")

# Singleton instance initialized with configured Master Key
vault_cipher = AESCipher()

