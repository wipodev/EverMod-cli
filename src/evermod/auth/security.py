from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from pathlib import Path
from base64 import b64encode, b64decode
import sys

# Ruta fija a la clave pública (embebida en el CLI)
PUBLIC_KEY_PATH = Path(__file__).parent / "keys" / "evermod_public.pem"

# Ruta donde solo tú tendrás la privada (no se distribuye)
PRIVATE_KEY_PATH = Path.home() / ".evermod" / "keys" / "private.pem"


# === UTILIDADES DE CLAVE ===

def load_public_key():
    with open(PUBLIC_KEY_PATH, "rb") as f:
        return serialization.load_pem_public_key(f.read())

def load_private_key():
    with open(PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


# === FIRMA / VERIFICACIÓN ===

def sign_message(message: str) -> bytes:
    """Usa la clave privada local para firmar un mensaje."""
    private_key = load_private_key()
    return private_key.sign(
        message.encode(),
        padding.PKCS1v15(),
        hashes.SHA256()
    )

def verify_signature(message: str, signature: bytes) -> bool:
    """Verifica una firma con la clave pública embebida en el CLI."""
    public_key = load_public_key()
    try:
        public_key.verify(
            signature,
            message.encode(),
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        return True
    except Exception:
        return False


# === VALIDACIÓN DE COMANDOS INTERNOS ===

def require_internal_auth(command_name: str):
    """
    Verifica que el entorno tenga clave privada válida y autoriza el comando interno.
    """
    message = f"evermod:{command_name}"

    try:
        signature = sign_message(message)
        if verify_signature(message, signature):
            print("🔏 EverMod internal signature verified.")
            return True
        else:
            print("⛔ Invalid signature — unauthorized command.")
            sys.exit(1)

    except FileNotFoundError:
        print("⛔ Missing private key: ~/.evermod/keys/private.pem")
        sys.exit(1)

# ====================================================
# 🔏 File signing utilities
# ====================================================

def sign_file(file_path: Path) -> Path:
    """
    Signs the given file using the EverMod private key and returns the .sig path.
    The signature uses RSA + SHA256 and is base64 encoded.
    """
    private_key_path = Path.home() / ".evermod" / "keys" / "private.pem"
    if not private_key_path.exists():
        print("❌ Private key not found. Cannot sign files.")
        return None

    data = file_path.read_bytes()
    private_key = serialization.load_pem_private_key(private_key_path.read_bytes(), password=None)

    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )

    sig_path = file_path.with_suffix(file_path.suffix + ".sig")
    sig_path.write_bytes(b64encode(signature))

    print(f"🔏 File signed → {sig_path.name}")
    return sig_path


def verify_file_signature(file_path: Path, sig_path: Path) -> bool:
    """
    Verifies a signed file using the embedded public key.
    Returns True if valid, False otherwise.
    """
    public_key_path = Path(__file__).parent / "keys" / "evermod_public.pem"
    if not public_key_path.exists():
        print("❌ Public key not found.")
        return False

    data = file_path.read_bytes()
    signature = b64decode(sig_path.read_bytes())
    public_key = serialization.load_pem_public_key(public_key_path.read_bytes())

    try:
        public_key.verify(
            signature,
            data,
            padding.PKCS1v15(),
            hashes.SHA256()
        )
        print(f"✅ Signature verified for {file_path.name}")
        return True
    except Exception:
        print(f"⛔ Invalid signature for {file_path.name}")
        return False
