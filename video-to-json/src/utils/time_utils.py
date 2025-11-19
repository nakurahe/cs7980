"""Time conversion utilities"""


def ms_to_timestamp(milliseconds: float) -> str:
    """
    Convert milliseconds to timestamp format (HH:MM:SS)
    
    Args:
        milliseconds: Time in milliseconds
        
    Returns:
        Formatted timestamp string (HH:MM:SS)
    """
    seconds = int(milliseconds / 1000)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def timestamp_to_ms(timestamp: str) -> float:
    """
    Convert timestamp format (HH:MM:SS) to milliseconds
    
    Args:
        timestamp: Time in HH:MM:SS format
        
    Returns:
        Time in milliseconds
    """
    parts = timestamp.split(":")
    hours = int(parts[0])
    minutes = int(parts[1])
    seconds = int(parts[2])
    
    total_seconds = hours * 3600 + minutes * 60 + seconds
    return total_seconds * 1000


def format_duration(milliseconds: float) -> str:
    """
    Format duration in a human-readable way
    
    Args:
        milliseconds: Duration in milliseconds
        
    Returns:
        Formatted duration string
    """
    seconds = int(milliseconds / 1000)
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}m {secs}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}h {minutes}m"
