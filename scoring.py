SCENARIO_KEYS = ["V", "K", "HD", "N", "S"]

SCENARIO_NAMES = {
    "V":  "Выживатель",
    "K":  "Контролёр",
    "HD": "Хорошая девочка",
    "N":  "Невидимка",
    "S":  "Спасатель",
}

GRAPH_FILES = {
    ("V",):        "grafik_V",
    ("K",):        "grafik_K",
    ("HD",):       "grafik_HD",
    ("N",):        "grafik_N",
    ("S",):        "grafik_S",
    ("V",  "K"):   "grafik_VK",
    ("V",  "HD"):  "grafik_VHD",
    ("V",  "N"):   "grafik_VN",
    ("V",  "S"):   "grafik_VS",
    ("K",  "HD"):  "grafik_KHD",
    ("K",  "N"):   "grafik_KN",
    ("K",  "S"):   "grafik_KS",
    ("HD", "N"):   "grafik_HDN",
    ("HD", "S"):   "grafik_HDS",
    ("N",  "S"):   "grafik_NS",
}

AUDIO_FILES = {
    "V":  "audio_V.ogg",
    "K":  "audio_K.ogg",
    "HD": "audio_HD.ogg",
    "N":  "audio_N.ogg",
    "S":  "audio_S.ogg",
}


def calculate_result(raw_scores: dict) -> dict:
    sorted_scores = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    top1_key, top1_val = sorted_scores[0]
    top2_key, top2_val = sorted_scores[1]

    diff = top1_val - top2_val
    if diff >= 2:
        result_type = "A"
        leaders = [top1_key]
    else:
        result_type = "B"
        pair = sorted([top1_key, top2_key], key=lambda x: SCENARIO_KEYS.index(x))
        leaders = pair

    FLOOR_0 = 5
    FLOOR_1 = 11

    floor_sum = 0
    floor_map = {}
    strong_keys = []

    for key, val in raw_scores.items():
        if val == 0:
            floor_map[key] = FLOOR_0
            floor_sum += FLOOR_0
        elif val == 1:
            floor_map[key] = FLOOR_1
            floor_sum += FLOOR_1
        else:
            floor_map[key] = None
            strong_keys.append((key, val))

    remainder = 100 - floor_sum
    total_strong = sum(v for _, v in strong_keys)

    percentages = {}
    for key in SCENARIO_KEYS:
        if floor_map[key] is not None:
            percentages[key] = floor_map[key]
        else:
            val = raw_scores[key]
            percentages[key] = round((val / total_strong) * remainder)

    delta = 100 - sum(percentages.values())
    if delta != 0 and strong_keys:
        top_strong = strong_keys[0][0]
        percentages[top_strong] += delta

    graph_key = tuple(leaders)
    graph_file = GRAPH_FILES.get(graph_key, "grafik_V")
    audio_key = leaders[0]

    return {
        "scores": raw_scores,
        "percentages": percentages,
        "result_type": result_type,
        "leaders": leaders,
        "graph_key": graph_key,
        "graph_file": graph_file,
        "audio_key": audio_key,
    }
