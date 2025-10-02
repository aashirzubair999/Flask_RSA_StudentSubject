from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes
import os

# Key file paths
PRIVATE_KEY_FILE = "rsa_private_key.pem"
PUBLIC_KEY_FILE = "rsa_public_key.pem"

def generate_and_save_keys():
    """Generate RSA keys and save them to files"""
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    public_key = private_key.public_key()
    
    # Save private key
    with open(PRIVATE_KEY_FILE, "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Save public key
    with open(PUBLIC_KEY_FILE, "wb") as f:
        f.write(public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ))
    
    return private_key, public_key

def load_keys():
    """Load RSA keys from files, generate if they don't exist"""
    if not os.path.exists(PRIVATE_KEY_FILE) or not os.path.exists(PUBLIC_KEY_FILE):
        return generate_and_save_keys()
    
    # Load private key
    with open(PRIVATE_KEY_FILE, "rb") as f:
        private_key = serialization.load_pem_private_key(f.read(), password=None)
    
    # Load public key
    with open(PUBLIC_KEY_FILE, "rb") as f:
        public_key = serialization.load_pem_public_key(f.read())
    
    return private_key, public_key

# Load keys when module is imported
private_key, public_key = load_keys()

def encrypt_name(name: str) -> bytes:
    return public_key.encrypt(
        name.encode(),
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def decrypt_name(encrypted_name) -> str:
    if isinstance(encrypted_name, memoryview):
        encrypted_name = encrypted_name.tobytes()
    elif isinstance(encrypted_name, bytes):
        pass  # Already bytes
    else:
        # Handle other types if needed
        encrypted_name = bytes(encrypted_name)

    try:
        decrypted = private_key.decrypt(
            encrypted_name,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
        return decrypted.decode("utf-8")
    except Exception as e:
        print(f"Decryption error: {e}")
        print(f"Encrypted data length: {len(encrypted_name)}")
        raise