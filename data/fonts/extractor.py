import string
import os
from PIL import Image, ImageFont, ImageDraw
from enum import Enum

def measure_font_metrics(font, chars_to_check):
    """Funkcja do mierzenia rzeczywistych wymiarów zestawu znaków"""
    max_ascent = 0
    max_descent = 0
    for char in chars_to_check:
        _, top, _, bottom = font.getbbox(char)
        if -top > max_ascent:
            max_ascent = -top
        if bottom > max_descent:
            max_descent = bottom

    content_height = max_ascent + max_descent
    
    return max_ascent, max_descent, content_height

def extract(type_folder, font_name):
    """
    Wyodrębnia znaki z czcionki, automatycznie dopasowując rozmiar,
    aby zmieściły się w obrazku o stałej wysokości
    """
    chars_to_extract = string.ascii_lowercase + string.digits + ".,?!"
    
    target_image_height = 48
    font_path = os.path.join("src", type_folder, font_name)

    font_size_guess = target_image_height
    
    font = ImageFont.truetype(font_path, size=font_size_guess)

    # mierzymy
    _, _, initial_content_height = measure_font_metrics(font, chars_to_extract)

    # jeśli za duża, obliczamy nowy rozmiar
    if initial_content_height > target_image_height:
        scale_factor = target_image_height / initial_content_height
        final_font_size = int(font_size_guess * scale_factor)
        
        print(f"  -> Font too large. Resizing from {font_size_guess}pt to {final_font_size}pt to fit.")
        
        # ładujemy czcionkę ponownie z nowym, mniejszym rozmiarem
        font = ImageFont.truetype(font_path, size=final_font_size)
    else:
        final_font_size = font_size_guess

    max_ascent, _, content_height = measure_font_metrics(font, chars_to_extract)
    
    # margines górny
    top_margin = (target_image_height - content_height) // 2
    
    # pozycja linii bazowej
    canvas_baseline = top_margin + max_ascent

    output_dir = os.path.join(type_folder, font_name[:-4])
    os.makedirs(output_dir, exist_ok = True)

    for char in chars_to_extract:
        left, _, right, _ = font.getbbox(char)

        char_width = max(right - left, 1)
        img = Image.new("L", (char_width, target_image_height), color = 255)
        draw = ImageDraw.Draw(img)
        
        # rysujemy, używając scentrowanej linii bazowej
        draw.text(
            (-left, canvas_baseline), char, font = font, fill = 0
        )

        safe_char = char if char.isalnum() else f"ord{ord(char)}"
        img.save(os.path.join(output_dir, f"{safe_char}.png"))

class Font(Enum):
    ARIAL = "sans/arial"
    COMIC = "sans/comic"
    LFAX = "serif/lfax"
    TIMES = "serif/times"

def get_path_from_char(font: Font, char: str):
    safe_char = char if char.isalnum() else f"ord{ord(char)}"
    return f"data/fonts/{font.value}/{safe_char}.png"

if __name__ == "__main__":
    for type_folder in os.listdir("src"):
        type_path = os.path.join("src", type_folder)
        for font_name in os.listdir(type_path):
            if font_name.lower().endswith(('.ttf', '.otf')):
                print(f"Processing: {type_folder}/{font_name}")
                extract(type_folder, font_name)