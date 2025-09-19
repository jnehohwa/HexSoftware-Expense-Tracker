"""Date utility functions for LedgerLite."""

from datetime import datetime, timedelta
from typing import Tuple


def get_month_date_range(month: str) -> Tuple[datetime, datetime]:
    """Get start and end dates for a given month.
    
    Args:
        month: Month in YYYY-MM format.
        
    Returns:
        Tuple of (start_date, end_date).
    """
    year, month_num = map(int, month.split("-"))
    start_date = datetime(year, month_num, 1)
    
    # Calculate end date (last day of month)
    if month_num == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = datetime(year, month_num + 1, 1) - timedelta(days=1)
    
    return start_date, end_date


def get_previous_month(month: str) -> str:
    """Get the previous month.
    
    Args:
        month: Month in YYYY-MM format.
        
    Returns:
        Previous month in YYYY-MM format.
    """
    year, month_num = map(int, month.split("-"))
    if month_num == 1:
        return f"{year - 1}-12"
    else:
        return f"{year}-{month_num - 1:02d}"


def get_next_month(month: str) -> str:
    """Get the next month.
    
    Args:
        month: Month in YYYY-MM format.
        
    Returns:
        Next month in YYYY-MM format.
    """
    year, month_num = map(int, month.split("-"))
    if month_num == 12:
        return f"{year + 1}-01"
    else:
        return f"{year}-{month_num + 1:02d}"


def format_month_display(month: str) -> str:
    """Format month for display.
    
    Args:
        month: Month in YYYY-MM format.
        
    Returns:
        Formatted month string (e.g., "January 2024").
    """
    year, month_num = map(int, month.split("-"))
    date = datetime(year, month_num, 1)
    return date.strftime("%B %Y")


def parse_date_string(date_str: str) -> datetime:
    """Parse various date string formats.
    
    Args:
        date_str: Date string in various formats.
        
    Returns:
        Parsed datetime object.
        
    Raises:
        ValueError: If date string cannot be parsed.
    """
    formats = [
        "%Y-%m-%d",      # 2024-01-15
        "%d/%m/%Y",      # 15/01/2024
        "%m/%d/%Y",      # 01/15/2024
        "%d-%m-%Y",      # 15-01-2024
        "%Y/%m/%d",      # 2024/01/15
    ]
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    
    raise ValueError(f"Unable to parse date string: {date_str}")


def is_same_day(date1: datetime, date2: datetime) -> bool:
    """Check if two dates are on the same day.
    
    Args:
        date1: First date.
        date2: Second date.
        
    Returns:
        True if dates are on the same day.
    """
    return date1.date() == date2.date()


def get_days_in_month(month: str) -> int:
    """Get number of days in a month.
    
    Args:
        month: Month in YYYY-MM format.
        
    Returns:
        Number of days in the month.
    """
    start_date, end_date = get_month_date_range(month)
    return (end_date - start_date).days + 1


def get_current_month() -> str:
    """Get current month in YYYY-MM format.
    
    Returns:
        Current month in YYYY-MM format.
    """
    now = datetime.now()
    return now.strftime("%Y-%m")


def get_months_list(start_month: str, count: int) -> list[str]:
    """Get a list of months starting from a given month.
    
    Args:
        start_month: Starting month in YYYY-MM format.
        count: Number of months to include.
        
    Returns:
        List of months in YYYY-MM format.
    """
    months = []
    current = start_month
    
    for _ in range(count):
        months.append(current)
        current = get_next_month(current)
    
    return months


