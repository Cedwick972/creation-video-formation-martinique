# Guide de Montage — Formation Drainage Lymphatique Martinique

## Projet
- **Client** : SP Massothérapie — Samuel Pinceau
- **Format** : Facebook Reel 9:16 (1080x1920 px)
- **Durée** : 90 secondes
- **Export** : MP4 H.264, 30 fps minimum

---

## Structure des segments

| # | Segment | Timing | B-roll | Overlays |
|---|---------|--------|--------|----------|
| 1 | HOOK | 0-10s | Plans aériens Martinique (seg1_hook_*) | #1 Bandeau Titre + #2 Tag Localisation |
| 2 | CONSTAT | 10-25s | Mains massage, jambes (seg2_constat_*) | #3 Lower Third + #4 Statistique |
| 3 | PROGRAMME | 25-45s | Atelier/explications (seg3_programme_*) | #5 Checklist Programme |
| 4 | TECHNIQUES | 45-60s | Réflexologie, ventouses (seg4_techniques_*) | #6 Checklist Techniques |
| 5 | FORMATEUR | 60-75s | Cadre tropical (seg5_cadre_*) | #7 Crédibilité |
| 6 | CTA | 75-90s | Coucher soleil (seg6_cta_*) | #8 CTA Inscription |

---

## Arborescence du projet

```
creation_video_formation_martinique/
├── b-roll/
│   ├── martinique/    # Segments 1, 5, 6 (plans aériens, nature, coucher soleil)
│   ├── massage/       # Segments 2, 3, 4 (drainage, réflexologie, ventouses)
│   └── samuel/        # Plans de Samuel face caméra (à tourner)
├── overlays/
│   ├── generated/     # 8 overlays PNG (Seedream V4.5)
│   └── prompts/       # Prompts utilisés pour la génération
├── audio/             # Voix off + musique
├── export/            # Vidéo finale
└── scripts/           # Scripts d'automatisation Freepik
```

---

## Charte graphique

- **Orange principal** : #F07D00
- **Noir fond** : rgba(0,0,0,0.6) — 60% opacité
- **Blanc texte** : #FFFFFF
- **Gris secondaire** : #CCCCCC / #6B6B6B
- **Police titres** : Bebas Neue
- **Police corps** : Nunito Bold / Regular
- **Bordure gauche** : 6px orange sur tous les overlays
- **Coins arrondis** : 8-12px

---

## Notes voix off

- Rythme : ~150 mots/min
- Total : ~250 mots (225-270)
- Ton : chaleureux, expert, inspiré
- Enregistrer en intérieur calme
