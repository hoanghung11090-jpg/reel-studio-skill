---
name: reel-studio
description: Biến clip quay điện thoại (thể thao, gym, du lịch, sự kiện...) thành video Reels/TikTok ngắn sôi động dựng sẵn trong CapCut Pro — chỉnh màu phim cinematic (LUT teal-orange, 4 bước), tìm nhạc trend Việt Nam và cắt đoạn hay nhất khớp phách, dựng timeline với zoom bám người chính + hiệu ứng giật (stutter, rung, zoom punch), làm ảnh bìa có chữ. Dùng khi người dùng nhờ "chỉnh clip", "làm reel/highlight", "chỉnh màu phim/cinematic", "tìm nhạc trend", "hiệu ứng giật", "ảnh bìa Reels", hoặc gọi /reel-studio. Có thể làm riêng từng phần (chỉ màu, chỉ nhạc, chỉ ảnh bìa).
---

# Reel Studio: màu phim + nhạc trend + dựng Reels trong CapCut

Đã làm thành công với clip cầu lông 33 s (10/2026, CapCut Pro 9.6 Windows). Mẫu kết quả: `D:\test capcut claude\CauLong`
(clip cinematic, nhạc cắt, LUT, ảnh bìa, `plan_caulong.json`), project CapCut `clip caulong`.
Người dùng nói tiếng Việt, gọi "anh/chị". Trả lời ngắn, báo tiến độ từng bước.

Script: `scripts/` của skill này (`%USERPROFILE%\.claude\skills\reel-studio\scripts`), chạy `python -P <script>`.
Cần: `python -m pip install --user numpy imageio-ffmpeg pillow`. ffmpeg lấy từ `imageio_ffmpeg.get_ffmpeg_exe()`.
Ghi project CapCut: dùng draft mẫu `assets/ref_draft_content.json` (đã làm sạch); chỉ ghi khi KHÔNG có `.locked`;
draft ở `%USERPROFILE%\Downloads\CapCut Drafts\<tên project>` (CapCut đổi tên thư mục theo tên project khi đóng).
Thư mục làm việc: `D:\test capcut claude\<TenDuAn>` (tạo mới cho mỗi video).

## 0. Hỏi trước (gộp một lần)
Nơi đăng (Reels/TikTok 9:16 hay YouTube 16:9) · phong cách (sôi động/nhẹ nhàng) · **người chính là ai (màu áo)** ·
nhạc (bài cụ thể, hay để Claude chọn trend) · chữ/ảnh bìa. Người dùng nên tạo project CapCut, kéo clip vào (và bài
nhạc nếu có), **đóng project**, gửi tên → đọc `materials.videos/audios[].path` trong `draft_content.json` để lấy file.

## 1. Phân tích clip
```
python -P scripts/analyze_clip.py <clip> <out_dir>/sheet.jpg [--fps 4 --crop 600:640:0:780]
```
In chuyển động mỗi 0.5 s + điểm cắt/lia máy; Read contact sheet để xem nội dung. Xác định vị trí (x, y: 0..1 từ
trái/trên) của **người chính** theo từng đoạn. Không chắc pha quan trọng → HỎI giây cụ thể, đừng đoán.
**Mặc định giữ trọn footage**; chỉ bỏ đoạn khi người dùng nói dư thừa.

## 2. Màu phim cinematic (4 bước) + làm nét
```
python -P scripts/grade.py <clip> <out_dir>/<ten>_cinematic_v2.mp4 --focus <x>,<y> --compare <giây>
```
(1) hệ màu: điện thoại đã Rec.709 → bỏ qua; clip LOG (rất xám/phẳng) → báo cần LUT chuyển hệ của hãng máy.
(2) LUT `Cinematic_TealOrange.cube` (tối→xanh ngọc, sáng→ấm, giảm xanh lá, tăng áo cam/đỏ; tạo lại bằng
`make_lut.py <out.cube>` nếu cần chỉnh). (3) sáng tối: nén đèn chói, đen sâu. (4) vignette tâm ở người chính.
Read ảnh `_truoc_sau.jpg` kiểm tra. `--strength soft` cho kiểu nhẹ nhàng. Chép LUT cho người dùng (CapCut:
Điều chỉnh → LUT → Nhập). Gợi ý thêm nút "Làm cho video rõ nét hơn" của CapCut Pro.
**Không xoá file đang được project tham chiếu** (CapCut báo "Phương tiện bị mất") — tạo bản mới tên `_v2`, `_v3`.

## 3. Nhạc trend
- TikTok Creative Center không còn bảng nhạc công khai (cần đăng nhập). Dùng bảng công khai
  `https://charts.youtube.com/charts/TopShortsSongs/vn/weekly` qua Claude in Chrome; đọc bằng javascript_tool:
  duyệt shadowRoot tìm `YTMC-ENTRY-ROW`, lấy textContent (hạng, tên, nghệ sĩ, số tuần trong bảng).
- Lọc bài hợp video (thể thao/giật → phonk, funk, hardtekk, rap mạnh; nhẹ nhàng → pop/acoustic; bỏ tên tục tĩu),
  đề xuất 3–4 bài kèm lý do.
- KHÔNG tải nhạc từ TikTok/YouTube/web (bản quyền, nguồn không tin cậy). Người dùng thêm bài từ **kho nhạc CapCut**
  (tab Âm thanh) vào project rồi đóng project, hoặc đưa MP3 của họ. Nhắc: Reels có thể bị tắt tiếng nếu nhạc không
  có trong thư viện Instagram → chọn lại bài đó khi đăng.
```
python -P scripts/analyze_music.py <bài> <out_dir>/flux.npy          → BPM, 3 đoạn sôi động nhất
python -P scripts/music_cut.py <bài> <flux.npy> <out.mp3> <giây_gần_đoạn_hay> <bpm> <số_phách>
```
`music_cut` tự bắt đúng phách đầu ô nhịp, fade out 1.6 s, in ra giây bắt đầu thật — ghi lại để cắt lại khi đổi độ dài
(cắt lại bằng ffmpeg `-ss <start> -t <phách*60/bpm+1.2>` + afade). Bài phải đủ dài tính từ điểm bắt đầu.

## 4. Dựng Reels (khớp phách + hiệu ứng giật)
Viết `<out_dir>/plan.json` (định dạng ở docstring `scripts/highlight_build.py`); mẫu đã duyệt: `D:\test capcut claude\CauLong\plan_caulong.json`.
Quy tắc người dùng đã duyệt:
- tốc độ ≈ 1x (0.9–1.05), mọi điểm cắt đúng phách; tổng phách = số phách nhạc đã cắt;
- khung bám người chính: `scale` 1.25–1.35, `cx, cy` = vị trí người chính; người sát mép khung gốc →
  `kind: "calm"`, `scale: 1.0` (không zoom/rung) để không mất người;
- stutter chỉ ở đầu video, `reps` chẵn (2) để không lệch phách; rung + zoom giật 8% mỗi 2 phách (mặc định);
- đoạn lia máy có sẵn trong clip → giữ làm chuyển cảnh; tắt tiếng gốc của clip.
```
python -P scripts/highlight_build.py "<draft_dir>" <clip_cinematic_v2.mp4> <nhac.mp3> <plan.json> --bpm <bpm>
```
Nhờ người dùng mở project kiểm tra. Góp ý theo giây trên timeline → đổi sang giây nguồn, sửa plan, cắt lại nhạc nếu
độ dài đổi, chạy lại (script tự sao lưu `_backup_<thời gian>`).

## 5. Ảnh bìa
Contact sheet quanh pha đẹp nhất của người chính (`analyze_clip.py --fps 6 --crop ...`), xuất khung PNG full-res
(`ffmpeg -ss <t> -i clip_cinematic -frames:v 1 frame.png`), rồi:
```
python -P scripts/cover.py frame.png <out_dir>/anh_bia_reels.jpg --crop x0,y0,x1,y1 --spot x,y [--ball x,y] --title "14H TRƯA" --sub "ĐỐI ĐẦU VỚI CÁI NÓNG 35 ĐỘ"
```
crop đúng tỉ lệ 9:16; spot/ball tính trên ảnh 1080x1920 sau khi cắt. Read kiểm tra chữ không đè người/vệt bóng;
gửi bằng SendUserFile. Dùng: Instagram "Chỉnh sửa ảnh bìa → Thêm từ thư viện"; CapCut nút "Ảnh bìa" đầu timeline.

## 6. Giao
Gợi ý xuất 1080p · 30fps · MP4. Liệt kê file trong thư mục dự án (clip cinematic, nhạc cắt, LUT, ảnh bìa, plan.json).
