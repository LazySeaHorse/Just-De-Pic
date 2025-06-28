"""Helper functions for the application."""

import os
from pathlib import Path


def get_file_size_str(file_path):
    """
    Get human-readable file size string.
    
    Args:
        file_path: Path to the file
        
    Returns:
        str: Human-readable file size (e.g., "1.5 MB")
    """
    size = os.path.getsize(file_path)
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.1f} {unit}"
        size /= 1024.0
        
    return f"{size:.1f} TB"
    

def is_image_file(file_path):
    """
    Check if a file is an image based on extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        bool: True if file is an image
    """
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', 
                       '.tiff', '.tif', '.webp', '.ico'}
    
    path = Path(file_path)
    return path.suffix.lower() in image_extensions
    

def create_thumbnail(image_path, size=(150, 150)):
    """
    Create a thumbnail from an image.
    
    Args:
        image_path: Path to the image
        size: Tuple of (width, height) for thumbnail
        
    Returns:
        PIL.Image: Thumbnail image
    """
    from PIL import Image
    
    img = Image.open(image_path)
    img.thumbnail(size)
    return img
    

def safe_filename(filename):
    """
    Create a safe filename by removing/replacing invalid characters.
    
    Args:
        filename: Original filename
        
    Returns:
        str: Safe filename
    """
    invalid_chars = '<>:"/\\|?*'
    
    for char in invalid_chars:
        filename = filename.replace(char, '_')
        
    return filename