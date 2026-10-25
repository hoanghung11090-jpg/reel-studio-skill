"""Tạo LUT .cube kiểu cinematic teal & orange cho video thể thao trong nhà."""
import sys, numpy as np

N = 33
g = np.linspace(0, 1, N)
b, gg, r = np.meshgrid(g, g, g, indexing="ij")    # thứ tự .cube: R chạy nhanh nhất
rgb = np.stack([r, gg, b], -1).reshape(-1, 3)

def lum(c):
    return c @ np.array([0.2126, 0.7152, 0.0722])

x = rgb.copy()
# sáng tối: S-curve nhẹ + nén vùng sáng chói
L = lum(x)[:, None]
s = L * L * (3 - 2 * L)
x = x + (s - L) * 0.45
x = np.where(x > 0.78, 0.78 + (x - 0.78) * 0.7, x)
x = np.clip(x - 0.015, 0, 1) * 1.015               # đen sâu hơn một chút
# giảm và đẩy xanh lá về xanh ngọc (sàn sân quá xanh)
gdom = np.clip(x[:, 1] - np.maximum(x[:, 0], x[:, 2]), 0, 1)[:, None]
L = lum(x)[:, None]
x = x + (L - x) * np.clip(gdom * 1.6, 0, 0.45)
x[:, 2:3] += gdom * 0.22
# split toning: tối → teal, sáng → cam
L = lum(x)[:, None]
x += (1 - L) ** 2 * np.array([-0.035, 0.008, 0.045]) + L ** 2 * np.array([0.05, 0.012, -0.045])
# tăng độ rực cho màu ấm (áo cam/đỏ, băng rôn)
warm = np.clip(x[:, 0] - x[:, 2], 0, 1)[:, None]
L = lum(x)[:, None]
x = L + (x - L) * (1 + 0.35 * warm)
x = np.clip(x, 0, 1)

with open(sys.argv[1], "w") as f:
    f.write('TITLE "Cinematic Sport Teal-Orange"\nLUT_3D_SIZE 33\n')
    for v in x:
        f.write(f"{v[0]:.6f} {v[1]:.6f} {v[2]:.6f}\n")
print("ok")
