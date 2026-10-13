import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
import subprocess
import os
import time
import requests
import re
import json
import threading
import queue
import shutil
import urllib3
import random
from urllib.parse import urlparse, unquote, quote
from requests_toolbelt import MultipartEncoder, MultipartEncoderMonitor
import boto3
from botocore.config import Config

try:
    import psutil
    HAS_PSUTIL = True
except ImportError: 
    HAS_PSUTIL = False

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError: 
    HAS_PLAYWRIGHT = False

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

VERSION = "18.7.0 (Smart Delogo & Placement)"
TOKEN = "8888154300:AAG2Bpw_dRza9a1mhFzvi182pP0ULo3IFwA"
ADMIN_CHAT_ID = 1013251619
CONFIG_FILE = "api_keys_config.json"

DEFAULT_KEYS = {
    "LARHU_API_KEY": "863rrqmdzm6sb4k4xwv",
    "ABSTREAM_API_KEY": "1855r1beof65n58tyjyd",
    "UQLOAD_API_KEY": "157590rbrqefwnpfz7n9qw",
    "VIDMOLY_API_KEY": "613979bpr8w0ktgk2qq9pl",
    "VIDARA_API_KEY": "cf4a3701c18ed1d4e044ee4c116ecdad3c95de9d3e2e09ec6210512851109573",
    "ONECLOUD_API_KEY": "HpZFGCVRWlaMGLybm2SqyIkjW8AilubITKtLLXrleqjZCWuxHzTcooY3IwCC8fXZ",
    "GOFILE_TOKEN": "cx4wR4PUzr9z8QhC1KySejOaq9obdoSQ",
    "VK_ACCESS_TOKEN": "vk1.a._jd7hQ2JExSqiXa87k8xEsb1EBkBUi4am0HIwMACqafuqpUZVC_KhUj-RrZRKDK4BNnFIkblwgZ0G-5jc41HzleTWTXO_dMRX6steQpiV-gPJgyhVrSEHi2Uu1OSXXjSr2jE858IJhKHJJY9tfoM5oaZ_qdjWE92zCBylXb1Tm_NqzVKsd3zK_8jWj14Mc6463-3Cs8jn8maizzzQY1jcQ",
    "DOODSTREAM_API_KEY": "561449auivdyww0hr4t161",
    
    # R2 Account 1
    "R2_ACCOUNT_ID": "a28ef4137231ef7aa6756d28c5450bcd",
    "R2_ACCESS_KEY": "c889ca01c50cc327d73a3726e01225a8",
    "R2_SECRET_KEY": "a291f299669e419b8b5d85fa8cff421732fc3af32030b731260d844f6d5bc2a2",
    "R2_BUCKET": "media-stream",
    "R2_PUBLIC_URL": "https://pub-eb6d088b2e4848c1b93664d6cb1123d1.r2.dev",
    
    # R2 Account 2
    "R2_ACCOUNT_ID_2": "219e4c7e6fdd32bf12e92ce4d6aae16d",
    "R2_ACCESS_KEY_2": "071ed475fbcd9ac78bab47b71e26f540",
    "R2_SECRET_KEY_2": "70c383e89d8b0f4e3fe3cfd41312bb3ed352452a145fb0bee50d500dc9f950e1",
    "R2_BUCKET_2": "media3arabfleex",
    "R2_PUBLIC_URL_2": "https://pub-f5ebfb24da75411f840807f94b5d81c6.r2.dev", 
    
    # R2 Account 3
    "R2_ACCOUNT_ID_3": "f49ecf947be60e4be771af74d83fec06",
    "R2_ACCESS_KEY_3": "5fc8ce6005d241684fdf6c6d5bd9a0e4",
    "R2_SECRET_KEY_3": "49947415bef9ab7a6034b0edfdedd5c2a3a422d292269904c5e91801def17df7",
    "R2_BUCKET_3": "mediaarabfleexx",
    "R2_PUBLIC_URL_3": "https://pub-ac3d320399914e82916aa1a30981f882.r2.dev" 
}

def load_config():
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "w", encoding="utf-8") as f: 
            json.dump(DEFAULT_KEYS, f, indent=4)
        return DEFAULT_KEYS.copy()
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            updated = False
            for k, v in DEFAULT_KEYS.items():
                if k not in data: 
                    data[k] = v
                    updated = True
            if updated:
                with open(CONFIG_FILE, "w", encoding="utf-8") as f_update: 
                    json.dump(data, f_update, indent=4)
            return data
    except Exception: 
        return DEFAULT_KEYS.copy()

def save_config(config_data):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f: 
        json.dump(config_data, f, indent=4)

bot_config = load_config()

LARHU_DOMAIN = "larhu.website"
ABSTREAM_DOMAIN = "abstream.to"
UQLOAD_DOMAIN = "uqload.vc"
VIDMOLY_DOMAIN = "vidmoly.me"
VIDARA_API_DOMAIN = "api.vidara.so"
DOODSTREAM_DOMAIN = "doodapi.co"
ONECLOUD_DOMAIN = "1cloudfile.com"
ONECLOUD_ACCOUNT_ID = "128144"
GOFILE_ACCOUNT_ID = "b5184479-1587-46a6-b25d-8414ff17a4a2"

bot = telebot.TeleBot(TOKEN)
active_tasks = {}
upload_selections = {}
failed_uploads = {}
processed_messages = set()
task_queue = queue.Queue()
merge_sessions = {}
COMMON_USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

FONT_URL = "https://github.com/google/fonts/raw/main/ofl/opensans/OpenSans-SemiBold.ttf"
FONT_FILE = "opensans_semibold.ttf"

def download_font():
    if not os.path.exists(FONT_FILE):
        try:
            r = requests.get(FONT_URL, timeout=10)
            with open(FONT_FILE, 'wb') as f:
                f.write(r.content)
            print("✅ تم تحميل الخط بنجاح.")
        except Exception as e:
            print(f"❌ فشل تحميل الخط: {e}")

def worker():
    while True:
        task = task_queue.get()
        if task is None: break
        try:
            if task.get('type') == 'upload_only':
                upload_only_logic(task['chat_id'], task['msg_id'], task['task_id'])
            elif task.get('type') == 'merge':
                merge_process_logic(task['links'], task['chat_id'], task['msg_id'], task['servers'], task.get('name'), task.get('quality', 'best'), task.get('watermark', False), task.get('logo_pos', 'none'))
            else:
                process_logic(task['url'], task['chat_id'], task['msg_id'], task['servers'], task.get('name'), task.get('quality', 'best'), task.get('watermark', False), task.get('logo_pos', 'none'))
        except Exception as e: 
            print(f"Error in queue task: {e}")
        finally: 
            task_queue.task_done()

threading.Thread(target=worker, daemon=True).start()

def auto_cleanup():
    while True:
        try:
            now = time.time()
            for filename in os.listdir('.'):
                if filename.startswith(("video_", "out_", "err_", "merge_", "concat_", "part_", "encode_", "wm_out_")):
                    filepath = os.path.join('.', filename)
                    if os.path.isfile(filepath) and os.stat(filepath).st_mtime < now - (12 * 3600):
                        try: os.remove(filepath)
                        except: pass
        except: pass
        time.sleep(3600)

threading.Thread(target=auto_cleanup, daemon=True).start()

def keep_alive_ping():
    while True:
        try:
            requests.get("https://api.github.com/zen", timeout=10)
            with open(".keepalive", "w") as f: f.write(str(time.time()))
        except Exception: pass
        time.sleep(300)

threading.Thread(target=keep_alive_ping, daemon=True).start()

def make_bar(percent):
    p = min(100, max(0, int(percent)))
    filled = p // 10
    empty = 10 - filled
    return "█" * filled + "░" * empty

def format_size(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0: return f"{bytes_val:.2f} {unit}"
        bytes_val /= 1024.0

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

def get_cancel_keyboard(task_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("❌ إلغاء العملية", callback_data=f"cancel_{task_id}"))
    return markup

def safe_error_text(text):
    return str(text).replace('`', '').replace('*', '').replace('_', '').replace('[', '').replace(']', '')

def safe_edit(bot_instance, chat_id, message_id, text, reply_markup=None):
    try: 
        bot_instance.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=reply_markup, parse_mode="Markdown")
    except: 
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('cancel_'))
def cancel_task(call):
    task_id = call.data.replace('cancel_', '')
    if task_id in active_tasks:
        active_tasks[task_id]['cancel'] = True
        p = active_tasks[task_id].get('process')
        if p:
            try: p.terminate()
            except: pass
        bot.answer_callback_query(call.id, "🛑 جاري إيقاف العملية فوراً...")
    else: 
        bot.answer_callback_query(call.id, "⚠️ العملية انتهت أو لم تبدأ بعد.")

@bot.message_handler(commands=['start'])
def start(message):
    if message.chat.id != ADMIN_CHAT_ID: return
    welcome_text = f"""🤖 *مرحباً بك في بوت Arab Fleex الاحترافي!*

✨ *المميزات المدمجة:*
- 📥 سحب ورفع مباشر بكافة الجودات (مع فصل الحقوق).
- ☁️ دعم Cloudflare R2 متعدد الحسابات.
- 🧩 دمج وإنتاج جودات متعددة محلياً (نص شفاف + تمويه ذكي).
- ♻️ إعادة الرفع الذكية عند الفشل.

📋 *الأوامر:*
🔹 `/merge` - دمج عدة مقاطع.
🔹 `/stats` - حالة السيرفر.
🔹 `/keys` - إدارة المفاتيح.
🔹 `/queue` - عرض الطابور.
🔹 `/clearqueue` - مسح الطابور.
🔹 `/clean` - تنظيف الملفات.

📦 *الإصدار الحالي:* `{VERSION}`"""
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['merge'])
def start_merge_session(message):
    if message.chat.id != ADMIN_CHAT_ID: return
    merge_sessions[message.chat.id] = []
    bot.reply_to(message, "🧩 *وضع الدمج مفعل!*\n\nقم بإرسال الرابط **الأول** الآن.", parse_mode="Markdown")

@bot.message_handler(commands=['done'])
def finish_merge_session(message):
    if message.chat.id != ADMIN_CHAT_ID: return
    if message.chat.id not in merge_sessions or len(merge_sessions[message.chat.id]) == 0:
        bot.reply_to(message, "⚠️ لا توجد روابط مضافة للدمج. استخدم `/merge` للبدء.", parse_mode="Markdown")
        return
    links = merge_sessions.pop(message.chat.id)
    msg = bot.reply_to(message, f"✅ تم استلام `{len(links)}` روابط للدمج.\n\n📝 الرجاء إرسال **الاسم الشامل** للملف المدمج (أو أرسل `/skip` للافتراضي):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_name_step, links, is_merge=True)

@bot.message_handler(commands=['queue', 'clearqueue', 'clean'])
def manage_queue_and_clean(message):
    if message.chat.id != ADMIN_CHAT_ID: return
    cmd = message.text.split()[0].lower()
    if cmd == '/queue':
        q_list = list(task_queue.queue)
        if not q_list:
            bot.reply_to(message, "الطابور فارغ حالياً. ✅")
            return
        txt = f"🚦 *مهام الطابور الحالية ({len(q_list)}):*\n\n"
        for i, task in enumerate(q_list, 1):
            if task.get('type') == 'merge': 
                txt += f"{i}. `دمج {len(task['links'])} مقاطع`\n"
            else: 
                txt += f"{i}. `{task.get('name', 'رابط غير معروف')[:40]}`\n"
        bot.reply_to(message, txt, parse_mode="Markdown")
    elif cmd == '/clearqueue':
        count = task_queue.qsize()
        with task_queue.mutex: task_queue.queue.clear()
        bot.reply_to(message, f"🗑️ *تم تفريغ الطابور!*\nتم حذف `{count}` مهمة.", parse_mode="Markdown")
    elif cmd == '/clean':
        count = 0
        for filename in os.listdir('.'):
            if filename.startswith(("video_", "out_", "err_", "merge_", "concat_", "part_", "encode_", "wm_out_")):
                try: 
                    os.remove(filename)
                    count += 1
                except: pass
        bot.reply_to(message, f"🧹 *تم تنظيف {count} ملف مؤقت بنجاح.*", parse_mode="Markdown")

@bot.message_handler(func=lambda message: message.text and message.text.startswith('http'))
def handle_text_messages(message):
    if message.chat.id != ADMIN_CHAT_ID: return
    text = message.text.strip()
    
    if message.chat.id in merge_sessions:
        merge_sessions[message.chat.id].append(text)
        count = len(merge_sessions[message.chat.id])
        bot.reply_to(message, f"✅ تم استلام الرابط رقم `{count}`.\n\nأرسل الرابط التالي، أو أرسل `/done` إذا انتهيت من كل الأجزاء.", parse_mode="Markdown")
        return

    msg = bot.reply_to(message, "🔗 *تم استلام الرابط!*\n\n📝 الرجاء إرسال **اسم الملف الآن** (أو أرسل `/skip` لتخطي التسمية وترك الاسم الافتراضي):", parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_name_step, text, is_merge=False)

def process_name_step(message, data_input, is_merge=False):
    if message.chat.id != ADMIN_CHAT_ID: return
    custom_name = message.text.strip() if message.text and message.text.strip().lower() != '/skip' else None

    sent_msg = bot.send_message(message.chat.id, "⏳ جاري التجهيز...", parse_mode="Markdown")
    msg_id = sent_msg.message_id
    
    if is_merge:
        upload_selections[msg_id] = {'type': 'merge', 'links': data_input, 'name': custom_name, 'quality': 'best', 'servers': [], 'watermark': False, 'logo_pos': 'none'}
    else:
        upload_selections[msg_id] = {'type': 'single', 'url': data_input, 'name': custom_name, 'quality': 'best', 'servers': [], 'watermark': False, 'logo_pos': 'none'}
    
    bot.edit_message_text(
        f"✅ الاسم: `{custom_name or 'الاسم الافتراضي'}`\n\n🎯 *الرجاء اختيار جودة التحميل:*",
        chat_id=message.chat.id, message_id=msg_id,
        reply_markup=get_quality_keyboard(msg_id), parse_mode="Markdown"
    )

def get_quality_keyboard(msg_id):
    markup = InlineKeyboardMarkup(row_width=2)
    wm_state = upload_selections.get(msg_id, {}).get('watermark', False)
    markup.add(InlineKeyboardButton(f"🛡️ وضع الحقوق (اللوجو): {'✅ مفعل' if wm_state else '❌ معطل'}", callback_data=f"qual_wmtoggle_{msg_id}"))
    markup.add(InlineKeyboardButton("🌟 أعلى جودة", callback_data=f"qual_best_{msg_id}"), InlineKeyboardButton("📺 1080p", callback_data=f"qual_1080_{msg_id}"))
    markup.add(InlineKeyboardButton("📺 720p", callback_data=f"qual_720_{msg_id}"), InlineKeyboardButton("📱 480p", callback_data=f"qual_480_{msg_id}"))
    markup.add(InlineKeyboardButton("📱 360p", callback_data=f"qual_360_{msg_id}"))
    markup.add(InlineKeyboardButton("🎬 تحميل كل الجودات (من المصدر)", callback_data=f"qual_all_{msg_id}"))
    markup.add(InlineKeyboardButton("🎬 إنتاج محلي (720, 480, 360)", callback_data=f"qual_encode_{msg_id}"))
    markup.add(InlineKeyboardButton("🛑 إلغاء", callback_data=f"qual_cancel_{msg_id}"))
    return markup

def get_logo_position_keyboard(msg_id):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton("↖️ أعلى اليسار", callback_data=f"pos_tl_{msg_id}"),
        InlineKeyboardButton("↗️ أعلى اليمين", callback_data=f"pos_tr_{msg_id}")
    )
    markup.add(
        InlineKeyboardButton("↙️ أسفل اليسار", callback_data=f"pos_bl_{msg_id}"),
        InlineKeyboardButton("↘️ أسفل اليمين", callback_data=f"pos_br_{msg_id}")
    )
    markup.add(InlineKeyboardButton("❌ بدون طمس (طباعة فقط أعلى اليسار)", callback_data=f"pos_none_{msg_id}"))
    markup.add(InlineKeyboardButton("🛑 إلغاء", callback_data=f"pos_cancel_{msg_id}"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('pos_'))
def handle_logo_position(call):
    try: bot.answer_callback_query(call.id)
    except: pass
    parts = call.data.split('_')
    pos_action, msg_id = parts[1], int(parts[2])

    if pos_action == "cancel":
        upload_selections.pop(msg_id, None)
        safe_edit(bot, call.message.chat.id, msg_id, "🛑 *تم الإلغاء.*")
        return

    if msg_id not in upload_selections:
        try: bot.answer_callback_query(call.id, "⚠️ الجلسة انتهت.", show_alert=True)
        except: pass
        return

    upload_selections[msg_id]['logo_pos'] = pos_action

    name = upload_selections[msg_id]['name'] or 'الاسم الافتراضي'
    action = upload_selections[msg_id]['quality']
    q_names = {'best': 'أعلى جودة 🌟', '1080': '1080p 📺', '720': '720p 📺', '480': '480p 📱', '360': '360p 📱', 'all': 'تحميل كل الجودات 🎬', 'encode': 'إنتاج محلي متعدد 🎬'}
    
    pos_names = {'tl': 'أعلى اليسار', 'tr': 'أعلى اليمين', 'bl': 'أسفل اليسار', 'br': 'أسفل اليمين', 'none': 'بدون طمس'}
    wm_status = f"✅ مفعل (طمس: {pos_names.get(pos_action)})"

    bot.edit_message_text(
        f"✅ الاسم: `{name}`\n✅ الجودة: `{q_names.get(action)}`\n🛡️ الحقوق: `{wm_status}`\n\n🎯 اختر السيرفرات التي تريد الرفع عليها:",
        chat_id=call.message.chat.id, message_id=msg_id,
        reply_markup=get_selection_keyboard(msg_id), parse_mode="Markdown"
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('qual_'))
def handle_quality_selection(call):
    try: bot.answer_callback_query(call.id)
    except: pass
    parts = call.data.split('_')
    action, msg_id = parts[1], int(parts[2])

    if action == "cancel":
        upload_selections.pop(msg_id, None)
        safe_edit(bot, call.message.chat.id, msg_id, "🛑 *تم الإلغاء.*")
        return
        
    if action == "wmtoggle":
        if msg_id in upload_selections:
            upload_selections[msg_id]['watermark'] = not upload_selections[msg_id].get('watermark', False)
            bot.edit_message_reply_markup(call.message.chat.id, msg_id, reply_markup=get_quality_keyboard(msg_id))
        return

    if msg_id not in upload_selections:
        try: bot.answer_callback_query(call.id, "⚠️ الجلسة انتهت.", show_alert=True)
        except: pass
        return

    upload_selections[msg_id]['quality'] = action
    
    # إذا كانت الحقوق مفعلة، اذهب لواجهة تحديد مكان اللوجو أولاً
    if upload_selections[msg_id].get('watermark'):
        bot.edit_message_text(
            f"🔍 **أين يوجد اللوجو القديم في هذا الفيديو؟**\n(سيتم طمس المكان المحدد ووضع شعار ArabFleex فوقه)",
            chat_id=call.message.chat.id, message_id=msg_id,
            reply_markup=get_logo_position_keyboard(msg_id), parse_mode="Markdown"
        )
    else:
        # إذا لم تكن مفعلة، اذهب مباشرة لاختيار السيرفرات
        q_names = {'best': 'أعلى جودة 🌟', '1080': '1080p 📺', '720': '720p 📺', '480': '480p 📱', '360': '360p 📱', 'all': 'تحميل كل الجودات 🎬', 'encode': 'إنتاج محلي متعدد 🎬'}
        name = upload_selections[msg_id]['name'] or 'الاسم الافتراضي'
        bot.edit_message_text(
            f"✅ الاسم: `{name}`\n✅ الجودة: `{q_names.get(action)}`\n🛡️ الحقوق: `❌ معطل (سحب سريع)`\n\n🎯 اختر السيرفرات التي تريد الرفع عليها:",
            chat_id=call.message.chat.id, message_id=msg_id,
            reply_markup=get_selection_keyboard(msg_id), parse_mode="Markdown"
        )

ALL_SERVERS = ["CloudflareR2", "CloudflareR2_2", "CloudflareR2_3", "Abstream", "Larhu", "Uqload", "Vidmoly", "Vidara", "1cloudfile", "GoFile", "VK", "Doodstream"]

def get_selection_keyboard(msg_id):
    markup = InlineKeyboardMarkup(row_width=2)
    if msg_id not in upload_selections: return markup
    selected = upload_selections[msg_id]['servers']
    servers_list = [
        ("☁️ Cloudflare R2 (1)", "CloudflareR2"), ("☁️ Cloudflare R2 (2)", "CloudflareR2_2"),
        ("☁️ Cloudflare R2 (3)", "CloudflareR2_3"), ("🟢 ABStream", "Abstream"),
        ("🟠 Larhu", "Larhu"), ("🔵 Uqload", "Uqload"),
        ("🟣 Vidmoly", "Vidmoly"), ("🟡 Vidara", "Vidara"),
        ("☁️ 1cloudfile", "1cloudfile"), ("🌐 GoFile", "GoFile"),
        ("📘 VK", "VK"), ("🟤 Playmogo", "Doodstream")
    ]
    buttons = [InlineKeyboardButton(f"✅ {label}" if srv in selected else f"⬜ {label}", callback_data=f"sel_toggle_{srv}_{msg_id}") for label, srv in servers_list]
    for i in range(0, len(buttons), 2): markup.add(*buttons[i:i+2])
    markup.add(InlineKeyboardButton("✅ تحديد الكل", callback_data=f"sel_all_{msg_id}"), InlineKeyboardButton("❌ مسح التحديد", callback_data=f"sel_none_{msg_id}"))
    markup.add(InlineKeyboardButton("🚀 بـدء الـرفـع الآن", callback_data=f"sel_start_{msg_id}"))
    markup.add(InlineKeyboardButton("🛑 إلغاء", callback_data=f"sel_cancel_{msg_id}"))
    return markup

@bot.callback_query_handler(func=lambda call: call.data.startswith('sel_'))
def handle_custom_selection(call):
    try: bot.answer_callback_query(call.id)
    except: pass
    parts = call.data.split('_')
    action, msg_id = parts[1], int(parts[-1])
    
    if action == "cancel":
        upload_selections.pop(msg_id, None)
        safe_edit(bot, call.message.chat.id, msg_id, "🛑 *تم الإلغاء.*")
        return
        
    if msg_id not in upload_selections:
        try: bot.answer_callback_query(call.id, "⚠️ الجلسة انتهت.", show_alert=True)
        except: pass
        return
        
    try:
        if action == "toggle":
            srv = "_".join(parts[2:-1])
            if srv in upload_selections[msg_id]['servers']: upload_selections[msg_id]['servers'].remove(srv)
            else: upload_selections[msg_id]['servers'].append(srv)
            bot.edit_message_reply_markup(call.message.chat.id, msg_id, reply_markup=get_selection_keyboard(msg_id))
        elif action == "all":
            upload_selections[msg_id]['servers'] = ALL_SERVERS.copy()
            bot.edit_message_reply_markup(call.message.chat.id, msg_id, reply_markup=get_selection_keyboard(msg_id))
        elif action == "none":
            upload_selections[msg_id]['servers'] = []
            bot.edit_message_reply_markup(call.message.chat.id, msg_id, reply_markup=get_selection_keyboard(msg_id))
        elif action == "start":
            data = upload_selections.pop(msg_id)
            if not data['servers']:
                upload_selections[msg_id] = data
                try: bot.answer_callback_query(call.id, "⚠️ اختر سيرفر واحد على الأقل!", show_alert=True)
                except: pass
                return
                
            task_info = data
            task_info['chat_id'] = call.message.chat.id
            task_info['msg_id'] = msg_id
            task_queue.put(task_info)
            pos = task_queue.qsize()
            safe_edit(bot, call.message.chat.id, msg_id, "⏳ *جاري البدء...*" if pos == 1 else f"📝 *بالطابور: {pos}*")
    except Exception as e:
        if "message is not modified" not in str(e).lower(): print(f"❌ خطأ أزرار: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith('retryup_'))
def handle_retry_upload(call):
    task_id = call.data.split('retryup_')[1]
    if task_id not in failed_uploads or not os.path.exists(failed_uploads[task_id]['file']):
        try: bot.answer_callback_query(call.id, "⚠️ الملف غير موجود. يبدو أنه تم مسحه تلقائياً.", show_alert=True)
        except: pass
        return
    chat_id, msg_id = call.message.chat.id, call.message.message_id
    task_queue.put({'type': 'upload_only', 'chat_id': chat_id, 'msg_id': msg_id, 'task_id': task_id})
    pos = task_queue.qsize()
    try: bot.answer_callback_query(call.id, f"✅ تمت الإضافة (ترتيبك: {pos})")
    except: pass
    safe_edit(bot, chat_id, msg_id, f"⏳ *تمت إضافة إعادة الرفع للطابور (ترتيبك: {pos})...*")

def bypass_1cloudfile(url):
    headers = {'User-Agent': COMMON_USER_AGENT}
    r = requests.get(url, headers=headers, timeout=20)
    match = re.search(r'l\(\s*["\']([a-fA-F0-9]{40,})["\']\s*,', r.text)
    if match:
        hex_str = match.group(1)
        direct_link = "".join(chr(int(hex_str[i:i+2], 16) ^ 0x7A) for i in range(0, len(hex_str), 2))
        if direct_link.startswith("http"): return direct_link
    raise Exception("فشل سحب الرابط المباشر من 1cloudfile.")

def bypass_vidoba(url, bot_instance, chat_id, message_id, task_id):
    session = requests.Session()
    session.headers.update({'User-Agent': COMMON_USER_AGENT, 'Accept': 'text/html,*/*;q=0.8', 'Referer': 'https://vidoba.org/'})
    try:
        if task_id: safe_edit(bot_instance, chat_id, message_id, "🔍 *جاري فك حماية Vidoba...*", reply_markup=get_cancel_keyboard(task_id))
        r1 = session.get(url, timeout=15, verify=False)
        data1 = {}
        for name in ['op', 'id', 'mode', 'hash']:
            match = re.search(fr'name=["\']{name}["\']\s+value=["\']([^"\']*)["\']', r1.text)
            if match: data1[name] = match.group(1)
        if 'hash' not in data1:
            match_code = re.search(r'vidoba\.[a-z]+/(?:d/)?([a-zA-Z0-9_]+)', url)
            if match_code:
                code = match_code.group(1) + ('_n' if not code.endswith(('_n','_l','_h')) else '')
                r1 = session.get(f"https://vidoba.org/d/{code}", timeout=15, verify=False)
                for name in ['op', 'id', 'mode', 'hash']:
                    match = re.search(fr'name=["\']{name}["\']\s+value=["\']([^"\']*)["\']', r1.text)
                    if match: data1[name] = match.group(1)
        if 'hash' not in data1: raise Exception("لم يتم العثور على حقل الـ hash.")
        time.sleep(1)
        r2 = session.post(r1.url, data=data1, timeout=20, verify=False)
        match_link = re.search(r'href=["\'](https?://[^"\']+cdnz[^"\']+)["\']', r2.text, re.IGNORECASE) or re.search(r'href=["\'](https?://[^"\']+\.(?:mp4|mkv)[^"\']*)["\'][^>]*download-btn', r2.text, re.IGNORECASE)
        if match_link: return match_link.group(1).replace('&amp;', '&')
        raise Exception("فشلت استخراج الرابط.")
    except Exception as e: raise Exception(f"❌ Vidoba: {str(e)}")

def bypass_uqload(url, bot_instance, chat_id, message_id, task_id):
    try:
        if task_id: safe_edit(bot_instance, chat_id, message_id, "🔍 *جاري فك حماية Uqload...*", reply_markup=get_cancel_keyboard(task_id))
        headers = {'User-Agent': COMMON_USER_AGENT, 'Referer': 'https://uqload.is/'}
        r = requests.get(url, headers=headers, timeout=20, verify=False)
        packed = re.search(r"eval\(function\(p,a,c,k,e,d\)\{.*?\}\('(.*?)',(\d+),(\d+),'(.*?)'\.split\('\|'\)\)\)", r.text, re.DOTALL)
        if not packed: raise Exception("لم يتم العثور على مشغل الفيديو.")
        p, a, c, k = packed.group(1), int(packed.group(2)), int(packed.group(3)), packed.group(4).split('|')
        def replace(m):
            word = m.group(0)
            try:
                n = int(word, a)
                return k[n] if n < len(k) and k[n] else word
            except: return word
        decoded = re.sub(r'\b\w+\b', replace, p)
        urls = re.findall(r'https?://[^\\"\' ]+\.m3u8[^\\"\' ]*', decoded)
        if urls: return urls[0], 'https://uqload.is/'
        raise Exception("لم يتم العثور على الرابط.")
    except Exception as e: raise Exception(f"❌ Uqload: {str(e)}")

def bypass_frdl(url, bot_instance, chat_id, message_id, task_id):
    if not HAS_PLAYWRIGHT: raise Exception("Playwright غير مثبت بالسيرفر.")
    try:
        if task_id: safe_edit(bot_instance, chat_id, message_id, "🔍 *جاري التخطي: frdl.my (تشغيل المتصفح الوهمي)...*", reply_markup=get_cancel_keyboard(task_id))
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox', '--disable-dev-shm-usage'])
            context = browser.new_context(user_agent=COMMON_USER_AGENT)
            page = context.new_page()
            page.goto(url, timeout=60000)
            final_link = page.query_selector('a:has-text("Download Now")')
            if final_link: 
                href = final_link.get_attribute("href")
                browser.close()
                return href, url
            for i in range(60, 0, -5):
                if active_tasks.get(task_id, {}).get("cancel"): 
                    browser.close()
                    raise Exception("🛑 تم إلغاء العملية.")
                if task_id: safe_edit(bot_instance, chat_id, message_id, f"⏳ *ننتظر {i} ثانية لتخطي الموقع...*", reply_markup=get_cancel_keyboard(task_id))
                page.wait_for_timeout(5000)
            try:
                page.evaluate("document.FREE1.submit()")
                page.wait_for_load_state("networkidle", timeout=30000)
            except:
                try: 
                    page.click('#downloadbtnfree', force=True)
                    page.wait_for_load_state("networkidle", timeout=30000)
                except: pass
            final_link = page.query_selector('a:has-text("Download Now")')
            if final_link: 
                href = final_link.get_attribute("href")
                browser.close()
                return href, url
            if page.query_selector('.h-captcha'): 
                browser.close()
                raise Exception("السيرفر يطلب كابتشا.")
            browser.close()
            raise Exception("فشلت محاولة استخراج الرابط بالمتصفح.")
    except Exception as e: raise Exception(f"❌ frdl.my: {str(e)}")

def bypass_player4me(url):
    try:
        session = requests.Session()
        base_url = url.split('#')[0].rstrip('/')
        session.headers.update({'User-Agent': COMMON_USER_AGENT, 'Origin': 'https://arabfleex.4meplayer.com', 'Referer': url})
        match_hash = re.search(r'#([a-zA-Z0-9]+)', url)
        if not match_hash: raise Exception("لم يتم العثور على ID.")
        vid_id = match_hash.group(1).split('&')[0]
        try: session.get(url, timeout=10)
        except: pass
        try:
            r_info = session.get(f"{base_url}/info?id={vid_id}", timeout=15)
            match_mp4 = re.search(r'(https?://[^\'"]+\.mp4[^\'"]*)', r_info.text.replace('\\/', '/'), re.IGNORECASE)
            if match_mp4: return match_mp4.group(1).replace('&amp;', '&')
        except: pass
        api_url = f"{base_url}/api/v1/download?id={vid_id}&w=1920&h=1080&r="
        r_api = session.get(api_url, timeout=15)
        clean_text = r_api.text.replace('\\/', '/')
        match_mp4 = re.search(r'(https?://[^\'"]+\.mp4[^\'"]*)', clean_text, re.IGNORECASE)
        if match_mp4: return match_mp4.group(1).replace('&amp;', '&')
        raise Exception(f"لم يتم العثور على الرابط.")
    except Exception as e: raise Exception(f"❌ Player4Me: {str(e)}")

def apply_cf_proxy(url):
    if "workers.dev" in url: return url
    if "b2.shahidtv.net" in url and (".mp4" in url or ".m3u8" in url):
        return f"https://shy-snow-52c3.alifalah9988044.workers.dev/?url={url}"
    # معالجة روابط ok.ru إذا كانت embed
    if "ok.ru/videoembed/" in url:
        return url.replace("videoembed/", "video/")
    return url

def get_video_quality(filepath):
    try:
        cmd = ["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", filepath]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout.strip()
        
        if output and 'x' in output:
            w_str, h_str = output.split('x')
            if w_str.isdigit() and h_str.isdigit():
                w, h = int(w_str), int(h_str)
                if w >= 3800 or h >= 2000: return "4K"
                elif w >= 2500 or h >= 1400: return "1440p"
                elif w >= 1900 or h >= 1000: return "1080p"
                elif w >= 1200 or h >= 700: return "720p"
                elif w >= 800 or h >= 480: return "480p"
                elif w >= 600 or h >= 360: return "360p"
                elif w >= 400 or h >= 240: return "240p"
                else: return "144p"
    except: pass
    return "Unknown"

def get_video_duration(filepath):
    try:
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return float(result.stdout.strip())
    except: return 0.0

def run_ffmpeg_with_progress(cmd, duration, task_id, bot_instance, chat_id, message_id, custom_msg):
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
    if task_id in active_tasks: active_tasks[task_id]['process'] = process
    last_update = time.time()
    
    for line in iter(process.stdout.readline, ''):
        if task_id in active_tasks and active_tasks.get(task_id, {}).get("cancel"):
            process.terminate(); raise Exception("🛑 تم إلغاء العملية.")
            
        if time.time() - last_update > 4 and "time=" in line:
            time_match = re.search(r'time=(\d{2}:\d{2}:\d{2}\.\d{2})', line)
            speed_match = re.search(r'speed=\s*([\d\.]+x)', line)
            if time_match:
                time_str = time_match.group(1)
                speed_str = speed_match.group(1) if speed_match else "؟"
                
                perc_str = ""
                if duration > 0:
                    try:
                        h, m, s = time_str.split(':')
                        current_sec = int(h)*3600 + int(m)*60 + float(s)
                        perc = min(100, (current_sec / duration) * 100)
                        perc_str = f"📊 التقدم: `[{make_bar(perc)}]` *{int(perc)}%*\n"
                    except: pass
                    
                txt = f"{custom_msg}\n\n{perc_str}⏱️ المعالج: `{time_str[:8]}`\n🚀 السرعة: `{speed_str}`"
                safe_edit(bot_instance, chat_id, message_id, txt, reply_markup=get_cancel_keyboard(task_id))
                last_update = time.time()
                
    process.wait()
    return process.returncode

def build_encode_cmd(input_file, scale_str, out_name, add_watermark=False, logo_pos="none"):
    filter_parts = []
    
    # فلتر تغيير الحجم
    if scale_str and scale_str != "iw:ih":
        filter_parts.append(f"scale={scale_str}")

    # إضافة التمويه (delogo) وطباعة اللوجو
    if add_watermark and os.path.exists(FONT_FILE):
        abs_font = os.path.abspath(FONT_FILE).replace('\\', '/')
        
        # الأبعاد الافتراضية للتمويه والنص (أعلى اليسار)
        dx, dy, dw, dh = "20", "20", "240", "70" # أبعاد التمويه (عرض 240، ارتفاع 70)
        tx, ty = "35", "35" # مكان النص

        if logo_pos == "tr": # أعلى اليمين
            dx, dy = "W-260", "20"
            tx, ty = "w-tw-35", "35"
        elif logo_pos == "bl": # أسفل اليسار
            dx, dy = "20", "H-90"
            tx, ty = "35", "h-th-35"
        elif logo_pos == "br": # أسفل اليمين
            dx, dy = "W-260", "H-90"
            tx, ty = "w-tw-35", "h-th-35"

        # إضافة فلتر الطمس فقط إذا لم يختر المستخدم "بدون طمس"
        if logo_pos != "none":
            filter_parts.append(f"delogo=x={dx}:y={dy}:w={dw}:h={dh}")
            
        # إضافة فلتر طباعة الشعار الجديد
        filter_parts.append(f"drawtext=fontfile='{abs_font}':text='ArabFleex':fontcolor=white:fontsize=28:x={tx}:y={ty}:bordercolor=black:borderw=2")

    if filter_parts:
        filter_str = ",".join(filter_parts)
        return ["ffmpeg", "-y", "-i", input_file, "-vf", filter_str, "-c:v", "libx264", "-crf", "23", "-preset", "ultrafast", "-c:a", "aac", out_name]
    else:
        # النسخ المباشر بدون فلاتر
        return ["ffmpeg", "-y", "-i", input_file, "-c:v", "copy", "-c:a", "copy", out_name]

def encode_local_qualities(input_file, base_name, task_id, bot_instance, chat_id, message_id, watermark=False, logo_pos="none"):
    produced_files = []
    resolutions = [("720p", "-2:720"), ("480p", "-2:480"), ("360p", "-2:360")]
    duration = get_video_duration(input_file)
    
    for q_label, scale in resolutions:
        if active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
        out_name = f"encode_{task_id}_{q_label}.mp4"
        wm_text = " (مع الحقوق)" if watermark else ""
        custom_msg = f"🎬 *جاري إنتاج جودة {q_label} محلياً{wm_text}...*"
        safe_edit(bot_instance, chat_id, message_id, custom_msg, reply_markup=get_cancel_keyboard(task_id))
        
        cmd = build_encode_cmd(input_file, scale, out_name, add_watermark=watermark, logo_pos=logo_pos)
        retcode = run_ffmpeg_with_progress(cmd, duration, task_id, bot_instance, chat_id, message_id, custom_msg)
        
        if retcode == 0 and os.path.exists(out_name):
            produced_files.append((f"{base_name} - {q_label}", out_name))
    return produced_files

def download_manager(url, filename, bot_instance, chat_id, message_id, task_id, referer=None, origin=None, custom_msg="📥 *المرحلة 1: جاري التحميل...*", quality="best"):
    if task_id and message_id: safe_edit(bot_instance, chat_id, message_id, custom_msg, reply_markup=get_cancel_keyboard(task_id))
    extra_headers = []
    if referer: extra_headers += ["--add-header", f"Referer:{referer}"]
    if origin: extra_headers += ["--add-header", f"Origin:{origin}"]
    
    if quality == '1080': yt_dlp_format = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/best[height<=1080][ext=mp4]/best"
    elif quality == '720': yt_dlp_format = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best"
    elif quality == '480': yt_dlp_format = "bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best"
    elif quality == '360': yt_dlp_format = "bestvideo[height<=360][ext=mp4]+bestaudio[ext=m4a]/best[height<=360][ext=mp4]/best"
    else: yt_dlp_format = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
    
    try:  
        cmd = ["python", "-m", "yt_dlp", "--no-playlist", "--geo-bypass", "-N", "8", "--newline", "--no-warnings", "--no-check-certificate", "-f", yt_dlp_format, "--remux-video", "mp4", "--hls-prefer-native", "-o", filename, "--user-agent", COMMON_USER_AGENT]
        if os.path.exists("cookies.txt"): cmd.extend(["--cookies", "cookies.txt"])
        cmd.extend(extra_headers); cmd.append(url)
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)
        if task_id in active_tasks: active_tasks[task_id]['process'] = process
        last_update = time.time()
        for line in iter(process.stdout.readline, ''):
            if task_id in active_tasks and active_tasks.get(task_id, {}).get("cancel"):
                process.terminate(); raise Exception("🛑 تم إلغاء العملية.")
            if task_id and message_id and time.time() - last_update > 3 and "[download]" in line and "%" in line:
                perc_m, speed_m, eta_m = re.search(r'([\d\.]+)\%', line), re.search(r'at\s+([\d\.\w]+)', line), re.search(r'ETA\s+([\d:]+)', line)
                if perc_m:
                    txt = f"{custom_msg.split('*')[1]} *(المحرك الأساسي)*\n\n📊 التقدم: `[{make_bar(float(perc_m.group(1)))}]` *{float(perc_m.group(1))}%*\n🚀 السرعة: `{speed_m.group(1) if speed_m else '؟'}`\n⏳ الوقت: `{eta_m.group(1) if eta_m else '--:--'}`"
                    safe_edit(bot_instance, chat_id, message_id, txt, reply_markup=get_cancel_keyboard(task_id))
                    last_update = time.time()
        process.wait()
        
        if process.returncode != 0 or not os.path.exists(filename):
            req_headers = {'User-Agent': COMMON_USER_AGENT}
            if referer: req_headers['Referer'] = referer
            if origin: req_headers['Origin'] = origin
            r = requests.get(url, headers=req_headers, stream=True, timeout=20, verify=False)
            r.raise_for_status()
            total_size, downloaded, start_dl_time, last_update = int(r.headers.get('content-length', 0)), 0, time.time(), time.time()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(2 * 1024 * 1024):
                    if task_id in active_tasks and active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        now = time.time()
                        if task_id and message_id and now - last_update > 3:
                            perc = (downloaded / total_size) * 100 if total_size else 0
                            speed = downloaded / (now - start_dl_time) if (now - start_dl_time) > 0 else 0
                            rem_time = (total_size - downloaded) / speed if speed > 0 and total_size else 0
                            txt = f"{custom_msg.split('*')[1]} *(المحرك الاحتياطي)*\n\n📊 التقدم: `[{make_bar(perc)}]` *{int(perc)}%*\n🚀 السرعة: `{format_size(speed)}/s`\n⏳ الوقت: `{format_time(rem_time)}`"
                            safe_edit(bot_instance, chat_id, message_id, txt, reply_markup=get_cancel_keyboard(task_id))
                            last_update = now
        return process.returncode
    except Exception as e:
        raise Exception(f"فشل التحميل: {safe_error_text(e)}")

class R2ProgressCallback:
    def __init__(self, total_bytes, progress_dict, site_name, task_id):
        self.total_bytes, self.bytes_so_far, self.progress_dict, self.site_name, self.task_id = total_bytes, 0, progress_dict, site_name, task_id
    def __call__(self, bytes_amount):
        if active_tasks.get(self.task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
        self.bytes_so_far += bytes_amount
        if self.total_bytes > 0: self.progress_dict[self.site_name] = (self.bytes_so_far / self.total_bytes) * 100

def upload_to_r2(file_path, safe_filename, custom_name, task_id, progress_dict, result_dict, site_name="CloudflareR2"):
    try:
        if active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
        progress_dict[site_name] = "🔍 الاتصال بـ R2..."
        
        if site_name == "CloudflareR2_2":
            acc_id, acc_key, sec_key = bot_config["R2_ACCOUNT_ID_2"], bot_config["R2_ACCESS_KEY_2"], bot_config["R2_SECRET_KEY_2"]
            bucket, pub_url = bot_config["R2_BUCKET_2"], bot_config.get("R2_PUBLIC_URL_2", "")
        elif site_name == "CloudflareR2_3":
            acc_id, acc_key, sec_key = bot_config["R2_ACCOUNT_ID_3"], bot_config["R2_ACCESS_KEY_3"], bot_config["R2_SECRET_KEY_3"]
            bucket, pub_url = bot_config["R2_BUCKET_3"], bot_config.get("R2_PUBLIC_URL_3", "")
        else:
            acc_id, acc_key, sec_key = bot_config["R2_ACCOUNT_ID"], bot_config["R2_ACCESS_KEY"], bot_config["R2_SECRET_KEY"]
            bucket, pub_url = bot_config["R2_BUCKET"], bot_config.get("R2_PUBLIC_URL", "")
            
        if not all([acc_id, acc_key, sec_key, bucket]): raise Exception("بيانات الدخول لهذا الحساب غير مكتملة.")

        s3_client = boto3.client(
            service_name='s3', endpoint_url=f'https://{acc_id}.r2.cloudflarestorage.com',
            aws_access_key_id=acc_key, aws_secret_access_key=sec_key,
            region_name='auto', config=Config(signature_version='s3v4')
        )
        progress_dict[site_name] = "📤 جاري الرفع..."
        remote_path = f"EG/{safe_filename}"
        s3_client.upload_file(
            Filename=file_path, Bucket=bucket, Key=remote_path,
            ExtraArgs={'ContentType': 'video/mp4'}, Callback=R2ProgressCallback(os.path.getsize(file_path), progress_dict, site_name, task_id)
        )
        encoded_path = quote(remote_path)
        base_domain = pub_url.rstrip('/') if pub_url else f"https://{acc_id}.r2.cloudflarestorage.com/{bucket}"
        result_dict[site_name] = f"{base_domain}/{encoded_path}"
        progress_dict[site_name] = "✅ مكتمل"
    except Exception as e:
        progress_dict[site_name] = "❌ فشل"; result_dict[site_name] = f"ERROR:{safe_error_text(e)}"

def upload_to_vk(file_path, safe_filename, custom_name, task_id, progress_dict, result_dict):
    site_name = "VK"
    try:
        if active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
        progress_dict[site_name] = "🔍 جلب السيرفر..."
        res = requests.post("https://api.vk.com/method/video.save", data={"access_token": bot_config["VK_ACCESS_TOKEN"], "v": "5.199", "name": custom_name or safe_filename, "wallpost": 0}, timeout=15).json()
        if "error" in res: raise Exception(f"خطأ في API: {res['error'].get('error_msg')}")
        upload_url = res["response"]["upload_url"]
        progress_dict[site_name] = "📤 جاري الرفع..."
        for attempt in range(3):
            try:
                with open(file_path, 'rb') as fh:
                    encoder = MultipartEncoder(fields={'video_file': (safe_filename, fh, 'video/mp4')})
                    def _cb(monitor):
                        if active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
                        if monitor.len > 0: progress_dict[site_name] = (monitor.bytes_read / monitor.len) * 100
                    up_res = requests.post(upload_url, data=MultipartEncoderMonitor(encoder, _cb), headers={'Content-Type': encoder.content_type}, timeout=1800).json()
                break
            except Exception as e:
                if attempt == 2: raise e
                progress_dict[site_name] = f"⚠️ محاولة ({attempt+1}/3)..."; time.sleep(5)
        if "video_hash" in up_res or "size" in up_res:
            acc_key = res["response"].get("access_key", "")
            result_dict[site_name] = f"https://vk.com/video_ext.php?oid={res['response']['owner_id']}&id={res['response']['video_id']}&hash={acc_key}" if acc_key else f"https://vk.com/video{res['response']['owner_id']}_{res['response']['video_id']}"
            progress_dict[site_name] = "✅ مكتمل"
        else: raise Exception("خطأ أثناء الرفع")
    except Exception as e: progress_dict[site_name] = "❌ فشل"; result_dict[site_name] = f"ERROR:{safe_error_text(e)}"

def upload_to_gofile(file_path, safe_filename, task_id, progress_dict, result_dict):
    site_name = "GoFile"
    try:
        if active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
        progress_dict[site_name] = "🔍 جلب السيرفر..."
        server = requests.get('https://api.gofile.io/servers', timeout=15).json()['data']['servers'][0]['name']
        progress_dict[site_name] = "📤 جاري الرفع..."
        for attempt in range(3):
            try:
                with open(file_path, 'rb') as fh:
                    encoder = MultipartEncoder(fields={'file': (safe_filename, fh, 'video/mp4')})
                    def _cb(monitor):
                        if active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
                        if monitor.len > 0: progress_dict[site_name] = (monitor.bytes_read / monitor.len) * 100
                    up = requests.post(f'https://{server}.gofile.io/contents/uploadfile', data=MultipartEncoderMonitor(encoder, _cb), headers={'Content-Type': encoder.content_type, 'Authorization': f'Bearer {bot_config["GOFILE_TOKEN"]}'}, timeout=1800)
                break
            except Exception as e:
                if attempt == 2: raise e
                progress_dict[site_name] = f"⚠️ محاولة ({attempt+1}/3)..."; time.sleep(5)
        data = up.json()
        if data.get('status') == 'ok': result_dict[site_name] = data['data']['downloadPage']; progress_dict[site_name] = "✅ مكتمل"
        else: raise Exception("خطأ في رفع GoFile")
    except Exception as e: progress_dict[site_name] = "❌ فشل"; result_dict[site_name] = f"ERROR:{safe_error_text(e)}"

def upload_to_xfs(domain, api_key, file_path, safe_filename, site_name, task_id, progress_dict, result_dict):
    try:
        if active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
        
        if site_name == "1cloudfile":
            progress_dict[site_name] = "🔍 جاري الرفع..."
            upload_url = f"https://{domain}/api/v2/file/upload?access_token={api_key}&account_id={ONECLOUD_ACCOUNT_ID}"
            with open(file_path, 'rb') as file_handle:
                encoder = MultipartEncoder(fields={'upload_file': (safe_filename, file_handle, 'video/mp4')})
                def _cb(monitor):
                    if active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
                    if monitor.len > 0: progress_dict[site_name] = (monitor.bytes_read / monitor.len) * 100
                up_req = requests.post(upload_url, data=MultipartEncoderMonitor(encoder, _cb), headers={'Content-Type': encoder.content_type, 'User-Agent': COMMON_USER_AGENT}, timeout=1800, verify=False)
            try:
                json_resp = up_req.json()
                if json_resp.get('_status') == 'success' and 'data' in json_resp and len(json_resp['data']) > 0:
                    result_dict[site_name] = json_resp['data'][0].get('short_url', 'ERROR:الكود مفقود')
                else: result_dict[site_name] = f"ERROR:{json_resp.get('response', str(json_resp)[:40])}"
            except: result_dict[site_name] = "ERROR:صيغة غير صحيحة"
        else:
            progress_dict[site_name] = "🔍 جلب السيرفر..."
            headers = {'User-Agent': COMMON_USER_AGENT, 'Accept': 'application/json'}
            if site_name == "Vidara":
                upload_url = requests.get(f"https://{VIDARA_API_DOMAIN}/v1/upload/server?api_key={api_key}", headers=headers, timeout=20, verify=False).json().get('result', {}).get('upload_server')
            else:
                upload_url = None
                for attempt in range(3):
                    try:
                        srv_data = requests.get(f"https://{domain}/api/upload/server?key={api_key}", headers=headers, timeout=20, verify=False).json()
                        res_data = srv_data.get('result')
                        upload_url = res_data if isinstance(res_data, str) and res_data.startswith('http') else (res_data.get('url') if isinstance(res_data, dict) else srv_data.get('url'))
                        if upload_url: break
                        time.sleep(5)
                    except: time.sleep(5)
            if not upload_url: raise Exception("فشل جلب السيرفر")
            if upload_url.startswith('//'): upload_url = 'https:' + upload_url
            if site_name != "Vidara": upload_url += f"{'&' if '?' in upload_url else '?'}json=1&api_key={api_key}"
            
            with open(file_path, 'rb') as file_handle:
                fields = {'key': api_key, 'api_key': api_key, 'file': (safe_filename, file_handle, 'video/mp4')} if site_name == "Vidara" else {'key': api_key, 'api_key': api_key, 'sess_id': api_key, 'upload_type': 'file', 'file': (safe_filename, file_handle, 'video/mp4')}
                encoder = MultipartEncoder(fields=fields)
                def _cb(monitor):
                    if active_tasks.get(task_id, {}).get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
                    if monitor.len > 0: progress_dict[site_name] = (monitor.bytes_read / monitor.len) * 100
                up_req = requests.post(upload_url, data=MultipartEncoderMonitor(encoder, _cb), headers={'Content-Type': encoder.content_type}, timeout=1800, verify=False)
            
            try:
                data = up_req.json()
                video_code = data.get('filecode') if site_name == "Vidara" else None
                if not video_code:
                    if 'files' in data and isinstance(data['files'], list) and len(data['files']) > 0: video_code = data['files'][0].get('filecode')
                    elif 'result' in data and isinstance(data['result'], list) and len(data['result']) > 0: video_code = data['result'][0].get('filecode')
                if not video_code:
                    match = re.search(r'"(?:file_code|filecode)"\s*:\s*"([a-zA-Z0-9]+)"', json.dumps(data), re.IGNORECASE)
                    if match: video_code = match.group(1)
                result_dict[site_name] = video_code if video_code else "ERROR:الكود مفقود"
            except:
                match = re.search(r"name=['\"]fn['\"][^>]*>([a-zA-Z0-9]+)<", up_req.text, re.IGNORECASE)
                result_dict[site_name] = match.group(1).strip() if match else "ERROR:رد غير متوقع"

        progress_dict[site_name] = "✅ مكتمل" if result_dict.get(site_name) and not str(result_dict.get(site_name)).startswith("ERROR:") else "❌ فشل"
    except Exception as e:
        progress_dict[site_name] = "❌ فشل"; result_dict[site_name] = f"ERROR:{safe_error_text(e)}"

def generate_final_links(target_servers, res_dict):
    watch_links, download_links, failed_sites = [], [], []
    for site in target_servers:
        code = res_dict.get(site)
        if code and not str(code).startswith("ERROR:"):
            if site == 'CloudflareR2':
                download_links.append(f"Cloudflare R2 (1):\n└  {code}")
            elif site == 'CloudflareR2_2':
                download_links.append(f"Cloudflare R2 (2):\n└  {code}")
            elif site == 'CloudflareR2_3':
                download_links.append(f"Cloudflare R2 (3):\n└  {code}")
            elif site == 'Abstream': 
                watch_links.append(f"ABStream:\n└  https://abstream.to/embed-{code}.html")
            elif site == 'Larhu': 
                watch_links.append(f"Larhu:\n└  https://larhu.website/embed-{code}.html")
            elif site == 'Vidmoly': 
                watch_links.append(f"Vidmoly:\n└  https://vidmoly.biz/embed-{code}.html")
            elif site == 'Uqload':
                watch_links.append(f"Uqload:\n└  https://uqload.vc/embed-{code}.html")
                download_links.append(f"Uqload:\n└  https://uqload.vc/{code}")
            elif site == 'Vidara': 
                watch_links.append(f"Vidara:\n└  {code if str(code).startswith('http') else f'https://vidaraa.cc/e/{code}'}")
            elif site == 'Doodstream': 
                watch_links.append(f"Doodstream:\n└  https://dood.to/e/{code}")
                download_links.append(f"Doodstream:\n└  https://dood.to/d/{code}")
            elif site == 'GoFile': 
                download_links.append(f"GoFile:\n└  {code}")
            elif site == 'VK': 
                watch_links.append(f"VK:\n└  {code}")
            elif site == '1cloudfile': 
                download_links.append(f"1cloudfile:\n└  {code}")
        else:
            err = str(code).replace('ERROR:', '') if code else 'فشل غير معروف'
            site_display = site.replace('_2', ' (2)').replace('_3', ' (3)')
            failed_sites.append(f"{site_display}:\n└  {err}")
    return watch_links, download_links, failed_sites

def process_logic(url, chat_id, message_id, target_servers, custom_name, quality="best", watermark=False, logo_pos="none"):
    task_id = f"{chat_id}_{message_id}_{int(time.time())}"
    active_tasks[task_id] = {"cancel": False, "process": None}
    out_file = f"out_{task_id}.mp4"
    success = False

    try:
        ref, org = None, None
        if "4meplayer" in url or "player4me" in url: url = bypass_player4me(url); ref = "https://arabfleex.4meplayer.com/"
        elif "vidoba" in url: url = bypass_vidoba(url, bot, chat_id, message_id, task_id); ref = "https://vidoba.org/"
        elif "1cloudfile" in url: url = bypass_1cloudfile(url)
        elif "up4ever" in url or "/d/" in url: ref = "https://www.up-4ever.net/"
        elif "uqload" in url and (".mp4" in url or "/v/" in url): ref, org = "https://uqload.is/", "https://uqload.is"
        elif "uqload" in url: url, ref = bypass_uqload(url, bot, chat_id, message_id, task_id)
        elif "frdl.my" in url: url, ref = bypass_frdl(url, bot, chat_id, message_id, task_id); org = "https://frdl.my"

        url = apply_cf_proxy(url)
        base_title = custom_name or f"Video_{random.randint(1000, 9999)}"

        if quality == 'all':
            qualities_to_download = ['1080', '720', '480', '360']
            for q in qualities_to_download:
                q_file = f"out_{task_id}_{q}.mp4"
                download_manager(url, q_file, bot, chat_id, message_id, task_id, referer=ref, origin=org, custom_msg=f"📥 *جاري تحميل جودة {q}p...*", quality=q)
                if os.path.exists(q_file) and os.path.getsize(q_file) > 500000:
                    actual_q = get_video_quality(q_file)
                    
                    needs_encode = watermark # الإجبار على الضغط لو الحقوق مفعلة
                    scale_val = f"-2:{q}"
                    
                    quality_hierarchy = {"144p": 1, "240p": 2, "360p": 3, "480p": 4, "720p": 5, "1080p": 6, "1440p": 7, "4K": 8, "Unknown": 0}
                    if quality_hierarchy.get(actual_q, 0) > quality_hierarchy.get(f"{q}p", 0):
                        needs_encode = True
                        
                    if needs_encode:
                        duration = get_video_duration(q_file)
                        wm_text = " (مع الحقوق)" if watermark else ""
                        custom_msg = f"🎬 *جاري الضغط لـ {q}p محلياً{wm_text}...*"
                        safe_edit(bot, chat_id, message_id, custom_msg, reply_markup=get_cancel_keyboard(task_id))
                        encoded_file = f"encode_forced_{task_id}_{q}.mp4"
                        
                        cmd = build_encode_cmd(q_file, scale_val, encoded_file, add_watermark=watermark, logo_pos=logo_pos)
                        retcode = run_ffmpeg_with_progress(cmd, duration, task_id, bot, chat_id, message_id, custom_msg)
                        
                        if retcode == 0 and os.path.exists(encoded_file):
                            try: os.remove(q_file)
                            except: pass
                            q_file = encoded_file
                            actual_q = f"{q}p"

                    display_q = actual_q if actual_q != "Unknown" else f"{q}p"
                    sub_name = f"{base_title} - {display_q}"
                    safe_name = f"{re.sub(r'[^\w\s\u0600-\u06FF-]', '', sub_name).strip().replace(' ', '_')[:40]}.mp4"
                    upload_and_send(q_file, safe_name, sub_name, chat_id, message_id, target_servers, task_id)
            success = True
            return

        elif quality == 'encode':
            download_manager(url, out_file, bot, chat_id, message_id, task_id, referer=ref, origin=org, custom_msg=f"📥 *جاري تحميل الفيديو الأصلي لإنتاج الجودات...*", quality='best')
            if not os.path.exists(out_file) or os.path.getsize(out_file) < 500000: raise Exception("❌ الملف تالف أو فارغ.")
            
            encoded_list = encode_local_qualities(out_file, base_title, task_id, bot, chat_id, message_id, watermark=watermark, logo_pos=logo_pos)
            try: os.remove(out_file)
            except: pass

            for sub_name, q_file in encoded_list:
                safe_name = f"{re.sub(r'[^\w\s\u0600-\u06FF-]', '', sub_name).strip().replace(' ', '_')[:40]}.mp4"
                upload_and_send(q_file, safe_name, sub_name, chat_id, message_id, target_servers, task_id)
            success = True
            return

        # Single specific quality or Best
        download_manager(url, out_file, bot, chat_id, message_id, task_id, referer=ref, origin=org, custom_msg=f"📥 *المرحلة 1: جاري التحميل...*", quality=quality)
        if not os.path.exists(out_file) or os.path.getsize(out_file) < 500000: raise Exception("❌ الملف تالف أو فارغ.")
        
        actual_quality = get_video_quality(out_file)
        
        needs_encode = watermark
        scale_val = None
        
        if quality in ['1080', '720', '480', '360']:
            requested_q_label = f"{quality}p"
            quality_hierarchy = {"144p": 1, "240p": 2, "360p": 3, "480p": 4, "720p": 5, "1080p": 6, "1440p": 7, "4K": 8, "Unknown": 0}
            
            if quality_hierarchy.get(actual_quality, 0) > quality_hierarchy.get(requested_q_label, 0):
                needs_encode = True
                scale_val = f"-2:{quality}"

        if needs_encode:
            duration = get_video_duration(out_file)
            wm_text = "مع إضافة الحقوق والتمويه" if watermark else "تحجيم أبعاد الفيديو"
            custom_msg = f"🎬 *جاري المعالجة محلياً ({wm_text})...*"
            safe_edit(bot, chat_id, message_id, custom_msg, reply_markup=get_cancel_keyboard(task_id))
            encoded_file = f"encode_forced_{task_id}.mp4"
            
            cmd = build_encode_cmd(out_file, scale_val, encoded_file, add_watermark=watermark, logo_pos=logo_pos)
            retcode = run_ffmpeg_with_progress(cmd, duration, task_id, bot, chat_id, message_id, custom_msg)
            
            if retcode == 0 and os.path.exists(encoded_file):
                try: os.remove(out_file)
                except: pass
                out_file = encoded_file
                if scale_val: actual_quality = f"{quality}p"

        display_quality = actual_quality if actual_quality != "Unknown" else (f"{quality}p" if quality.isdigit() else "أعلى جودة")
        full_title = f"{base_title} - {display_quality}"
        safe_name = f"{re.sub(r'[^\w\s\u0600-\u06FF-]', '', full_title).strip().replace(' ', '_')[:40]}.mp4"

        upload_and_send(out_file, safe_name, full_title, chat_id, message_id, target_servers, task_id)
        success = True

    except Exception as e:
        markup = None
        if os.path.exists(out_file):
            failed_uploads[task_id] = {'file': out_file, 'name': custom_name, 'servers': target_servers, 'quality': quality}
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton("♻️ إعادة رفع الفيديو", callback_data=f"retryup_{task_id}"))
        safe_edit(bot, chat_id, message_id, f"❌ *توقفت المهمة:*\n`{safe_error_text(e)}`", reply_markup=markup)
    finally:
        active_tasks.pop(task_id, None)
        if success and os.path.exists(out_file):
            try: os.remove(out_file)
            except: pass

def upload_and_send(file_path, safe_filename, full_title, chat_id, message_id, target_servers, task_id):
    prog_dict, res_dict, threads = {s: "⏳ في الانتظار..." for s in target_servers}, {s: None for s in target_servers}, []
    args_map = {
        "Abstream": (ABSTREAM_DOMAIN, bot_config["ABSTREAM_API_KEY"]), "Larhu": (LARHU_DOMAIN, bot_config["LARHU_API_KEY"]),
        "Uqload": (UQLOAD_DOMAIN, bot_config["UQLOAD_API_KEY"]), "Vidmoly": (VIDMOLY_DOMAIN, bot_config["VIDMOLY_API_KEY"]),
        "Vidara": (VIDARA_API_DOMAIN, bot_config["VIDARA_API_KEY"]), "Doodstream": (DOODSTREAM_DOMAIN, bot_config["DOODSTREAM_API_KEY"]),
        "1cloudfile": (ONECLOUD_DOMAIN, bot_config["ONECLOUD_API_KEY"])
    }

    for site in target_servers:
        if site.startswith("CloudflareR2"): t = threading.Thread(target=upload_to_r2, args=(file_path, safe_filename, full_title, task_id, prog_dict, res_dict, site))
        elif site == "GoFile": t = threading.Thread(target=upload_to_gofile, args=(file_path, safe_filename, task_id, prog_dict, res_dict))
        elif site == "VK": t = threading.Thread(target=upload_to_vk, args=(file_path, safe_filename, full_title, task_id, prog_dict, res_dict))
        else: t = threading.Thread(target=upload_to_xfs, args=(args_map[site][0], args_map[site][1], file_path, safe_filename, site, task_id, prog_dict, res_dict))
        threads.append(t); t.start(); time.sleep(2)

    last_upd = time.time()
    while any(t.is_alive() for t in threads):
        if active_tasks[task_id].get("cancel"): break
        if time.time() - last_upd > 3:
            txt = f"🚀 *المرحلة 2: الرفع [{full_title}]...*\n\n"
            for s in target_servers:
                display_name = s.replace('CloudflareR2_2', 'CloudflareR2 (2)').replace('CloudflareR2_3', 'CloudflareR2 (3)')
                icon = '☁️' if s.startswith('CloudflareR2') or s == '1cloudfile' else '🟢' if s == 'Abstream' else '🟠' if s == 'Larhu' else '🔵' if s == 'Uqload' else '🟣' if s == 'Vidmoly' else '🟡' if s == 'Vidara' else '🟤' if s == 'Doodstream' else '📘' if s == 'VK' else '🌐'
                if isinstance(prog_dict[s], float):
                    txt += f"{icon} *{display_name}:* `[{make_bar(prog_dict[s])}]` *{int(prog_dict[s])}%*\n"
                else:
                    txt += f"{icon} *{display_name}:* `{prog_dict[s]}`\n"
            safe_edit(bot, chat_id, message_id, txt.strip(), reply_markup=get_cancel_keyboard(task_id))
            last_upd = time.time()
        time.sleep(1)

    for t in threads: t.join()
    if active_tasks[task_id].get("cancel"): raise Exception("🛑 تم إلغاء العملية.")

    watch_links, download_links, failed_sites = generate_final_links(target_servers, res_dict)
    if not watch_links and not download_links: raise Exception("لم يتم العثور على أي روابط بعد الرفع.")

    res_txt = f"🎉 اكتملت المهمة بنجاح!\n🎬 {full_title}\n💡 _(اضغط على أي رابط لنسخه مباشرة)_\n\n"
    if watch_links: res_txt += "📺 روابط المشاهدة:\n━━━━━━━━━━━━━\n" + "\n".join(watch_links) + "\n\n"
    if download_links: res_txt += "📥 روابط التحميل المباشر:\n━━━━━━━━━━━━━\n" + "\n".join(download_links) + "\n\n"
    if failed_sites: res_txt += "⚠️ سيرفرات فشل الرفع عليها:\n━━━━━━━━━━━━━\n" + "\n".join(failed_sites)

    for attempt in range(3):
        try:
            bot.send_message(chat_id, res_txt.strip(), parse_mode=None, reply_to_message_id=message_id, disable_web_page_preview=True)
            break
        except Exception as e:
            if attempt == 2: raise Exception(f"سيرفر تليجرام لا يستجيب: {e}")
            time.sleep(3)

    if os.path.exists(file_path):
        try: os.remove(file_path)
        except: pass

def upload_only_logic(chat_id, message_id, task_id):
    if task_id not in failed_uploads: return
    data = failed_uploads[task_id]
    out_file, target_servers, custom_name, quality = data['file'], data['servers'], data['name'], data.get('quality', 'best')
    active_tasks[task_id] = {"cancel": False, "process": None}
    success = False
    actual_quality = get_video_quality(out_file)
    display_quality = actual_quality if actual_quality != "Unknown" else (f"{quality}p" if quality.isdigit() else "أعلى جودة")
    full_title = f"{custom_name or 'Video'} - {display_quality}"
    safe_name = f"{re.sub(r'[^\w\s\u0600-\u06FF-]', '', full_title).strip().replace(' ', '_')[:40]}.mp4"
    
    try:
        upload_and_send(out_file, safe_name, full_title, chat_id, message_id, target_servers, task_id)
        success = True
    except Exception as e:
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("♻️ محاولة الرفع مرة أخرى", callback_data=f"retryup_{task_id}"))
        safe_edit(bot, chat_id, message_id, f"❌ *توقفت إعادة الرفع:*\n`{safe_error_text(e)}`", reply_markup=markup)
    finally:
        active_tasks.pop(task_id, None)
        if success: failed_uploads.pop(task_id, None)

def merge_process_logic(links_list, chat_id, message_id, target_servers, custom_name, quality="best", watermark=False, logo_pos="none"):
    task_id = f"merge_{chat_id}_{message_id}_{int(time.time())}"
    active_tasks[task_id] = {"cancel": False, "process": None}
    concat_out_file = f"concat_{task_id}.mp4"
    merged_out_file = concat_out_file
    concat_txt_file = f"concat_{task_id}.txt"
    downloaded_parts, success = [], False

    try:
        for i, url in enumerate(links_list, 1):
            if active_tasks[task_id].get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
            part_filename = f"part_{task_id}_{i}.mp4"
            custom_msg = f"📥 *المرحلة 1: جاري تحميل المقطع ({i}/{len(links_list)})...*"
            ref, org = None, None
            if "4meplayer" in url or "player4me" in url: url = bypass_player4me(url); ref = "https://arabfleex.4meplayer.com/"
            elif "vidoba" in url: url = bypass_vidoba(url, bot, chat_id, message_id, task_id); ref = "https://vidoba.org/"
            elif "1cloudfile" in url: url = bypass_1cloudfile(url)
            elif "up4ever" in url or "/d/" in url: ref = "https://www.up-4ever.net/"
            elif "uqload" in url and (".mp4" in url or "/v/" in url): ref, org = "https://uqload.is/", "https://uqload.is"
            elif "uqload" in url: url, ref = bypass_uqload(url, bot, chat_id, message_id, task_id)
            elif "frdl.my" in url: url, ref = bypass_frdl(url, bot, chat_id, message_id, task_id); org = "https://frdl.my"
            url = apply_cf_proxy(url)
            download_manager(url, part_filename, bot, chat_id, message_id, task_id, referer=ref, origin=org, custom_msg=custom_msg, quality=quality)
            if not os.path.exists(part_filename) or os.path.getsize(part_filename) < 500000: raise Exception(f"❌ المقطع {i} تالف.")
            downloaded_parts.append(part_filename)

        if active_tasks[task_id].get("cancel"): raise Exception("🛑 تم إلغاء العملية.")
        safe_edit(bot, chat_id, message_id, "🧩 *المرحلة 2: جاري دمج المقاطع بسرعة فائقة...*", reply_markup=get_cancel_keyboard(task_id))
        
        with open(concat_txt_file, 'w', encoding='utf-8') as f:
            for part in downloaded_parts: f.write(f"file '{part}'\n")

        ffmpeg_cmd = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_txt_file, "-c", "copy", concat_out_file]
        process = subprocess.Popen(ffmpeg_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
        active_tasks[task_id]['process'] = process
        process.communicate()
        
        if process.returncode != 0 or not os.path.exists(concat_out_file): raise Exception("❌ فشل عملية الدمج. تأكد من تطابق الصيغ.")
        for part in downloaded_parts:
            try: os.remove(part)
            except: pass
        try: os.remove(concat_txt_file)
        except: pass
        
        # إضافة الحقوق والتمويه على الفيديو المدمج إذا كانت مفعلة
        if watermark:
            duration = get_video_duration(concat_out_file)
            custom_msg = f"🎬 *جاري طمس اللوجو القديم وطباعة الحقوق...*"
            safe_edit(bot, chat_id, message_id, custom_msg, reply_markup=get_cancel_keyboard(task_id))
            wm_file = f"wm_out_{task_id}.mp4"
            
            cmd = build_encode_cmd(concat_out_file, None, wm_file, add_watermark=True, logo_pos=logo_pos)
            retcode = run_ffmpeg_with_progress(cmd, duration, task_id, bot, chat_id, message_id, custom_msg)
            
            if retcode == 0 and os.path.exists(wm_file):
                try: os.remove(concat_out_file)
                except: pass
                merged_out_file = wm_file

        actual_quality = get_video_quality(merged_out_file)
        display_quality = actual_quality if actual_quality != "Unknown" else (f"{quality}p" if quality.isdigit() else "أعلى جودة")

        base_title = custom_name or "Merged_Video"
        full_title = f"{base_title} - {display_quality}"
        safe_name = f"{re.sub(r'[^\w\s\u0600-\u06FF-]', '', full_title).strip().replace(' ', '_')[:40]}.mp4"

        upload_and_send(merged_out_file, safe_name, full_title, chat_id, message_id, target_servers, task_id)
        success = True

    except Exception as e:
        markup = None
        if os.path.exists(merged_out_file):
            failed_uploads[task_id] = {'file': merged_out_file, 'name': custom_name, 'servers': target_servers, 'quality': quality}
            markup = InlineKeyboardMarkup().add(InlineKeyboardButton("♻️ إعادة رفع الفيديو", callback_data=f"retryup_{task_id}"))
        safe_edit(bot, chat_id, message_id, f"❌ *توقفت المهمة:*\n`{safe_error_text(e)}`", reply_markup=markup)
    finally:
        active_tasks.pop(task_id, None)
        if success and os.path.exists(merged_out_file):
            try: os.remove(merged_out_file)
            except: pass

try:
    download_font()  # أمر تحميل الخط قبل تشغيل البوت
    bot.remove_webhook()
    print(f"🤖 Bot Started - {VERSION}")
    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=30)
except Exception as e:
    print(f"❌ Error: {e}")
