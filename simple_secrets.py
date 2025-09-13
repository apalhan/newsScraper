"""
Simple Secrets Management (without encryption)
For quick setup and development
"""

import os
import json
from pathlib import Path
from typing import Optional

class SimpleSecrets:
    """Simple secrets manager without encryption"""
    
    def __init__(self, secrets_file: str = "nyt_secrets.json"):
        self.secrets_file = Path(secrets_file)
        self.secrets = {}
        self.load_secrets()
    
    def load_secrets(self):
        """Load secrets from file or environment variables"""
        # Priority: Environment variables > Secrets file
        self.secrets = {}
        
        # Load from environment variables first
        env_value = os.getenv('NYT_API_KEY')
        if env_value:
            self.secrets['nyt_api_key'] = env_value
        
        # Load from secrets file if it exists
        if self.secrets_file.exists():
            try:
                with open(self.secrets_file, 'r') as f:
                    file_secrets = json.load(f)
                    self.secrets.update(file_secrets)
            except (json.JSONDecodeError, Exception) as e:
                print(f"Warning: Could not load secrets file: {e}")
    
    def save_secrets(self):
        """Save secrets to file"""
        if not self.secrets:
            return
        
        try:
            with open(self.secrets_file, 'w') as f:
                json.dump(self.secrets, f, indent=2)
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

# Global secrets manager instance
secrets = SimpleSecrets()

# Convenience functions
def get_nyt_api_key() -> Optional[str]:
    """Get NYT API key from secrets manager"""
    return secrets.get_secret('nyt_api_key')

def is_nyt_configured() -> bool:
    """Check if NYT API is configured"""
    return secrets.is_configured('nyt_api_key')
