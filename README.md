# Godot 4 Game Studio — Meteor Summon & VFX Showcase

Godot **4.7.2-stable**, **godot-mcp (v3.1.0, 157 tools)**, **bubblewrap + Xvfb** 격리 렌더러, 그리고 `godot4-game-studio` 전역 스킬 기반으로 신규 **홍염 대마법사 캐릭터 + '멸망의 메테오!!' 운석 소환 스킬**까지 End-to-End 구현 및 검증한 저장소입니다.

## 바로 보기 (웹 / 모바일 단일 파일)
* **GitHub Releases (`v1.1.0` 메테오 쇼케이스 단일 파일 `index.html`)**: https://github.com/slalglel3/godot4-studio-showcase/releases/latest
* **GitHub Pages (브라우저 바로 보기)**: https://slalglel3.github.io/godot4-studio-showcase/
  * `index.html`은 외부 의존성 없이 **H.264 MP4 + 모바일 호환 WebP 루프 + 15개 키프레임 + 6-Frame QA 시트 + 생성 캐릭터/운석/배경 5종 + 공용 VFX 8종 + MCP JSON + 12개 GDScript/Shader/Scene 원본**을 모두 Data URI로 내장한 완전 독립형(Standalone) 단일 HTML입니다.

## Verification Summary (`v1.1.0` Meteor Showcase)
* **Main Scene**: `res://scenes/meteor_showcase.tscn`
* **Engine & Renderer**: `Godot 4.7.2.stable.official.ed1daf0bf` (`Vulkan 1.4.335 - Forward+ - llvmpipe`)
* **MCP Validation (`godot:validate_scripts`)**: `5 / 5` GDScript files valid, `0` errors (`meteor_showcase.gd`, `vfx_showcase.gd`, `vfx_director.gd`, `boss_dual_gauge.gd`, `squad_skill_runner.gd`)
* **MovieMaker Capture**: `90 frames @ 30 FPS` (`1280×720`, `3.00s`) rendered in `5s` (`CPU 0.29ms`, `GPU 31.51ms/frame`)
