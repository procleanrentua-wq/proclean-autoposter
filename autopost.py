#!/usr/bin/env python3
"""
PRO-CLEAN RENT v4.2 — Editorial 4:5 HD AutoPoster (1080x1350):
- Автоматичне чергування 1 через 1: журнальна картка з лайфхаком <-> 100% чисте інтер'єрне фото без написів (проти банерної сліпоти).
- Крупний читабельний шрифт на жовтій плашці та нижчий градієнт (не перекриває акцентні деталі в центрі кадру).
- Повна відсутність згадок про ФОП, прізвища, імена та назви вулиць (лише бренд PRO-CLEAN RENT, міста обслуговування, телефон і сайт).
- Повна сумісність із .github/workflows/main.yml (META_PAGE_ACCESS_TOKEN, FB_PAGE_ID, IG_USER_ID, GEMINI_API_KEY) та фото .jfif / .jpg / .png / .webp.
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
SAFE_PAD_X = 64
MAX_TEXT_W = CARD_W - SAFE_PAD_X * 2  # 952 px безпечної ширини

BUSINESS_CONTEXT = """
Ти ведеш сторінку локального сервісу оренди техніки та хімчистки PRO-CLEAN RENT.
Міста обслуговування: Дрогобич, Трускавець, Борислав, Стебник, Східниця.
Контакти: Тел / Viber / Telegram / WhatsApp: 098 521 02 04.
Сайт з онлайн-калькулятором: https://proclean-drohobych.netlify.app

СУВОРЕ ПРАВИЛО КОНФІДЕНЦІЙНОСТІ:
Ніколи НЕ згадуй у тексті слово «ФОП», жодних прізвищ, імен власника чи майстрів, а також жодних назв вулиць чи номерів будинків. Пиши від імені команди сервісу PRO-CLEAN RENT, а щодо отримання техніки зазначай просто: «самовивіз у Дрогобичі або доставка під двері».

Наші послуги та актуальні ціни:
1) Подобова оренда професійної техніки для самостійної хімчистки (1 порція 80 г хімії Kärcher RM 760 у подарунок до кожного миючого пилососа):
   - Миючий пилосос-екстрактор Kärcher Puzzi 8/1 (Німеччина) — 600 грн/доба
   - Потужний італійський екстрактор Santoemma Sabrina SW15 (глибока витяжка з товстих матраців і килимів) — 650 грн/доба
   - Пароочисник Kärcher SC 2 EasyFix Plus (кухня, жир, духовка, плитка, шви, санвузол без хімії) — 400 грн/доба
   - Робот для миття вікон Hobot (спиртовий концентрат RM 503 та серветки у комплекті) — 450 грн/доба
   - Американська турбосушка Dri-Eaz Dri-Pod (сушить диван чи матрац за 2–3 години замість 24 годин у вологу погоду) — 350 грн/доба (+250 грн у комбо з пилососом)
   - Професійний озонатор повітря YATO YT-73350 (усуває запахи диму, тварин, сечі, плісняви, вогкості) — 350 грн/доба
   - Піногенератор 2 л Kwazar Venus Super Foamer Pro+ (густа активна піна для авто та делікатних тканин) — +100 грн/доба до пилососа (150 грн окремо)
   - Порційна професійна хімія: Kärcher RM 760 (90 грн), кислотний ополіскувач Chemspec All Fiber Textile Rinse (90 грн), ензимний преспрей Chemspec PreKleen проти білка й сечі (100 грн), нейтралізатор запахів Chemspec Kill Odor Citrus (100 грн), делікатний Koch Chemie Pol Star pH 7 (130 грн), плямовивідник Kärcher RM 769 (100 грн), піногасник RM 761 (70 грн).
   - Готові набори хімії: «Дитячий / Гіпоалергенний» (110 грн), «Анти-Запах Тварин / Сеча» (250 грн), «Делікат / Авто + Піна Kwazar» (220 грн), «Анти-Пляма MAX» (340 грн).
   - Вигідні КОМБО на добу:
     * КОМБО №1 «Сухий диван за 2 години» (Пилосос + Турбосушка + хімія) = 850 грн (з Puzzi) / 900 грн (з Sabrina)
     * КОМБО №2 «Меблі + Кухня та Ванна» (Пилосос + Пароочисник SC 2 + хімія) = 850 грн / 900 грн
     * КОМБО №3 «Анти-Запах» (Пилосос + Озонатор YATO + хімія) = 850 грн / 900 грн
     * КОМБО №4 «Ідеальні вікна та шви» (Робот Hobot + Пароочисник SC 2) = 750 грн
     * КОМБО №5 «Генеральне прибирання All-in-One» (Екстрактор + Пароочисник + Hobot + Турбосушка) = 1450 грн / 1500 грн
   - Доставка в 1 сторону: самовивіз у Дрогобичі — 0 грн; доставка по Дрогобичу — 150 грн; Трускавець / Стебник — 200 грн; Борислав — 250 грн; Східниця — 350 грн.

2) Виїзна 5-ступенева хімчистка м'яких меблів, матраців, килимів і салонів авто (ензими Chemspec США + обов'язкове кислотне ополіскування All Fiber Rinse, безпечно для немовлят та алергіків).
"""

TOPICS = [
    {
        "id": 1,
        "image": "1_coffee_sofa.jpg",
        "badge": "ЛАЙФХАК ПРОТИ ПЛЯМ",
        "headline": "Розлили каву на світлий диван? Не тріть губкою!",
        "tip": "1. Промокніть серветкою без тертя  •  2. Без окропу й «Ванішу»  •  3. Промийте екстрактором",
        "cta_button": "Оренда Puzzi 8/1: 600 грн/доба  •  098 521 02 04",
        "topic_prompt": (
            "Рубрика «Лайфхаки з виведення плям»: пролита кава з молоком, чай або вино на світлому дивані. "
            "Дай 3 конкретні практичні дії першої допомоги: 1) притискати сухі білі паперові рушники від країв до центру без тертя по колу; "
            "2) не лити гарячу воду й не сушити гарячим феном (білок молока запікається у волокнах) та не заливати побутовим милом чи «Ванішем» (лишає липкий ореол); "
            "3) злегка зволожити пляму прохолодною чистою водою й витягнути рідину з поролону вакуумним екстрактором Kärcher Puzzi 8/1 (600 грн/доба з порцією RM 760 у комплекті) або Santoemma Sabrina SW15 (650 грн/доба) з ополіскувачем Chemspec All Fiber Rinse."
        ),
    },
    {
        "id": 2,
        "image": "2_mattress_stain.jpg",
        "badge": "ЕНЗИМНА ЧИСТКА МАТРАЦІВ",
        "headline": "Жовті ореоли чи дитячі й котячі несподіванки на матраці?",
        "tip": "Оцет і сода лише консервують сечову кислоту — білок і запах розщеплюють ензими Chemspec",
        "cta_button": "Оренда Sabrina SW15: 650 грн/доба  •  098 521 02 04",
        "topic_prompt": (
            "Рубрика «Лайфхаки для матраців»: жовті ореоли від поту, молока, дитячих несподіванок або домашніх тварин на матраці. "
            "Дай 3 конкретні кроки першої допомоги: 1) максимально зібрати вологу сухими паперовими рушниками, сильно притискаючи їх до матраца; "
            "2) не сушити гарячим феном чи праскою та не засипати содою з оцтом (кристали сечової кислоти залишаються в поролоні і знову пахнуть у вологу погоду); "
            "3) розщепити білок теплим ензимним розчином Chemspec PreKleen на 15 хвилин, нейтралізувати запах Kill Odor Citrus і промити з кислотним ополіскувачем All Fiber Rinse потужним екстрактором Santoemma Sabrina SW15 (650 грн/доба + набір хімії «Анти-Запах / Сеча» 250 грн, а з турбосушкою Dri-Pod матрац висохне за 2–3 години)."
        ),
    },
    {
        "id": 3,
        "image": "3_puzzi_sabrina.jpg",
        "badge": "ОРЕНДА У ДРОГОБИЧІ",
        "headline": "Хімчистка всіх меблів у домі за 600 грн замість 4000 грн!",
        "tip": "Kärcher Puzzi 8/1 та Santoemma Sabrina SW15 на добу  •  Порція хімії RM 760 у подарунок",
        "cta_button": "Оренда від 600 грн/доба  •  098 521 02 04",
        "topic_prompt": (
            "Тема: Як за одну добу самостійно перемити диван, крісла, матраци і килими у 5–6 разів дешевше за виклик клінінгу на кожну річ. "
            "Дай 3 прості поради, як обрати апарат під свої завдання: 1) німецький Kärcher Puzzi 8/1 (600 грн/доба) — легкий та маневровий для диванів, крісел і салону авто; "
            "2) італійський Santoemma Sabrina SW15 (650 грн/доба) — підвищена сила всмоктування для товстих матраців і килимів; "
            "3) обов'язковий фінальний прохід чистою водою або ополіскувачем Chemspec All Fiber Rinse, щоб тканина стала м'якою та гіпоалергенною."
        ),
    },
    {
        "id": 4,
        "image": "4_steam_sc2.jpg",
        "badge": "ПАРООЧИСТКА БЕЗ ХІМІЇ",
        "headline": "Застарілий жир на кухні, шви плитки та наліт у ванній?",
        "tip": "Гаряча пара під тиском розчиняє жир у духовці, витяжці й швах плитки без запаху хлору",
        "cta_button": "Пароочисник SC 2: 400 грн/доба  •  098 521 02 04",
        "topic_prompt": (
            "Тема: Екологічне генеральне прибирання кухні та ванної кімнати пароочисником Kärcher SC 2 EasyFix Plus (400 грн/доба або 850 грн у КОМБО №2 з миючим пилососом). "
            "Дай 3 конкретні лайфхаки роботи з парою: 1) точковою насадкою вибити чорний наліт із міжплиткових швів і гумок душової кабіни й одразу протерти мікрофіброю; "
            "2) розм'якшити липкий жир на решітці витяжки та дверцятах духовки без їдкої лужної хімії; "
            "3) пройтися парою по радіаторах опалення й ущільнювачах вікон, не затримуючи сопло в одній точці на ламінаті чи делікатному пластику."
        ),
    },
    {
        "id": 5,
        "image": "5_window_hobot.jpg",
        "badge": "ЧИСТІ ВІКНА БЕЗ РИЗИКУ",
        "headline": "Панорамні вікна та балкони до блиску без миття на висоті!",
        "tip": "Робот Hobot сам натирає скло зовні й усередині  •  Спиртовий концентрат RM 503 у комплекті",
        "cta_button": "Робот вікон Hobot: 450 грн/доба  •  098 521 02 04",
        "topic_prompt": (
            "Тема: Безпечне миття високих вікон, панорамних балконів, дзеркал шаф-купе та глянцевої плитки роботом Hobot (450 грн/доба або 750 грн у комбо з пароочисником). "
            "Дай 3 практичні секрети ідеального скла без розводів: 1) перший сухий прохід чистими серветками знімає вуличний пил, щоб не розмазувати бруд; "
            "2) другий прохід із кількома пшиками німецького спиртового концентрату Kärcher RM 503 полірує скло до дзеркального блиску; "
            "3) обов'язково фіксувати страхувальний трос у кімнаті та запускати робота за плюсової температури без дощу."
        ),
    },
    {
        "id": 6,
        "image": "6_dryer_dripod.jpg",
        "badge": "СУХИЙ ДИВАН ЗА 2–3 ГОДИНИ",
        "headline": "Боїтеся прати диван восени чи взимку через сирість у кімнаті?",
        "tip": "Турбосушка Dri-Eaz Dri-Pod (США) видуває вологу на 360° — спати на сухому можна вже ввечері",
        "cta_button": "Комбо з сушкою: 850 грн/доба  •  098 521 02 04",
        "topic_prompt": (
            "Тема: Швидке сушіння диванів, матраців і килимів у прохолодну вологу прикарпатську погоду. "
            "Дай 3 правила сушіння після хімчистки: 1) під час фінального проходу екстрактором зробити 2–3 повільні сухі вакуумні протяжки без подачі води, щоб зібрати максимум вологи; "
            "2) не ставити впритул побутові спіральні обігрівачі (вони пересушують тканину плямами, залишаючи поролон сирим усередині); "
            "3) увімкнути американську купольну турбосушку Dri-Eaz Dri-Pod (+250 грн у КОМБО №1 з пилососом = 850 грн/доба), яка потоком повітря 360° висушує диван чи матрац за 2–3 години."
        ),
    },
    {
        "id": 7,
        "image": "7_car_kwazar.jpg",
        "badge": "ДЕТЕЙЛІНГ АВТО ТА ВЕЛЮРУ",
        "headline": "Хімчистка салону авто й делікатних тканин густою піною!",
        "tip": "Піногенератор Kwazar + Koch Chemie Pol Star (pH 7) чистять сидіння без перезволоження",
        "cta_button": "Набір для авто: від 700 грн  •  098 521 02 04",
        "topic_prompt": (
            "Тема: Самостійна хімчистка тканинних сидінь авто, підлокітників та делікатних диванів без перезволоження поролону й електропідігріву. "
            "Дай 3 професійні поради дітейлінгу: 1) спершу ретельно пропилососити сухий пісок зі швів сидінь; "
            "2) нанести густу напівсуху піну нейтрального засобу Koch Chemie Pol Star (pH 7) через ручний піногенератор Kwazar Venus Pro+ (+100 грн до пилососа) і м'яко пройтися щіткою; "
            "3) одразу зібрати піну з брудом вузькою насадкою екстрактора Puzzi 8/1 (і пам'ятати, що стелю авто мочити екстрактором не можна, щоб не провисла підкладка)."
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


def sanitize_privacy(text: str) -> str:
    """Гарантує 0% згадок про ФОП, прізвище чи назви вулиць навіть якщо AI спробує щось додати від себе."""
    cleaned = text
    patterns = [
        r"\(\s*ФОП[^)]*\)",
        r"\bФОП\s+[А-ЯІЇЄҐа-яіїєґA-Za-z'\-]+(?:\s+[А-ЯІЇЄҐа-яіїєґA-Za-z'\-]+){0,2}",
        r"\bвул\.\s*[А-ЯІЇЄҐа-яіїєґ0-9,\-\s]+",
        r"\bвулиц[яіюею]\s+[А-ЯІЇЄҐ][А-ЯІЇЄҐа-яіїєґ'\-]+(?:\s+[0-9А-ЯІЇЄҐа-яіїєґ/\-]+)?",
    ]
    for pat in patterns:
        cleaned = re.sub(pat, "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def get_drohobych_weather() -> dict:
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=49.35&longitude=23.50"
        "&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
        "&timezone=Europe%2FKyiv"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ProCleanDrohobych/4.2"})
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
            "context_str": "Зараз у Дрогобичі прохолодна пора, підвищена вологість повітря.",
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
        "Ранковий час — жителі Дрогобича п'ють каву і планують справи на день."
        if is_morning else
        "Вечірній час — люди вдома відпочивають і планують завтрашній день або вихідні."
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
            upcoming_notes.append(f"СЬОГОДНІ СВЯТО: {h_title}!")
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
        req = urllib.request.Request(list_url, headers={"User-Agent": "ProCleanAutoPoster/4.2"})
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
        return sanitize_privacy(build_dynamic_fallback_caption(topic, weather, cal))

    prompt = f"""{BUSINESS_CONTEXT}

КОНТЕКСТ СЬОГОДНІШНЬОГО ДНЯ У ДРОГОБИЧІ:
1. ДАТА: {cal['calendar_summary']}
2. ПОГОДА ЗАРАЗ У ДРОГОБИЧІ: {weather['context_str']}
3. ТЕМА ДОПИСУ: {topic['topic_prompt']}

Напиши живий, лаконічний і практичний допис українською мовою для жителів Дрогобича, Трускавця, Борислава, Стебника та Східниці у Facebook та Instagram.

СУВОРІ ВИМОГИ ДО СТРУКТУРИ ТА СТИЛЮ:
- ПЕРШИЙ АБЗАЦ (лише 1–2 короткі речення!): почни одразу з гострого життєвого питання по темі та вплети сьогоднішню погоду у Дрогобичі ({weather['temp']}°C, {weather['short_desc'].lower()}) або день тижня ({cal['weekday_name']}), щоб читач одразу натиснув «Більше». Не пиши довгих вступів на 5–6 рядків.
- ДРУГИЙ БЛОК: дай рівно 3 конкретні практичні дії (1., 2., 3.) без води й без загальних фраз на кшталт «використовуйте професійний підхід». Перевір узгодження відмінків і числа української мови (пиши «гарячий фен або праску», а не «гарячий фени»).
- ТРЕТІЙ АБЗАЦ (2–3 речення): чітко запропонуй рішення від сервісу PRO-CLEAN RENT з реальними цінами у гривнях.
- СУВОРА ЗАБОРОНА: категорично НЕ згадуй слово «ФОП», жодних прізвищ, імен майстрів або назв вулиць чи адрес. Пиши від імені команди PRO-CLEAN RENT («у сервісі PRO-CLEAN RENT», «ми підкажемо», «самовивіз у Дрогобичі або доставка під двері»).
- ФІНАЛЬНИЙ БЛОК КОНТАКТІВ:
  Тел / Viber / Telegram / WhatsApp: 098 521 02 04
  Онлайн-калькулятор та бронювання: https://proclean-drohobych.netlify.app
- У кінці один рядок хештегів: #дрогобич #трускавець #борислав #стебник #східниця #хімчисткадрогобич #орендадрогобич #procleanrent
- НЕ використовуй символи ** або ###, поверни лише готовий чистий текст поста (900–1250 символів).
"""

    for model_name in discover_gemini_models(gemini_api_key):
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1150},
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
                text = sanitize_privacy(text)
                if len(text) > 180:
                    print(f"Унікальний живий текст згенеровано через {model_name}!")
                    return text
        except Exception as exc:
            print(f"Модель {model_name} недоступна ({exc}), пробуємо наступну...")

    return sanitize_privacy(build_dynamic_fallback_caption(topic, weather, cal))


def build_dynamic_fallback_caption(topic: dict, weather: dict, cal: dict) -> str:
    sign = "+" if weather["temp"] > 0 else ""
    return (
        f"{topic['headline']} За вікном у Дрогобичі {sign}{weather['temp']}°C ({weather['short_desc'].lower()}), "
        f"{cal['weekday_name']} — саме час легко навести ідеальну чистоту вдома.\n\n"
        f"Швидка пам'ятка:\n"
        f"{topic['tip']}\n\n"
        f"У сервісі PRO-CLEAN RENT доступні подобово (самовивіз у Дрогобичі або доставка під двері):\n"
        f"• Kärcher Puzzi 8/1 — 600 грн/доба (порція хімії RM 760 у комплекті)\n"
        f"• Santoemma Sabrina SW15 — 650 грн/доба\n"
        f"• КОМБО «Пилосос + Турбосушка Dri-Eaz Dri-Pod» — 850 грн/доба (сухий диван за 2–3 год)\n"
        f"• Пароочисник Kärcher SC 2 — 400 грн | Робот для вікон Hobot — 450 грн | Озонатор YATO — 350 грн\n\n"
        f"Тел / Viber / Telegram / WhatsApp: 098 521 02 04\n"
        f"Онлайн-калькулятор та набори хімії: https://proclean-drohobych.netlify.app\n\n"
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
            req = urllib.request.Request(raw_url, headers={"User-Agent": "ProCleanAutoPoster/4.2"})
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
    """Опущений градієнт (починається з y=795), щоб центральна зона та деталі на дивані/матраці залишались на 100% світлими."""
    w, h = base_rgb.size
    grad_col = Image.new("RGBA", (1, h), (0, 0, 0, 0))
    px = grad_col.load()

    top_end = 135
    bot_start = 795

    for y in range(h):
        alpha = 0
        if y < top_end:
            t = 1.0 - (y / top_end)
            alpha = int(115 * (t ** 1.6))
        elif y >= bot_start:
            t = (y - bot_start) / max(1, (h - 1 - bot_start))
            smooth = 0.5 - 0.5 * math.cos(math.pi * min(1.0, t))
            alpha = int(244 * (smooth ** 0.62))
        px[0, y] = (10, 15, 28, alpha)

    overlay = grad_col.resize((w, h), Image.Resampling.BILINEAR)
    composed = Image.alpha_composite(base_rgb.convert("RGBA"), overlay)
    return composed.convert("RGB")


def render_clean_photo(topic: dict, out_path: Path) -> Path:
    """Режим 100% живого інтер'єрного фото без жодних плашок і написів (чергується через раз проти банерної сліпоти)."""
    src_path = resolve_topic_image(topic)
    print(f"Фото-основа (режим ЧИСТЕ ФОТО без написів): {src_path.name}")
    raw_img = ImageOps.exif_transpose(Image.open(src_path)).convert("RGB")
    fitted = ImageOps.fit(
        raw_img,
        (CARD_W, CARD_H),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fitted.save(str(out_path), format="JPEG", quality=95, subsampling=0, optimize=True)
    size_kb = out_path.stat().st_size // 1024
    print(f"Збережено чисте HD-фото {CARD_W}x{CARD_H}: {out_path} ({size_kb} KB)")
    return out_path


def render_editorial_card(topic: dict, weather: dict, cal: dict, out_path: Path) -> Path:
    src_path = resolve_topic_image(topic)
    print(f"Фото-основа (режим КАРТКА З ЛАЙФХАКОМ): {src_path.name}")

    raw_img = ImageOps.exif_transpose(Image.open(src_path)).convert("RGB")
    fitted = ImageOps.fit(
        raw_img,
        (CARD_W, CARD_H),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.52),
    )
    canvas = apply_editorial_vignette(fitted).convert("RGBA")
    ui_layer = Image.new("RGBA", (CARD_W, CARD_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ui_layer)

    # 1. Верхня компактна плашка погоди й дати
    top_text = strip_non_bmp(f"{weather['badge_str']}  •  {cal['short_countdown_badge']}")
    top_lines, f_top = wrap_and_fit_text(draw, top_text, MAX_TEXT_W - 44, max_lines=1, start_size=22, min_size=16, bold=True)
    top_line = top_lines[0] if top_lines else top_text
    tw, th = measure_text(draw, top_line, f_top)
    pill_w = min(MAX_TEXT_W, tw + 44)
    pill_h = th + 22
    pill_x1 = SAFE_PAD_X
    pill_y1 = 38
    draw.rounded_rectangle(
        [pill_x1, pill_y1, pill_x1 + pill_w, pill_y1 + pill_h],
        radius=pill_h // 2,
        fill=(15, 23, 42, 182),
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

    # Підготовка елементів нижнього блоку (компактніше по висоті + великий шрифт на кнопці!)
    footer_geo = "Дрогобич • Трускавець • Борислав • Стебник  |  proclean-drohobych.netlify.app"
    geo_lines, f_geo = wrap_and_fit_text(draw, footer_geo, MAX_TEXT_W, max_lines=1, start_size=20, min_size=15, bold=False)
    geo_line = geo_lines[0]

    cta_str = strip_non_bmp(topic["cta_button"])
    price_lines, f_price = wrap_and_fit_text(draw, cta_str, MAX_TEXT_W - 48, max_lines=1, start_size=31, min_size=22, bold=True)
    price_line = price_lines[0]

    tip_lines, f_tip = wrap_and_fit_text(draw, topic["tip"], MAX_TEXT_W, max_lines=2, start_size=23, min_size=18, bold=False)
    head_lines, f_head = wrap_and_fit_text(draw, topic["headline"], MAX_TEXT_W, max_lines=2, start_size=42, min_size=30, bold=True)

    badge_str = strip_non_bmp(topic["badge"]).upper()
    badge_lines, f_badge = wrap_and_fit_text(draw, badge_str, MAX_TEXT_W - 40, max_lines=1, start_size=19, min_size=15, bold=True)
    badge_line = badge_lines[0]

    y_cursor = CARD_H - 38

    # 5) Нижній рядок міст та сайту
    g_bbox = draw.textbbox((0, 0), geo_line, font=f_geo)
    gh = g_bbox[3] - g_bbox[1]
    y_cursor -= gh
    draw.text((SAFE_PAD_X - g_bbox[0], y_cursor - g_bbox[1]), geo_line, font=f_geo, fill=(186, 230, 253, 235))
    y_cursor -= 16

    # 4) Акцентна жовта кнопка з крупним шрифтом ціни та телефону
    p_bbox = draw.textbbox((0, 0), price_line, font=f_price)
    pw, ph = p_bbox[2] - p_bbox[0], p_bbox[3] - p_bbox[1]
    bar_h = ph + 32
    bar_w = MAX_TEXT_W
    y_cursor -= bar_h
    draw.rounded_rectangle(
        [SAFE_PAD_X, y_cursor, SAFE_PAD_X + bar_w, y_cursor + bar_h],
        radius=16,
        fill=(250, 204, 21, 250),
    )
    draw.text(
        (SAFE_PAD_X + (bar_w - pw) // 2 - p_bbox[0], y_cursor + (bar_h - ph) // 2 - p_bbox[1]),
        price_line,
        font=f_price,
        fill=(15, 23, 42, 255),
    )
    y_cursor -= 18

    # 3) Рядки короткого лайфхаку
    for line in reversed(tip_lines):
        lb = draw.textbbox((0, 0), line, font=f_tip)
        lh = lb[3] - lb[1]
        y_cursor -= lh
        draw.text((SAFE_PAD_X - lb[0], y_cursor - lb[1]), line, font=f_tip, fill=(226, 232, 240, 248))
        y_cursor -= 8
    y_cursor -= 10

    # 2) Заголовок
    for line in reversed(head_lines):
        hb = draw.textbbox((0, 0), line, font=f_head)
        lh = hb[3] - hb[1]
        y_cursor -= lh
        draw.text((SAFE_PAD_X - hb[0] + 2, y_cursor - hb[1] + 2), line, font=f_head, fill=(0, 0, 0, 150))
        draw.text((SAFE_PAD_X - hb[0], y_cursor - hb[1]), line, font=f_head, fill=(255, 255, 255, 255))
        y_cursor -= 10
    y_cursor -= 10

    # 1) Контрастний бейдж рубрики
    bb = draw.textbbox((0, 0), badge_line, font=f_badge)
    bw, bh = bb[2] - bb[0], bb[3] - bb[1]
    b_pad_x, b_pad_y = 16, 8
    b_h = bh + b_pad_y * 2
    b_w = min(MAX_TEXT_W, bw + b_pad_x * 2)
    y_cursor -= b_h
    draw.rounded_rectangle(
        [SAFE_PAD_X, y_cursor, SAFE_PAD_X + b_w, y_cursor + b_h],
        radius=10,
        fill=(15, 23, 42, 222),
        outline=(56, 189, 248, 215),
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
        print("Оновлене зображення збережено в GitHub репозиторії! Чекаємо 5 с на оновлення CDN...")
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
    post_seq = day_of_year * 2 + slot

    idx_str = os.environ.get("FORCE_TOPIC_INDEX", "").strip()
    if idx_str.isdigit():
        val = int(idx_str)
        topic_index = (val - 1) if 1 <= val <= len(TOPICS) else (val % len(TOPICS))
    else:
        topic_index = post_seq % len(TOPICS)

    topic = TOPICS[topic_index % len(TOPICS)]

    # Чергування 1 через 1: картка з лайфхаком <-> чисте інтер'єрне фото без тексту
    # (якщо користувач вручну ввів номер теми FORCE_TOPIC_INDEX для перевірки картки — рендеримо картку, або за FORCE_RENDER_MODE)
    mode_override = os.environ.get("FORCE_RENDER_MODE", "").strip().lower()
    if mode_override in ("clean", "photo", "pure"):
        use_clean_photo = True
    elif mode_override in ("card", "text"):
        use_clean_photo = False
    elif idx_str.isdigit():
        use_clean_photo = False
    else:
        use_clean_photo = ((day_of_year + slot) % 2 == 1)

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

    mode_label = "ЧИСТЕ ФОТО БЕЗ ТЕКСТУ" if use_clean_photo else "КАРТКА З ЛАЙФХАКОМ"
    print(f"=== Рубрика #{topic['id']} [{mode_label}]: {topic['headline']} ({now_kyiv.strftime('%Y-%m-%d %H:%M')} Kyiv) ===")
    print(f"Погода: {weather['context_str']}")
    print(f"Календар: {cal['calendar_summary']}")

    if use_clean_photo:
        card_path = render_clean_photo(topic, OUTPUT_CARD_PATH)
    else:
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
