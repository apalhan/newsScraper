"""
Secure Secrets Management for NYT API
Handles API keys and sensitive configuration data
"""

import base64
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from cryptography.fernet import Fernet


class SecretsManager:
    """Secure secrets management with encryption support"""
    
    def __init__(self, secrets_file: str = "nyt_secrets.json", key_file: str = ".secret_key"):
        self.secrets_file = Path(secrets_file)
        self.key_file = Path(key_file)
        self.encryption_key = None
        self.secrets = {}
        self.load_encryption_key()
        self.load_secrets()
    
    def load_encryption_key(self):
        """Load or generate encryption key"""
        if self.key_file.exists():
            with open(self.key_file, 'rb') as f:
                self.encryption_key = f.read()
        else:
            # Generate new key for first time
            self.encryption_key = Fernet.generate_key()
            with open(self.key_file, 'wb') as f:
                f.write(self.encryption_key)
            # Make key file read-only for owner
            os.chmod(self.key_file, 0o600)
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt a string value"""
        if not self.encryption_key:
            return value
        f = Fernet(self.encryption_key)
        return f.encrypt(value.encode()).decode()
    
    def decrypt_value(self, encrypted_value: str) -> str:
        """Decrypt a string value"""
        if not self.encryption_key:
            return encrypted_value
        try:
            f = Fernet(self.encryption_key)
            return f.decrypt(encrypted_value.encode()).decode()
        except Exception:
            return encrypted_value
    
    def load_secrets(self):
        """Load secrets from file or environment variables"""
        # Priority: Environment variables > Encrypted file > Plain file
        self.secrets = {}
        
        # Load from environment variables first
        env_keys = ['NYT_API_KEY', 'OPENAI_API_KEY', 'DATABASE_URL']
        for key in env_keys:
            env_value = os.getenv(key)
            if env_value:
                self.secrets[key.lower()] = env_value
        
        # Load from secrets file if it exists
        if self.secrets_file.exists():
            try:
                with open(self.secrets_file, 'r') as f:
                    file_secrets = json.load(f)
                    
                # Check if values are encrypted (contain 'encrypted:' prefix)
                for key, value in file_secrets.items():
                    if isinstance(value, str) and value.startswith('encrypted:'):
                        decrypted_value = self.decrypt_value(value[10:])  # Remove 'encrypted:' prefix
                        self.secrets[key] = decrypted_value
                    else:
                        self.secrets[key] = value
                        
            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Could not load secrets file: {e}")
    
    def save_secrets(self, encrypt: bool = True):
        """Save secrets to file with optional encryption"""
        if not self.secrets:
            return
        
        secrets_to_save = {}
        for key, value in self.secrets.items():
            if encrypt and self.encryption_key:
                encrypted_value = self.encrypt_value(value)
                secrets_to_save[key] = f"encrypted:{encrypted_value}"
            else:
                secrets_to_save[key] = value
        
        try:
            with open(self.secrets_file, 'w') as f:
                json.dump(secrets_to_save, f, indent=2)
            
            # Make secrets file read-only for owner
            os.chmod(self.secrets_file, 0o600)
            print(f"Secrets saved to {self.secrets_file}")
            
        except Exception as e:
            print(f"Error saving secrets: {e}")
    
    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret value"""
        return self.secrets.get(key.lower(), default)
    
    def set_secret(self, key: str, value: str, save: bool = True):
        """Set a secret value"""
        self.secrets[key.lower()] = value
        if save:
            self.save_secrets()
    
    def is_configured(self, key: str = 'nyt_api_key') -> bool:
        """Check if a secret is properly configured"""
        value = self.get_secret(key)
        return value is not None and value != 'your_api_key_here' and len(value) > 10
    
    def setup_interactive(self):
        """Interactive setup for API keys"""
        print("🔐 NYT API Configuration Setup")
        print("=" * 40)
        
        # NYT API Key
        if not self.is_configured('nyt_api_key'):
            print("\n📰 New York Times API Key")
            print("Get your free API key from: https://developer.nytimes.com/")
            api_key = input("Enter your NYT API key: ").strip()
            if api_key:
                self.set_secret('nyt_api_key', api_key)
                print("✅ NYT API key configured!")
            else:
                print("❌ No API key provided")
        else:
            print("✅ NYT API key already configured")
        
        # Optional: Other API keys
        other_apis = {
            'openai_api_key': 'OpenAI API Key (optional)',
            'database_url': 'Database URL (optional)'
        }
        
        for key, description in other_apis.items():
            if not self.is_configured(key):
                print(f"\n{description}")
                value = input(f"Enter {key}: ").strip()
                if value:
                    self.set_secret(key, value)
                    print(f"✅ {key} configured!")
        
        print("\n🎉 Configuration complete!")
        print(f"Secrets saved to: {self.secrets_file}")
        print("Remember to add .secret_key and nyt_secrets.json to .gitignore!")

# Global secrets manager instance
secrets = SecretsManager()

# Convenience functions
def get_nyt_api_key() -> Optional[str]:
    """Get NYT API key from secrets manager"""
    return secrets.get_secret('nyt_api_key')

def is_nyt_configured() -> bool:
    """Check if NYT API is configured"""
    return secrets.is_configured('nyt_api_key')

def setup_api_keys():
    """Interactive API key setup"""
    secrets.setup_interactive()
