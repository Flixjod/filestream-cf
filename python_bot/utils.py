"""
Cryptographic utilities for secure hash generation
"""
import hmac
import hashlib
import secrets
import string
import base64
from config import config


class Cryptic:
    """Secure hash generation and verification"""
    
    @staticmethod
    def generate_random_token(length: int = 16) -> str:
        """Generate cryptographically secure random token"""
        chars = string.ascii_letters + string.digits
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def hmac_sha256(message: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature"""
        signature = hmac.new(
            secret.encode('utf-8'),
            message.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Convert to URL-safe base64
        return base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    @staticmethod
    def hash_message_id(message_id: str) -> str:
        """
        Generate secure hash: random_token + message_id + HMAC(random_token:message_id, secret)
        Format: randomToken.messageId.signature (URL-safe)
        """
        random_token = Cryptic.generate_random_token(12)
        payload = f"{random_token}:{message_id}"
        signature = Cryptic.hmac_sha256(payload, config.SECRET_KEY)
        
        # Return format: randomToken.messageId.signature (first 32 chars)
        return f"{random_token}.{message_id}.{signature[:32]}"
    
    @staticmethod
    def dehash_message_id(hashed: str) -> str:
        """
        Verify and extract message_id from hash
        Raises ValueError if hash is invalid
        """
        parts = hashed.split('.')
        if len(parts) != 3:
            raise ValueError('Invalid hash format')
        
        random_token, message_id, provided_signature = parts
        
        # Verify HMAC signature
        payload = f"{random_token}:{message_id}"
        expected_signature = Cryptic.hmac_sha256(payload, config.SECRET_KEY)[:32]
        
        if provided_signature != expected_signature:
            raise ValueError('Invalid signature - hash verification failed')
        
        return message_id
    
    @staticmethod
    def generate_secret_token() -> str:
        """Generate a secret token for file access control"""
        return Cryptic.generate_random_token(16)


def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    if not text:
        return 'Unknown File'
    return text.replace('`', "'")


def format_size(bytes_size: int) -> str:
    """Format file size in human-readable format"""
    if bytes_size == 0:
        return '0 B'
    
    sizes = ['B', 'KB', 'MB', 'GB', 'TB']
    k = 1024
    i = 0
    size = float(bytes_size)
    
    while size >= k and i < len(sizes) - 1:
        size /= k
        i += 1
    
    return f"{size:.2f} {sizes[i]}"
