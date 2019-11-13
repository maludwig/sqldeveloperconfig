#!/usr/bin/env python
"""
For encryption and decryption of SQLDeveloper passwords
"""

import base64
import hashlib

from Cryptodome.Cipher import DES


def generate_cipher(decryption_key, iv):
    return DES.new(decryption_key, DES.MODE_CBC, iv)


def pad(unpadded_str):
    unpadded_bytes = bytearray(unpadded_str.encode("utf8"))
    pad_len = 8 - (len(unpadded_bytes) % 8)
    padding = bytearray([pad_len for _ in range(pad_len)])
    padded_bytes = unpadded_bytes + padding
    return padded_bytes


def unpad(padded_str):
    amount_of_padding = ord(padded_str[len(padded_str) - 1 :])
    return padded_str[:-amount_of_padding]


def des_cbc_decrypt(encrypted_password, decryption_key, iv):
    crypter = generate_cipher(decryption_key, iv)
    decrypted_password = unpad(crypter.decrypt(encrypted_password))

    return decrypted_password


def des_cbc_encrypt(plaintext_password, decryption_key, iv):
    crypter = generate_cipher(decryption_key, iv)
    encrypted_password_bytes = crypter.encrypt(pad(plaintext_password))
    return encrypted_password_bytes


def v4_salt_iv(db_system_id):

    salt = bytes.fromhex("051399429372e8ad")
    num_iteration = 42

    # key generation from a machine-unique value with a fixed salt
    key = bytes(db_system_id, "utf8") + salt
    for i in range(num_iteration):
        m = hashlib.md5(key)
        key = m.digest()

    secret_key = key[:8]
    iv = key[8:]
    return secret_key, iv


def decrypt_v4(encrypted, db_system_id):
    if encrypted == "":
        return ""
    secret_key, iv = v4_salt_iv(db_system_id)
    encrypted_password = base64.b64decode(encrypted)
    decrypted = des_cbc_decrypt(encrypted_password, secret_key, iv)
    return decrypted.decode("utf8")


def encrypt_v4(plain_pass, db_system_id):
    if plain_pass == "":
        return ""
    secret_key, iv = v4_salt_iv(db_system_id)
    encrypted_bytes = des_cbc_encrypt(plain_pass, secret_key, iv)
    encrypted_password = base64.b64encode(encrypted_bytes)
    return encrypted_password.decode("utf8")
