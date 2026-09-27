# Como instalar isso no seu perfil (glimaalv)

## 1. Crie o repositório especial
No GitHub, crie um repositório **público** chamado exatamente `glimaalv`
(igual ao seu usuário). Se já existir, pode usar o mesmo.

## 2. Copie estes arquivos para dentro dele
Mantenha esta estrutura de pastas:

```
glimaalv/
├── README.md
├── glimaalv-ascii.svg
├── info-card.svg
├── contrib-heatmap.svg      (placeholder até a 1ª execução do workflow)
├── scripts/
│   ├── requirements.txt
│   ├── prep_photo.py
│   ├── make_ascii_svg.py
│   ├── make_info_card.py
│   ├── fetch_contributions.py
│   ├── render_heatmap_svg.py
│   ├── source-photo.png     (sua foto original, guardada pra regerar depois)
│   └── source-prepped.png   (foto já com fundo removido)
├── data/
│   └── .gitkeep
└── .github/workflows/update-profile-art.yml
```

## 3. Suba pro GitHub
```bash
git init
git remote add origin https://github.com/glimaalv/glimaalv.git
git add .
git commit -m "profile: readme animado com ascii art, card e heatmap"
git branch -M main
git push -u origin main
```

## 4. Rode o workflow uma vez manualmente
Vá na aba **Actions** do repositório → workflow **"Update profile art"** →
**Run workflow**. Isso busca suas contribuições reais e substitui o
`contrib-heatmap.svg` placeholder pelo gráfico de verdade. Depois disso,
ele roda sozinho todo dia (cron `17 6 * * *`, ~06:17 UTC).

## 5. Confira seu perfil
Acesse `github.com/glimaalv` e veja o resultado. Se o retrato ASCII, o card
ou o heatmap não aparecerem, dê um "hard refresh" (Ctrl+Shift+R) — o GitHub
cacheia imagens do README por um tempo.

## Se quiser trocar a foto ou os textos depois
- Nova foto: `python scripts/prep_photo.py nova-foto.jpg` e depois
  `python scripts/make_ascii_svg.py`.
- Mudar cargo/stack/bio: edite as constantes no topo de
  `scripts/make_info_card.py` (`FIELDS` e `BIO`) e rode o script de novo.
- Antes de rodar os scripts localmente, instale as dependências:
  `pip install -r scripts/requirements.txt`.

## Limitações que vale saber
- A remoção de fundo em `prep_photo.py` é um flood fill simples (funciona
  bem porque sua foto tem fundo escuro contínuo), não um removedor de fundo
  por IA — se trocar de foto com fundo diferente, pode precisar ajustar o
  `BG_THRESHOLD` no início do arquivo.
- `fetch_contributions.py` depende do HTML público do GitHub, que pode
  mudar sem aviso. Se o workflow começar a falhar, o próprio GitHub Actions
  vai mostrar o erro na aba Actions.
