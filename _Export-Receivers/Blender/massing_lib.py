"""
massing_lib.py — shared helpers for build_massing_template.py and import_massing.py.
Pure bpy + stdlib math, no add-ons required (Blender 4.2+ moved most bundled add-ons,
including "Sun Position", to the online Extensions platform — not available on an
offline/locked-down install). Sun angle is computed here directly instead.

Import by adding this file's folder to sys.path before `import massing_lib`.
"""
import bpy
import bmesh
import math

# ---- schema constants, matched to Massing-Studio.html (Nonimuss-Residence/3_Massing) ----
# type -> 0xRRGGBB, exactly the Studio's own COLOR map (buildInterchange / three.js COLOR const)
TYPE_COLORS_HEX = {
    "house":  0x5b6b7a,
    "office": 0xf2f0ea,
    "pool":   0x7fb0d0,
    "link":   0xb49bd0,
    "gym":    0x9aa39a,
    "terr":   0xe6d9b8,
}
VOLUME_TYPES = list(TYPE_COLORS_HEX.keys())

TIER_A_PREFIX = "TierA_"
TIER_B_NAMES = [
    "Brick",
    "WoodSiding",
    "MetalRoof_StandingSeam",
    "Stucco",
    "ConcreteBoardFormed",
    "Glazing_CurtainWall",
    "StoneVeneer",
    "RoofShingle_Asphalt",
    "Metal_Generic",
    "Paving_Hardscape",
]
GROUND_MATERIAL_NAME = "Ground_Generic"  # utility material for the template's base plane, not part of Tier B


def srgb_to_linear(c):
    c = c / 255.0
    if c <= 0.04045:
        return c / 12.92
    return ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear_rgba(hex_int, alpha=1.0):
    r = (hex_int >> 16) & 0xFF
    g = (hex_int >> 8) & 0xFF
    b = hex_int & 0xFF
    return (srgb_to_linear(r), srgb_to_linear(g), srgb_to_linear(b), alpha)


def solar_elevation_azimuth(lat_deg, lon_deg, year, month, day, hour_utc):
    """Meeus low-precision solar position (~0.01 deg accuracy).
    Validated against Massing-Studio.html's own reference altitudes for
    Nonimuss-Residence (lat 50.99N): winter-solstice noon 15.6 deg, summer 62.4 deg —
    this function reproduces 15.57 / 62.44. Returns (elevation_deg, azimuth_deg_from_north_cw).
    """
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    jd = jdn + (hour_utc - 12) / 24.0
    n = jd - 2451545.0  # days since J2000.0

    L = math.radians((280.460 + 0.9856474 * n) % 360)
    g = math.radians((357.528 + 0.9856003 * n) % 360)
    lam = L + math.radians(1.915) * math.sin(g) + math.radians(0.020) * math.sin(2 * g)
    eps = math.radians(23.439 - 0.0000004 * n)

    ra = math.atan2(math.cos(eps) * math.sin(lam), math.cos(lam))
    dec = math.asin(math.sin(eps) * math.sin(lam))

    gmst = (6.697375 + 0.0657098242 * n + hour_utc) % 24.0
    lst_hours = (gmst + lon_deg / 15.0) % 24.0
    H = math.radians(lst_hours * 15.0) - ra
    H = (H + math.pi) % (2 * math.pi) - math.pi  # normalize to [-pi, pi]

    lat = math.radians(lat_deg)
    elev = math.asin(math.sin(lat) * math.sin(dec) + math.cos(lat) * math.cos(dec) * math.cos(H))
    az = math.atan2(-math.sin(H), math.cos(lat) * math.tan(dec) - math.sin(lat) * math.cos(H))
    az_deg = (math.degrees(az) + 360) % 360
    return math.degrees(elev), az_deg


def solar_noon_utc_hour(lon_deg, year, month, day):
    """Coarse scan (10-min steps) to find the UTC hour of true solar noon at this longitude/date."""
    best_h, best_elev = 12.0, -999
    for i in range(0, 24 * 6):
        h = i / 6.0
        elev, _ = solar_elevation_azimuth(0.0, lon_deg, year, month, day, h)
        if elev > best_elev:
            best_elev, best_h = elev, h
    return best_h


def get_or_create_collection(name, parent=None):
    coll = bpy.data.collections.get(name)
    if coll is None:
        coll = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(coll)
    return coll


def get_or_create_material(name, base_color_rgba, roughness=0.6, metallic=0.0,
                            transmission=0.0, ior=1.45, anisotropic=0.0):
    mat = bpy.data.materials.get(name)
    if mat is not None:
        return mat
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = base_color_rgba
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if "Transmission Weight" in bsdf.inputs:  # Blender 4.x renamed input
        bsdf.inputs["Transmission Weight"].default_value = transmission
    elif "Transmission" in bsdf.inputs:
        bsdf.inputs["Transmission"].default_value = transmission
    bsdf.inputs["IOR"].default_value = ior
    if "Anisotropic" in bsdf.inputs:
        bsdf.inputs["Anisotropic"].default_value = anisotropic
    mat.diffuse_color = base_color_rgba
    # Without this, Blender drops zero-user data-blocks on save — and Tier A/B materials are
    # deliberately unassigned in the template (Tier B especially: reserved for later one-line
    # assignment during an interactive session), so they'd silently vanish from the .blend.
    mat.use_fake_user = True
    return mat


def build_tier_a_materials():
    """One flat/matte material per volume type, colors matched to the Studio's own COLOR map."""
    mats = {}
    for t, hexcol in TYPE_COLORS_HEX.items():
        name = TIER_A_PREFIX + t
        mats[t] = get_or_create_material(name, hex_to_linear_rgba(hexcol), roughness=0.75, metallic=0.0)
    return mats


def _add_brick_procedural(mat):
    """Simple procedural brick pattern feeding the Principled BSDF's base color — schematic, not photoreal."""
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.inputs["Color1"].default_value = hex_to_linear_rgba(0xa14a34)
    brick.inputs["Color2"].default_value = hex_to_linear_rgba(0x8a3d2b)
    brick.inputs["Mortar"].default_value = hex_to_linear_rgba(0xc9c2b0)
    brick.inputs["Scale"].default_value = 8.0
    mapping = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(mapping.outputs["Generated"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.85


def _add_concrete_formwork(mat):
    """Board-formed concrete: subtle banded roughness variation via a wave texture."""
    nt = mat.node_tree
    bsdf = nt.nodes.get("Principled BSDF")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = 'BANDS'
    wave.inputs["Scale"].default_value = 25.0
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.45
    ramp.color_ramp.elements[1].position = 0.55
    mapping = nt.nodes.new("ShaderNodeTexCoord")
    nt.links.new(mapping.outputs["Generated"], wave.inputs["Vector"])
    nt.links.new(wave.outputs["Fac"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], bsdf.inputs["Roughness"])


def build_tier_b_materials():
    """The 10 fixed advanced materials, ready for one-line assignment in a later interactive session."""
    mats = {}

    mats["Brick"] = get_or_create_material(
        "Brick", hex_to_linear_rgba(0xa14a34), roughness=0.85, metallic=0.0)
    _add_brick_procedural(mats["Brick"])

    mats["WoodSiding"] = get_or_create_material(
        "WoodSiding", hex_to_linear_rgba(0x8a5a34), roughness=0.55, metallic=0.0)

    mats["MetalRoof_StandingSeam"] = get_or_create_material(
        "MetalRoof_StandingSeam", hex_to_linear_rgba(0x3a3f42), roughness=0.28, metallic=0.85)
    bsdf = mats["MetalRoof_StandingSeam"].node_tree.nodes.get("Principled BSDF")
    if "Anisotropic" in bsdf.inputs:
        bsdf.inputs["Anisotropic"].default_value = 0.6

    mats["Stucco"] = get_or_create_material(
        "Stucco", hex_to_linear_rgba(0xe8e2d3), roughness=0.8, metallic=0.0)

    mats["ConcreteBoardFormed"] = get_or_create_material(
        "ConcreteBoardFormed", hex_to_linear_rgba(0x9b9b93), roughness=0.65, metallic=0.0)
    _add_concrete_formwork(mats["ConcreteBoardFormed"])

    mats["Glazing_CurtainWall"] = get_or_create_material(
        "Glazing_CurtainWall", hex_to_linear_rgba(0xbfd7e0, alpha=0.15),
        roughness=0.05, metallic=0.0, transmission=1.0, ior=1.52)
    mats["Glazing_CurtainWall"].blend_method = 'BLEND'
    mats["Glazing_CurtainWall"].show_transparent_back = False

    mats["StoneVeneer"] = get_or_create_material(
        "StoneVeneer", hex_to_linear_rgba(0x8c8271), roughness=0.75, metallic=0.0)

    mats["RoofShingle_Asphalt"] = get_or_create_material(
        "RoofShingle_Asphalt", hex_to_linear_rgba(0x53504c), roughness=0.7, metallic=0.0)

    # Metal - generic: reused for curtain-wall mullions, flashing, parapet cap flashing, exposed structural steel.
    mats["Metal_Generic"] = get_or_create_material(
        "Metal_Generic", hex_to_linear_rgba(0x9aa0a6), roughness=0.35, metallic=0.9)

    mats["Paving_Hardscape"] = get_or_create_material(
        "Paving_Hardscape", hex_to_linear_rgba(0xa9a49b), roughness=0.9, metallic=0.0)

    return mats


def build_ground_material():
    return get_or_create_material(GROUND_MATERIAL_NAME, hex_to_linear_rgba(0x8f9a86), roughness=0.9, metallic=0.0)


def setup_world_nishita_sky():
    world = bpy.data.worlds.get("World") or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    sky = nt.nodes.new("ShaderNodeTexSky")
    sky.sky_type = 'NISHITA'
    sky.sun_elevation = math.radians(45.0)
    sky.sun_rotation = math.radians(0.0)
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    return sky


def get_or_create_sun():
    sun_obj = bpy.data.objects.get("Sun")
    if sun_obj is None:
        sun_data = bpy.data.lights.new("Sun", type='SUN')
        sun_obj = bpy.data.objects.new("Sun", sun_data)
        bpy.context.scene.collection.objects.link(sun_obj)
    return sun_obj


def set_sun(elevation_deg, azimuth_deg):
    """Point the Sun object AND the world's Nishita sky at the same solar angle.
    azimuth_deg is measured from North, clockwise (matches solar_elevation_azimuth's output).

    Rotation formula (rx=pi/2-elev, ry=0, rz=pi-az) was derived and numerically verified
    against the expected sun-direction vector (sin(az)cos(elev), cos(az)cos(elev), sin(elev))
    for East/North/mid-azimuth/high-elevation cases before use here — see fork transcript.
    """
    sun_obj = get_or_create_sun()
    sun_obj.rotation_mode = 'XYZ'
    elev = math.radians(elevation_deg)
    az = math.radians(azimuth_deg)
    sun_obj.rotation_euler = (math.pi / 2 - elev, 0.0, math.pi - az)

    world = bpy.context.scene.world
    if world and world.use_nodes:
        sky_node = next((n for n in world.node_tree.nodes if n.type == 'TEX_SKY'), None)
        if sky_node is not None:
            sky_node.sun_elevation = elev
            sky_node.sun_rotation = az
    return sun_obj


def make_box_mesh(name, x_min, y_min, z_min, x_max, y_max, z_max):
    """Build a box mesh directly in world coordinates (object stays at origin, no transform math needed)."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()
    verts = [
        bm.verts.new((x_min, y_min, z_min)),
        bm.verts.new((x_max, y_min, z_min)),
        bm.verts.new((x_max, y_max, z_min)),
        bm.verts.new((x_min, y_max, z_min)),
        bm.verts.new((x_min, y_min, z_max)),
        bm.verts.new((x_max, y_min, z_max)),
        bm.verts.new((x_max, y_max, z_max)),
        bm.verts.new((x_min, y_max, z_max)),
    ]
    faces = [
        (0, 1, 2, 3), (4, 5, 6, 7),
        (0, 1, 5, 4), (1, 2, 6, 5),
        (2, 3, 7, 6), (3, 0, 4, 7),
    ]
    for f in faces:
        bm.faces.new([verts[i] for i in f])
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    return obj


def interchange_xz_to_blender_xy(x, z):
    """axes note in massing.json: x=East, z=South, y=Up, 'North is -z'.
    Blender convention here: +X=East (unchanged), +Y=North => blender_y = -interchange_z."""
    return x, -z
