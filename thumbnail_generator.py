import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import config

def draw_heavy_3d_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, center_x: int, y: int, fill_color: tuple, stroke_color: tuple = (10, 15, 25), stroke_width: int = 8):
    b = draw.textbbox((0, 0), text, font=font)
    tw = b[2] - b[0]
    tx = center_x - (tw // 2)

    shadow_offset = stroke_width + 4
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy <= stroke_width * stroke_width:
                draw.text((tx + dx + 3, y + dy + shadow_offset), text, fill=(0, 0, 0, 210), font=font)

    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy <= stroke_width * stroke_width:
                draw.text((tx + dx, y + dy), text, fill=stroke_color, font=font)

    draw.text((tx, y), text, fill=fill_color, font=font)

def generate_thumbnail(image_path: str, title_1: str, title_2: str, hook: str, output_path: str, ep_number: int = 1) -> str:
    base = Image.open(image_path).convert("RGBA")
    if base.size != (config.VIDEO_WIDTH, config.VIDEO_HEIGHT):
        base = base.resize((config.VIDEO_WIDTH, config.VIDEO_HEIGHT), Image.Resampling.LANCZOS)

    draw = ImageDraw.Draw(base)
    font_path = config.FONT_PATH if os.path.exists(config.FONT_PATH) else config.FALLBACK_FONT_PATH
    badge_font = ImageFont.truetype(font_path, 32)
    hook_font = ImageFont.truetype(font_path, 36)

    # 1. Episode Badge Pill with generous breathing room
    badge_text = f"• {config.CHANNEL_NAME} • FOLGE {ep_number:02d} •"
    bbox = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = bbox[2] - bbox[0]
    bh = bbox[3] - bbox[1]
    bx = config.SUBTITLE_CENTER_X - (bw // 2)
    by = 165

    draw.rounded_rectangle(
        [bx - 35, by - 12, bx + bw + 35, by + bh + 16],
        radius=20,
        fill=(255, 215, 0, 245),
        outline=(255, 255, 255, 230),
        width=2
    )
    draw.text((bx, by), badge_text, fill=(15, 20, 30), font=badge_font)

    # 2. Main High-Impact Titles (Lines 1 & 2)
    font_t1 = ImageFont.truetype(font_path, 80)
    draw_heavy_3d_text(draw, title_1.upper(), font_t1, config.SUBTITLE_CENTER_X, 260, (255, 255, 255), stroke_width=8)

    font_t2 = ImageFont.truetype(font_path, 80)
    draw_heavy_3d_text(draw, title_2.upper(), font_t2, config.SUBTITLE_CENTER_X, 370, (255, 215, 0), stroke_width=8)

    # 3. Hook Subtitle Pill
    if hook:
        h_box = draw.textbbox((0, 0), hook.upper(), font=hook_font)
        hw = h_box[2] - h_box[0]
        hh = h_box[3] - h_box[1]
        hx = config.SUBTITLE_CENTER_X - (hw // 2)
        hy = 490

        draw.rounded_rectangle(
            [hx - 32, hy - 12, hx + hw + 32, hy + hh + 16],
            radius=18,
            fill=(14, 18, 30, 230),
            outline=(255, 215, 0, 210),
            width=2
        )
        draw.text((hx, hy), hook.upper(), fill=(255, 255, 255), font=hook_font)

    base.convert("RGB").save(output_path, quality=95)
    print(f"[Thumbnail] Thumbnail erfolgreich generiert: {output_path}")
    return output_path
