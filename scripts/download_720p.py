"""
Téléchargement des B-roll en 720p via les previews Freepik.
Sélection des meilleurs clips par segment du script.
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import requests
from pathlib import Path

API_KEY = os.environ.get("FREEPIK_API_KEY")
BASE_URL = "https://api.freepik.com/v1"
HDR = {"x-freepik-api-key": API_KEY, "Accept-Language": "fr-FR"}
PROJECT_DIR = Path(__file__).resolve().parent.parent
BROLL_DIR = PROJECT_DIR / "b-roll"


def get_preview_url(video_id, target_width=1280):
    """Récupère l'URL preview la plus proche de target_width (720p = 1280)."""
    resp = requests.get(f"{BASE_URL}/videos/{video_id}", headers=HDR)
    resp.raise_for_status()
    data = resp.json().get("data", {})
    previews = data.get("previews", [])

    # Filter out tiny thumbnails (455px)
    valid = [p for p in previews if p.get("width", 0) >= 640]
    if not valid:
        valid = previews

    # Find closest to target width
    best = min(valid, key=lambda p: abs(p.get("width", 9999) - target_width))
    return best.get("url"), best.get("width"), best.get("height"), data.get("name", "")


def download_preview(video_id, dest_folder, prefix, target_width=1280):
    """Télécharge une vidéo via son URL preview en basse résolution."""
    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    url, w, h, name = get_preview_url(video_id, target_width)
    if not url:
        print(f"  x Pas de preview pour #{video_id}")
        return None

    fname = f"{prefix}_{video_id}_{w}x{h}.mp4"
    filepath = dest_folder / fname
    print(f"  -> #{video_id} ({w}x{h}) {name[:50]}...")

    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    size_mb = filepath.stat().st_size / (1024 * 1024)
    print(f"     OK: {fname} ({size_mb:.1f} MB)")
    return filepath


# ============================================================
# SÉLECTION PAR SEGMENT — IDs de vidéos GRATUITES uniquement
# ============================================================

SEGMENTS = {
    # Segment 1 — HOOK (0-10s) : Plans tropicaux aériens
    "martinique": {
        "seg1_hook": [
            3535453,  # vue aérienne plage tropicale palmiers eau turquoise
            3384756,  # côte tropicale vierge palmiers coco
            28983,    # rayons lumineux colline verdoyante
        ],
        # Segment 5 — FORMATEUR (60-75s) : Cadre tropical
        "seg5_cadre": [
            3535453,  # plage tropicale (réutilisé angle différent)
            2855451,  # couples piscine station thermale
            2930290,  # nature morte bougies encens serviettes (ambiance)
        ],
        # Segment 6 — CTA (75-90s) : Fin / ambiance
        "seg6_cta": [
            3384756,  # côte tropicale
            2900683,  # nature morte bougies encens (fermeture douce)
        ],
    },
    # Segment 2 — CONSTAT (10-25s) : Massage mains, jambes
    "massage": {
        "seg2_constat": [
            6125077,  # Massage on leg with oil
            5966664,  # person receiving relaxing leg massage
            5966659,  # masseuse hand massage close-up
            2789729,  # femme massage jambes
        ],
        # Segment 3 — PROGRAMME (25-45s) : Atelier pratique
        "seg3_programme": [
            6124990,  # Massage and Relaxation (40s)
            6125069,  # séance massage thérapeutique
            3549099,  # femme massage dos spa
            6124973,  # Massage therapy for relaxation
        ],
        # Segment 4 — TECHNIQUES (45-60s) : Réflexologie, ventouses, palper-rouler
        "seg4_techniques": [
            2743544,  # gros plan thérapeute massage pieds (réflexologie)
            3544166,  # massage des pieds
            3543797,  # séance thérapie ventouses
            4381112,  # massage anti-cellulite (palper-rouler) — try, might be premium
            6375346,  # Massage therapy for leg
            1725765,  # thérapeute massage pied patient clinique
        ],
    },
}


def main():
    print("\n=== TELECHARGEMENT B-ROLL 720p ===\n")
    total = 0
    errors = 0
    downloaded_ids = set()

    for category, segs in SEGMENTS.items():
        for seg_name, video_ids in segs.items():
            dest = BROLL_DIR / category
            print(f"\n--- {seg_name.upper()} -> {dest} ---")
            for vid_id in video_ids:
                if vid_id in downloaded_ids:
                    print(f"  ~ #{vid_id} deja telecharge, skip")
                    continue
                try:
                    result = download_preview(vid_id, dest, prefix=seg_name)
                    if result:
                        total += 1
                        downloaded_ids.add(vid_id)
                except Exception as e:
                    print(f"  x #{vid_id}: {e}")
                    errors += 1

    print(f"\n=== TERMINE ===")
    print(f"  Telechargements: {total}")
    print(f"  Erreurs: {errors}")

    # List all files
    print(f"\n=== FICHIERS B-ROLL ===")
    for cat in ["martinique", "massage"]:
        d = BROLL_DIR / cat
        if d.exists():
            files = sorted(d.glob("*.mp4"))
            print(f"\n  {cat}/")
            for f in files:
                size_mb = f.stat().st_size / (1024 * 1024)
                print(f"    {f.name} ({size_mb:.1f} MB)")


if __name__ == "__main__":
    if not API_KEY:
        print("ERREUR: FREEPIK_API_KEY non definie")
        sys.exit(1)
    main()
