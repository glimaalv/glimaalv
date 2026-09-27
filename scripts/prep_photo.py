#!/usr/bin/env python3
"""
prep_photo.py
Prepara uma foto para virar ASCII art:
  1. Remove o fundo escuro contínuo (flood fill a partir das bordas da imagem).
  2. Aplica CLAHE (contraste local) no rosto para realçar luz e sombra.
  3. Compõe o resultado sobre um fundo branco puro (fundo -> extremo "vazio" da rampa ASCII).

Uso:
    python scripts/prep_photo.py caminho/da/foto.png
Saída:
    scripts/source-prepped.png (grayscale, fundo branco)
"""
import sys
import os
import numpy as np
import cv2
from PIL import Image

BG_THRESHOLD = 45      # luminância abaixo disso é candidata a "fundo"
FLOOD_TOLERANCE = 18    # tolerância do flood fill (loDiff/upDiff)
OUTPUT_NAME = "source-prepped.png"


def remove_dark_background(bgr: np.ndarray) -> np.ndarray:
    """Marca como fundo a região escura conectada às bordas da imagem
    (flood fill a partir dos 4 cantos + meio das bordas) e pinta de branco."""
    h, w = bgr.shape[:2]
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)

    mask = np.zeros((h + 2, w + 2), dtype=np.uint8)
    flood_img = bgr.copy()

    seeds = [
        (0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1),
        (w // 2, 0), (0, h // 2), (w - 1, h // 2),
    ]
    for sx, sy in seeds:
        if gray[sy, sx] < BG_THRESHOLD:
            cv2.floodFill(
                flood_img, mask, (sx, sy), (255, 255, 255),
                loDiff=(FLOOD_TOLERANCE,) * 3,
                upDiff=(FLOOD_TOLERANCE,) * 3,
                flags=cv2.FLOODFILL_FIXED_RANGE,
            )

    # mask tem 1 nos pixels preenchidos (com borda extra de 1px)
    filled = mask[1:-1, 1:-1] > 0
    out = bgr.copy()
    out[filled] = (255, 255, 255)
    return out


def boost_local_contrast(gray: np.ndarray) -> np.ndarray:
    clahe = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8))
    return clahe.apply(gray)


def main():
    if len(sys.argv) < 2:
        print("Uso: python scripts/prep_photo.py caminho/da/foto.png")
        sys.exit(1)

    src_path = sys.argv[1]
    bgr = cv2.imread(src_path, cv2.IMREAD_COLOR)
    if bgr is None:
        raise FileNotFoundError(f"Não consegui abrir a imagem: {src_path}")

    no_bg = remove_dark_background(bgr)
    gray = cv2.cvtColor(no_bg, cv2.COLOR_BGR2GRAY)

    # Onde o pixel já virou branco puro (fundo), mantém branco;
    # no resto, aplica CLAHE para realçar o rosto.
    bg_mask = gray > 250
    enhanced = boost_local_contrast(gray)
    enhanced[bg_mask] = 255

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, OUTPUT_NAME)
    Image.fromarray(enhanced).save(out_path)
    print(f"OK -> {out_path}")


if __name__ == "__main__":
    main()
