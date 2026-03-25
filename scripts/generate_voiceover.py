"""
Génération voix off — Voix française de France (Charlie, ElevenLabs)
A relancer quand la limite quotidienne API est réinitialisée.
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
HDR = {"x-freepik-api-key": API_KEY, "Content-Type": "application/json"}
AUDIO_DIR = Path(__file__).resolve().parent.parent / "audio"

# Voix Charlie — Homme français de France
VOICE_ID = "IKne3meq5aSn9XLyUdCD"

# Script voix off complet — 6 segments
SEGMENTS = [
    ("seg1_hook",
     "La Martinique, le soleil, la mer… et une opportunité unique pour transformer "
     "votre pratique. Je suis Samuel Pinceau, massothérapeute agréé depuis 2018 — "
     "et je reviens aux Antilles avec une formation exclusive."),

    ("seg2_constat",
     "Le drainage lymphatique, c'est l'une des techniques les plus demandées par vos "
     "clients. Rétention d'eau, jambes lourdes, récupération post-opératoire… En climat "
     "tropical, ces problématiques sont encore plus fréquentes. Pourtant, peu de "
     "praticiens maîtrisent les protocoles adaptés."),

    ("seg3_programme",
     "Cette formation, c'est un programme complet. Vous allez comprendre la lymphe, "
     "son fonctionnement, ce qui crée la congestion. Vous apprendrez à reconnaître "
     "les pathologies liées à la rétention. Et surtout — vous passerez à la pratique "
     "avec des ateliers concrets."),

    ("seg4_techniques",
     "Réflexologie plantaire, techniques de drainage, palper-rouler, ventouse… Chaque "
     "module est conçu pour être appliqué dès la première séance avec vos clients. "
     "On reprend aussi le B.A.-BA du massage pour solidifier vos fondations."),

    ("seg5_formateur",
     "Agréé depuis 2018, sept techniques maîtrisées, une clientèle fidèle ici aux "
     "Antilles. Je me déplace en Martinique deux fois par an pour accompagner mes "
     "clients — et maintenant, pour transmettre mon savoir-faire. Une formation en "
     "petit groupe, dans un cadre exceptionnel."),

    ("seg6_cta",
     "Les places sont limitées. Inscrivez-vous dès maintenant sur mon site — ou "
     "contactez-moi directement. Lien en description. On se retrouve en Martinique."),
]


def main():
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    print("=== GENERATION VOIX OFF (Charlie - Homme francais de France) ===\n")
    print(f"Voice ID: {VOICE_ID}")
    print(f"Dossier: {AUDIO_DIR}\n")

    tasks = {}
    for seg_name, text in SEGMENTS:
        print(f"[{seg_name}] Envoi...", end=" ", flush=True)
        try:
            resp = requests.post(
                f"{BASE_URL}/ai/voiceover/elevenlabs-turbo-v2-5",
                headers=HDR,
                json={
                    "text": text,
                    "voice_id": VOICE_ID,
                    "stability": 0.55,
                    "similarity_boost": 0.5,
                    "speed": 0.95,
                    "use_speaker_boost": True,
                }
            )
            if resp.status_code == 200:
                data = resp.json().get("data", {})
                task_id = data.get("task_id")
                print(f"OK (task: {task_id})")
                tasks[seg_name] = task_id
            elif resp.status_code == 429:
                print("LIMITE QUOTIDIENNE ATTEINTE — relancez demain")
                tasks[seg_name] = None
                break
            else:
                print(f"Erreur {resp.status_code}")
                tasks[seg_name] = None
        except Exception as e:
            print(f"Exception: {e}")
            tasks[seg_name] = None

    # Attendre et télécharger
    print("\n--- Attente des resultats ---\n")
    success = 0
    for seg_name, task_id in tasks.items():
        if not task_id:
            continue
        print(f"[{seg_name}]", end="", flush=True)
        for attempt in range(40):
            try:
                resp = requests.get(
                    f"{BASE_URL}/ai/voiceover/elevenlabs-turbo-v2-5/{task_id}",
                    headers={"x-freepik-api-key": API_KEY}
                )
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    status = data.get("status")
                    if status == "COMPLETED":
                        urls = data.get("generated", [])
                        if urls:
                            audio_resp = requests.get(urls[0], stream=True)
                            audio_resp.raise_for_status()
                            filepath = AUDIO_DIR / f"voixoff_{seg_name}.mp3"
                            with open(filepath, "wb") as f:
                                for chunk in audio_resp.iter_content(8192):
                                    f.write(chunk)
                            size_kb = filepath.stat().st_size / 1024
                            print(f" OK ({size_kb:.0f} KB)")
                            success += 1
                        break
                    elif status == "FAILED":
                        print(" ECHOUE")
                        break
                    else:
                        print(".", end="", flush=True)
                        time.sleep(3)
                else:
                    print(f" erreur {resp.status_code}")
                    break
            except Exception as e:
                print(f" exception: {e}")
                break

    print(f"\n=== {success}/{len(SEGMENTS)} segments generes ===")
    print(f"Fichiers dans: {AUDIO_DIR}")

    if success < len(SEGMENTS):
        print("\nNote: relancez ce script demain pour les segments manquants.")


if __name__ == "__main__":
    if not API_KEY:
        print("ERREUR: FREEPIK_API_KEY non definie")
        print("  export FREEPIK_API_KEY='votre_cle'")
        sys.exit(1)
    main()
