# 🐍 Snake Bamako - By Assataeur-OSS

Un Snake Game rétro fait en Python / Pygame avec musique !

🎮 **JOUER EN LIGNE ICI** : https://assataeur-oss.github.io/Snake/

## Fonctionnalités
- ✅ Musique de fond + effets sonores
- ✅ Contrôles tactiles + clavier (ZQSD / Flèches)
- ✅ Touche M pour couper le son
- ✅ Score et Game Over
- ✅ 100% Python

## Comment jouer en local
```bash
pip install pygame numpy
python main.py

### 2. Le plus important : Ton `deploy.yml` actuel ne va pas marcher pour un jeu Pygame

Pygame ne marche pas direct sur GitHub Pages. Il faut le convertir en web avec `pygbag`.

Va dans ton repo > `.github/workflows/deploy.yml` > clique sur le crayon pour éditer, et remplace TOUT par ça :

```yaml
name: Deploy Snake to GitHub Pages

on:
  push:
    branches: [ "Principale", "main" ]

permissions:
  contents: read
  pages: write
  id-token: write

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          
      - name: Install pygbag
        run: |
          pip install pygbag
          pip install pygame numpy
          
      - name: Build web version
        run: |
          pygbag --build main.py
          
      - name: Setup Pages
        uses: actions/configure-pages@v4
        
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: 'build/web'

  deploy:
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    needs: build
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
