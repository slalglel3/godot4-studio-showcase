# Godot 4 Game Studio — Environment & VFX Verification Showcase

Godot **4.7.2-stable**, **godot-mcp (v3.1.0, 157 tools)**, **bubblewrap + Xvfb** 격리 렌더러, 그리고 `godot4-game-studio` 전역 스킬로 스캐폴딩부터 정적 검증·비주얼 프레임 검증까지 완료한 테스트 쇼케이스 저장소입니다.

## Live Showcase
* Interactive HTML Report (`index.html`): 실시간 H.264 렌더 영상, 13-Keyframe 타임라인 스크러버, 6-Frame QA 컨택트 시트, MCP 검증 JSON, 8종 절차적 VFX 텍스처 및 셰이더/GDScript 소스 인스펙터 포함

## Verification Summary
* **Engine**: `Godot 4.7.2.stable.official.ed1daf0bf` (`Forward+`, HDR Glow)
* **GPU Backend**: `Vulkan 1.4.335 - llvmpipe (LLVM 21.1.8, 256 bits)` via `godot-xvfb-run`
* **MCP Validation (`godot:validate_scripts`)**: `4 / 4` GDScript files valid, `0` errors
* **MovieMaker Capture**: `60 frames @ 30 FPS` (`1280×720`, `2.00s`) rendered in `3s` (`CPU 0.60ms`, `GPU 30.42ms/frame`)

## Repository Structure
```text
.
├── index.html                  # Self-contained interactive verification dashboard
├── assets/
│   ├── demo.mp4                # H.264 60-frame render capture
│   ├── contact_sheet.jpg       # 6-frame QA contact sheet
│   ├── frames/                 # 13 extracted keyframe PNGs (f_0001..f_0060)
│   └── textures/               # 8 procedural VFX PNGs
├── data/
│   ├── verification_report.json
│   ├── read_scene.json
│   └── showcase_bundle.js
└── godot_project/              # Runnable Godot 4.7.2 project (scenes, shared shaders & scripts)
```
