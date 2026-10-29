import os, sys, argparse, asyncio, json
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if sys.platform == 'win32':
    try: sys.stdout.reconfigure(encoding='utf-8')
    except Exception: pass

import config
from story_generator import generate_full_podcast_story, generate_metadata, load_history_topics
from tts_engine import generate_podcast_audio
from thumbnail_generator import generate_thumbnail
from video_composer import render_podcast_video
from publish_youtube import publish_to_youtube
from publish_facebook import upload_to_facebook

def save_episode_history(record: dict):
    """Synchronously saves episode history to published_videos.json, history.json, and history.js."""
    base_dir = config.BASE_DIR
    p1 = os.path.join(base_dir, "published_videos.json")
    history = []
    if os.path.exists(p1):
        try:
            with open(p1, "r", encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []

    history.append(record)

    # 1. published_videos.json
    with open(p1, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    # 2. history.json
    p2 = os.path.join(base_dir, "history.json")
    with open(p2, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

    # 3. history.js
    p3 = os.path.join(base_dir, "history.js")
    with open(p3, "w", encoding="utf-8") as f:
        f.write("// Episodenverlauf & Themenregister\n")
        f.write("const PODCAST_HISTORY = " + json.dumps(history, indent=2, ensure_ascii=False) + ";\n")
        f.write("if (typeof module !== 'undefined' && module.exports) { module.exports = PODCAST_HISTORY; }\n")
        f.write("if (typeof window !== 'undefined') { window.PODCAST_HISTORY = PODCAST_HISTORY; }\n")

    print(f"[Verlauf] Episode #{record['episode']} erfolgreich in published_videos.json, history.json und history.js gespeichert")

def run_auto_pipeline(target_minutes: float = 20.0, topic: str = None, dry_run: bool = False, preview_seconds: float = None, force_youtube: bool = False):
    print("=" * 75)
    print(f"    [SOLO-PODCAST] {config.CHANNEL_NAME} - AUTOMATISIERTE PIPELINE")
    print(f"    Moderatorin : {config.HOST1_NAME} ({config.VOICE_HOST1})")
    print(f"    Zieldauer : {target_minutes:.1f} Minuten")
    print("=" * 75)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    past_topics = load_history_topics()
    ep_num = len(past_topics) + 1

    # Étape 1 : Conception du sujet et monologue
    print(f"\n[Schritt 1/5] Generiere Geschichte und Akte (Ziel: {target_minutes:.1f} Min.)...")
    story = generate_full_podcast_story(target_minutes=target_minutes, topic=topic, ep_num=ep_num)

    # Étape 2 : Synthèse vocale neuronale & synchronisation
    print(f"\n[Schritt 2/5] Neuronale Sprachsynthese und Wort-Zeitstempel...")
    master_audio, subtitle_chunks, total_dur = asyncio.run(generate_podcast_audio(story["dialogue"]))

    # Calcul des horodatages des chapitres
    for ch in story["chapters"]:
        start_turn = ch["start_turn"]
        ch_time = 0.0
        for c in subtitle_chunks:
            if c.get("turn_idx") == start_turn:
                ch_time = c["start"]
                break
        ch["start_time"] = ch_time

    # Étape 3 : Création de la miniature YouTube Haute Visibilité
    print(f"\n[Schritt 3/5] Generiere YouTube-Thumbnail...")
    thumb_path = os.path.join(config.OUTPUT_DIR, f"thumb_ep{ep_num}_{timestamp}.jpg")
    generate_thumbnail(
        config.DEFAULT_IMAGE_PATH,
        story["thumbnail_title_1"],
        story["thumbnail_title_2"],
        story["thumbnail_hook"],
        thumb_path,
        ep_number=ep_num
    )

    # Étape 4 : Rendu Vidéo 1080p avec bulle sous-titres et visualiseur
    print(f"\n[Schritt 4/5] Rendere 1080p-Full-HD-Video via FFmpeg-Pipe...")
    video_path = os.path.join(config.OUTPUT_DIR, f"podcast_ep{ep_num}_{timestamp}.mp4")
    render_podcast_video(
        config.DEFAULT_IMAGE_PATH,
        master_audio,
        subtitle_chunks,
        video_path,
        fps=config.VIDEO_FPS,
        preview_seconds=preview_seconds
    )

    # Étape 5 : Métadonnées et Publication Sociale
    meta = generate_metadata(story["topic"], total_dur, story["chapters"], ep_num=ep_num)
    published_platforms = []
    if dry_run:
        print("[DRY RUN] Testmodus aktiv: Veröffentlichung in sozialen Netzen übersprungen.")
    else:
        # Facebook
        print(f"\n[Schritt 5/5] Veröffentliche auf Facebook-Seite '{config.CHANNEL_NAME}'...")
        try:
            fb_res = upload_to_facebook(video_path, meta["title"], meta["description"])
            if fb_res and (fb_res.get("id") or fb_res.get("success")):
                vid_id = fb_res.get("id") or fb_res.get("data", {}).get("id")
                print(f"[Facebook Erfolg] Video-ID: {vid_id}")
                published_platforms.append("Facebook")
            else:
                print(f"[Facebook Hinweis] {fb_res}")
        except Exception as e:
            print(f"[Facebook Fehler] {e}")

        # YouTube
        print(f"\n[Schritt 5/5] Prüfe YouTube-Veröffentlichungsplan...")
        try:
            yt_res = publish_to_youtube(video_path, meta["title"], meta["description"], thumb_path=thumb_path, force=force_youtube)
            if yt_res:
                published_platforms.append("YouTube")
        except Exception as e:
            print(f"[YouTube Fehler] {e}")

    # Enregistrement dans l'historique
    record = {
        "episode": ep_num,
        "topic": story["topic"],
        "date": datetime.now().isoformat(),
        "duration_sec": round(total_dur, 2),
        "duration_min": round(total_dur / 60.0, 2),
        "video_file": os.path.basename(video_path),
        "thumbnail_file": os.path.basename(thumb_path),
        "platform": ", ".join(published_platforms) if published_platforms else "Local"
    }
    save_episode_history(record)

    print("\n" + "=" * 75)
    print(f"       PIPELINE ERFOLGREICH ABGESCHLOSSEN! Episode #{ep_num}")
    print(f"       Videodatei   : {video_path}")
    print(f"       Thumbnail    : {thumb_path}")
    print(f"       Gesamtdauer  : {total_dur:.1f}s ({total_dur/60:.1f} Min.)")
    print("=" * 75)
    return video_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=f"{config.CHANNEL_NAME} - Automatisierte Beziehungs-Podcast-Pipeline")
    parser.add_argument("--duration", type=float, default=20.0, help="Zieldauer in Minuten (Standard: 20.0)")
    parser.add_argument("--topic", type=str, default=None, help="Benutzerdefiniertes Thema")
    parser.add_argument("--dry-run", action="store_true", help="Veröffentlichung in sozialen Netzen überspringen")
    parser.add_argument("--preview", type=float, default=None, help="Nur X Sekunden Vorschau rendern (z. B.: 15.0)")
    parser.add_argument("--force-youtube", action="store_true", help="YouTube-Veröffentlichung erzwingen")
    args = parser.parse_args()

    run_auto_pipeline(target_minutes=args.duration, topic=args.topic, dry_run=args.dry_run, preview_seconds=args.preview, force_youtube=args.force_youtube)
