#!/usr/bin/env python3
"""Фото -> шпалери для Пипа (466x466, RGB565) і, якщо хочете, одразу в брелок.
   python3 tools/wallpaper.py photo.jpg [--dim 0.6] [--zoom 1.0] [--out wallpaper.bin]
   python3 tools/wallpaper.py photo.jpg --flash [--addr 0x920000] [--port /dev/cu.usbmodem1101]
   python3 tools/wallpaper.py --clear --flash        (прибрати шпалери)
Формат файлу: ui/wallpaper.h (заголовок 16 байт + піксели RGB565 little endian). Адресу брелок пише в логу при
завантаженні ("wallpaper goes at flash 0x...") і в відповіді на команду config (поле "wall")."""
import argparse, struct, subprocess, sys
import numpy as np
from PIL import Image, ImageOps

S = 466
BAYER = np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]], np.float32) / 16 - 0.5

def fnv1a(b: bytes) -> int:
    h = 2166136261
    for x in b:
        h = ((h ^ x) * 16777619) & 0xFFFFFFFF
    return h

def convert(path, dim=0.6, zoom=1.0) -> bytes:
    im = ImageOps.exif_transpose(Image.open(path)).convert("RGB")
    side = min(im.size) / max(zoom, 1.0)  # the square that is cut out of the middle
    cx, cy = im.size[0] / 2, im.size[1] / 2
    im = im.crop((round(cx - side / 2), round(cy - side / 2), round(cx + side / 2), round(cy + side / 2))).resize((S, S), Image.LANCZOS)
    a = np.asarray(im, np.float32) * dim  # dimmed, so the labels stay readable
    d = np.tile(BAYER, (S // 4 + 1, S // 4 + 1))[:S, :S]  # ordered dither: no bands in the sky, no green tint in the greys
    r = np.clip(np.floor(a[..., 0] / 8 + d + 0.5), 0, 31).astype(np.uint16)
    g = np.clip(np.floor(a[..., 1] / 4 + d + 0.5), 0, 63).astype(np.uint16)
    b = np.clip(np.floor(a[..., 2] / 8 + d + 0.5), 0, 31).astype(np.uint16)
    px = ((r << 11) | (g << 5) | b).astype("<u2").tobytes()
    return b"PWL1" + struct.pack("<HHII", S, S, len(px), fnv1a(px)) + px

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("photo", nargs="?")
    ap.add_argument("--dim", type=float, default=0.6, help="яскравість 0.2..1 (менше = текст читається краще)")
    ap.add_argument("--zoom", type=float, default=1.0, help="1 = найбільший квадрат із середини, більше = ближче")
    ap.add_argument("--out", default="wallpaper.bin")
    ap.add_argument("--flash", action="store_true")
    ap.add_argument("--clear", action="store_true", help="записати порожній сектор: шпалер не буде")
    ap.add_argument("--addr", default="0x920000")
    ap.add_argument("--port")
    a = ap.parse_args()
    if a.clear:
        data = b"\xff" * 4096
    elif a.photo:
        data = convert(a.photo, a.dim, a.zoom)
    else:
        ap.error("потрібне фото або --clear")
    open(a.out, "wb").write(data)
    print(f"{a.out}: {len(data)} байт")
    cmd = [sys.executable, "-m", "esptool", "--chip", "esp32s3"] + (["--port", a.port] if a.port else []) + ["write_flash", a.addr, a.out]
    if a.flash:
        sys.exit(subprocess.call(cmd))
    print("прошити:", " ".join(cmd))

main()
