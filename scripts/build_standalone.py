#!/usr/bin/env python3
"""Build a 100% self-contained standalone index.html for Meteor Summon Showcase."""
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


def b64_webp_resized(rel_path: str, max_w: int = 960, quality: int = 86, preserve_alpha: bool = False) -> tuple[str, int, int, str]:
    full = os.path.join(REPO, rel_path)
    buf = io.BytesIO()
    with Image.open(full) as im:
        orig_w, orig_h = im.size
        mode = im.mode
        work = im.convert("RGBA" if preserve_alpha else "RGB")
        if orig_w > max_w:
            nh = max(1, int(orig_h * (max_w / orig_w)))
            work = work.resize((max_w, nh), Image.Resampling.LANCZOS)
        work.save(buf, "WEBP", quality=quality, method=6)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/webp;base64,{encoded}", orig_w, orig_h, mode


def build() -> None:
    report = json.load(open(f"{REPO}/data/verification_report.json", encoding="utf-8"))
    read_scene = json.load(open(f"{REPO}/data/read_scene.json", encoding="utf-8"))

    source_files = [
        ("meteor_showcase.gd", "godot_project/scenes/meteor_showcase.gd", "gdscript", "마법사 메테오 소환 시전·낙하·충격파·보스 피격 플래시 메인 타임라인"),
        ("meteor_showcase.tscn", "godot_project/scenes/meteor_showcase.tscn", "scene", "고딕 흑요석 결투장 + 마법사 + 보스 + 메테오 CPUParticles2D + HDR 씬"),
        ("vfx_director.gd", "godot_project/shared/scripts/vfx_director.gd", "gdscript", "감쇠 트라우마 셰이크, 충격파 레이어 분리, 겹침 방지 컷인 큐"),
        ("boss_dual_gauge.gd", "godot_project/shared/scripts/boss_dual_gauge.gd", "gdscript", "보스 HP(주황) + 잔상 트레일(아이보리) + 브레이크 게이지(화이트)"),
        ("squad_skill_runner.gd", "godot_project/shared/scripts/squad_skill_runner.gd", "gdscript", "스쿼드 쿨타임·브레이크 사이클 자동 스케줄러"),
        ("vfx_shockwave.gdshader", "godot_project/shared/shaders/vfx_shockwave.gdshader", "shader", "hint_screen_texture 기반 방사형 왜곡 + 색수차 충격파 셰이더"),
        ("vfx_additive_scroll.gdshader", "godot_project/shared/shaders/vfx_additive_scroll.gdshader", "shader", "HDR Emissive Bloom + UV 스크롤 가산 혼합 불꽃/마법진/꼬리"),
        ("vfx_hit_flash.gdshader", "godot_project/shared/shaders/vfx_hit_flash.gdshader", "shader", "캐릭터 림 아웃라인(마법사 시전) + 보스 피격 백색/황금 플래시"),
        ("vfx_dissolve_curse.gdshader", "godot_project/shared/shaders/vfx_dissolve_curse.gdshader", "shader", "노이즈 디졸브 + 글리치 + 보라색 저주 오라 셰이더"),
        ("ui_cutin_banner.gdshader", "godot_project/shared/shaders/ui_cutin_banner.gdshader", "shader", "사선 클리핑 평행사변형 스킬 컷인 배너 셰이더"),
        ("vfx_showcase.gd", "godot_project/scenes/vfx_showcase.gd", "gdscript", "베이스라인 셰이더/컷인 테스트 씬 스크립트"),
        ("vfx_showcase.tscn", "godot_project/scenes/vfx_showcase.tscn", "scene", "베이스라인 셰이더/컷인 테스트 씬"),
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

    custom_asset_specs = [
        ("mage_caster.png", "godot_project/assets/sprites/mage_caster.png", True, "홍염 대마법사 (Side-View Battle Sprite + clean_cutout.py)"),
        ("mage_cutin.png", "godot_project/assets/sprites/mage_cutin.png", False, "스킬 컷인 배너 일러스트 ('멸망의 메테오!!')"),
        ("boss_kardon.png", "godot_project/assets/sprites/boss_kardon.png", True, "저무는 카르돈 보스 스프라이트 (clean_cutout.py)"),
        ("meteor_rock.png", "godot_project/assets/sprites/meteor_rock.png", True, "용암 균열 화산 운석 본체 (clean_cutout.py)"),
        ("arena_bg.png", "godot_project/assets/textures/arena_bg.png", False, "고딕 흑요석 결투장 2.5D 배경 (1280×720)"),
    ]
    custom_sprites = []
    for name, rel_path, has_alpha, desc in custom_asset_specs:
        uri, ow, oh, mode = b64_webp_resized(rel_path, max_w=540, quality=88, preserve_alpha=has_alpha)
        custom_sprites.append({
            "name": name,
            "path": rel_path,
            "width": ow,
            "height": oh,
            "mode": mode,
            "bytes": os.path.getsize(os.path.join(REPO, rel_path)),
            "desc": desc,
            "dataUri": uri,
        })

    tex_meta = {
        "noise_fbm.png": "심리스 FBM 노이즈 (스크롤/왜곡)",
        "noise_voronoi.png": "보로노이 셀 노이즈 (불꽃/용암 균열)",
        "glow_radial.png": "방사형 HDR 코어 글로우",
        "spark_streak.png": "이방성 스파크 & 혜성 꼬리",
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
        ("f_0001.png", 1, 0.00, "0.00s — 대치 개시: 홍염 대마법사 vs 저무는 카르돈 (흑요석의 수호자)"),
        ("f_0007.png", 7, 0.20, "0.20s — 영창 개시: 마법사 발밑 2.5D 마법진 전개 + 지팡이 루비 코어 점화 + 컷인 진입"),
        ("f_0014.png", 14, 0.43, "0.43s — 상공 소환 포탈(Sky Rift) 개방 시작 + 보스 발밑 메테오 낙하지점 전조(Telegraph)"),
        ("f_0020.png", 20, 0.63, "0.63s — '멸망의 메테오!!' 아이 컷인 고정 + 하늘 마법진 & 타겟 링 가속"),
        ("f_0028.png", 28, 0.90, "0.90s — 메테오 발사 직전 최대 영창 에너지 집중"),
        ("f_0034.png", 34, 1.10, "1.10s — 상공 포탈에서 거대 용암 운석(MeteorRock) 출현 + 혜성 화염 꼬리 생성"),
        ("f_0038.png", 38, 1.23, "1.23s — 대각선 궤적을 따라 가속 강하 + HDR 화염 꼬리 & 불꽃 파티클(42 sparks) 비산"),
        ("f_0042.png", 42, 1.37, "1.37s — 보스 두상 직상방 강하 돌입 (낙하 스케일 확대 연출)"),
        ("f_0046.png", 46, 1.50, "1.50s — 타격 60ms 직전 초고속 낙하 임계 프레임"),
        ("f_0049.png", 49, 1.60, "1.60s — 메테오 직격! 보스 백색/황금 Hit-Flash + 1차 색수차 스크린 충격파(UI 미왜곡)"),
        ("f_0052.png", 52, 1.70, "1.70s — 2차 충격파 확산 + 용암 화염 기둥/폭발 돔 팽창 + 보스 넉백 리코일"),
        ("f_0056.png", 56, 1.83, "1.83s — 보스 HP 대폭 차감(-4350 HP / -520 Stagger) + 56개 방사형 스파크 분출"),
        ("f_0064.png", 64, 2.10, "2.10s — 폭발 여파 소강 & 보스 게이지 아이보리 잔상(Trailing Ghost) 드레인"),
        ("f_0076.png", 76, 2.50, "2.50s — 바닥 용암 크레이터 작열 잔광 유지 & 보스 스탠스 복귀"),
        ("f_0090.png", 90, 2.97, "2.97s — 90프레임(3.00s) 무오류 완결"),
    ]
    frames = []
    for fn, num, sec, caption in frames_meta:
        uri, _, _, _ = b64_webp_resized(f"assets/frames/{fn}", max_w=960, quality=84, preserve_alpha=False)
        frames.append({
            "name": fn,
            "path": f"assets/frames/{fn}",
            "frame": num,
            "timeSec": sec,
            "caption": caption,
            "dataUri": uri,
        })

    bundle = {
        "standalone": True,
        "report": report,
        "read_scene": read_scene,
        "sources": sources,
        "customSprites": custom_sprites,
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
  <title>Godot 4 Game Studio — Meteor Summon &amp; VFX Showcase (v1.1.0)</title>
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
        radial-gradient(1200px 600px at 15% -10%, rgba(255, 77, 109, 0.12), transparent 60%),
        radial-gradient(900px 500px at 88% 5%, rgba(255, 202, 87, 0.10), transparent 55%),
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
      background: linear-gradient(90deg, var(--crimson), var(--gold), var(--cyan), var(--violet));
    }}
    .eyebrow {{
      display: inline-flex; align-items: center; gap: 8px;
      font-size: 12px; font-weight: 700; letter-spacing: 0.08em;
      text-transform: uppercase; color: var(--gold); margin-bottom: 8px;
    }}
    h1 {{ margin: 0 0 8px; font-size: clamp(22px, 3.2vw, 34px); line-height: 1.2; letter-spacing: -0.02em; }}
    .subtitle {{ margin: 0; color: var(--muted); font-size: 14.5px; max-width: 840px; }}
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
      padding: 7px 12px; border-radius: 9px; background: rgba(255, 202, 87, 0.09);
      border: 1px solid rgba(255, 202, 87, 0.24); color: var(--text); font-size: 13px; font-weight: 600;
    }}
    .nav-pills a:hover {{ text-decoration: none; background: rgba(255, 202, 87, 0.18); border-color: var(--gold); }}
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
    button.btn:hover {{ border-color: var(--gold); background: rgba(255, 202, 87, 0.12); }}
    button.btn.active {{ border-color: var(--gold); background: rgba(255, 202, 87, 0.22); color: #fff; }}
    .scrubber-box {{ margin-top: 12px; padding: 12px; background: var(--bg-elev); border: 1px solid var(--border); border-radius: 10px; }}
    input[type="range"] {{ width: 100%; accent-color: var(--gold); cursor: pointer; }}
    .frame-caption {{ margin-top: 8px; font-size: 13px; color: var(--text); display: flex; justify-content: space-between; gap: 10px; flex-wrap: wrap; }}
    .frame-tag {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; color: var(--gold); font-weight: 700; }}
    .jump-pills {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 10px; }}
    .contact-sheet-img {{ width: 100%; border-radius: 10px; border: 1px solid var(--border); cursor: zoom-in; display: block; }}
    .tex-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(215px, 1fr)); gap: 12px; }}
    .tex-card {{ background: var(--bg-elev); border: 1px solid var(--border); border-radius: 12px; padding: 12px; display: flex; flex-direction: column; gap: 8px; }}
    .tex-preview {{
      height: 156px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08);
      display: flex; align-items: center; justify-content: center; padding: 8px; background: #0d0a10; overflow: hidden;
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
    .tex-name {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 13px; font-weight: 700; color: var(--gold); }}
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
      <div class="eyebrow">Godot 4 Game Studio · Meteor Summon Combat Showcase (v1.1.0)</div>
      <h1>홍염 대마법사 — '멸망의 메테오!!' 스킬 &amp; 운석 낙하 검증 리포트</h1>
      <p class="subtitle">
        신규 생성한 마법사(<code class="inline">mage_caster.png</code>)·컷인(<code class="inline">mage_cutin.png</code>)·보스(<code class="inline">boss_kardon.png</code>)·화산 운석(<code class="inline">meteor_rock.png</code>)·결투장(<code class="inline">arena_bg.png</code>) 에셋을 Godot 4.7.2 <code class="inline">Forward+</code> HDR 씬(<code class="inline">meteor_showcase.tscn</code>)으로 통합해 90프레임(3.00s) 시전→상공 소환→운석 낙하→대폭발 충격파를 렌더링 검증한 <strong>모바일/오프라인 단일 파일</strong> 리포트입니다.
      </p>
      <div class="badge-row" id="heroBadges"></div>
      <nav class="nav-pills">
        <a href="#sec-render">1. 메테오 영상 &amp; 타임라인</a>
        <a href="#sec-sheet">2. 6-Frame QA 시트</a>
        <a href="#sec-sprites">3. 생성 캐릭터 · 운석 · 배경 (5종)</a>
        <a href="#sec-mcp">4. MCP &amp; 렌더 검증 결과</a>
        <a href="#sec-textures">5. 절차적 VFX 텍스처 (8종)</a>
        <a href="#sec-code">6. 셰이더 &amp; GDScript 소스</a>
      </nav>
    </header>

    <section aria-label="핵심 검증 지표">
      <div class="kpi-grid" id="kpiGrid"></div>
    </section>

    <section id="sec-render">
      <div class="section-head">
        <h2>1. 메테오 소환 &amp; 운석 낙하 렌더 영상 + 프레임 스크러버</h2>
        <p class="section-desc">3.00초(90프레임 @ 30fps, 1280×720, Vulkan 1.4.335 llvmpipe Forward+)</p>
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
              <button class="btn" id="btnModeWebp" type="button">WebP 루프 (모바일)</button>
              <button class="btn" id="btnPlayToggle" type="button">재생/정지</button>
              <button class="btn speed-btn" data-speed="0.25" type="button">0.25x</button>
              <button class="btn speed-btn" data-speed="0.5" type="button">0.5x</button>
              <button class="btn speed-btn active" data-speed="1" type="button">1.0x</button>
            </div>
            <span class="tex-meta" id="videoTimeLabel">0.00s / 3.00s</span>
          </div>
          <p class="tex-meta" style="margin: 10px 0 0;">
            ※ <strong>연출 타임라인</strong>: 0.20s 아이 컷인(<code class="inline">멸망의 메테오!!</code>) → 0.42s 상공 포탈 + 바닥 2.5D 전조 → 0.92s 화산 운석 대각선 강하 → 1.56s 대폭발 기둥·스크린 충격파(HUD 미왜곡)·보스 히트 플래시 &amp; -4,350 HP 타격.
          </p>
        </div>

        <div class="card">
          <div class="stage-wrap">
            <img id="framePreview" alt="Selected Godot keyframe" style="cursor: zoom-in;" />
          </div>
          <div class="scrubber-box">
            <input id="frameSlider" type="range" min="0" max="14" value="6" />
            <div class="frame-caption">
              <span class="frame-tag" id="frameTag">f038 · 1.23s</span>
              <span id="frameText">로딩 중...</span>
            </div>
            <div class="toolbar" style="margin-top: 8px;">
              <button class="btn" id="btnAutoFrames" type="button">▶ 키프레임 슬라이드 재생</button>
              <span class="tex-meta">슬라이더/버튼으로 메테오 궤적·폭발 정밀 검수</span>
            </div>
            <div class="jump-pills" id="jumpPills"></div>
          </div>
        </div>
      </div>
    </section>

    <section id="sec-sheet">
      <div class="section-head">
        <h2>2. 자동 생성 6-Frame QA 컨택트 시트</h2>
        <p class="section-desc"><code class="inline">render_verify.sh</code>가 90프레임 캡처 직후 생성한 시각 검증 시트 (클릭 시 확대)</p>
      </div>
      <div class="card">
        <img id="contactSheetImg" class="contact-sheet-img" alt="6-frame meteor verification contact sheet" />
      </div>
    </section>

    <section id="sec-sprites">
      <div class="section-head">
        <h2>3. 신규 생성 2D 캐릭터 · 운석 · 컷인 · 배경 에셋 (5종)</h2>
        <div><button class="btn" id="btnToggleSpriteChecker" type="button">체커보드 투명 배경 토글</button></div>
      </div>
      <div class="tex-grid" id="spriteGrid"></div>
    </section>

    <section id="sec-mcp">
      <div class="section-head">
        <h2>4. MCP 정적/씬 검증 &amp; MovieMaker 렌더 텔레메트리</h2>
        <p class="section-desc">씬 및 스크립트 수정 후 재실행한 최종 검증 데이터</p>
      </div>
      <div class="card">
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>검증 항목</th>
                <th>실행 도구 / 명령</th>
                <th>관측 결과</th>
                <th>주요 검증 포인트</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><strong>1. 에셋 생성 &amp; 경량 알파 컷아웃</strong></td>
                <td><code class="inline">image-generator</code> + <code class="inline">clean_cutout.py</code></td>
                <td><span style="color:var(--green);font-weight:700;">PASS</span> · 5종 스프라이트/배경</td>
                <td>Pillow/NumPy 기반 CPU 경량 컷아웃(PyTorch/rembg 미사용)으로 마법사·보스·메테오 알파 외곽선 깔끔 추출</td>
              </tr>
              <tr>
                <td><strong>2. Godot MCP 정적/타입 검증</strong></td>
                <td><code class="inline">godot:validate_scripts (scope="all")</code></td>
                <td><span style="color:var(--green);font-weight:700;">PASS</span> · 5/5 files (<code class="inline">filesWithErrors: 0</code>)</td>
                <td>신규 <code class="inline">scenes/meteor_showcase.gd</code> 포함 전체 5개 GDScript 파싱/타입 오류 0건</td>
              </tr>
              <tr>
                <td><strong>3. 씬 트리 &amp; 2.5D 원근 검증</strong></td>
                <td><code class="inline">godot:read_scene("scenes/meteor_showcase.tscn")</code></td>
                <td><span style="color:var(--green);font-weight:700;">PASS</span> · <code class="inline">MeteorShowcase</code></td>
                <td>2.5D 바닥 마법진(<code class="inline">CastPlane</code>/<code class="inline">TelegraphPlane</code>) 부모 스케일 분리를 통해 타원 원근 회전 정상화</td>
              </tr>
              <tr>
                <td><strong>4. MovieMaker 90프레임 렌더링</strong></td>
                <td><code class="inline">render_verify.sh ... 90 30</code> (<code class="inline">godot-xvfb-run</code>)</td>
                <td><span style="color:var(--green);font-weight:700;">PASS</span> · 90 frames in 5s (CPU 0.29ms / GPU 31.51ms)</td>
                <td><code class="inline">f038</code> 운석 강하 궤적 정렬, <code class="inline">f049</code> 충격파·히트플래시·보스 게이지 차감 프레임 육안 검증 완료</td>
              </tr>
            </tbody>
          </table>
        </div>
        <details class="json-box">
          <summary>MCP <code class="inline">validate_scripts</code> &amp; <code class="inline">get_project_info</code> &amp; <code class="inline">render_verify</code> 실제 JSON 보기</summary>
          <pre id="mcpJsonPre"></pre>
        </details>
        <details class="json-box">
          <summary>MCP <code class="inline">read_scene("scenes/meteor_showcase.tscn")</code> 노드 트리 JSON 보기</summary>
          <pre id="sceneJsonPre"></pre>
        </details>
      </div>
    </section>

    <section id="sec-textures">
      <div class="section-head">
        <h2>5. 공용 절차적 VFX 텍스처 아틀라스 (8종)</h2>
        <div><button class="btn" id="btnToggleChecker" type="button">체커보드 투명 배경 토글</button></div>
      </div>
      <div class="tex-grid" id="texGrid"></div>
    </section>

    <section id="sec-code">
      <div class="section-head">
        <h2>6. 검증된 Godot 4 셰이더 &amp; GDScript 소스 코드</h2>
        <p class="section-desc">메테오 연출 씬 및 공용 파이프라인 전체 12개 파일</p>
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
      <div>Release v1.1.0 · Godot 4.7.2-stable · godot-mcp v3.1.0 (157 tools) · Bubblewrap Xvfb + Vulkan llvmpipe</div>
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
          {{ text: "v1.1.0 Meteor Summon Standalone HTML", cls: "gold" }},
          {{ text: "Godot " + env.godot_version, cls: "cyan" }},
          {{ text: env.renderer, cls: "cyan" }},
          {{ text: env.mcp_server, cls: "" }},
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
          {{ label: "Skill Showcase", value: "멸망의 메테오!!", cls: "gold", sub: "홍염 대마법사 시전 → 상공 포탈 운석 강하 · 대폭발" }},
          {{ label: "MCP Static Check", value: `${{val.fileCount}} / ${{val.fileCount}} PASS`, cls: "ok", sub: `Errors: ${{val.filesWithErrors}} (godot:validate_scripts)` }},
          {{ label: "MovieMaker Render", value: `${{rv.frames_captured}}f (${{rv.duration_sec.toFixed(1)}}s) in ${{rv.wall_time_sec}}s`, cls: "cyan", sub: `CPU ${{rv.cpu_avg_ms_per_frame.toFixed(2)}}ms · GPU ${{rv.gpu_avg_ms_per_frame.toFixed(2)}}ms / frame` }},
          {{ label: "Custom + VFX Assets", value: `${{data.customSprites.length}} Sprites / ${{data.textures.length}} VFX`, cls: "", sub: "5 Shaders + 2 CPUParticles2D + Shockwave" }}
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
          if (useWebp) timeLbl.textContent = "WebP 루프 (18fps · 3.00s)";
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
          const dur = Number.isFinite(video.duration) ? video.duration : 3.0;
          timeLbl.textContent = `${{video.currentTime.toFixed(2)}}s / ${{dur.toFixed(2)}}s`;
        }});

        // Frame scrubber
        const frames = data.frames;
        const slider = document.getElementById("frameSlider");
        const preview = document.getElementById("framePreview");
        const frameTag = document.getElementById("frameTag");
        const frameText = document.getElementById("frameText");
        const jumpPills = document.getElementById("jumpPills");
        const btnAutoFrames = document.getElementById("btnAutoFrames");
        slider.max = String(frames.length - 1);
        let currentFrameIdx = 6;
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
            }}, 380);
          }}
        }});
        selectFrame(6); // f038 Meteor Descent

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

        function renderAssetGrid(items, containerId, defaultChecker) {{
          const grid = document.getElementById(containerId);
          const boxes = [];
          items.forEach(item => {{
            const card = document.createElement("div");
            card.className = "tex-card";
            const box = document.createElement("div");
            box.className = "tex-preview" + (defaultChecker ? " checker" : "");
            const img = document.createElement("img");
            img.src = item.dataUri;
            img.alt = item.name;
            img.style.cursor = "zoom-in";
            img.addEventListener("click", () => openLightbox(item.dataUri));
            box.appendChild(img);
            boxes.push(box);

            const nm = document.createElement("div"); nm.className = "tex-name"; nm.textContent = item.name;
            const desc = document.createElement("div"); desc.style.fontSize = "12.5px"; desc.textContent = item.desc;
            const meta = document.createElement("div"); meta.className = "tex-meta";
            meta.textContent = `${{item.width}}×${{item.height}} · ${{item.mode}} · ${{(item.bytes / 1024).toFixed(1)}} KB`;
            card.append(box, nm, desc, meta);
            grid.appendChild(card);
          }});
          return boxes;
        }}

        const spriteBoxes = renderAssetGrid(data.customSprites, "spriteGrid", true);
        let spriteCheckerOn = true;
        document.getElementById("btnToggleSpriteChecker").addEventListener("click", (e) => {{
          spriteCheckerOn = !spriteCheckerOn;
          e.target.classList.toggle("active", spriteCheckerOn);
          spriteBoxes.forEach(b => b.classList.toggle("checker", spriteCheckerOn));
        }});

        const texBoxes = renderAssetGrid(data.textures, "texGrid", false);
        let checkerOn = false;
        document.getElementById("btnToggleChecker").addEventListener("click", (e) => {{
          checkerOn = !checkerOn;
          e.target.classList.toggle("active", checkerOn);
          texBoxes.forEach(b => b.classList.toggle("checker", checkerOn));
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
