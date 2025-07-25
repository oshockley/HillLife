from PIL import Image, ImageDraw, ImageFont
import os

def create_app_icons():
    """Create app icons for Hill Life PWA"""
    
    # Create icons directory
    os.makedirs('static/icons', exist_ok=True)
    
    # Icon sizes needed
    sizes = [16, 32, 72, 96, 128, 144, 152, 192, 384, 512]
    
    # Create a simple mountain icon
    for size in sizes:
        # Create image with sunset gradient background
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Draw gradient background circle
        for i in range(size):
            color_ratio = i / size
            r = int(255 * (1 - color_ratio * 0.3))  # ff to cc
            g = int(126 + (180 - 126) * color_ratio)  # 7e to b4
            b = int(95 + (123 - 95) * color_ratio)   # 5f to 7b
            draw.ellipse([i//4, i//4, size-i//4, size-i//4], fill=(r, g, b, 255))
        
        # Draw mountain shape
        mountain_color = (255, 255, 255, 200)
        center_x = size // 2
        center_y = size // 2
        
        # Mountain peaks
        peak_height = size // 3
        peak_width = size // 4
        
        # Main peak
        draw.polygon([
            (center_x - peak_width, center_y + peak_height//2),
            (center_x, center_y - peak_height//2),
            (center_x + peak_width, center_y + peak_height//2)
        ], fill=mountain_color)
        
        # Left peak
        draw.polygon([
            (center_x - peak_width*1.5, center_y + peak_height//2),
            (center_x - peak_width//2, center_y),
            (center_x, center_y + peak_height//2)
        ], fill=mountain_color)
        
        # Right peak
        draw.polygon([
            (center_x, center_y + peak_height//2),
            (center_x + peak_width//2, center_y),
            (center_x + peak_width*1.5, center_y + peak_height//2)
        ], fill=mountain_color)
        
        img.save(f'static/icons/icon-{size}x{size}.png', 'PNG')
        print(f'Created icon-{size}x{size}.png')

if __name__ == '__main__':
    create_app_icons()
    print('All app icons created successfully!')
