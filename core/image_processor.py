"""Image processing operations: resize and crop."""

from PIL import Image
from pathlib import Path


class ImageProcessor:
    """Handles image resize and crop operations."""
    
    def resize_image(self, image_path, max_width, max_height, maintain_aspect=True):
        """
        Resize an image to fit within max dimensions.
        
        Args:
            image_path: Path to the image file
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            maintain_aspect: Whether to maintain aspect ratio (default: True)
        """
        path = Path(image_path)
        
        with Image.open(path) as img:
            if maintain_aspect:
                # Calculate the scaling factor
                width_ratio = max_width / img.width
                height_ratio = max_height / img.height
                scale_factor = min(width_ratio, height_ratio)
                
                # Only downscale, never upscale
                if scale_factor < 1:
                    new_width = int(img.width * scale_factor)
                    new_height = int(img.height * scale_factor)
                    
                    # Resize the image
                    resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Save with same format
                    resized.save(path, img.format)
            else:
                # Force exact dimensions (may distort)
                resized = img.resize((max_width, max_height), Image.Resampling.LANCZOS)
                resized.save(path, img.format)
                
    def crop_center(self, image_path, crop_width, crop_height):
        """
        Crop an image from the center to specified dimensions.
        
        Args:
            image_path: Path to the image file
            crop_width: Target width in pixels
            crop_height: Target height in pixels
        """
        path = Path(image_path)
        
        with Image.open(path) as img:
            # Calculate center crop coordinates
            left = (img.width - crop_width) // 2
            top = (img.height - crop_height) // 2
            right = left + crop_width
            bottom = top + crop_height
            
            # Ensure crop is within bounds
            left = max(0, left)
            top = max(0, top)
            right = min(img.width, right)
            bottom = min(img.height, bottom)
            
            # Crop the image
            cropped = img.crop((left, top, right, bottom))
            
            # Save with same format
            cropped.save(path, img.format)
            
    def crop_custom(self, image_path, left, top, right, bottom):
        """
        Crop an image with custom coordinates.
        
        Args:
            image_path: Path to the image file
            left: Left coordinate
            top: Top coordinate
            right: Right coordinate
            bottom: Bottom coordinate
        """
        path = Path(image_path)
        
        with Image.open(path) as img:
            # Ensure coordinates are within bounds
            left = max(0, min(left, img.width))
            top = max(0, min(top, img.height))
            right = max(left, min(right, img.width))
            bottom = max(top, min(bottom, img.height))
            
            # Crop the image
            cropped = img.crop((left, top, right, bottom))
            
            # Save with same format
            cropped.save(path, img.format)