"""Ảnh bìa Reels 1080x1920 từ một khung hình: cắt vùng người chơi, làm nổi người, vệt sáng quả cầu/bóng, chữ tiêu đề.

python cover.py <frame.png> <out.jpg> --crop x0,y0,x1,y1 --spot x,y [--ball x,y] --title "14H TRƯA" [--sub "..."]
- crop: vùng cắt trên khung gốc (nên đúng tỉ lệ 9:16); spot/ball: toạ độ trên ảnh 1080x1920 sau khi cắt.
- Chữ nằm trong vùng giữa 3:4 (y 240-1680) để lưới trang cá nhân Instagram không cắt mất.
"""
import argparse
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont, ImageChops

ap = argparse.ArgumentParser()
ap.add_argument("frame"); ap.add_argument("out")
ap.add_argument("--crop", required=True)
ap.add_argument("--spot", required=True)
ap.add_argument("--ball")
ap.add_argument("--title", required=True)
ap.add_argument("--sub", default="")
ap.add_argument("--title-color", default="255,186,28")
a = ap.parse_args()

W, H = 1080, 1920
F_BLACK = "C:/Windows/Fonts/seguibl.ttf"   # Segoe UI Black: đủ dấu tiếng Việt
crop = tuple(map(int, a.crop.split(",")))
px, py = map(int, a.spot.split(","))

im = Image.open(a.frame).convert("RGB").crop(crop).resize((W, H), Image.LANCZOS)
im = im.filter(ImageFilter.UnsharpMask(radius=3, percent=90, threshold=2))
im = ImageEnhance.Color(ImageEnhance.Contrast(im).enhance(1.18)).enhance(1.15)

mask = Image.new("L", (W, H), 0)
ImageDraw.Draw(mask).ellipse((px - 380, py - 520, px + 420, py + 470), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(160))
im = Image.composite(im, ImageEnhance.Brightness(ImageEnhance.Color(im).enhance(0.7)).enhance(0.45), mask)

grad = Image.new("L", (1, H))
for y in range(H):
    grad.putpixel((0, y), int(max(0, min(1, (y - 1150) / 500)) * 210))
im = Image.composite(Image.new("RGB", (W, H), (5, 10, 14)), im, grad.resize((W, H)))

if a.ball:
    sx, sy = map(int, a.ball.split(","))
    glow = Image.new("RGB", (W, H), 0); g = ImageDraw.Draw(glow)
    g.line([(sx, sy), (sx + 120, sy - 260)], fill=(255, 210, 90), width=26)
    g.ellipse((sx - 34, sy - 34, sx + 34, sy + 34), fill=(255, 240, 200))
    im = ImageChops.add(im, glow.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(im)
    d.line([(sx, sy), (sx + 120, sy - 260)], fill=(255, 246, 220), width=5)
    d.ellipse((sx - 9, sy - 9, sx + 9, sy + 9), fill="white")

def fit(s, max_w, size):
    while size > 20:
        f = ImageFont.truetype(F_BLACK, size)
        if ImageDraw.Draw(im).textlength(s, font=f) <= max_w:
            return f
        size -= 4
    return f

def text(xy, s, font, fill, stroke):
    sh = Image.new("RGBA", (W, H), 0)
    ImageDraw.Draw(sh).text((xy[0] + 8, xy[1] + 12), s, font=font, fill=(0, 0, 0, 170), anchor="mm")
    sh = sh.filter(ImageFilter.GaussianBlur(10)); im.paste(sh, (0, 0), sh)
    ImageDraw.Draw(im).text(xy, s, font=font, fill=fill, anchor="mm", stroke_width=stroke, stroke_fill=(10, 10, 10))

tc = tuple(map(int, a.title_color.split(",")))
if a.sub:
    text((W // 2, 1430), a.title, fit(a.title, 960, 240), tc, 12)
    ImageDraw.Draw(im).rounded_rectangle((W // 2 - 70, 1556, W // 2 + 70, 1564), 4, fill=(255, 120, 40))
    text((W // 2, 1625), a.sub, fit(a.sub, 940, 72), (255, 255, 255), 6)
else:
    text((W // 2, 1500), a.title, fit(a.title, 960, 240), tc, 12)
im.save(a.out, quality=95)
print("ok", a.out)
