# Godot 4 Game Studio — 3D Rigged Meteor Combat & VFX Showcase

**Blender 4.5.16 LTS + CC0 모션 리타게팅(`Skeleton3D` 53본)**, **Godot 4.7.2-stable**, **godot-mcp (v3.1.0, 157 tools)**, **bubblewrap + Xvfb** 격리 렌더러, 그리고 `blender-character-studio` & `godot4-game-studio` 전역 스킬 기반으로 **관절이 살아 움직이는 3D 홍염 대마법사 vs 심연의 대검 보스 카르돈 실전 메테오 전투씬**을 End-to-End 구현 및 검증한 저장소입니다.

## 바로 보기 (웹 / 모바일 단일 파일)
* **GitHub Releases (`v1.2.0` 3D 리깅 메테오 전투 단일 파일 `index.html`)**: https://github.com/slalglel3/godot4-studio-showcase/releases/latest
* **GitHub Pages (브라우저 바로 보기)**: https://slalglel3.github.io/godot4-studio-showcase/
  * `index.html`은 외부 의존성 없이 **H.264 MP4 + 모바일 호환 WebP 루프 + 15개 키프레임 + 6-Frame QA 시트 + Blender 리깅 시트·에셋 5종 + 공용 VFX 8종 + MCP JSON + 16개 GDScript/Shader/Scene 원본**을 모두 Data URI로 내장한 완전 독립형(Standalone) 단일 HTML입니다.

## Verification Summary (`v1.2.0` 3D Rigged Combat)
* **Main Scene**: `res://scenes/meteor_showcase.tscn`
* **3D Character Pipeline**: `Blender 4.5.16 LTS` + `retarget_ual.py` (`scarlet_mage.glb`, `boss_kardon.glb`, `Skeleton3D` 53 bones, `StaffTip`/`BladeTip` sockets, scale-normalized `toon_cel_outline` & `toon_outline_nextpass`)
* **Engine & Renderer**: `Godot 4.7.2.stable.official.ed1daf0bf` (`Vulkan 1.4.335 - Forward+ - llvmpipe`, SubViewport MSAA 4x)
* **MCP Validation (`godot:validate_scripts`)**: `7 / 7` GDScript files valid, `0` errors (`meteor_showcase.gd`, `rigged_actor_3d.gd`, `subviewport_stage_bridge.gd`, `vfx_director.gd`, `boss_dual_gauge.gd`, `squad_skill_runner.gd`, `vfx_showcase.gd`)
* **MovieMaker Capture**: `90 frames @ 30 FPS` (`1280×720`, `3.00s`) rendered in `11s` (`CPU 1.68ms`, `GPU 31.52ms/frame`)
