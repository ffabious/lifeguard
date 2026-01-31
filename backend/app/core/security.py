import hashlib
import hmac
import json
from urllib.parse import parse_qsl
from typing import Optional

from app.core.config import settings


def validate_telegram_data(init_data: str) -> Optional[dict]:
    """
    Validate Telegram Web App init data.
    
    The init_data is a query string that contains user data and a hash.
    We validate it by computing HMAC-SHA256 of the data using the bot token.
    
    Returns user data dict if valid, None otherwise.
    """
    if not init_data:
        return None

    try:
        # Parse the init_data query string
        parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))
        
        # Extract the hash
        received_hash = parsed_data.pop("hash", None)
        if not received_hash:
            return None

        # Create data-check-string
        # Sort all key-value pairs alphabetically by key
        data_check_string = "\n".join(
            f"{k}={v}" for k, v in sorted(parsed_data.items())
        )

        # Create secret key using HMAC-SHA256 of bot token with "WebAppData"
        secret_key = hmac.new(
            key=b"WebAppData",
            msg=settings.telegram_bot_token.encode(),
            digestmod=hashlib.sha256,
        ).digest()

        # Calculate hash of data-check-string
        calculated_hash = hmac.new(
            key=secret_key,
            msg=data_check_string.encode(),
            digestmod=hashlib.sha256,
        ).hexdigest()

        # Compare hashes
        if not hmac.compare_digest(calculated_hash, received_hash):
            return None

        # Parse user data
        user_data = parsed_data.get("user")
        if user_data:
            parsed_data["user"] = json.loads(user_data)

        return parsed_data

    except Exception:
        return None


def get_telegram_user_from_init_data(init_data: str) -> Optional[dict]:
    """
    Extract and validate user data from Telegram init_data.
    
    Returns user dict with id, first_name, last_name, username, etc.
    """
    validated_data = validate_telegram_data(init_data)
    if validated_data and "user" in validated_data:
        return validated_data["user"]
    return None
