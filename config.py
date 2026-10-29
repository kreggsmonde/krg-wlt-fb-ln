import os, sys
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_DIR = os.path.join(BASE_DIR, "input")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

for d in [INPUT_DIR, OUTPUT_DIR, TEMP_DIR, ASSETS_DIR]:
    os.makedirs(d, exist_ok=True)

# Podcast & Channel Branding
LANGUAGE = "German"
LANGUAGE_CODE = "de"
CHANNEL_NAME = "DIE KUNST DER VERBINDUNG"
TAGLINE = "Beziehungspsychologie, Liebe & menschliche Verbindung"
DEFAULT_IMAGE_PATH = os.path.join(ASSETS_DIR, "host_studio.png")
LOGO_PATH = os.path.join(ASSETS_DIR, "channel_logo.png")

# Video Specs (1080p Landscape)
VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
VIDEO_FPS = 30

# Solo Host Setup (Host is on the left X: 0-800; Subtitles & Visualizer on the right X: 900-1850)
IS_SOLO = True

# Subtitle Bubble & Pill Layout
SUBTITLE_CENTER_X = 1380
SUBTITLE_Y = 320
MAX_SUBTITLE_WIDTH = 760
SUBTITLE_FONT_SIZE = 42

# Audio Spectrum Visualizer
VIS_CENTER_X = 1380
VIS_BASE_Y = 580
VIS_NUM_BARS = 18
VIS_BAR_WIDTH = 12
VIS_BAR_SPACING = 10
VIS_MIN_HEIGHT = 4
VIS_MAX_HEIGHT = 58
VIS_COLOR = (255, 215, 0, 240)  # Radiant warm gold

# Voice & Host Configuration (Solo Female Host)
VOICE_HOST1 = "de-DE-KatjaNeural"  # Warme, reife deutsche Moderatorinnen-Stimme in Gold-Standard
VOICE_FALLBACK = "de-DE-SeraphinaMultilingualNeural"
HOST1_NAME = "Lena"
HOST1_SPEAKER = "female"
HOST1_PITCH = "+0Hz"
TTS_RATE = "-6%"  # Gentle, calm, soothing, reflective therapy pace (not rushed)
PAUSE_BETWEEN_TURNS = 0.75  # Natural human breathing space between spoken turns

# Subtitle line breaking limits
MAX_WORDS_PER_LINE = 5
MAX_CHARS_PER_LINE = 40

# Pollinations AI Prompting (Loaded from environment / Windows user variables)
POLLINATIONS_API_KEY = os.environ.get("POLLINATIONS_API_KEY", "")
POLLINATIONS_ENDPOINT = os.environ.get("POLLINATIONS_ENDPOINT", "https://gen.pollinations.ai/v1/chat/completions")
POLLINATIONS_MODEL = os.environ.get("POLLINATIONS_MODEL", "gemini-fast")

NICHE_PROMPT = (
    "ein fesselnder, tiefgründiger und wohltuender Podcast mit einer deutschen Psychologin und Beziehungsberaterin. "
    "Sie erkundet mit Feingefühl und Nuancen die Kunst menschlicher Beziehungen, die Sprachen der Liebe, emotionale Bindung, "
    "wertschätzende Kommunikation, Intimität, Verletzlichkeit, gesunde Grenzen und emotionale Heilung. "
    "Der Ton ist sanft, erhellend, intim, beruhigend und zutiefst tröstlich für die Zuhörer."
)
SYSTEM_LANGUAGE_INSTRUCTION = "Generiere alle Inhalte vollständig in elegantem, natürlichem und fesselndem Deutsch, mit einer poetischen und wohlwollend-psychologischen Note."

# System Fonts
FONT_CANDIDATES = [
    "C:\\Windows\\Fonts\\arialbd.ttf",
    "C:\\Windows\\Fonts\\segoeuib.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), "arial.ttf")
FALLBACK_FONT_PATH = FONT_PATH
