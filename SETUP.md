# Como instalar isso no seu perfil (glimaalv)

## 1. Crie o repositório especial
No GitHub, crie um repositório **público** chamado exatamente `glimaalv`
(igual ao seu usuário). Se já existir (seu caso), pode usar o mesmo.

## 2. Copie estes arquivos para dentro dele
Mantenha esta estrutura de pastas:

```
glimaalv/
├── README.md
├── glimaalv-ascii-dark.svg
├── glimaalv-ascii-light.svg
├── info-card-dark.svg
├── info-card-light.svg
├── contrib-heatmap-dark.svg     (placeholder até a 1ª execução do workflow)
├── contrib-heatmap-light.svg    (placeholder até a 1ª execução do workflow)
├── scripts/
│   ├── requirements.txt
│   ├── prep_photo.py
│   ├── make_ascii_svg.py
│   ├── make_info_card.py
│   ├── fetch_contributions.py
│   ├── render_heatmap_svg.py
│   ├── source-photo.png
│   └── source-prepped.png
├── data/
│   └── .gitkeep
└── .github/workflows/update-profile-art.yml
```

## 3. Suba pro GitHub
```bash
git add .
git commit -m "profile: readme com suporte a tema claro/escuro"
git push
```

## 4. Rode o workflow uma vez manualmente
Aba **Actions** → workflow **"Update profile art"** → **Run workflow**.
Isso gera o `contrib-heatmap-dark.svg` e o `contrib-heatmap-light.svg` de
verdade, com suas contribuições reais, no lugar dos placeholders. Depois
disso ele roda sozinho todo dia (cron `17 6 * * *`, ~06:17 UTC).

## Como funciona a troca automática de tema
O README usa a tag `<picture>` com `prefers-color-scheme`: o GitHub decide,
com base no tema (claro/escuro) que a pessoa está usando no site, qual dos
dois SVGs carregar — não precisa de JavaScript nem de nada externo.

## Se quiser trocar a foto ou os textos depois
Depois de editar `scripts/make_info_card.py` (campos `FIELDS`/`BIO`) ou
trocar a foto com `scripts/prep_photo.py`, gere as duas versões de novo:
```bash
pip install -r scripts/requirements.txt

python scripts/prep_photo.py nova-foto.jpg
THEME=dark  python scripts/make_ascii_svg.py
THEME=light python scripts/make_ascii_svg.py

THEME=dark  python scripts/make_info_card.py
THEME=light python scripts/make_info_card.py
```

## Limitações que vale saber
- A remoção de fundo em `prep_photo.py` é um flood fill simples (funciona
  bem porque sua foto tem fundo escuro contínuo), não um removedor de fundo
  por IA.
- `fetch_contributions.py` depende do HTML público do GitHub, que pode
  mudar sem aviso. Se o workflow começar a falhar, a aba Actions mostra o
  erro.
