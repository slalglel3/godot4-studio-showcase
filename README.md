# Godot 4 Game Studio — Environment & VFX Verification Showcase

Godot **4.7.2-stable**, **godot-mcp (v3.1.0, 157 tools)**, **bubblewrap + Xvfb** 격리 렌더러, 그리고 `godot4-game-studio` 전역 스킬로 스캐폴딩부터 정적 검증·비주얼 프레임 검증까지 완료한 테스트 쇼케이스 저장소입니다.

## 바로 보기 (웹 / 모바일 단일 파일)
* **GitHub Pages (브라우저 바로 보기)**: https://slalglel3.github.io/godot4-studio-showcase/
* **GitHub Releases (`v1.0.0` 단일 파일 `index.html`)**: https://github.com/slalglel3/godot4-studio-showcase/releases/latest
  * `index.html`은 외부 의존성 없이 **모든 영상(MP4 + 모바일 WebP 루프)·13개 키프레임·컨택트 시트·8종 VFX 텍스처·MCP JSON·GDScript/Shader 소스가 Data URI로 내장된 완전 독립형(Standalone) 단일 HTML**입니다. 모바일에서도 단일 파일만 다운로드해 바로 실행할 수 있습니다.

## Verification Summary
* **Engine**: `Godot 4.7.2.stable.official.ed1daf0bf` (`Forward+`, HDR Glow)
* **GPU Backend**: `Vulkan 1.4.335 - llvmpipe (LLVM 21.1.8, 256 bits)` via `godot-xvfb-run`
* **MCP Validation (`godot:validate_scripts`)**: `4 / 4` GDScript files valid, `0` errors
* **MovieMaker Capture**: `60 frames @ 30 FPS` (`1280×720`, `2.00s`) rendered in `3s` (`CPU 0.60ms`, `GPU 30.42ms/frame`)

## Repository Structure
```text
.
├── index.html                    # Self-contained standalone dashboard (all assets inlined)
├── scripts/build_standalone.py   # Rebuilds standalone index.html from assets & source files
├── assets/
│   ├── demo.mp4                  # H.264 60-frame render capture
│   ├── demo.webp                 # Animated WebP fallback (24fps)
│   ├── contact_sheet.jpg         # 6-frame QA contact sheet
│   ├── frames/                   # 13 extracted keyframe PNGs (f_0001..f_0060)
│   └── textures/                 # 8 procedural VFX PNGs
├── data/
│   ├── verification_report.json
│   ├── read_scene.json
│   └── showcase_bundle.js
└── godot_project/                # Runnable Godot 4.7.2 project (scenes, shared shaders & scripts)
```
