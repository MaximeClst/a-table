# À table — Mon carnet alimentaire

Carnet web statique (HTML, CSS, JavaScript natifs) pour consulter un programme alimentaire de quatre journées, cocher sa liste de courses et suivre le batch cooking.

- `dist/` : site publié (aucune compilation requise)
- `dist/data.json` : données de l'édition V10 générées par `prepare_data.py`
- `dist/downloads/` : PDF A4 imprimables

Déploiement : Vercel, dossier de sortie `dist` (voir `vercel.json`).

Les valeurs nutritionnelles sont des estimations issues de références alimentaires (Ciqual 2025, étiquettes produits) et ne constituent pas un avis médical.
