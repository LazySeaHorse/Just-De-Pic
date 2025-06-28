"""Metadata handling for various image formats."""

import piexif
from PIL import Image
from pathlib import Path
import json


class MetadataHandler:
    """Handles reading, writing, and removing image metadata."""
    
    def get_all_metadata(self, image_path):
        """
        Get all metadata from an image file.
        
        Returns:
            dict: Dictionary containing metadata categories and their fields
        """
        metadata = {
            "EXIF": {},
            "IPTC": {},
            "XMP": {},
            "Basic": {}
        }
        
        try:
            # Open image with PIL
            with Image.open(image_path) as img:
                # Get basic info
                metadata["Basic"]["Format"] = img.format
                metadata["Basic"]["Mode"] = img.mode
                metadata["Basic"]["Size"] = f"{img.width}x{img.height}"
                
                # Get EXIF data
                if img.format in ['JPEG', 'TIFF']:
                    exif_dict = piexif.load(image_path)
                    
                    # Process each IFD
                    for ifd_name in exif_dict:
                        if ifd_name == "thumbnail":
                            continue
                            
                        ifd_data = exif_dict[ifd_name]
                        for tag, value in ifd_data.items():
                            # Get tag name
                            tag_name = piexif.TAGS[ifd_name].get(tag, {}).get("name", f"Tag_{tag}")
                            
                            # Convert bytes to string if needed
                            if isinstance(value, bytes):
                                try:
                                    value = value.decode('utf-8', errors='ignore')
                                except:
                                    value = str(value)
                                    
                            metadata["EXIF"][tag_name] = value
                            
                # Get other metadata from PIL info
                info = img.info
                for key, value in info.items():
                    if key not in metadata["EXIF"]:
                        metadata["XMP"][key] = str(value)
                        
        except Exception as e:
            print(f"Error reading metadata: {e}")
            
        # Remove empty categories
        metadata = {k: v for k, v in metadata.items() if v}
        
        return metadata
        
    def has_metadata(self, image_path):
        """Check if an image has any metadata."""
        try:
            metadata = self.get_all_metadata(image_path)
            # Check if any category has data (besides Basic)
            for category, data in metadata.items():
                if category != "Basic" and data:
                    return True
            return False
        except:
            return False
            
    def remove_all_metadata(self, image_path):
        """Remove all metadata from an image file."""
        path = Path(image_path)
        
        try:
            # Open and save image without metadata
            with Image.open(path) as img:
                # Create a clean copy without metadata
                clean_img = Image.new(img.mode, img.size)
                clean_img.putdata(list(img.getdata()))
                
                # Save without metadata
                if img.format == 'JPEG':
                    clean_img.save(path, 'JPEG', quality=95)
                elif img.format == 'PNG':
                    clean_img.save(path, 'PNG')
                else:
                    clean_img.save(path, img.format)
                    
        except Exception as e:
            # Alternative method using piexif for JPEG
            if path.suffix.lower() in ['.jpg', '.jpeg']:
                piexif.remove(str(path))
            else:
                raise e
                
    def update_metadata(self, image_path, metadata_dict):
        """
        Update metadata in an image file.
        
        Args:
            image_path: Path to the image file
            metadata_dict: Dictionary containing metadata to update
        """
        path = Path(image_path)
        
        try:
            if path.suffix.lower() in ['.jpg', '.jpeg']:
                # Load existing EXIF
                exif_dict = piexif.load(str(path))
                
                # Update EXIF data
                if "EXIF" in metadata_dict:
                    for field, value in metadata_dict["EXIF"].items():
                        # Find the appropriate IFD and tag
                        for ifd_name in ["0th", "Exif", "GPS", "1st"]:
                            for tag, tag_info in piexif.TAGS[ifd_name].items():
                                if tag_info.get("name") == field:
                                    # Convert value to appropriate type
                                    if isinstance(value, str):
                                        value = value.encode('utf-8')
                                    exif_dict[ifd_name][tag] = value
                                    break
                                    
                # Save with updated EXIF
                exif_bytes = piexif.dump(exif_dict)
                piexif.insert(exif_bytes, str(path))
                
        except Exception as e:
            print(f"Error updating metadata: {e}")