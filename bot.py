import asyncio
import os
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder

from config import BOT_TOKEN, CTA_URL, ADMIN_ID
from questions import QUESTIONS
from scenarios import SCENARIOS, SCENARIO_NAMES
from scoring import SCENARIO_KEYS, AUDIO_FILES, calculate_result
from infographic import generate_graph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp  = Dispatcher(storage=MemoryStorage())

TOTAL_Q = len(QUESTIONS)

def get_video_file_id():
    return os.environ.get("VIDEO_FILE_ID") or None

def save_video_file_id(file_id: str):
    logger.info(f"New video file_id: {file_id}")

@dp.message(Command("setvideo"))
async def cmd_setvideo(message: Message):
    if str(message.from_user.id) != str(ADMIN_ID):
        return
    if message.video:
        file_id = message.video.file_id
        save_video_file_id(file_id)
        await message.answer(
            f"✅ Видео получено!\n\nfile_id:\n{file_id}\n\n"
            f"Добавь его в Railway → Variables → VIDEO_FILE_ID"
        )
    else:
        await message.answer("Send video with /setvideo caption")

class QuizState(StatesGroup):
    answering = State()

@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    kb = InlineKeyboardBuilder()
    kb.button(text="▶ Пройти Чекап", callback_data="start_quiz")

    photo_path = None
    for name in ["welcome.jpg", "welcome.jpeg", "welcome.png"]:
        if os.path.exists(name):
            photo_path = name
            break

    logger.info(f"Files in current dir: {os.listdir('.')}")
    logger.info(f"Photo path found: {photo_path}")

    welcome_text = (
        "Привет. Я Катарина Ковальская — эксперт по программированию подсознания.\n\n"
        "Вижу то, чего не видят психологи: глубинные программы, которые управляют "
        "твоей жизнью «за кадром» и не дают развиваться и двигаться дальше.\n\n"
        "Подсознательные сценарии — это программы, которые были «записаны» давно "
        "и с тех пор тихо управляют твоими решениями, реакциями и тем, что ты "
        "притягиваешь в свою жизнь.\n\n"
        "Пока ты их не видишь — они спокойно работают и разрушают жизнь. "
        "Поэтому их стоит подсвечивать, выявлять и перепрограммировать!\n\n"
        "За 5 минут Чекап подсознания покажет:\n"
        "● какой сценарий сейчас доминирует и управляет твоей жизнью\n"
        "● что именно он блокирует — деньги, отношения или энергию\n"
        "● и с чего начать, чтобы выйти из этого замкнутого круга"
    )

    if photo_path:
        await message.answer_photo(
            photo=FSInputFile(photo_path),
            caption=welcome_text,
            reply_markup=kb.as_markup()
        )
    else:
        await message.answer(
            welcome_text,
            reply_markup=kb.as_markup()
        )

@dp.callback_query(F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext):
    scores = {k: 0 for k in SCENARIO_KEYS}
    await state.set_state(QuizState.answering)
    await state.update_data(q_idx=0, scores=scores)
    await callback.answer()
    await send_question(callback.message, 0)

async def send_question(message: Message, idx: int):
    q = QUESTIONS[idx]
    kb = InlineKeyboardBuilder()
    for opt in q["options"]:
        kb.button(text=opt["text"], callback_data=f"ans_{opt['scenario']}")
    kb.adjust(1)
    await message.answer(
        f"_{idx + 1} из {TOTAL_Q}_\n\n*{q['text']}*",
        parse_mode="Markdown",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(QuizState.answering, F.data.startswith("ans_"))
async def process_answer(callback: CallbackQuery, state: FSMContext):
    scenario = callback.data.replace("ans_", "")
    data = await state.get_data()
    scores = data["scores"]
    scores[scenario] = scores.get(scenario, 0) + 1
    idx = data["q_idx"] + 1
    await state.update_data(scores=scores, q_idx=idx)
    await callback.answer()
    if idx < TOTAL_Q:
        await send_question(callback.message, idx)
    else:
        await show_result(callback.message, scores, state)

async def show_result(message: Message, raw_scores: dict, state: FSMContext):
    await message.answer(
        "⏳ *Твоё сканирование завершено.*\n\nСейчас обрабатываю ответы...",
        parse_mode="Markdown"
    )
    await asyncio.sleep(2)
    result  = calculate_result(raw_scores)
    pct     = result["percentages"]
    leaders = result["leaders"]
    lines = []
    for key in ["V", "K", "HD", "N", "S"]:
        marker = "⭐" if key in leaders else "·"
        lines.append(f"{marker} *{SCENARIO_NAMES[key]}* — {pct[key]}%")
    await message.answer(
        "📊 *Профиль жизненных сценариев:*\n\n" + "\n".join(lines),
        parse_mode="Markdown"
    )
    await asyncio.sleep(1)
    img_path = generate_graph(pct, leaders, result["graph_file"])
    photo    = FSInputFile(img_path)
    leader_names = " + ".join(SCENARIO_NAMES[k] for k in leaders)
    type_label   = "один ведущий сценарий" if result["result_type"] == "A" else "два ведущих сценария"
    await message.answer_photo(
        photo=photo,
        caption=f"*Твой результат: {leader_names}*\n_{type_label}_",
        parse_mode="Markdown"
    )
    await asyncio.sleep(1)
    primary = leaders[0]
    sc = SCENARIOS[primary]
    await message.answer(
        f"*Твой ведущий сценарий — {sc['name'].upper()}*\n\n{sc['description']}",
        parse_mode="Markdown"
    )
    await asyncio.sleep(1)
    await state.update_data(leader=primary, quiz_done_at=datetime.now().isoformat())
    await send_podcast(message, primary, sc)

async def send_podcast(message: Message, key: str, sc: dict):
    await message.answer(
        "🎙 *Записала тебе личное аудио послание — прослушай его, это важно.*",
        parse_mode="Markdown"
    )
    audio_file = AUDIO_FILES[key]
    audio_path = None
    for folder in ["media/{audio,video}", "media", "media/audio", "."]:
        candidate = os.path.join(folder, audio_file)
        if os.path.exists(candidate):
            audio_path = candidate
            break

    if audio_path:
        await message.answer_voice(voice=FSInputFile(audio_path))
    else:
        logger.warning(f"Audio not found: {audio_file}")
        await message.answer(
            "_(Аудио временно недоступно)_",
            parse_mode="Markdown"
        )
    await asyncio.sleep(1)
    await send_podcast_bridge(message)

async def send_podcast_bridge(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="▶ Смотреть видео", callback_data="watch_video")
    await message.answer(
        "Поздравляю — первый шаг сделан! И теперь мы нащупали твою доминантную ведущую программу.\n\n"
        "Ты думаешь: «Окей, теперь я понимаю, в чём причина. Буду работать над собой».\n\n"
        "Я угадала?\n\n"
        "Это естественная реакция. Но вот что важно знать:\n\n"
        "Выявление программы не ведёт к улучшениям. Разрушающие программы умеют хитро "
        "адаптироваться — они надевают другие маски, часто этот сценарий появляется в "
        "новых ситуациях, с новыми людьми. И жизнь снова и снова возвращает тебя в одни и те же сценарии.\n\n"
        "Чтобы это остановить — нужно найти корень. Не симптом, а первопричину.\n\n"
        "В следующем видео я расскажу, как именно это работает — и что нужно сделать, "
        "чтобы сценарий перестал повторяться.",
        reply_markup=kb.as_markup()
    )

@dp.callback_query(F.data == "watch_video")
async def send_video(callback: CallbackQuery):
    await callback.answer()
    file_id = get_video_file_id()
    if file_id:
        await callback.message.answer_video(video=file_id)
    else:
        await callback.message.answer(
            "🎬 _(Видео скоро появится здесь)_",
            parse_mode="Markdown"
        )
    await asyncio.sleep(1)
    await send_cta(callback.message)

async def send_cta(message: Message):
    kb = InlineKeyboardBuilder()
    kb.button(text="▶ Записаться на Сканирование жизни", url=CTA_URL)
    await message.answer(
        "Теперь ты знаешь свой доминирующий сценарий.\n\n"
        "А давай пойдём глубже — но уже вместе?\n\n"
        "Я приглашаю тебя на личное Сканирование.\n\n"
        "Это 30 минут работы со мной, один на один, где я покажу тебе, "
        "что именно стоит за твоей программой, откуда она появилась — "
        "и с чего начать, чтобы она перестала управлять твоей жизнью.\n\n"
        "Я знаю пошаговый план для каждого сценария. "
        "И уже на этой встрече ты на себе ощутишь, как работает мой метод.\n\n"
        "Сразу скажу, что возможность записаться на сканирование бесплатно "
        "открыта только один раз, в течении 48 часов после чекапа.",
        reply_markup=kb.as_markup()
    )

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
