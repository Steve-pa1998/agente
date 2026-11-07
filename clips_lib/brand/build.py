from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

BRAND = Path(__file__).parent

NAVY = (10, 22, 40)
STEEL = (30, 58, 95)
CIAN = (79, 195, 247)
BLANCO = (232, 244, 253)
ELECTRICO = (0, 229, 255)


def draw_waves(draw, width, height, y_start, color, opacity=100):
    """Dibuja una onda simple."""
    points = []
    for x in range(0, width, 4):
        y = y_start + (30 * ((x * 7) % 100) / 100)
        points.append((x, y))
    points.append((width, height))
    points.append((0, height))
    overlay = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.polygon(points, fill=color + (opacity,))
    return overlay


def build_logo():
    img = Image.new("RGBA", (800, 800), NAVY + (255,))
    d = ImageDraw.Draw(img)
    # Forma orgánica (elipse con recorte)
    d.ellipse([200, 120, 600, 560], fill=CIAN + (255,))
    d.ellipse([280, 220, 520, 480], fill=NAVY + (255,))
    # Punto central
    d.ellipse([355, 335, 445, 425], fill=NAVY + (255,))
    # Cola inferior
    d.polygon([(340, 500), (460, 500), (420, 700), (380, 700)], fill=CIAN + (255,))
    img.save(BRAND / "logo_800.png")
    print(f"[OK] logo_800.png (800x800)")


def build_overlay():
    img = Image.new("RGBA", (1920, 1080), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    # Bordes
    d.rectangle([0, 0, 1919, 7], fill=CIAN + (150,))
    d.rectangle([0, 1073, 1919, 1079], fill=CIAN + (150,))
    d.rectangle([0, 0, 7, 1079], fill=CIAN + (80,))
    d.rectangle([1913, 0, 1919, 1079], fill=CIAN + (80,))
    # Logo esquina sup-izq
    d.ellipse([45, 45, 115, 115], fill=CIAN + (130,))
    # Marco webcam inf-derecha
    d.rounded_rectangle([1520, 820, 1880, 1040], radius=16, outline=CIAN + (200,), width=4)
    # Espacio alertas sup-derecha
    d.rounded_rectangle([1400, 40, 1880, 100], radius=8, fill=STEEL + (150,))
    img.save(BRAND / "overlay_1920.png")
    print(f"[OK] overlay_1920.png (1920x1080)")


def build_template_clips():
    img = Image.new("RGBA", (1080, 1920), NAVY + (255,))
    d = ImageDraw.Draw(img)
    # Ondas inferiores
    wave1 = draw_waves(d, 1080, 1920, 1600, STEEL, 80)
    img.paste(wave1, (0, 0), wave1)
    wave2 = draw_waves(d, 1080, 1920, 1700, STEEL, 50)
    img.paste(wave2, (0, 0), wave2)
    # Logo esquina inf-izq
    d = ImageDraw.Draw(img)
    d.ellipse([50, 1810, 110, 1870], fill=CIAN + (150,))
    img.save(BRAND / "template_clips_1080.png")
    print(f"[OK] template_clips_1080.png (1080x1920)")


def build_banner():
    img = Image.new("RGBA", (1280, 480), NAVY + (255,))
    d = ImageDraw.Draw(img)
    # Onda inferior
    wave = draw_waves(d, 1280, 480, 350, STEEL, 100)
    img.paste(wave, (0, 0), wave)
    d = ImageDraw.Draw(img)
    # Logo
    d.ellipse([140, 180, 260, 300], fill=CIAN + (200,))
    # Texto
    try:
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        font = ImageFont.load_default()
    d.text((320, 220), "elbusk_pa_chin", fill=BLANCO + (255,), font=font)
    img.save(BRAND / "banner_1280.png")
    print(f"[OK] banner_1280.png (1280x480)")


def build_offline():
    img = Image.new("RGBA", (1920, 1080), NAVY + (255,))
    d = ImageDraw.Draw(img)
    # Onda
    wave = draw_waves(d, 1920, 1080, 800, STEEL, 80)
    img.paste(wave, (0, 0), wave)
    d = ImageDraw.Draw(img)
    # Logo central
    d.ellipse([880, 320, 1040, 480], fill=CIAN + (180,))
    # Texto
    try:
        font_big = ImageFont.truetype("arial.ttf", 64)
        font_small = ImageFont.truetype("arial.ttf", 32)
    except:
        font_big = ImageFont.load_default()
        font_small = font_big
    d.text((960, 580), "Vuelvo pronto", fill=BLANCO + (255,), font=font_big, anchor="mt")
    d.text((960, 680), "@elbusk_pa_chin", fill=CIAN + (255,), font=font_small, anchor="mt")
    img.save(BRAND / "offline_1920.png")
    print(f"[OK] offline_1920.png (1920x1080)")


def build():
    print("[BRAND] Generando assets...\n")
    build_logo()
    build_overlay()
    build_template_clips()
    build_banner()
    build_offline()
    print(f"\n[BRAND] 5 assets generados en {BRAND}")


if __name__ == "__main__":
    build()   
