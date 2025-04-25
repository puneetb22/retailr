"""
Create a logo for the Agritech POS System
"""

from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_logo():
    """Create a simple logo for the application"""
    print("Creating logo for Agritech POS System...")
    
    # Ensure assets directory exists
    os.makedirs("assets", exist_ok=True)
    logo_path = Path("assets/logo.png")
    
    # Create a 256x256 image with primary color background
    # #4e73df = (78, 115, 223) - Primary blue color from our styles
    img = Image.new('RGBA', (256, 256), color=(78, 115, 223, 255))
    draw = ImageDraw.Draw(img)
    
    # Create a white rectangle for the text background
    draw.rectangle([(64, 96), (192, 160)], fill=(255, 255, 255, 220))
    
    # Try to use a nice font if available
    try:
        # Try different system fonts
        font_options = ["arial.ttf", "Arial.ttf", "times.ttf", "Times.ttf", "verdana.ttf", "Verdana.ttf"]
        font = None
        
        for font_name in font_options:
            try:
                font = ImageFont.truetype(font_name, 48)
                break
            except:
                continue
                
        if font is None:
            font = ImageFont.load_default()
            
    except:
        # Fallback to default font
        font = ImageFont.load_default()
    
    # Draw POS text
    draw.text((128, 128), "POS", fill=(78, 115, 223, 255), font=font, anchor="mm")
    
    # Draw "Agritech" text above
    small_font = None
    try:
        if font:
            small_font = ImageFont.truetype(font.path, 24)
        else:
            small_font = ImageFont.load_default()
    except:
        small_font = ImageFont.load_default()
    
    draw.text((128, 80), "AGRITECH", fill=(78, 115, 223, 255), font=small_font, anchor="mm")
    
    # Draw a leaf icon simple shape
    leaf_points = [
        (195, 75),  # Tip of leaf
        (175, 95),  # Right curve 
        (205, 105), # Bottom curve
        (165, 85),  # Left curve
    ]
    draw.polygon(leaf_points, fill=(28, 200, 138, 255))  # Green color
    
    # Add curved line for stem
    for i in range(10):
        # Draw a small line segment for the curved stem
        draw.line([(195+i, 75+i), (195+i+1, 75+i+1)], fill=(28, 200, 138, 255), width=2)
    
    # Save the image
    img.save(logo_path)
    print(f"Logo created at {logo_path}")

if __name__ == "__main__":
    create_logo()