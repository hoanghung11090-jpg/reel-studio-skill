"""Phân tích clip: chuyển động mỗi 0.5 s, điểm cắt cảnh/lia máy; xuất contact sheet có mốc thời gian để xem nội dung.

python analyze_clip.py <clip.mp4> <sheet.jpg> [--fps 1] [--crop w:h:x:y]
"""
import argparse, subprocess, numpy as np, imageio_ffmpeg

ap = argparse.ArgumentParser()
ap.add_argument("clip"); ap.add_argument("sheet")
ap.add_argument("--fps", type=float, default=1)
ap.add_argument("--crop", default="", help="chỉ xem một vùng, vd 600:640:0:780")
a = ap.parse_args()
FF = imageio_ffmpeg.get_ffmpeg_exe()

info = subprocess.run([FF, "-i", a.clip], capture_output=True, text=True).stderr
fps = float(next(t for t in info.split(",") if " fps" in t).split()[0])
W, H = 90, 160
raw = subprocess.run([FF, "-loglevel", "error", "-i", a.clip, "-vf", f"scale={W}:{H},format=gray", "-f", "rawvideo", "-"],
                     capture_output=True).stdout
fr = np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)
diff = np.abs(np.diff(fr, axis=0)).mean(axis=(1, 2))
cut = np.where(diff > diff.mean() + 4 * diff.std())[0] / fps
print(f"dài {len(fr) / fps:.1f}s, {fps:.2f} fps")
print("cắt cảnh/lia máy quanh (s):", np.round(np.unique(np.round(cut, 1)), 1))
step = int(round(fps / 2))
print("chuyển động mỗi 0.5s:", " ".join(f"{i*0.5:.1f}:{diff[i*step:(i+1)*step].mean():.1f}" for i in range(len(diff) // step)))

n = int(len(fr) / fps * a.fps)
cols = 12 if n > 36 else 11
rows = -(-n // cols)
vf = f"fps={a.fps}," + (f"crop={a.crop}," if a.crop else "") + "scale=160:-1," \
     f"drawtext=text='%{{pts\\:hms}}':x=3:y=3:fontsize=14:fontcolor=yellow:box=1:boxcolor=black:" \
     f"fontfile='C\\:/Windows/Fonts/arial.ttf',tile={cols}x{rows}"
subprocess.run([FF, "-y", "-loglevel", "error", "-i", a.clip, "-vf", vf, "-frames:v", "1", a.sheet], check=True)
print("contact sheet:", a.sheet)
