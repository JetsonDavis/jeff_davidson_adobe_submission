"""
Color extraction service for extracting brand colors from images.
"""
from pathlib import Path
from typing import List
from PIL import Image
from collections import Counter


class ColorExtractor:
    """Extracts dominant colors from brand asset images"""
    
    def extract_colors(self, image_path: str, num_colors: int = 5) -> List[str]:
        """
        Extract dominant colors from an image.
        
        Args:
            image_path: Path to image file
            num_colors: Number of colors to extract
        
        Returns:
            List of hex color codes
        """
        try:
            # Open image and resize for faster processing
            img = Image.open(image_path)
            img = img.convert('RGB')
            img = img.resize((150, 150))
            
            # Get all pixels
            pixels = list(img.getdata())
            
            # Count color frequency
            color_counter = Counter(pixels)
            
            # Get most common colors
            common_colors = color_counter.most_common(num_colors)
            
            # Convert RGB to hex
            hex_colors = [self._rgb_to_hex(rgb) for rgb, count in common_colors]
            
            return hex_colors
        
        except Exception as e:
            print(f"Error extracting colors from {image_path}: {e}")
            return []
    
    def _rgb_to_hex(self, rgb: tuple) -> str:
        """Convert RGB tuple to hex color code"""
        return '#{:02x}{:02x}{:02x}'.format(rgb[0], rgb[1], rgb[2])


# Singleton instance
color_extractor = ColorExtractor()
