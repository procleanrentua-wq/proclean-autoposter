#!/usr/bin/env python3
"""
PRO-CLEAN RENT — Smart Editorial AutoPoster v4.0 (Facebook Page + Instagram Business)
Локація: м. Дрогобич, Трускавець, Борислав, Стебник, Східниця
Сайт: https://proclean-drohobych.netlify.app | Тел.: 098 521 02 04
"""

import argparse
from datetime import datetime
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageEnhance, ImageFont

KYIV_TZ = ZoneInfo("Europe/Kyiv")
BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"
OUTPUT_CARD = IMAGES_DIR / "daily_smart_card.jpg"

CANVAS_W = 1080
CANVAS_H = 1350
SAFE_MARGIN_X = 80
MAX_TEXT_W = CANVAS_W - (SAFE_MARGIN_X * 2)  # 920 px (по 80 px відступу з країв)

TOPICS = [
    {
        "id": "coffee_lifehack",
        "prefix": "1_",
        "image": "1_coffee_sofa.jpg",
        "headline": "Розлили каву на світлий диван?",
        "subline": "Лайфхак першої хвилини, щоб не запекти пляму",
        "prompt_focus": (
            "Напиши живий експертний пост-лайфхак: що робити у перші 2 хвилини, якщо на світлий диван "
            "розлили каву (з молоком чи без). Поясни 3 правила: 1) не терти по колу, а щільно промокати сухими "
            "білими рушниками; 2) ніякого окропу й гарячого фена (білок молока і таніни запікаються у волокнах); "
            "3) не заливати Ванішем чи милом, бо залишиться липке темне коло. Потім м'яко поясни, що глибоку пляму "
            "з поролону витягує миючий пилосос-екстрактор (Kärcher Puzzi 8/1 — 600 грн/доба або Santoemma Sabrina — "
            "650 грн/доба) з ензимним преспреєм Chemspec PreKleen та ополіскувачем All Fiber."
        ),
        "fallback_text": (
            "Знайомий ранок, коли чашка свіжої кави раптом опиняється просто на світлому дивані? ☕🛋\n\n"
            "Головне у перші 60 секунд — не зробити помилку, яка зафіксує пляму у волокнах назавжди:\n"
            "1. Не тріть ганчіркою по колу — так ви лише заганяєте каву глибше й розширюєте ореол. Щільно притискайте сухі паперові рушники або білу мікрофібру.\n"
            "2. Ніякої гарячої води чи сушіння феном! Висока температура миттєво «запікає» білок молока та кавовий пігмент.\n"
            "3. Не заливайте диван побутовим милом чи Ванішем — піна залишиться у поролоні й після висихання дасть темний липкий контур.\n\n"
            "Якщо ж кава пішла вглиб оббивки або пляма давня — врятує вакуумна промивка. У Дрогобичі ви можете взяти в оренду професійний миючий пилосос Kärcher Puzzi 8/1 (600 грн/доба) або Santoemma Sabrina (650 грн/доба) зі стартовою порцією хімії у комплекті, а для складних плям додати ензимний преспрей Chemspec PreKleen (100 грн).\n\n"
            "📍 Дрогобич • Трускавець • Борислав • Стебник • Східниця\n"
            "📞 Бронювання: 098 521 02 04\n"
            "🌐 Онлайн-калькулятор: https://proclean-drohobych.netlify.app\n"
            "#дрогобич #трускавець #борислав #стебник #хімчисткадрогобич #орендадрогобич"
        ),
    },
    {
        "id": "mattress_urine_lifehack",
        "prefix": "2_",
        "image": "2_mattress_stain.jpg",
        "headline": "Пляма чи запах на матраці?",
        "subline": "Чому сода й оцет роблять лише гірше",
        "prompt_focus": (
            "Напиши тактовний, практичний пост-лайфхак для батьків маленьких дітей та власників котів і собак: "
            "як діяти, якщо на матраці з'явилася пляма сечі чи жовтий ореол. Поясни: 1) одразу витиснути вологу "
            "сухими рушниками натисканням; 2) чому не можна засипати мокру пляму содою з оцтом і гріти феном/праскою "
            "(кристалізація солей сечової кислоти + ризик темного ореолу від кокосової койри всередині матраца); "
            "3) як працює наш готовий хім-набір «Анти-Запах Тварин / Сеча» (250 грн: ензим Chemspec PreKleen + "
            "нейтралізатор Kill Odor Citrus + ополіскувач All Fiber) у парі з орендою пилососа та турбосушки Dri-Pod."
        ),
        "fallback_text": (
            "У кожному домі, де ростуть маленькі діти або живуть пухнасті улюбленці, матрац рано чи пізно проходить випробування 🐾🛏\n\n"
            "Що варто зробити у перші хвилини, щоб не залишилося жовтого контуру й запаху:\n"
            "• Максимально витягніть вологу сухими рушниками, сильно притискаючи їх до матраца без розтирання.\n"
            "• Не сипте соду з оцтом і не сушіть пляму феном чи праскою — нагрів перетворює сечову кислоту на стійкі кристали солей, які знову пахнуть у вологу погоду.\n"
            "• Не лийте багато води з губки: якщо в матраці є кокосова койра, зайва волога підтягне з неї темний коричневий ореол.\n\n"
            "Щоб прибрати і пляму, і запах без перемочування, у PRO-CLEAN RENT у Дрогобичі є готовий хім-набір «Анти-Запах Тварин / Сеча» (250 грн: ензим PreKleen + нейтралізатор Kill Odor Citrus + ополіскувач All Fiber) до оренди миючого пилососа (від 600 грн/доба), а турбосушка Dri-Pod висушить матрац за 2–3 години.\n\n"
            "📍 м. Дрогобич (самовивіз або доставка під двері)\n"
            "📞 098 521 02 04 | 🌐 https://proclean-drohobych.netlify.app\n"
            "#дрогобич #трускавець #борислав #чисткаматраців #прокаттехніки"
        ),
    },
    {
        "id": "extractors_flagship",
        "prefix": "3_",
        "image": "3_puzzi_sabrina.jpg",
        "headline": "Хімчистка дивана власноруч за 600 грн",
        "subline": "Kärcher Puzzi 8/1 та Santoemma Sabrina у Дрогобичі",
        "prompt_focus": (
            "Напиши переконливий пост про вигоду подобової оренди професійних миючих пилососів у Дрогобичі: "
            "німецький Kärcher Puzzi 8/1 (600 грн/доба) та італійський Santoemma Sabrina SW15 (650 грн/доба зі штангою "
            "для прання килимів стоячи). Наголоси, що стартова порція порошку Kärcher RM 760 (80 г на 8 л) входить "
            "безкоштовно, а за одну добу можна оновити всі дивани, матраци й килими вдома."
        ),
        "fallback_text": (
            "За одну добу оренди можна спокійно перемити всі дивани, матраци, крісла й килими вдома — за ціною виклику майстра лише на одне крісло ✨\n\n"
            "У нашому сервісі в Дрогобичі доступні обидва світові лідери екстракторної чистки:\n"
            "• Kärcher Puzzi 8/1 (Німеччина) — 600 грн/доба: компактний, легкий і дуже зручний для диванів та салону авто.\n"
            "• Santoemma Sabrina SW15 (Італія) — 650 грн/доба: підвищена сила вакууму та висока штанга для глибокого прання килимів стоячи.\n\n"
            "Стартова порція гіпоалергенного порошку Kärcher RM 760 (80 г на 8 л води) та детальна інструкція вже у комплекті!\n\n"
            "📍 Дрогобич • Трускавець • Борислав • Стебник • Східниця\n"
            "📞 098 521 02 04 | 🌐 https://proclean-drohobych.netlify.app\n"
            "#дрогобич #трускавець #борислав #karcherpuzzi #santoemmasabrina #хімчисткамеблів"
        ),
    },
    {
        "id": "steam_sc2",
        "prefix": "4_",
        "image": "4_steam_sc2.jpg",
        "headline": "Кухня, плитка і шви без краплі хімії",
        "subline": "Оренда пароочисника Kärcher SC 2 — 400 грн/доба",
        "prompt_focus": (
            "Напиши практичний пост про оренду пароочисника Kärcher SC 2 EasyFix у Дрогобичі (400 грн/доба окремо або "
            "у КОМБО з пилососом чи роботом вікон). Розкажи, як гаряча пара без хімії вимиває міжплиткові шви, пори "
            "ламінату, жир на кухонному фартусі, витяжці, духовці, кранах і душовій кабіні."
        ),
        "fallback_text": (
            "Темні міжплиткові шви у ванній, жир на витяжці чи в'ївшийся бруд у текстурі ламінату, який не бере швабра? 💨\n\n"
            "Замість агресивної побутової хімії візьміть на добу німецький пароочисник Kärcher SC 2 EasyFix із повним набором насадок. Струмінь чистої гарячої пари під тиском розчиняє застарілий жир, наліт навколо змішувачів, бруд у віконних рамах і знищує 99,9% бактерій — ідеально для сімей із дітьми та алергіків.\n\n"
            "Вартість оренди у Дрогобичі — всього 400 грн/доба (замість купівлі за 9 100 грн!), а в парі з миючим пилососом або роботом для вікон діє вигідна знижка КОМБО.\n\n"
            "📞 098 521 02 04 | 🌐 https://proclean-drohobych.netlify.app\n"
            "#дрогобич #трускавець #борислав #пароочисник #генеральнеприбирання"
        ),
    },
    {
        "id": "window_hobot",
        "prefix": "5_",
        "image": "5_window_hobot.jpg",
        "headline": "Чисті панорамні вікна без ризику",
        "subline": "Робот для миття вікон Hobot — 450 грн/доба",
        "prompt_focus": (
            "Напиши корисний пост про оренду робота для миття вікон Hobot у Дрогобичі та Трускавці (450 грн/доба, "
            "засіб для скла й чисті серветки з мікрофібри в комплекті). Акцентуй на безпеці на високих поверхах, "
            "глухих стулках балконів, панорамних вікнах і великих дзеркалах шаф-купе."
        ),
        "fallback_text": (
            "Мити глухі стулки балкона чи панорамні вікна на високому поверсі вручну — завжди ризик і години на холодному вітрі 🪟✨\n\n"
            "Робот-мийник Hobot зробить це за вас безпечно й без розводів: потужний вакуум міцно тримає його на склі, страхувальний трос гарантує спокій, а змінні серветки з мікрофібри натирають вікна, лоджії та дзеркала шаф-купе до кришталевого блиску.\n\n"
            "Оренда у Дрогобичі — 450 грн/доба (професійний засіб для скла вже у комплекті!).\n\n"
            "📍 Дрогобич • Трускавець • Борислав • Стебник\n"
            "📞 098 521 02 04 | 🌐 https://proclean-drohobych.netlify.app\n"
            "#дрогобич #трускавець #чистівікна #роботдлявікон #орендадрогобич"
        ),
    },
    {
        "id": "dryer_dripod",
        "prefix": "6_",
        "image": "6_dryer_dripod.jpg",
        "headline": "Помили диван вранці — сухий за 2 години",
        "subline": "Турбосушка Dri-Eaz Dri-Pod — 350 грн/доба",
        "prompt_focus": (
            "Напиши переконливий пост про вирішення головної проблеми осінньо-зимової хімчистки — довгого висихання меблів. "
            "Поясни, як американська купольна турбосушка Dri-Eaz Dri-Pod скорочує час сушіння дивана чи матраца з 12–15 годин "
            "до 2–3 годин без затхлості (окремо 350 грн/доба, а у КОМБО №1 з пилососом — лише +250 грн!)."
        ),
        "fallback_text": (
            "Боїтеся чистити диван або дитячий матрац у прохолодну пору, бо він сохнутиме до наступного дня? 🌬🛋\n\n"
            "Американська купольна турбосушка Dri-Eaz Dri-Pod вирішує це питання за 2–3 години: спрямований потік повітря на 360° швидко видуває вологу з наповнювача, тож уже ввечері родина спокійно відпочиває на сухих і свіжих меблях.\n\n"
            "Окремо оренда сушки коштує 350 грн/доба, а в нашому хітовому КОМБО №1 разом із миючим пилососом та порцією хімії — лише +250 грн (850–900 грн за весь комплект!).\n\n"
            "📞 Бронювання у Дрогобичі: 098 521 02 04\n"
            "🌐 https://proclean-drohobych.netlify.app\n"
            "#дрогобич #трускавець #борислав #сушкамеблів #хімчисткадиванів"
        ),
    },
    {
        "id": "car_detailing_kwazar",
        "prefix": "7_",
        "image": "7_car_kwazar.jpg",
        "headline": "Хімчистка салону авто власноруч",
        "subline": "Миючий пилосос + піногенератор Kwazar + Pol Star",
        "prompt_focus": (
            "Напиши практичний пост для водіїв Дрогобича, Борислава і Трускавця: як самостійно зробити професійний "
            "детейлінг сидінь, підлоги й багажника авто у власному гаражі чи на подвір'ї. Опиши набір «Делікат / Авто + "
            "Піна Kwazar» (220 грн: німецький концентрат Koch Chemie Pol Star pH 7 + піногасник + помповий піногенератор "
            "Kwazar 2 л на добу) разом із Puzzi 8/1 (600 грн) та озонатором повітря YATO проти запаху тютюну й вогкості."
        ),
        "fallback_text": (
            "Освіжити сидіння, карти дверей, підлогу й багажник власного авто на професійному обладнанні можна за одні вихідні — у 4 рази дешевше за автостудію 🚗✨\n\n"
            "До миючого пилососа Kärcher Puzzi 8/1 (600 грн/доба) у нас є спеціальний авто-сет «Делікат / Авто + Піна Kwazar» (220 грн): нейтральний німецький засіб Koch Chemie Pol Star (pH 7 для тканини, велюру та алькантари), піногасник і ручний піногенератор Kwazar 2 л, який дає щільну піну без перезволоження поролону сидінь.\n\n"
            "А якщо в салоні відчувається запах тютюну чи вологи з пічки — візьміть додатково промисловий озонатор YATO для повної стерилізації повітря за 30 хвилин.\n\n"
            "📍 м. Дрогобич • Тел./Viber: 098 521 02 04\n"
            "🌐 Калькулятор оренди: https://proclean-drohobych.netlify.app\n"
            "#дрогобич #борислав #трускавець #хімчисткаавто #детейлінг"
        ),
    },
]


def get_env_any(*names: str, default: str = "") -> str:
    for n in names:
        val = os.environ.get(n, "").strip()
        if val:
            return val
    return default


def fetch_drohobych_weather() -> str:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=49.35&longitude=23.50"
        "&current=temperature_2m,weather_code"
        "&timezone=Europe%2FKyiv"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ProCleanAutoPoster/4.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        cur = data.get("current", {})
        temp = round(cur.get("temperature_2m", 5))
        wcode = cur.get("weather_code", 0)
        if wcode == 0:
            desc = "сонячно"
        elif wcode in (1, 2, 3):
            desc = "хмарно з проясненнями"
        elif wcode in (45, 48):
            desc = "туманно"
        elif wcode in (51, 53, 55, 61, 63, 65, 80, 81, 82):
            desc = "дощить і сиро"
        elif wcode in (71, 73, 75, 77, 85, 86):
            desc = "сніжно й морозно"
        else:
            desc = "прохолодно"
        return f"{temp:+d}°C ({desc})"
    except Exception:
        return "свіжа погода"


def choose_topic(now_kyiv: datetime, cli_topic: str | None = None) -> tuple[int, dict]:
    forced = (cli_topic or os.environ.get("FORCE_TOPIC_INDEX", "")).strip()
    if forced.lstrip("-").isdigit():
        val = int(forced)
        # Якщо передано 1..7 або 0..6 — коректно приводимо до індексу
        idx = (val - 1) % len(TOPICS) if val >= 1 else val % len(TOPICS)
        return idx, TOPICS[idx]
    day_ordinal = now_kyiv.toordinal()
    slot = 0 if now_kyiv.hour < 14 else 1
    idx = (day_ordinal * 2 + slot) % len(TOPICS)
    return idx, TOPICS[idx]


def ensure_cyrillic_fonts() -> tuple[str, str]:
    """Забезпечує сучасний кириличний шрифт Montserrat / Inter (або надійний системний резерв)."""
    cache_dir = Path("/tmp/proclean_fonts")
    cache_dir.mkdir(parents=True, exist_ok=True)
    bold_dl = cache_dir / "Montserrat-Bold.ttf"
    med_dl = cache_dir / "Montserrat-Medium.ttf"

    urls = [
        (bold_dl, "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Bold.ttf"),
        (med_dl, "https://raw.githubusercontent.com/JulietaUla/Montserrat/master/fonts/ttf/Montserrat-Medium.ttf"),
    ]
    for dst, url in urls:
        if not dst.exists() or dst.stat().st_size < 20000:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "ProCleanAutoPoster/4.0"})
                with urllib.request.urlopen(req, timeout=10) as r:
                    data = r.read()
                if len(data) > 20000:
                    dst.write_bytes(data)
            except Exception:
                pass

    if bold_dl.exists() and med_dl.exists():
        return str(bold_dl), str(med_dl)

    bold_candidates = [
        str(BASE_DIR / "fonts" / "Inter-Bold.ttf"),
        "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    reg_candidates = [
        str(BASE_DIR / "fonts" / "Inter-Medium.ttf"),
        "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    b_font = next((p for p in bold_candidates if os.path.exists(p)), "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    r_font = next((p for p in reg_candidates if os.path.exists(p)), b_font)
    return b_font, r_font


def wrap_and_fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_path: str,
    start_size: int,
    min_size: int,
    max_width: int,
    max_lines: int = 2,
) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    """Гарантує, що жодна літера ніколи не вийде за межі безпечної зони max_width."""
    words = text.strip().split()
    for sz in range(start_size, min_size - 1, -2):
        font = ImageFont.truetype(font_path, sz)
        lines: list[str] = []
        cur = ""
        for w in words:
            cand = f"{cur} {w}".strip()
            bbox = draw.textbbox((0, 0), cand, font=font)
            if (bbox[2] - bbox[0]) <= max_width:
                cur = cand
            else:
                if cur:
                    lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)

        fits_width = all((draw.textbbox((0, 0), ln, font=font)[2] - draw.textbbox((0, 0), ln, font=font)[0]) <= max_width for ln in lines)
        if fits_width and len(lines) <= max_lines:
            return font, lines

    font = ImageFont.truetype(font_path, min_size)
    return font, [text]


def resolve_topic_image(topic: dict):
    from pathlib import Path

    images_dir = Path(IMAGES_DIR)
    valid_exts = {".jpg", ".jpeg", ".jfif", ".png", ".webp"}
    skip_prefixes = ("daily_smart_card", "generated_")

    all_files = sorted(
        p for p in images_dir.iterdir()
        if p.is_file()
        and p.suffix.lower() in valid_exts
        and not p.name.lower().startswith(skip_prefixes)
    )
    if not all_files:
        raise FileNotFoundError(f"У папці {IMAGES_DIR} немає вхідних зображень!")

    candidates = []
    for val in topic.values():
        if isinstance(val, str) and val.lower().endswith(tuple(valid_exts)):
            candidates.append(val.strip())
        elif isinstance(val, (list, tuple)):
            for item in val:
                if isinstance(item, str) and item.lower().endswith(tuple(valid_exts)):
                    candidates.append(item.strip())

    for cand in candidates:
        cand_stem = Path(cand).name.lower().split(".")[0]
        for p in all_files:
            if p.name.lower().split(".")[0] == cand_stem:
                return p

    return all_files[0]


def render_editorial_card(topic: dict) -> Path:
    """Формує повноекранну журнальну картку 1080x1350 (4:5) без рамок і з кришталевою різкістю."""
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    src_path = resolve_topic_image(topic)
    print(f"Фото-основа: {src_path.name}")

    im = Image.open(src_path).convert("RGB")
    scale = max(CANVAS_W / im.width, CANVAS_H / im.height)
    nw, nh = int(round(im.width * scale)), int(round(im.height * scale))
    im_resized = im.resize((nw, nh), Image.Resampling.LANCZOS)
    x0 = (nw - CANVAS_W) // 2
    y0 = (nh - CANVAS_H) // 2
    base = im_resized.crop((x0, y0, x0 + CANVAS_W, y0 + CANVAS_H))

    base = ImageEnhance.Contrast(base).enhance(1.03)
    base = ImageEnhance.Sharpness(base).enhance(1.08)
    rgba = base.convert("RGBA")

    # М'який напівпрозорий градієнт лише у верхній та нижній кромках під текст
    grad = Image.new("RGBA", (CANVAS_W, CANVAS_H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(grad)

    top_h = 345
    for y in range(top_h):
        ratio = 1.0 - (y / top_h)
        alpha = int(170 * (ratio ** 1.45))
        g_draw.line([(0, y), (CANVAS_W, y)], fill=(10, 16, 28, alpha))

    bot_start = 1175
    bot_h = CANVAS_H - bot_start
    for i in range(bot_h):
        y = bot_start + i
        ratio = i / max(1, bot_h - 1)
        alpha = int(180 * (ratio ** 1.35))
        g_draw.line([(0, y), (CANVAS_W, y)], fill=(10, 16, 28, alpha))

    composed = Image.alpha_composite(rgba, grad)
    draw = ImageDraw.Draw(composed)
    bold_font_path, reg_font_path = ensure_cyrillic_fonts()

    # 1. Верхній бренд-підпис
    f_over, over_lines = wrap_and_fit_text(
        draw, "PRO-CLEAN RENT  •  ОРЕНДА У ДРОГОБИЧІ", bold_font_path, start_size=24, min_size=18, max_width=MAX_TEXT_W, max_lines=1
    )
    over_txt = over_lines[0]
    ob = draw.textbbox((0, 0), over_txt, font=f_over)
    ox = (CANVAS_W - (ob[2] - ob[0])) // 2
    draw.text((ox + 1, 51), over_txt, font=f_over, fill=(0, 0, 0, 150))
    draw.text((ox, 50), over_txt, font=f_over, fill=(250, 214, 105, 255))

    # 2. Журнальний заголовок (1–2 рядки, авто-контроль ширини)
    f_head, head_lines = wrap_and_fit_text(
        draw, topic["headline"], bold_font_path, start_size=50, min_size=30, max_width=MAX_TEXT_W, max_lines=2
    )
    cur_y = 94
    for ln in head_lines:
        lb = draw.textbbox((0, 0), ln, font=f_head)
        lw = lb[2] - lb[0]
        lh = lb[3] - lb[1]
        lx = (CANVAS_W - lw) // 2
        draw.text((lx + 2, cur_y + 3), ln, font=f_head, fill=(0, 0, 0, 170))
        draw.text((lx, cur_y), ln, font=f_head, fill=(255, 255, 255, 255))
        cur_y += lh + 14

    # 3. Короткий підзаголовок
    f_sub, sub_lines = wrap_and_fit_text(
        draw, topic["subline"], reg_font_path, start_size=27, min_size=19, max_width=MAX_TEXT_W, max_lines=2
    )
    cur_y += 4
    for sln in sub_lines:
        sb = draw.textbbox((0, 0), sln, font=f_sub)
        sw = sb[2] - sb[0]
        sh = sb[3] - sb[1]
        sx = (CANVAS_W - sw) // 2
        draw.text((sx + 1, cur_y + 2), sln, font=f_sub, fill=(0, 0, 0, 155))
        draw.text((sx, cur_y), sln, font=f_sub, fill=(226, 232, 240, 255))
        cur_y += sh + 8

    # 4. Охайний контакт унизу без рамок
    footer_str = "098 521 02 04  •  proclean-drohobych.netlify.app"
    f_foot, foot_lines = wrap_and_fit_text(
        draw, footer_str, bold_font_path, start_size=27, min_size=19, max_width=MAX_TEXT_W, max_lines=1
    )
    ftxt = foot_lines[0]
    fb = draw.textbbox((0, 0), ftxt, font=f_foot)
    fx = (CANVAS_W - (fb[2] - fb[0])) // 2
    fy = CANVAS_H - 66
    draw.text((fx + 2, fy + 2), ftxt, font=f_foot, fill=(0, 0, 0, 180))
    draw.text((fx, fy), ftxt, font=f_foot, fill=(255, 255, 255, 255))

    final_rgb = composed.convert("RGB")
    final_rgb.save(str(OUTPUT_CARD), format="JPEG", quality=95, subsampling=0, optimize=True)
    print(f"Збережено HD-картку 1080x1350: {OUTPUT_CARD} ({OUTPUT_CARD.stat().st_size // 1024} KB)")
    return OUTPUT_CARD


def generate_caption_with_gemini(api_key: str, topic: dict, weather_str: str, now_kyiv: datetime) -> str:
    if not api_key:
        return topic["fallback_text"]

    models_to_try = ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.0-flash"]
    try:
        list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
        with urllib.request.urlopen(list_url, timeout=15) as resp:
            mdata = json.loads(resp.read().decode("utf-8"))
        discovered = [
            m["name"].replace("models/", "")
            for m in mdata.get("models", [])
            if "generateContent" in m.get("supportedGenerationMethods", [])
            and "flash" in m.get("name", "").lower()
            and "tts" not in m.get("name", "").lower()
            and "image" not in m.get("name", "").lower()
        ]
        ordered = [m for m in models_to_try if m in discovered] + [m for m in discovered if m not in models_to_try]
        if ordered:
            models_to_try = ordered
    except Exception as e:
        print(f"Використовуємо базовий перелік моделей ({e})")

    part_of_day = "ранок" if now_kyiv.hour < 14 else "вечір"
    prompt = (
        "Ти — власник сервісу оренди професійної техніки для прибирання та хімчистки PRO-CLEAN RENT у м. Дрогобич "
        "(працюємо: Дрогобич, Трускавець, Борислав, Стебник, Східниця). "
        "Пиши українською мовою природно, живо, доброзичливо й експертно.\n\n"
        "СУВОРІ ПРАВИЛА:\n"
        "1. НЕ починай пост із шаблонних зведень погоди чи дати ('Дрогобич зараз: +3°C...'). Починай одразу з живого життєвого питання або болю клієнта.\n"
        f"2. Частина доби зараз — {part_of_day}, погода в Дрогобичі — {weather_str} (згадай погоду ненав'язливо ЛИШЕ якщо це доречно за темою).\n"
        f"3. Тема публікації: {topic['prompt_focus']}\n"
        "4. Точні тарифи сервісу: Kärcher Puzzi 8/1 — 600 грн/доба, Santoemma Sabrina SW15 — 650 грн/доба (порція 80 г RM 760 у комплекті), "
        "Пароочисник Kärcher SC 2 — 400 грн/доба, Робот для вікон Hobot — 450 грн/доба, Турбосушка Dri-Eaz Dri-Pod — 350 грн/доба "
        "(+250 грн у комбо з пилососом), Озонатор YATO — 350 грн/доба, Піногенератор Kwazar 2 л — +100 грн до пилососа; "
        "готові хім-набори Chemspec/Koch Chemie — від 110 до 340 грн.\n"
        "5. У кінці вкажи телефон 098 521 02 04, сайт https://proclean-drohobych.netlify.app та 5–7 локальних хештегів (#дрогобич #трускавець #борислав тощо).\n"
        "6. Обсяг 850–1300 символів, короткі абзаци з відступами, без води й без капслоку, максимум 5 емодзі."
    )

    payload = json.dumps({
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"temperature": 0.75, "maxOutputTokens": 900},
    }).encode("utf-8")

    for model_name in models_to_try:
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        req = urllib.request.Request(endpoint, data=payload, headers={"Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                res = json.loads(resp.read().decode("utf-8"))
            text = res.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "").strip()
            if len(text) > 180:
                print(f"Унікальний текст згенеровано через {model_name}!")
                return text
        except urllib.error.HTTPError as he:
            print(f"Модель {model_name} повернула HTTP {he.code}, пробуємо наступну...")
        except Exception as ex:
            print(f"Помилка {model_name}: {ex}")

    return topic["fallback_text"]


def git_commit_and_push_card(card_path: Path) -> str:
    repo = get_env_any("GITHUB_REPOSITORY", default="procleanrentua-wq/proclean-autoposter")
    branch = get_env_any("GITHUB_REF_NAME", default="main")
    rel_card = card_path.relative_to(BASE_DIR).as_posix()

    try:
        subprocess.run(["git", "config", "user.name", "PRO-CLEAN AutoPoster"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "config", "user.email", "actions@github.com"], cwd=BASE_DIR, check=False)
        subprocess.run(["git", "add", rel_card], cwd=BASE_DIR, check=True)
        diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=BASE_DIR)
        if diff.returncode != 0:
            subprocess.run(["git", "commit", "-m", f"Update daily smart card: {rel_card}"], cwd=BASE_DIR, check=True)
            subprocess.run(["git", "pull", "--rebase", "origin", branch], cwd=BASE_DIR, check=False)
            subprocess.run(["git", "push", "origin", f"HEAD:{branch}"], cwd=BASE_DIR, check=True)
            time.sleep(3)
    except Exception as e:
        print(f"Примітка git push: {e}")

    return f"https://raw.githubusercontent.com/{repo}/{branch}/{rel_card}?v={int(time.time())}"


def publish_to_facebook_page(page_id: str, token: str, card_path: Path, caption: str) -> dict:
    boundary = f"----ProCleanBoundary{uuid.uuid4().hex}"
    body = io.BytesIO()

    def write_field(name: str, value: str):
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode("utf-8"))
        body.write(f"{value}\r\n".encode("utf-8"))

    write_field("caption", caption)
    write_field("published", "true")
    write_field("access_token", token)

    body.write(f"--{boundary}\r\n".encode("utf-8"))
    body.write(b'Content-Disposition: form-data; name="source"; filename="daily_smart_card.jpg"\r\n')
    body.write(b"Content-Type: image/jpeg\r\n\r\n")
    body.write(card_path.read_bytes())
    body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    fb_url = f"https://graph.facebook.com/v21.0/{page_id}/photos"
    req = urllib.request.Request(
        fb_url,
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=40) as resp:
        return json.loads(resp.read().decode("utf-8"))


def discover_ig_user_id(page_id: str, token: str) -> str:
    url = f"https://graph.facebook.com/v21.0/{page_id}?fields=instagram_business_account&access_token={urllib.parse.quote(token)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("instagram_business_account", {}).get("id", "")
    except Exception:
        return ""


def publish_to_instagram(ig_user_id: str, token: str, image_url: str, caption: str) -> dict | None:
    if not ig_user_id:
        print("Instagram акаунт не прив'язаний або IG_USER_ID не задано — пропускаємо IG.")
        return None

    create_url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media"
    ig_caption = caption.replace(
        "https://proclean-drohobych.netlify.app",
        "proclean-drohobych.netlify.app (посилання в шапці профілю)",
    )
    params = urllib.parse.urlencode({
        "image_url": image_url,
        "caption": ig_caption,
        "access_token": token,
    }).encode("utf-8")

    req = urllib.request.Request(create_url, data=params, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        creation = json.loads(resp.read().decode("utf-8"))
    creation_id = creation.get("id")
    if not creation_id:
        raise RuntimeError(f"Instagram не повернув creation_id: {creation}")

    status_url = f"https://graph.facebook.com/v21.0/{creation_id}?fields=status_code&access_token={urllib.parse.quote(token)}"
    for _ in range(10):
        time.sleep(3)
        try:
            with urllib.request.urlopen(status_url, timeout=15) as sresp:
                sdata = json.loads(sresp.read().decode("utf-8"))
            if sdata.get("status_code") == "FINISHED":
                break
        except Exception:
            pass

    pub_url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media_publish"
    pub_params = urllib.parse.urlencode({
        "creation_id": creation_id,
        "access_token": token,
    }).encode("utf-8")
    preq = urllib.request.Request(pub_url, data=pub_params, method="POST")
    with urllib.request.urlopen(preq, timeout=30) as presp:
        return json.loads(presp.read().decode("utf-8"))


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--topic", "-t", default=None)
    parser.add_argument("pos_topic", nargs="?", default=None)
    args, _ = parser.parse_known_args()

    now_kyiv = datetime.now(KYIV_TZ)
    topic_idx, topic = choose_topic(now_kyiv, args.topic or args.pos_topic)
    weather_str = fetch_drohobych_weather()

    print(f"=== Рубрика #{topic_idx + 1}: {topic['headline']} ({now_kyiv.strftime('%Y-%m-%d %H:%M')} Kyiv) ===")

    card_path = render_editorial_card(topic)
    public_img_url = git_commit_and_push_card(card_path)

    gemini_key = get_env_any("GEMINI_API_KEY", "GOOGLE_API_KEY", "GEMINI_KEY")
    caption = generate_caption_with_gemini(gemini_key, topic, weather_str, now_kyiv)
    print("\n--- ЗГЕНЕРОВАНИЙ ЖИВИЙ ТЕКСТ ПОСТА ---\n")
    print(caption)
    print("\n--------------------------------------\n")

    meta_token = get_env_any("META_ACCESS_TOKEN", "FB_PAGE_ACCESS_TOKEN", "FB_ACCESS_TOKEN", "FACEBOOK_ACCESS_TOKEN", "PAGE_ACCESS_TOKEN")
    fb_page_id = get_env_any("FB_PAGE_ID", "FACEBOOK_PAGE_ID", "META_PAGE_ID", "PAGE_ID")
    ig_user_id = get_env_any("IG_USER_ID", "IG_ACCOUNT_ID", "IG_BUSINESS_ID", "INSTAGRAM_USER_ID", "INSTAGRAM_BUSINESS_ACCOUNT_ID")

    if not meta_token or not fb_page_id:
        raise RuntimeError("Не знайдено секретів META_ACCESS_TOKEN або FB_PAGE_ID у GitHub Secrets!")

    fb_res = publish_to_facebook_page(fb_page_id, meta_token, card_path, caption)
    print(f"✅ Опубліковано на Facebook Page: {fb_res}")

    if not ig_user_id:
        ig_user_id = discover_ig_user_id(fb_page_id, meta_token)

    try:
        ig_res = publish_to_instagram(ig_user_id, meta_token, public_img_url, caption)
        if ig_res:
            print(f"✅ Опубліковано в Instagram: {ig_res}")
    except urllib.error.HTTPError as he:
        print(f"⚠️ Примітка Instagram ({he.code}): {he.read().decode('utf-8', errors='ignore')}")
    except Exception as e:
        print(f"⚠️ Примітка Instagram: {e}")


if __name__ == "__main__":
    main()
