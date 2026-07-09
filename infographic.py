"""
Генерирует горизонтальную диаграмму профиля сценариев.
Ведущие сценарии выделены золотым, остальные — приглушённым.
"""
import os
from PIL import Image, ImageDraw, ImageFont

SIZE       = 1080
BG         = "#1C1320"   # тёмно-сливовый, глубокий и дорогой
LEAD_COLOR = "#7B3B6E"   # насыщенный фиолетово-бордо (ведущие)
MUTED      = "#3D2B3A"   # приглушённый тёмно-лавандовый (остальные)
TEXT_MAIN  = "#F0EAF5"   # мягкий кремово-лиловый
TEXT_DIM   = "#907A8A"   # приглушённый розово-серый
ACCENT_LINE= "#7B3B6E"   # линии в цвет бренда

SCENARIO_ORDER = ["V", "K", "HD", "N", "S"]
SCENARIO_LABELS = {
    "V":  "Выживатель",
    "K":  "Контролёр",
    "HD": "Хорошая\nдевочка",
    "N":  "Невидимка",
    "S":  "Спасатель",
}


def _font(size, bold=False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold
        else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for p in candidates:
        if os.path.exists(p):
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                pass
    return ImageFont.load_default()


def generate_graph(percentages: dict, leaders: list, graph_file: str) -> str:
    """
    percentages: {"В": 49, "К": 24, "ХД": 11, "Н": 11, "С": 5}
    leaders:     ["К"] или ["В", "К"]
    graph_file:  "grafik_K" (без расширения)
    Возвращает путь к PNG.
    """
    img  = Image.new("RGB", (SIZE, SIZE), BG)
    draw = ImageDraw.Draw(img)

    # ── Рамка ────────────────────────────────────────────────────────────────
    draw.rectangle([10, 10, SIZE-10, SIZE-10], outline=LEAD_COLOR, width=2)

    # ── Заголовок ────────────────────────────────────────────────────────────
    f_head  = _font(30, bold=True)
    f_sub   = _font(22)
    f_label = _font(26, bold=True)
    f_pct   = _font(30, bold=True)
    f_small = _font(20)

    draw.text((SIZE//2, 60),  "ВАШ ПРОФИЛЬ ЖИЗНЕННЫХ СЦЕНАРИЕВ",
              font=f_head, fill=TEXT_MAIN, anchor="mm")
    draw.text((SIZE//2, 100), "Чекап подсознания · Катарина Ковальская",
              font=f_sub,  fill=TEXT_DIM, anchor="mm")

    # Разделитель
    draw.line([(60, 130), (SIZE-60, 130)], fill=ACCENT_LINE, width=1)

    # ── Бары ─────────────────────────────────────────────────────────────────
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

        # Фон бара
        draw.rounded_rectangle(
            [bar_left, bar_top, bar_left + bar_max, bar_bot],
            radius=10, fill="#2A1E28"
        )
        # Заполненный бар
        draw.rounded_rectangle(
            [bar_left, bar_top, bar_left + fill_w, bar_bot],
            radius=10, fill=color
        )

        # Метка сценария (слева)
        label = SCENARIO_LABELS[key]
        label_color = TEXT_MAIN if is_lead else TEXT_DIM
        # Двустрочные подписи
        lines = label.split("\n")
        if len(lines) == 1:
            draw.text((bar_left - 14, cy), lines[0],
                      font=f_label, fill=label_color, anchor="rm")
        else:
            draw.text((bar_left - 14, cy - 14), lines[0],
                      font=_font(22, bold=True), fill=label_color, anchor="rm")
            draw.text((bar_left - 14, cy + 12), lines[1],
                      font=_font(22, bold=True), fill=label_color, anchor="rm")

        # Процент (справа от бара)
        pct_x = bar_left + fill_w + 14
        draw.text((pct_x, cy), f"{pct}%",
                  font=f_pct, fill=TEXT_MAIN if is_lead else TEXT_DIM, anchor="lm")

        # Звёздочка у ведущего
        if is_lead:
            draw.text((bar_left - 50, cy), "★",
                      font=_font(28, bold=True), fill=LEAD_COLOR, anchor="mm")

    # ── Подпись снизу ────────────────────────────────────────────────────────
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

    # ── Сохраняем ────────────────────────────────────────────────────────────
    os.makedirs("temp", exist_ok=True)
    path = f"temp/{graph_file}.png"
    img.save(path, "PNG")
    return path
