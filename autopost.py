#!/usr/bin/env python3
"""
PRO-CLEAN RENT v4.1 — Editorial 4:5 HD AutoPoster (1080x1350) + Live Weather, Holiday Countdown & Stain Lifehacks.
Повністю сумісний з існуючим .github/workflows/main.yml:
- Підтримує секрети META_PAGE_ACCESS_TOKEN (та резервно META_ACCESS_TOKEN), FB_PAGE_ID, IG_USER_ID, GEMINI_API_KEY.
- Автоматично розпізнає фото у папці images/ з розширеннями .jpg, .jpeg, .jfif, .jpg.jfif, .png, .webp.
- Повноекранний журнальний формат 1080x1350 (4:5) без білих рамок і колажів, з автопідбором шрифту в межах безпечної зони (0% обрізання тексту) та збереженням JPEG 4:4:4 (quality=95, subsampling=0).
- Актуальний Meta Graph API v27.0 + динамічний вибір робочої моделі Gemini API.
"""

import datetime
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

from PIL import Image, ImageDraw, ImageFont, ImageOps

GRAPH_API_VERSION = "v27.0"
BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR / "images"
OUTPUT_REL_PATH = "images/daily_smart_card.jpg"
OUTPUT_CARD_PATH = BASE_DIR / OUTPUT_REL_PATH

CARD_W = 1080
CARD_H = 1350
SAFE_PAD_X = 68
MAX_TEXT_W = CARD_W - SAFE_PAD_X * 2  # 944 px безпечної ширини

BUSINESS_CONTEXT = """
Ти — досвідчений локальний майстер хімчистки та автор блогу сервісу PRO-CLEAN RENT у м. Дрогобич (ФОП Собко Андрій).
Географія: Дрогобич, Трускавець, Борислав, Стебник, Східниця.
Контакти: Тел / Viber / Telegram / WhatsApp: 098 521 02 04.
Сайт з онлайн-калькулятором: https://proclean-drohobych.netlify.app

Наші послуги та точні ціни:
1) Подобова оренда професійної техніки для самостійної хімчистки (1 порція 80 г хімії Kärcher RM 760 у ПОДАРУНОК до кожного миючого пилососа!):
   - Миючий пилосос-екстрактор Kärcher Puzzi 8/1 (Німеччина) — 600 грн/доба
   - Потужний італійський екстрактор Santoemma Sabrina SW15 (глибока витяжка з товстих матраців і килимів) — 650 грн/доба
   - Пароочисник Kärcher SC 2 EasyFix Plus (кухня, жир, духовка, плитка, шви, санвузол без хімії) — 400 грн/доба
   - Робот для миття вікон Hobot (спиртовий концентрат RM 503 та серветки у комплекті) — 450 грн/доба
   - Американська турбосушка Dri-Eaz Dri-Pod (сушить диван чи матрац за 2–3 години замість 24 годин у сиру погоду!) — 350 грн/доба (+250 грн у комбо з пилососом)
   - Професійний озонатор повітря YATO YT-73350 (знищує запахи диму, тварин, сечі, плісняви, вогкості) — 350 грн/доба
   - Піногенератор 2 л Kwazar Venus Super Foamer Pro+ (густа активна піна для авто та делікатних диванів) — +100 грн/доба до пилососа (150 грн окремо)
   - Професійна порційна хімія: Kärcher RM 760 (90 грн), кислотний ополіскувач Chemspec All Fiber Textile Rinse (90 грн), ензимний преспрей Chemspec PreKleen проти білка й сечі (100 грн), нейтралізатор запахів Chemspec Kill Odor Citrus (100 грн), делікатний Koch Chemie Pol Star pH 7 (130 грн), плямовивідник Kärcher RM 769 (100 грн), піногасник RM 761 (70 грн).
   - Готові набори хімії: «Дитячий / Гіпоалергенний» (110 грн), «Анти-Запах Тварин / Сеча» (250 грн), «Делікат / Авто + Піна Kwazar» (220 грн), «Анти-Пляма MAX» (340 грн).
   - Вигідні КОМБО на добу:
     * КОМБО №1 «Сухий диван за 2 години» (Пилосос + Турбосушка + хімія) = 850 грн (з Puzzi) / 900 грн (з Sabrina)
     * КОМБО №2 «Меблі + Кухня та Ванна» (Пилосос + Пароочисник SC 2 + хімія) = 850 грн / 900 грн
     * КОМБО №3 «Анти-Запах» (Пилосос + Озонатор YATO + хімія) = 850 грн / 900 грн
     * КОМБО №4 «Ідеальні вікна та шви» (Робот Hobot + Пароочисник SC 2) = 750 грн
     * КОМБО №5 «Генеральне прибирання All-in-One» (Екстрактор + Пароочисник + Hobot + Турбосушка) = 1450 грн / 1500 грн
   - Доставка в 1 сторону: Самовивіз (Дрогобич) — 0 грн; по Дрогобичу — 150 грн; Трускавець / Стебник — 200 грн; Борислав — 250 грн; Східниця — 350 грн.

2) Виїзна 5-ступенева хімчистка м'яких меблів, матраців, килимів і салонів авто нашим майстром (ензими Chemspec США + обов'язкове кислотне ополіскування All Fiber Rinse, 100% безпечно для немовлят та алергіків).
"""

TOPICS = [
    {
        "id": 1,
        "image": "1_coffee_sofa.jpg",
        "badge": "ЛАЙФХАК ПРОТИ ПЛЯМ",
        "headline": "Розлили каву на світлий диван? Не тріть губкою!",
        "tip": "1. Промокніть паперовим рушником без тертя  •  2. Без окропу й «Ванішу»  •  3. Витягніть із поролону екстрактором",
        "price_line": "Оренда Kärcher Puzzi 8/1 + хімія: 600 грн/доба",
        "topic_prompt": (
            "Рубрика «Лайфхаки з виведення плям»: свіжа або підсохла пляма від кави з молоком, чаю чи вина на світлому дивані. "
            "Дай чіткі 3 правила першої допомоги: 1) чому не можна терти губкою по колу (кава з молоком і цукром йде глибше в поролон); "
            "2) чому не можна лити окріп (білок молока запікається у волокнах) та побутовий «Ваніш» (залишає липкий ореол); "
            "3) як екстрактор Kärcher Puzzi 8/1 (600 грн/доба з порцією RM 760 у комплекті) або Santoemma Sabrina SW15 (650 грн/доба) витягує пляму з глибини поролону разом із промивкою ополіскувачем Chemspec All Fiber Rinse."
        ),
    },
    {
        "id": 2,
        "image": "2_mattress_stain.jpg",
        "badge": "ЕНЗИМНА ЧИСТКА МАТРАЦІВ",
        "headline": "Жовті ореоли чи дитячі й котячі несподіванки на матраці?",
        "tip": "Оцет і сода лише закріплюють кристали сечової кислоти — білок і запах розщеплюють ензими Chemspec",
        "price_line": "Sabrina SW15 (650 грн) + набір «Анти-Запах / Сеча» (250 грн)",
        "topic_prompt": (
            "Рубрика «Лайфхаки для матраців»: жовті ореоли від поту, пролитого молока, дитячих несподіванок або домашніх улюбленців на матраці. "
            "Поясни спокійно та експертно: чому замивання водою, содою чи оцтом не прибирає кристали сечової кислоти у поролоні (запах повертається у сиру погоду). "
            "Дай пораду першої допомоги (сухе промокання без гарячого фена) і поясни, як працює американський ензимний преспрей Chemspec PreKleen + нейтралізатор запаху Kill Odor Citrus + ополіскувач All Fiber Rinse з глибокою витяжкою екстрактором Santoemma Sabrina SW15."
        ),
    },
    {
        "id": 3,
        "image": "3_puzzi_sabrina.jpg",
        "badge": "ОРЕНДА У ДРОГОБИЧІ",
        "headline": "Хімчистка всіх меблів у домі за 600 грн замість 4000 грн!",
        "tip": "Kärcher Puzzi 8/1 та Santoemma Sabrina SW15 на добу  •  Порція фірмової хімії RM 760 у подарунок",
        "price_line": "Puzzi 8/1 — 600 грн/доба  •  Sabrina SW15 — 650 грн/доба",
        "topic_prompt": (
            "Тема: Чому оренда професійного миючого пилососа на добу у Дрогобичі, Трускавці, Бориславі та Стебнику — це у 5–6 разів вигідніше за виклик клінінгу на кожну річ окремо. "
            "Порівняй простою мовою німецький Kärcher Puzzi 8/1 (600 грн/доба — легкий, ідеальний для диванів і авто) та італійську Santoemma Sabrina SW15 (650 грн/доба — підвищений вакуум для товстих матраців і килимів). Нагадай, що перша порція хімії вже входить у вартість, а також видається покрокова інструкція."
        ),
    },
    {
        "id": 4,
        "image": "4_steam_sc2.jpg",
        "badge": "ТЕРМОУДАР ПАРОЮ БЕЗ ХІМІЇ",
        "headline": "Застарілий жир на кухні, шви плитки та наліт у ванній?",
        "tip": "Гаряча пара розчиняє жир за секунди у духовці, витяжці й швах плитки без їдкого запаху хлору",
        "price_line": "Пароочисник Kärcher SC 2 — 400 грн/доба (КОМБО з пилососом: 850 грн)",
        "topic_prompt": (
            "Тема: Генеральне прибирання кухні, духовки, витяжки, міжплиткових швів і санвузла без агресивної побутової хімії за допомогою німецького пароочисника Kärcher SC 2 EasyFix Plus (400 грн/доба або 850 грн у КОМБО №2 разом із миючим пилососом). "
            "Дай 2–3 практичні лайфхаки, що саме у квартирі найшвидше відмивається парою під тиском (жирна решітка витяжки, ущільнювачі вікон, шви плитки, дитячі іграшки) і чого парою гріти не варто (делікатний велюр чи ламінат на стиках без мікрофібри)."
        ),
    },
    {
        "id": 5,
        "image": "5_window_hobot.jpg",
        "badge": "ЧИСТІ ВІКНА БЕЗ РИЗИКУ",
        "headline": "Панорамні вікна та балкони до блиску без миття на висоті!",
        "tip": "Робот Hobot сам натирає скло зовні та всередині  •  Спиртовий концентрат RM 503 без розводів у комплекті",
        "price_line": "Робот-мийник вікон Hobot — 450 грн/доба (КОМБО з SC 2: 750 грн)",
        "topic_prompt": (
            "Тема: Безпечне миття високих вікон, панорамних лоджій, дзеркал шаф-купе та кахлю у прохолодну погоду у Дрогобичі й Трускавці. "
            "Поясни, як працює робот-мийник вікон Hobot (450 грн/доба зі страхувальним тросом, змінними серветками з мікрофібри та німецьким спиртовим концентратом Kärcher RM 503, від якого скло не плаче і не лишає розводів)."
        ),
    },
    {
        "id": 6,
        "image": "6_dryer_dripod.jpg",
        "badge": "СУХИЙ ДИВАН ЗА 2–3 ГОДИНИ",
        "headline": "Боїтеся прати диван восени чи взимку через сирість у кімнаті?",
        "tip": "Турбосушка Dri-Eaz Dri-Pod (США) видуває вологу потоком 360° — спати на матраці можна вже ввечері!",
        "price_line": "КОМБО «Пилосос + Турбосушка Dri-Pod + Хімія» — 850 грн/доба",
        "topic_prompt": (
            "Тема: Як випрати диван, матрац і килими у прохолодну вологу прикарпатську погоду і лягти спати на сухе вже того ж вечора. "
            "Прив'яжи до сьогоднішньої погоди за вікном у Дрогобичі! Поясни, чому без обдуву вологий поролон сохне до 24 годин, а з американською турбосушкою Dri-Eaz Dri-Pod (+250 грн до пилососа у КОМБО №1 за 850 грн/доба) диван висихає за 2–3 години без жодного запаху вогкості."
        ),
    },
    {
        "id": 7,
        "image": "7_car_kwazar.jpg",
        "badge": "ДЕТЕЙЛІНГ АВТО ТА ДЕЛІКАТНИХ ТКАНИН",
        "headline": "Хімчистка салону авто та велюру густою піною без перезволоження!",
        "tip": "Піногенератор Kwazar + нейтральний Koch Chemie Pol Star (pH 7) чистять сидіння, алькантару й карти дверей",
        "price_line": "Пилосос + Піногенератор Kwazar + набір «Авто / Делікат»: від 820 грн",
        "topic_prompt": (
            "Тема: Професійна самостійна хімчистка салону автомобіля або делікатного велюрового дивана вдома без заливання водою. "
            "Розкажи лайфхак дітейлерів: чому сидіння авто з підігрівом і делікатні тканини краще чистити густою напівсухою піною через піногенератор Kwazar Venus Super Foamer Pro+ (+100 грн до пилососа) із німецьким нейтральним засобом Koch Chemie Pol Star (pH 7), а потім миттєво витягувати бруд вузькою насадкою екстрактора Puzzi 8/1. Застережи, що стелю авто мочити екстрактором не можна."
        ),
    },
]

WMO_WEATHER_UA = {
    0: ("Ясно", "сонячна погода без опадів"),
    1: ("Переважно ясно", "легка хмарність з проясненнями"),
    2: ("Хмарно з проясненнями", "мінлива хмарність"),
    3: ("Похмуро", "затягнуте хмарами небо"),
    45: ("Туман", "густий туман і висока вологість повітря"),
    48: ("Туман і паморозь", "туман із памороззю"),
    51: ("Легка мряка", "дрібна мряка і вологе повітря"),
    53: ("Мряка", "мряка і мокрий асфальт"),
    55: ("Сильна мряка", "густа холодна мряка"),
    61: ("Невеликий дощ", "невеликий дощ і мокрі вулиці"),
    63: ("Дощ", "дощ і сльота на вулицях"),
    65: ("Сильна злива", "рясна злива"),
    66: ("Крижаний дощ", "крижаний дощ"),
    67: ("Сильний крижаний дощ", "сильний крижаний дощ"),
    71: ("Невеликий сніг", "легкий сніжок"),
    73: ("Сніг", "сніжна погода у Дрогобичі"),
    75: ("Сильний снігопад", "густий снігопад"),
    77: ("Снігова крупа", "снігова крупа і морозне повітря"),
    80: ("Короткочасний дощ", "короткочасні дощі"),
    81: ("Сильний дощ", "рясний дощ"),
    85: ("Снігопад", "лапатий сніг"),
    86: ("Хуртовина", "заметіль на вулицях"),
}


def strip_non_bmp(text: str) -> str:
    return re.sub(r"[^\u0000-\u27BF]", "", text).strip()


def get_drohobych_weather() -> dict:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=49.35&longitude=23.50"
        "&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
        "&timezone=Europe%2FKyiv"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ProCleanDrohobych/4.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))["current"]
            temp = round(float(data.get("temperature_2m", 5.0)))
            humidity = int(data.get("relative_humidity_2m", 80))
            wcode = int(data.get("weather_code", 3))
            wind = round(float(data.get("wind_speed_10m", 3.0)))
            short_desc, detail_desc = WMO_WEATHER_UA.get(wcode, ("Прохолодно", "типова прикарпатська погода"))
            sign = "+" if temp > 0 else ""
            badge_str = f"Дрогобич: {sign}{temp}°C, {short_desc.lower()}"
            context_str = (
                f"Зараз у Дрогобичі та Трускавці температура {sign}{temp}°C, {detail_desc}, "
                f"вологість повітря {humidity}%, вітер {wind} км/год."
            )
            return {
                "temp": temp,
                "humidity": humidity,
                "wcode": wcode,
                "short_desc": short_desc,
                "badge_str": badge_str,
                "context_str": context_str,
            }
    except Exception as exc:
        print(f"Не вдалося отримати погоду ({exc}) — використовуємо сезонні дані.")
        return {
            "temp": 4,
            "humidity": 82,
            "wcode": 3,
            "short_desc": "Прохолодно",
            "badge_str": "Дрогобич: +4°C, прохолодно",
            "context_str": "Зараз у Дрогобичі прохолодна пора, висока вологість повітря.",
        }


def get_ukrainian_calendar_context(now_kyiv: datetime.datetime) -> dict:
    today = now_kyiv.date()
    year = today.year

    weekdays_ua = ["понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"]
    months_genitive = {
        1: "січня", 2: "лютого", 3: "березня", 4: "квітня",
        5: "травня", 6: "червня", 7: "липня", 8: "серпня",
        9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня",
    }
    weekday_name = weekdays_ua[today.weekday()]
    date_human = f"{today.day} {months_genitive[today.month]}"
    is_morning = now_kyiv.hour < 14
    time_of_day_hint = (
        "Ранковий час — люди у Дрогобичі п'ють ранкову каву і планують справи на день."
        if is_morning else
        "Вечірній час — люди повернулися з роботи додому, відпочивають і планують завтрашній день або вихідні."
    )

    holidays = [
        (datetime.date(year, 11, 21), "День Гідності та Свободи"),
        (datetime.date(year, 11, 30), "День Святого Андрія Первозванного"),
        (datetime.date(year, 12, 6), "День Святого Миколая та День ЗСУ"),
        (datetime.date(year, 12, 24), "Святвечір перед Різдвом Христовим"),
        (datetime.date(year, 12, 25), "Різдво Христове"),
        (datetime.date(year, 1, 1), "Новий рік"),
        (datetime.date(year + 1, 1, 1), "Новий рік"),
        (datetime.date(year, 1, 6), "Водохреща (Богоявлення)"),
        (datetime.date(year + 1, 1, 6), "Водохреща (Богоявлення)"),
        (datetime.date(year, 2, 14), "День Святого Валентина"),
        (datetime.date(year + 1, 2, 14), "День Святого Валентина"),
        (datetime.date(year, 3, 8), "Весняне оновлення дому"),
        (datetime.date(year, 5, 1), "Великоднє генеральне прибирання"),
        (datetime.date(year, 8, 24), "День Незалежності України"),
        (datetime.date(year, 10, 1), "Покрова Пресвятої Богородиці та День захисників України"),
    ]

    upcoming_notes = []
    short_countdown_badge = f"{date_human}, {weekday_name}"

    for h_date, h_title in holidays:
        delta = (h_date - today).days
        if delta == 0:
            upcoming_notes.append(f"СЬОГОДНІ СВЯТО: {h_title}! Доречно коротко привітати читачів.")
            short_countdown_badge = f"Сьогодні: {h_title}"
        elif 1 <= delta <= 45:
            upcoming_notes.append(f"До події «{h_title}» залишилося {delta} дн.")

    st_nicholas = datetime.date(year, 12, 6)
    christmas = datetime.date(year, 12, 25)
    new_year = datetime.date(year + 1, 1, 1)

    if 1 <= (st_nicholas - today).days <= 30:
        short_countdown_badge = f"До Миколая: {(st_nicholas - today).days} дн."
    elif 1 <= (christmas - today).days <= 25:
        short_countdown_badge = f"До Різдва: {(christmas - today).days} дн."
    elif 1 <= (new_year - today).days <= 25:
        short_countdown_badge = f"До Нового року: {(new_year - today).days} дн."

    weekday_advice = ""
    if today.weekday() in (3, 4):
        weekday_advice = "Кінець робочого тижня — нагадай забронювати техніку на суботу-неділю заздалегідь."
    elif today.weekday() in (5, 6):
        weekday_advice = "Вихідний день — зручний час оновити меблі за пару годин."

    calendar_summary = (
        f"Сьогодні {date_human} {year} року ({weekday_name}). {time_of_day_hint} "
        f"{'; '.join(upcoming_notes[:2]) if upcoming_notes else 'Сезон домашнього затишку.'} {weekday_advice}"
    )
    return {
        "date_human": date_human,
        "weekday_name": weekday_name,
        "short_countdown_badge": short_countdown_badge,
        "calendar_summary": calendar_summary,
    }


def discover_gemini_models(gemini_api_key: str) -> list[str]:
    fallback_candidates = [
        "gemini-2.5-flash",
        "gemini-2.0-flash",
        "gemini-flash-lite-latest",
    ]
    list_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={gemini_api_key}"
    try:
        req = urllib.request.Request(list_url, headers={"User-Agent": "ProCleanAutoPoster/4.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            found_flash = []
            found_other = []
            skip_words = ("tts", "image", "embedding", "aqa", "audio", "vision", "veo", "imagen", "robotics", "thinking")
            for m in data.get("models", []):
                methods = m.get("supportedGenerationMethods", [])
                name = m.get("name", "")
                if "generateContent" not in methods or not name.startswith("models/gemini"):
                    continue
                short_name = name.replace("models/", "")
                if any(sw in short_name.lower() for sw in skip_words):
                    continue
                if "flash" in short_name.lower():
                    found_flash.append(short_name)
                else:
                    found_other.append(short_name)
            found_flash.sort(reverse=True)
            found_other.sort(reverse=True)
            combined = found_flash + found_other
            if combined:
                print(f"Активні моделі Gemini: {combined[:5]}")
                return combined[:5]
    except Exception as exc:
        print(f"Не вдалося отримати список моделей ({exc}), використовуємо резервні.")
    return fallback_candidates


def generate_live_caption_with_gemini(
    topic: dict, weather: dict, cal: dict, gemini_api_key: str
) -> str:
    if not gemini_api_key:
        return build_dynamic_fallback_caption(topic, weather, cal)

    prompt = f"""{BUSINESS_CONTEXT}

КОНТЕКСТ СЬОГОДНІШНЬОГО ДНЯ У ДРОГОБИЧІ:
1. ДАТА: {cal['calendar_summary']}
2. ПОГОДА ЗАРАЗ У ДРОГОБИЧІ: {weather['context_str']}
3. ТЕМА ДОПИСУ: {topic['topic_prompt']}

Напиши природний, практичний і корисний допис українською мовою для жителів Дрогобича, Трускавця, Борислава, Стебника та Східниці у Facebook та Instagram.

СУВОРІ ПРАВИЛА:
- Пиши грамотною чистою українською мовою (без суржику і без випадкових латинських літер усередині українських слів; назви брендів Kärcher Puzzi 8/1, Santoemma Sabrina SW15, Chemspec, Koch Chemie Pol Star, Hobot, Dri-Eaz Dri-Pod, Kwazar пиши правильно латиницею).
- У першому короткому абзаці ненав'язливо поєднай тему з сьогоднішньою погодою у Дрогобичі ({weather['temp']}°C, {weather['short_desc'].lower()}) або днем тижня ({cal['weekday_name']}).
- Дай конкретний покроковий лайфхак (нумерованим списком 1, 2, 3), щоб читач зберіг допис у закладки.
- Коротко й чітко запропонуй рішення від PRO-CLEAN RENT з реальними цінами у гривнях.
- Додай контакти:
  Телефон / Viber / Telegram: 098 521 02 04
  Онлайн-калькулятор та бронювання: https://proclean-drohobych.netlify.app
- У кінці один рядок з 6–8 хештегів: #дрогобич #трускавець #борислав #стебник #східниця #хімчисткадрогобич #орендадрогобич #procleanrent
- НЕ використовуй символи ** або ###, поверни лише готовий чистий текст поста (до 1300 символів).
"""

    for model_name in discover_gemini_models(gemini_api_key):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.75, "maxOutputTokens": 1200},
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                parts = data["candidates"][0]["content"]["parts"]
                text = "".join(p.get("text", "") for p in parts).strip()
                text = text.replace("**", "").replace("###", "")
                if len(text) > 180:
                    print(f"Унікальний живий текст згенеровано через {model_name}!")
                    return text
        except Exception as exc:
            print(f"Модель {model_name} недоступна ({exc}), пробуємо наступну...")

    return build_dynamic_fallback_caption(topic, weather, cal)


def build_dynamic_fallback_caption(topic: dict, weather: dict, cal: dict) -> str:
    sign = "+" if weather["temp"] > 0 else ""
    return (
        f"Дрогобич сьогодні зустрічає погодою {sign}{weather['temp']}°C ({weather['short_desc'].lower()}), "
        f"на календарі {cal['date_human']} ({cal['weekday_name']}) — саме час подбати про чистоту та свіжість оселі.\n\n"
        f"{topic['headline']}\n"
        f"{topic['tip']}\n\n"
        f"У сервісі PRO-CLEAN RENT доступні подобово:\n"
        f"• Kärcher Puzzi 8/1 — 600 грн/доба (порція хімії RM 760 у комплекті)\n"
        f"• Santoemma Sabrina SW15 — 650 грн/доба\n"
        f"• КОМБО «Пилосос + Турбосушка Dri-Eaz Dri-Pod» — 850 грн/доба (сухий диван за 2–3 год)\n"
        f"• Пароочисник Kärcher SC 2 — 400 грн | Робот для вікон Hobot — 450 грн | Озонатор YATO — 350 грн\n"
        f"• Професійна порційна хімія Chemspec (США) та Koch Chemie (Німеччина)\n\n"
        f"Онлайн-калькулятор та набори хімії: https://proclean-drohobych.netlify.app\n"
        f"Бронювання (Тел / Viber / Telegram): 098 521 02 04\n\n"
        f"#дрогобич #трускавець #борислав #стебник #східниця #хімчисткадрогобич #орендадрогобич #procleanrent"
    )


def ensure_editorial_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    font_dir = Path("/tmp/proclean_fonts")
    font_dir.mkdir(parents=True, exist_ok=True)
    ttf_name = "Montserrat-Bold.ttf" if bold else "Montserrat-Medium.ttf"
    cached_ttf = font_dir / ttf_name

    if not cached_ttf.exists():
        raw_url = (
            "https://github.com/JulietaUla/Montserrat/raw/master/fonts/ttf/" + ttf_name
        )
        try:
            req = urllib.request.Request(raw_url, headers={"User-Agent": "ProCleanAutoPoster/4.1"})
            with urllib.request.urlopen(req, timeout=12) as resp:
                data = resp.read()
                if len(data) > 40000:
                    cached_ttf.write_bytes(data)
        except Exception:
            pass

    candidates = [
        str(cached_ttf),
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def wrap_and_fit_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_lines: int,
    start_size: int,
    min_size: int = 20,
    bold: bool = True,
) -> tuple[list[str], ImageFont.FreeTypeFont]:
    clean = strip_non_bmp(text)
    words = clean.split()
    if not words:
        return [], ensure_editorial_font(min_size, bold=bold)

    for size in range(start_size, min_size - 1, -2):
        font = ensure_editorial_font(size, bold=bold)
        lines: list[str] = []
        current = words[0]
        fits_single_words = measure_text(draw, current, font)[0] <= max_width

        for w in words[1:]:
            trial = f"{current} {w}"
            if measure_text(draw, trial, font)[0] <= max_width:
                current = trial
            else:
                lines.append(current)
                current = w
                if measure_text(draw, current, font)[0] > max_width:
                    fits_single_words = False
        lines.append(current)

        if fits_single_words and len(lines) <= max_lines:
            return lines, font

    font = ensure_editorial_font(min_size, bold=bold)
    lines = []
    current = words[0]
    for w in words[1:]:
        trial = f"{current} {w}"
        if measure_text(draw, trial, font)[0] <= max_width:
            current = trial
        else:
            lines.append(current)
            current = w
    lines.append(current)
    return lines[:max_lines], font


def resolve_topic_image(topic: dict) -> Path:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    valid_exts = {".jpg", ".jpeg", ".jfif", ".png", ".webp"}
    skip_prefixes = ("daily_smart_card", "generated_")

    all_files = sorted(
        p for p in IMAGES_DIR.iterdir()
        if p.is_file()
        and p.suffix.lower() in valid_exts
        and not p.name.lower().startswith(skip_prefixes)
    )
    if not all_files:
        assets_dir = IMAGES_DIR / "assets"
        if assets_dir.exists():
            all_files = sorted(
                p for p in assets_dir.iterdir()
                if p.is_file()
                and p.suffix.lower() in valid_exts
                and not p.name.lower().startswith(skip_prefixes)
            )

    if not all_files:
        raise FileNotFoundError(f"У папці {IMAGES_DIR} немає вхідних зображень!")

    target = str(topic.get("image", "")).strip()
    if target:
        target_stem = Path(target).name.lower().split(".")[0]
        for p in all_files:
            if p.name.lower().split(".")[0] == target_stem:
                return p

    idx = (int(topic.get("id", 1)) - 1) % len(all_files)
    return all_files[idx]


def apply_editorial_vignette(base_rgb: Image.Image) -> Image.Image:
    """М'яке кінематографічне затемнення лише зверху (для плашки погоди) і знизу (для тексту), центр фото 100% чистий."""
    w, h = base_rgb.size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    grad_col = Image.new("RGBA", (1, h), (0, 0, 0, 0))
    px = grad_col.load()

    top_end = 150
    bot_start = 680

    for y in range(h):
        alpha = 0
        if y < top_end:
            t = 1.0 - (y / top_end)
            alpha = int(125 * (t ** 1.5))
        elif y >= bot_start:
            t = (y - bot_start) / max(1, (h - 1 - bot_start))
            smooth = 0.5 - 0.5 * math.cos(math.pi * min(1.0, t))
            alpha = int(244 * (smooth ** 0.68))
        px[0, y] = (10, 15, 28, alpha)

    overlay = grad_col.resize((w, h), Image.Resampling.BILINEAR)
    composed = Image.alpha_composite(base_rgb.convert("RGBA"), overlay)
    return composed.convert("RGB")


def render_editorial_card(topic: dict, weather: dict, cal: dict, out_path: Path) -> Path:
    src_path = resolve_topic_image(topic)
    print(f"Фото-основа: {src_path.name}")

    raw_img = ImageOps.exif_transpose(Image.open(src_path)).convert("RGB")
    # Центрування зі зміщенням трохи вище центру (0.42), щоб головний об'єкт кадру був у чистій зоні над текстом
    fitted = ImageOps.fit(
        raw_img,
        (CARD_W, CARD_H),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.42),
    )
    canvas = apply_editorial_vignette(fitted).convert("RGBA")
    ui_layer = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui_layer)

    # 1. Верхня напівпрозора плашка погоди та календаря (компактна, динамічна ширина)
    top_text = strip_non_bmp(f"{weather['badge_str']}  •  {cal['short_countdown_badge']}")
    top_lines, f_top = wrap_and_fit_text(draw, top_text, MAX_TEXT_W - 44, max_lines=1, start_size=22, min_size=16, bold=True)
    top_line = top_lines[0] if top_lines else top_text
    tw, th = measure_text(draw, top_line, f_top)
    pill_w = min(MAX_TEXT_W, tw + 44)
    pill_h = th + 24
    pill_x1 = SAFE_PAD_X
    pill_y1 = 42
    draw.rounded_rectangle(
        [pill_x1, pill_y1, pill_x1 + pill_w, pill_y1 + pill_h],
        radius=pill_h // 2,
        fill=(15, 23, 42, 178),
        outline=(255, 255, 255, 58),
        width=2,
    )
    t_bbox = draw.textbbox((0, 0), top_line, font=f_top)
    draw.text(
        (pill_x1 + 22 - t_bbox[0], pill_y1 + (pill_h - (t_bbox[3] - t_bbox[1])) // 2 - t_bbox[1]),
        top_line,
        font=f_top,
        fill=(241, 245, 249, 255),
    )

    # Підготовка нижнього текстового блоку знизу вгору (щоб 0% шансів вилізти за край!)
    # Футер (контакти + сайт)
    footer_geo = "Дрогобич • Трускавець • Борислав • Стебник  |  proclean-drohobych.netlify.app"
    geo_lines, f_geo = wrap_and_fit_text(draw, footer_geo, MAX_TEXT_W, max_lines=1, start_size=20, min_size=15, bold=False)
    geo_line = geo_lines[0]

    # Цінова плашка + телефон
    price_str = f"{strip_non_bmp(topic['price_line'])}   |   098 521 02 04"
    price_lines, f_price = wrap_and_fit_text(draw, price_str, MAX_TEXT_W - 44, max_lines=1, start_size=25, min_size=17, bold=True)
    price_line = price_lines[0]

    # Практичний лайфхак / опис (до 2 рядків)
    tip_lines, f_tip = wrap_and_fit_text(draw, topic["tip"], MAX_TEXT_W, max_lines=2, start_size=24, min_size=18, bold=False)

    # Головний заголовок (до 2 рядків)
    head_lines, f_head = wrap_and_fit_text(draw, topic["headline"], MAX_TEXT_W, max_lines=2, start_size=44, min_size=30, bold=True)

    # Бейдж рубрики
    badge_str = strip_non_bmp(topic["badge"]).upper()
    badge_lines, f_badge = wrap_and_fit_text(draw, badge_str, MAX_TEXT_W - 40, max_lines=1, start_size=20, min_size=15, bold=True)
    badge_line = badge_lines[0]

    # Точний розрахунок координат знизу вгору з комфортним повітрям
    y_cursor = CARD_H - 46

    # 5) Нижній рядок міст та сайту
    g_bbox = draw.textbbox((0, 0), geo_line, font=f_geo)
    gh = g_bbox[3] - g_bbox[1]
    y_cursor -= gh
    draw.text((SAFE_PAD_X - g_bbox[0], y_cursor - g_bbox[1]), geo_line, font=f_geo, fill=(186, 230, 253, 235))
    y_cursor -= 20

    # 4) Акцентна жовта плашка з ціною та номером 098 521 02 04
    p_bbox = draw.textbbox((0, 0), price_line, font=f_price)
    pw, ph = p_bbox[2] - p_bbox[0], p_bbox[3] - p_bbox[1]
    bar_h = ph + 28
    bar_w = min(MAX_TEXT_W, max(pw + 44, MAX_TEXT_W))
    y_cursor -= bar_h
    draw.rounded_rectangle(
        [SAFE_PAD_X, y_cursor, SAFE_PAD_X + bar_w, y_cursor + bar_h],
        radius=16,
        fill=(250, 204, 21, 248),
    )
    draw.text(
        (SAFE_PAD_X + (bar_w - pw) // 2 - p_bbox[0], y_cursor + (bar_h - ph) // 2 - p_bbox[1]),
        price_line,
        font=f_price,
        fill=(15, 23, 42, 255),
    )
    y_cursor -= 22

    # 3) Рядки лайфхаку / підзаголовка
    for line in reversed(tip_lines):
        lb = draw.textbbox((0, 0), line, font=f_tip)
        lh = lb[3] - lb[1]
        y_cursor -= lh
        draw.text((SAFE_PAD_X - lb[0], y_cursor - lb[1]), line, font=f_tip, fill=(226, 232, 240, 248))
        y_cursor -= 10
    y_cursor -= 12

    # 2) Головний заголовок (з м'якою тінню для читабельності)
    for line in reversed(head_lines):
        hb = draw.textbbox((0, 0), line, font=f_head)
        lh = hb[3] - hb[1]
        y_cursor -= lh
        draw.text((SAFE_PAD_X - hb[0] + 2, y_cursor - hb[1] + 2), line, font=f_head, fill=(0, 0, 0, 140))
        draw.text((SAFE_PAD_X - hb[0], y_cursor - hb[1]), line, font=f_head, fill=(255, 255, 255, 255))
        y_cursor -= 12
    y_cursor -= 12

    # 1) Компактний бейдж рубрики над заголовком
    bb = draw.textbbox((0, 0), badge_line, font=f_badge)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    b_pad_x, b_pad_y = 18, 10
    b_h = bh + b_pad_y * 2
    b_w = min(MAX_TEXT_W, bw + b_pad_x * 2)
    y_cursor -= b_h
    draw.rounded_rectangle(
        [SAFE_PAD_X, y_cursor, SAFE_PAD_X + b_w, y_cursor + b_h],
        radius=10,
        fill=(15, 23, 42, 220),
        outline=(56, 189, 248, 210),
        width=2,
    )
    draw.text(
        (SAFE_PAD_X + b_pad_x - bb[0], y_cursor + b_pad_y - bb[1]),
        badge_line,
        font=f_badge,
        fill=(186, 230, 253, 255),
    )

    final_rgb = Image.alpha_composite(canvas, ui_layer).convert("RGB")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final_rgb.save(str(out_path), format="JPEG", quality=95, subsampling=0, optimize=True)
    size_kb = out_path.stat().st_size // 1024
    print(f"Збережено HD-картку {CARD_W}x{CARD_H}: {out_path} ({size_kb} KB)")
    return out_path


def commit_and_push_generated_image(rel_image_path: str) -> bool:
    try:
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", rel_image_path], check=True)
        subprocess.run(["git", "commit", "-m", f"Update daily smart card: {rel_image_path}"], check=False)
        subprocess.run(["git", "pull", "--rebase"], check=False)
        subprocess.run(["git", "push"], check=True)
        print("Оновлену картку збережено в GitHub репозиторії! Чекаємо 5 с на оновлення CDN...")
        time.sleep(5)
        return True
    except Exception as exc:
        print(f"Не вдалося запушити картинку в git ({exc}).")
        return False


def publish_to_facebook_page_binary(page_id: str, access_token: str, local_image_path: str, caption: str) -> dict:
    endpoint = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{page_id}/photos"
    boundary = f"----ProCleanBoundary{uuid.uuid4().hex}"

    with open(local_image_path, "rb") as f:
        img_bytes = f.read()

    body = io.BytesIO()
    for field_name, field_val in [("caption", caption), ("access_token", access_token)]:
        body.write(f"--{boundary}\r\n".encode("utf-8"))
        body.write(f'Content-Disposition: form-data; name="{field_name}"\r\n\r\n'.encode("utf-8"))
        body.write(field_val.encode("utf-8"))
        body.write(b"\r\n")

    body.write(f"--{boundary}\r\n".encode("utf-8"))
    body.write(b'Content-Disposition: form-data; name="source"; filename="daily_smart_card.jpg"\r\n')
    body.write(b"Content-Type: image/jpeg\r\n\r\n")
    body.write(img_bytes)
    body.write(f"\r\n--{boundary}--\r\n".encode("utf-8"))

    req = urllib.request.Request(
        endpoint,
        data=body.getvalue(),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_json = exc.read().decode("utf-8", errors="replace")
        print(f"Детальна відповідь Facebook API (HTTP {exc.code}): {err_json}")
        raise


def publish_to_instagram_business(ig_user_id: str, access_token: str, image_url: str, caption: str) -> dict:
    create_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{ig_user_id}/media"
    create_data = urllib.parse.urlencode({
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token,
    }).encode("utf-8")
    req1 = urllib.request.Request(create_url, data=create_data, method="POST")
    try:
        with urllib.request.urlopen(req1, timeout=35) as resp1:
            container_info = json.loads(resp1.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_json = exc.read().decode("utf-8", errors="replace")
        print(f"Детальна відповідь Instagram Media API (HTTP {exc.code}): {err_json}")
        raise

    creation_id = container_info["id"]
    print(f"Instagram медіа-контейнер створено: {creation_id}. Чекаємо 10 с на обробку...")
    time.sleep(10)

    publish_url = f"https://graph.facebook.com/{GRAPH_API_VERSION}/{ig_user_id}/media_publish"
    publish_data = urllib.parse.urlencode({
        "creation_id": creation_id,
        "access_token": access_token,
    }).encode("utf-8")
    req2 = urllib.request.Request(publish_url, data=publish_data, method="POST")
    try:
        with urllib.request.urlopen(req2, timeout=35) as resp2:
            return json.loads(resp2.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        err_json = exc.read().decode("utf-8", errors="replace")
        print(f"Детальна відповідь Instagram Publish API (HTTP {exc.code}): {err_json}")
        raise


def main() -> None:
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_kyiv = now_utc + datetime.timedelta(hours=2)

    day_of_year = now_kyiv.timetuple().tm_yday
    slot = 0 if now_kyiv.hour < 14 else 1
    idx_str = os.environ.get("FORCE_TOPIC_INDEX", "").strip()
    if idx_str.isdigit():
        # Підтримка як 0..6, так і 1..7 при ручному введенні
        val = int(idx_str)
        topic_index = (val - 1) if 1 <= val <= len(TOPICS) else (val % len(TOPICS))
    else:
        topic_index = (day_of_year * 2 + slot) % len(TOPICS)

    topic = TOPICS[topic_index % len(TOPICS)]

    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    fb_page_id = (os.environ.get("FB_PAGE_ID") or os.environ.get("FACEBOOK_PAGE_ID") or "").strip()
    ig_user_id = (
        os.environ.get("IG_USER_ID")
        or os.environ.get("IG_ACCOUNT_ID")
        or os.environ.get("IG_BUSINESS_ID")
        or ""
    ).strip()
    meta_token = (
        os.environ.get("META_PAGE_ACCESS_TOKEN")
        or os.environ.get("META_ACCESS_TOKEN")
        or ""
    ).strip()
    github_repo = os.environ.get("GITHUB_REPOSITORY", "procleanrentua-wq/proclean-autoposter").strip()
    branch = os.environ.get("GITHUB_REF_NAME", "main").strip()

    weather = get_drohobych_weather()
    cal = get_ukrainian_calendar_context(now_kyiv)

    print(f"=== Рубрика #{topic['id']}: {topic['headline']} ({now_kyiv.strftime('%Y-%m-%d %H:%M')} Kyiv) ===")
    print(f"Погода: {weather['context_str']}")
    print(f"Календар: {cal['calendar_summary']}")

    card_path = render_editorial_card(topic, weather, cal, OUTPUT_CARD_PATH)

    pushed = False
    if os.environ.get("GITHUB_ACTIONS") == "true":
        pushed = commit_and_push_generated_image(OUTPUT_REL_PATH)

    caption = generate_live_caption_with_gemini(topic, weather, cal, gemini_key)
    print("\n--- ЗГЕНЕРОВАНИЙ ЖИВИЙ ТЕКСТ ПОСТА ---\n")
    print(caption)
    print("\n--------------------------------------\n")

    if not meta_token or not fb_page_id:
        if os.environ.get("GITHUB_ACTIONS") == "true":
            raise RuntimeError("Не знайдено секретів META_PAGE_ACCESS_TOKEN або FB_PAGE_ID у GitHub Secrets!")
        print("Локальний тестовий запуск завершено (без публікації в соцмережі).")
        return

    cache_bust = int(time.time())
    if pushed:
        image_url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/{OUTPUT_REL_PATH}?v={cache_bust}"
    else:
        src_rel = resolve_topic_image(topic).relative_to(BASE_DIR).as_posix()
        image_url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/{urllib.parse.quote(src_rel)}?v={cache_bust}"

    print(f"URL зображення для Instagram: {image_url}")

    errors = []

    if fb_page_id:
        print(f"Публікуємо HD-фото на сторінку Facebook ({fb_page_id})...")
        try:
            fb_res = publish_to_facebook_page_binary(fb_page_id, meta_token, str(card_path), caption)
            print("Успішно опубліковано у Facebook! ID:", fb_res.get("id"))
        except Exception as exc:
            errors.append(f"Facebook: {exc}")

    if ig_user_id:
        print(f"Публікуємо HD-фото в Instagram Business ({ig_user_id})...")
        try:
            ig_res = publish_to_instagram_business(ig_user_id, meta_token, image_url, caption)
            print("Успішно опубліковано в Instagram! ID:", ig_res.get("id"))
        except Exception as exc:
            errors.append(f"Instagram: {exc}")

    if errors:
        print("\nВиникли помилки під час публікації:")
        for err in errors:
            print(" -", err)
        sys.exit(1)


if __name__ == "__main__":
    main()
