"""
PII (Personally Identifiable Information) masking utilities.
"""
import re
from typing import Any, Dict, List, Union


class PIIMasker:
    """PII masking utility for sensitive data."""
    
    def __init__(self):
        # Email patterns
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        
        # Phone patterns (Swedish + international)
        self.phone_patterns = [
            re.compile(r'\+46\s*\d{1,2}\s*\d{3}\s*\d{2}\s*\d{2}'),  # +46 70 123 45 67
            re.compile(r'0\d{1,2}\s*\d{3}\s*\d{2}\s*\d{2}'),        # 070 123 45 67
            re.compile(r'\+1\s*\d{3}\s*\d{3}\s*\d{4}'),             # +1 555 123 4567
        ]
        
        # JWT token pattern (3 parts, base64)
        self.jwt_pattern = re.compile(r'eyJ[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+')
        
        # OAuth codes
        self.oauth_pattern = re.compile(r'[A-Za-z0-9]{32,}')
        
        # IBAN patterns
        self.iban_pattern = re.compile(r'\b[A-Z]{2}[0-9]{2}[A-Z0-9]{4}[0-9]{7}([A-Z0-9]?){0,16}\b')
        
        # Credit card patterns
        self.credit_card_pattern = re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b')
        
        # API keys (common patterns)
        self.api_key_patterns = [
            re.compile(r'sk-[A-Za-z0-9]{48}'),  # OpenAI style
            re.compile(r'[A-Za-z0-9]{32,}'),    # Generic long keys
        ]
    
    def mask_email(self, text: str) -> str:
        """Mask email addresses."""
        def mask_email(match):
            email = match.group(0)
            username, domain = email.split('@')
            masked_username = username[:2] + '*' * (len(username) - 2)
            masked_domain = domain[:2] + '*' * (len(domain) - 2)
            return f"{masked_username}@{masked_domain}"
        
        return self.email_pattern.sub(mask_email, text)
    
    def mask_phone(self, text: str) -> str:
        """Mask phone numbers."""
        def mask_phone(match):
            phone = match.group(0)
            # Keep first 3 and last 2 digits
            if len(phone) >= 8:
                return phone[:3] + '*' * (len(phone) - 5) + phone[-2:]
            return '*' * len(phone)
        
        for pattern in self.phone_patterns:
            text = pattern.sub(mask_phone, text)
        return text
    
    def mask_jwt(self, text: str) -> str:
        """Mask JWT tokens."""
        def mask_jwt(match):
            jwt = match.group(0)
            parts = jwt.split('.')
            if len(parts) == 3:
                # Keep first 8 chars of header and payload, mask signature
                header = parts[0][:8] + '...'
                payload = parts[1][:8] + '...'
                signature = '*' * 20
                return f"{header}.{payload}.{signature}"
            return '*' * len(jwt)
        
        return self.jwt_pattern.sub(mask_jwt, text)
    
    def mask_oauth(self, text: str) -> str:
        """Mask OAuth codes."""
        def mask_oauth(match):
            code = match.group(0)
            if len(code) >= 8:
                return code[:4] + '*' * (len(code) - 8) + code[-4:]
            return '*' * len(code)
        
        return self.oauth_pattern.sub(mask_oauth, text)
    
    def mask_iban(self, text: str) -> str:
        """Mask IBAN numbers."""
        def mask_iban(match):
            iban = match.group(0)
            if len(iban) >= 8:
                return iban[:4] + '*' * (len(iban) - 8) + iban[-4:]
            return '*' * len(iban)
        
        return self.iban_pattern.sub(mask_iban, text)
    
    def mask_credit_card(self, text: str) -> str:
        """Mask credit card numbers."""
        def mask_credit_card(match):
            card = match.group(0)
            # Keep first 4 and last 4 digits
            if len(card) >= 8:
                return card[:4] + '*' * (len(card) - 8) + card[-4:]
            return '*' * len(card)
        
        return self.credit_card_pattern.sub(mask_credit_card, text)
    
    def mask_api_keys(self, text: str) -> str:
        """Mask API keys."""
        def mask_api_key(match):
            key = match.group(0)
            if len(key) >= 8:
                return key[:4] + '*' * (len(key) - 8) + key[-4:]
            return '*' * len(key)
        
        for pattern in self.api_key_patterns:
            text = pattern.sub(mask_api_key, text)
        return text
    
    def mask_all(self, text: str) -> str:
        """Apply all PII masking."""
        text = self.mask_email(text)
        text = self.mask_phone(text)
        text = self.mask_jwt(text)
        text = self.mask_oauth(text)
        text = self.mask_iban(text)
        text = self.mask_credit_card(text)
        text = self.mask_api_keys(text)
        return text
    
    def mask_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively mask PII in dictionary."""
        masked_data = {}
        
        for key, value in data.items():
            if isinstance(value, str):
                masked_data[key] = self.mask_all(value)
            elif isinstance(value, dict):
                masked_data[key] = self.mask_dict(value)
            elif isinstance(value, list):
                masked_data[key] = [self.mask_dict(item) if isinstance(item, dict) else 
                                  self.mask_all(item) if isinstance(item, str) else item 
                                  for item in value]
            else:
                masked_data[key] = value
        
        return masked_data


# Global PII masker instance
pii_masker = PIIMasker()
