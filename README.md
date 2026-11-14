# Godot 4 Game Studio — 2D Skeleton2D Articulated Meteor Combat Showcase

**Godot 4.7.2-stable 네이티브 2D 골격 리깅(`Skeleton2D` + `Bone2D` + Soft-Skinned `Polygon2D` + `CanvasGroup`)**, **OpenCV TELEA + SciPy EDT 레이어 분리(`extract_rig_parts.py`)**, **godot-mcp (v3.1.0)**, 그리고 **bubblewrap + Xvfb** 격리 렌더러를 결합하여 **`v1.1.0` 원본 캐릭터 일러스트를 100% 그대로 유지한 채** 전신 관절 모션과 메테오 전투 연출을 구현·검증한 저장소입니다.

## 바로 보기 (웹 / 모바일 단일 파일)
* **GitHub Releases (`v1.3.0` 원본 캐릭터 2D 골격 리깅 메테오 전투 단일 파일 `index.html`)**: https://github.com/slalglel3/godot4-studio-showcase/releases/latest
* **GitHub Pages (브라우저 바로 보기)**: https://slalglel3.github.io/godot4-studio-showcase/
  * `index.html`은 외부 의존성 없이 **H.264 MP4 + 모바일 호환 WebP 루프 + 15개 키프레임 + 6-Frame QA 시트 + 원본 일러스트 & Skeleton2D 파츠 시트 6종 + 공용 VFX 8종 + MCP JSON + 15개 GDScript/Shader/Scene/Python 원본**을 모두 Data URI로 내장한 완전 독립형(Standalone) 단일 HTML입니다.

## Verification Summary (`v1.3.0` 2D Articulated Motion on Original Art)
* **Main Scene**: `res://scenes/meteor_showcase.tscn`
* **2D Articulation Pipeline**: `scripts/extract_rig_parts.py` (원본 `mage_caster.png` 4레이어 + `boss_kardon.png` 6레이어 분리 및 TELEA 인페인팅) → `RiggedActor2D` (`CanvasGroup` 통합 실루엣 아웃라인 + `vfx_canvasgroup_hit_flash.gdshader`, 지팡이 강체 가중치, `StaffTip` 오브 추적, 보스 양손 대검 **Analytical 2-Bone IK**)
* **Engine & Renderer**: `Godot 4.7.2.stable.official.ed1daf0bf` (`Vulkan 1.4.335 - Forward+ - llvmpipe`)
* **MCP Validation (`godot:validate_scripts`)**: `6 / 6` GDScript files valid, `0` errors (`meteor_showcase.gd`, `rigged_actor_2d.gd`, `vfx_director.gd`, `boss_dual_gauge.gd`, `squad_skill_runner.gd`, `vfx_showcase.gd`)
* **MovieMaker Capture**: `90 frames @ 30 FPS` (`1280×720`, `3.00s`) rendered in `7s` (`CPU 0.43ms`, `GPU 46.03ms/frame`)
