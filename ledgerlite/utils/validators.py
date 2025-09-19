"""Validation utility functions for LedgerLite."""

import re
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple, Union


def validate_amount(amount_str: str) -> Tuple[bool, Optional[Decimal], Optional[str]]:
    """Validate amount string.
    
    Args:
        amount_str: Amount string to validate.
        
    Returns:
        Tuple of (is_valid, parsed_amount, error_message).
    """
    if not amount_str or not amount_str.strip():
        return False, None, "Amount cannot be empty"
    
    try:
        # Remove currency symbols and whitespace
        cleaned = amount_str.replace("$", "").replace("€", "").replace("£", "").replace(",", "").strip()
        amount = Decimal(cleaned)
        
        if amount <= 0:
            return False, None, "Amount must be greater than zero"
        
        return True, amount, None
        
    except InvalidOperation:
        return False, None, "Invalid amount format"


def validate_date_string(date_str: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """Validate date string.
    
    Args:
        date_str: Date string to validate.
        
    Returns:
        Tuple of (is_valid, error_message, None).
    """
    if not date_str or not date_str.strip():
        return False, "Date cannot be empty", None
    
    # Check for common date patterns
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',      # YYYY-MM-DD
        r'^\d{2}/\d{2}/\d{4}$',      # DD/MM/YYYY or MM/DD/YYYY
        r'^\d{2}-\d{2}-\d{4}$',      # DD-MM-YYYY
        r'^\d{4}/\d{2}/\d{2}$',      # YYYY/MM/DD
    ]
    
    for pattern in patterns:
        if re.match(pattern, date_str.strip()):
            return True, None, None
    
    return False, "Invalid date format. Use YYYY-MM-DD, DD/MM/YYYY, or DD-MM-YYYY", None


def validate_email(email: str) -> bool:
    """Validate email address.
    
    Args:
        email: Email address to validate.
        
    Returns:
        True if email is valid.
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_category_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate category name.
    
    Args:
        name: Category name to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not name or not name.strip():
        return False, "Category name cannot be empty"
    
    if len(name.strip()) > 100:
        return False, "Category name must be 100 characters or less"
    
    # Check for invalid characters
    if re.search(r'[<>:"/\\|?*]', name):
        return False, "Category name contains invalid characters"
    
    return True, None


def validate_account_name(name: str) -> Tuple[bool, Optional[str]]:
    """Validate account name.
    
    Args:
        name: Account name to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not name or not name.strip():
        return False, "Account name cannot be empty"
    
    if len(name.strip()) > 100:
        return False, "Account name must be 100 characters or less"
    
    return True, None


def validate_color_hex(color_hex: str) -> Tuple[bool, Optional[str]]:
    """Validate hex color code.
    
    Args:
        color_hex: Hex color code to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not color_hex:
        return False, "Color cannot be empty"
    
    # Remove # if present
    if color_hex.startswith('#'):
        color_hex = color_hex[1:]
    
    # Check if it's a valid hex color
    if not re.match(r'^[0-9A-Fa-f]{6}$', color_hex):
        return False, "Invalid hex color format. Use #RRGGBB"
    
    return True, None


def validate_note(note: str) -> Tuple[bool, Optional[str]]:
    """Validate transaction note.
    
    Args:
        note: Note text to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if note and len(note) > 1000:
        return False, "Note must be 1000 characters or less"
    
    return True, None


def validate_month_string(month: str) -> Tuple[bool, Optional[str]]:
    """Validate month string in YYYY-MM format.
    
    Args:
        month: Month string to validate.
        
    Returns:
        Tuple of (is_valid, error_message).
    """
    if not month:
        return False, "Month cannot be empty"
    
    pattern = r'^\d{4}-\d{2}$'
    if not re.match(pattern, month):
        return False, "Invalid month format. Use YYYY-MM"
    
    try:
        year, month_num = map(int, month.split("-"))
        if not (1 <= month_num <= 12):
            return False, "Month must be between 01 and 12"
        
        if not (1900 <= year <= 2100):
            return False, "Year must be between 1900 and 2100"
        
        return True, None
        
    except ValueError:
        return False, "Invalid month format. Use YYYY-MM"


def validate_budget_amount(amount: Union[Decimal, float, int, str]) -> Tuple[bool, Optional[Decimal], Optional[str]]:
    """Validate budget amount.
    
    Args:
        amount: Budget amount to validate.
        
    Returns:
        Tuple of (is_valid, parsed_amount, error_message).
    """
    if isinstance(amount, str):
        is_valid, parsed_amount, error = validate_amount(amount)
        return is_valid, parsed_amount, error
    
    try:
        amount_decimal = Decimal(str(amount))
        if amount_decimal <= 0:
            return False, None, "Budget amount must be greater than zero"
        
        return True, amount_decimal, None
        
    except (InvalidOperation, ValueError):
        return False, None, "Invalid budget amount"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage.
    
    Args:
        filename: Original filename.
        
    Returns:
        Sanitized filename.
    """
    # Remove or replace invalid characters
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Remove leading/trailing whitespace and dots
    sanitized = sanitized.strip('. ')
    
    # Limit length
    if len(sanitized) > 255:
        name, ext = sanitized.rsplit('.', 1) if '.' in sanitized else (sanitized, '')
        sanitized = name[:255-len(ext)-1] + ('.' + ext if ext else '')
    
    return sanitized or "untitled"
