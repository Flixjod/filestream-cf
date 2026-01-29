import hashlib
import hmac
import base64
import secrets
from config import Config

class Cryptic:
    """Cryptographic utilities for secure hashing"""
    
    @staticmethod
    def generate_random_token(length: int = 16) -> str:
        """Generate cryptographically secure random token"""
        chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        return ''.join(secrets.choice(chars) for _ in range(length))
    
    @staticmethod
    def hmac_sha256(message: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature"""
        key = secret.encode('utf-8')
        msg = message.encode('utf-8')
        signature = hmac.new(key, msg, hashlib.sha256).digest()
        # URL-safe base64 encoding
        return base64.urlsafe_b64encode(signature).decode('utf-8').rstrip('=')
    
    @staticmethod
    def hash(text: str) -> str:
        """
        Generate secure hash: random_token + message_id + HMAC(random_token:message_id, secret)
        Format: randomToken.messageId.signature
        """
        random_token = Cryptic.generate_random_token(12)
        payload = f"{random_token}:{text}"
        signature = Cryptic.hmac_sha256(payload, Config.SIA_SECRET)
        return f"{random_token}.{text}.{signature[:32]}"
    
    @staticmethod
    def dehash(hashed: str) -> str:
        """Verify and extract message_id from hash"""
        parts = hashed.split('.')
        if len(parts) != 3:
            raise ValueError('Invalid hash format')
        
        random_token, message_id, provided_signature = parts
        
        # Verify HMAC signature
        payload = f"{random_token}:{message_id}"
        expected_signature = Cryptic.hmac_sha256(payload, Config.SIA_SECRET)[:32]
        
        if provided_signature != expected_signature:
            raise ValueError('Invalid signature - hash verification failed')
        
        return message_id

def format_size(bytes_size: int) -> str:
    """Format file size in human-readable format"""
    if bytes_size == 0:
        return '0 B'
    
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    k = 1024
    i = 0
    size = float(bytes_size)
    
    while size >= k and i < len(units) - 1:
        size /= k
        i += 1
    
    return f"{size:.2f} {units[i]}"

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    if not text:
        return 'Unknown File'
    return text.replace('`', "'")

def generate_secret_token(length: int = 16) -> str:
    """Generate a secret token for file revocation"""
    return Cryptic.generate_random_token(length)
