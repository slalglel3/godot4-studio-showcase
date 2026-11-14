class_name SubViewportStageBridge
extends Node2D
## 2.5D Hybrid Stage Bridge: renders RiggedActor3D squads & bosses inside a transparent
## SubViewport overlaid cleanly onto a 2D HDR arena and exposes unproject_to_2d(world_pos).

@export var viewport_size: Vector2i = Vector2i(1280, 720)
@export var camera_pos: Vector3 = Vector3(0.0, 2.2, 6.2)
@export var camera_look_at: Vector3 = Vector3(0.0, 1.0, 0.0)
@export var camera_fov: float = 32.0

var subviewport: SubViewport
var stage_camera: Camera3D
var actors_root: Node3D
var viewport_sprite: TextureRect


func _ready() -> void:
	_build_viewport_rig()


func _build_viewport_rig() -> void:
	subviewport = SubViewport.new()
	subviewport.name = "ActorsSubViewport"
	subviewport.size = viewport_size
	subviewport.transparent_bg = true
	subviewport.render_target_update_mode = SubViewport.UPDATE_ALWAYS
	subviewport.msaa_3d = Viewport.MSAA_4X
	subviewport.own_world_3d = true
	add_child(subviewport)

	var world_env := WorldEnvironment.new()
	var env := Environment.new()
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.28, 0.24, 0.36, 1.0)
	env.ambient_light_energy = 0.85
	world_env.environment = env
	subviewport.add_child(world_env)

	var key_light := DirectionalLight3D.new()
	key_light.name = "KeyLight"
	key_light.light_color = Color(1.0, 0.94, 0.86, 1.0)
	key_light.light_energy = 1.65
	key_light.rotation_degrees = Vector3(-42.0, -32.0, 0.0)
	subviewport.add_child(key_light)

	var rim_light := DirectionalLight3D.new()
	rim_light.name = "RimLight"
	rim_light.light_color = Color(0.55, 0.72, 1.0, 1.0)
	rim_light.light_energy = 1.15
	rim_light.rotation_degrees = Vector3(28.0, 148.0, 0.0)
	subviewport.add_child(rim_light)

	stage_camera = Camera3D.new()
	stage_camera.name = "StageCamera"
	stage_camera.fov = camera_fov
	stage_camera.position = camera_pos
	subviewport.add_child(stage_camera)
	stage_camera.look_at(camera_look_at, Vector3.UP)

	actors_root = Node3D.new()
	actors_root.name = "ActorsRoot"
	subviewport.add_child(actors_root)

	viewport_sprite = TextureRect.new()
	viewport_sprite.name = "ViewportComposite"
	viewport_sprite.texture = subviewport.get_texture()
	viewport_sprite.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	viewport_sprite.position = Vector2.ZERO
	viewport_sprite.size = Vector2(viewport_size)
	viewport_sprite.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(viewport_sprite)


func add_rigged_actor(
	glb_path: String,
	actor_name: String,
	world_pos: Vector3,
	facing_yaw_deg: float,
	rim_col: Color = Color(1.0, 0.48, 0.24, 1.0),
	actor_scale: float = 1.0
) -> RiggedActor3D:
	var packed := load(glb_path) as PackedScene
	if packed == null:
		push_error("Failed to load rigged GLB: %s" % glb_path)
		return null
	var actor := RiggedActor3D.new()
	actor.name = actor_name
	actor.rim_color = rim_col
	actor.position = world_pos
	actor.rotation_degrees = Vector3(0.0, facing_yaw_deg, 0.0)
	actor.scale = Vector3.ONE * actor_scale
	var model := packed.instantiate()
	actor.add_child(model)
	actors_root.add_child(actor)
	return actor


func unproject_to_2d(world_pos_3d: Vector3) -> Vector2:
	if stage_camera == null:
		return Vector2(640.0, 360.0)
	return stage_camera.unproject_position(world_pos_3d)
