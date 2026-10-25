"""Chỉnh màu cinematic 4 bước + làm nét cho clip điện thoại; xuất ảnh so sánh trước/sau.

python grade.py <clip_in> <clip_out.mp4> [--lut Cinematic_TealOrange.cube] [--focus 0.3,0.55] [--size 1080x1920]
                [--strength normal|soft] [--compare t=20]
1. Hệ màu: điện thoại/máy thường đã Rec.709 → bỏ qua. Clip LOG (màu rất phẳng, xám) → báo người dùng, cần LUT chuyển hệ của hãng máy.
2. LUT/preset: mặc định Cinematic_TealOrange.cube (tạo bằng make_lut.py nếu chưa có).
3. Sáng tối: eq contrast/gamma + LUT đã nén vùng chói, đen sâu.
4. Mask: vignette tâm ở --focus (vị trí chủ thể, 0..1 từ trái/trên).
Kèm khử nhiễu nhẹ, phóng lên --size bằng lanczos, làm nét (cas + unsharp).
"""
import argparse, pathlib, subprocess, imageio_ffmpeg

ap = argparse.ArgumentParser()
ap.add_argument("src"); ap.add_argument("out")
ap.add_argument("--lut", default=str(pathlib.Path(__file__).with_name("Cinematic_TealOrange.cube")))
ap.add_argument("--focus", default="0.5,0.55")
ap.add_argument("--size", default="", help="WxH; bỏ trống = tự chọn 1080x1920 (dọc) hoặc 1920x1080 (ngang)")
ap.add_argument("--strength", choices=["normal", "soft"], default="normal")
ap.add_argument("--compare", type=float, default=None, help="giây lấy khung so sánh trước/sau")
a = ap.parse_args()
FF = imageio_ffmpeg.get_ffmpeg_exe()

lut = pathlib.Path(a.lut).resolve()
if not lut.exists():
    raise SystemExit(f"Chưa có LUT {lut} — chạy make_lut.py trước.")
info = subprocess.run([FF, "-i", a.src], capture_output=True, text=True).stderr
import re
w, h = map(int, re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", info).groups())
size = a.size or ("1080x1920" if h > w else "1920x1080")
SW, SH = size.split("x")
# tâm vignette chỉ lệch 40% về phía chủ thể — lệch hẳn sẽ làm góc đối diện đen đặc
fx, fy = (f"{0.5 + (float(v) - 0.5) * 0.4:.3f}" for v in a.focus.split(","))
sat, sharp = ("1.25", "0.9") if a.strength == "normal" else ("1.12", "0.6")
lut_arg = str(lut).replace("\\", "/").replace(":", "\\:")
vf = (f"hqdn3d=1:1:3:3,scale={SW}:{SH}:flags=lanczos,eq=contrast=1.1:saturation={sat}:gamma=0.97,"
      f"lut3d='{lut_arg}',vignette=angle=PI/6:x0=w*{fx}:y0=h*{fy},cas={sharp},unsharp=5:5:0.6:5:5:0")
subprocess.run([FF, "-y", "-loglevel", "error", "-i", a.src, "-vf", vf, "-c:v", "libx264", "-preset", "slow",
                "-crf", "15", "-pix_fmt", "yuv420p", "-an", a.out], check=True)
print("ok", a.out)
if a.compare is not None:
    cmp_path = str(pathlib.Path(a.out).with_name(pathlib.Path(a.out).stem + "_truoc_sau.jpg"))
    half = f"scale={int(SW)//2}:{int(SH)//2}"
    subprocess.run([FF, "-y", "-loglevel", "error", "-ss", str(a.compare), "-i", a.src, "-ss", str(a.compare), "-i", a.out,
                    "-filter_complex", f"[0:v]{half}[x];[1:v]{half}[y];[x][y]hstack", "-frames:v", "1", cmp_path], check=True)
    print("so sánh:", cmp_path)
