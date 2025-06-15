from data.fonts.extractor import get_path_from_char, Font
import os
import numpy as np
from PIL import Image

def generate_images_from_text_file(text_file_path: str, save_path: str, margin = 320):
    """
    Generuje obrazy z pojedynczego pliku tekstowego dla wszystkich czcionek.
    """
    rotation_angle = [8, 30, -8, -30]
    os.makedirs(save_path, exist_ok = True)

    if os.listdir(save_path): return

    try:
        with open(text_file_path, 'r', encoding='utf-8') as file:
            text = file.read().strip()

        for i, font in enumerate(Font):
            # prosty obraz
            straight_image = create_text_image(text, font, margin)
            
            # obrócony obraz
            rotated_image = create_rotated_text_image(straight_image, rotation_angle[i])
            
            # zapisz obrazy do plików
            straight_path = os.path.join(save_path, f"{os.path.splitext(os.path.basename(text_file_path))[0]}_{font.name}_straight.png")
            rotated_path = os.path.join(save_path, f"{os.path.splitext(os.path.basename(text_file_path))[0]}_{font.name}_rotated.png")
            straight_image.save(straight_path)
            rotated_image.save(rotated_path)

            # dodaj szum salt and pepper i zapisz z sufixem _noise
            add_salt_and_pepper_noise(straight_path, straight_path.replace('.png', '_noise.png'))
            add_salt_and_pepper_noise(rotated_path, rotated_path.replace('.png', '_noise.png'))
        
    except Exception as e:
        print(f"Error processing {text_file_path}: {e}")


def create_text_image(text: str, font: Font, margin: int):
    """Tworzy prosty obraz z tekstu z zadanym marginesem."""
    line_spacing = 10
    
    lines = text.split('\n')
    line_widths = []
    line_heights = []
    
    for line in lines:
        line_width = 0
        line_height = 0
        
        for char in line:
            if char == ' ':
                line_width += 20  # szerokość spacji
                continue
            
            try:
                path = get_path_from_char(font, char)
                if path and os.path.exists(path):
                    img = Image.open(path)
                    line_width += img.width
                    line_height = max(line_height, img.height)
            except:
                continue
        
        line_widths.append(line_width)
        line_heights.append(line_height)
    
    # wymiary tekstu
    text_width = max(line_widths) if line_widths else 0
    text_height = sum(line_heights) + (len(lines) - 1) * line_spacing
    
    # wymiary całego obrazu z tylko zadanym marginesem
    img_width = text_width + 2 * margin
    img_height = text_height + 2 * margin
    
    image = Image.new('RGB', (img_width, img_height), 'white')
    
    # wklejanie znaków (używając zadanego marginesu)
    y_offset = margin
    for line_idx, line in enumerate(lines):
        x_offset = margin
        
        for char in line:
            if char == ' ':
                x_offset += 20
                continue
            
            try:
                path = get_path_from_char(font, char)
                if path and os.path.exists(path):
                    char_img = Image.open(path).convert('RGB')
                    image.paste(char_img, (x_offset, y_offset))
                    x_offset += char_img.width
            except:
                continue
        
        if line_idx < len(line_heights):
            y_offset += line_heights[line_idx] + line_spacing
    
    return image

def create_rotated_text_image(straight_image: Image.Image, angle: float):
    """Tworzy obrócony obraz z już gotowego prostego obrazu."""
    rotated = straight_image.rotate(angle, expand = False, fillcolor = 'white', resample = Image.Resampling.BICUBIC)
    
    return rotated

def add_salt_and_pepper_noise(input_image_path: str, output_image_path: str, salt_prob: float = 0.01, pepper_prob: float = 0.01):
    """
    Dodaje szum typu sól i pieprz do obrazu.
    
    :param input_image_path: Ścieżka do wejściowego obrazu.
    :param output_image_path: Ścieżka do zapisu obrazu z szumem.
    :param salt_prob: Prawdopodobieństwo wystąpienia piksela soli.
    :param pepper_prob: Prawdopodobieństwo wystąpienia piksela pieprzu.
    """
    image = Image.open(input_image_path)
    image = image.convert('RGB')
    np_image = np.array(image)
    
    # Generujemy macierz losową dla całego obrazu
    random_matrix = np.random.random(np_image.shape[:2])  # Tylko wysokość i szerokość
    
    # Dodawanie szumu sól (białe piksele)
    if salt_prob > 0:
        salt_mask = random_matrix < salt_prob
        np_image[salt_mask] = 255

    # Dodawanie szumu pieprz (czarne piksele)
    if pepper_prob > 0:
        pepper_mask = random_matrix < (salt_prob + pepper_prob)
        pepper_mask = pepper_mask & ~salt_mask  # Wykluczamy piksele już oznaczone jako sól
        np_image[pepper_mask] = 0

    # Konwertujemy z powrotem do obrazu PIL i zapisujemy
    result_image = Image.fromarray(np_image.astype(np.uint8))
    result_image.save(output_image_path)