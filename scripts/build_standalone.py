#!/usr/bin/env python3
"""Build a 100% self-contained standalone index.html with all assets inlined as data URIs."""
import base64
import io
import json
import os
from PIL import Image

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def b64_file(rel_path: str, mime: str) -> str:
    full = os.path.join(REPO, rel_path)
    with open(full, "rb") as f:
        encoded = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{encoded}"


def b64_webp_from_png(rel_path: str, quality: int = 90) -> str:
    full = os.path.join(REPO, rel_path)
    buf = io.BytesIO()
    with Image.open(full) as im:
        im.convert("RGB").save(buf, "WEBP", quality=quality, method=6)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/webp;base64,{encoded}"


def build() -> None:
    report = json.load(open(f"{REPO}/data/verification_report.json", encoding="utf-8"))
    read_scene = json.load(open(f"{REPO}/data/read_scene.json", encoding="utf-8"))

    source_files = [
        ("vfx_showcase.gd", "godot_project/scenes/vfx_showcase.gd", "gdscript", "2.5D VFX 테스트 씬 타임라인 (0.2s 컷인, 0.35s 컷인2, 0.72s 슬래시+충격파)"),
        ("vfx_director.gd", "godot_project/shared/scripts/vfx_director.gd", "gdscript", "히트스톱, 감쇠 트라우마 셰이크, 충격파 레이어 분리, 겹침 방지 컷인 큐"),
        ("boss_dual_gauge.gd", "godot_project/shared/scripts/boss_dual_gauge.gd", "gdscript", "보스 HP(주황) + 잔상 트레일(아이보리) + 브레이크 게이지(화이트)"),
        ("squad_skill_runner.gd", "godot_project/shared/scripts/squad_skill_runner.gd", "gdscript", "스쿼드 쿨타임·브레이크 사이클 자동 스케줄러"),
        ("vfx_shockwave.gdshader", "godot_project/shared/shaders/vfx_shockwave.gdshader", "shader", "hint_screen_texture 기반 방사형 왜곡 + 색수차 충격파 셰이더"),
        ("vfx_additive_scroll.gdshader", "godot_project/shared/shaders/vfx_additive_scroll.gdshader", "shader", "HDR Emissive Bloom + UV 스크롤 가산 혼합 마법진/기둥/검기"),
        ("vfx_dissolve_curse.gdshader", "godot_project/shared/shaders/vfx_dissolve_curse.gdshader", "shader", "노이즈 디졸브 + 글리치 + 보라색 저주 테두리 발광"),
        ("vfx_hit_flash.gdshader", "godot_project/shared/shaders/vfx_hit_flash.gdshader", "shader", "피격 순간 백색/발광 플래시 셰이더"),
        ("ui_cutin_banner.gdshader", "godot_project/shared/shaders/ui_cutin_banner.gdshader", "shader", "사선 클리핑 평행사변형 스킬 컷인 배너 셰이더"),
        ("vfx_showcase.tscn", "godot_project/scenes/vfx_showcase.tscn", "scene", "Forward+ HDR WorldEnvironment + ShockwaveLayer(1) + HudLayer(10)"),
    ]
    sources = []
    for name, rel_path, kind, desc in source_files:
        with open(os.path.join(REPO, rel_path), encoding="utf-8") as f:
            sources.append({
                "name": name,
                "path": rel_path,
                "kind": kind,
                "desc": desc,
                "content": f.read(),
            })

    tex_meta = {
        "noise_fbm.png": "심리스 FBM 노이즈 (스크롤/왜곡)",
        "noise_voronoi.png": "보로노이 셀 노이즈 (불기둥/균열)",
        "glow_radial.png": "방사형 HDR 코어 글로우",
        "spark_streak.png": "이방성 스파크 스트릭",
        "slash_arc.png": "테이퍼드 크림슨 검기 아크",
        "magic_zodiac.png": "12섹터 성좌 마법진 링",
        "smoke_puff.png": "카툰 연기 퍼프 알파 마스크",
        "shadow_oval.png": "바닥 접촉 타원 그림자",
    }
    textures = []
    for fn in sorted(os.listdir(f"{REPO}/assets/textures")):
        if not fn.endswith(".png"):
            continue
        p = f"{REPO}/assets/textures/{fn}"
        with Image.open(p) as im:
            w, h = im.size
            mode = im.mode
        textures.append({
            "name": fn,
            "path": f"assets/textures/{fn}",
            "width": w,
            "height": h,
            "mode": mode,
            "bytes": os.path.getsize(p),
            "desc": tex_meta.get(fn, "Procedural VFX texture"),
            "dataUri": b64_file(f"assets/textures/{fn}", "image/png"),
        })

    frames_meta = [
        ("f_0001.png", 1, 0.00, "초기 상태 — HDR 마법진(시안) · 황금 불기둥 · 저주 오라 · 보스 듀얼 게이지(8500/10000)"),
        ("f_0007.png", 7, 0.20, "0.20s — Left 슬롯 컷인 발동: 랜서 '성창의 가호!!' 슬라이드 인"),
        ("f_0012.png", 12, 0.37, "0.37s — Right 슬롯 컷인 동시 발동: 로즈 퀸 '마지막 왈츠!!' (좌/우 겹침 0%)"),
        ("f_0018.png", 18, 0.57, "0.57s — 양측 사선 컷인 배너 유지 + 마법진 회전 & 보로노이 불기둥 상승"),
        ("f_0022.png", 22, 0.70, "0.70s — 슬래시/충격파 직전 임계 프레임"),
        ("f_0024.png", 24, 0.77, "0.77s — 검기(SlashArc) + 스크린 왜곡 충격파(Shockwave) + 보스 HP(-1400)·브레이크(-180) 직격"),
        ("f_0027.png", 27, 0.87, "0.87s — 충격파 링 외곽 확산 (HudLayer 레이어 분리로 UI 왜곡 없음) + 카메라 트라우마"),
        ("f_0030.png", 30, 0.97, "0.97s — 충격파 소멸 단계 + 검기 잔광 페이드아웃"),
        ("f_0036.png", 36, 1.17, "1.17s — 보스 HP 아이보리 잔상(Trailing Ghost) 드레인 진행 + 컷인 퇴장 시작"),
        ("f_0042.png", 42, 1.37, "1.37s — 컷인 슬롯 복귀 및 게이지 안정화"),
        ("f_0048.png", 48, 1.57, "1.57s — 타격 후 정착 프레임 (HP 7100/10000 반영 완료)"),
        ("f_0054.png", 54, 1.77, "1.77s — 지속 셰이더 루프 검증 (마법진 회전 + HDR 글로우)"),
        ("f_0060.png", 60, 1.97, "1.97s — 60프레임 캡처 종료 (무오류 완결)"),
    ]
    frames = []
    for fn, num, sec, caption in frames_meta:
        frames.append({
            "name": fn,
            "path": f"assets/frames/{fn}",
            "frame": num,
            "timeSec": sec,
            "caption": caption,
            "dataUri": b64_webp_from_png(f"assets/frames/{fn}", quality=90),
        })

    bundle = {
        "standalone": True,
        "report": report,
        "read_scene": read_scene,
        "sources": sources,
        "textures": textures,
        "frames": frames,
        "media": {
            "demoMp4Uri": b64_file("assets/demo.mp4", "video/mp4"),
            "demoWebpUri": b64_file("assets/demo.webp", "image/webp"),
            "contactSheetUri": b64_file("assets/contact_sheet.jpg", "image/jpeg"),
        },
    }

    safe_json = json.dumps(bundle, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")

    html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Godot 4 Game Studio — Standalone Verification Showcase</title>
  <style>
    :root {{
      --bg: #0a0c12;
      --bg-elev: #111622;
      --bg-card: #161d2e;
      --bg-code: #0d111a;
      --border: #25304a;
      --text: #e8eef8;
      --muted: #93a3c0;
      --cyan: #3ee0ff;
      --gold: #ffca57;
      --crimson: #ff4d6d;
      --green: #38e59d;
      --violet: #b37cff;
      --radius: 14px;
      --shadow: 0 18px 48px rgba(0, 0, 0, 0.45);
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans KR", Roboto, sans-serif;
      background:
        radial-gradient(1200px 600px at 15% -10%, rgba(62, 224, 255, 0.10), transparent 60%),
        radial-gradient(900px 500px at 88% 5%, rgba(255, 77, 109, 0.10), transparent 55%),
        var(--bg);
      color: var(--text);
      line-height: 1.58;
      -webkit-text-size-adjust: 100%;
    }}
    a {{ color: var(--cyan); text-decoration: none; }}
    a:hover {{ text-decoration: underline; }}
    .container {{ max-width: 1240px; margin: 0 auto; padding: 24px 16px 64px; }}
    .hero {{
      background: linear-gradient(145deg, rgba(22, 29, 46, 0.96), rgba(13, 17, 27, 0.96));
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: 24px;
      box-shadow: var(--shadow);
      position: relative;
      overflow: hidden;
    }}
    .hero::after {{
      content: "";
      position: absolute;
      inset: 0 0 auto 0;
      height: 3px;
      background: linear-gradient(90deg, var(--cyan), var(--gold), var(--crimson), var(--violet));
    }}
    .eyebrow {{
      display: inline-flex; align-items: center; gap: 8px;
      font-size: 12px; font-weight: 700; letter-spacing: 0.08em;
      text-transform: uppercase; color: var(--cyan); margin-bottom: 8px;
    }}
    h1 {{ margin: 0 0 8px; font-size: clamp(22px, 3.2vw, 34px); line-height: 1.2; letter-spacing: -0.02em; }}
    .subtitle {{ margin: 0; color: var(--muted); font-size: 14.5px; max-width: 820px; }}
    .badge-row {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 16px; }}
    .badge {{
      display: inline-flex; align-items: center; gap: 6px; padding: 5px 11px;
      border-radius: 999px; font-size: 12px; font-weight: 600;
      background: rgba(255, 255, 255, 0.04); border: 1px solid var(--border); color: var(--text);
    }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; background: var(--green); box-shadow: 0 0 8px var(--green); }}
    .dot.cyan {{ background: var(--cyan); box-shadow: 0 0 8px var(--cyan); }}
    .dot.gold {{ background: var(--gold); box-shadow: 0 0 8px var(--gold); }}
    .nav-pills {{
      display: flex; flex-wrap: wrap; gap: 8px; margin-top: 18px; padding-top: 14px;
      border-top: 1px solid rgba(255,255,255,0.06);
    }}
    .nav-pills a {{
      padding: 7px 12px; border-radius: 9px; background: rgba(62, 224, 255, 0.08);
      border: 1px solid rgba(62, 224, 255, 0.22); color: var(--text); font-size: 13px; font-weight: 600;
    }}
    .nav-pills a:hover {{ text-decoration: none; background: rgba(62, 224, 255, 0.16); border-color: var(--cyan); }}
    section {{ margin-top: 28px; }}
    .section-head {{ display: flex; flex-wrap: wrap; justify-content: space-between; align-items: baseline; gap: 10px; margin-bottom: 12px; }}
    .section-head h2 {{ margin: 0; font-size: 19px; letter-spacing: -0.01em; }}
    .section-desc {{ margin: 0; color: var(--muted); font-size: 13px; }}
    .card {{
      background: var(--bg-card); border: 1px solid var(--border);
      border-radius: var(--radius); padding: 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.28);
    }}
    .kpi-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap: 12px; }}
    .kpi {{ background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 15px 16px; }}
    .kpi-label {{ font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); margin-bottom: 5px; }}
    .kpi-value {{ font-size: 21px; font-weight: 700; color: var(--text); margin-bottom: 3px; }}
    .kpi-sub {{ font-size: 12px; color: var(--muted); }}
    .kpi-value.ok {{ color: var(--green); }}
    .kpi-value.cyan {{ color: var(--cyan); }}
    .kpi-value.gold {{ color: var(--gold); }}
    .media-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }}
    @media (max-width: 920px) {{ .media-grid {{ grid-template-columns: 1fr; }} }}
    .stage-wrap {{
      position: relative; background: #05070b; border-radius: 10px; overflow: hidden;
      border: 1px solid #2b354f; aspect-ratio: 16 / 9;
    }}
    .stage-wrap video, .stage-wrap img {{ width: 100%; height: 100%; display: block; object-fit: contain; }}
    .hidden {{ display: none !important; }}
    .toolbar {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 8px; margin-top: 12px; }}
    .btn-group {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    button.btn {{
      appearance: none; border: 1px solid var(--border); background: var(--bg-elev);
      color: var(--text); padding: 7px 11px; border-radius: 8px; font-size: 12.5px;
      font-weight: 600; cursor: pointer; touch-action: manipulation;
    }}
    button.btn:hover {{ border-color: var(--cyan); background: rgba(62, 224, 255, 0.12); }}
    button.btn.active {{ border-color: var(--cyan); background: rgba(62, 224, 255, 0.22); color: #fff; }}
    .scrubber-box {{ margin-top: 12px; padding: 12px; background: var(--bg-elev); border: 1px solid var(--border); border-radius: 10px; }}
    input[type="range"] {{ width: 100%; accent-color: var(--cyan); cursor: pointer; }}
    .frame-caption {{ margin-top: 8px; font-size: 13px; color: var(--text); display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap; }}
    .frame-tag {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; color: var(--gold); font-weight: 700; }}
    .jump-pills {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
    .contact-sheet-img {{ width: 100%; border-radius: 10px; border: 1px solid var(--border); cursor: zoom-in; display: block; }}
    .tex-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(210px, 1fr)); gap: 12px; }}
    .tex-card {{ background: var(--bg-elev); border: 1px solid var(--border); border-radius: 12px; padding: 12px; display: flex; flex-direction: column; gap: 8px; }}
    .tex-preview {{
      height: 144px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);
      display: flex; align-items: center; justify-content: center; padding: 10px; background: #0d0a10; overflow: hidden;
    }}
    .tex-preview.checker {{
      background-color: #1f2430;
      background-image:
        linear-gradient(45deg, #2b3242 25%, transparent 25%),
        linear-gradient(-45deg, #2b3242 25%, transparent 25%),
        linear-gradient(45deg, transparent 75%, #2b3242 75%),
        linear-gradient(-45deg, transparent 75%, #2b3242 75%);
      background-size: 20px 20px;
      background-position: 0 0, 0 10px, 10px -10px, -10px 0;
    }}
    .tex-preview img {{ max-width: 100%; max-height: 100%; object-fit: contain; }}
    .tex-name {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; font-weight: 700; color: var(--cyan); }}
    .tex-meta {{ font-size: 12px; color: var(--muted); }}
    .table-wrap {{ overflow-x: auto; }}
    table {{ width: 100%; border-collapse: collapse; font-size: 13px; }}
    th, td {{ text-align: left; padding: 10px; border-bottom: 1px solid rgba(255,255,255,0.07); vertical-align: top; }}
    th {{ color: var(--muted); font-weight: 600; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.05em; }}
    code, pre {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace; }}
    code.inline {{ background: rgba(255,255,255,0.06); padding: 2px 6px; border-radius: 5px; font-size: 12px; color: var(--cyan); }}
    .tabs {{ display: flex; flex-wrap: wrap; gap: 6px; margin-bottom: 12px; }}
    .code-shell {{ background: var(--bg-code); border: 1px solid var(--border); border-radius: 12px; overflow: hidden; }}
    .code-bar {{
      display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px;
      padding: 10px 14px; background: rgba(255,255,255,0.03); border-bottom: 1px solid var(--border); font-size: 12.5px;
    }}
    pre.code-view {{ margin: 0; padding: 14px; max-height: 460px; overflow: auto; font-size: 12px; line-height: 1.5; color: #d7e2f4; white-space: pre; }}
    details.json-box {{ margin-top: 12px; background: var(--bg-elev); border: 1px solid var(--border); border-radius: 10px; padding: 10px 14px; }}
    details.json-box summary {{ cursor: pointer; font-weight: 600; font-size: 13px; color: var(--text); }}
    details.json-box pre {{ margin: 10px 0 0; max-height: 300px; overflow: auto; background: var(--bg-code); padding: 12px; border-radius: 8px; font-size: 11.5px; color: #c8d6ee; }}
    .lightbox {{
      position: fixed; inset: 0; background: rgba(5, 7, 12, 0.92); display: none;
      align-items: center; justify-content: center; padding: 20px; z-index: 999; cursor: zoom-out;
    }}
    .lightbox.open {{ display: flex; }}
    .lightbox img {{ max-width: 96vw; max-height: 92vh; border-radius: 10px; border: 1px solid var(--border); box-shadow: 0 24px 64px rgba(0,0,0,0.8); }}
    .error-banner {{
      margin-top: 14px; padding: 12px 14px; border-radius: 10px;
      background: rgba(255, 77, 109, 0.14); border: 1px solid var(--crimson); color: #ffd6de; font-size: 13px;
    }}
    footer {{
      margin-top: 38px; padding-top: 16px; border-top: 1px solid var(--border);
      color: var(--muted); font-size: 12.5px; display: flex; flex-wrap: wrap; justify-content: space-between; gap: 10px;
    }}
  </style>
</head>
<body>
  <div class="container">
    <noscript>
      <div class="error-banner">
        JavaScript가 차단된 뷰어에서는 인터랙티브 탭이 동작하지 않습니다. 모바일 다운로드 파일의 경우 Chrome 또는 Safari 브라우저로 열어 주세요.
      </div>
    </noscript>
    <div id="fatalError" class="error-banner hidden"></div>

    <header class="hero">
      <div class="eyebrow">Godot 4 Game Studio · Self-Contained Verification Report</div>
      <h1>Godot 4.7.2 + MCP VFX Pipeline Verification</h1>
      <p class="subtitle">
        전역 스킬 <code class="inline">godot4-game-studio</code>로 신규 프로젝트(<code class="inline">Godot4StudioShowcase</code>)를 스캐폴딩한 뒤,
        <code class="inline">godot-mcp</code>(157개 도구) 정적 검증과 <code class="inline">godot-xvfb-run</code> Vulkan Forward+ MovieMaker 렌더링(60프레임 @ 30fps)을 End-to-End 실행·검증한 <strong>오프라인/모바일 단일 파일 호환</strong> 리포트입니다.
      </p>
      <div class="badge-row" id="heroBadges"></div>
      <nav class="nav-pills">
        <a href="#sec-render">1. 렌더 영상 &amp; 프레임</a>
        <a href="#sec-sheet">2. 컨택트 시트</a>
        <a href="#sec-mcp">3. MCP &amp; WSL2 결과</a>
        <a href="#sec-textures">4. VFX 텍스처 (8종)</a>
        <a href="#sec-code">5. 셰이더 &amp; GDScript</a>
      </nav>
    </header>

    <section aria-label="핵심 검증 지표">
      <div class="kpi-grid" id="kpiGrid"></div>
    </section>

    <section id="sec-render">
      <div class="section-head">
        <h2>1. MovieMaker 렌더 영상 &amp; 프레임별 타임라인 검증</h2>
        <p class="section-desc">2.00초(60프레임 @ 30fps, 1280×720, Vulkan 1.4.335 llvmpipe Forward+)</p>
      </div>
      <div class="media-grid">
        <div class="card">
          <div class="stage-wrap">
            <video id="demoVideo" autoplay loop muted playsinline controls></video>
            <img id="demoWebp" class="hidden" alt="Animated WebP playback fallback" />
          </div>
          <div class="toolbar">
            <div class="btn-group">
              <button class="btn active" id="btnModeMp4" type="button">MP4 영상</button>
              <button class="btn" id="btnModeWebp" type="button">WebP 애니메이션 (모바일 호환)</button>
              <button class="btn" id="btnPlayToggle" type="button">재생/정지</button>
              <button class="btn speed-btn" data-speed="0.25" type="button">0.25x</button>
              <button class="btn speed-btn" data-speed="0.5" type="button">0.5x</button>
              <button class="btn speed-btn active" data-speed="1" type="button">1.0x</button>
            </div>
            <span class="tex-meta" id="videoTimeLabel">0.00s / 2.00s</span>
          </div>
          <p class="tex-meta" style="margin: 10px 0 0;">
            ※ <strong>핵심 확인 포인트</strong>: 0.20s·0.35s 연속 컷인 좌/우 슬롯 겹침 없음, 0.72s 충격파가 <code class="inline">ShockwaveLayer(layer 1)</code>에서만 왜곡되어 상단 보스 게이지(<code class="inline">HudLayer(layer 10)</code>) 및 컷인 텍스트가 찌그러지지 않음. (모바일 뷰어에서 MP4가 차단되면 자동으로 WebP 루프로 전환됩니다.)
          </p>
        </div>

        <div class="card">
          <div class="stage-wrap">
            <img id="framePreview" alt="Selected Godot keyframe" style="cursor: zoom-in;" />
          </div>
          <div class="scrubber-box">
            <input id="frameSlider" type="range" min="0" max="12" value="5" />
            <div class="frame-caption">
              <span class="frame-tag" id="frameTag">f024 · 0.77s</span>
              <span id="frameText">로딩 중...</span>
            </div>
            <div class="toolbar" style="margin-top: 8px;">
              <button class="btn" id="btnAutoFrames" type="button">▶ 키프레임 슬라이드 재생</button>
              <span class="tex-meta">슬라이더 또는 버튼으로 구간별 검수</span>
            </div>
            <div class="jump-pills" id="jumpPills"></div>
          </div>
        </div>
      </div>
    </section>

    <section id="sec-sheet">
      <div class="section-head">
        <h2>2. 자동 생성 6-Frame 검증 컨택트 시트</h2>
        <p class="section-desc"><code class="inline">render_verify.sh</code>가 프레임 캡처 직후 생성한 시각 QA 시트 (클릭 시 확대)</p>
      </div>
      <div class="card">
        <img id="contactSheetImg" class="contact-sheet-img" alt="6-frame verification contact sheet" />
      </div>
    </section>

    <section id="sec-mcp">
      <div class="section-head">
        <h2>3. MCP 정적/씬 검증 &amp; WSL2 격리 Xvfb 파이프라인 결과</h2>
        <p class="section-desc">실제 <code class="inline">godot</code> MCP 서버 호출 결과 및 구축 과정에서 발견·해결한 WSL2 이슈 요약</p>
      </div>
      <div class="card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>검증 계층</th>
                <th>실행 도구 / 명령</th>
                <th>관측 결과</th>
                <th>핵심 해결 내역 (테스트 중 발견)</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>1. 프로젝트 스캐폴딩 &amp; 리소스 임포트</strong></td>
                <td><code class="inline">scaffold_godot_project.sh</code></td>
                <td><span style="color:var(--green);font-weight:700;">PASS</span> · 8 textures / 5 shaders / 4 scripts / 1 scene</td>
                <td>초기 빈 프로젝트에서 <code class="inline">.godot/imported/</code> 미생성으로 인한 <code class="inline">No loader found for .png</code> 및 전역 클래스 미인식을 발견 → <code class="inline">--headless --import --quit</code> 자동화 패치 후 재검증 완료</td>
              </tr>
              <tr>
                <td><strong>2. Godot MCP 정적/타입 검사</strong></td>
                <td><code class="inline">godot:validate_scripts (scope="all")</code></td>
                <td><span style="color:var(--green);font-weight:700;">PASS</span> · 4/4 files (<code class="inline">filesWithErrors: 0</code>)</td>
                <td>WSL2 <code class="inline">DISPLAY=:0</code> 소켓 대기 행(30s hang)을 <code class="inline">mcp_config.json</code>에서 <code class="inline">DISPLAY</code> 제거로 차단하여 <code class="inline">&lt;1s</code> 응답 달성</td>
              </tr>
              <tr>
                <td><strong>3. 씬 트리 &amp; 메타데이터 파싱</strong></td>
                <td><code class="inline">godot:read_scene</code> · <code class="inline">godot:get_project_info</code></td>
                <td><span style="color:var(--green);font-weight:700;">PASS</span> · <code class="inline">VfxShowcase</code> (Forward+, 4.7.2.stable)</td>
                <td><code class="inline">WorldEnvironment(HDR Glow 0.95)</code> + <code class="inline">ShockwaveLayer(1)</code> + <code class="inline">HudLayer(10)</code> 트리 검증 완료</td>
              </tr>
              <tr>
                <td><strong>4. 그래픽 렌더링 &amp; 프레임 QA</strong></td>
                <td><code class="inline">render_verify.sh ... 60 30</code> (<code class="inline">godot-xvfb-run</code>)</td>
                <td><span style="color:var(--green);font-weight:700;">PASS</span> · 60 frames in 3s (CPU 0.60ms / GPU 30.42ms)</td>
                <td>WSLg Weston 주기적 Segfault(signal 11)로부터 독립된 사용자 영역 <code class="inline">bubblewrap + Xvfb</code>로 안정 캡처</td>
              </tr>
            </tbody>
          </table>
        </div>
        <details class="json-box">
          <summary>MCP <code class="inline">validate_scripts</code> &amp; <code class="inline">get_project_info</code> 실제 반환 JSON 보기</summary>
          <pre id="mcpJsonPre"></pre>
        </details>
        <details class="json-box">
          <summary>MCP <code class="inline">read_scene("scenes/vfx_showcase.tscn")</code> 노드 트리 JSON 보기</summary>
          <pre id="sceneJsonPre"></pre>
        </details>
      </div>
    </section>

    <section id="sec-textures">
      <div class="section-head">
        <h2>4. 절차적 VFX 텍스처 아틀라스 (8종)</h2>
        <div><button class="btn" id="btnToggleChecker" type="button">체커보드 투명 배경 토글</button></div>
      </div>
      <div class="tex-grid" id="texGrid"></div>
    </section>

    <section id="sec-code">
      <div class="section-head">
        <h2>5. 검증된 Godot 4 셰이더 &amp; GDScript 소스 코드</h2>
        <p class="section-desc">실제 프로젝트에 포함되어 컴파일·렌더링 검증을 통과한 원본 소스</p>
      </div>
      <div class="card">
        <div class="tabs" id="sourceTabs"></div>
        <div class="code-shell">
          <div class="code-bar">
            <div><strong id="codeTitle">-</strong><span class="tex-meta" id="codePath" style="margin-left:8px;"></span></div>
            <button class="btn" id="btnCopyCode" type="button">코드 복사</button>
          </div>
          <pre class="code-view" id="codeContent"></pre>
        </div>
      </div>
    </section>

    <footer>
      <div>Repository: <a href="https://github.com/slalglel3/godot4-studio-showcase" target="_blank" rel="noopener">github.com/slalglel3/godot4-studio-showcase</a></div>
      <div>Toolchain: Godot 4.7.2-stable · godot-mcp v3.1.0 (157 tools) · Bubblewrap Xvfb + Vulkan llvmpipe</div>
    </footer>
  </div>

  <div class="lightbox" id="lightbox" aria-hidden="true">
    <img id="lightboxImg" alt="Zoomed verification image" />
  </div>

  <script>window.GODOT_SHOWCASE_DATA = {safe_json};</script>
  <script>
    (function () {{
      try {{
        const data = window.GODOT_SHOWCASE_DATA;
        if (!data) throw new Error("Embedded GODOT_SHOWCASE_DATA is missing.");

        const rep = data.report;
        const env = rep.environment;
        const rv = rep.render_verify;
        const val = rep.mcp_validate_scripts;

        const badges = [
          {{ text: "Standalone Single-File HTML (Offline Ready)", cls: "" }},
          {{ text: "Godot " + env.godot_version, cls: "cyan" }},
          {{ text: env.renderer, cls: "cyan" }},
          {{ text: env.mcp_server, cls: "gold" }},
          {{ text: `GDScript ${{val.fileCount}}/${{val.fileCount}} Valid (0 Errors)`, cls: "" }},
          {{ text: `MovieMaker ${{rv.frames_captured}}f @ ${{env.fps}}fps (${{rv.wall_time_sec}}s)`, cls: "gold" }}
        ];
        const badgesEl = document.getElementById("heroBadges");
        badges.forEach(b => {{
          const span = document.createElement("span");
          span.className = "badge";
          const dot = document.createElement("span");
          dot.className = "dot" + (b.cls ? " " + b.cls : "");
          span.appendChild(dot);
          span.appendChild(document.createTextNode(b.text));
          badgesEl.appendChild(span);
        }});

        const kpis = [
          {{ label: "Godot Engine", value: "4.7.2-stable", cls: "cyan", sub: "Forward+ HDR Glow (Threshold 0.95)" }},
          {{ label: "MCP Static Check", value: `${{val.fileCount}} / ${{val.fileCount}} PASS`, cls: "ok", sub: `Errors: ${{val.filesWithErrors}} (godot:validate_scripts)` }},
          {{ label: "MovieMaker Render", value: `${{rv.frames_captured}}f in ${{rv.wall_time_sec}}s`, cls: "gold", sub: `CPU ${{rv.cpu_avg_ms_per_frame.toFixed(2)}}ms · GPU ${{rv.gpu_avg_ms_per_frame.toFixed(2)}}ms / frame` }},
          {{ label: "Assets & Shaders", value: `${{rep.mcp_project_info.structure.assets}} PNG / 5 Shader`, cls: "", sub: "Shockwave · Additive · Dissolve · Flash · Cut-in" }}
        ];
        const kpiGrid = document.getElementById("kpiGrid");
        kpis.forEach(k => {{
          const card = document.createElement("div");
          card.className = "kpi";
          const l = document.createElement("div"); l.className = "kpi-label"; l.textContent = k.label;
          const v = document.createElement("div"); v.className = "kpi-value " + k.cls; v.textContent = k.value;
          const s = document.createElement("div"); s.className = "kpi-sub"; s.textContent = k.sub;
          card.append(l, v, s);
          kpiGrid.appendChild(card);
        }});

        // Media setup (MP4 + WebP fallback)
        const video = document.getElementById("demoVideo");
        const webp = document.getElementById("demoWebp");
        const btnModeMp4 = document.getElementById("btnModeMp4");
        const btnModeWebp = document.getElementById("btnModeWebp");
        const timeLbl = document.getElementById("videoTimeLabel");
        video.src = data.media.demoMp4Uri;
        webp.src = data.media.demoWebpUri;
        document.getElementById("contactSheetImg").src = data.media.contactSheetUri;

        function setPlaybackMode(mode) {{
          const useWebp = mode === "webp";
          video.classList.toggle("hidden", useWebp);
          webp.classList.toggle("hidden", !useWebp);
          btnModeMp4.classList.toggle("active", !useWebp);
          btnModeWebp.classList.toggle("active", useWebp);
          if (useWebp) {{
            timeLbl.textContent = "WebP 루프 (24fps · 2.00s)";
          }}
        }}
        btnModeMp4.addEventListener("click", () => setPlaybackMode("mp4"));
        btnModeWebp.addEventListener("click", () => setPlaybackMode("webp"));
        video.addEventListener("error", () => setPlaybackMode("webp"));
        setTimeout(() => {{
          if (video.readyState === 0 && video.error) setPlaybackMode("webp");
        }}, 1500);

        document.getElementById("btnPlayToggle").addEventListener("click", () => {{
          setPlaybackMode("mp4");
          if (video.paused) video.play().catch(() => setPlaybackMode("webp")); else video.pause();
        }});
        document.querySelectorAll(".speed-btn").forEach(btn => {{
          btn.addEventListener("click", () => {{
            document.querySelectorAll(".speed-btn").forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            video.playbackRate = parseFloat(btn.dataset.speed);
          }});
        }});
        video.addEventListener("timeupdate", () => {{
          const dur = Number.isFinite(video.duration) ? video.duration : 2.0;
          timeLbl.textContent = `${{video.currentTime.toFixed(2)}}s / ${{dur.toFixed(2)}}s`;
        }});

        // Frame scrubber + auto-slideshow
        const frames = data.frames;
        const slider = document.getElementById("frameSlider");
        const preview = document.getElementById("framePreview");
        const frameTag = document.getElementById("frameTag");
        const frameText = document.getElementById("frameText");
        const jumpPills = document.getElementById("jumpPills");
        const btnAutoFrames = document.getElementById("btnAutoFrames");
        slider.max = String(frames.length - 1);
        let currentFrameIdx = 5;
        let autoTimer = null;

        function selectFrame(idx) {{
          currentFrameIdx = idx;
          const f = frames[idx];
          slider.value = String(idx);
          preview.src = f.dataUri;
          frameTag.textContent = `f${{String(f.frame).padStart(3, "0")}} · ${{f.timeSec.toFixed(2)}}s`;
          frameText.textContent = f.caption;
          Array.from(jumpPills.children).forEach((btn, i) => btn.classList.toggle("active", i === idx));
        }}

        frames.forEach((f, idx) => {{
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "btn";
          btn.textContent = `f${{String(f.frame).padStart(3, "0")}}`;
          btn.addEventListener("click", () => selectFrame(idx));
          jumpPills.appendChild(btn);
        }});
        slider.addEventListener("input", () => selectFrame(parseInt(slider.value, 10)));
        btnAutoFrames.addEventListener("click", () => {{
          if (autoTimer) {{
            clearInterval(autoTimer);
            autoTimer = null;
            btnAutoFrames.textContent = "▶ 키프레임 슬라이드 재생";
            btnAutoFrames.classList.remove("active");
          }} else {{
            btnAutoFrames.textContent = "■ 슬라이드 정지";
            btnAutoFrames.classList.add("active");
            autoTimer = setInterval(() => {{
              selectFrame((currentFrameIdx + 1) % frames.length);
            }}, 420);
          }}
        }});
        selectFrame(5);

        // Lightbox
        const lightbox = document.getElementById("lightbox");
        const lightboxImg = document.getElementById("lightboxImg");
        function openLightbox(src) {{
          lightboxImg.src = src;
          lightbox.classList.add("open");
        }}
        preview.addEventListener("click", () => openLightbox(preview.src));
        document.getElementById("contactSheetImg").addEventListener("click", (e) => openLightbox(e.target.src));
        lightbox.addEventListener("click", () => lightbox.classList.remove("open"));
        document.addEventListener("keydown", (e) => {{
          if (e.key === "Escape") lightbox.classList.remove("open");
        }});

        // MCP JSON
        document.getElementById("mcpJsonPre").textContent = JSON.stringify({{
          project_info: rep.mcp_project_info,
          validate_scripts: rep.mcp_validate_scripts,
          render_verify: rep.render_verify
        }}, null, 2);
        document.getElementById("sceneJsonPre").textContent = JSON.stringify(data.read_scene, null, 2);

        // Textures
        const texGrid = document.getElementById("texGrid");
        const previewBoxes = [];
        data.textures.forEach(t => {{
          const card = document.createElement("div");
          card.className = "tex-card";
          const box = document.createElement("div");
          box.className = "tex-preview";
          const img = document.createElement("img");
          img.src = t.dataUri;
          img.alt = t.name;
          img.style.cursor = "zoom-in";
          img.addEventListener("click", () => openLightbox(t.dataUri));
          box.appendChild(img);
          previewBoxes.push(box);

          const nm = document.createElement("div"); nm.className = "tex-name"; nm.textContent = t.name;
          const desc = document.createElement("div"); desc.style.fontSize = "12.5px"; desc.textContent = t.desc;
          const meta = document.createElement("div"); meta.className = "tex-meta";
          meta.textContent = `${{t.width}}×${{t.height}} · ${{t.mode}} · ${{(t.bytes / 1024).toFixed(1)}} KB`;
          card.append(box, nm, desc, meta);
          texGrid.appendChild(card);
        }});

        let checkerOn = false;
        document.getElementById("btnToggleChecker").addEventListener("click", (e) => {{
          checkerOn = !checkerOn;
          e.target.classList.toggle("active", checkerOn);
          previewBoxes.forEach(b => b.classList.toggle("checker", checkerOn));
        }});

        // Source code viewer
        const tabsEl = document.getElementById("sourceTabs");
        const codeTitle = document.getElementById("codeTitle");
        const codePath = document.getElementById("codePath");
        const codeContent = document.getElementById("codeContent");
        let activeSourceIdx = 0;

        function selectSource(idx) {{
          activeSourceIdx = idx;
          const s = data.sources[idx];
          codeTitle.textContent = s.desc;
          codePath.textContent = s.path;
          codeContent.textContent = s.content;
          Array.from(tabsEl.children).forEach((b, i) => b.classList.toggle("active", i === idx));
        }}
        data.sources.forEach((s, idx) => {{
          const btn = document.createElement("button");
          btn.type = "button";
          btn.className = "btn";
          btn.textContent = s.name;
          btn.addEventListener("click", () => selectSource(idx));
          tabsEl.appendChild(btn);
        }});
        selectSource(0);

        document.getElementById("btnCopyCode").addEventListener("click", async (e) => {{
          const s = data.sources[activeSourceIdx];
          try {{
            await navigator.clipboard.writeText(s.content);
            e.target.textContent = "복사됨!";
            setTimeout(() => {{ e.target.textContent = "코드 복사"; }}, 1200);
          }} catch (_) {{
            e.target.textContent = "수동 선택 복사";
          }}
        }});
      }} catch (err) {{
        const el = document.getElementById("fatalError");
        if (el) {{
          el.classList.remove("hidden");
          el.textContent = "리포트 초기화 오류: " + (err && err.message ? err.message : String(err));
        }}
      }}
    }})();
  </script>
</body>
</html>
"""

    out_path = os.path.join(REPO, "index.html")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Built standalone index.html: {os.path.getsize(out_path) / (1024 * 1024):.2f} MB")


if __name__ == "__main__":
    build()
