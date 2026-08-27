"""
build_massing_template.py — builds the reusable _Massing-Template.blend.
Run ONCE (re-run only if you want to rebuild the template from scratch):

    "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe" --background --python build_massing_template.py

Produces `_Massing-Template.blend` next to this script. See README.md for the full pipeline
(this template + import_massing.py, then handing off to an interactive blender-mcp session).
"""
import bpy
import os
import sys
import math

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import massing_lib as ml  # noqa: E402


def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def setup_units():
    scene = bpy.context.scene
    scene.unit_settings.system = 'METRIC'
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = 'METERS'


def setup_collections():
    site = ml.get_or_create_collection("Site")
    for t in ml.VOLUME_TYPES:
        ml.get_or_create_collection(t)
    return site


def setup_ground_plane(site_coll):
    mesh = bpy.data.meshes.new("GroundPlane")
    size = 200.0
    obj = ml.make_box_mesh("GroundPlane", -size / 2, -size / 2, -0.05, size / 2, size / 2, 0.0)
    obj.data.name = "GroundPlane"
    mat = ml.build_ground_material()
    obj.data.materials.append(mat)
    site_coll.objects.link(obj)
    return obj


def setup_cameras(site_coll):
    cams = {}

    def add_cam(name, loc, rot_deg):
        cam_data = bpy.data.cameras.new(name)
        cam_obj = bpy.data.objects.new(name, cam_data)
        cam_obj.location = loc
        cam_obj.rotation_euler = tuple(math.radians(d) for d in rot_deg)
        site_coll.objects.link(cam_obj)
        cams[name] = cam_obj
        return cam_obj

    # Generic placeholder framing, aimed roughly at world origin — import_massing.py reframes
    # these to the real project bounding box once geometry exists.
    add_cam("Cam_StreetElevation", (0, -40, 1.7), (90, 0, 0))
    add_cam("Cam_Aerial34", (35, -35, 30), (60, 0, 45))
    add_cam("Cam_EyeLevel", (15, -20, 1.7), (85, 0, 30))

    bpy.context.scene.camera = cams["Cam_Aerial34"]
    return cams


def setup_render_settings():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.filepath = "//renders/"  # relative to wherever the project .blend is saved

    view_layer = bpy.context.view_layer
    view_layer.use_freestyle = True
    scene.render.use_freestyle = True
    # Line thickness kept modest; the property-line edge mark is what actually gets drawn —
    # import_massing.py marks that edge loop with `use_freestyle_mark = True` after the lot cut.
    scene.render.line_thickness = 1.0

    # Create the lineset + linestyle here (not left to import_massing.py) so the template is
    # already render-safe: an empty lineset slot with no linestyle attached crashes Freestyle's
    # line-style Python parameter editor at render time (AttributeError on NoneType.use_chaining).
    if not view_layer.freestyle_settings.linesets:
        lineset = view_layer.freestyle_settings.linesets.new("PropertyLine")
        lineset.select_by_edge_types = True
        lineset.edge_type_negation = 'INCLUSIVE'
        lineset.select_edge_mark = True
        lineset.linestyle = bpy.data.linestyles.new("PropertyLineStyle")
        lineset.linestyle.use_fake_user = True


def setup_sun_and_sky():
    ml.setup_world_nishita_sky()
    # Generic default angle until a project sets real lat/long via import_massing.py --latlong.
    ml.set_sun(elevation_deg=45.0, azimuth_deg=180.0)


def build_all_materials():
    ml.build_tier_a_materials()
    ml.build_tier_b_materials()


def main():
    reset_scene()
    setup_units()
    site_coll = setup_collections()
    setup_ground_plane(site_coll)
    setup_cameras(site_coll)
    setup_render_settings()
    setup_sun_and_sky()
    build_all_materials()

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_Massing-Template.blend")
    bpy.ops.wm.save_as_mainfile(filepath=out_path)
    print("TEMPLATE_SAVED:", out_path)
    print("MATERIALS:", len(bpy.data.materials))
    print("COLLECTIONS:", [c.name for c in bpy.data.collections])
    print("OBJECTS:", [o.name for o in bpy.data.objects])


if __name__ == "__main__":
    main()
