"""
Дожимная цепочка — 3 касания + закрытие.

Отправляется через планировщик (apscheduler) или вручную через команды.
Для Railway: добавить APScheduler в requirements и запускать в фоне.

Временны́е метки от момента прохождения квиза:
  - +12 часов → касание 1
  - +24 часа  → касание 2
  - +48 часов → касание 3
  - после 48ч → закрытие записи
"""
from scenarios import FOLLOWUP_12H, FOLLOWUP_24H, FOLLOWUP_48H, FOLLOWUP_CLOSED

FOLLOWUP_SCHEDULE = [
    {"hours": 12, "text": FOLLOWUP_12H,    "btn": "▶ Записаться на Сканирование"},
    {"hours": 24, "text": FOLLOWUP_24H,    "btn": "▶ Записаться на Сканирование"},
    {"hours": 48, "text": FOLLOWUP_48H,    "btn": "▶ Записаться на Сканирование"},
    {"hours": 72, "text": FOLLOWUP_CLOSED, "btn": "▶ Оставить заявку"},
]
