#!/usr/bin/env python3
"""
PRO-CLEAN RENT — Повністю автоматичний генератор текстів І фотореалістичних зображень
для Facebook та Instagram (GitHub Actions + Google Gemini / Imagen API + Meta Graph API).

Особливість:
1. На кожному запуску скрипт спочатку генерує НОВИЙ текст допису І НОВИЙ промпт для реального
   живого фото на смартфон (RAW smartphone photography, без «пластикового» ШІ-глянцю).
2. Далі скрипт генерує НОВУ фотореалістичну картинку через Google Gemini Image API (Imagen 3 /
   Gemini Flash Image) або Pollinations Flux-Realism, зберігає її в images/generated_latest.jpg,
   комітить у ваш GitHub-репозиторій і публікує цей свіжий файл у Facebook та Instagram!
"""

import base64
import datetime
import json
import os
import random
import subprocess
import sys
import time
import urllib.parse
import urllib.request

BUSINESS_CONTEXT = """
Ти — професійний SMM-маркетолог сервісу PRO-CLEAN RENT (ФОП Собко Андрій Тарасович).
Локація: м. Дрогобич, Трускавець, Борислав, Стебник, Східниця та район.
Телефон / Viber / Telegram / WhatsApp: 098-521-02-04.
Вебсайт з онлайн-калькулятором: https://proclean-drohobych.netlify.app

Два напрямки роботи:
1) Подобова оренда професійної клінінгової техніки додому (1 стартова порція хімії Kärcher RM 760 у комплекті!):
   - Миючий пилосос Kärcher Puzzi 8/1 (Німеччина, ручна насадка + висока штанга для килимів) — 600 грн/доба
   - Потужний італійський екстрактор Santoemma Sabrina SW15 (+ висока штанга для килимів) — 650 грн/доба
   - Пароочисник Kärcher SC 2 EasyFix (кухня, жир, шви, плитка, санвузол без хімії) — 400 грн/доба
   - Робот для миття вікон Hobot (концентрат RM 503 та серветки у комплекті) — 450 грн/доба
   - Американська турбосушка Dri-Eaz Dri-Pod (сушить диван чи килим за 2–3 години замість 15 годин!) — 350 грн/доба
   - Професійний озонатор повітря YATO YT-73350 (знищує запахи диму, тварин, сечі, плісняви) — 350 грн/доба
   - Додаткова порція хімії — 90 грн.
   - Комбо-пакети на добу зі знижкою:
     * КОМБО №1 «Сухий диван за 2 години» (Пилосос + Турбосушка + хімія) = 850 грн (з Puzzi) / 900 грн (з Sabrina)
     * КОМБО №2 «Меблі + Кухня та Ванна» (Пилосос + Пароочисник SC 2 + хімія) = 850 грн / 900 грн
     * КОМБО №3 «Анти-Запах» (Пилосос + Озонатор YATO + хімія) = 850 грн / 900 грн
     * КОМБО №4 «Ідеальні вікна та шви» (Робот Hobot + Пароочисник SC 2) = 750 грн
     * КОМБО №5 «Генеральне прибирання All-in-One» (Екстрактор + Пароочисник + Робот Hobot + Турбосушка) = 1450 грн / 1500 грн
   - Тарифи доставки в 1 сторону: Самовивіз у Дрогобичі — 0 грн; Дрогобич — 150 грн; Трускавець та Стебник — 200 грн; Борислав — 250 грн; Східниця — 350 грн.

2) Виїзна професійна хімчистка м'яких меблів, матраців, килимів та авто нашим майстром під ключ:
   - Працюємо італійським екстрактором Santoemma Sabrina SW15, пароочисником Kärcher та турбосушкою Dri-Pod.
   - 5-ступенева преміум-хімія США та Німеччини: ензимний преспрей Chemspec PreKleen, основна екстракція RM 760 / Koch Chemie Pol Star, точкові плямовивідники RM 769 / Fleckenwasser та обов'язкове фінальне промивання кислотним ополіскувачем-нейтралізатором Chemspec All Fiber Textile Rinse (100% безпечно для немовлят, алергіків і тварин).
"""

# Теми та реалістичні сценарії зйомки (як живе фото на iPhone у реальній українській квартирі, без ШІ-глянцю)
SCENARIOS = [
    {
        "theme": "Чому оренда миючого пилососа Kärcher Puzzi 8/1 за 600 грн/доба вигідніша за виклик клінінгу на 1 диван, бо за добу можна перемити всі меблі, матраци і килими в домі.",
        "photo_scene": "Authentic unretouched smartphone photo taken on iPhone 15 inside a real everyday Ukrainian apartment living room in natural daylight from a window: a compact grey-and-yellow professional spray extraction vacuum cleaner stands on a laminate floor next to a normal beige fabric corner sofa, half of the sofa seat cushion is visibly damp and freshly cleaned while the other half has realistic everyday coffee and kids smudges, natural room clutter in background, 28mm mobile lens, natural sensor grain, realistic shadows, zero CGI gloss, no text, no watermarks.",
        "fallback_img": "08_zhyve_foto_tekhniky.jpg",
    },
    {
        "theme": "Проблема сушіння дивана восени та взимку: як американська підлогова турбосушка Dri-Eaz Dri-Pod (КОМБО з пилососом за 850 грн) висушує диван чи матрац за 2–3 години замість доби.",
        "photo_scene": "Candid real-life iPhone photo inside a modest cozy apartment bedroom: a compact round blue floor turbo dryer pod sits on the floor blowing air onto a freshly cleaned white orthopedic mattress on a bed frame, natural indoor lighting mixed with overcast daylight from a window with curtains, realistic fabric texture, unposed documentary photography, slight natural smartphone grain, no text, no labels.",
        "fallback_img": "03_kombo_ta_dostavka.jpg",
    },
    {
        "theme": "Виїзна хімчистка диванів та килимів майстром з італійським екстрактором Santoemma Sabrina SW15 та 5-ступеневою американською хімією Chemspec з кислотним ополіскувачем All Fiber Rinse.",
        "photo_scene": "Close-up real-world documentary photograph taken on a smartphone: a technician's hand in a black nitrile glove holding a transparent plastic upholstery extraction nozzle pressed against a textured grey sofa cushion, pulling dark dirty brownish water through the clear nozzle tube, a blue professional extractor hose visible, natural indoor lighting, sharp fabric weave detail, authentic unstaged working moment, no text, no watermarks.",
        "fallback_img": "04_do_pislya_khimchystka.jpg",
    },
    {
        "theme": "Хімчистка в домах із собаками, котами та маленькими дітьми: як ензимний преспрей Chemspec PreKleen розщеплює запахи сечі, поту та сліди лап.",
        "photo_scene": "Real candid smartphone photo of a cute domestic cat and a golden retriever dog sitting on a clean rug next to a light-grey sofa in a lived-in Ukrainian flat, natural daylight from a balcony door, warm realistic colors, unretouched everyday home atmosphere, shot on iPhone 14, natural depth of field, no AI plastic look, no text.",
        "fallback_img": "05_simya_sobaka_kit.jpg",
    },
    {
        "theme": "Миття вікон та панорамних балконів без ризику: оренда робота для миття вікон Hobot за 450 грн/доба з концентратом Kärcher RM 503 у комплекті.",
        "photo_scene": "Unstaged real smartphone photo taken from inside an apartment balcony: a white square robotic window cleaner attached by vacuum suction to a large glass window pane, half of the glass is crystal clear showing a blurry courtyard trees outside and half has realistic rain dust spots, natural daylight, authentic home window frame, shot on mobile camera, no text, no watermarks.",
        "fallback_img": "09_hobot_vikna.jpg",
    },
    {
        "theme": "Ідеальна чистота на кухні та у ванній без хімії: пароочисник Kärcher SC 2 EasyFix (400 грн/доба або Комбо з пилососом за 850 грн) проти жиру на витяжці, духовці та чорних швів плитки.",
        "photo_scene": "Real-life candid iPhone photo inside a home kitchen: a person's hand holding a steam cleaner nozzle spraying a visible puff of hot white steam onto ceramic wall tile grout lines behind a stove, realistic water droplets condensing on the tiles, natural indoor kitchen lighting, documentary smartphone photography, no text, no watermarks.",
        "fallback_img": "10_paroochysnyk_sc2.jpg",
    },
    {
        "theme": "Хімчистка салону авто власноруч за 600 грн/доба або з озонатором повітря YATO проти запаху тютюну, вогкості та пального.",
        "photo_scene": "Candid real-life smartphone photo taken outdoors in a driveway on an overcast day: an open car door showing cloth car seats being cleaned with a clear handheld upholstery extraction nozzle, half of the car seat fabric is dark and wet while dirt is extracted, a grey-and-yellow vacuum hose leading out of the car door, authentic everyday car interior, shot on iPhone, no text, no watermarks.",
        "fallback_img": "07_ozonator_yato.jpg",
    },
]


def generate_caption_and_scene_with_gemini(scenario: dict, gemini_api_key: str) -> tuple[str, str]:
    """Генерує свіжий текст поста ТА уточнений реалістичний фото-промпт через Gemini."""
    if not gemini_api_key:
        return fallback_caption(scenario["theme"]), scenario["photo_scene"]

    prompt = f"""{BUSINESS_CONTEXT}

Сьогоднішня тема: {scenario['theme']}
Базовий опис фото-сцени: {scenario['photo_scene']}

Виконай 2 завдання і поверни результат СТРОГО у форматі JSON з двома ключами ("caption" та "image_prompt"):
1) "caption": Напиши живий, переконливий, корисний та продаючий допис українською мовою для Facebook та Instagram на сьогоднішню тему.
   - Почни з сильного життєвого хука або запитання.
   - Наведи конкретні цифри цін та вигоду для жителів Дрогобича, Трускавця, Борислава, Стебника, Східниці.
   - Обов'язково вкажи сайт з калькулятором: https://proclean-drohobych.netlify.app та телефон / Viber / Telegram: 098-521-02-04.
   - Додай 6–8 локальних хештегів у кінці. Без зірочок (**).
2) "image_prompt": Напиши англійською мовою детальний промпт для генерації ультра-реалістичної живої фотографії на смартфон (iPhone 15 Pro candid unretouched documentary photo, natural indoor lighting, slight sensor grain, realistic lived-in Ukrainian apartment, zero CGI look, no text, no watermarks), яка ідеально ілюструє цей допис.
"""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.8,
            "responseMimeType": "application/json",
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
            raw_json = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = json.loads(raw_json)
            caption = parsed.get("caption", "").replace("**", "").strip()
            img_prompt = parsed.get("image_prompt", scenario["photo_scene"]).strip()
            if caption:
                return caption, img_prompt
    except Exception as exc:
        print(f"Помилка генерації JSON у Gemini ({exc}) — пробуємо звичайний текстовий режим.")

    return fallback_caption(scenario["theme"]), scenario["photo_scene"]


def generate_realistic_image(image_prompt: str, gemini_api_key: str, out_path: str) -> bool:
    """
    Генерує нову фотореалістичну картинку (без ефекту штучного ШІ) і зберігає у out_path.
    Спочатку пробує офіційний Google Imagen 3 / Gemini Image API за тим самим GEMINI_API_KEY,
    а якщо ключ не має доступу до Imagen — автоматично генерує через безкоштовний Flux-Realism.
    """
    full_prompt = (
        f"{image_prompt} "
        "Shot on iPhone 15 Pro, 28mm f/1.8 lens, raw unedited smartphone photo, natural window light, "
        "authentic everyday textures, subtle sensor noise, documentary realism, NOT 3D render, NOT CGI, "
        "no text, no letters, no watermarks."
    )

    # Спроба 1: Google Imagen 3 через Gemini API
    if gemini_api_key:
        imagen_url = f"https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-002:predict?key={gemini_api_key}"
        payload = {
            "instances": [{"prompt": full_prompt}],
            "parameters": {"sampleCount": 1, "aspectRatio": "4:3"},
        }
        req = urllib.request.Request(
            imagen_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                b64_img = data["predictions"][0]["bytesBase64Encoded"]
                with open(out_path, "wb") as f:
                    f.write(base64.b64decode(b64_img))
                print("Нове фото успішно згенеровано через Google Imagen 3 API!")
                return True
        except Exception as exc:
            print(f"Google Imagen 3 недоступний на цьому тарифному плані ({exc}) — перемикаємось на Flux-Realism...")

    # Спроба 2: Безкоштовний генератор Flux-Realism (Pollinations AI, модель flux-realism)
    seed = random.randint(10000, 9999999)
    encoded_prompt = urllib.parse.quote(full_prompt)
    flux_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1080&height=1350&seed={seed}&model=flux-realism&nologo=true"
    req_flux = urllib.request.Request(
        flux_url,
        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) ProCleanAutoPoster/2.0"},
    )
    try:
        with urllib.request.urlopen(req_flux, timeout=60) as resp:
            img_bytes = resp.read()
            if len(img_bytes) > 15000:
                with open(out_path, "wb") as f:
                    f.write(img_bytes)
                print("Нове фотореалістичне зображення успішно згенеровано через Flux-Realism!")
                return True
    except Exception as exc:
        print(f"Помилка генерації Flux-Realism ({exc}).")

    return False


def commit_and_push_generated_image(rel_image_path: str) -> bool:
    """Комітить та пушить щойно згенеровану картинку у репозиторій GitHub, щоб Meta отримала публічний URL."""
    try:
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=True)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=True)
        subprocess.run(["git", "add", rel_image_path], check=True)
        diff = subprocess.run(["git", " status", "--porcelain", rel_image_path], capture_output=True, text=True)
        subprocess.run(["git", "commit", "-m", f"Auto-generate realistic photo: {rel_image_path}"], check=False)
        subprocess.run(["git", "push"], check=True)
        print("Згенероване фото збережено в GitHub репозиторії!")
        return True
    except Exception as exc:
        print(f"Не вдалося запушити картинку в git ({exc}) — використовуємо базове фото з репозиторію.")
        return False


def fallback_caption(topic_theme: str) -> str:
    return (
        f"🔥 {topic_theme}\n\n"
        "Обирайте професійний догляд за меблями, килимами та вікнами з PRO-CLEAN RENT!\n\n"
        "🔹 Оренда миючого пилососа Kärcher Puzzi 8/1 — 600 грн/доба (+ порція хімії RM 760 у комплекті!)\n"
        "🔹 Потужний італійський екстрактор Santoemma Sabrina SW15 — 650 грн/доба\n"
        "🔹 Турбосушка Dri-Eaz Dri-Pod (сухий диван за 2–3 год!) — 350 грн/доба\n"
        "🔹 Пароочисник Kärcher SC 2 — 400 грн/доба | Робот для вікон Hobot — 450 грн/доба\n"
        "🔹 Озонатор повітря YATO — 350 грн/доба\n"
        "🔥 Комбо «Пилосос + Турбосушка» або «Пилосос + Пароочисник» — всього від 850 грн/доба!\n\n"
        "🧮 Порахуйте точну вартість оренди або доставки у своє місто в онлайн-калькуляторі:\n"
        "👉 https://proclean-drohobych.netlify.app\n\n"
        "📍 Працюємо: Дрогобич, Трускавець, Борислав, Стебник, Східниця.\n"
        "📞 Бронювання (Тел / Viber / Telegram): 098-521-02-04\n\n"
        "#дрогобич #трускавець #борислав #стебник #східниця #хімчисткадрогобич #орендадрогобич #procleanrent"
    )


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
    day_of_year = datetime.datetime.now(datetime.timezone.utc).timetuple().tm_yday
    idx_str = os.environ.get("FORCE_TOPIC_INDEX", "").strip()
    scenario_index = int(idx_str) if idx_str.isdigit() else (day_of_year % len(SCENARIOS))
    scenario = SCENARIOS[scenario_index % len(SCENARIOS)]

    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    fb_page_id = os.environ.get("FB_PAGE_ID", "").strip()
    ig_user_id = os.environ.get("IG_USER_ID", "").strip()
    meta_token = os.environ.get("META_PAGE_ACCESS_TOKEN", "").strip()
    github_repo = os.environ.get("GITHUB_REPOSITORY", "procleanrentua-wq/proclean-autoposter").strip()
    branch = os.environ.get("GITHUB_REF_NAME", "main").strip()

    print(f"=== Сценарій #{scenario_index + 1}: {scenario['theme']} ===")
    caption, refined_photo_prompt = generate_caption_and_scene_with_gemini(scenario, gemini_key)

    print("\n--- ЗГЕНЕРОВАНИЙ ТЕКСТ ПОСТА ---\n")
    print(caption)
    print("\n--- ПРОМПТ ДЛЯ РЕАЛІСТИЧНОГО ФОТО ---\n")
    print(refined_photo_prompt)
    print("\n-------------------------------------\n")

    os.makedirs("images", exist_ok=True)
    generated_rel_path = "images/generated_latest.jpg"
    cache_bust = int(time.time())

    if generate_realistic_image(refined_photo_prompt, gemini_key, generated_rel_path) and os.environ.get("GITHUB_ACTIONS") == "true":
        if commit_and_push_generated_image(generated_rel_path):
            image_url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/{generated_rel_path}?v={cache_bust}"
        else:
            image_url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/images/{scenario['fallback_img']}"
    else:
        image_url = f"https://raw.githubusercontent.com/{github_repo}/{branch}/images/{scenario['fallback_img']}"

    print(f"URL зображення для публікації: {image_url}")

    if not meta_token:
        print("Тестовий запуск (DRY RUN): додайте META_PAGE_ACCESS_TOKEN у GitHub Secrets для автопублікації.")
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
