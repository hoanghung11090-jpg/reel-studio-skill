"""Phân tích bài nhạc: năng lượng mỗi 5 s, đoạn to nhất (dài --win giây), tempo (BPM); lưu onset envelope cho music_cut.py.

python analyze_music.py <bài hát (mp3/mp4/m4a...)> <flux.npy> [--win 20]
"""
import argparse, subprocess, numpy as np, imageio_ffmpeg

ap = argparse.ArgumentParser()
ap.add_argument("song"); ap.add_argument("flux_out")
ap.add_argument("--win", type=float, default=20)
a = ap.parse_args()
FF = imageio_ffmpeg.get_ffmpeg_exe()
SR = 22050
pcm = subprocess.run([FF, "-loglevel", "error", "-i", a.song, "-ac", "1", "-ar", str(SR), "-f", "s16le", "-"],
                     capture_output=True).stdout
x = np.frombuffer(pcm, np.int16).astype(np.float32) / 32768
hop = SR // 2
rms = np.array([np.sqrt(np.mean(x[i:i + hop] ** 2)) for i in range(0, len(x) - hop, hop)])
win = int(a.win * 2)
sm = np.convolve(rms, np.ones(win) / win, mode="valid")
order = np.argsort(sm)[::-1]
picks = []
for i in order:   # 3 đoạn to nhất, không chồng nhau
    if all(abs(i - j) >= win for j in picks):
        picks.append(i)
    if len(picks) == 3:
        break
print(f"bài dài {len(x)/SR:.1f}s")
print("đoạn sôi động nhất (giây bắt đầu):", ", ".join(f"{i*0.5:.1f}" for i in picks))
print("năng lượng mỗi 5s:", " ".join(f"{i*5}:{rms[i*10:i*10+10].mean():.3f}" for i in range(len(rms) // 10)))

n, hopo = 512, 256
frames = np.lib.stride_tricks.sliding_window_view(x, n)[::hopo]
spec = np.abs(np.fft.rfft(frames * np.hanning(n), axis=1))
flux = np.maximum(0, np.diff(np.log1p(spec), axis=0)).sum(1)
flux = (flux - flux.mean()) / flux.std()
ofps = SR / hopo
ac = np.correlate(flux, flux, "full")[len(flux) - 1:]
lags = np.arange(len(ac)) / ofps
mask = (lags > 60 / 180) & (lags < 60 / 70)
print(f"tempo ≈ {60 / lags[mask][np.argmax(ac[mask])]:.1f} BPM")
np.save(a.flux_out, flux)
