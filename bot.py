import asyncio
import datetime
import html
import logging
import os
import re
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ContextTypes

from data import (
    BUS_SCHEDULE,
    CLASS_SCHEDULE,
    DAYS,
    DAY_LABELS,
    SUBJECTS,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATERIALS_DIR = os.path.join(BASE_DIR, "materials")
ENV_FILE = os.path.join(BASE_DIR, ".env")
MALAYSIA_TZ = datetime.timezone(datetime.timedelta(hours=8))
STUDY_REMINDER_INTERVAL = 1
study_tasks: dict[tuple[int, int], asyncio.Task] = {}


def read_env_value(name: str) -> str | None:
    """Read one value from the local .env file."""
    if not os.path.isfile(ENV_FILE):
        return None
    with open(ENV_FILE, encoding="utf-8") as env_file:
        for raw_line in env_file:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == name:
                return value.strip().strip("\"'") or None
    return None


BOT_TOKEN = os.getenv("BOT_TOKEN") or read_env_value("BOT_TOKEN")


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"Telegram bot is running")
    
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

    def log_message(self, format, *args):
        return


def start_health_server():
    """Bind to Render's web-service port without blocking the Telegram bot."""
    port = os.getenv("PORT")
    if not port:
        return

    server = ThreadingHTTPServer(("0.0.0.0", int(port)), HealthCheckHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logger.info("Health server listening on port %s", port)


def malaysia_now() -> datetime.datetime:
    return datetime.datetime.now(MALAYSIA_TZ)


def today_key() -> str:
    """Return mon..fri, falling back to Monday on weekends."""
    weekday = malaysia_now().weekday()
    return DAYS[weekday] if weekday <= 4 else "mon"


def parse_study_time(value: str) -> datetime.time | None:
    """Accept times such as 21:30, 9:30pm, or 9pm."""
    normalized = value.strip().replace(" ", "").upper()
    for time_format in ("%H:%M", "%I:%M%p", "%I%p"):
        try:
            return datetime.datetime.strptime(normalized, time_format).time()
        except ValueError:
            continue
    return None


def next_study_datetime(
    requested_time: datetime.time,
    now: datetime.datetime | None = None,
) -> datetime.datetime:
    """Return the next occurrence of a Malaysia-time clock time."""
    now = now or malaysia_now()
    target = datetime.datetime.combine(now.date(), requested_time, MALAYSIA_TZ)
    current_minute = now.replace(second=0, microsecond=0)
    if target < current_minute:
        target += datetime.timedelta(days=1)
    return target


def format_class_schedule(
    day: str,
    now: datetime.datetime | None = None,
) -> str:
    """Escape schedule text and highlight the class happening now."""
    now = now or malaysia_now()
    current_day = DAYS[now.weekday()] if now.weekday() <= 4 else None
    current_minutes = now.hour * 60 + now.minute
    formatted_lines = []

    for line in CLASS_SCHEDULE[day]:
        safe_line = html.escape(line)
        match = re.match(
            r"(?i)\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?\s*-\s*"
            r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?",
            line,
        )
        is_current = False
        if day == current_day and match and not any(
            word in line.lower() for word in ("lunch", "break")
        ):
            start_hour, start_minute, start_period, end_hour, end_minute, end_period = match.groups()

            def to_minutes(hour: str, minute: str | None, period: str | None) -> int:
                hour_number = int(hour)
                if period:
                    hour_number %= 12
                    if period.lower() == "pm":
                        hour_number += 12
                return hour_number * 60 + int(minute or 0)

            start = to_minutes(start_hour, start_minute, start_period)
            end = to_minutes(end_hour, end_minute, end_period)
            is_current = start <= current_minutes < end

        if is_current:
            safe_line = f"👉 <b>{safe_line}</b>"
        formatted_lines.append(safe_line)

    return "\n".join(formatted_lines)


def all_subjects() -> dict:
    """Return configured subjects that have a folder under materials/."""
    subject_bank = SUBJECTS
    material_subjects = {
        entry.name for entry in os.scandir(MATERIALS_DIR) if entry.is_dir()
    }
    return {
        key: info
        for key, info in subject_bank.items()
        if key in material_subjects
    }


def main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(info["label"], callback_data=f"subject:{key}")]
        for key, info in all_subjects().items()
    ]
    buttons.extend(
        [
            [InlineKeyboardButton("Bus Schedule", callback_data="bus:menu")],
            [InlineKeyboardButton("Class Schedule", callback_data="class:menu")],
        ]
    )
    return InlineKeyboardMarkup(buttons)


def subject_menu_keyboard(bank: dict, subject_key: str) -> InlineKeyboardMarkup:
    subject = bank[subject_key]
    buttons = [
        [InlineKeyboardButton(chapter["label"], callback_data=f"chapter:{subject_key}:{i}")]
        for i, chapter in enumerate(subject["chapters"])
    ]
    buttons.append(
        [InlineKeyboardButton("Assignments", callback_data=f"assign:{subject_key}")]
    )
    buttons.append([InlineKeyboardButton("Back", callback_data="menu:main")])
    return InlineKeyboardMarkup(buttons)



def assignments_menu_keyboard(subject_key: str) -> InlineKeyboardMarkup:
    assignments = SUBJECTS[subject_key]["assignments"]
    buttons = [
        [InlineKeyboardButton(item["label"], callback_data=f"assignment:{subject_key}:{i}")]
        for i, item in enumerate(assignments)
    ]
    buttons.append([InlineKeyboardButton("Back", callback_data=f"subject:{subject_key}")])
    return InlineKeyboardMarkup(buttons)


def day_buttons_keyboard(prefix: str) -> InlineKeyboardMarkup:
    row = [
        InlineKeyboardButton(DAY_LABELS[day][:3], callback_data=f"{prefix}:day:{day}")
        for day in DAYS
    ]
    return InlineKeyboardMarkup(
        [row, [InlineKeyboardButton("Back", callback_data="menu:main")]]
    )


def find_subject(subject_key: str) -> dict:
    return SUBJECTS[subject_key]


async def send_material(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    item: dict,
    keyboard=None,
):
    query = update.callback_query
    chat_id = query.message.chat_id

    if item["type"] == "file":
        path = item["path"]
        absolute_path = path if os.path.isabs(path) else os.path.join(BASE_DIR, path)
        if os.path.exists(absolute_path):
            with open(absolute_path, "rb") as material_file:
                await context.bot.send_document(chat_id=chat_id, document=material_file)
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"File not found yet: {path}",
                reply_markup=keyboard,
            )
    elif item["type"] == "link":
        await context.bot.send_message(
            chat_id=chat_id,
            text=item["url"],
            reply_markup=keyboard,
        )
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text=item["content"],
            reply_markup=keyboard,
        )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Welcome! What do you need?",
        reply_markup=main_menu_keyboard(),
    )


async def run_study_reminder(
    context: ContextTypes.DEFAULT_TYPE,
    key: tuple[int, int],
    target: datetime.datetime,
):
    """Wait until the requested time, then remind once per second."""
    chat_id, _ = key
    try:
        delay = max(0, (target - malaysia_now()).total_seconds())
        await asyncio.sleep(delay)
        while True:
            await context.bot.send_message(
                chat_id=chat_id,
                text="go study!!! (/stop to stop)",
            )
            await asyncio.sleep(STUDY_REMINDER_INTERVAL)
    except asyncio.CancelledError:
        raise
    except Exception:
        logger.exception("Study reminder failed for chat %s", chat_id)
    finally:
        if study_tasks.get(key) is asyncio.current_task():
            study_tasks.pop(key, None)


async def study_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Schedule repeated study reminders with /study <time>."""
    if not context.args:
        await update.effective_message.reply_text(
            "Usage: /study <time>\nExamples: /study 21:30 or /study 9:30pm"
        )
        return

    requested_time = parse_study_time("".join(context.args))
    if requested_time is None:
        await update.effective_message.reply_text(
            "I couldn't read that time. Try /study 21:30 or /study 9:30pm."
        )
        return

    key = (update.effective_chat.id, update.effective_user.id)
    previous_task = study_tasks.pop(key, None)
    if previous_task:
        previous_task.cancel()

    target = next_study_datetime(requested_time)
    task = asyncio.create_task(run_study_reminder(context, key, target))
    study_tasks[key] = task
    await update.effective_message.reply_text(
        "Study reminder set for "
        f"{target.strftime('%A %I:%M %p')}.\n"
    )


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stop this user's pending or active study reminder."""
    key = (update.effective_chat.id, update.effective_user.id)
    task = study_tasks.pop(key, None)
    if task:
        task.cancel()
        await update.effective_message.reply_text("Study reminders stopped.")
    else:
        await update.effective_message.reply_text("You have no active study reminder.")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split(":")
    action = parts[0]

    if data == "menu:main":
        await query.edit_message_text(
            "What do you need?",
            reply_markup=main_menu_keyboard(),
        )
        return

    if action == "subject":
        subject_key = parts[1]
        bank = SUBJECTS
        await query.edit_message_text(
            f"{bank[subject_key]['label']} - choose a chapter:",
            reply_markup=subject_menu_keyboard(bank, subject_key),
        )
        return

    if action == "chapter":
        subject_key, index = parts[1], int(parts[2])
        subject = find_subject(subject_key)
        bank = SUBJECTS
        await send_material(
            update,
            context,
            subject["chapters"][index],
            keyboard=subject_menu_keyboard(bank, subject_key),
        )
        return

    if action == "assign":
        subject_key = parts[1]
        assignments = find_subject(subject_key)["assignments"]
        if isinstance(assignments, list):
            await query.edit_message_text(
                "Choose an assignment:",
                reply_markup=assignments_menu_keyboard(subject_key),
            )
        else:
            await send_material(
                update,
                context,
                assignments,
                keyboard=subject_menu_keyboard(SUBJECTS, subject_key),
            )
        return

    if action == "assignment":
        subject_key, index = parts[1], int(parts[2])
        assignments = find_subject(subject_key)["assignments"]
        await send_material(
            update,
            context,
            assignments[index],
            keyboard=assignments_menu_keyboard(subject_key),
        )
        return
    if data == "bus:menu":
        day = today_key()
        text = f"Today ({DAY_LABELS[day]}):\n\n{BUS_SCHEDULE[day]}\n\nOr pick a day:"
        await query.edit_message_text(text, reply_markup=day_buttons_keyboard("bus"))
        return

    if action == "bus" and parts[1] == "day":
        day = parts[2]
        await query.edit_message_text(
            BUS_SCHEDULE[day],
            reply_markup=day_buttons_keyboard("bus"),
        )
        return

    if data == "class:menu":
        day = today_key()
        lines = format_class_schedule(day)
        text = f"Today ({DAY_LABELS[day]}):\n\n{lines}\n\nOr pick a day:"
        await query.edit_message_text(
            text,
            reply_markup=day_buttons_keyboard("class"),
            parse_mode="HTML",
        )
        return

    if action == "class" and parts[1] == "day":
        day = parts[2]
        lines = format_class_schedule(day)
        await query.edit_message_text(
            f"{DAY_LABELS[day]}:\n\n{lines}",
            reply_markup=day_buttons_keyboard("class"),
            parse_mode="HTML",
        )


def main():
    if not BOT_TOKEN:
        raise SystemExit(
            "No BOT_TOKEN found. Set it as an environment variable or add it to .env."
        )

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("study", study_command))
    app.add_handler(CommandHandler("stop", stop_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    start_health_server()
    logger.info("Bot starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
