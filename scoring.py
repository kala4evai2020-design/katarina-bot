SCENARIO_KEYS = ["V", "K", "HD", "N", "S", "Z"]

SCENARIO_NAMES = {
    "V":  "Выживатель",
    "K":  "Контролёр",
    "HD": "Хорошая девочка",
    "N":  "Невидимка",
    "S":  "Спасатель",
    "Z":  "Свободный",
}

AUDIO_FILES = {
    "V":  "audio_V.ogg",
    "K":  "audio_K.ogg",
    "HD": "audio_HD.ogg",
    "N":  "audio_N.ogg",
    "S":  "audio_S.ogg",
    "Z":  "audio_6.ogg",
}

def calculate_result(raw_scores: dict) -> dict:
    total = sum(raw_scores.values()) or 1
    pct = {k: round(raw_scores.get(k, 0) / total * 100) for k in SCENARIO_KEYS}

    sorted_keys = sorted(pct, key=lambda k: pct[k], reverse=True)
    top1, top2 = sorted_keys[0], sorted_keys[1]

    if pct[top1] - pct[top2] >= 2:
        leaders = [top1]
        result_type = "A"
    else:
        leaders = [top1, top2]
        result_type = "B"

    graph_file = "grafik_" + "_".join(leaders)

    return {
        "percentages": pct,
        "leaders": leaders,
        "result_type": result_type,
        "graph_file": graph_file,
    }
