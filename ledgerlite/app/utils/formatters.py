"""Utility formatters for currency, dates, and other data display."""

import locale
from typing import Optional
from decimal import Decimal
from datetime import datetime, date
import matplotlib.ticker as ticker


def format_currency(amount: Decimal, symbol: str = "R", show_cents: bool = True) -> str:
    """Format a decimal amount as currency.
    
    Args:
        amount: The amount to format
        symbol: Currency symbol (R, $, etc.)
        show_cents: Whether to show decimal places for large amounts
        
    Returns:
        Formatted currency string
    """
    if amount is None:
        return f"{symbol} 0"
    
    # Convert to float for formatting
    amount_float = float(amount)
    
    # For large amounts, don't show cents
    if abs(amount_float) >= 1000 and not show_cents:
        formatted = f"{amount_float:,.0f}"
    else:
        formatted = f"{amount_float:,.2f}"
    
    # Add thousands separators and currency symbol
    return f"{symbol} {formatted}"


def format_currency_compact(amount: Decimal, symbol: str = "R") -> str:
    """Format currency in compact form (e.g., R1.2K, R1.5M).
    
    Args:
        amount: The amount to format
        symbol: Currency symbol
        
    Returns:
        Compact formatted currency string
    """
    if amount is None:
        return f"{symbol} 0"
    
    amount_float = float(amount)
    abs_amount = abs(amount_float)
    
    if abs_amount >= 1_000_000:
        return f"{symbol} {amount_float / 1_000_000:.1f}M"
    elif abs_amount >= 1_000:
        return f"{symbol} {amount_float / 1_000:.1f}K"
    else:
        return format_currency(amount, symbol, show_cents=True)


def format_number(value: int) -> str:
    """Format a number with thousands separators.
    
    Args:
        value: The number to format
        
    Returns:
        Formatted number string
    """
    if value is None:
        return "0"
    
    return f"{value:,}"


def format_date_display(date_obj: date) -> str:
    """Format a date for display in UI.
    
    Args:
        date_obj: The date to format
        
    Returns:
        Formatted date string
    """
    if date_obj is None:
        return ""
    
    return date_obj.strftime("%d %b %Y")


def format_month_display(month_str: str) -> str:
    """Format a month string for display (YYYY-MM -> Month YYYY).
    
    Args:
        month_str: Month string in YYYY-MM format
        
    Returns:
        Formatted month string
    """
    if not month_str:
        return ""
    
    try:
        year, month = month_str.split('-')
        month_num = int(month)
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        return f"{month_names[month_num - 1]} {year}"
    except (ValueError, IndexError):
        return month_str


def currency_formatter(symbol: str = "R") -> ticker.FuncFormatter:
    """Create a matplotlib currency formatter.
    
    Args:
        symbol: Currency symbol to use
        
    Returns:
        Matplotlib FuncFormatter for currency
    """
    def fmt_func(x: float, pos=None) -> str:
        if abs(x) >= 1000:
            # For large values, don't show decimals
            return f"{symbol} {x:,.0f}"
        else:
            return f"{symbol} {x:,.0f}"
    
    return ticker.FuncFormatter(fmt_func)


def get_currency_symbol() -> str:
    """Get the default currency symbol based on locale or configuration.
    
    Returns:
        Currency symbol string
    """
    # For now, return R (South African Rand)
    # This could be made configurable later
    return "R"


def format_delta(amount: Decimal, symbol: str = "R") -> str:
    """Format a delta amount with appropriate sign and color indication.
    
    Args:
        amount: The delta amount
        symbol: Currency symbol
        
    Returns:
        Formatted delta string with sign
    """
    if amount is None:
        return "±0"
    
    if amount > 0:
        return f"+{format_currency(amount, symbol, show_cents=False)}"
    elif amount < 0:
        return f"-{format_currency(abs(amount), symbol, show_cents=False)}"
    else:
        return "±0"


