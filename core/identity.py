"""
Device Identity System for SynapseOS
Cryptographic identity management inspired by OpenClaw
"""

import os
import json
import base64
from datetime import datetime
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.backends import default_backend
import logging

logger = logging.getLogger(__name__)

class DeviceIdentity:
    """Device identity with Ed25519 key pair"""

    def __init__(self, identity_file: str = "config/device_identity.json"):
        self.identity_file = identity_file
        self.device_id = None
        self.public_key = None
        self.private_key = None
        self.created_at = None

        self._load_or_create_identity()

    def _load_or_create_identity(self):
        """Load existing identity or create new one"""
        if os.path.exists(self.identity_file):
            self._load_identity()
        else:
            self._create_identity()

    def _load_identity(self):
        """Load identity from file"""
        try:
            with open(self.identity_file, 'r') as f:
                data = json.load(f)

            self.device_id = data['device_id']
            self.created_at = data['created_at']

            # Load private key
            private_pem = base64.b64decode(data['private_key_pem'])
            self.private_key = serialization.load_pem_private_key(
                private_pem,
                password=None,
                backend=default_backend()
            )

            # Load public key
            public_pem = base64.b64decode(data['public_key_pem'])
            self.public_key = serialization.load_pem_public_key(
                public_pem,
                backend=default_backend()
            )

            logger.info(f"Loaded device identity: {self.device_id}")

        except Exception as e:
            logger.error(f"Failed to load identity: {e}")
            self._create_identity()

    def _create_identity(self):
        """Create new device identity"""
        logger.info("Creating new device identity")

        # Generate Ed25519 key pair
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()

        # Create device ID from public key
        public_bytes = self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
        import hashlib
        self.device_id = hashlib.sha256(public_bytes).hexdigest()

        self.created_at = int(datetime.now().timestamp() * 1000)  # milliseconds

        self._save_identity()
        logger.info(f"Created device identity: {self.device_id}")

    def _save_identity(self):
        """Save identity to file"""
        try:
            os.makedirs(os.path.dirname(self.identity_file), exist_ok=True)

            # Serialize keys
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            public_pem = self.public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            data = {
                'device_id': self.device_id,
                'public_key_pem': base64.b64encode(public_pem).decode('utf-8'),
                'private_key_pem': base64.b64encode(private_pem).decode('utf-8'),
                'created_at': self.created_at
            }

            with open(self.identity_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            logger.error(f"Failed to save identity: {e}")

    def sign_message(self, message: bytes) -> bytes:
        """Sign a message with the private key"""
        return self.private_key.sign(message)

    def verify_signature(self, message: bytes, signature: bytes) -> bool:
        """Verify a signature with the public key"""
        try:
            self.public_key.verify(signature, message)
            return True
        except Exception:
            return False

    def get_public_key_pem(self) -> str:
        """Get public key in PEM format"""
        pem = self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        return pem.decode('utf-8')

    def get_device_info(self) -> dict:
        """Get device information"""
        return {
            'device_id': self.device_id,
            'public_key_pem': self.get_public_key_pem(),
            'created_at_ms': self.created_at
        }