import os, sys, json, time, requests, re
import config

RELATIONSHIP_CURRICULUM = [['Die Geheimnisse emotionaler Bindung', 'Unsere Bindungsstile und tiefen Ängste verstehen und sicher lieben lernen'], ['Die Kunst, zu sprechen ohne zu verletzen', 'Bedürfnisse zärtlich und klar ausdrücken, ohne Vorwurf und Verteidigung'], ['Gesunde Grenzen setzen lernen', 'Wohlwollend Nein sagen, um die Harmonie der Partnerschaft und das Selbstwertgefühl zu bewahren'], ['Angst vor Ablehnung und Verlassenwerden heilen', 'Innere Sicherheit wiederfinden und unerschütterliches Vertrauen in die Verbindung aufbauen'], ['Die 5 Sprachen der Liebe im Alltag', 'Die tiefen emotionalen Bedürfnisse deines Partners entschlüsseln und die Liebe täglich nähren'], ['Verletzlichkeit: die unsichtbare Stärke der Partnerschaft', 'Warum es der einzige wahre Schlüssel zur Intimität ist, sich authentisch und unvollkommen zu zeigen'], ['Konflikte entschärfen ohne Groll', 'Meinungsverschiedenheiten in Chancen für Annäherung und gegenseitiges Verständnis verwandeln'], ['Aus emotionaler Abhängigkeit herausfinden', 'Emotionale Eigenständigkeit kultivieren und zu zweit voll aufblühen'], ['Aktives Zuhören und die Kraft der Stille', 'Hören, was das Herz des anderen hinter Müdigkeit und Alltagsworten flüstert'], ['Vertrauen nach einer Verletzung wieder aufbauen', 'Der geduldige Weg der Wiedergutmachung, Wahrheit und des gemeinsamen Verzeihens']]

DEFAULT_5_ACTS = [['Akt 1: Die Bestandsaufnahme des Herzens', 'Warme Einführung und Eintauchen in die Realität der Beziehungsherausforderung'], ['Akt 2: Die unbewussten Wurzeln', 'Psychologische Erkundung von Ängsten, Kindheitswunden und unseren Schutzreflexen'], ['Akt 3: Praktische Schlüssel & beruhigende Worte', 'Transformierende Sätze, wohlwollende Haltungen und konstruktive Alltagsdialoge'], ['Akt 4: Durch emotionale Stürme gehen', 'Wut und Rückzug bewältigen und Spannungsmomente ohne Panik überwinden'], ['Akt 5: Die Herzensaufgabe & täglicher Segen', 'Wohlwollende Selbstreflexion, Verbindungsritual für die Woche und Hoffnungsbotschaft']]

def load_history_topics() -> list:
    """Reads all past published topics from published_videos.json and history.json to ensure no repeats."""
    past = []
    for fname in ["published_videos.json", "history.json"]:
        fpath = os.path.join(config.BASE_DIR, fname)
        if os.path.exists(fpath):
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict) and item.get("topic"):
                                t = item["topic"].strip()
                                if t not in past:
                                    past.append(t)
            except Exception:
                pass
    return past

def generate_dynamic_topic_ai(past_topics: list, ep_num: int = 1) -> dict:
    """Fragt die Pollinations-KI mit Verlauf vergangener Themen nach einem brandneuen, sich nicht wiederholenden deutschen Beziehungsthema."""
    key = config.POLLINATIONS_API_KEY
    if not key:
        return None

    past_sample = past_topics[-30:] if len(past_topics) > 30 else past_topics
    prompt = (
        f"Du bist die ausführende Produzentin und Konzepterin des deutschen Podcasts '{config.CHANNEL_NAME}'.\n"
        f"Slogan: {config.TAGLINE}\n"
        f"Format: Intimer Solo-Podcast mit {config.HOST1_NAME}, einer wohlwollenden Psychologin und Vertrauten.\n"
        f"Thematik: Menschliche Beziehungen, Liebespsychologie, Bindung, Kommunikation, Zärtlichkeit, Resilienz der Partnerschaft.\n"
        f"Sprachregel: ALLES muss in elegantem, natürlichem und herzlichem Deutsch verfasst sein.\n\n"
        f"Bereits behandelte Episoden (NICHT WIEDERHOLEN):\n"
        + json.dumps(past_sample, indent=2, ensure_ascii=False) + "\n\n"
        f"Generiere EIN NEUES, fesselndes und bereicherndes Episodenthema für Episode #{ep_num}.\n\n"
        f"AUSGABEFORMAT: Gib AUSSCHLIESSLICH ein gültiges JSON-Objekt zurück (kein Markdown, keine Einleitung):\n"
        "{\n"
        f'  "id": "ep_{ep_num}",\n'
        '  "topic": "Fesselnder deutscher Titel (z. B.: Vergeben lernen ohne sich zu vergessen)",\n'
        '  "focus": "Ein Satz: Was die Zuhörer über ihre Bindungen verstehen und verwandeln werden",\n'
        '  "thumbnail_title_1": "ERSTE WÖRTER (MAX. 16 ZEICHEN)",\n'
        '  "thumbnail_title_2": "ZWEITE WÖRTER (MAX. 16 ZEICHEN)",\n'
        '  "thumbnail_hook": "Packender Aufhänger (z. B.: Partnerschaft sanft retten)",\n'
        '  "acts": [\n'
        '    ["Akt 1: Titel", "Beschreibung des Fokus..."],\n'
        '    ["Akt 2: Titel", "Beschreibung des Fokus..."],\n'
        '    ["Akt 3: Titel", "Beschreibung des Fokus..."],\n'
        '    ["Akt 4: Titel", "Beschreibung des Fokus..."],\n'
        '    ["Akt 5: Titel", "Beschreibung des Fokus..."]\n'
        '  ]\n'
        "}" 
    )

    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": config.POLLINATIONS_MODEL,
        "messages": [
            {"role": "system", "content": "Du bist ein erstklassiger Podcast-Produzent. Du antwortest ausschließlich mit gültigem JSON."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.82
    }

    for attempt in range(3):
        try:
            print(f"[StoryGenerator] KI-generiertes neues Beziehungsthema (Versuch {attempt+1}/3)...")
            resp = requests.post(config.POLLINATIONS_ENDPOINT, json=payload, headers=headers, timeout=25)
            if resp.status_code == 200:
                raw = resp.json()["choices"][0]["message"]["content"].strip()
                if "```" in raw:
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:].strip()
                    raw = raw.split("```")[0].strip()
                data = json.loads(raw)
                topic_val = data.get("topic", "")
                if topic_val and data.get("acts") and len(data["acts"]) >= 4:
                    t_lower = topic_val.lower().strip()
                    past_lowers = [p.lower().strip() for p in past_topics]
                    if t_lower not in past_lowers:
                        print(f"[StoryGenerator] Neues Thema erfolgreich generiert: '{topic_val}'")
                        return data
        except Exception as e:
            print(f"[StoryGenerator] Fehler KI-Themenversuch ({attempt+1}) : {e}")
            time.sleep(1.5)
    return None

def get_next_topic(history: list, custom_topic: str = None, ep_num: int = 1) -> dict:
    if custom_topic:
        words = custom_topic.split()
        mid = len(words) // 2
        t1 = " ".join(words[:mid]) if mid > 0 else words[0]
        t2 = " ".join(words[mid:]) if mid > 0 else "BEZIEHUNG"
        return {
            "id": f"custom_{ep_num}",
            "topic": custom_topic,
            "focus": "Eine intime und beruhigende Reflexion über die Dynamik menschlicher Beziehungen",
            "thumbnail_title_1": t1[:16].upper(),
            "thumbnail_title_2": t2[:16].upper(),
            "thumbnail_hook": "Das Herz verstehen",
            "acts": DEFAULT_5_ACTS
        }

    past_topics = load_history_topics()

    # 1. AI Dynamic Generation
    ai_topic = generate_dynamic_topic_ai(past_topics, ep_num=ep_num)
    if ai_topic:
        t1 = ai_topic.get("thumbnail_title_1", "")
        t2 = ai_topic.get("thumbnail_title_2", "")
        if not t1 or not t2:
            words = ai_topic["topic"].split()
            mid = len(words) // 2
            t1 = " ".join(words[:mid])
            t2 = " ".join(words[mid:])
        return {
            "id": ai_topic.get("id", f"ep_{ep_num}"),
            "topic": ai_topic["topic"],
            "focus": ai_topic.get("focus", "Unsere emotionalen Beziehungen verstehen und nähren"),
            "thumbnail_title_1": t1[:16].upper(),
            "thumbnail_title_2": t2[:16].upper(),
            "thumbnail_hook": ai_topic.get("thumbnail_hook", "Paarpsychologie"),
            "acts": ai_topic.get("acts", DEFAULT_5_ACTS)
        }

    # 2. Curated Curriculum Fallback
    past_lowers = [p.lower().strip() for p in past_topics]
    for idx, (title, focus) in enumerate(RELATIONSHIP_CURRICULUM):
        if title.lower().strip() not in past_lowers:
            print(f"[StoryGenerator] Katalogthema ausgewählt: '{title}'")
            words = title.split()
            mid = len(words) // 2
            t1 = " ".join(words[:mid])
            t2 = " ".join(words[mid:])
            return {
                "id": f"ep_{ep_num}",
                "topic": title,
                "focus": focus,
                "thumbnail_title_1": t1[:16].upper(),
                "thumbnail_title_2": t2[:16].upper(),
                "thumbnail_hook": "Die Kunst menschlicher Verbindung",
                "acts": DEFAULT_5_ACTS
            }

    # 3. Endless Cycle Variation
    cycle = (ep_num - 1) // len(RELATIONSHIP_CURRICULUM) + 1
    cat_idx = (ep_num - 1) % len(RELATIONSHIP_CURRICULUM)
    base_title, base_focus = RELATIONSHIP_CURRICULUM[cat_idx]
    title = f"{base_title} : Vertiefung & Heilung (Teil {cycle})"
    words = title.split()
    mid = len(words) // 2
    t1 = " ".join(words[:mid])
    t2 = " ".join(words[mid:])
    return {
        "id": f"ep_{ep_num}",
        "topic": title,
        "focus": f"Wesentliche Vertiefung: {base_focus}",
        "thumbnail_title_1": t1[:16].upper(),
        "thumbnail_title_2": t2[:16].upper(),
        "thumbnail_hook": f"Therapeutischer Ansatz #{cycle}",
        "acts": DEFAULT_5_ACTS
    }

def generate_curated_fallback_act(act_idx: int, act_title: str, topic: str, target_turns: int = 40) -> list:
    """Deutsche Beziehungs-Monologe mit therapeutischer Wärme und poetischer Eleganz."""
    h1 = config.HOST1_NAME
    s1 = config.HOST1_SPEAKER
    cname = config.CHANNEL_NAME

    solo_act_scripts = [
        # Akt 1: Die Bestandsaufnahme des Herzens
        [
        f"Willkommen bei {cname}. Ich freue mich sehr, dass du dir heute Zeit für diesen intimen Moment nimmst.",
        f"Heute halten wir inne und widmen uns einem wesentlichen Thema: {topic}.",
        f"Im Trubel unseres Alltags vergessen wir oft, auf das Schlagen unseres Herzens zu hören.",
        f"Menschliche Beziehungen sind zugleich unsere größte Zuflucht und unser ehrlichster Spiegel.",
        f"Wenn wir lieben, legen wir unsere tiefsten Sehnsüchte offen, aber auch unsere Verletzlichkeit.",
        f"Vielleicht kennst du dieses stille Missverstehen, das sich manchmal zwischen zwei Menschen legt.",
        f"Zwei Menschen, die sich innig lieben, und sich doch nicht mehr erreichen.",
        f"Atme einmal tief mit mir durch und lege alle angesammelte Anspannung ab.",
        f"Dieser Podcast ist dein Schutzraum, ein Ort, an dem Verletzlichkeit zu großer Stärke wird.",
        f"Wir suchen hier weder Perfektion, noch verteilen wir Vorwürfe.",
        ],
        # Akt 2: Die unbewussten Wurzeln
        [
        f"Um zu verstehen, was in unseren heutigen Beziehungen geschieht, müssen wir oft zurückblicken.",
        f"Unsere Art zu lieben und uns zu binden wurzelt in unseren frühesten Kindheitserfahrungen.",
        f"Unsere ersten familiären Bindungen haben unseren emotionalen Kompass geprägt.",
        f"Wo emotionale Sicherheit fehlte, kann eine panische Angst vor dem Verlassenwerden entstehen.",
        f"Wo wir uns eingeengt fühlten, kann Bindung wie ein goldener Käfig wirken.",
        f"Diese unbewussten Reflexe sind unsere Bindungsstile, unsere schützenden Rüstungen.",
        f"Zieht sich unser Partner zum Durchatmen zurück, gerät unser inneres Kind in Panik.",
        f"Wir glauben, die Liebe verschwinde, dabei braucht der andere nur Raum.",
        f"Dieses Verständnis verändert absolut alles in der Dynamik einer Partnerschaft.",
        f"Wut ist oft nur ein verzweifelter Ruf danach, gesehen und beruhigt zu werden.",
        ],
        # Akt 3: Praktische Schlüssel & beruhigende Worte
        [
        f"Wenden wir uns nun der täglichen Praxis dieser Herzenskommunikation zu.",
        f"Die größte Falle im Gespräch: die Identität des anderen anzugreifen, statt das eigene Empfinden zu zeigen.",
        f"Ersetze 'Du achtest nie auf mich' durch ein schlichtes 'Ich fühle mich gerade einsam'.",
        f"Spüre, wie diese kleine Nuance das Bedürfnis zum Gegenangriff sofort entschärft.",
        f"Wer von sich spricht, ehrlich und verletzlich, lädt den anderen zum Trösten ein.",
        f"Wer anklagt, zwingt den anderen in Rüstung und Rechtfertigung.",
        f"Ein weiteres wunderbares Geheimnis liegt in der Kunst kleiner, unerwarteter Aufmerksamkeiten.",
        f"Diese winzigen Gesten senden an unser Nervensystem ein starkes Signal: Bei mir bist du sicher.",
        f"Warte nicht auf große Jahrestage, um die Gegenwart des geliebten Menschen zu feiern.",
        f"Sage heute schlicht 'Ich verstehe dich, und ich bin bei dir', das hat unendliche Heilkraft.",
        ],
        # Akt 4: Durch emotionale Stürme gehen
        [
        f"Selbst mit größter Weisheit gehören Stürme und Reibung zum Leben zu zweit dazu.",
        f"Zwei Menschen im geteilten Alltag erleben unweigerlich Momente der Meinungsverschiedenheit und Müdigkeit.",
        f"Das Geheimnis dauerhafter Paare liegt nicht in der Abwesenheit von Konflikten, sondern in der Art, sie zu durchqueren.",
        f"Steigt die Spannung und wird der Ton schärfer, schaltet unser Gehirn in den Überlebensmodus.",
        f"In diesem Alarmzustand kann kein konstruktives Gespräch gelingen.",
        f"Der mutigste Schritt ist dann eine beruhigende Pause: 'Ich liebe dich, lass uns zehn Minuten durchatmen'.",
        f"Diese Auszeit lässt das Herz langsamer werden und erspart verletzende Worte, die man bereut.",
        f"Stolz und Ego sind die schlechtesten Ratgeber, wenn es um Liebe geht.",
        f"Frage dich stets: Willst du um jeden Preis recht behalten, oder in Frieden und Verbindung sein?",
        f"Eigene Fehler einzugestehen ist niemals Schwäche, sondern die höchste Eleganz des Herzens.",
        ],
        # Akt 5: Die Herzensaufgabe & täglicher Segen
        [
        f"Nun sind wir am Ende unserer gemeinsamen Reflexion auf diesem Kanal angelangt.",
        f"Um diese Erkenntnis in deinem Leben zu verankern, habe ich diese Woche eine Herzensaufgabe für dich.",
        f"Sage heute oder morgen einem lieben Menschen, was seine Gegenwart dir Schönes schenkt.",
        f"Sprich nicht davon, was er tut, sondern was er für dich ist und welches Licht er verbreitet.",
        f"Du wirst sehen, wie ein aufrichtiges Wort ein Gesicht erhellen und einen ganzen Tag wärmen kann.",
        f"Vergiss nie: Du verdienst es, mit Respekt, Sanftheit und Achtung geliebt zu werden.",
        f"Und schenke dir selbst jeden Morgen vor dem Spiegel dasselbe Wohlwollen.",
        f"Ich danke dir von Herzen für dein Zuhören und deine Treue auf {cname}.",
        f"Abonniere, damit du keines unserer sanften und erhellenden Treffen verpasst.",
        f"Achte gut auf dich und deine Lieben, und pflege stets die kostbare Kunst der Verbindung.",
        ],
    ]

    safe_act_idx = min(act_idx, len(solo_act_scripts) - 1)
    lines = solo_act_scripts[safe_act_idx]
    result = []
    for l in lines:
        result.append({"speaker": s1, "name": h1, "text": l})
        if len(result) >= target_turns:
            break

    while len(result) < target_turns:
        for l in lines:
            prefix = "Wenn wir mit dem Herzen darüber nachdenken, "
            result.append({"speaker": s1, "name": h1, "text": f"{prefix}{l[0].lower() + l[1:] if len(l) > 1 else l}"})
            if len(result) >= target_turns:
                break

    return result

def generate_act_ai(act_idx: int, act_title: str, topic_title: str, focus: str, target_turns: int = 35) -> list:
    key = config.POLLINATIONS_API_KEY
    if not key:
        return None

    if act_idx == 0:
        transition_note = "Eröffnungsakt: Begrüße die Zuhörer herzlich auf dem Kanal, schaffe eine sanfte, intime Atmosphäre und führe einfühlsam ins Thema ein."
    elif act_idx == 1:
        transition_note = "Akt 2: WICHTIG - Sage NICHT 'willkommen' oder 'erneut willkommen'. Knüpfe direkt und natürlich an die psychologischen Wurzeln und das Unbewusste an."
    elif act_idx == 2:
        transition_note = "Akt 3: WICHTIG - Sage NICHT 'willkommen'. Knüpfe fließend an konkrete Alltagsbeispiele, sanfte Kommunikation und beruhigende Worte an."
    elif act_idx == 3:
        transition_note = "Akt 4: WICHTIG - Sage NICHT 'willkommen'. Fahre fort mit Krisenbewältigung, Streit und Heilung von Verletzungen ohne Panik."
    else:
        transition_note = "Akt 5 (Abschluss): WICHTIG - Sanfter Übergang zur praktischen Wochenaufgabe, einer Hoffnungsbotschaft für die Partnerschaft und einem herzlichen Schlusswort."

    prompt = (
        f"Du schreibst das Skript einer intimen und tröstlichen Podcast-Episode für den Kanal '{config.CHANNEL_NAME}'.\n"
        f"Alleinmoderatorin: {config.HOST1_NAME} (Psychologin und Expertin für menschliche Beziehungen, warme, empathische und wohlwollende weibliche Stimme).\n"
        f"Format: SOLO-MONOLOG auf Deutsch, in dem sie die Zuhörer direkt ('du') anspricht wie eine liebe Freundin oder in einer intimen Beratung.\n"
        f"Episodenthema: {topic_title}\n"
        f"Aktueller Abschnitt: {act_title}\n"
        f"Emotionaler Fokus: {focus}\n"
        f"Übergangsregel: {transition_note}\n\n"
        f"STRENGE ANFORDERUNGEN:\n"
        f"- Genau {target_turns} aufeinanderfolgende Monolog-Repliken von {config.HOST1_NAME}.\n"
        f"- Jede Replik 14 bis 24 Wörter, in natürlichem, fließendem, berührendem und elegantem gesprochenem Stil.\n"
        f"- Psychologisches Vokabular, zugänglich, voller Wohlwollen, Nuancen und emotionaler Weisheit.\n"
        f"- Gib AUSSCHLIESSLICH ein rohes JSON-Array von Objekten zurück (kein Markdown, kein Begleittext):\n"
        f"[\n"
        f"- Jedes Objekt MUSS zusätzlich ein \"en\"-Feld mit einer natürlichen englischen Übersetzung von \"text\" enthalten (nur Untertitel, wird niemals gesprochen).\n"
        f'  {{"speaker": "{config.HOST1_SPEAKER}", "name": "{config.HOST1_NAME}", "text": "...", "en": "..."}},\n'
        f'  {{"speaker": "{config.HOST1_SPEAKER}", "name": "{config.HOST1_NAME}", "text": "...", "en": "..."}}\n'
        f"]"
    )

    try:
        resp = requests.post(
            config.POLLINATIONS_ENDPOINT,
            json={
                "model": config.POLLINATIONS_MODEL,
                "messages": [
                    {"role": "system", "content": "Du bist ein erstklassiger Radio- und Podcast-Generator. Du antwortest ausschließlich mit gültigem JSON."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.78
            },
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
            timeout=25
        )
        if resp.status_code == 200:
            raw = resp.json()["choices"][0]["message"]["content"].strip()
            if "```" in raw:
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:].strip()
                raw = raw.split("```")[0].strip()
            parsed = json.loads(raw)
            min_needed = max(2, min(target_turns, 8))
            if isinstance(parsed, list) and len(parsed) >= min_needed:
                result_turns = []
                for p in parsed:
                    txt = p.get("text", "").strip()
                    if not txt:
                        continue
                    result_turns.append({"speaker": config.HOST1_SPEAKER, "name": config.HOST1_NAME, "text": txt, "en": p.get("en", "").strip()})

                # Sanitize repetitive greetings in Acts 2-5
                if act_idx > 0 and result_turns:
                    first_text = result_turns[0]["text"]
                    for prefix in ['willkommen', 'hallo und willkommen', 'erneut willkommen', 'hallo zusammen']:
                        if first_text.lower().startswith(prefix):
                            cleaned = re.sub(r"^(?:willkommen(?:\s+erneut)?(?:\s+bei\s+[^.!?]*)?[.!?]\s*|hallo\s+(?:und\s+willkommen\s+)?[^.!?]*[.!?]\s*)", "", first_text, flags=re.IGNORECASE).strip()
                            if cleaned:
                                result_turns[0]["text"] = cleaned[0].upper() + cleaned[1:] if len(cleaned) > 1 else cleaned
                            else:
                                result_turns[0]["text"] = f"Setzen wir unsere Reflexion über {topic_title} fort und betrachten unser Verhalten im Alltag."
                            break

                if len(result_turns) >= target_turns:
                    return result_turns[:target_turns]
                elif len(result_turns) >= min_needed:
                    fallback_turns = generate_curated_fallback_act(act_idx, act_title, topic_title, target_turns=target_turns)
                    seen_texts = set(r["text"] for r in result_turns)
                    for ft in fallback_turns:
                        if len(result_turns) >= target_turns:
                            break
                        if ft["text"] not in seen_texts:
                            result_turns.append(ft)
                            seen_texts.add(ft["text"])
                    return result_turns[:target_turns]
    except Exception as e:
        print(f"  [KI-Hinweis] Akt {act_idx+1} auf kuratiertes Notfallskript zurückgefallen: {e}")
    return None

def generate_full_podcast_story(target_minutes: float = 20.0, topic: str = None, ep_num: int = 1) -> dict:
    history = load_history_topics()
    topic_info = get_next_topic(history, custom_topic=topic, ep_num=ep_num)
    selected_topic = topic_info["topic"]
    acts_meta = topic_info.get("acts", DEFAULT_5_ACTS)

    print(f"[StoryGenerator] Episode #{ep_num} - Thema: '{selected_topic}'")

    # Target 20 minutes calibrated with slower -6% speech rate and 0.75s natural pauses (~6.5s per turn)
    turns_per_act = int(max(4, (target_minutes * 60) / (len(acts_meta) * 6.5)))
    if target_minutes <= 1.0:
        turns_per_act = 4
    elif target_minutes <= 3.0:
        turns_per_act = 8

    dialogue = []
    chapters = []

    for act_idx, (act_title, act_focus) in enumerate(acts_meta):
        chapters.append({"title": act_title, "start_turn": len(dialogue)})
        print(f"  [Akt {act_idx+1}/5] Generiere '{act_title}' ({turns_per_act} Repliken)...")

        turns = generate_act_ai(act_idx, act_title, selected_topic, act_focus, target_turns=turns_per_act)
        if not turns:
            turns = generate_curated_fallback_act(act_idx, act_title, selected_topic, target_turns=turns_per_act)

        dialogue.extend(turns)

    print(f"[StoryGenerator] Vollständiger Monolog generiert: {len(dialogue)} Repliken in {len(acts_meta)} Akten.")
    return {
        "topic": selected_topic,
        "thumbnail_title_1": topic_info["thumbnail_title_1"],
        "thumbnail_title_2": topic_info["thumbnail_title_2"],
        "thumbnail_hook": topic_info["thumbnail_hook"],
        "chapters": chapters,
        "dialogue": dialogue
    }

def generate_metadata(topic: str, duration_sec: float, chapters: list, ep_num: int = 1) -> dict:
    title = f"{topic} | {config.CHANNEL_NAME} Folge {ep_num}"
    lines = [
        f"🎙️ Willkommen bei {config.CHANNEL_NAME} mit {config.HOST1_NAME} - Episode #{ep_num}!",
        f"Thema des Tages: {topic}",
        "",
        "🕒 KAPITEL & ZEITMARKEN:",
    ]
    for ch in chapters:
        m = int(ch.get("start_time", 0) // 60)
        s = int(ch.get("start_time", 0) % 60)
        lines.append(f"{m:02d}:{s:02d} - {ch['title']}")

    clean_tag = config.CHANNEL_NAME.replace(" ", "").replace("'", "")
    lines.extend([
        "",
        "💡 Eine sanfte und erhellende Reise ins Herz der Psychologie menschlicher Beziehungen, der Liebe und emotionaler Intimität.",
        "👉 Abonniere, um jede Woche eine neue beruhigende und inspirierende Episode zu erhalten.",
    f"#{clean_tag} #Psychologie #Beziehungen #LiebeUndPartnerschaft #PodcastDeutsch #Persönlichkeitsentwicklung #Bindung"
    ])

    return {
        "title": title[:100],
        "description": "\n".join(lines),
        "tags": ["menschliche Beziehungen", "Paarpsychologie", "Podcast Deutsch", "Liebe", "wertschätzende Kommunikation", "emotionale Bindung", config.CHANNEL_NAME.lower()]
    }
