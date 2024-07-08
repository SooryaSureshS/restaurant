import os
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet


class PaymentCardEncrypt:

    def __init__(self, card_holder, cvv, card_number, key):
        self.card_holder = card_holder
        self.cvv = cvv
        self.card_number = card_number
        self.key = key

    def url_safe_base64_encoded_key(self):
        backend = default_backend()
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=backend
        )
        in_bytes = self._generate_bytes(self._generate_key())
        self.key = base64.urlsafe_b64encode(kdf.derive(in_bytes))

    def _generate_key(self):
        return self.card_holder[-3:] + self.cvv + self.card_number[-4:]

    @staticmethod
    def _generate_bytes(string_2_bytes):
        return bytes(string_2_bytes, 'utf-8')

    def get_encrypted_string(self, string_2_bytes):
        cipher_suite = Fernet(self.key)
        return cipher_suite.encrypt(self._generate_bytes(string_2_bytes=string_2_bytes))

    def get_decrypt_data(self, string_2_decrypt):
        cipher_suite = Fernet(self.key)
        ciphered_text = string_2_decrypt
        return cipher_suite.decrypt(ciphered_text)
