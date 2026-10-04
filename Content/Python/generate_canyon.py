from __future__ import annotations
import unreal
import random
import math
import typing as t

if  t.TYPE_CHECKING:
    pass

"""
Configuration
"""
CONTENT_ROOT_PATH = "/Game/ObstacleCourse"

# Generated Actors / World Outliner folders
GENERATED_FOLDER_ROOT = "Generated"
GENERATED_FOLDER_TREES = GENERATED_FOLDER_ROOT + "/Trees"
GENERATED_FOLDER_BOULDERS = GENERATED_FOLDER_ROOT + "/Boulders"
GENERATED_FOLDER_CLIFFS = GENERATED_FOLDER_ROOT + "/Cliffs"
GAMEPLAY_ROCK_FOLDER = GENERATED_FOLDER_ROOT + "/Gameplay/Rocks"

# Canyon / Spline
CANYON_ACTOR_CLASS_PREFIX = "BP_CanyonPath"
CANYON_SPLINE_COMPONENT_NAME = "CanyonSpline"

# Landscape / Road
ROAD_PAINT_ENABLED = True
ROAD_LAYER_NAME = "Dirt"

# 900 UU radius => 1800 UU total spline width.
ROAD_WIDTH = 1400.0

# Increase the falloff to blur road edges
ROAD_SIDE_FALLOFF = 500.0  # Makes texture transition softer.
ROAD_END_FALLOFF = 0.0

# IMPORTANT: False = do not modify Landscape height.
ROAD_RAISE_TERRAIN = False
ROAD_LOWER_TERRAIN = False

"""
If your Landscape uses Edit Layers and the automatic
"None" selection does not work, specify the exact
Edit Layer name here.

Example:
ROAD_EDIT_LAYER_NAME = "LandscapeLayer"

Leave as "None" to let Unreal use the default behavior.
"""
ROAD_EDIT_LAYER_NAME = "Layer"

# Assets
TREE_ASSET = f"{CONTENT_ROOT_PATH}/Materials/SM_Pine_Tree_01.SM_Pine_Tree_01"
BOULDER_ASSET = f"{CONTENT_ROOT_PATH}/Materials/SM_NordicBoulder.SM_NordicBoulder"
CLIFF_ASSET = f"{CONTENT_ROOT_PATH}/Materials/SM_Quarry_Cliff.SM_Quarry_Cliff"


# Generation counts
TREE_COUNT = 280
BOULDER_COUNT = 60


"""
Tree placement

Road:
      -900 ... +900

Trees:
      -2100 ... -1200
      +1200 ... +2100
"""
TREE_MIN_OFFSET = 1200.0
TREE_MAX_OFFSET = 2100.0
TREE_MIN_DISTANCE = 150.0
TREE_MIN_SCALE = 0.85
TREE_MAX_SCALE = 1.15
TREE_GROUND_OFFSET = 30.0

# Boulder placement
BOULDER_MIN_OFFSET = 1200.0
BOULDER_MAX_OFFSET = 2000.0
BOULDER_MIN_SCALE = 1.75
BOULDER_MAX_SCALE = 2.25
BOULDER_GROUND_OFFSET = 5.0

# Landscape trace
TRACE_HEIGHT = 20000.0

"""
Tree slope filtering

Normal.Z:

1.0  = completely horizontal surface
0.0  = vertical wall
"""
MIN_TREE_NORMAL_Z = 0.35
MAX_TREE_NORMAL_Z = 1.0

# Cliffs

# Main row - near to canyon
# CLIFF_INNER_MIN_OFFSET = 1750.0
# CLIFF_INNER_MAX_OFFSET = 2350.0

CLIFF_INNER_MIN_OFFSET = 2350.0
CLIFF_INNER_MAX_OFFSET = 2850.0

CLIFF_INNER_MIN_SCALE = 1.25
CLIFF_INNER_MAX_SCALE = 1.70

# Outside row - make deep
CLIFF_OUTER_COUNT_PER_SIDE = 0
CLIFF_OUTER_MIN_OFFSET = 2900.0
CLIFF_OUTER_MAX_OFFSET = 3700.0
CLIFF_OUTER_MIN_SCALE = 0.55
CLIFF_OUTER_MAX_SCALE = 0.90

# We deepen rocks downwards to avoid cracks at bottom
CLIFF_GROUND_OFFSET = -150.0  # Was 0.0. Rock sinks deeper into the ground
CLIFF_MIN_DISTANCE = 260.0

CLIFF_LENGTH = 1273.0
CLIFF_OVERLAP = 250.0

# Little roll by height
CLIFF_Z_JITTER = 20.0

IS_GAMEPLAY_GENERATION_ENABLED = False

# Gameplay corridor
GAMEPLAY_WIDTH = 1200.0
GAMEPLAY_HALF_WIDTH = GAMEPLAY_WIDTH * 0.5
GAMEPLAY_OBJECT_MIN_DISTANCE = 500.0

GAMEPLAY_ROCK_COUNT = 20
GAMEPLAY_ROCK_MIN_DISTANCE = 800.0
GAMEPLAY_ROCK_MIN_SPLINE_DISTANCE = 2000.0
GAMEPLAY_ROCK_MAX_SPLINE_DISTANCE = -1.0
GAMEPLAY_ROCK_MIN_SCALE = 0.8
GAMEPLAY_ROCK_MAX_SCALE = 1.2
GAMEPLAY_ROCK_GROUND_OFFSET = 5.0

# Minimum distance between gameplay corridor and decorative objects.
DECORATION_GAMEPLAY_GAP = 200.0

# Tags
GENERATED_TAG = "Generated"
GENERATED_TREE_TAG = "GeneratedTree"
GENERATED_BOULDER_TAG = "GeneratedBoulder"
GENERATED_CLIFF_TAG = "GeneratedCliff"
GAMEPLAY_ROCK_TAG = "GeneratedGameplayRock"
GENERATED_TAGS = (
    GENERATED_TAG,
    GENERATED_TREE_TAG,
    GENERATED_BOULDER_TAG,
    GENERATED_CLIFF_TAG,
    GAMEPLAY_ROCK_TAG,
)


# Random seed
RANDOM_SEED = 12345

"""
Utility
"""
def initialize_random() -> None:
    if RANDOM_SEED is not None:
        random.seed(RANDOM_SEED)
        unreal.log(f"Random seed: {RANDOM_SEED}")
    else:
        random.seed()
        unreal.log("Random seed: random")


def set_actor_folder(actor, folder_path):
    """
    Places generated Actor into a World Outliner folder.
    """
    if actor is None:
        return
    try:
        actor.set_folder_path(folder_path)
    except Exception as error:
        unreal.log_warning(f"Could not set folder '{folder_path}' for actor '{actor.get_name()}': {error}")


"""
Find canyon spline
"""

def find_canyon_path():
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = actor_subsystem.get_all_level_actors()

    for actor in actors:
        actor_class_name = actor.get_class().get_name()
        if actor_class_name.startswith(CANYON_ACTOR_CLASS_PREFIX):
            return actor
    return None


def find_canyon_spline():
    canyon_actor = find_canyon_path()
    if canyon_actor is None:
        unreal.log_error("Could not find BP_CanyonPath actor.")
        return None

    unreal.log(f"Found canyon actor: {canyon_actor.get_name()}")
    spline_component = canyon_actor.get_component_by_class(unreal.SplineComponent)
    if spline_component is None:
        unreal.log_error("Could not find SplineComponent on BP_CanyonPath.")
        return None

    unreal.log("Found CanyonSpline component.")
    return spline_component


def find_landscape():
    """
    Find Landscape actor
    """
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = actor_subsystem.get_all_level_actors()

    for actor in actors:
        if isinstance(actor, unreal.Landscape):
            unreal.log(f"Found Landscape: {actor.get_name()}")
            return actor

    unreal.log_error("Could not find Landscape actor.")
    return None


def find_landscape_layer_info(landscape, layer_name):
    """
    Finds Landscape Layer Info
    """
    layer_info_path = f"{CONTENT_ROOT_PATH}/Landscape/Resources/LI_{layer_name}.LI_{layer_name}"
    unreal.log(f"Loading Landscape Layer Info: {layer_info_path}")

    layer_info = unreal.EditorAssetLibrary.load_asset(layer_info_path)
    if layer_info is None:
        unreal.log_error(f"Could not load Landscape Layer Info: {layer_info_path}")
        return None

    if not isinstance(layer_info, unreal.LandscapeLayerInfoObject):
        unreal.log_error(f"Loaded asset is not LandscapeLayerInfoObject: {layer_info}")
        return None

    try:
        loaded_layer_name = layer_info.get_editor_property("layer_name")
        unreal.log(f"Loaded Layer Info: {layer_info.get_name()}")
        unreal.log(f"Layer name: {loaded_layer_name}")

        if str(loaded_layer_name) != layer_name:
            unreal.log_error(f"Layer name mismatch. Expected '{layer_name}', got '{loaded_layer_name}'.")
            return None
    except Exception as error:
        unreal.log_warning(f"Could not read layer_name: {error}")
    return layer_info


def paint_dirt_along_canyon(spline_component):
    if not ROAD_PAINT_ENABLED:
        unreal.log("Road painting disabled.")
        return True

    unreal.log("\n========================================")
    unreal.log("PAINTING DIRT ROAD")
    unreal.log("========================================")

    # Find Landscape
    landscape = find_landscape()
    if landscape is None:
        unreal.log_error("Road painting aborted: Landscape not found.")
        return False

    # Check target layer
    target_layer_names = landscape.get_target_layer_names(False)
    target_layer_names_as_strings = [str(name) for name in target_layer_names]

    if ROAD_LAYER_NAME not in target_layer_names_as_strings:
        unreal.log_error(f"Road painting aborted: Landscape does not contain layer '{ROAD_LAYER_NAME}'.")
        return False

    # Find LI_Dirt
    dirt_layer_info = find_landscape_layer_info(landscape, ROAD_LAYER_NAME)
    if dirt_layer_info is None:
        unreal.log_error(f"Road painting aborted: Landscape Layer Info for '{ROAD_LAYER_NAME}' was not found.")
        return False

    # Spline length
    spline_length = spline_component.get_spline_length()
    if spline_length <= 0.0:
        unreal.log_error("Road painting aborted: Spline length is zero.")
        return False

    # Apply spline
    #
    # IMPORTANT:
    #
    # raise_heights = False
    # lower_heights = False
    #
    # Therefore this operation paints Dirt only.
    # It does NOT reshape the Landscape.
    unreal.log("Applying spline to Landscape...")
    unreal.log("Layer: {}".format(ROAD_LAYER_NAME))
    unreal.log("Width: {:.1f} UU".format(ROAD_WIDTH))
    unreal.log("Side falloff: {:.1f} UU".format(ROAD_SIDE_FALLOFF))
    unreal.log("End falloff: {:.1f} UU".format(ROAD_END_FALLOFF))
    unreal.log("Spline length: {:.1f} UU".format(spline_length))

    try:
        landscape.editor_apply_spline(
            spline_component,

            # Start/end width.
            ROAD_WIDTH,
            ROAD_WIDTH,

            # Start/end side falloff.
            ROAD_SIDE_FALLOFF,
            ROAD_SIDE_FALLOFF,

            # Start/end roll.
            0.0,
            0.0,

            # Spline subdivisions.
            20,

            # Do NOT change height.
            ROAD_RAISE_TERRAIN,
            ROAD_LOWER_TERRAIN,

            # Paint Dirt.
            dirt_layer_info,

            # Edit Layer.
            ROAD_EDIT_LAYER_NAME
        )
    except Exception as error:
        unreal.log_error(f"Landscape spline application failed: {error}")
        return False

    # Force Landscape update
    try:
        landscape.force_layers_full_update()
    except Exception as error:
        unreal.log_warning(f"Landscape layers forced full update failed: {error}")

    unreal.log("Dirt road painted successfully.")
    unreal.log("----------------------------------------")
    unreal.log(f"Road width: {ROAD_WIDTH:.1f} UU")
    unreal.log(f"Road radius: approximately {ROAD_WIDTH * 0.5:.1f} UU")
    unreal.log(f"Layer: {ROAD_LAYER_NAME}")
    unreal.log("----------------------------------------")

    return True


def load_asset(asset_path):
    """
    Load an asset from disk
    """
    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
    if asset is None:
        unreal.log_error(f"Could not load asset: {asset_path}")

    return asset


def clear_generated_objects():
    """
    Delete previously generated objects
    """
    actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = actor_subsystem.get_all_level_actors()

    deleted_count = 0

    for actor in actors:
        if any(tag in GENERATED_TAGS for tag in actor.tags):
            actor_subsystem.destroy_actor(actor)
            deleted_count += 1

    unreal.log(f"Deleted generated actors: {deleted_count}")


def line_trace_to_landscape(x, y):
    """
    Landscape trace
    """
    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_subsystem.get_editor_world()

    start = unreal.Vector(x, y, TRACE_HEIGHT)
    end = unreal.Vector(x, y, -TRACE_HEIGHT)

    hit = unreal.SystemLibrary.line_trace_single(
        world,
        start,
        end,
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        True,
        [],
        unreal.DrawDebugTrace.NONE,
        True
    )
    if hit is None:
        return None

    data = hit.to_tuple()
    if not data or not data[0]:
        return None

    return data[4], data[6]


def is_valid_tree_surface(normal):
    """
    Normal validation
    """
    if normal is None:
        return False

    normal_z = normal.z

    if normal_z < MIN_TREE_NORMAL_Z:
        return False

    if normal_z > MAX_TREE_NORMAL_Z:
        return False

    return True


def normalize_horizontal_vector(vector):
    """
    Makes vector normalization
    """
    length = math.sqrt(vector.x * vector.x + vector.y * vector.y)
    if length < 0.0001:
        return None

    return unreal.Vector(vector.x / length, vector.y / length, 0.0)

def get_spline_point(spline_component, distance, offset):
    spline_location = spline_component.get_location_at_distance_along_spline(distance, unreal.SplineCoordinateSpace.WORLD)
    spline_direction = spline_component.get_direction_at_distance_along_spline(distance, unreal.SplineCoordinateSpace.WORLD)

    horizontal_direction = normalize_horizontal_vector(spline_direction)
    if horizontal_direction is None:
        return None

    right_vector = unreal.Vector(-horizontal_direction.y, horizontal_direction.x, 0.0)
    return unreal.Vector(
        spline_location.x + right_vector.x * offset,
        spline_location.y + right_vector.y * offset,
        spline_location.z
    )


def get_spline_basis(spline_component, distance, offset):
    """
    Gets spline basis
    """
    spline_location = spline_component.get_location_at_distance_along_spline(distance, unreal.SplineCoordinateSpace.WORLD)
    spline_direction = spline_component.get_direction_at_distance_along_spline(distance, unreal.SplineCoordinateSpace.WORLD)

    horizontal_direction = normalize_horizontal_vector(spline_direction)
    if horizontal_direction is None:
        return None, None, None

    right_vector = unreal.Vector(-horizontal_direction.y, horizontal_direction.x, 0.0)
    location = unreal.Vector(
        spline_location.x + right_vector.x * offset,
        spline_location.y + right_vector.y * offset,
        spline_location.z
    )

    return location, horizontal_direction, right_vector


def get_gameplay_position(spline_component, distance, offset):
    """
    Returns a world-space position relative to the gameplay corridor.

    Negative offset = left of the spline.
    Positive offset = right of the spline.
    """
    basis = get_spline_basis(spline_component, distance, offset)

    if basis is None:
        return None

    location, _, _ = basis
    return location


def is_inside_gameplay_corridor(offset):
    """
    Checks whether an offset is inside the gameplay corridor.
    """
    return abs(offset) <= GAMEPLAY_HALF_WIDTH


def is_outside_gameplay_corridor(offset):
    """
    Checks whether an offset is outside the gameplay corridor.
    """
    return not is_inside_gameplay_corridor(offset)


def get_random_gameplay_offset():
    return random.uniform(-GAMEPLAY_HALF_WIDTH, GAMEPLAY_HALF_WIDTH)


def is_valid_decoration_offset(offset):
    """
    Checks whether a decorative object can be placed
    outside the gameplay corridor with the required gap.
    """
    minimum_offset = GAMEPLAY_HALF_WIDTH + DECORATION_GAMEPLAY_GAP

    return abs(offset) >= minimum_offset


def log_gameplay_corridor(spline_component, spline_length):
    """
    Logs gameplay corridor boundaries along the CanyonSpline.
    """
    unreal.log("\n========================================")
    unreal.log("GAMEPLAY CORRIDOR")
    unreal.log("========================================")

    center_distance = spline_length * 0.5

    center = get_gameplay_position(
        spline_component,
        center_distance,
        0.0
    )

    left = get_gameplay_position(
        spline_component,
        center_distance,
        -GAMEPLAY_HALF_WIDTH
    )

    right = get_gameplay_position(
        spline_component,
        center_distance,
        GAMEPLAY_HALF_WIDTH
    )

    if center is None or left is None or right is None:
        unreal.log_warning("Could not calculate gameplay corridor.")
        return

    unreal.log(f"Gameplay width: {GAMEPLAY_WIDTH:.1f} UU")
    unreal.log(f"Gameplay half width: {GAMEPLAY_HALF_WIDTH:.1f} UU")

    unreal.log(f"Center: X={center.x:.1f}, Y={center.y:.1f}, Z={center.z:.1f}")
    unreal.log(f"Left:   X={left.x:.1f}, Y={left.y:.1f}, Z={left.z:.1f}")
    unreal.log(f"Right:  X={right.x:.1f}, Y={right.y:.1f}, Z={right.z:.1f}")
    unreal.log("========================================")


def get_gameplay_landscape_position(spline_component, distance, offset):
    """
    Returns a world-space position on the Landscape
    inside the gameplay corridor.
    """
    gameplay_position = get_gameplay_position(spline_component, distance, offset)
    if gameplay_position is None:
        return None

    hit_result = line_trace_to_landscape(gameplay_position.x, gameplay_position.y)
    if hit_result is None:
        return None

    landscape_location, landscape_normal = hit_result
    return landscape_location, landscape_normal


def get_gameplay_position_at_distance(
    spline_component,
    distance,
    offset
):
    """
    Returns a valid Landscape position inside
    the gameplay corridor.
    """
    spline_length = spline_component.get_spline_length()

    if distance < 0.0 or distance > spline_length:
        return None

    if not is_inside_gameplay_corridor(offset):
        return None

    return get_gameplay_landscape_position(
        spline_component,
        distance,
        offset
    )


def get_random_gameplay_landscape_position(
    spline_component,
    spline_length,
    min_distance=0.0,
    max_distance=None
):
    """
    Returns a random valid Landscape position
    inside the gameplay corridor.
    """
    if max_distance is None:
        max_distance = spline_length

    distance = random.uniform(
        min_distance,
        max_distance
    )

    offset = get_random_gameplay_offset()

    return get_gameplay_position_at_distance(
        spline_component,
        distance,
        offset
    )


def validate_gameplay_corridor(spline_component, spline_length):
    """
    Validates gameplay corridor against the Landscape.
    """
    unreal.log("\n========================================")
    unreal.log("VALIDATING GAMEPLAY CORRIDOR")
    unreal.log("========================================")

    sample_count = 10
    trace_failed_count = 0

    for index in range(sample_count + 1):
        distance = (
            spline_length * index / sample_count
        )

        for side in (-1.0, 0.0, 1.0):
            offset = GAMEPLAY_HALF_WIDTH * side

            result = get_gameplay_landscape_position(
                spline_component,
                distance,
                offset
            )

            if result is None:
                trace_failed_count += 1
                unreal.log_warning(
                    f"Gameplay trace failed: "
                    f"distance={distance:.1f}, "
                    f"offset={offset:.1f}"
                )

    total_samples = (sample_count + 1) * 3

    unreal.log("----------------------------------------")
    unreal.log(f"Gameplay samples: {total_samples}")
    unreal.log(f"Trace failed: {trace_failed_count}")
    unreal.log("----------------------------------------")

    return trace_failed_count == 0


def spawn_tree(tree_mesh, location, scale_value, tree_index):
    """
    Spawns tree at location
    """
    rotation = unreal.Rotator(0.0, 0.0, 0.0)
    spawn_location = unreal.Vector(location.x, location.y, location.z + TREE_GROUND_OFFSET)

    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(tree_mesh, spawn_location, rotation)
    if actor is None:
        return None

    actor.tags = [GENERATED_TAG, GENERATED_TREE_TAG]
    actor.set_actor_label(f"SMA_Tree_{tree_index:03d}")
    actor.set_actor_scale3d(unreal.Vector(scale_value, scale_value, scale_value))

    # World Outliner folder
    set_actor_folder(actor, GENERATED_FOLDER_TREES)

    return actor


def spawn_boulder(boulder_mesh, location, scale_value, boulder_index):
    """
    Spawn boulder
    """
    rotation = unreal.Rotator(random.uniform(0.0, 360.0), random.uniform(0.0, 360.0), random.uniform(0.0, 360.0))
    spawn_location = unreal.Vector(location.x, location.y, random.uniform(0.0, BOULDER_GROUND_OFFSET))

    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(boulder_mesh, spawn_location, rotation)
    if actor is None:
        return None

    actor.tags = [GENERATED_TAG, GENERATED_BOULDER_TAG]
    actor.set_actor_label(f"SMA_Boulder_{boulder_index:03d}")
    actor.set_actor_scale3d(unreal.Vector(scale_value, scale_value, scale_value))

    # World Outliner folder
    set_actor_folder(actor, GENERATED_FOLDER_BOULDERS)

    return actor

def spawn_cliff(asset, location, rotation, scale, side: str, row):
    """
    Spawn Cliff
    """
    actor = unreal.EditorLevelLibrary.spawn_actor_from_object(asset, location, rotation)
    if not actor:
        return None

    actor.tags = [GENERATED_TAG, GENERATED_CLIFF_TAG]
    actor.set_actor_label(f"SMA_Cliff_{side}_{row}")
    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))

    # World Outliner folder
    set_actor_folder(actor, GENERATED_FOLDER_CLIFFS)

    return actor


def spawn_gameplay_rock(rock_asset, location, scale):
    """
    Spawns a gameplay rock at the specified Landscape position.
    """
    rotation = unreal.Rotator(0.0, 0.0, random.uniform(0.0, 360.0))

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(unreal.StaticMeshActor, location, rotation)
    if actor is None:
        return None

    mesh_component = actor.static_mesh_component
    mesh_component.set_static_mesh(rock_asset)
    mesh_component.set_collision_enabled(unreal.CollisionEnabled.QUERY_AND_PHYSICS)
    mesh_component.set_collision_profile_name("BlockAll")
    mesh_component.set_simulate_physics(True)

    actor.set_actor_scale3d(unreal.Vector(scale, scale, scale))
    actor.tags = [GAMEPLAY_ROCK_TAG]
    set_actor_folder(actor, GAMEPLAY_ROCK_FOLDER)
    actor.set_actor_label(f"SMA_GameplayRock_{random.randint(100000, 999999)}")

    return actor


def is_tree_position_valid(location, existing_tree_locations):
    """
    Checks if the tree distance is valid
    """
    minimum_distance_squared = (TREE_MIN_DISTANCE * TREE_MIN_DISTANCE)

    for existing_location in existing_tree_locations:
        delta_x = (location.x - existing_location.x)
        delta_y = (location.y - existing_location.y)

        if (delta_x * delta_x + delta_y * delta_y) < minimum_distance_squared:
            return False

    return True


def is_gameplay_position_valid(location, existing_locations, min_distance):
    """
    Checks whether a gameplay object can be placed
    at the specified location.
    """
    for existing_location in existing_locations:
        distance_squared = (
            (location.x - existing_location.x) ** 2
            + (location.y - existing_location.y) ** 2
        )

        if distance_squared < min_distance ** 2:
            return False

    return True


def find_free_gameplay_position(
    spline_component,
    spline_length,
    existing_locations,
    min_distance,
    min_spline_distance=0.0,
    max_spline_distance=None,
    max_attempts=20
):
    """
    Finds a random valid Landscape position inside
    the gameplay corridor.
    """
    if max_spline_distance is None:
        max_spline_distance = spline_length

    for _ in range(max_attempts):
        result = get_random_gameplay_landscape_position(
            spline_component,
            spline_length,
            min_spline_distance,
            max_spline_distance
        )
        if result is None:
            continue

        location, normal = result

        if not is_gameplay_position_valid(
            location,
            existing_locations,
            min_distance
        ):
            continue

        return location, normal

    return None


def generate_trees(spline_component, tree_mesh, spline_length):
    """
    Generates trees
    """
    unreal.log("\n========================================")
    unreal.log("GENERATING TREES")
    unreal.log("========================================")

    existing_tree_locations = []
    generated_count = 0
    attempts = 0
    max_attempts = TREE_COUNT * 30

    # Diagnostics
    trace_failed_count = 0
    invalid_normal_count = 0
    too_close_count = 0
    spawn_failed_count = 0
    invalid_gameplay_offset_count = 0

    while generated_count < TREE_COUNT and attempts < max_attempts:
        attempts += 1

        distance = random.uniform(0.0, spline_length)
        side = random.choice([-1.0, 1.0])
        offset = random.uniform(TREE_MIN_OFFSET, TREE_MAX_OFFSET) * side

        if not is_valid_decoration_offset(offset):
            invalid_gameplay_offset_count += 1
            continue

        spline_location = get_spline_point(spline_component, distance, offset)
        if spline_location is None:
            continue

        hit_result = line_trace_to_landscape(spline_location.x, spline_location.y)
        if hit_result is None:
            trace_failed_count += 1
            continue

        landscape_location, landscape_normal = hit_result
        if not is_valid_tree_surface(landscape_normal):
            invalid_normal_count += 1
            continue

        if not is_tree_position_valid(landscape_location, existing_tree_locations):
            continue

        scale_value = random.uniform(TREE_MIN_SCALE, TREE_MAX_SCALE)

        actor = spawn_tree(tree_mesh, landscape_location, scale_value, generated_count)
        if actor is None:
            spawn_failed_count += 1
            continue

        existing_tree_locations.append(landscape_location)
        generated_count += 1

    # Results
    unreal.log("----------------------------------------")
    unreal.log(f"Trees generated: {generated_count} / {TREE_COUNT}")
    unreal.log(f"Tree generation attempts: {attempts}")
    unreal.log(f"\nTrace failed: {trace_failed_count}")
    unreal.log(f"Invalid surface normal: {invalid_normal_count}")
    unreal.log(f"Too close to existing tree: {too_close_count}")
    unreal.log(f"Tree spawn failed: {spawn_failed_count}")
    unreal.log(f"Invalid gameplay offset: {invalid_gameplay_offset_count}")
    unreal.log("----------------------------------------")

    if generated_count < TREE_COUNT:
        unreal.log_warning(
            "Could not place all requested trees. See diagnostic counters above."
        )

    return generated_count

def generate_boulders(spline_component, boulder_mesh, spline_length):
    """
    Generate boulders
    """
    unreal.log("\n========================================")
    unreal.log("GENERATING BOULDERS")
    unreal.log("========================================")

    generated_count = 0
    attempts = 0
    invalid_gameplay_offset_count = 0

    max_attempts = BOULDER_COUNT * 20

    while generated_count < BOULDER_COUNT and attempts < max_attempts:
        attempts += 1
        distance = random.uniform(0.0, spline_length)
        side = random.choice([-1.0, 1.0])
        offset = random.uniform(BOULDER_MIN_OFFSET, BOULDER_MAX_OFFSET) * side

        if not is_valid_decoration_offset(offset):
            invalid_gameplay_offset_count += 1
            continue

        spline_location = get_spline_point(spline_component, distance, offset)
        if spline_location is None:
            continue

        hit_result = line_trace_to_landscape(spline_location.x, spline_location.y)
        if hit_result is None:
            continue

        landscape_location, _ = hit_result
        scale_value = random.uniform(BOULDER_MIN_SCALE, BOULDER_MAX_SCALE)

        actor = spawn_boulder(boulder_mesh, landscape_location, scale_value, generated_count)
        if actor is None:
            continue

        generated_count += 1

    unreal.log("----------------------------------------")
    unreal.log(f"Boulders generated: {generated_count} / {BOULDER_COUNT}")
    unreal.log(f"Boulder generation attempts: {attempts}")
    unreal.log(f"Invalid gameplay offset: {invalid_gameplay_offset_count}")
    unreal.log("----------------------------------------")

    if generated_count < BOULDER_COUNT:
        unreal.log_warning("Could not place all requested boulders.")

    return generated_count


def generate_cliffs(spline, asset):
    """
    Generate cliffs with improved scan of height
    """
    unreal.log("========================================")
    unreal.log("GENERATING CLIFFS")
    unreal.log("========================================")

    spline_length = spline.get_spline_length()
    generated = []
    attempts = 0
    trace_failed = 0
    invalid_normal = 0
    too_close = 0
    spawn_failed = 0

    # Список акторов, которые трассировка должна полностью игнорировать
    cliffs_to_ignore = []

    def try_spawn_cliff(distance, side, row, min_offset, max_offset, min_scale, max_scale):
        nonlocal attempts, trace_failed, invalid_normal, too_close, spawn_failed
        attempts += 1

        offset_dist = random.uniform(min_offset, max_offset) * side

        # Сканируем ландшафт по 3 точкам
        sample_distances = [distance - 300.0, distance, distance + 300.0]
        total_z = 0.0
        valid_samples = 0
        best_hit_location = None
        best_hit_normal = None

        _, current_dir, _ = get_spline_basis(spline, distance, offset_dist)

        for d in sample_distances:
            clamped_d = max(0.0, min(d, spline_length))
            basis = get_spline_basis(spline, clamped_d, offset_dist)
            if basis is None:
                continue

            pos, _, _ = basis

            # ВАЖНО: Модифицируем стандартный trace. Передаем массив cliffs_to_ignore,
            # чтобы лучи игнорировали уже построенные скалы и мерили ТОЛЬКО ландшафт.
            start = unreal.Vector(pos.x, pos.y, TRACE_HEIGHT)
            end = unreal.Vector(pos.x, pos.y, -TRACE_HEIGHT)

            editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            world = editor_subsystem.get_editor_world()

            hit = unreal.SystemLibrary.line_trace_single(
                world, start, end,
                unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                True,
                cliffs_to_ignore,  # Добавлено игнорирование старых скал
                unreal.DrawDebugTrace.NONE,
                True
            )

            if hit:
                data = hit.to_tuple()
                if data and data[0]:
                    loc, norm = data[4], data[6]
                    total_z += loc.z
                    valid_samples += 1
                    if d == distance:
                        best_hit_location = loc
                        best_hit_normal = norm

        if valid_samples == 0 or best_hit_location is None:
            trace_failed += 1
            return False

        if best_hit_normal.z < MIN_TREE_NORMAL_Z:
            invalid_normal += 1
            return False

        # Проверка дистанции до соседних объектов
        min_distance_sq = CLIFF_MIN_DISTANCE ** 2
        for existing_location in generated:
            dx = best_hit_location.x - existing_location.x
            dy = best_hit_location.y - existing_location.y
            if dx * dx + dy * dy < min_distance_sq:
                too_close += 1
                return False

        # Расчет направления (Yaw)
        base_yaw = math.degrees(math.atan2(current_dir.y, current_dir.x)) if current_dir else 0.0
        target_yaw = base_yaw + (180.0 if side > 0 else 0.0)

        # Устранение лесенок: Рассчитываем угол наклона земли (Pitch) вдоль ландшафта
        # чтобы скала повторяла подъем или спуск холма, а не стояла строго вертикально
        pitch_angle = 0.0
        if best_hit_normal:
            # Проекция наклона нормали на вектор направления дороги
            forward_slope = best_hit_normal.x * current_dir.x + best_hit_normal.y * current_dir.y
            pitch_angle = math.degrees(math.asin(forward_slope)) * -0.5  # Мягкое сглаживание наклона

        rotation = unreal.Rotator(pitch_angle, target_yaw, 0.0)
        scale = random.uniform(min_scale, max_scale)

        average_z = total_z / valid_samples

        location = unreal.Vector(
            best_hit_location.x,
            best_hit_location.y,
            average_z + CLIFF_GROUND_OFFSET + random.uniform(-CLIFF_Z_JITTER, CLIFF_Z_JITTER)
        )

        actor = spawn_cliff(asset, location, rotation, scale, "Left" if side < 0 else "Right", row)
        if not actor:
            spawn_failed += 1
            return False

        # Запоминаем актора, чтобы следующие скалы его игнорировали при поиске высоты
        cliffs_to_ignore.append(actor)
        generated.append(best_hit_location)
        return True

    # Настройка шага спавна для Inner ряда
    step = CLIFF_LENGTH - CLIFF_OVERLAP
    cliffs_per_side = int(spline_length / step) + 1

    for side in (-1, 1):
        for index in range(cliffs_per_side):
            distance = (index * step)
            distance = max(0.0, min(distance, spline_length))

            try_spawn_cliff(
                distance, side, "Inner",
                CLIFF_INNER_MIN_OFFSET, CLIFF_INNER_MAX_OFFSET,
                CLIFF_INNER_MIN_SCALE, CLIFF_INNER_MAX_SCALE
            )

    # Outer ряд
    target_outer = CLIFF_OUTER_COUNT_PER_SIDE
    for side in (-1, 1):
        created = 0
        local_attempts = 0
        while created < target_outer:
            local_attempts += 1
            if local_attempts > target_outer * 20:
                break
            distance = random.uniform(0.0, spline_length)
            if try_spawn_cliff(
                    distance, side, "Outer",
                    CLIFF_OUTER_MIN_OFFSET, CLIFF_OUTER_MAX_OFFSET,
                    CLIFF_OUTER_MIN_SCALE, CLIFF_OUTER_MAX_SCALE
            ):
                created += 1

    return len(generated)


def generate_cliffs(spline, asset):
    """
    Generate cliffs with improved scan of height
    """
    unreal.log("========================================")
    unreal.log("GENERATING CLIFFS")
    unreal.log("========================================")

    spline_length = spline.get_spline_length()
    generated = []
    attempts = 0
    trace_failed = 0
    invalid_normal = 0
    too_close = 0
    spawn_failed = 0

    # Use a strictly typed Unreal Array to safely ignore previously spawned cliffs
    cliffs_to_ignore = unreal.Array(unreal.Actor)

    def try_spawn_cliff(distance, side, row, min_offset, max_offset, min_scale, max_scale):
        nonlocal attempts, trace_failed, invalid_normal, too_close, spawn_failed
        attempts += 1

        offset_dist = random.uniform(min_offset, max_offset) * side

        # Scan the landscape at 3 points to calculate a stable average Z height
        sample_distances = [distance - 300.0, distance, distance + 300.0]
        total_z = 0.0
        valid_samples = 0
        best_hit_location = None
        best_hit_normal = None

        _, current_dir, _ = get_spline_basis(spline, distance, offset_dist)

        for d in sample_distances:
            clamped_d = max(0.0, min(d, spline_length))
            basis = get_spline_basis(spline, clamped_d, offset_dist)
            if basis is None:
                continue

            pos, _, _ = basis

            start = unreal.Vector(pos.x, pos.y, TRACE_HEIGHT)
            end = unreal.Vector(pos.x, pos.y, -TRACE_HEIGHT)

            editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
            world = editor_subsystem.get_editor_world()

            # Line trace shoots through already generated cliffs directly to the landscape
            hit = unreal.SystemLibrary.line_trace_single(
                world, start, end,
                unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
                True,
                cliffs_to_ignore,
                unreal.DrawDebugTrace.NONE,
                True
            )

            if hit:
                data = hit.to_tuple()
                if data and data[0]:
                    loc, norm = data[4], data[6]
                    total_z += loc.z
                    valid_samples += 1
                    if d == distance:
                        best_hit_location = loc
                        best_hit_normal = norm

        if valid_samples == 0 or best_hit_location is None:
            trace_failed += 1
            return False

        if best_hit_normal.z < MIN_TREE_NORMAL_Z:
            invalid_normal += 1
            return False

        # Check distance to neighbor objects
        min_distance_sq = CLIFF_MIN_DISTANCE ** 2
        for existing_location in generated:
            dx = best_hit_location.x - existing_location.x
            dy = best_hit_location.y - existing_location.y
            if dx * dx + dy * dy < min_distance_sq:
                too_close += 1
                return False

        # Calculate rotation in direction of spline (Yaw)
        base_yaw = math.degrees(math.atan2(current_dir.y, current_dir.x)) if current_dir else 0.0
        target_yaw = base_yaw + (180.0 if side > 0 else 0.0)

        # Pitch guaranty equals zero, and cliffs will places up ideally,
        rotation = unreal.Rotator(roll=0.0, pitch=0.0, yaw=target_yaw)
        scale = random.uniform(min_scale, max_scale)

        average_z = total_z / valid_samples

        # Align position to middle height
        location = unreal.Vector(
            best_hit_location.x,
            best_hit_location.y,
            average_z + CLIFF_GROUND_OFFSET
        )

        actor = spawn_cliff(asset, location, rotation, scale, "Left" if side < 0 else "Right", row)
        if not actor:
            spawn_failed += 1
            return False

        cliffs_to_ignore.append(actor)
        generated.append(best_hit_location)
        return True

    # Tune step of spawn for inner row
    step = CLIFF_LENGTH - CLIFF_OVERLAP
    cliffs_per_side = int(spline_length / step) + 1

    for side in (-1, 1):
        for index in range(cliffs_per_side):
            distance = (index * step)
            distance = max(0.0, min(distance, spline_length))

            try_spawn_cliff(
                distance, side, "Inner",
                CLIFF_INNER_MIN_OFFSET, CLIFF_INNER_MAX_OFFSET,
                CLIFF_INNER_MIN_SCALE, CLIFF_INNER_MAX_SCALE
            )

    # Outer row
    target_outer = CLIFF_OUTER_COUNT_PER_SIDE
    for side in (-1, 1):
        created = 0
        local_attempts = 0
        while created < target_outer:
            local_attempts += 1
            if local_attempts > target_outer * 20:
                break
            distance = random.uniform(0.0, spline_length)
            if try_spawn_cliff(
                    distance, side, "Outer",
                    CLIFF_OUTER_MIN_OFFSET, CLIFF_OUTER_MAX_OFFSET,
                    CLIFF_OUTER_MIN_SCALE, CLIFF_OUTER_MAX_SCALE
            ):
                created += 1

    return len(generated)


def generate_gameplay_rocks(spline_component, spline_length, rock_asset):
    """
    Generates gameplay rocks inside the gameplay corridor.
    """
    unreal.log("\n========================================")
    unreal.log("GENERATING GAMEPLAY ROCKS")
    unreal.log("========================================")

    generated_locations = []
    spawned_count = 0

    max_spline_distance = GAMEPLAY_ROCK_MAX_SPLINE_DISTANCE

    if max_spline_distance < 0.0:
        max_spline_distance = spline_length

    for index in range(GAMEPLAY_ROCK_COUNT):
        result = find_free_gameplay_position(
            spline_component,
            spline_length,
            generated_locations,
            GAMEPLAY_ROCK_MIN_DISTANCE,
            GAMEPLAY_ROCK_MIN_SPLINE_DISTANCE,
            max_spline_distance
        )

        if result is None:
            unreal.log_warning(f"Could not find free position for gameplay rock {index + 1}")
            continue

        location, _ = result

        scale = random.uniform( GAMEPLAY_ROCK_MIN_SCALE, GAMEPLAY_ROCK_MAX_SCALE)
        location = unreal.Vector(
            location.x,
            location.y,
            location.z + GAMEPLAY_ROCK_GROUND_OFFSET
        )

        actor = spawn_gameplay_rock(rock_asset, location, scale)
        if actor is None:
            continue

        generated_locations.append(location)
        spawned_count += 1

    unreal.log("----------------------------------------")
    unreal.log(f"Gameplay rocks spawned: {spawned_count}")
    unreal.log("----------------------------------------")

    return spawned_count


def draw_gameplay_corridor(spline_component, spline_length):
    """
    Draws the gameplay corridor boundaries for visual debugging.
    """
    unreal.log("\n========================================")
    unreal.log("DRAWING GAMEPLAY CORRIDOR")
    unreal.log("========================================")

    editor_subsystem = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem)
    world = editor_subsystem.get_editor_world()

    sample_count = 50

    previous_left = None
    previous_right = None
    previous_center = None

    for index in range(sample_count + 1):
        distance = spline_length * index / sample_count

        left_result = get_gameplay_landscape_position(
            spline_component,
            distance,
            -GAMEPLAY_HALF_WIDTH
        )

        center_result = get_gameplay_landscape_position(
            spline_component,
            distance,
            0.0
        )

        right_result = get_gameplay_landscape_position(
            spline_component,
            distance,
            GAMEPLAY_HALF_WIDTH
        )

        if left_result is None or center_result is None or right_result is None:
            continue

        left_location, _ = left_result
        center_location, _ = center_result
        right_location, _ = right_result

        # Lift debug lines slightly above Landscape.
        debug_offset = 20.0

        left_location = unreal.Vector(
            left_location.x,
            left_location.y,
            left_location.z + debug_offset
        )

        center_location = unreal.Vector(
            center_location.x,
            center_location.y,
            center_location.z + debug_offset
        )

        right_location = unreal.Vector(
            right_location.x,
            right_location.y,
            right_location.z + debug_offset
        )

        if previous_left is not None:
            unreal.SystemLibrary.draw_debug_line(
                world,
                previous_left,
                left_location,
                unreal.LinearColor(1.0, 0.0, 0.0, 1.0),
                60.0,
                0.0
            )

        if previous_center is not None:
            unreal.SystemLibrary.draw_debug_line(
                world,
                previous_center,
                center_location,
                unreal.LinearColor(1.0, 1.0, 0.0, 1.0),
                40.0,
                0.0
            )

        if previous_right is not None:
            unreal.SystemLibrary.draw_debug_line(
                world,
                previous_right,
                right_location,
                unreal.LinearColor(0.0, 0.0, 1.0, 1.0),
                60.0,
                0.0
            )

        previous_left = left_location
        previous_center = center_location
        previous_right = right_location

    unreal.log(f"Gameplay width: {GAMEPLAY_WIDTH:.1f} UU")
    unreal.log("Gameplay corridor debug drawing complete.")


def main():
    unreal.log("\n========================================")
    unreal.log("CANYON GENERATOR")
    unreal.log("========================================")

    # Random
    initialize_random()

    # Find Spline
    spline_component = find_canyon_spline()
    if spline_component is None:
        unreal.log_error("Generation aborted: CanyonSpline not found.")
        return

    spline_length = spline_component.get_spline_length()
    if spline_length <= 0.0:
        unreal.log_error("Generation aborted: Spline length is zero.")
        return

    unreal.log(f"Spline length: {spline_length:.2f} UU")

    log_gameplay_corridor(spline_component, spline_length)

    if not validate_gameplay_corridor(spline_component, spline_length):
        unreal.log_error(f"Generation aborted: Gameplay corridor validation failed.")
        return

    draw_gameplay_corridor(spline_component, spline_length)

    # Paint road
    if ROAD_PAINT_ENABLED:
        if not paint_dirt_along_canyon(spline_component):
            unreal.log_error("Generation aborted: Dirt road could not be painted.")
            return

    tree_mesh = load_asset(TREE_ASSET)
    boulder_mesh = load_asset(BOULDER_ASSET)
    cliff_mesh = load_asset(CLIFF_ASSET)

    if not tree_mesh or not boulder_mesh or not cliff_mesh:
        unreal.log_error("Failed to load some asset, check configuration section.")
        return

    clear_generated_objects()

    tree_count = generate_trees(spline_component, tree_mesh, spline_length)
    boulder_count = generate_boulders(spline_component, boulder_mesh, spline_length)
    cliff_count = generate_cliffs(spline_component, cliff_mesh)

    rocks_count = 0
    if IS_GAMEPLAY_GENERATION_ENABLED:
        rocks_count = generate_gameplay_rocks(spline_component, spline_length, boulder_mesh)

    unreal.log("\n========================================")
    unreal.log("GENERATION FINISHED")
    unreal.log("========================================")

    unreal.log(f"         Trees: {tree_count} / {TREE_COUNT}")
    unreal.log(f"      Boulders: {boulder_count} / {BOULDER_COUNT}")
    unreal.log(f"        Cliffs: {cliff_count}")
    unreal.log(f" Spline length: {spline_length:.2f} UU")

    if IS_GAMEPLAY_GENERATION_ENABLED:
        unreal.log(f"Gameplay rocks: {rocks_count} / {GAMEPLAY_ROCK_COUNT}")

    unreal.log(f"\n"
               f" Road painting: {'ON' if ROAD_PAINT_ENABLED else 'OFF'}")
    if ROAD_PAINT_ENABLED:
        unreal.log(f"    Road layer: {ROAD_LAYER_NAME}")
        unreal.log(f"    Road width: {ROAD_WIDTH:.1f} UU")
        unreal.log(f"   Road radius: {ROAD_WIDTH * 0.5:.1f} UU")

    unreal.log("\n"
               "  Tree rotation: Pitch=0, Yaw=0, Roll=0")
    unreal.log(f"   Tree offset: {TREE_MIN_OFFSET} - {TREE_MAX_OFFSET} UU")
    unreal.log(f"Boulder offset: {BOULDER_MIN_OFFSET} - {BOULDER_MAX_OFFSET} UU")

    unreal.log("\nGenerated folders:")
    unreal.log(f"         Trees: {GENERATED_FOLDER_TREES}")
    unreal.log(f"      Boulders: {GENERATED_FOLDER_BOULDERS}")
    unreal.log(f"        Cliffs: {GENERATED_FOLDER_CLIFFS}")

    if IS_GAMEPLAY_GENERATION_ENABLED:
        unreal.log(f"Gameplay rocks: {GAMEPLAY_ROCK_FOLDER}")

    unreal.log("========================================")
    unreal.log("DONE")
    unreal.log("========================================")


if __name__ == "__main__":
    main()
