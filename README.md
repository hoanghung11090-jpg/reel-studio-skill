# reel-studio — Claude Code skill

Skill cho Claude Code: biến clip quay điện thoại (thể thao, gym, du lịch, sự kiện...) thành video **Reels/TikTok ngắn
sôi động**, dựng sẵn trong **CapCut Pro** (đã kiểm chứng trên CapCut 9.6 Windows):

- 🎨 **Màu phim cinematic** 4 bước: LUT teal & orange, nén vùng chói, tối viền quanh người chính, làm nét + lên 1080p
- 🎵 **Nhạc trend**: đọc bảng Top Shorts Songs Việt Nam, gợi ý bài hợp video, tìm đoạn hay nhất, đo BPM, cắt khớp phách
- ✂️ **Dựng Reels**: cắt đúng phách, khung bám người chính, hiệu ứng giật (stutter, rung, zoom punch)
- 🖼️ **Ảnh bìa** 1080×1920 có chữ tiêu đề, an toàn với lưới 3:4 của Instagram

## Cài đặt

1. Chép thư mục này vào `~/.claude/skills/reel-studio/` (Windows: `C:\Users\<tên>\.claude\skills\reel-studio\`).
2. Cài thư viện Python:
   ```bash
   python -m pip install --user numpy imageio-ffmpeg pillow
   ```
3. Cần: CapCut bản máy tính, Google Chrome + tiện ích **Claude in Chrome** (để đọc bảng xếp hạng nhạc).

## Dùng

Trong Claude Code gõ `/reel-studio` hoặc nhắn: *"Chỉnh clip cầu lông này thành reel sôi động, tôi mặc áo đen, tìm nhạc trend"*.
Bạn chỉ cần: tạo project CapCut, kéo clip (và bài nhạc chọn từ kho nhạc CapCut) vào, **đóng project**, gửi tên project.

## Nội dung

| File | Việc |
|---|---|
| `SKILL.md` | Quy trình từng bước cho Claude |
| `scripts/analyze_clip.py` | Chuyển động, điểm cắt cảnh, contact sheet có mốc giờ |
| `scripts/grade.py`, `make_lut.py`, `Cinematic_TealOrange.cube` | Chỉnh màu phim + làm nét, ảnh so sánh trước/sau |
| `scripts/analyze_music.py`, `music_cut.py` | BPM, đoạn sôi động nhất, cắt nhạc khớp phách |
| `scripts/highlight_build.py` | Ghi timeline Reels vào project CapCut đã đóng (theo `plan.json`) |
| `scripts/cover.py` | Ảnh bìa có chữ |
| `assets/ref_draft_content.json` | Draft CapCut mẫu đã làm sạch, dùng làm khuôn |

## Lưu ý

- Chỉ ghi khi project đã đóng trong CapCut (không có file `.locked`); script tự sao lưu trước khi ghi.
- Định dạng draft của CapCut không công khai và có thể đổi theo phiên bản.
- Skill không tải nhạc từ TikTok/YouTube. Hãy dùng nhạc trong kho CapCut hoặc nhạc bạn có quyền dùng.
