import sys
from pathlib import Path
import pytest

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.crypto.aes_cipher import AESCipher, vault_cipher
from app.crypto.masking import DataMasker

def test_aes_encryption_and_decryption_roundtrip():
    """Verify that sensitive banking data can be encrypted and accurately decrypted."""
    pan = "ABCDE1234F"
    context = "CUST-1001"
    
    ciphertext, nonce = vault_cipher.encrypt(pan, associated_data=context)
    assert ciphertext != pan
    assert nonce != ""
    
    decrypted = vault_cipher.decrypt(ciphertext, nonce, associated_data=context)
    assert decrypted == pan

def test_aes_different_nonces_produce_different_ciphertexts():
    """Verify that encrypting the same value twice produces different ciphertexts (semantic security)."""
    balance = "500000.00"
    ct1, nonce1 = vault_cipher.encrypt(balance)
    ct2, nonce2 = vault_cipher.encrypt(balance)
    
    assert ct1 != ct2
    assert nonce1 != nonce2

def test_aes_tamper_detection():
    """Verify that tampering with ciphertext fails authentication (AEAD integrity)."""
    secret = "TopSecretAccountDetails"
    ciphertext, nonce = vault_cipher.encrypt(secret)
    
    # Tamper with the base64 ciphertext
    tampered_bytes = bytearray(ciphertext.encode("utf-8"))
    tampered_bytes[10] = ord('X') if tampered_bytes[10] != ord('X') else ord('Y')
    tampered_ciphertext = tampered_bytes.decode("utf-8")
    
    with pytest.raises(ValueError, match="Integrity check failed"):
        vault_cipher.decrypt(tampered_ciphertext, nonce)

def test_aes_wrong_context_fails():
    """Verify that associated data (AAD) binds the ciphertext to the specific customer."""
    secret = "SensitiveData"
    ct, nonce = vault_cipher.encrypt(secret, associated_data="CUST-1001")
    
    # Attempt to decrypt using another customer's ID
    with pytest.raises(ValueError, match="Integrity check failed"):
        vault_cipher.decrypt(ct, nonce, associated_data="CUST-9999")

def test_dynamic_masking():
    """Verify privacy-preserving masking outputs."""
    assert DataMasker.mask_account_number("501002348912") == "•••• •••• 8912"
    assert DataMasker.mask_pan("ABCDE1234F") == "••••••234F"
    assert DataMasker.mask_balance("284500.50") == "₹ ••,•••.••"
    assert "•" in DataMasker.mask_email("rahul.sharma@example.com")
    assert "345" in DataMasker.mask_phone("+91 98201 12345")
