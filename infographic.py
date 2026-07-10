"""
Генерирует горизонтальную диаграмму профиля сценариев.
Ведущие сценарии выделены золотым, остальные — приглушённым.
"""
import os
import urllib.request
from PIL import Image, ImageDraw, ImageFont

SIZE       = 1080
BG         = "#1C1320"
LEAD_COLOR = "#7B3B6E"
MUTED      = "#3D2B3A"
TEXT_MAIN  = "#F0EAF5"
TEXT_DIM   = "#907A8A"
ACCENT_LINE= "#7B3B6E"

SCENARIO_ORDER = ["V", "K", "HD", "N", "S"]
SCENARIO_LABELS = {
    "V":  "Выживатель",
    "K":  "Контролёр",
    "HD": "Хорошая\nдевочка",
    "N":  "Невидимка",
    "S":  "Спасатель",
}

FONT_URL_REGULAR = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Regular.ttf"
FONT_URL_BOLD    = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
FONT_PATH_REGULAR = "/tmp/Roboto-Regular.ttf"
FONT_PATH_BOLD    = "/tmp/Roboto-Bold.ttf"


def _download_fonts():
    if not os.path.exists(FONT_PATH_REGULAR):
        urllib.request.urlretrieve(FONT_URL_REGULAR, FONT_PATH_REGULAR)
    if not os.path.exists(FONT_PATH_BOLD):
        urllib.request.urlretrieve(FONT_URL_BOLD, FONT_PATH_BOLD)


def _font(size, bold=False):
    _download_fonts()
    path = FONT_PATH_BOLD if bold else FONT_PATH_REGULAR
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def generate_graph(percentages: dict, leaders: list, graph_file: str) -> str:
    img  = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)

    draw.rectangle([10, 10, SIZE-10, SIZE-10], outline=LEAD_COLOR, width=2)

    f_head  = _font(30, bold=True)
    f_sub   = _font(22)
    f_label = _font(26, bold=True)
    f_pct   = _font(30, bold=True)
    f_small = _font(20)

    draw.text((SIZE//2, 60),  "ВАШ ПРОФИЛЬ ЖИЗНЕННЫХ СЦЕНАРИЕВ",
              font=f_head, fill=TEXT_MAIN, anchor="mm")
    draw.text((SIZE//2, 100), "Чекап подсознания · Катарина Ковальская",
              font=f_sub,  fill=TEXT_DIM, anchor="mm")

    draw.line([(60, 130), (SIZE-60, 130)], fill=ACCENT_LINE, width=1)

    n        = len(SCENARIO_ORDER)
    area_top = 155
    area_bot = SIZE - 160
    slot_h   = (area_bot - area_top) // n
    bar_h    = int(slot_h * 0.55)
    bar_left = 260
    bar_max  = SIZE - bar_left - 80

    for i, key in enumerate(SCENARIO_ORDER):
        pct     = percentages.get(key, 0)
        is_lead = key in leaders
        color   = LEAD_COLOR if is_lead else MUTED
        fill_w  = max(int((pct / 100) * bar_max), 8)

        cy       = area_top + i * slot_h + slot_h // 2
        bar_top  = cy - bar_h // 2
        bar_bot  = cy + bar_h // 2

        draw.rounded_rectangle(
            [bar_left, bar_top, bar_left + bar_max, bar_bot],
            radius=10, fill="#2A1E28"
        )
        draw.rounded_rectangle(
            [bar_left, bar_top, bar_left + fill_w, bar_bot],
            radius=10, fill=color
        )

        label = SCENARIO_LABELS[key]
        label_color = TEXT_MAIN if is_lead else TEXT_DIM
        lines = label.split("\n")
        if len(lines) == 1:
            draw.text((bar_left - 14, cy), lines[0],
                      font=f_label, fill=label_color, anchor="rm")
        else:
            draw.text((bar_left - 14, cy - 14), lines[0],
                      font=_font(22, bold=True), fill=label_color, anchor="rm")
            draw.text((bar_left - 14, cy + 12), lines[1],
                      font=_font(22, bold=True), fill=label_color, anchor="rm")

        pct_x = bar_left + fill_w + 14
        draw.text((pct_x, cy), f"{pct}%",
                  font=f_pct, fill=TEXT_MAIN if is_lead else TEXT_DIM, anchor="lm")

        if is_lead:
            draw.text((bar_left - 50, cy), "★",
                      font=_font(28, bold=True), fill=LEAD_COLOR, anchor="mm")

    draw.line([(60, SIZE-140), (SIZE-60, SIZE-140)], fill=ACCENT_LINE, width=1)

    leader_names = " + ".join(
        SCENARIO_LABELS[k].replace("\n", " ") for k in leaders
    )
    result_type = "Один ведущий сценарий" if len(leaders) == 1 else "Два ведущих сценария"

    draw.text((SIZE//2, SIZE-110), f"Ведущий сценарий: {leader_names}",
              font=_font(24, bold=True), fill=LEAD_COLOR, anchor="mm")
    draw.text((SIZE//2, SIZE-78),  result_type,
              font=f_small, fill=TEXT_DIM, anchor="mm")
    draw.text((SIZE//2, SIZE-44),
              "Любой сценарий — это точка входа, а не приговор.",
              font=f_small, fill=TEXT_DIM, anchor="mm")

    os.makedirs("temp", exist_ok=True)
    path = f"temp/{graph_file}.png"
    img.save(path, "PNG")
    return path
