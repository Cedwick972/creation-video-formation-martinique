"""
Freepik API Assistant — Formation Drainage Lymphatique Martinique
Recherche/téléchargement de ressources + génération d'overlays Seedream V4.5
"""

import os
import sys
import json
import time
import requests

# Fix Windows console encoding
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
from pathlib import Path

# --- Configuration ---
PROJECT_DIR = Path(__file__).resolve().parent.parent
BROLL_DIR = PROJECT_DIR / "b-roll"
OVERLAYS_DIR = PROJECT_DIR / "overlays"
PROMPTS_DIR = OVERLAYS_DIR / "prompts"
GENERATED_DIR = OVERLAYS_DIR / "generated"

BASE_URL = "https://api.freepik.com/v1"

def get_api_key():
    key = os.environ.get("FREEPIK_API_KEY")
    if not key:
        print("ERREUR: Variable d'environnement FREEPIK_API_KEY non définie.")
        print("  export FREEPIK_API_KEY='votre_clé_ici'")
        sys.exit(1)
    return key

def headers():
    return {
        "x-freepik-api-key": get_api_key(),
        "Accept-Language": "fr-FR"
    }

# ============================================================
# RECHERCHE DE RESSOURCES (photos, vecteurs, PSD)
# ============================================================

def search_resources(term, limit=20, content_type=None, orientation=None, license_type=None):
    """Recherche de ressources Freepik (photos, vecteurs, PSD)."""
    params = {"term": term, "limit": limit, "order": "relevance"}
    if content_type:
        params["filters.content_type"] = content_type  # photo, psd, vector
    if orientation:
        params["filters.orientation"] = orientation  # portrait, landscape, square
    if license_type:
        params["filters.license"] = license_type  # freemium, premium

    resp = requests.get(f"{BASE_URL}/resources", headers=headers(), params=params)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("data", [])
    print(f"  → {len(results)} résultats pour '{term}'")
    return results


def download_resource(resource_id, resource_format, dest_folder, filename=None):
    """Télécharge une ressource par ID et format."""
    url = f"{BASE_URL}/resources/{resource_id}/download/{resource_format}"
    resp = requests.get(url, headers=headers())
    resp.raise_for_status()
    data = resp.json()

    downloads = data.get("data", [])
    if not downloads:
        print(f"  ✗ Aucun lien de téléchargement pour resource {resource_id}")
        return None

    download_url = downloads[0].get("url") if isinstance(downloads, list) else downloads.get("url")
    if not download_url:
        print(f"  ✗ URL manquante pour resource {resource_id}")
        return None

    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    if not filename:
        filename = downloads[0].get("filename", f"resource_{resource_id}.{resource_format}") if isinstance(downloads, list) else downloads.get("filename", f"resource_{resource_id}.{resource_format}")

    filepath = dest_folder / filename
    print(f"  ↓ Téléchargement {filepath.name}...")
    file_resp = requests.get(download_url, stream=True)
    file_resp.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in file_resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  ✓ Sauvegardé: {filepath}")
    return filepath


# ============================================================
# RECHERCHE ET TÉLÉCHARGEMENT DE VIDÉOS
# ============================================================

def search_videos(term, limit=10, orientation=None, duration=None):
    """Recherche de vidéos Freepik."""
    params = {"term": term, "order": "relevance"}
    # Note: orientation filter not supported on /videos endpoint
    if duration:
        params["filters[duration]"] = duration

    resp = requests.get(f"{BASE_URL}/videos", headers=headers(), params=params)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("data", [])
    print(f"  → {len(results)} vidéos pour '{term}'")
    return results


def download_video(video_id, dest_folder, filename=None):
    """Télécharge une vidéo par ID."""
    url = f"{BASE_URL}/videos/{video_id}/download"
    resp = requests.get(url, headers=headers())
    resp.raise_for_status()
    data = resp.json().get("data", {})

    download_url = data.get("url")
    if not download_url:
        print(f"  ✗ Pas d'URL pour vidéo {video_id}")
        return None

    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    if not filename:
        filename = data.get("filename", f"video_{video_id}.mp4")

    filepath = dest_folder / filename
    print(f"  ↓ Téléchargement vidéo {filepath.name}...")
    file_resp = requests.get(download_url, stream=True)
    file_resp.raise_for_status()
    with open(filepath, "wb") as f:
        for chunk in file_resp.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"  ✓ Vidéo sauvegardée: {filepath}")
    return filepath


# ============================================================
# GÉNÉRATION D'OVERLAYS — SEEDREAM V4.5
# ============================================================

def generate_overlay(prompt_text, aspect_ratio="social_story_9_16", seed=None):
    """Lance une génération d'image via Seedream V4.5. Retourne le task_id."""
    payload = {
        "prompt": prompt_text,
        "aspect_ratio": aspect_ratio,
        "enable_safety_checker": True
    }
    if seed is not None:
        payload["seed"] = seed

    resp = requests.post(
        f"{BASE_URL}/ai/text-to-image/seedream-v4-5",
        headers={**headers(), "Content-Type": "application/json"},
        json=payload
    )
    resp.raise_for_status()
    data = resp.json().get("data", {})
    task_id = data.get("task_id")
    status = data.get("status")
    print(f"  ⚙ Tâche créée: {task_id} (status: {status})")
    return task_id


def check_task_status(task_id):
    """Vérifie le statut d'une tâche Seedream V4.5."""
    resp = requests.get(
        f"{BASE_URL}/ai/text-to-image/seedream-v4-5/{task_id}",
        headers=headers()
    )
    resp.raise_for_status()
    return resp.json().get("data", {})


def wait_and_download_overlay(task_id, dest_folder, filename, max_wait=120, interval=5):
    """Attend la fin d'une tâche Seedream et télécharge l'image générée."""
    dest_folder = Path(dest_folder)
    dest_folder.mkdir(parents=True, exist_ok=True)

    elapsed = 0
    while elapsed < max_wait:
        data = check_task_status(task_id)
        status = data.get("status", "UNKNOWN")

        if status == "COMPLETED":
            images = data.get("generated", [])
            if images:
                img_url = images[0]
                filepath = dest_folder / filename
                print(f"  ↓ Téléchargement overlay {filename}...")
                img_resp = requests.get(img_url, stream=True)
                img_resp.raise_for_status()
                with open(filepath, "wb") as f:
                    for chunk in img_resp.iter_content(chunk_size=8192):
                        f.write(chunk)
                print(f"  ✓ Overlay sauvegardé: {filepath}")
                return filepath
            else:
                print(f"  ✗ Tâche terminée mais aucune image générée")
                return None

        elif status == "FAILED":
            print(f"  ✗ Tâche échouée: {task_id}")
            return None

        print(f"  ⏳ En cours... ({elapsed}s / {max_wait}s)")
        time.sleep(interval)
        elapsed += interval

    print(f"  ✗ Timeout après {max_wait}s pour tâche {task_id}")
    return None


# ============================================================
# PROMPTS OVERLAYS DU PROJET
# ============================================================

OVERLAY_PROMPTS = {
    "overlay_01_A1_bandeau_titre": (
        "Professional video overlay graphic on transparent background, 9:16 vertical format. "
        "Centered horizontal banner with text 'FORMATION DRAINAGE LYMPHATIQUE' in bold white uppercase sans-serif font. "
        "Solid orange (#F07D00) rectangle background, height 110px, width 900px, rounded corners 8px. "
        "Clean, minimalist wellness branding. Orange and white only. No other elements."
    ),
    "overlay_02_G4_tag_localisation": (
        "Professional video overlay graphic on transparent background, 9:16 vertical format. "
        "Bottom-left location tag card: dark semi-transparent background (60% black) with orange left border 6px. "
        "White map pin icon 40px on left. Line 1: 'MARTINIQUE — ANTILLES' in bold orange (#F07D00) uppercase. "
        "Line 2: 'Prochaine session sur place' in smaller white (#CCCCCC) text. "
        "Clean, professional, wellness aesthetic."
    ),
    "overlay_03_G1_lower_third": (
        "Professional video lower third overlay on transparent background, 9:16 vertical format. "
        "Two stacked blocks bottom-left: Top block with 'SAMUEL PINCEAU' in bold white text on orange (#F07D00) background. "
        "Bottom block with 'Massothérapeute agréé · Québec' in white text on dark semi-transparent background. "
        "Clean broadcast-style lower third, professional wellness branding."
    ),
    "overlay_04_A3_statistique": (
        "Professional video overlay card on transparent background, 9:16 vertical format. "
        "Dark semi-transparent card (60% black) with orange (#F07D00) left border 6px, rounded corners 12px. "
        "Text: 'Rétention · Jambes lourdes · Récupération post-op' in bold white sans-serif font. "
        "Width 560px, padding 32px. Clean, premium health/wellness style."
    ),
    "overlay_05_C1_checklist_programme": (
        "Professional video checklist overlay on transparent background, 9:16 vertical format. "
        "Dark semi-transparent card (60% black) with orange (#F07D00) left border 6px, rounded corners 12px. "
        "Vertical list with orange checkmarks: "
        "'Connaître la lymphe', 'Comprendre la congestion', 'Pathologies de rétention', 'Ateliers pratiques'. "
        "Bold white text, orange bullet points. Clean wellness infographic style."
    ),
    "overlay_06_C1_checklist_techniques": (
        "Professional video checklist overlay on transparent background, 9:16 vertical format. "
        "Dark semi-transparent card (60% black) with orange (#F07D00) left border 6px, rounded corners 12px. "
        "Vertical list with orange checkmarks: "
        "'Réflexologie plantaire', 'Techniques de drainage', 'Palper-rouler & ventouse', 'B.A.-BA du massage'. "
        "Bold white text, orange bullet points. Clean wellness infographic style."
    ),
    "overlay_07_A2_credibilite": (
        "Professional video testimonial card overlay on transparent background, 9:16 vertical format. "
        "Dark semi-transparent card (60% black) with orange (#F07D00) left border 6px, rounded corners 12px. "
        "Large faded orange quotation marks top-left. "
        "Italic white text: '7 techniques maîtrisées · Agréé depuis 2018 · Clientèle fidèle aux Antilles'. "
        "Attribution line in orange: '— Samuel Pinceau · Formateur'. Premium, authentic wellness style."
    ),
    "overlay_08_F1_cta_inscription": (
        "Professional video CTA overlay on transparent background, 9:16 vertical format. "
        "Centered composition: Large orange (#F07D00) button with 'S INSCRIRE' in bold black text and arrow icon. "
        "Below: pill-shaped outline with 'spmassotherapeute.com' in white. "
        "Below: phone number '(581) 305-1499' in gray. "
        "Subtext: 'Places limitées — Formation en Martinique' in gray. Dynamic, inviting CTA design."
    ),
}


# ============================================================
# SÉQUENCES DE RECHERCHE B-ROLL
# ============================================================

BROLL_SEARCHES = {
    "martinique": [
        {"term": "martinique aerial tropical island", "type": "video", "orientation": "portrait", "count": 3},
        {"term": "caribbean turquoise sea tropical", "type": "video", "orientation": "portrait", "count": 2},
        {"term": "tropical vegetation lush green caribbean", "type": "video", "orientation": "portrait", "count": 2},
        {"term": "martinique sunset beach", "type": "photo", "orientation": "portrait", "count": 3},
    ],
    "massage": [
        {"term": "lymphatic drainage massage hands", "type": "video", "orientation": "portrait", "count": 3},
        {"term": "massage legs spa professional", "type": "video", "orientation": "portrait", "count": 2},
        {"term": "reflexology foot massage close up", "type": "video", "orientation": "portrait", "count": 2},
        {"term": "cupping therapy massage", "type": "video", "orientation": "portrait", "count": 2},
        {"term": "massage wellness spa tropical", "type": "photo", "orientation": "portrait", "count": 3},
    ],
}


# ============================================================
# COMMANDES PRINCIPALES
# ============================================================

def cmd_search_broll():
    """Recherche et affiche les résultats B-roll disponibles (sans télécharger)."""
    print("\n=== RECHERCHE B-ROLL ===\n")
    all_results = {}

    for category, searches in BROLL_SEARCHES.items():
        print(f"\n--- Catégorie: {category.upper()} ---")
        cat_results = []
        for search in searches:
            term = search["term"]
            search_type = search.get("type", "video")
            orientation = search.get("orientation")

            if search_type == "video":
                results = search_videos(term, limit=search["count"], orientation=orientation)
                for r in results:
                    cat_results.append({
                        "type": "video",
                        "id": r.get("id"),
                        "name": r.get("name", ""),
                        "duration": r.get("duration", ""),
                        "term": term,
                        "preview": r.get("previews", [{}])[0].get("url", "") if isinstance(r.get("previews"), list) else "",
                    })
            else:
                results = search_resources(term, limit=search["count"], content_type="photo", orientation=orientation)
                for r in results:
                    cat_results.append({
                        "type": "photo",
                        "id": r.get("id"),
                        "name": r.get("name", ""),
                        "term": term,
                    })

        all_results[category] = cat_results
        for i, r in enumerate(cat_results):
            print(f"  [{i+1}] {r['type'].upper()} #{r['id']} — {r.get('name', 'N/A')[:60]}")

    # Sauvegarder le manifeste
    manifest_path = PROJECT_DIR / "broll_search_results.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\n✓ Résultats sauvegardés dans {manifest_path}")
    return all_results


def cmd_download_broll():
    """Télécharge les B-roll depuis le manifeste de recherche."""
    manifest_path = PROJECT_DIR / "broll_search_results.json"
    if not manifest_path.exists():
        print("Lancez d'abord: python freepik_assistant.py search-broll")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        all_results = json.load(f)

    print("\n=== TÉLÉCHARGEMENT B-ROLL ===\n")
    for category, items in all_results.items():
        dest = BROLL_DIR / category
        print(f"\n--- {category.upper()} → {dest} ---")
        for item in items:
            try:
                if item["type"] == "video":
                    download_video(item["id"], dest)
                else:
                    download_resource(item["id"], "jpg", dest)
            except Exception as e:
                print(f"  ✗ Erreur pour #{item['id']}: {e}")


def cmd_generate_overlays():
    """Génère les 8 overlays via Seedream V4.5."""
    print("\n=== GÉNÉRATION DES OVERLAYS (Seedream V4.5) ===\n")
    tasks = {}

    # Sauvegarder les prompts
    for name, prompt in OVERLAY_PROMPTS.items():
        prompt_file = PROMPTS_DIR / f"{name}.txt"
        with open(prompt_file, "w", encoding="utf-8") as f:
            f.write(prompt)

    # Lancer toutes les générations
    for name, prompt in OVERLAY_PROMPTS.items():
        print(f"\n[{name}]")
        try:
            task_id = generate_overlay(prompt, aspect_ratio="social_story_9_16")
            tasks[name] = task_id
        except Exception as e:
            print(f"  ✗ Erreur: {e}")
            tasks[name] = None

    # Attendre et télécharger
    print("\n--- Attente des résultats ---\n")
    for name, task_id in tasks.items():
        if not task_id:
            continue
        print(f"\n[{name}]")
        wait_and_download_overlay(task_id, GENERATED_DIR, f"{name}.png")

    print("\n✓ Génération terminée. Overlays dans:", GENERATED_DIR)


def cmd_status():
    """Affiche l'état du dossier projet."""
    print(f"\n=== ÉTAT DU PROJET ===")
    print(f"Dossier: {PROJECT_DIR}\n")

    for subdir in ["b-roll/martinique", "b-roll/massage", "b-roll/samuel", "overlays/generated", "overlays/prompts", "audio", "export"]:
        d = PROJECT_DIR / subdir
        files = list(d.glob("*")) if d.exists() else []
        count = len([f for f in files if f.is_file()])
        print(f"  {subdir:30s} → {count} fichier(s)")


# ============================================================
# CLI
# ============================================================

def main():
    if len(sys.argv) < 2:
        print("""
Usage: python freepik_assistant.py <commande>

Commandes:
  search-broll       Rechercher les B-roll (Martinique + massage)
  download-broll     Télécharger les B-roll trouvés
  generate-overlays  Générer les 8 overlays via Seedream V4.5
  status             Afficher l'état du dossier projet

Pré-requis:
  export FREEPIK_API_KEY='votre_clé_ici'
""")
        return

    cmd = sys.argv[1].lower()
    if cmd == "search-broll":
        cmd_search_broll()
    elif cmd == "download-broll":
        cmd_download_broll()
    elif cmd == "generate-overlays":
        cmd_generate_overlays()
    elif cmd == "status":
        cmd_status()
    else:
        print(f"Commande inconnue: {cmd}")


if __name__ == "__main__":
    main()
