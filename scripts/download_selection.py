"""
Téléchargement sélectif des meilleurs B-roll pour chaque segment du script.
+ Génération des 8 overlays via Seedream V4.5.
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import json
import time
import requests
from pathlib import Path

API_KEY = os.environ.get("FREEPIK_API_KEY")
BASE_URL = "https://api.freepik.com/v1"
PROJECT_DIR = Path(__file__).resolve().parent.parent
BROLL_DIR = PROJECT_DIR / "b-roll"
OVERLAYS_DIR = PROJECT_DIR / "overlays" / "generated"

HDR = {"x-freepik-api-key": API_KEY, "Accept-Language": "fr-FR"}


def download_video(video_id, dest_folder, prefix=""):
    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)
    resp = requests.get(f"{BASE_URL}/videos/{video_id}/download", headers=HDR)
    resp.raise_for_status()
    data = resp.json().get("data", {})
    url = data.get("url")
    if not url:
        print(f"  x Pas d'URL pour video {video_id}")
        return None
    fname = data.get("filename", f"{prefix}video_{video_id}.mp4")
    if prefix and not fname.startswith(prefix):
        fname = f"{prefix}_{fname}"
    filepath = dest_folder / fname
    print(f"  -> Telechargement {filepath.name}...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print(f"  OK: {filepath}")
    return filepath


def download_resource(resource_id, fmt, dest_folder, prefix=""):
    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)
    resp = requests.get(f"{BASE_URL}/resources/{resource_id}/download/{fmt}", headers=HDR)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    if isinstance(data, list) and data:
        url = data[0].get("url")
        fname = data[0].get("filename", f"{prefix}resource_{resource_id}.{fmt}")
    elif isinstance(data, dict):
        url = data.get("url")
        fname = data.get("filename", f"{prefix}resource_{resource_id}.{fmt}")
    else:
        print(f"  x Pas de donnees pour resource {resource_id}")
        return None
    if not url:
        return None
    if prefix and not fname.startswith(prefix):
        fname = f"{prefix}_{fname}"
    filepath = dest_folder / fname
    print(f"  -> Telechargement {filepath.name}...")
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print(f"  OK: {filepath}")
    return filepath


# ============================================================
# SÉLECTION DES MEILLEURS B-ROLL PAR SEGMENT
# ============================================================

# Segment 1 — HOOK (0-10s) : Plans aériens Martinique
SEGMENT_1_MARTINIQUE = [
    2892021,  # prise de vue aérienne belle plage Martinique
    965139,   # voler sur la côte océan drone
    2910699,  # drone aérien après-midi ensoleillé
]

# Segment 2 — CONSTAT (10-25s) : Massage mains, jambes
SEGMENT_2_MASSAGE = [
    5446489,  # Beauty technician glides fingertips
    1666448,  # Close shot fingers massaging arm
    1487604,  # patient massage thérapeute qualifié
    6125077,  # Massage on leg with oil
    3935170,  # femme recevant massage des jambes
]

# Segment 3 — PROGRAMME (25-45s) : Samuel explique + atelier
SEGMENT_3_PROGRAMME = [
    3908186,  # séance de massage thérapeutique
    3098752,  # femme massage main
    2487103,  # traitement relaxation salon spa
]

# Segment 4 — TECHNIQUES (45-60s) : Réflexologie, ventouses, palper-rouler
SEGMENT_4_TECHNIQUES = [
    845218,   # gros plan femme pouces réflexologie
    6490432,  # therapist massaging female foot
    6377098,  # séance thérapie ventouses
    3793035,  # cupping therapy session
    4381112,  # massage anti-cellulite (palper-rouler)
]

# Segment 5 — FORMATEUR (60-75s) : Cadre tropical + massage
SEGMENT_5_CADRE = [
    556487,   # eaux turquoises mer caraïbes
    1151882,  # littoral île tropicale lagon bleu
    881814,   # panorama mer caraïbes
]

# Segment 6 — CTA (75-90s) : Coucher soleil Martinique
SEGMENT_6_CTA = [
    328805,   # coucher du soleil panoramique
    332939,   # vue aérienne grande soeur Seychelles (tropical sunset)
]


def download_all_broll():
    print("\n=== TELECHARGEMENT B-ROLL SELECTIONNES ===\n")

    segments = {
        "martinique": [
            ("seg1_hook", SEGMENT_1_MARTINIQUE, "video"),
            ("seg5_cadre", SEGMENT_5_CADRE, "video"),
            ("seg6_cta", SEGMENT_6_CTA, "video"),
        ],
        "massage": [
            ("seg2_constat", SEGMENT_2_MASSAGE, "video"),
            ("seg3_programme", SEGMENT_3_PROGRAMME, "video"),
            ("seg4_techniques", SEGMENT_4_TECHNIQUES, "video"),
        ],
    }

    for category, segs in segments.items():
        for prefix, ids, media_type in segs:
            dest = BROLL_DIR / category
            print(f"\n--- {prefix.upper()} ({len(ids)} fichiers) -> {dest} ---")
            for vid_id in ids:
                try:
                    if media_type == "video":
                        download_video(vid_id, dest, prefix=prefix)
                    else:
                        download_resource(vid_id, "jpg", dest, prefix=prefix)
                except Exception as e:
                    print(f"  x Erreur video #{vid_id}: {e}")


# ============================================================
# GÉNÉRATION DES 8 OVERLAYS — SEEDREAM V4.5
# ============================================================

OVERLAY_PROMPTS = {
    "overlay_01_A1_bandeau_titre": (
        "Professional video overlay graphic on transparent background, 9:16 vertical format 1080x1920px. "
        "Centered horizontal banner with text 'FORMATION DRAINAGE LYMPHATIQUE' in bold white uppercase sans-serif font (similar to Bebas Neue), 72px. "
        "Solid orange (#F07D00) rectangle background, height 110px, width 900px, rounded corners 8px. "
        "Clean, minimalist wellness branding style. Only orange and white colors. No other decorative elements. Transparent background."
    ),
    "overlay_02_G4_tag_localisation": (
        "Professional video overlay on transparent background, 9:16 vertical 1080x1920px. "
        "Location tag card positioned bottom-left: semi-transparent dark background (60% black opacity) with bold orange (#F07D00) left border 6px wide. "
        "Contains a small white map pin icon 40px on left side. "
        "Line 1: 'MARTINIQUE - ANTILLES' in bold uppercase orange (#F07D00) text, 52px. "
        "Line 2: 'Prochaine session sur place' in smaller white (#CCCCCC) text, 30px. "
        "Professional, clean, sober design. Transparent background."
    ),
    "overlay_03_G1_lower_third": (
        "Professional broadcast-style lower third overlay on transparent background, 9:16 vertical 1080x1920px. "
        "Two stacked rectangular blocks positioned bottom-left. "
        "Top block: 'SAMUEL PINCEAU' in bold white 80px text on solid orange (#F07D00) background rectangle. "
        "Bottom block: 'Massotherapeute agree - Quebec' in white 36px text on semi-transparent dark (60% black) background. "
        "Clean professional wellness branding. Transparent background."
    ),
    "overlay_04_A3_statistique": (
        "Professional video info card overlay on transparent background, 9:16 vertical 1080x1920px. "
        "Dark semi-transparent card (60% black opacity) with orange (#F07D00) left border 6px, rounded corners 12px. "
        "Width approximately 560px, padding 32px. "
        "Text: 'Retention - Jambes lourdes - Recuperation post-op' in bold white sans-serif 42px. "
        "Clean, premium health and wellness style. Only orange, black, white. Transparent background."
    ),
    "overlay_05_C1_checklist_programme": (
        "Professional video checklist card overlay on transparent background, 9:16 vertical 1080x1920px. "
        "Dark semi-transparent card (60% black) with orange (#F07D00) left border 6px, rounded corners 12px, width 560px. "
        "Vertical list with orange checkmark bullets: "
        "1. Connaitre la lymphe, 2. Comprendre la congestion, 3. Pathologies de retention, 4. Ateliers pratiques. "
        "Bold white text 38px, orange (#F07D00) checkmarks. Clean wellness infographic. Transparent background."
    ),
    "overlay_06_C1_checklist_techniques": (
        "Professional video checklist card overlay on transparent background, 9:16 vertical 1080x1920px. "
        "Dark semi-transparent card (60% black) with orange (#F07D00) left border 6px, rounded corners 12px, width 560px. "
        "Vertical list with orange checkmark bullets: "
        "1. Reflexologie plantaire, 2. Techniques de drainage, 3. Palper-rouler et ventouse, 4. B.A.-BA du massage. "
        "Bold white text 38px, orange (#F07D00) checkmarks. Clean wellness style. Transparent background."
    ),
    "overlay_07_A2_credibilite": (
        "Professional video testimonial card overlay on transparent background, 9:16 vertical 1080x1920px. "
        "Dark semi-transparent card (60% black) with orange (#F07D00) left border 6px, rounded corners 12px, width 560px padding 32px. "
        "Large faded orange quotation marks (30% opacity) at top-left of card. "
        "Italic white bold text 40px: '7 techniques maitrisees - Agree depuis 2018 - Clientele fidele aux Antilles'. "
        "Attribution line in orange 30px: '- Samuel Pinceau - Formateur'. Premium, authentic style. Transparent background."
    ),
    "overlay_08_F1_cta_inscription": (
        "Professional video CTA overlay on transparent background, 9:16 vertical 1080x1920px. "
        "Centered vertically: Large orange (#F07D00) button rectangle 680px wide 110px tall rounded 8px with bold black text 'S INSCRIRE' 72px and arrow icon. "
        "Below: pill-shaped outlined button with 'spmassotherapeute.com' in white 34px, white border 2px, rounded 50px. "
        "Below: '(581) 305-1499' in gray (#6B6B6B) 28px. "
        "Below: 'Places limitees - Formation en Martinique' in gray 26px. "
        "Dynamic, inviting call-to-action design. Transparent background."
    ),
}


def generate_all_overlays():
    print("\n=== GENERATION OVERLAYS SEEDREAM V4.5 ===\n")
    OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

    tasks = {}
    for name, prompt in OVERLAY_PROMPTS.items():
        print(f"[{name}]")
        try:
            resp = requests.post(
                f"{BASE_URL}/ai/text-to-image/seedream-v4-5",
                headers={**HDR, "Content-Type": "application/json"},
                json={
                    "prompt": prompt,
                    "aspect_ratio": "social_story_9_16",
                    "enable_safety_checker": True,
                }
            )
            resp.raise_for_status()
            data = resp.json().get("data", {})
            task_id = data.get("task_id")
            print(f"  Tache creee: {task_id} (status: {data.get('status')})")
            tasks[name] = task_id
        except Exception as e:
            print(f"  x Erreur: {e}")
            tasks[name] = None

    # Attendre et télécharger chaque overlay
    print("\n--- Attente des resultats ---\n")
    for name, task_id in tasks.items():
        if not task_id:
            continue
        print(f"[{name}]")
        for attempt in range(24):  # max 2 minutes
            try:
                resp = requests.get(
                    f"{BASE_URL}/ai/text-to-image/seedream-v4-5/{task_id}",
                    headers=HDR
                )
                resp.raise_for_status()
                data = resp.json().get("data", {})
                status = data.get("status", "UNKNOWN")

                if status == "COMPLETED":
                    images = data.get("generated", [])
                    if images:
                        img_url = images[0]
                        filepath = OVERLAYS_DIR / f"{name}.png"
                        img_resp = requests.get(img_url, stream=True)
                        img_resp.raise_for_status()
                        with open(filepath, "wb") as f:
                            for chunk in img_resp.iter_content(8192):
                                f.write(chunk)
                        print(f"  OK: {filepath}")
                    else:
                        print(f"  x Complete mais aucune image")
                    break
                elif status == "FAILED":
                    print(f"  x Echoue")
                    break
                else:
                    print(f"  En cours... ({attempt * 5}s)")
                    time.sleep(5)
            except Exception as e:
                print(f"  x Erreur polling: {e}")
                break

    print(f"\nGeneration terminee. Overlays dans: {OVERLAYS_DIR}")


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    if not API_KEY:
        print("ERREUR: FREEPIK_API_KEY non definie")
        sys.exit(1)

    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    if cmd in ("broll", "all"):
        download_all_broll()

    if cmd in ("overlays", "all"):
        generate_all_overlays()

    if cmd == "all":
        print("\n=== TOUT TERMINE ===")
        print(f"Dossier projet: {PROJECT_DIR}")
