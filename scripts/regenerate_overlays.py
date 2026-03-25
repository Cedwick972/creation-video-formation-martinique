"""
Régénération des 8 overlays via Seedream V4.5
FOND TRANSPARENT — pas d'image de fond, uniquement les éléments graphiques.
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import time
import requests
from pathlib import Path

API_KEY = os.environ.get("FREEPIK_API_KEY")
BASE_URL = "https://api.freepik.com/v1"
HDR = {"x-freepik-api-key": API_KEY, "Accept-Language": "fr-FR"}
OVERLAYS_DIR = Path(__file__).resolve().parent.parent / "overlays" / "generated"

# ============================================================
# PROMPTS V2 — FOND TRANSPARENT, PAS DE PHOTOS, PAS DE VISAGES
# Insistance sur : graphic design only, no photography, no people
# ============================================================

OVERLAY_PROMPTS = {
    "overlay_01_A1_bandeau_titre": (
        "Flat graphic design element ONLY on a solid bright green chroma key background #00FF00. "
        "No photographs, no people, no faces, no scenery. Pure 2D vector graphic overlay. "
        "A single horizontal banner centered: text 'FORMATION DRAINAGE LYMPHATIQUE' in bold white uppercase Bebas Neue style font 72px. "
        "Solid orange #F07D00 rectangle behind the text, 110px tall, 900px wide, rounded corners 8px. "
        "Nothing else on the image. Green chroma key background everywhere except the banner. "
        "9:16 vertical format 1080x1920px."
    ),
    "overlay_02_G4_tag_localisation": (
        "Flat graphic design element ONLY on a solid bright green chroma key background #00FF00. "
        "No photographs, no people, no faces, no scenery. Pure 2D vector-style overlay. "
        "Bottom-left positioned card: semi-transparent dark gray rectangle with a 6px orange #F07D00 left border. "
        "Small white map pin icon on the left side. "
        "Line 1: 'MARTINIQUE - ANTILLES' in bold uppercase orange #F07D00 text. "
        "Line 2: 'Prochaine session sur place' in smaller light gray #CCCCCC text. "
        "Green chroma key background everywhere except the card element. "
        "9:16 vertical format 1080x1920px."
    ),
    "overlay_03_G1_lower_third": (
        "Flat graphic design element ONLY on a solid bright green chroma key background #00FF00. "
        "No photographs, no people, no faces, no scenery. Pure 2D vector-style lower third. "
        "Bottom-left positioned: two stacked rectangular blocks. "
        "Top block: solid orange #F07D00 rectangle with 'SAMUEL PINCEAU' in bold white 80px text. "
        "Bottom block: dark semi-transparent rectangle with 'Massotherapeute agree - Quebec' in white 36px text. "
        "Green chroma key background everywhere else. Clean broadcast-style graphic. "
        "9:16 vertical format 1080x1920px."
    ),
    "overlay_04_A3_statistique": (
        "Flat graphic design element ONLY on a solid bright green chroma key background #00FF00. "
        "No photographs, no people, no faces, no scenery. Pure 2D vector-style info card. "
        "A dark charcoal #2A2A2A rounded rectangle card, width 560px, rounded corners 12px, "
        "with a 6px orange #F07D00 left border and 32px padding inside. "
        "White bold text inside: 'Retention - Jambes lourdes - Recuperation post-op' in sans-serif 42px. "
        "Green chroma key background #00FF00 everywhere except the card. "
        "9:16 vertical format 1080x1920px."
    ),
    "overlay_05_C1_checklist_programme": (
        "Flat graphic design element ONLY on a solid bright green chroma key background #00FF00. "
        "No photographs, no people, no faces, no scenery. Pure 2D vector-style checklist card. "
        "A dark charcoal #2A2A2A rounded rectangle card with 6px orange #F07D00 left border, rounded corners 12px. "
        "Inside: vertical checklist with orange checkmark icons and white bold text 38px: "
        "1) Connaitre la lymphe 2) Comprendre la congestion 3) Pathologies de retention 4) Ateliers pratiques. "
        "Green chroma key background everywhere except the card. "
        "9:16 vertical format 1080x1920px."
    ),
    "overlay_06_C1_checklist_techniques": (
        "Flat graphic design element ONLY on a solid bright green chroma key background #00FF00. "
        "No photographs, no people, no faces, no scenery. Pure 2D vector-style checklist card. "
        "A dark charcoal #2A2A2A rounded rectangle card with 6px orange #F07D00 left border, rounded corners 12px. "
        "Inside: vertical checklist with orange checkmark icons and white bold text 38px: "
        "1) Reflexologie plantaire 2) Techniques de drainage 3) Palper-rouler et ventouse 4) B.A.-BA du massage. "
        "Green chroma key background everywhere except the card. "
        "9:16 vertical format 1080x1920px."
    ),
    "overlay_07_A2_credibilite": (
        "Flat graphic design element ONLY on a solid bright green chroma key background #00FF00. "
        "No photographs, no people, no faces, no scenery. Pure 2D vector-style quote card. "
        "A dark charcoal #2A2A2A rounded rectangle card with 6px orange #F07D00 left border, rounded corners 12px. "
        "Large faded orange quotation mark at top-left inside card. "
        "White italic bold text 40px: '7 techniques maitrisees - Agree depuis 2018 - Clientele fidele aux Antilles'. "
        "Below: orange text 30px: '- Samuel Pinceau - Formateur'. "
        "Green chroma key background everywhere except the card. "
        "9:16 vertical format 1080x1920px."
    ),
    "overlay_08_F1_cta_inscription": (
        "Flat graphic design element ONLY on a solid bright green chroma key background #00FF00. "
        "No photographs, no people, no faces, no scenery. Pure 2D vector-style CTA buttons. "
        "Centered vertically: "
        "1) Large orange #F07D00 rounded button 680px wide with bold black text 'S INSCRIRE' and a right arrow icon. "
        "2) Below: pill-shaped outlined button with white border and white text 'spmassotherapeute.com'. "
        "3) Below: gray text '(581) 305-1499'. "
        "4) Below: small gray text 'Places limitees - Formation en Martinique'. "
        "Green chroma key background #00FF00 everywhere except the UI elements. "
        "9:16 vertical format 1080x1920px."
    ),
}


def main():
    print("=== REGENERATION OVERLAYS V2 (fond chroma key vert) ===\n")
    OVERLAYS_DIR.mkdir(parents=True, exist_ok=True)

    # Lancer toutes les générations
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
            print(f"  Tache: {task_id} ({data.get('status')})")
            tasks[name] = task_id
        except Exception as e:
            print(f"  x Erreur: {e}")
            tasks[name] = None

    # Attendre et télécharger
    print("\n--- Attente des resultats ---\n")
    success = 0
    for name, task_id in tasks.items():
        if not task_id:
            continue
        print(f"[{name}]", end="", flush=True)
        for attempt in range(30):  # max 2.5 min
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
                        # Save as v2 to keep originals
                        filepath = OVERLAYS_DIR / f"{name}.png"
                        img_resp = requests.get(images[0], stream=True)
                        img_resp.raise_for_status()
                        with open(filepath, "wb") as f:
                            for chunk in img_resp.iter_content(8192):
                                f.write(chunk)
                        size_kb = filepath.stat().st_size / 1024
                        print(f" OK ({size_kb:.0f} KB)")
                        success += 1
                    else:
                        print(" x (pas d'image)")
                    break
                elif status == "FAILED":
                    print(" x ECHOUE")
                    break
                else:
                    print(".", end="", flush=True)
                    time.sleep(5)
            except Exception as e:
                print(f" x ({e})")
                break

    print(f"\n=== TERMINE: {success}/8 overlays generes ===")


if __name__ == "__main__":
    if not API_KEY:
        print("ERREUR: FREEPIK_API_KEY non definie")
        sys.exit(1)
    main()
