# Création Vidéo — Workflow Automatisé

Workflow complet de pré-production vidéo assisté par IA, utilisant l'API Freepik pour sourcer les assets et générer les éléments graphiques.

## Prérequis

- **Python 3.10+** avec `requests` (`pip install requests`)
- **Clé API Freepik** : [https://www.freepik.com/developers](https://www.freepik.com/developers)
- **Navigateur web** pour l'export des overlays HTML/CSS

```bash
export FREEPIK_API_KEY="votre_clé_ici"
```

---

## Workflow en 7 étapes

### 1. Charger le document script

Chaque projet commence par un **document DOCX/PDF** fourni par le client, qui contient :
- Script voix off par segment (avec timing)
- Spécifications de chaque overlay (texte, police, taille, couleur, position, animation)
- Indications B-roll par segment
- Charte graphique (couleurs hex, polices, style)
- Notes de production (format, résolution, export)

> Ce document est la **source de vérité unique** du projet. Tout respecter à la lettre.

### 2. Rechercher et télécharger les B-roll

```bash
# Recherche de vidéos et photos pertinentes
python scripts/freepik_assistant.py search-broll

# Téléchargement des meilleurs clips en 720p (via previews)
python scripts/download_720p.py
```

**Points clés :**
- Les vidéos Freepik gratuites se téléchargent via les URLs de preview (720p, 1080p)
- Les vidéos premium retournent une erreur 403
- Le script organise les clips par segment du script (seg1_hook, seg2_constat, etc.)
- Filtres API : `term`, `order`, pas de filtre `orientation` sur l'endpoint `/videos`

### 3. Créer les overlays (HTML/CSS)

Les overlays sont créés en **HTML/CSS pur** — pas de génération IA (Seedream, Midjourney...).

```bash
# Lancer le serveur de prévisualisation
python -m http.server 8090 --directory overlays/html
```

Ouvrir `http://localhost:8090/index.html` dans le navigateur.

**Méthode :**
- Chaque overlay est un élément HTML en **1080×1920px** (format 9:16)
- Fond transparent réel (canal alpha) grâce à `html2canvas` avec `backgroundColor: null`
- Polices Google Fonts (Bebas Neue, Nunito)
- Bouton "Exporter PNG" pour chaque overlay → télécharge un PNG 1080×1920 transparent
- Le fond en damier dans la preview représente la transparence

**Structure d'un overlay :**
```html
<div class="overlay-frame" id="ov1" style="width:1080px;height:1920px;">
  <!-- Éléments positionnés en absolu selon les specs du script -->
</div>
```

### 4. Générer la voix off

```bash
python scripts/generate_voiceover.py
```

**Points clés :**
- API : `POST /v1/ai/voiceover/elevenlabs-turbo-v2-5`
- **Voix française de France uniquement** (pas d'accent québécois/canadien)
- Voice ID recommandé : `IKne3meq5aSn9XLyUdCD` (Charlie — homme français)
- Paramètres : stability 0.55, similarity_boost 0.5, speed 0.95
- Limite quotidienne API : ~4-6 segments/jour. Prévoir 2 jours si > 6 segments
- Texte avec accents UTF-8 supporté

### 5. Rechercher et télécharger les musiques

```bash
python scripts/freepik_assistant.py  # (ou script dédié)
```

**API Musique :**
- `GET /v1/music` — params : `q`, `genre`, `mood`, `include-premium`, `order_by`, `limit`
- `GET /v1/music/{id}/download` → retourne `download_url`
- Moods utiles : Peaceful, Happy, Energetic, Laid Back
- Choisir une piste qui couvre la durée de la vidéo

### 6. Rechercher et télécharger les effets sonores (SFX)

**API SFX :**
- `GET /v1/sound-effects` — params : `q`, `category`, `include-premium`, `order_by`, `limit`
- `GET /v1/sound-effects/{id}/download` → retourne `download_url`

**SFX types recommandés pour le montage :**

| Usage | Recherche |
|-------|-----------|
| Slide overlay | `whoosh`, `swoosh transition` |
| Apparition overlay | `pop notification`, `soft chime` |
| Changement B-roll | `smooth transition`, `cinematic hit` |
| Bouton CTA | `click ui` |
| Ambiance | `ocean waves`, selon le thème |

### 7. Organiser le dossier projet

```
nom_du_projet/
├── .gitignore              # Exclure les vidéos du repo
├── README.md               # Ce fichier
├── MONTAGE_GUIDE.md        # Guide de montage spécifique au projet
├── b-roll/
│   ├── categorie_1/        # Clips vidéo par catégorie (exclus du git)
│   └── categorie_2/
├── overlays/
│   ├── html/               # Sources HTML/CSS des overlays
│   │   └── index.html      # Page de prévisualisation et export
│   └── generated/          # PNG exportés (1080×1920, transparent)
├── audio/
│   ├── voixoff_seg*.mp3    # Voix off par segment
│   ├── music_*.mp3         # Musiques de fond
│   └── sfx/                # Effets sonores
│       └── sfx_*.mp3
├── export/                 # Vidéo finale
├── scripts/                # Scripts d'automatisation Python
│   ├── freepik_assistant.py
│   ├── download_720p.py
│   ├── generate_voiceover.py
│   └── regenerate_overlays.py
├── broll_search_results.json
├── free_videos_selection.json
└── music_search_results.json
```

---

## API Freepik — Référence rapide

| Endpoint | Méthode | Usage |
|----------|---------|-------|
| `/v1/resources` | GET | Recherche photos/vecteurs/PSD |
| `/v1/resources/{id}/download/{format}` | GET | Téléchargement ressource |
| `/v1/videos` | GET | Recherche vidéos |
| `/v1/videos/{id}/download` | GET | Téléchargement vidéo |
| `/v1/music` | GET | Recherche musique |
| `/v1/music/{id}/download` | GET | Téléchargement musique |
| `/v1/sound-effects` | GET | Recherche SFX |
| `/v1/sound-effects/{id}/download` | GET | Téléchargement SFX |
| `/v1/ai/voiceover/elevenlabs-turbo-v2-5` | POST | Génération voix off |
| `/v1/ai/voiceover/elevenlabs-turbo-v2-5/{task-id}` | GET | Status voix off |
| `/v1/ai/text-to-image/seedream-v4-5` | POST | Génération image IA |

**Auth** : Header `x-freepik-api-key`
**Filtres resources** : format `filters.content_type` (point, pas crochets)
**Filtres videos** : pas de filtre `orientation` disponible
**Previews vidéo** : disponibles en 4K, 1080p, 720p, 455px — utiliser 720p pour les B-roll

---

## Charte du projet actuel

- **Format** : 9:16 (1080×1920 px) — Facebook Reels
- **Orange** : #F07D00
- **Noir fond** : rgba(0,0,0,0.6)
- **Blanc** : #FFFFFF
- **Gris** : #CCCCCC / #6B6B6B
- **Police titres** : Bebas Neue
- **Police corps** : Nunito Bold / Regular
