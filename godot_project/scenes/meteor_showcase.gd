extends Node2D
## Meteor Summon Showcase (v1.3.0): v1.1.0 original Scarlet Archmage & Boss Kardon characters
## upgraded with 2D Skeleton2D + Polygon2D skeletal articulation while preserving 100% original art.

const ADDITIVE_SHADER := preload("res://shared/shaders/vfx_additive_scroll.gdshader")
const GROUP_FLASH_SHADER := preload("res://shared/shaders/vfx_canvasgroup_hit_flash.gdshader")
const CUTIN_TEX := preload("res://assets/sprites/mage_cutin.png")
const FBM_NOISE := preload("res://shared/textures/noise_fbm.png")
const VORONOI_NOISE := preload("res://shared/textures/noise_voronoi.png")

const MAGE_TEX_BODY := preload("res://assets/parts/mage/body.png")
const MAGE_TEX_HEAD := preload("res://assets/parts/mage/head.png")
const MAGE_TEX_ARM_L := preload("res://assets/parts/mage/left_arm.png")
const MAGE_TEX_ARM_R_STAFF := preload("res://assets/parts/mage/right_arm_staff.png")

const BOSS_TEX_CAPE := preload("res://assets/parts/boss/cape.png")
const BOSS_TEX_BODY := preload("res://assets/parts/boss/body.png")
const BOSS_TEX_ARM_R := preload("res://assets/parts/boss/right_arm.png")
const BOSS_TEX_ARM_L := preload("res://assets/parts/boss/left_arm.png")
const BOSS_TEX_SWORD := preload("res://assets/parts/boss/greatsword.png")
const BOSS_TEX_HEAD := preload("res://assets/parts/boss/head.png")

const SKY_RIFT_POS := Vector2(1130.0, 84.0)
const IMPACT_POS := Vector2(925.0, 520.0)

@onready var director: VfxDirector = $VfxDirector
@onready var boss_hud: BossDualGauge = $HudLayer/BossDualGauge

@onready var mage_root: Node2D = $Arena/MageRoot
@onready var mage_rig: RiggedActor2D = $Arena/MageRoot/MageRig
@onready var cast_plane: Node2D = $Arena/MageRoot/CastPlane
@onready var mage_zodiac: Sprite2D = $Arena/MageRoot/CastPlane/CastZodiac
@onready var staff_orb: Sprite2D = $Arena/MageRoot/StaffOrb
@onready var staff_flare: Sprite2D = $Arena/MageRoot/StaffFlare

@onready var boss_root: Node2D = $Arena/BossRoot
@onready var boss_rig: RiggedActor2D = $Arena/BossRoot/BossRig
@onready var telegraph_plane: Node2D = $Arena/TelegraphPlane
@onready var impact_telegraph: Sprite2D = $Arena/TelegraphPlane/ImpactTelegraph
@onready var crater_plane: Node2D = $Arena/CraterPlane
@onready var crater_glow: Sprite2D = $Arena/CraterPlane/CraterGlow

@onready var sky_rift_root: Node2D = $SkyVfx/SkyRift
@onready var sky_rift_ring: Sprite2D = $SkyVfx/SkyRift/RiftPlane/RiftRing
@onready var sky_rift_core: Sprite2D = $SkyVfx/SkyRift/RiftCore

@onready var meteor_root: Node2D = $SkyVfx/MeteorRoot
@onready var wake_container: Node2D = $SkyVfx/MeteorRoot/WakeContainer
@onready var meteor_core: Sprite2D = $SkyVfx/MeteorRoot/MeteorCore
@onready var meteor_halo: Sprite2D = $SkyVfx/MeteorRoot/WakeContainer/FireHalo
@onready var meteor_tail_a: Sprite2D = $SkyVfx/MeteorRoot/WakeContainer/FlameTailA
@onready var meteor_tail_b: Sprite2D = $SkyVfx/MeteorRoot/WakeContainer/FlameTailB
@onready var meteor_sparks: CPUParticles2D = $SkyVfx/MeteorRoot/MeteorSparks

@onready var impact_pillar: Sprite2D = $ImpactVfx/ImpactPillar
@onready var impact_dome: Sprite2D = $ImpactVfx/ImpactDome
@onready var impact_ring_plane: Node2D = $ImpactVfx/ImpactRingPlane
@onready var impact_ring: Sprite2D = $ImpactVfx/ImpactRingPlane/ImpactRing
@onready var impact_sparks: CPUParticles2D = $ImpactVfx/ImpactSparks

var _t: float = 0.0
var _cutin_done: bool = false
var _rift_done: bool = false
var _launch_done: bool = false
var _impact_done: bool = false
var _mage_mat: ShaderMaterial
var _boss_mat: ShaderMaterial
var _impact_whip: float = 0.0


func _ready() -> void:
	boss_hud.boss_name = "저무는 카르돈 (흑요석의 수호자)"
	boss_hud.max_hp = 10000.0
	boss_hud.current_hp = 9200.0
	boss_hud.max_stagger = 1000.0
	boss_hud.current_stagger = 820.0
	boss_hud.apply_damage(0.0, 0.0)

	_build_mage_rig()
	_build_boss_rig()
	_setup_character_shaders()
	_setup_spell_materials()
	_reset_initial_vfx_state()
	_update_character_poses(0.0)


func _build_mage_rig() -> void:
	var m_size := Vector2(764.0, 829.0)
	mage_rig.build_skeleton(m_size, [
		{"name": "Pelvis", "parent": "", "pos": Vector2(350, 410)},
		{"name": "Spine", "parent": "Pelvis", "pos": Vector2(350, 320)},
		{"name": "Chest", "parent": "Spine", "pos": Vector2(348, 240)},
		{"name": "Head", "parent": "Chest", "pos": Vector2(336, 184)},
		{"name": "ShoulderL", "parent": "Chest", "pos": Vector2(254, 232)},
		{"name": "ElbowL", "parent": "ShoulderL", "pos": Vector2(155, 310)},
		{"name": "HandL", "parent": "ElbowL", "pos": Vector2(228, 326)},
		{"name": "ShoulderR", "parent": "Chest", "pos": Vector2(416, 224)},
		{"name": "ElbowR", "parent": "ShoulderR", "pos": Vector2(498, 212)},
		{"name": "HandR", "parent": "ElbowR", "pos": Vector2(578, 198)},
		{"name": "StaffTip", "parent": "HandR", "pos": Vector2(686, 102)},
		# Ground-anchored legs & soft-skinned flowing coat-tail
		{"name": "KneeL", "parent": "", "pos": Vector2(172, 710)},
		{"name": "FootL", "parent": "", "pos": Vector2(150, 792)},
		{"name": "KneeR", "parent": "", "pos": Vector2(455, 675)},
		{"name": "FootR", "parent": "", "pos": Vector2(458, 765)},
		{"name": "Tail1", "parent": "Pelvis", "pos": Vector2(220, 505)},
		{"name": "Tail2", "parent": "Tail1", "pos": Vector2(105, 590)},
		{"name": "Tail3", "parent": "Tail2", "pos": Vector2(32, 685)},
	])

	mage_rig.add_skinned_layer("Body", MAGE_TEX_BODY, 1, 20, 22, [
		{"bone": "Chest", "pos": Vector2(348, 235), "radius": 110.0, "weight_scale": 1.3},
		{"bone": "Spine", "pos": Vector2(350, 325), "radius": 100.0, "weight_scale": 1.2},
		{"bone": "Pelvis", "pos": Vector2(350, 420), "radius": 120.0, "weight_scale": 1.4},
		{"bone": "KneeL", "pos": Vector2(172, 700), "radius": 115.0, "weight_scale": 1.2},
		{"bone": "FootL", "pos": Vector2(150, 792), "radius": 95.0, "weight_scale": 1.5},
		{"bone": "KneeR", "pos": Vector2(455, 665), "radius": 120.0, "weight_scale": 1.2},
		{"bone": "FootR", "pos": Vector2(458, 765), "radius": 105.0, "weight_scale": 1.5},
		{"bone": "Tail1", "pos": Vector2(210, 515), "radius": 105.0, "weight_scale": 1.1},
		{"bone": "Tail2", "pos": Vector2(105, 595), "radius": 100.0, "weight_scale": 1.3},
		{"bone": "Tail3", "pos": Vector2(36, 685), "radius": 95.0, "weight_scale": 1.5},
	])

	mage_rig.add_skinned_layer("LeftArm", MAGE_TEX_ARM_L, 2, 12, 12, [
		{"bone": "ShoulderL", "pos": Vector2(246, 232), "radius": 70.0, "weight_scale": 1.3},
		{"bone": "ElbowL", "pos": Vector2(142, 315), "radius": 85.0, "weight_scale": 1.2},
		{"bone": "HandL", "pos": Vector2(226, 332), "radius": 75.0, "weight_scale": 1.4},
	])

	# Keep the long diagonal staff + ruby crystal 100% rigid on HandR while softening upper shoulder sleeve
	var staff_rigid := func(uv: Vector2) -> bool:
		var seg := Geometry2D.get_closest_point_to_segment(uv, Vector2(405.0, 418.0), Vector2(692.0, 96.0))
		return uv.distance_to(seg) < 46.0 or (uv.x > 550.0 and uv.y < 238.0)

	mage_rig.add_skinned_layer("RightArmStaff", MAGE_TEX_ARM_R_STAFF, 3, 16, 16, [
		{"bone": "Chest", "pos": Vector2(398, 236), "radius": 55.0, "weight_scale": 1.1},
		{"bone": "ShoulderR", "pos": Vector2(428, 224), "radius": 70.0, "weight_scale": 1.3},
		{"bone": "ElbowR", "pos": Vector2(506, 220), "radius": 85.0, "weight_scale": 1.2},
		{"bone": "HandR", "pos": Vector2(578, 198), "radius": 90.0, "weight_scale": 1.5},
	], "HandR", staff_rigid)

	mage_rig.add_skinned_layer("Head", MAGE_TEX_HEAD, 4, 8, 8, [], "Head")


func _build_boss_rig() -> void:
	var b_size := Vector2(1024.0, 891.0)
	boss_rig.build_skeleton(b_size, [
		{"name": "Pelvis", "parent": "", "pos": Vector2(505, 445)},
		{"name": "Spine", "parent": "Pelvis", "pos": Vector2(482, 340)},
		{"name": "Chest", "parent": "Spine", "pos": Vector2(468, 250)},
		{"name": "Head", "parent": "Chest", "pos": Vector2(416, 185)},
		{"name": "ShoulderR", "parent": "Chest", "pos": Vector2(368, 226)},
		{"name": "ElbowR", "parent": "ShoulderR", "pos": Vector2(388, 336)},
		{"name": "HandR", "parent": "ElbowR", "pos": Vector2(480, 448)},
		{"name": "SwordPivot", "parent": "HandR", "pos": Vector2(492, 444)},
		{"name": "HiltTop", "parent": "SwordPivot", "pos": Vector2(568, 412)},
		{"name": "ShoulderL", "parent": "Chest", "pos": Vector2(578, 190)},
		{"name": "ElbowL", "parent": "ShoulderL", "pos": Vector2(650, 315)},
		{"name": "HandL", "parent": "ElbowL", "pos": Vector2(568, 412)},
		{"name": "Cape1", "parent": "Chest", "pos": Vector2(655, 225)},
		{"name": "Cape2", "parent": "Cape1", "pos": Vector2(805, 315)},
		{"name": "Cape3", "parent": "Cape2", "pos": Vector2(950, 425)},
		# Ground-anchored armor boots & knees
		{"name": "KneeR", "parent": "", "pos": Vector2(356, 650)},
		{"name": "FootR", "parent": "", "pos": Vector2(315, 818)},
		{"name": "KneeL", "parent": "", "pos": Vector2(702, 650)},
		{"name": "FootL", "parent": "", "pos": Vector2(832, 855)},
	])

	boss_rig.add_skinned_layer("Cape", BOSS_TEX_CAPE, 0, 14, 14, [
		{"bone": "Chest", "pos": Vector2(595, 235), "radius": 135.0, "weight_scale": 1.85},
		{"bone": "Cape1", "pos": Vector2(680, 260), "radius": 115.0, "weight_scale": 1.35},
		{"bone": "Cape2", "pos": Vector2(805, 330), "radius": 130.0, "weight_scale": 1.3},
		{"bone": "Cape3", "pos": Vector2(945, 430), "radius": 140.0, "weight_scale": 1.6},
	])

	boss_rig.add_skinned_layer("Body", BOSS_TEX_BODY, 1, 20, 22, [
		{"bone": "Chest", "pos": Vector2(468, 250), "radius": 130.0, "weight_scale": 1.3},
		{"bone": "Spine", "pos": Vector2(485, 345), "radius": 120.0, "weight_scale": 1.2},
		{"bone": "Pelvis", "pos": Vector2(505, 455), "radius": 140.0, "weight_scale": 1.4},
		{"bone": "KneeR", "pos": Vector2(356, 650), "radius": 135.0, "weight_scale": 1.3},
		{"bone": "FootR", "pos": Vector2(315, 818), "radius": 120.0, "weight_scale": 1.6},
		{"bone": "KneeL", "pos": Vector2(702, 650), "radius": 140.0, "weight_scale": 1.3},
		{"bone": "FootL", "pos": Vector2(832, 855), "radius": 125.0, "weight_scale": 1.6},
	])

	boss_rig.add_skinned_layer("RightArm", BOSS_TEX_ARM_R, 2, 10, 12, [
		{"bone": "ShoulderR", "pos": Vector2(362, 235), "radius": 90.0, "weight_scale": 1.3},
		{"bone": "ElbowR", "pos": Vector2(388, 336), "radius": 90.0, "weight_scale": 1.2},
		{"bone": "HandR", "pos": Vector2(475, 444), "radius": 85.0, "weight_scale": 1.4},
	])

	boss_rig.add_skinned_layer("LeftArm", BOSS_TEX_ARM_L, 3, 10, 12, [
		{"bone": "ShoulderL", "pos": Vector2(582, 185), "radius": 95.0, "weight_scale": 1.3},
		{"bone": "ElbowL", "pos": Vector2(648, 315), "radius": 95.0, "weight_scale": 1.2},
		{"bone": "HandL", "pos": Vector2(568, 412), "radius": 85.0, "weight_scale": 1.4},
	])

	boss_rig.add_skinned_layer("Greatsword", BOSS_TEX_SWORD, 4, 8, 8, [], "SwordPivot")
	boss_rig.add_skinned_layer("Head", BOSS_TEX_HEAD, 5, 8, 8, [], "Head")


func _process(delta: float) -> void:
	_t += delta
	_impact_whip = maxf(0.0, _impact_whip - delta * 2.2)
	_update_character_poses(_t)
	_update_continuous_fx(delta)

	if not _cutin_done and _t >= 0.20:
		_cutin_done = true
		director.enqueue_cutin("archmage", "멸망의 메테오!!", CUTIN_TEX, Color(1.0, 0.36, 0.14))

	if not _rift_done and _t >= 0.42:
		_rift_done = true
		_open_sky_rift_and_telegraph()

	if not _launch_done and _t >= 0.92:
		_launch_done = true
		_launch_meteor()

	if not _impact_done and _t >= 1.56:
		_impact_done = true
		_trigger_meteor_impact()


func _update_character_poses(t: float) -> void:
	# --- 1. SCARLET ARCHMAGE CHOREOGRAPHY ---
	var gather := _smoothstep_range(t, 0.0, 0.56)
	var thrust := _smoothstep_range(t, 0.94, 1.46)
	var blast_recoil := _smoothstep_range(t, 1.56, 1.72) * (1.0 - _smoothstep_range(t, 1.85, 2.35))
	var relax := _smoothstep_range(t, 2.05, 2.92)
	var breath := sin(t * 4.4)

	# Squat into deep chant stance while ground-anchoring FootL/FootR
	var hip_drop := 24.0 * gather - 6.0 * thrust + 14.0 * blast_recoil - 18.0 * relax + breath * 3.5
	var hip_x := -14.0 * gather + 24.0 * thrust - 14.0 * blast_recoil - 10.0 * relax
	mage_rig.set_bone_offset("Pelvis", Vector2(hip_x, hip_drop))
	mage_rig.set_bone_offset("KneeL", Vector2(-14.0 * gather + 10.0 * thrust + 4.0 * relax, hip_drop * 0.48))
	mage_rig.set_bone_offset("KneeR", Vector2(14.0 * gather + 12.0 * thrust - 20.0 * relax, hip_drop * 0.45))

	var spine_deg := -7.5 * gather + 11.5 * thrust - 6.0 * blast_recoil - 4.0 * relax + breath * 1.4
	var chest_deg := -9.0 * gather + 12.5 * thrust - 7.0 * blast_recoil - 3.5 * relax
	var head_deg := -14.0 * gather + 18.0 * thrust - 8.0 * blast_recoil - 4.0 * relax
	mage_rig.set_bone_deg("Spine", spine_deg * 0.55)
	mage_rig.set_bone_deg("Chest", chest_deg)
	mage_rig.set_bone_deg("Head", head_deg)

	# Staff-bearing Right Arm sweeps heroically up toward Sky Rift, then commands downward smash
	var r_sh := -25.0 * gather + 38.0 * thrust - 13.0 * relax + sin(t * 6.5) * 1.6
	var r_el := -11.0 * gather + 16.0 * thrust - 5.0 * relax
	var r_hd := -5.0 * gather + 10.0 * thrust - 5.0 * relax
	mage_rig.set_bone_deg("ShoulderR", r_sh)
	mage_rig.set_bone_deg("ElbowR", r_el)
	mage_rig.set_bone_deg("HandR", r_hd)

	# Free Left Arm draws mana inward, flares sleeve across on thrust, then recovers
	var l_sh := 18.0 * gather - 28.0 * thrust + 10.0 * relax
	var l_el := -22.0 * gather + 30.0 * thrust - 8.0 * relax
	var l_hd := 12.0 * gather - 16.0 * thrust + 4.0 * relax
	mage_rig.set_bone_deg("ShoulderL", l_sh)
	mage_rig.set_bone_deg("ElbowL", l_el)
	mage_rig.set_bone_deg("HandL", l_hd)

	# Flowing coat-tail ripples gently, then whips violently from impact blast
	var tail_amp := 5.5 + 16.0 * _impact_whip
	mage_rig.set_bone_deg("Tail1", sin(t * 6.0) * tail_amp - 6.0 * thrust + 14.0 * _impact_whip)
	mage_rig.set_bone_deg("Tail2", sin(t * 6.0 - 1.1) * tail_amp * 1.3 + 12.0 * _impact_whip)
	mage_rig.set_bone_deg("Tail3", sin(t * 6.0 - 2.2) * tail_amp * 1.6)

	# Track ruby staff crystal socket dynamically for HDR StaffOrb + StaffFlare
	var staff_local := mage_root.to_local(mage_rig.get_bone_global_pos("StaffTip"))
	staff_orb.position = staff_local
	staff_flare.position = staff_local

	# --- 2. BOSS KARDON CHOREOGRAPHY (Left-facing: +deg = clockwise/up for blade, -deg = forward lean) ---
	var brace := _smoothstep_range(t, 0.35, 1.22)
	var hit_up := _smoothstep_range(t, 1.56, 1.68)
	var hit_recover := _smoothstep_range(t, 1.78, 2.22)
	var hit_pose := hit_up * (1.0 - hit_recover)
	var counter_wind := _smoothstep_range(t, 1.98, 2.44)
	var counter_slam := _smoothstep_range(t, 2.44, 2.84)
	var end_ease := _smoothstep_range(t, 2.84, 3.00)
	var boss_breath := sin(t * 3.4)

	# Deep defensive crouch as telegraph opens -> knocked backward -> ferocious lunge cleave
	var b_hip_y := (18.0 * brace + 12.0 * hit_pose + 18.0 * counter_slam) * (1.0 - end_ease) + boss_breath * 7.5
	var b_hip_x := (8.0 * brace + 34.0 * hit_pose - 24.0 * counter_slam) * (1.0 - end_ease)
	boss_rig.set_bone_offset("Pelvis", Vector2(b_hip_x, b_hip_y))
	boss_rig.set_bone_offset("KneeR", Vector2((-10.0 * brace - 14.0 * counter_slam) * (1.0 - end_ease), b_hip_y * 0.48))
	boss_rig.set_bone_offset("KneeL", Vector2((10.0 * brace + 8.0 * hit_pose) * (1.0 - end_ease), b_hip_y * 0.45))

	var b_spine := (-5.0 * brace + 14.0 * hit_pose + 10.0 * counter_wind - 18.0 * counter_slam) * (1.0 - end_ease) + boss_breath * 2.0
	var b_chest := (-5.0 * brace + 13.0 * hit_pose + 8.0 * counter_wind - 15.0 * counter_slam) * (1.0 - end_ease)
	var b_head := (-6.0 * brace + 22.0 * hit_pose + 10.0 * counter_wind - 16.0 * counter_slam) * (1.0 - end_ease) - boss_breath * 1.5
	boss_rig.set_bone_deg("Spine", b_spine * 0.65)
	boss_rig.set_bone_deg("Chest", b_chest)
	boss_rig.set_bone_deg("Head", b_head)

	# Heavy Greatsword: +deg clockwise raises sword UPWARD toward horizontal guard/overhead!
	var r_arm_lift := (14.0 * brace + 10.0 * hit_pose + 18.0 * counter_wind - 22.0 * counter_slam) * (1.0 - end_ease) + boss_breath * 1.5
	var r_el_flex := (-8.0 * brace - 6.0 * counter_wind + 14.0 * counter_slam) * (1.0 - end_ease)
	var sword_wrist := (16.0 * brace + 14.0 * hit_pose + 18.0 * counter_wind - 22.0 * counter_slam) * (1.0 - end_ease) + boss_breath * 1.5
	boss_rig.set_bone_deg("ShoulderR", r_arm_lift)
	boss_rig.set_bone_deg("ElbowR", r_el_flex)
	boss_rig.set_bone_deg("SwordPivot", sword_wrist)

	# Analytical 2-Bone Law-of-Cosines IK locks Left Hand permanently onto the Sword HiltTop!
	_solve_boss_left_arm_ik()

	# Torn Abyss Cape ripples ominously, then whips skyward (-deg) from impact shockwave!
	var cape_amp := 6.0 + 22.0 * _impact_whip + 10.0 * counter_slam
	boss_rig.set_bone_deg("Cape1", sin(t * 4.8) * cape_amp - 28.0 * _impact_whip + 10.0 * counter_slam)
	boss_rig.set_bone_deg("Cape2", sin(t * 4.8 - 1.0) * cape_amp * 1.3 - 14.0 * _impact_whip)
	boss_rig.set_bone_deg("Cape3", sin(t * 4.8 - 2.1) * cape_amp * 1.6)

	if _mage_mat:
		var chant_glow := _smoothstep_range(t, 0.22, 0.55) * (1.0 - _smoothstep_range(t, 1.35, 1.80))
		_mage_mat.set_shader_parameter("outline_width", 1.25 * chant_glow)


func _solve_boss_left_arm_ik() -> void:
	const L1 := 144.25 # distance ShoulderL(578,190) -> ElbowL(650,315)
	const L2 := 127.00 # distance ElbowL(650,315) -> HandL(568,412)
	const ANGLE1_REST := 1.04825 # atan2(125, 72)
	const BEND_REST := 1.22443   # atan2(97, -82) - atan2(125, 72)

	var b_shr := boss_rig.bones["ShoulderR"] as Bone2D
	var b_elr := boss_rig.bones["ElbowR"] as Bone2D
	var b_hanr := boss_rig.bones["HandR"] as Bone2D
	var b_sw := boss_rig.bones["SwordPivot"] as Bone2D
	var b_hilt := boss_rig.bones["HiltTop"] as Bone2D
	var b_shl := boss_rig.bones["ShoulderL"] as Bone2D
	var b_ell := boss_rig.bones["ElbowL"] as Bone2D

	var xf := b_shr.transform * b_elr.transform * b_hanr.transform * b_sw.transform
	var target_in_chest := xf * b_hilt.position
	var delta := target_in_chest - b_shl.position
	var dist := clampf(delta.length(), absf(L1 - L2) + 4.0, L1 + L2 - 2.0)
	var base_ang := delta.angle()
	var cos_a := clampf((L1 * L1 + dist * dist - L2 * L2) / (2.0 * L1 * dist), -1.0, 1.0)
	var cos_g := clampf((L1 * L1 + L2 * L2 - dist * dist) / (2.0 * L1 * L2), -1.0, 1.0)
	var desired_ang1 := base_ang - acos(cos_a)
	var bend := PI - acos(cos_g)
	b_shl.rotation = desired_ang1 - ANGLE1_REST
	b_ell.rotation = bend - BEND_REST


func _smoothstep_range(t: float, t0: float, t1: float) -> float:
	if t1 <= t0:
		return 1.0 if t >= t0 else 0.0
	var x := clampf((t - t0) / (t1 - t0), 0.0, 1.0)
	return x * x * (3.0 - 2.0 * x)


func _setup_character_shaders() -> void:
	_mage_mat = ShaderMaterial.new()
	_mage_mat.shader = GROUP_FLASH_SHADER
	_mage_mat.set_shader_parameter("outline_color", Color(1.0, 0.48, 0.16, 0.72))
	_mage_mat.set_shader_parameter("outline_width", 0.0)
	_mage_mat.set_shader_parameter("outline_hdr", 1.85)
	mage_rig.material = _mage_mat

	_boss_mat = ShaderMaterial.new()
	_boss_mat.shader = GROUP_FLASH_SHADER
	_boss_mat.set_shader_parameter("flash_color", Color(1.0, 0.80, 0.45, 1.0))
	_boss_mat.set_shader_parameter("flash_hdr", 1.68)
	_boss_mat.set_shader_parameter("outline_color", Color(0.95, 0.25, 0.58, 0.65))
	_boss_mat.set_shader_parameter("outline_width", 0.0)
	_boss_mat.set_shader_parameter("outline_hdr", 1.65)
	boss_rig.material = _boss_mat


func _setup_spell_materials() -> void:
	mage_zodiac.material = _make_additive_mat(
		FBM_NOISE, Color(1.0, 0.88, 0.48), Color(1.0, 0.25, 0.08), 2.5, Vector2(0.08, -0.18), 0.025
	)
	staff_orb.material = _make_additive_mat(
		FBM_NOISE, Color(1.0, 0.96, 0.78), Color(1.0, 0.28, 0.10), 3.1, Vector2(0.4, -0.7), 0.04
	)
	staff_flare.material = _make_additive_mat(
		FBM_NOISE, Color(1.0, 0.92, 0.6), Color(1.0, 0.35, 0.08), 2.8, Vector2(0.0, -0.6), 0.02
	)
	impact_telegraph.material = _make_additive_mat(
		FBM_NOISE, Color(1.0, 0.78, 0.38), Color(1.0, 0.16, 0.05), 2.9, Vector2(0.15, 0.2), 0.03
	)
	crater_glow.material = _make_additive_mat(
		VORONOI_NOISE, Color(1.0, 0.85, 0.42), Color(0.98, 0.22, 0.04), 3.2, Vector2(0.05, -0.35), 0.07
	)

	sky_rift_ring.material = _make_additive_mat(
		VORONOI_NOISE, Color(1.0, 0.90, 0.50), Color(1.0, 0.26, 0.06), 3.1, Vector2(0.1, -0.8), 0.045
	)
	sky_rift_core.material = _make_additive_mat(
		FBM_NOISE, Color(1.0, 0.96, 0.82), Color(1.0, 0.42, 0.08), 3.4, Vector2(0.0, -1.2), 0.09
	)

	meteor_halo.material = _make_additive_mat(
		VORONOI_NOISE, Color(1.0, 0.92, 0.62), Color(1.0, 0.32, 0.04), 3.5, Vector2(-1.8, 0.2), 0.11
	)
	meteor_tail_a.material = _make_additive_mat(
		FBM_NOISE, Color(1.0, 0.90, 0.55), Color(1.0, 0.24, 0.05), 3.6, Vector2(-2.5, 0.0), 0.10
	)
	meteor_tail_b.material = _make_additive_mat(
		VORONOI_NOISE, Color(1.0, 0.78, 0.40), Color(0.95, 0.18, 0.04), 3.0, Vector2(-1.9, 0.15), 0.08
	)

	impact_pillar.material = _make_additive_mat(
		VORONOI_NOISE, Color(1.0, 0.95, 0.72), Color(1.0, 0.35, 0.05), 4.0, Vector2(0.0, -2.2), 0.12
	)
	impact_dome.material = _make_additive_mat(
		FBM_NOISE, Color(1.0, 0.92, 0.68), Color(1.0, 0.28, 0.06), 3.7, Vector2(0.2, -1.4), 0.10
	)
	impact_ring.material = _make_additive_mat(
		FBM_NOISE, Color(1.0, 0.82, 0.45), Color(1.0, 0.22, 0.05), 3.0, Vector2(0.0, -0.4), 0.03
	)


func _make_additive_mat(
	noise: Texture2D,
	core_col: Color,
	edge_col: Color,
	hdr: float,
	scroll: Vector2,
	distort: float
) -> ShaderMaterial:
	var mat := ShaderMaterial.new()
	mat.shader = ADDITIVE_SHADER
	mat.set_shader_parameter("noise_tex", noise)
	mat.set_shader_parameter("core_color", core_col)
	mat.set_shader_parameter("edge_color", edge_col)
	mat.set_shader_parameter("hdr_intensity", hdr)
	mat.set_shader_parameter("scroll_speed", scroll)
	mat.set_shader_parameter("noise_scale", 1.45)
	mat.set_shader_parameter("distort_strength", distort)
	mat.set_shader_parameter("alpha_power", 1.1)
	mat.set_shader_parameter("dissolve_cutoff", 0.0)
	return mat


func _reset_initial_vfx_state() -> void:
	cast_plane.scale = Vector2(0.25, 0.09)
	mage_zodiac.modulate.a = 0.0
	var tw := create_tween().set_parallel(true)
	tw.tween_property(cast_plane, "scale", Vector2(0.95, 0.34), 0.36).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(mage_zodiac, "modulate:a", 0.95, 0.25)

	staff_orb.scale = Vector2(0.35, 0.35)
	staff_flare.scale = Vector2(0.28, 0.28)

	sky_rift_root.visible = false
	telegraph_plane.visible = false
	crater_plane.visible = false
	meteor_root.visible = false
	meteor_sparks.emitting = false

	impact_pillar.visible = false
	impact_dome.visible = false
	impact_ring_plane.visible = false
	impact_sparks.emitting = false


func _update_continuous_fx(delta: float) -> void:
	mage_zodiac.rotation += delta * 1.15
	staff_flare.rotation -= delta * 1.9
	var orb_pulse := (0.48 + 0.22 * sin(_t * 14.0)) * (1.35 if (_t >= 0.2 and _t <= 1.2) else 0.7)
	staff_orb.scale = Vector2(orb_pulse, orb_pulse)
	staff_flare.scale = Vector2(orb_pulse * 0.95, orb_pulse * 0.52)

	if sky_rift_root.visible:
		sky_rift_ring.rotation += delta * 1.6
	if meteor_root.visible:
		meteor_core.rotation += delta * 5.2
	if telegraph_plane.visible:
		impact_telegraph.rotation -= delta * 1.35


func _open_sky_rift_and_telegraph() -> void:
	sky_rift_root.visible = true
	sky_rift_root.position = SKY_RIFT_POS
	sky_rift_root.scale = Vector2(0.08, 0.08)
	sky_rift_root.modulate.a = 0.0
	var tw := create_tween().set_parallel(true)
	tw.tween_property(sky_rift_root, "scale", Vector2(1.0, 1.0), 0.35).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
	tw.tween_property(sky_rift_root, "modulate:a", 1.0, 0.24)

	telegraph_plane.visible = true
	telegraph_plane.position = Vector2(IMPACT_POS.x, 588.0)
	telegraph_plane.scale = Vector2(0.3, 0.1)
	impact_telegraph.modulate.a = 0.0
	var tw_tel := create_tween().set_parallel(true)
	tw_tel.tween_property(telegraph_plane, "scale", Vector2(1.42, 0.44), 0.45).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw_tel.tween_property(impact_telegraph, "modulate:a", 0.92, 0.25)


func _launch_meteor() -> void:
	meteor_root.visible = true
	meteor_root.position = SKY_RIFT_POS + Vector2(12.0, -18.0)
	meteor_root.scale = Vector2(0.68, 0.68)

	var flight_vec := IMPACT_POS - meteor_root.position
	wake_container.rotation = flight_vec.angle()
	meteor_sparks.emitting = true

	var tw := create_tween().set_parallel(true)
	tw.tween_property(meteor_root, "position", IMPACT_POS, 0.64).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)
	tw.tween_property(meteor_root, "scale", Vector2(1.18, 1.18), 0.64).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_IN)

	var tw_fade := create_tween()
	tw_fade.tween_interval(0.55)
	tw_fade.tween_property(sky_rift_root, "modulate:a", 0.0, 0.35)


func _trigger_meteor_impact() -> void:
	meteor_root.visible = false
	meteor_sparks.emitting = false
	telegraph_plane.visible = false
	_impact_whip = 1.0

	director.add_trauma(0.88)
	director.spawn_shockwave(IMPACT_POS, 0.56, 0.055)
	var sw2 := create_tween()
	sw2.tween_interval(0.08)
	sw2.tween_callback(func() -> void:
		director.spawn_shockwave(IMPACT_POS, 0.62, 0.038)
	)

	impact_sparks.position = IMPACT_POS
	impact_sparks.restart()
	impact_sparks.emitting = true

	impact_dome.visible = true
	impact_dome.position = IMPACT_POS
	impact_dome.scale = Vector2(0.45, 0.45)
	impact_dome.modulate.a = 1.0
	var tw_dome := create_tween().set_parallel(true)
	tw_dome.tween_property(impact_dome, "scale", Vector2(3.4, 2.8), 0.42).set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_OUT)
	tw_dome.tween_property(impact_dome, "modulate:a", 0.0, 0.58).set_delay(0.14)

	impact_pillar.visible = true
	impact_pillar.position = IMPACT_POS + Vector2(0.0, -160.0)
	impact_pillar.scale = Vector2(1.55, 0.4)
	impact_pillar.modulate.a = 1.0
	var tw_pil := create_tween().set_parallel(true)
	tw_pil.tween_property(impact_pillar, "scale", Vector2(2.3, 3.85), 0.28).set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_OUT)
	tw_pil.tween_property(impact_pillar, "modulate:a", 0.0, 0.68).set_delay(0.18)

	impact_ring_plane.visible = true
	impact_ring_plane.position = Vector2(IMPACT_POS.x, 588.0)
	impact_ring_plane.scale = Vector2(0.45, 0.16)
	impact_ring.modulate.a = 1.0
	var tw_ring := create_tween().set_parallel(true)
	tw_ring.tween_property(impact_ring_plane, "scale", Vector2(2.3, 0.78), 0.52).set_trans(Tween.TRANS_EXPO).set_ease(Tween.EASE_OUT)
	tw_ring.tween_property(impact_ring, "modulate:a", 0.0, 0.58).set_delay(0.1)

	crater_plane.visible = true
	crater_plane.position = Vector2(IMPACT_POS.x, 588.0)
	crater_plane.scale = Vector2(2.2, 0.72)
	crater_glow.modulate.a = 0.92
	var tw_crater := create_tween()
	tw_crater.tween_property(crater_glow, "modulate:a", 0.24, 1.35)

	_boss_mat.set_shader_parameter("flash_amount", 0.84)
	_boss_mat.set_shader_parameter("outline_width", 1.5)
	var tw_flash := create_tween()
	tw_flash.tween_method(
		func(v: float) -> void:
			_boss_mat.set_shader_parameter("flash_amount", v)
			_boss_mat.set_shader_parameter("outline_width", 1.5 * v),
		0.84, 0.0, 0.26
	)

	var orig_x := boss_root.position.x
	var tw_recoil := create_tween()
	tw_recoil.tween_property(boss_root, "position:x", orig_x + 34.0, 0.09).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw_recoil.tween_property(boss_root, "position:x", orig_x, 0.42).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)

	boss_hud.apply_damage(4350.0, 520.0)
