"""Tìm phách mạnh gần đoạn sôi động nhất, cắt nhạc dài N phách + fade out."""
import sys, subprocess, numpy as np, imageio_ffmpeg

FF = imageio_ffmpeg.get_ffmpeg_exe()
song, flux_path, out, approx, bpm, beats = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6])
flux = np.load(flux_path); ofps = 22050 / 256
period = 60 / bpm

def score(t0, n=64):
    idx = ((t0 + np.arange(n) * period) * ofps).astype(int)
    idx = idx[idx < len(flux)]
    return flux[idx].mean()

# pha phách tốt nhất quanh vùng đã chọn
cands = approx - 2 + np.arange(0, 4, 0.005)
t_beat = cands[int(np.argmax([score(t) for t in cands]))]
# chọn phách đầu ô nhịp: trong 4 phách liên tiếp, phách có onset mạnh nhất qua 8 ô nhịp
bar_scores = [np.mean([flux[int((t_beat + (k + 4 * b) * period) * ofps)] for b in range(8)]) for k in range(4)]
start = t_beat + int(np.argmax(bar_scores)) * period
dur = beats * period + 1.2
subprocess.run([FF, "-y", "-loglevel", "error", "-ss", f"{start:.3f}", "-t", f"{dur:.3f}", "-i", song, "-vn",
                "-af", f"afade=t=in:d=0.05,afade=t=out:st={dur - 1.6:.3f}:d=1.6", "-b:a", "256k", out], check=True)
print(f"start={start:.3f}s period={period:.4f}s dur={dur:.2f}s")
