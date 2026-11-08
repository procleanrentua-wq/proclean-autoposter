#!/usr/bin/env python3
"""
PRO-CLEAN RENT v3.1 — Smart Weather, Holiday Countdown, Stain Lifehacks & Hybrid B+C Card Generator.
Працює двічі на день (08:45 та 19:15 за Києвом) через GitHub Actions:

1. Перевіряє РЕАЛЬНУ погоду в м. Дрогобич просто зараз через безкоштовний Open-Meteo API
   (температура, сніг, дощ, мряка, туман, ясно, вологість).
2. Визначає сьогоднішній день тижня, українські свята, традиції та точний відлік днів до подій
   (Святий Миколай 6 грудня, Різдво 25 грудня, Новий рік 1 січня, Великдень тощо).
3. Чергує 8 живих рубрик (включно з 4 глибокими рубриками лайфхаків виведення плям із тканини:
   кава/вино, дитячі несподіванки/сеча тварин, жир/шоколад/віск, чорнило/фломастери/кров).
4. Генерує ідеальну чітку картку 1080x1080 (Суміш Варіантів Б і В — жодних кривих ШІ-кімнат!):
   - Для фону завантажує чистий макро-кадр реальної текстури (тканина дивана, краплі дощу або
     сніжинки на вікні — без жодних меблів чи фальшивих апаратів!) або використовує преміум-банер.
   - Зверху накладає живу шапку з сьогоднішньою погодою в Дрогобичі та відліком днів до свята,
     великий заголовок теми, фото реальної техніки PRO-CLEAN RENT та жовту плашку ціни!
"""

import datetime
import io
import json
import os
import random
import re
import subprocess
import sys
import textwrap
import time
import urllib.parse
import urllib.request

from PIL import Image, ImageDraw, ImageFilter, ImageFont

BUSINESS_CONTEXT = """
Ти — досвідчений локальний SMM-експерт та майстер хімчистки сервісу PRO-CLEAN RENT у м. Дрогобич (ФОП Собко Андрій Тарасович).
Географія: Дрогобич, Трускавець, Борислав, Стебник, Східниця та села Дрогобицької ОТГ.
Контакти: Тел / Viber / Telegram / WhatsApp: 098-521-02-04.
Сайт з онлайн-калькулятором: https://proclean-drohobych.netlify.app

Наші послуги та точні ціни:
1) Подобова оренда професійної техніки для самостійної хімчистки (1 порція хімії Kärcher RM 760 у ПОДАРУНОК до кожного пилососа!):
   - Миючий пилосос Kärcher Puzzi 8/1 (Німеччина, ручна насадка для меблів + висока штанга для килимів) — 600 грн/доба
   - Потужний італійський екстрактор Santoemma Sabrina SW15 (глибока витяжка з товстих матраців і килимів) — 650 грн/доба
   - Пароочисник Kärcher SC 2 EasyFix (кухня, жир, духовка, плитка, шви, санвузол без хімії) — 400 грн/доба
   - Робот для миття вікон Hobot (концентрат RM 503 та серветки у комплекті) — 450 грн/доба
   - Американська турбосушка Dri-Eaz Dri-Pod (сушить диван чи матрац за 2–3 години замість 24 годин у сиру погоду!) — 350 грн/доба
   - Професійний озонатор повітря YATO YT-73350 (знищує запахи диму, тварин, сечі, плісняви, вогкості) — 350 грн/доба
   - Додаткова порція преміум-хімії — 90 грн.
   - Вигідні КОМБО на добу:
     * КОМБО №1 «Сухий диван за 2 години» (Пилосос + Турбосушка + хімія) = 850 грн (з Puzzi) / 900 грн (з Sabrina)
     * КОМБО №2 «Меблі + Кухня та Ванна» (Пилосос + Пароочисник SC 2 + хімія) = 850 грн / 900 грн
     * КОМБО №3 «Анти-Запах» (Пилосос + Озонатор YATO + хімія) = 850 грн / 900 грн
     * КОМБО №4 «Ідеальні вікна та шви» (Робот Hobot + Пароочисник SC 2) = 750 грн
     * КОМБО №5 «Генеральне прибирання All-in-One» (Екстрактор + Пароочисник + Hobot + Турбосушка) = 1450 грн / 1500 грн
   - Доставка в 1 сторону: Самовивіз (Дрогобич) — 0 грн; по Дрогобичу — 150 грн; Трускавець / Стебник — 200 грн; Борислав — 250 грн; Східниця — 350 грн.

2) Виїзна преміум-хімчистка м'яких меблів, матраців, килимів і салонів авто нашим майстром:
   - 5-ступенева технологія США та Німеччини: ензимний преспрей Chemspec PreKleen (розщеплює білок, піт, їжу, сечу), екстракція Kärcher RM 760 / Koch Chemie Pol Star, точкові плямовивідники RM 769 / Fleckenwasser та обов'язкова нейтралізація кислотним ополіскувачем Chemspec All Fiber Textile Rinse (100% безпечно для немовлят, алергіків і тварин).
"""

RUBRICS = [
    {
        "mode": "BC",
        "main_photo": "post_instagram_hubka_vs_karcher.jpg",
        "mini_badge_img": "card_puzzi.jpg",
        "macro_bg_prompt": "Extreme macro close-up photography of beige linen sofa upholstery fabric weave texture in natural window light, shallow depth of field, zero objects, no rooms, no text",
        "badge": "ЛАЙФХАК ПРОТИ ПЛЯМ #1",
        "headline": "Пляма від кави, вина чи соку на дивані: що НЕ можна робити?",
        "subline": "Губка з Ванішем заганяє бруд у поролон, а екстрактор Puzzi 8/1 витягує його з глибини!",
        "price_tag": "Оренда Kärcher Puzzi 8/1 + хімія RM 760: 600 грн/доба",
        "topic_prompt": "Рубрика «Лайфхаки з виведення плям із тканини»: свіжа або застаріла пляма від кави, чаю, червоного вина чи узвару на світлому дивані. Поясни покроково: 1) чому не можна терти губкою з Фейрі чи Ванішем по колу (бо рідина з цукром і танінами йде вглиб поролону і після висихання дає жовтий ореол); 2) як правильно промокнути сухою серветкою з країв до центру; 3) як за допомогою екстрактора Kärcher Puzzi 8/1 та лужного розчину RM 760 витягнути пляму з глибини 7 см назавжди.",
    },
    {
        "mode": "BC",
        "main_photo": "post_facebook_soba_kit_karcher.jpg",
        "mini_badge_img": "card_sabrina.jpg",
        "macro_bg_prompt": "Macro close-up photograph of soft grey velour sofa fabric texture in warm daylight, clean textile fibers, no furniture, no rooms, no text",
        "badge": "ЛАЙФХАК ПРОТИ ПЛЯМ #2",
        "headline": "Дитячі несподіванки, молоко або сеча кота й собаки на матраці",
        "subline": "Чому оцет і сода лише консервують запах у поролоні та як працюють ензими Chemspec?",
        "price_tag": "Виїзна хімчистка Chemspec або Оренда екстрактора: від 600 грн",
        "topic_prompt": "Рубрика «Лайфхаки з виведення складних білкових плям»: дитяча сеча, пролите молоко, дитяче харчування або мітки домашніх улюбленців на матраці чи дивані. Розповідай живо і професійно: чому замивання водою, оцтом чи содою вступає в реакцію з кристалами сечової кислоти та закріплює запах у поролоні, який повертається у вологу погоду. Дай правильний лайфхак першої допомоги і поясни, як працює наш американський ензимний преспрей Chemspec PreKleen + кислотний ополіскувач All Fiber Textile Rinse та екстрактор Santoemma Sabrina SW15.",
    },
    {
        "mode": "BC",
        "main_photo": "olx_4_zhyve_foto_tekhniky.jpg",
        "mini_badge_img": "card_dripod.jpg",
        "macro_bg_prompt": "Macro close-up of window glass with autumn raindrops and blurred outdoor trees, natural daylight, no rooms, no text",
        "badge": "ПОГОДНИЙ КОНТРОЛЬ ДРОГОБИЧ",
        "headline": "Як висушити диван чи матрац за 2–3 години у прохолодну погоду?",
        "subline": "Американська турбосушка Dri-Eaz Dri-Pod видуває вологу на 360° без сирісті!",
        "price_tag": "КОМБО №1 «Пилосос + Турбосушка + Хімія» = 850 грн/доба",
        "topic_prompt": "Тема: Проблема сушіння меблів і килимів у поточну погоду в Дрогобичі. Прив'яжи текст до сьогоднішньої погоди за вікном і температури! Поясни, чому в прохолодну чи вологу погоду випраний диван без обдуву сохне 15–24 години і може затхнутися, а наша американська підлогова турбосушка Dri-Eaz Dri-Pod у КОМБО №1 з пилососом за 850 грн робить диван повністю сухим за 2–3 години.",
    },
    {
        "mode": "BC",
        "main_photo": "olx_3_do_pislya_khimchystka.jpg",
        "mini_badge_img": "card_sc2.jpg",
        "macro_bg_prompt": "Extreme close-up macro of white ceramic kitchen tiles with clean grout lines and water droplets, natural daylight, no rooms, no text",
        "badge": "ЛАЙФХАК ПРОТИ ПЛЯМ #3",
        "headline": "Жирні плями від їжі, шоколад, віск і пластилін на оббивці дивана",
        "subline": "Як термоудар парою 130°C + точковий плямовивідник RM 769 рятують тканину",
        "price_tag": "Пароочисник SC 2: 400 грн | КОМБО з пилососом: 850 грн/доба",
        "topic_prompt": "Рубрика «Лайфхаки з виведення плям із тканини»: жирні плями від їжі (піца, соус, олія, шоколад), а також віск від свічок чи пластилін на килимі та дивані. Дай практичну пораду господиням (як прибрати віск через паперову серветку праскою або льодом, чому жир не бере звичайна холодна вода) і розкажи, як комбінація пароочисника Kärcher SC 2 EasyFix та миючого пилососа (КОМБО №2 за 850 грн) або наш професійний плямовивідник Kärcher RM 769 розчиняють жир без сліду.",
    },
    {
        "mode": "BC",
        "main_photo": "hero_fleet_studio.jpg",
        "mini_badge_img": "card_hobot.jpg",
        "macro_bg_prompt": "Close-up macro of crystal clear glass window pane with soft bokeh city lights and trees outside, natural daylight, no text",
        "badge": "ЧИСТІ ВІКНА ДО СВЯТ",
        "headline": "Ідеально чисті вікна та панорамні балкони без ризику і розводів!",
        "subline": "Робот-мийник вікон Hobot + спиртовий концентрат Kärcher RM 503 у комплекті",
        "price_tag": "Оренда робота Hobot: 450 грн/доба | КОМБО з пароочисником: 750 грн",
        "topic_prompt": "Тема: Чисті вікна та панорамні балкони у Дрогобичі, Трускавці та Бориславі з оглядом сьогоднішньої погоди за вікном та підготовки до найближчих українських свят. Чому мити вікна руками на висоті в холодну чи вітряну погоду небезпечно і важко, і як робот Hobot за 450 грн/доба зі спеціальним спиртовим концентратом Kärcher RM 503 натирає скло до блиску без розводів, поки ви п'єте гарячий чай.",
    },
    {
        "mode": "BC",
        "main_photo": "before_after_clean.jpg",
        "mini_badge_img": "card_sabrina.jpg",
        "macro_bg_prompt": "Extreme macro close-up of clean plush carpet fibers in natural daylight, soft texture, zero furniture, no text",
        "badge": "ЛАЙФХАК ПРОТИ ПЛЯМ #4",
        "headline": "Фломастери, ручка, слайм чи кров на дивані: головне правило хімії",
        "subline": "Чому кров і білок миють ТІЛЬКИ крижаною водою та як витягнути чорнило з тканини?",
        "price_tag": "Оренда екстрактора: від 600 грн | Виїзд майстра у Дрогобичі та районі",
        "topic_prompt": "Рубрика «Лайфхаки з виведення плям із тканини»: кулькова ручка, дитячі фломастери, слайм та краплі крові на дивані чи матраці. Поясни золоте правило хімії: чому кров і будь-який білок у жодному разі не можна мити гарячою водою (білок миттєво згортається і навічно в'їдається у волокна — тільки крижана вода + ензими!), як спиртовий розчин піднімає чорнило, але чому без вакуумного промивання екстрактором пляма лише розпливається ширше.",
    },
    {
        "mode": "BC",
        "main_photo": "olx_5_ozonator_yato.jpg",
        "mini_badge_img": "card_yato.jpg",
        "macro_bg_prompt": "Close-up macro of fresh morning dew drops on green pine needles in crisp Carpathian air, natural bokeh, no text",
        "badge": "СВІЖЕ ПОВІТРЯ В ОСЕЛІ ТА АВТО",
        "headline": "Як за 1 годину назавжди прибрати запах диму, вогкості чи тварин?",
        "subline": "Професійний озонатор повітря YATO YT-73350 (20 000 мг/год) стерилізує повітря!",
        "price_tag": "Оренда озонатора YATO: 350 грн/доба | КОМБО з пилососом: 850 грн",
        "topic_prompt": "Тема: Професійне озонування квартири, будинку або салону авто озонатором YATO YT-73350 та підготовка салону машини й оселі до сезону й свят. Поясни, як газ озон (O3) проникає у всі щілини, вентиляцію та тканину, руйнуючи молекули запаху сигарет, старого житла, горілої їжі чи котячих міток за 40–60 хвилин.",
    },
    {
        "mode": "BC",
        "main_photo": "hero_fleet_studio.jpg",
        "mini_badge_img": "card_puzzi.jpg",
        "macro_bg_prompt": "Extreme macro close-up of clean knitted wool blanket texture by a sunny window, cozy home atmosphere, no furniture, no text",
        "badge": "PRO-CLEAN RENT • ВЕСЬ ПАРК ТЕХНІКИ",
        "headline": "Як за 600 грн/доба перемити всі дивани, матраци і килими в домі?",
        "subline": "Kärcher Puzzi • Sabrina SW15 • Hobot • SC 2 • Сушка Dri-Pod • Доставка під двері!",
        "price_tag": "Оренда від 350–600 грн/доба • Комбо All-in-One: 1450 грн",
        "topic_prompt": "Тема: Як за 1 добу влаштувати повне перезавантаження чистоти у своїй квартирі чи будинку в Дрогобичі, Трускавці, Бориславі, Стебнику чи Східниці перед святами або вихідними. Порівняй економію: один виклик клінінгу на великий кутовий диван, 2 матраци і килим коштує 3500–4500 грн, а оренда миючого пилососа з хімією в подарунок — лише 600 грн на цілу добу (або КОМБО All-in-One за 1450 грн).",
    },
]

WMO_WEATHER_UA = {
    0: ("Ясно і сонячно", "сонячна погода без опадів"),
    1: ("Переважно ясно", "легка хмарність з проясненнями"),
    2: ("Мінлива хмарність", "хмарна з проясненнями погода"),
    3: ("Похмуро", "щільно затягнуте хмарами небо"),
    45: ("Туман і вогкість", "густий осінньо-зимовий туман і висока вологість повітря"),
    48: ("Паморозь і туман", "туман із памороззю та сирістю"),
    51: ("Легка мряка", "дрібна мряка і вологе повітря"),
    53: ("Мряка і сльота", "мряка, мокрий асфальт і сирість"),
    55: ("Сильна мряка", "густа холодна мряка і болото під ногами"),
    61: ("Невеликий дощ", "невеликий дощ і мокрі вулиці"),
    63: ("Дощ і калюжі", "справжній дощ, калюжі та сльота на вулицях"),
    65: ("Сильна злива", "рясна злива і мокрі дороги"),
    66: ("Крижаний дощ", "крижаний дощ і ожеледиця"),
    67: ("Сильний крижаний дощ", "сильний крижаний дощ і слизькі тротуари"),
    71: ("Невеликий сніг", "перший легкий сніжок, що кружляє у повітрі"),
    73: ("Йде сніг", "справжній сніг у Дрогобичі та білі дахи"),
    75: ("Сильний снігопад", "густий снігопад і кучугури снігу"),
    77: ("Снігова крупа", "колюча снігова крупа і морозне повітря"),
    80: ("Зливовий дощ", "короткочасні дощі та калюжі"),
    81: ("Сильний дощ", "рясний дощ та болото у дворах"),
    85: ("Снігопад", "лапатий сніг і зимова атмосфера"),
    86: ("Сильна хуртовина", "заметіль і багато снігу на вулицях"),
}


def strip_non_bmp(text: str) -> str:
    """Прибирає кольорові емодзі для малювання на зображенні через стандартні TTF-шрифти (щоб не було квадратиків)."""
    return re.sub(r"[^\u0000-\u27BF]", "", text).strip()


def get_drohobych_weather() -> dict:
    """Отримує реальну погоду в м. Дрогобич просто зараз через безкоштовний Open-Meteo API."""
    url = (
        "https://api.open-meteo.com/v1/forecast"
        "?latitude=49.35&longitude=23.50"
        "&current=temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m"
        "&timezone=Europe%2FKyiv"
    )
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ProCleanDrohobych/3.1"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))["current"]
            temp = round(float(data.get("temperature_2m", 5.0)))
            humidity = int(data.get("relative_humidity_2m", 80))
            wcode = int(data.get("weather_code", 3))
            wind = round(float(data.get("wind_speed_10m", 3.0)))
            short_desc, detail_desc = WMO_WEATHER_UA.get(wcode, ("Прохолодно", "типова прикарпатська погода"))
            sign = "+" if temp > 0 else ""
            badge_str = f"Дрогобич зараз: {sign}{temp}°C ({short_desc})"
            context_str = (
                f"Зараз у Дрогобичі та Трускавці реальна температура {sign}{temp}°C, {detail_desc}, "
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
            "badge_str": "Дрогобич: +4°C (Прохолодно)",
            "context_str": "Зараз у Дрогобичі прохолодна пора, висока вологість на вулиці.",
        }


def get_ukrainian_calendar_context(now_kyiv: datetime.datetime) -> dict:
    """Визначає сьогоднішній день тижня, українські свята, традиції та точний відлік днів до подій."""
    today = now_kyiv.date()
    year = today.year

    weekdays_ua = [
        "понеділок", "вівторок", "середа", "четвер", "п'ятниця", "субота", "неділя"
    ]
    months_genitive = {
        1: "січня", 2: "лютого", 3: "березня", 4: "квітня",
        5: "травня", 6: "червня", 7: "липня", 8: "серпня",
        9: "вересня", 10: "жовтня", 11: "листопада", 12: "грудня"
    }
    weekday_name = weekdays_ua[today.weekday()]
    date_human = f"{today.day} {months_genitive[today.month]}"
    is_morning = now_kyiv.hour < 14
    time_of_day_hint = (
        "Ранковий кавовий час (08:45 ранку) — люди у Дрогобичі п'ють ранкову каву, збираються у справах і планують свій день."
        if is_morning else
        "Вечірній прайм-тайм (19:15 вечора) — люди повернулися з роботи додому, відпочивають на дивані й планують справи на завтра."
    )

    holidays = [
        (datetime.date(year, 11, 21), "День Гідності та Свободи (Михайла за старим стилем, початок активної підготовки оселі до зими)"),
        (datetime.date(year, 11, 30), "День Святого Андрія Первозванного (українські вечорниці та початок зимового циклу свят)"),
        (datetime.date(year, 12, 6), "День Святого Миколая та День ЗСУ (час, коли Миколай кладе подарунки під ідеально чисті подушки!)"),
        (datetime.date(year, 12, 24), "Святвечір перед Різдвом Христовим (традиція зустрічати Різдво у бездоганно чистій хаті, де вимиті всі кутки, вікна, килими й меблі)"),
        (datetime.date(year, 12, 25), "Різдво Христове (коляда, прийом гостей та родини за святковим столом)"),
        (datetime.date(year, 1, 1), "Новий рік"),
        (datetime.date(year + 1, 1, 1), "Новий рік"),
        (datetime.date(year, 1, 6), "Водохреща (Богоявлення — час освіжити меблі після святкових застіль!)"),
        (datetime.date(year + 1, 1, 6), "Водохреща (Богоявлення)"),
        (datetime.date(year, 2, 14), "День Святого Валентина"),
        (datetime.date(year + 1, 2, 14), "День Святого Валентина"),
        (datetime.date(year, 3, 8), "Весняне оновлення дому"),
        (datetime.date(year, 5, 1), "Великоднє генеральне прибирання"),
        (datetime.date(year, 8, 24), "День Незалежності України"),
        (datetime.date(year, 10, 1), "Покрова Пресвятої Богородиці та День захисників України"),
    ]

    upcoming_notes = []
    short_countdown_badge = f"{date_human} ({weekday_name})"

    for h_date, h_title in holidays:
        delta = (h_date - today).days
        if delta == 0:
            upcoming_notes.append(f"СЬОГОДНІ В УКРАЇНІ СВЯТО: {h_title}! Обов'язково щиро привітай дрогобичан і трускавчан у першому абзаці!")
            short_countdown_badge = f"Сьогодні: {h_title.split('(')[0].strip()}!"
        elif 1 <= delta <= 45:
            upcoming_notes.append(f"До події «{h_title}» залишилося рівно {delta} дн.")

    st_nicholas = datetime.date(year, 12, 6)
    christmas = datetime.date(year, 12, 25)
    new_year = datetime.date(year + 1, 1, 1)

    if 1 <= (st_nicholas - today).days <= 32:
        d_nik = (st_nicholas - today).days
        short_countdown_badge = f"До Миколая: {d_nik} дн. ({date_human})"
    elif 1 <= (christmas - today).days <= 25:
        d_chr = (christmas - today).days
        short_countdown_badge = f"До Різдва: {d_chr} дн. ({date_human})"
    elif 1 <= (new_year - today).days <= 30:
        d_ny = (new_year - today).days
        short_countdown_badge = f"До Нового року: {d_ny} дн.!"

    weekday_advice = ""
    if today.weekday() in (3, 4):
        weekday_advice = "Сьогодні кінець робочого тижня — нагадай, що на суботу та неділю техніку розбирають найшвидше, тому краще забронювати на вихідні вже зараз."
    elif today.weekday() in (5, 6):
        weekday_advice = "Сьогодні вихідний день — ідеальний час приділити 2 години дому або замовити виїзд майстра на наступний тиждень."

    calendar_summary = (
        f"Сьогодні {date_human} {year} року, день тижня: {weekday_name}. {time_of_day_hint} "
        f"Календар свят та відлік днів: {'; '.join(upcoming_notes[:3]) if upcoming_notes else 'сезон домашнього затишку'}. "
        f"{weekday_advice}"
    )
    return {
        "date_human": date_human,
        "weekday_name": weekday_name,
        "short_countdown_badge": short_countdown_badge,
        "calendar_summary": calendar_summary,
    }


def generate_live_caption_with_gemini(
    rubric: dict, weather: dict, cal: dict, gemini_api_key: str
) -> str:
    """Генерує 100% унікальний живий пост з урахуванням погоди в Дрогобичі, календаря свят і лайфхаку."""
    if not gemini_api_key:
        return build_dynamic_fallback_caption(rubric, weather, cal)

    prompt = f"""{BUSINESS_CONTEXT}

РЕАЛЬНИЙ КОНТЕКСТ СЬОГОДНІШНЬОГО ДНЯ У ДРОГОБИЧІ (ОБОВ'ЯЗКОВО ВПЛЕТИ ЦЕ В ТЕКСТ!):
1. ДАТА І СВЯТА: {cal['calendar_summary']}
2. ПОГОДА ПРОСТО ЗАРАЗ У ДРОГОБИЧІ: {weather['context_str']}
3. СЬОГОДНІШНЯ ТЕМА / РУБРИКА: {rubric['topic_prompt']}

Твоє завдання — написати живий, теплий, розумний, абсолютно нешаблонний допис для наших сусідів у Facebook та Instagram (Дрогобич, Трускавець, Борислав, Стебник, Східниця).

СУВОРІ ВИМОГИ ДО ТЕКСТУ:
- У перших 1–2 реченнях природно й живо згадай сьогоднішню погоду у Дрогобичі (температуру {weather['temp']}°C, стан неба: {weather['short_desc']}) ТА/АБО скільки днів залишилося до найближчого свята ({cal['short_countdown_badge']}) чи який сьогодні день тижня ({cal['weekday_name']}). Пиши так, ніби ти сам щойно виглянув у вікно в Дрогобичі!
- Далі детально й цікаво розкрий тему сьогоднішньої рубрики (особливо якщо це лайфхак із виведення плям — дай реальну практичну користь, щоб люди зберегли собі пост у закладки!).
- Природно підведи до рішення від PRO-CLEAN RENT з точними цінами (наприклад, оренда Kärcher Puzzi 8/1 — 600 грн/доба з хімією у комплекті, Sabrina SW15 — 650 грн, КОМБО з турбосушкою чи пароочисником — 850 грн, або виїзд нашого майстра).
- Обов'язково вкажи клікабельне посилання на наш сайт із калькулятором: https://proclean-drohobych.netlify.app
- Обов'язково вкажи телефон / Viber / Telegram: 098-521-02-04.
- У кінці додай 6–8 локальних хештегів (#дрогобич #трускавець #борислав #стебник #східниця #хімчисткадрогобич #орендадрогобич #procleanrent).
- НЕ використовуй зірочки (** або *), НЕ пиши слово "Заголовок:", поверни тільки чистий готовий текст допису з гарними абзацами та емодзі.
"""

    models = ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"]
    for model_name in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.85,
                "maxOutputTokens": 1200,
            },
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=35) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
                text = text.replace("**", "")
                if len(text) > 150:
                    print(f"Унікальний текст успішно згенеровано через {model_name}!")
                    return text
        except Exception as exc:
            print(f"Модель {model_name} повернула помилку ({exc}), пробуємо наступну...")

    return build_dynamic_fallback_caption(rubric, weather, cal)


def build_dynamic_fallback_caption(rubric: dict, weather: dict, cal: dict) -> str:
    sign = "+" if weather["temp"] > 0 else ""
    return (
        f"📍 {weather['badge_str']} | 🗓 {cal['short_countdown_badge']}\n\n"
        f"Друзі, сьогодні у нас в Дрогобичі {sign}{weather['temp']}°C ({weather['short_desc']}), "
        f"а на календарі вже {cal['date_human']} ({cal['weekday_name']})! Саме час подбати про чистоту й затишок в оселі перед святами.\n\n"
        f"💡 {rubric['badge']}: {rubric['headline']}\n"
        f"{rubric['subline']}\n\n"
        f"Чому жителі Дрогобича, Трускавця, Борислава та Стебника обирають PRO-CLEAN RENT?\n"
        f"✅ {rubric['price_tag']}\n"
        f"✅ Миючий пилосос Kärcher Puzzi 8/1 — 600 грн/доба (порція хімії RM 760 вже у комплекті!)\n"
        f"✅ Італійський екстрактор Santoemma Sabrina SW15 — 650 грн/доба\n"
        f"✅ КОМБО «Пилосос + Американська турбосушка Dri-Pod» (сухий диван за 2–3 год у будь-яку сирість!) — 850 грн/доба\n"
        f"✅ Пароочисник Kärcher SC 2 — 400 грн | Робот для вікон Hobot — 450 грн | Озонатор YATO — 350 грн\n"
        f"✅ Виїзна 5-ступенева хімчистка майстром преміум-хімією Chemspec (США) з безпечним ополіскувачем All Fiber Rinse!\n\n"
        f"🧮 Порахуйте вартість оренди або доставки за 30 секунд у нашому онлайн-калькуляторі:\n"
        f"👉 https://proclean-drohobych.netlify.app\n\n"
        f"📞 Бронювання та консультація (Тел / Viber / Telegram): 098-521-02-04\n\n"
        f"#дрогобич #трускавець #борислав #стебник #східниця #хімчисткадрогобич #орендадрогобич #procleanrent"
    )


def load_font(size: int, bold: bool = True) -> ImageFont.FreeTypeFont:
    candidates = [
        "/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf" if bold else "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def fetch_macro_texture_bg(macro_prompt: str) -> Image.Image | None:
    """Завантажує чистий макро-фон фактури (тканина, краплі на склі) без жодних кімнат і без апаратів."""
    seed = random.randint(1000, 999999)
    encoded = urllib.parse.quote(macro_prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width=1080&height=1080&seed={seed}&model=flux-realism&nologo=true"
    req = urllib.request.Request(url, headers={"User-Agent": "ProCleanAutoPoster/3.1"})
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read()
            if len(raw) > 15000:
                im = Image.open(io.BytesIO(raw)).convert("RGB")
                return im.resize((1080, 1080), Image.Resampling.LANCZOS)
    except Exception as exc:
        print(f"Макро-фон недоступний ({exc}) — використовуємо преміальний темно-синій фон.")
    return None


def build_hybrid_card_image(rubric: dict, weather: dict, cal: dict, out_path: str) -> None:
    """
    Генерує 100% чітку, реалістичну і живу картку 1080x1080 (Суміш Варіантів Б і В):
    - Жодних кривих ШІ-кімнат чи вигаданих пилососів!
    - Використовує ВИКЛЮЧНО високої роздільної здатності фото техніки та інфографіки у центрі
      + живу верхню панель із погодою в Дрогобичі та зворотним відліком до свята!
    """
    W, H = 1080, 1080
    canvas = Image.new("RGB", (W, H), (15, 23, 42))

    if rubric.get("macro_bg_prompt"):
        bg_im = fetch_macro_texture_bg(rubric["macro_bg_prompt"])
        if bg_im is not None:
            bg_blurred = bg_im.filter(ImageFilter.GaussianBlur(radius=4))
            dark_overlay = Image.new("RGB", (W, H), (12, 19, 36))
            canvas = Image.blend(bg_blurred, dark_overlay, alpha=0.72)

    draw = ImageDraw.Draw(canvas)

    f_weather = load_font(22, bold=True)
    f_badge = load_font(24, bold=True)
    f_head = load_font(38, bold=True)
    f_sub = load_font(24, bold=False)
    f_price = load_font(31, bold=True)
    f_footer = load_font(23, bold=True)

    # 1. Верхня жива панель: Погода в Дрогобичі + Відлік до свята (без емодзі, які дають квадратики)
    draw.rounded_rectangle([32, 24, 1048, 88], radius=16, fill=(30, 41, 59), outline=(56, 189, 248), width=2)
    top_bar_text = strip_non_bmp(f"{weather['badge_str']}   |   {cal['short_countdown_badge']}")
    draw.text((52, 43), top_bar_text[:66], font=f_weather, fill=(125, 211, 252))

    # 2. Жовта плашка рубрики
    badge_clean = strip_non_bmp(rubric["badge"])
    draw.rounded_rectangle([32, 104, 520, 152], radius=12, fill=(250, 204, 21))
    draw.text((50, 114), badge_clean, font=f_badge, fill=(15, 23, 42))

    # 3. Заголовок теми (повністю вміщається в 2 рядки без обрізання!)
    wrapped_head = textwrap.wrap(strip_non_bmp(rubric["headline"]), width=42)[:2]
    y_cursor = 166
    for line in wrapped_head:
        draw.text((36, y_cursor), line, font=f_head, fill=(255, 255, 255))
        y_cursor += 46

    # 4. Центральна вітрина з високої якості фото з images/assets/
    card_top = 274
    card_bottom = 788
    draw.rounded_rectangle(
        [32, card_top, 1048, card_bottom],
        radius=28,
        fill=(255, 255, 255),
        outline=(250, 204, 21),
        width=4,
    )

    main_photo_path = os.path.join("images", "assets", rubric["main_photo"])
    if not os.path.exists(main_photo_path):
        main_photo_path = os.path.join("images", rubric["main_photo"])

    if os.path.exists(main_photo_path):
        im_main = Image.open(main_photo_path).convert("RGB")
        im_main.thumbnail((996, 494), Image.Resampling.LANCZOS)
        paste_x = 32 + (1016 - im_main.width) // 2
        paste_y = card_top + (514 - im_main.height) // 2
        canvas.paste(im_main, (paste_x, paste_y))

    # Маленький бейдж реального апарата у правому нижньому кутку вітрини
    mini_name = rubric.get("mini_badge_img")
    mini_path = os.path.join("images", "assets", mini_name) if mini_name else None
    if mini_path and os.path.exists(mini_path):
        draw.rounded_rectangle([810, card_bottom - 155, 1032, card_bottom - 14], radius=18, fill=(255, 255, 255), outline=(56, 189, 248), width=3)
        im_mini = Image.open(mini_path).convert("RGB")
        im_mini.thumbnail((196, 120), Image.Resampling.LANCZOS)
        canvas.paste(im_mini, (810 + (222 - im_mini.width) // 2, (card_bottom - 155) + (141 - im_mini.height) // 2))

    # 5. Підзаголовок-вигода
    wrapped_sub = textwrap.wrap(strip_non_bmp(rubric["subline"]), width=62)[:2]
    y_sub = 802
    for line in wrapped_sub:
        draw.text((38, y_sub), line, font=f_sub, fill=(226, 232, 240))
        y_sub += 32

    # 6. Яскрава жовта плашка з ціною
    draw.rounded_rectangle([32, 878, 1048, 962], radius=18, fill=(250, 204, 21))
    price_clean = strip_non_bmp(rubric["price_tag"])
    draw.text((54, 903), f">> {price_clean}", font=f_price, fill=(15, 23, 42))

    # 7. Футер із контактами та географією
    draw.text(
        (38, 982),
        "Тел / Viber / TG: 098-521-02-04  •  Дрогобич • Трускавець • Борислав • Стебник",
        font=f_footer,
        fill=(56, 189, 248),
    )
    draw.text(
        (38, 1020),
        "Онлайн-калькулятор: proclean-drohobych.netlify.app",
        font=f_footer,
        fill=(248, 250, 252),
    )

    canvas.save(out_path, quality=94)
    print(f"Згенеровано нову фірмову картку з реальною технікою та погодою: {out_path}")


def commit_and_push_generated_image(rel_image_path: str) -> bool:
    try:
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", rel_image_path], check=True)
        subprocess.run(["git", "commit", "-m", f"Update daily smart card: {rel_image_path}"], check=False)
        subprocess.run(["git", "push"], check=True)
        print("Свіжу картку дня збережено в GitHub репозиторії!")
        return True
    except Exception as exc:
        print(f"Не вдалося запушити картинку в git ({exc}).")
        return False


def publish_to_facebook_page(page_id: str, access_token: str, image_url: str, caption: str) -> dict:
    endpoint = f"https://graph.facebook.com/v21.0/{page_id}/photos"
    form_data = urllib.parse.urlencode({
        "url": image_url,
        "caption": caption,
        "access_token": access_token,
    }).encode("utf-8")
    req = urllib.request.Request(endpoint, data=form_data, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def publish_to_instagram_business(ig_user_id: str, access_token: str, image_url: str, caption: str) -> dict:
    create_url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media"
    create_data = urllib.parse.urlencode({
        "image_url": image_url,
        "caption": caption,
        "access_token": access_token,
    }).encode("utf-8")
    req1 = urllib.request.Request(create_url, data=create_data, method="POST")
    with urllib.request.urlopen(req1, timeout=30) as resp1:
        container_info = json.loads(resp1.read().decode("utf-8"))

    creation_id = container_info["id"]
    print(f"Instagram медіа-контейнер створено: {creation_id}. Чекаємо 10 секунд на обробку...")
    time.sleep(10)

    publish_url = f"https://graph.facebook.com/v21.0/{ig_user_id}/media_publish"
    publish_data = urllib.parse.urlencode({
        "creation_id": creation_id,
        "access_token": access_token,
    }).encode("utf-8")
    req2 = urllib.request.Request(publish_url, data=publish_data, method="POST")
    with urllib.request.urlopen(req2, timeout=30) as resp2:
        return json.loads(resp2.read().decode("utf-8"))


def main():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    now_kyiv = now_utc + datetime.timedelta(hours=2)

    day_of_year = now_kyiv.timetuple().tm_yday
    slot = 0 if now_kyiv.hour < 14 else 1
    idx_str = os.environ.get("FORCE_TOPIC_INDEX", "").strip()
    rubric_index = int(idx_str) if idx_str.isdigit() else ((day_of_year * 2 + slot) % len(RUBRICS))
    rubric = RUBRICS[rubric_index % len(RUBRICS)]

    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    fb_page_id = os.environ.get("FB_PAGE_ID", "").strip()
    ig_user_id = os.environ.get("IG_USER_ID", "").strip()
    meta_token = os.environ.get("META_PAGE_ACCESS_TOKEN", "").strip()
    github_repo = os.environ.get("GITHUB_REPOSITORY", "procleanrentua-wq/proclean-autoposter").strip()
    branch = os.environ.get("GITHUB_REF_NAME", "main").strip()

    weather = get_drohobych_weather()
    cal = get_ukrainian_calendar_context(now_kyiv)

    print(f"=== Рубрика #{rubric_index + 1} ({rubric['badge']}): {rubric['headline']} ===")
    print(f"Погода в Дрогобичі: {weather['context_str']}")
    print(f"Календар: {cal['calendar_summary']}")

    caption = generate_live_caption_with_gemini(rubric, weather, cal, gemini_key)
    print("\n--- ЗГЕНЕРОВАНИЙ ЖИВИЙ ТЕКСТ ПОСТА ---\n")
    print(caption)
    print("\n--------------------------------------\n")

    os.makedirs("images", exist_ok=True)
    generated_rel_path = "images/daily_smart_card.jpg"
    build_hybrid_card_image(rubric, weather, cal, generated_rel_path)

    cache_bust = int(time.time())
    if os.environ.get("GITHUB_ACTIONS") == "true" and commit_and_push_generated_image(generated_rel_path):
        image_url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/{generated_rel_path}?v={cache_bust}"
    else:
        image_url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/images/01_park_tekhniky.jpg"

    print(f"URL зображення для публікації: {image_url}")

    if not meta_token:
        print("Тестовий запуск (DRY RUN): META_PAGE_ACCESS_TOKEN не задано.")
        sys.exit(0)

    if fb_page_id:
        print(f"Публікуємо на Facebook Page ({fb_page_id})...")
        fb_res = publish_to_facebook_page(fb_page_id, meta_token, image_url, caption)
        print("Успішно опубліковано у Facebook! ID:", fb_res.get("id"))

    if ig_user_id:
        print(f"Публікуємо в Instagram Business ({ig_user_id})...")
        ig_res = publish_to_instagram_business(ig_user_id, meta_token, image_url, caption)
        print("Успішно опубліковано в Instagram! ID:", ig_res.get("id"))


if __name__ == "__main__":
    main()
