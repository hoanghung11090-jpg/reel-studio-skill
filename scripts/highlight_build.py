"""Dựng timeline highlight 9:16 khớp nhịp vào project CapCut ĐÃ ĐÓNG: zoom bám người chơi, lặp khung (stutter),
rung + zoom giật mỗi 2 phách.

python highlight_build.py <draft_dir> <video.mp4> <music.mp3> <plan.json> [--bpm 99.4] [--ref ...]

plan.json: danh sách đoạn theo thứ tự trên timeline, ví dụ
[
  {"stutter": 0.0, "len": 0.30, "reps": 2, "scale": 1.30, "cx": 0.15, "cy": 0.58},
  {"src": [0.0, 3.5], "beats": 6, "scale": 1.25, "cx": 0.15, "cy": 0.58, "kind": "push"},
  {"src": [3.5, 5.4], "beats": 3, "scale": 1.0, "kind": "calm"}
]
- cx, cy: vị trí người chơi chính trong khung gốc (0..1 tính từ trái/trên); khung tự giới hạn để không lộ mép.
- kind: push (đẩy zoom chậm), hold, outro (đẩy zoom chậm cuối), calm (không zoom/rung — dùng khi người chơi sát mép).
- stutter: lặp `reps` lần đoạn dài `len` giây bắt đầu ở giây `stutter`, mỗi lần nửa phách. Dùng reps chẵn để giữ đúng phách.
"""
import argparse, json, copy, uuid, pathlib, shutil, subprocess, re, time
import imageio_ffmpeg

SKILL_ASSETS = pathlib.Path(__file__).resolve().parents[1] / "assets"
ap = argparse.ArgumentParser()
ap.add_argument("draft", type=pathlib.Path)
ap.add_argument("video", type=pathlib.Path)
ap.add_argument("music", type=pathlib.Path)
ap.add_argument("plan", type=pathlib.Path)
ap.add_argument("--bpm", type=float, required=True)
ap.add_argument("--ref", type=pathlib.Path, default=SKILL_ASSETS / "ref_draft_content.json")
ap.add_argument("--punch", type=float, default=1.08, help="mức zoom giật")
ap.add_argument("--margin", type=float, default=0.045, help="chừa chỗ cho rung")
a = ap.parse_args()

FF = imageio_ffmpeg.get_ffmpeg_exe()
US = 1_000_000
BEAT = 60 / a.bpm
DRAFT = a.draft
if (DRAFT / ".locked").exists():
    raise SystemExit("Project đang mở trong CapCut — cần đóng project trước.")

def uid(): return str(uuid.uuid4()).upper()
def probe(p):
    r = subprocess.run([FF, "-i", str(p)], capture_output=True, text=True).stderr
    h, m, s = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r).groups()
    wh = re.search(r"Video:.*?(\d{2,5})x(\d{2,5})", r)
    return int((int(h) * 3600 + int(m) * 60 + float(s)) * US), (tuple(map(int, wh.groups())) if wh else None)

plan = json.loads(a.plan.read_text(encoding="utf-8-sig"))
ref = json.load(open(a.ref, encoding="utf-8"))
draft = json.load(open(DRAFT / "draft_content.json", encoding="utf-8"))
tl_files = list((DRAFT / "Timelines").glob("*/draft_content.json"))
bk = DRAFT / f"_backup_{time.strftime('%Y%m%d_%H%M%S')}"; bk.mkdir()
for f in [DRAFT / "draft_content.json", DRAFT / "draft_meta_info.json"] + tl_files:
    shutil.copy2(f, bk / (f.name if f.parent == DRAFT else f"timeline_{f.parent.name}.json"))

seg_tpl = {t["type"]: t["segments"][0] for t in ref["tracks"]}
track_tpl = {k: v for k, v in ref["tracks"][0].items() if k != "segments"}
mat = ref["materials"]
M = {k: [] for k in set(draft["materials"]) | set(mat)}

def helper(kind, **kw):
    o = copy.deepcopy(mat[kind][0]); o["id"] = uid(); o.update(kw); M[kind].append(o); return o["id"]

def kf(prop, pairs):
    return {"id": uid(), "material_id": "", "property_type": prop,
            "keyframe_list": [{"curveType": "Line", "graphID": "", "id": uid(), "left_control": {"x": 0.0, "y": 0.0},
                               "right_control": {"x": 0.0, "y": 0.0}, "time_offset": int(t), "values": [v]} for t, v in pairs]}

vdur, (vw, vh) = probe(a.video)
vm = copy.deepcopy(mat["videos"][0])
vm.update(id=uid(), type="video", path=str(a.video).replace("\\", "/"), material_name=a.video.name, duration=vdur,
          width=vw, height=vh, has_audio=False, local_material_id=str(uuid.uuid4()), unique_id="")
M["videos"].append(vm)

def center(s, cx, cy):
    lim = max(0.0, s - 1 - a.margin)
    return (max(-lim, min(lim, -(cx - 0.5) * 2 * s)), max(-lim, min(lim, (cy - 0.5) * 2 * s)))

JIT = [(0.03, -0.02), (-0.035, 0.025), (0.025, 0.02), (-0.015, -0.015), (0, 0)]

def video_seg(start, src0, dur, speed, s, cx, cy, kind):
    seg = copy.deepcopy(seg_tpl["video"])
    seg.update(id=uid(), material_id=vm["id"], speed=speed, volume=0.0, keyframe_refs=[], common_keyframes=[],
               target_timerange={"start": start, "duration": dur},
               source_timerange={"start": src0, "duration": int(dur * speed)})
    seg["extra_material_refs"] = [helper("speeds", speed=speed), helper("placeholder_infos"), helper("canvases"),
                                  helper("sound_channel_mappings"), helper("material_colors"), helper("vocal_separations")]
    x0, y0 = center(s, cx, cy) if s > 1 else (0.0, 0.0)
    seg["clip"]["scale"] = {"x": s, "y": s}; seg["clip"]["transform"] = {"x": x0, "y": y0}
    if kind == "calm":
        return seg
    sc, px, py, h = [], [], [], 0
    while h < dur - 0.25 * US:          # zoom giật + rung mỗi 2 phách
        sc += [(h, s * a.punch), (h + 0.2 * US, s)]
        for k, (jx, jy) in enumerate(JIT):
            px.append((h + k * 0.05 * US, x0 + jx)); py.append((h + k * 0.05 * US, y0 + jy))
        h += int(2 * BEAT * US)
    if kind in ("push", "outro"):
        end = s * (1.08 if kind == "push" else 1.12)
        sc = [(t, v * (1 + (end / s - 1) * t / dur)) for t, v in sc] + [(dur - 1, end)]
    else:
        sc.append((dur - 1, s))
    px.append((dur - 1, x0)); py.append((dur - 1, y0))
    seg["common_keyframes"] = [kf("KFTypeScaleX", sc), kf("KFTypeScaleY", sc),
                               kf("KFTypePositionX", px), kf("KFTypePositionY", py)]
    return seg

vsegs, t = [], 0
for p in plan:
    s, cx, cy = p.get("scale", 1.25), p.get("cx", 0.5), p.get("cy", 0.5)
    if "stutter" in p:
        d = int(BEAT / 2 * US)
        for r in range(p.get("reps", 2)):
            vsegs.append(video_seg(t, int(p["stutter"] * US), d, p.get("len", 0.3) / (BEAT / 2), s * (1 + 0.06 * r), cx, cy, "hold")); t += d
    else:
        (sa, sb), d = p["src"], int(p["beats"] * BEAT * US)
        vsegs.append(video_seg(t, int(sa * US), d, (sb - sa) * US / d, s, cx, cy, p.get("kind", "hold"))); t += d
TOTAL = t

mdur, _ = probe(a.music)
am = copy.deepcopy(mat["audios"][0])
am.update(id=uid(), path=str(a.music).replace("\\", "/"), name=a.music.stem, duration=mdur, music_id=str(uuid.uuid4()),
          type="extract_music", category_name="local_music", category_id="local")
M["audios"].append(am)
aseg = copy.deepcopy(seg_tpl["audio"])
ad = min(mdur, TOTAL + int(1.2 * US))
aseg.update(id=uid(), material_id=am["id"], volume=1.0, last_nonzero_volume=1.0, common_keyframes=[], keyframe_refs=[],
            target_timerange={"start": 0, "duration": ad}, source_timerange={"start": 0, "duration": ad})
aseg["extra_material_refs"] = [helper(k) for k in ("speeds", "placeholder_infos", "beats", "sound_channel_mappings", "vocal_separations")]

def track(kind, segs, idx):
    tr = copy.deepcopy(track_tpl); tr.update(id=uid(), type=kind, segments=segs)
    for s in segs: s["track_render_index"] = idx
    return tr

draft["tracks"] = [track("video", vsegs, 0), track("audio", [aseg], 1)]
draft["materials"] = M
draft["duration"] = max(TOTAL, ad)
portrait = vh > vw
draft["canvas_config"] = {"ratio": "9:16" if portrait else "16:9", "width": 1080 if portrait else 1920,
                          "height": 1920 if portrait else 1080, "background": None}
out = json.dumps(draft, ensure_ascii=False, separators=(",", ":"))
(DRAFT / "draft_content.json").write_text(out, encoding="utf-8")
for f in tl_files: f.write_text(out, encoding="utf-8")
meta = DRAFT / "draft_meta_info.json"
meta.write_text(re.sub(r'"tm_duration":\d+', f'"tm_duration":{draft["duration"]}', meta.read_text(encoding="utf-8")), encoding="utf-8")
print(f"ok: {len(vsegs)} đoạn, {TOTAL / US:.1f}s ({TOTAL / US / BEAT:.1f} phách); backup {bk.name}")
