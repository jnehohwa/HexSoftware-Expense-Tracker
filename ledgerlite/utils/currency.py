"""Currency utility functions for LedgerLite."""

from decimal import Decimal
from typing import Union


def format_currency(amount: Union[Decimal, float, int], currency: str = "USD") -> str:
    """Format amount as currency string.
    
    Args:
        amount: Amount to format.
        currency: Currency code (default: USD).
        
    Returns:
        Formatted currency string.
    """
    if currency == "USD":
        return f"${amount:,.2f}"
    elif currency == "EUR":
        return f"€{amount:,.2f}"
    elif currency == "GBP":
        return f"£{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"


def format_amount_with_sign(amount: Union[Decimal, float, int], transaction_type: str = "expense") -> str:
    """Format amount with appropriate sign and color.
    
    Args:
        amount: Amount to format.
        transaction_type: Type of transaction (expense or income).
        
    Returns:
        Formatted amount string with sign.
    """
    if transaction_type == "income":
        return f"+${amount:,.2f}"
    else:
        return f"-${amount:,.2f}"


def parse_currency_string(currency_str: str) -> Decimal:
    """Parse currency string to Decimal.
    
    Args:
        currency_str: Currency string (e.g., "$123.45", "-$67.89").
        
    Returns:
        Parsed amount as Decimal.
        
    Raises:
        ValueError: If currency string cannot be parsed.
    """
    # Remove currency symbols and whitespace
    cleaned = currency_str.replace("$", "").replace("€", "").replace("£", "").replace(",", "").strip()
    
    try:
        return Decimal(cleaned)
    except Exception as e:
        raise ValueError(f"Unable to parse currency string: {currency_str}") from e


def get_amount_color(amount: Union[Decimal, float, int], transaction_type: str = "expense") -> str:
    """Get color for amount based on transaction type.
    
    Args:
        amount: Amount value.
        transaction_type: Type of transaction (expense or income).
        
    Returns:
        Color hex code.
    """
    if transaction_type == "income":
        return "#34c759"  # Green
    else:
        return "#ff3b30"  # Red


def is_positive_amount(amount: Union[Decimal, float, int]) -> bool:
    """Check if amount is positive.
    
    Args:
        amount: Amount to check.
        
    Returns:
        True if amount is positive.
    """
    return float(amount) > 0


def is_negative_amount(amount: Union[Decimal, float, int]) -> bool:
    """Check if amount is negative.
    
    Args:
        amount: Amount to check.
        
    Returns:
        True if amount is negative.
    """
    return float(amount) < 0


def get_net_amount(income: Union[Decimal, float, int], expense: Union[Decimal, float, int]) -> Decimal:
    """Calculate net amount (income - expense).
    
    Args:
        income: Total income amount.
        expense: Total expense amount.
        
    Returns:
        Net amount as Decimal.
    """
    return Decimal(str(income)) - Decimal(str(expense))


def get_percentage_change(old_amount: Union[Decimal, float, int], new_amount: Union[Decimal, float, int]) -> float:
    """Calculate percentage change between two amounts.
    
    Args:
        old_amount: Original amount.
        new_amount: New amount.
        
    Returns:
        Percentage change (positive for increase, negative for decrease).
    """
    if old_amount == 0:
        return 0.0 if new_amount == 0 else 100.0
    
    return ((float(new_amount) - float(old_amount)) / float(old_amount)) * 100


def format_percentage_change(percentage: float) -> str:
    """Format percentage change for display.
    
    Args:
        percentage: Percentage change value.
        
    Returns:
        Formatted percentage string with sign and color indicator.
    """
    if percentage > 0:
        return f"+{percentage:.1f}%"
    elif percentage < 0:
        return f"{percentage:.1f}%"
    else:
        return "0.0%"


