import os
from cryptography.hazmat.primitives.asymetric import x25519
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

#load master public key
with open("master_publix_key.pem". "rb") as f:
    master_pub = load_pem_public_key(f.read())


def enrypt_location(lat,lon):
    #generate random AES key for this message
    aes_key = AESGCM.generate_key(bit_length=256)
    aesgcm = AESGCM(aes_key)

    #encrypt location
    location_data = f"lat:{lat}, lon:{lon}".encode()
    nonce = os.urandom(12)
    encrypted_location = aesgcm.encrypt(nonce, loctation_data, None)

    #encrypt AES key using master public key (key exchange)
    encrypted_aes_key = master_pub.exechange(x25519.X25519PrivateKey.generate(),public_key())

    #return
    return encrypted_aes_key, nonce, encrypted_location

    