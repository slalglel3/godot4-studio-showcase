extends Node2D
## Meteor Summon Showcase: Scarlet Archmage casts "멸망의 메테오!!"
## Phases:
##   0.00s - 0.90s: Staff orb surge + 2.5D cast zodiac circle + eye cut-in + sky rift + telegraph
##   0.92s - 1.56s: Magma meteor streaks diagonally from sky rift with aligned flame wake & sparks
##   1.56s - 3.00s: Crater explosion, screen shockwave, hit-flash knockback, boss gauge drain

const ADDITIVE_SHADER := preload("res://shared/shaders/vfx_additive_scroll.gdshader")
const HIT_FLASH_SHADER := preload("res://shared/shaders/vfx_hit_flash.gdshader")
const CUTIN_TEX := preload("res://assets/sprites/mage_cutin.png")
const FBM_NOISE := preload("res://shared/textures/noise_fbm.png")
const VORONOI_NOISE := preload("res://shared/textures/noise_voronoi.png")

const STAFF_TIP_LOCAL := Vector2(92.0, -100.0)
const SKY_RIFT_POS := Vector2(1130.0, 84.0)
const IMPACT_POS := Vector2(925.0, 520.0)

@onready var director: VfxDirector = $VfxDirector
@onready var boss_hud: BossDualGauge = $HudLayer/BossDualGauge

@onready var mage_sprite: Sprite2D = $Arena/MageRoot/MageSprite
@onready var cast_plane: Node2D = $Arena/MageRoot/CastPlane
@onready var mage_zodiac: Sprite2D = $Arena/MageRoot/CastPlane/CastZodiac
@onready var staff_orb: Sprite2D = $Arena/MageRoot/StaffOrb
@onready var staff_flare: Sprite2D = $Arena/MageRoot/StaffFlare

@onready var boss_root: Node2D = $Arena/BossRoot
@onready var boss_sprite: Sprite2D = $Arena/BossRoot/BossSprite
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


func _ready() -> void:
	boss_hud.boss_name = "저무는 카르돈 (흑요석의 수호자)"
	boss_hud.max_hp = 10000.0
	boss_hud.current_hp = 9200.0
	boss_hud.max_stagger = 1000.0
	boss_hud.current_stagger = 820.0
	boss_hud.apply_damage(0.0, 0.0)

	_setup_character_shaders()
	_setup_spell_materials()
	_reset_initial_vfx_state()


func _process(delta: float) -> void:
	_t += delta
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


func _setup_character_shaders() -> void:
	_mage_mat = ShaderMaterial.new()
	_mage_mat.shader = HIT_FLASH_SHADER
	_mage_mat.set_shader_parameter("outline_color", Color(1.0, 0.45, 0.16, 0.9))
	_mage_mat.set_shader_parameter("outline_width", 2.5)
	_mage_mat.set_shader_parameter("outline_hdr", 2.2)
	mage_sprite.material = _mage_mat

	_boss_mat = ShaderMaterial.new()
	_boss_mat.shader = HIT_FLASH_SHADER
	_boss_mat.set_shader_parameter("flash_color", Color(1.0, 0.72, 0.38, 1.0))
	_boss_mat.set_shader_parameter("flash_hdr", 2.6)
	_boss_mat.set_shader_parameter("outline_color", Color(0.95, 0.25, 0.58, 0.85))
	_boss_mat.set_shader_parameter("outline_width", 2.2)
	_boss_mat.set_shader_parameter("outline_hdr", 1.9)
	boss_sprite.material = _boss_mat


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

	staff_orb.position = STAFF_TIP_LOCAL
	staff_flare.position = STAFF_TIP_LOCAL
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
	var cast_energy := 1.0 if _t < 1.56 else maxf(0.2, 1.0 - (_t - 1.56) * 0.8)
	mage_sprite.position.y = sin(_t * 6.5) * 4.5 * cast_energy
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

	# Align horizontal flame wake backward cleanly along trajectory angle
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

	_boss_mat.set_shader_parameter("flash_amount", 1.0)
	var tw_flash := create_tween()
	tw_flash.tween_method(
		func(v: float) -> void:
			_boss_mat.set_shader_parameter("flash_amount", v),
		1.0, 0.0, 0.28
	)

	var orig_x := boss_root.position.x
	var tw_recoil := create_tween()
	tw_recoil.tween_property(boss_root, "position:x", orig_x + 34.0, 0.09).set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw_recoil.tween_property(boss_root, "position:x", orig_x, 0.42).set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)

	boss_sprite.scale = Vector2(0.39, 0.29)
	var tw_squash := create_tween()
	tw_squash.tween_property(boss_sprite, "scale", Vector2(0.34, 0.34), 0.26).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)

	boss_hud.apply_damage(4350.0, 520.0)
