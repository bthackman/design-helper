"""
import_massing.py — massing.json (from the Massing Studio's Export JSON button) -> a project
.blend, built on top of _Massing-Template.blend. Run headless:

    "C:\\Program Files\\Blender Foundation\\Blender 4.4\\blender.exe" --background --python import_massing.py -- \
        --json "path\\to\\project-massing.json" --out "path\\to\\Project-Massing.blend" \
        [--template "path\\to\\_Massing-Template.blend"] [--latlong "50.99,-114.0"] \
        [--date "2026-06-21"] [--hour-utc 19.6]

Everything after the lone `--` is this script's own argv; Blender ignores it.
See README.md for the full pipeline and the site.latLong schema gap this --latlong flag works around.
"""
import bpy
import bmesh
import json
import os
import sys
import math
import argparse
import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import massing_lib as ml  # noqa: E402


def parse_args():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    p = argparse.ArgumentParser()
    p.add_argument("--json", required=True)
    p.add_argument("--out", required=True)
    p.add_argument("--template", default=None)
    p.add_argument("--latlong", default=None, help="'lat,lon' in decimal degrees, e.g. '50.99,-114.0'")
    p.add_argument("--date", default=None, help="YYYY-MM-DD, defaults to today")
    p.add_argument("--hour-utc", type=float, default=None, help="defaults to solar noon for --date/--latlong")
    return p.parse_args(argv)


def load_template(template_path):
    bpy.ops.wm.open_mainfile(filepath=template_path)


def load_interchange(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if data.get("schema") != "massing-interchange/v1":
        print("WARNING: unexpected schema '{0}', proceeding anyway.".format(data.get("schema")))
    return data


def build_volumes(data):
    bounds = {"xmin": math.inf, "xmax": -math.inf, "ymin": math.inf, "ymax": -math.inf,
              "zmin": math.inf, "zmax": -math.inf}
    created = []
    for v in data.get("volumes", []):
        vtype = v.get("type")
        if vtype not in ml.VOLUME_TYPES:
            print("WARNING: unknown volume type '{0}' for id '{1}', skipping.".format(vtype, v.get("id")))
            continue
        x, z, w, d, h = float(v["x"]), float(v["z"]), float(v["w"]), float(v["d"]), float(v["h"])
        base = float(v.get("base", 0.0))

        # interchange x,z = one corner of the box in plan; box spans x..x+w, z..z+d.
        # Blender: +X = East (unchanged), +Y = North = -interchange_z (see massing_lib.interchange_xz_to_blender_xy).
        x_min, x_max = x, x + w
        y_min, y_max = -(z + d), -z
        z_min, z_max = base, base + h

        obj = ml.make_box_mesh("{0}_{1}".format(v.get("id", "vol"), vtype), x_min, y_min, z_min, x_max, y_max, z_max)
        mat_name = ml.TIER_A_PREFIX + vtype
        mat = bpy.data.materials.get(mat_name)
        if mat is not None:
            obj.data.materials.append(mat)
        coll = bpy.data.collections.get(vtype)
        (coll or bpy.context.scene.collection).objects.link(obj)
        created.append(obj)

        bounds["xmin"] = min(bounds["xmin"], x_min)
        bounds["xmax"] = max(bounds["xmax"], x_max)
        bounds["ymin"] = min(bounds["ymin"], y_min)
        bounds["ymax"] = max(bounds["ymax"], y_max)
        bounds["zmin"] = min(bounds["zmin"], z_min)
        bounds["zmax"] = max(bounds["zmax"], z_max)

        if v.get("clerestory"):
            print("NOTE: 'clerestory' flag on '{0}' is not modelled (metadata-only, matches Revit receiver's "
                  "treatment of glazing-as-metadata).".format(v.get("id")))

    return created, bounds


def build_lot_boundary(data, site_coll):
    """A separate, slightly-raised (1cm) flat ngon exactly matching site.lotPolygon, sharing the
    ground material, with its boundary edges marked for Freestyle. This reads as the property line
    living on the ground surface without the coplanar-boolean / knife-project instability that
    editing the single big GroundPlane mesh directly would risk in headless mode (see README)."""
    lot = data.get("site", {}).get("lotPolygon", [])
    if not lot:
        print("WARNING: no site.lotPolygon in massing.json, skipping lot boundary.")
        return None, None

    mesh = bpy.data.meshes.new("LotBoundary")
    bm = bmesh.new()
    verts = []
    for (lx, lz) in lot:
        bx, by = ml.interchange_xz_to_blender_xy(lx, lz)
        verts.append(bm.verts.new((bx, by, 0.01)))
    face = bm.faces.new(verts)
    bm.normal_update()
    for e in face.edges:
        e.seam = True  # visually distinguishable in the UV/edit-mode overlay too
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("LotBoundary", mesh)
    ground_mat = bpy.data.materials.get(ml.GROUND_MATERIAL_NAME)
    if ground_mat is not None:
        obj.data.materials.append(ground_mat)
    site_coll.objects.link(obj)

    # Freestyle marks live on the *object's* mesh edges via bpy.types.MeshEdge.use_freestyle_mark,
    # not via a bmesh custom layer name lookup as attempted above (kept simple + correct here).
    for e in obj.data.edges:
        e.use_freestyle_mark = True

    # Freestyle only renders marks that pass through a "Freestyle Edge Marks" line set — make sure
    # the active view layer's default line set is configured to select by edge mark.
    view_layer = bpy.context.view_layer
    if view_layer.freestyle_settings.linesets:
        lineset = view_layer.freestyle_settings.linesets[0]
    else:
        lineset = view_layer.freestyle_settings.linesets.new("PropertyLine")
    lineset.select_by_edge_types = True
    lineset.edge_type_negation = 'INCLUSIVE'
    lineset.select_edge_mark = True
    if lineset.linestyle is None:
        # Enabling use_freestyle on the view layer creates an empty lineset slot without a
        # linestyle attached (a Blender quirk when done via Python rather than the UI operator) —
        # renders with select_edge_mark=True but no linestyle crash Freestyle's own line-style
        # Python parameter editor at render time (AttributeError on NoneType.use_chaining).
        lineset.linestyle = bpy.data.linestyles.new("PropertyLineStyle")

    bx0, by0 = ml.interchange_xz_to_blender_xy(lot[0][0], lot[0][1])
    return obj, [ml.interchange_xz_to_blender_xy(p[0], p[1]) for p in lot]


def build_north_arrow(data, site_coll, lot_bounds_xy):
    north_deg = float(data.get("site", {}).get("northDeg", 0.0))
    empty = bpy.data.objects.new("NorthArrow", None)
    empty.empty_display_type = 'SINGLE_ARROW'
    empty.empty_display_size = 3.0
    if lot_bounds_xy:
        cx = sum(p[0] for p in lot_bounds_xy) / len(lot_bounds_xy)
        cy = sum(p[1] for p in lot_bounds_xy) / len(lot_bounds_xy)
        empty.location = (cx, cy, 0.05)
    # Baseline: interchange north = -z = Blender +Y, so an un-rotated arrow already points north
    # when northDeg == 0. ASSUMPTION (untested — every sample scheme so far has northDeg == 0):
    # northDeg rotates the arrow clockwise from that +Y baseline, matching the solar-azimuth
    # convention used elsewhere in this receiver. Verify against a real non-zero-northDeg project
    # before trusting the sign.
    empty.rotation_euler = (0.0, 0.0, math.radians(-north_deg))
    site_coll.objects.link(empty)
    return empty


def reframe_cameras(bounds):
    if bounds["xmin"] == math.inf:
        return
    cx = (bounds["xmin"] + bounds["xmax"]) / 2
    cy = (bounds["ymin"] + bounds["ymax"]) / 2
    cz = (bounds["zmin"] + bounds["zmax"]) / 2
    span = max(bounds["xmax"] - bounds["xmin"], bounds["ymax"] - bounds["ymin"], 8.0)

    def look_at(obj, target):
        direction = (target - obj.location)
        obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

    import mathutils
    target = mathutils.Vector((cx, cy, cz))

    street = bpy.data.objects.get("Cam_StreetElevation")
    if street:
        street.location = (cx, bounds["ymin"] - span * 1.2, 1.7)
        look_at(street, target)

    aerial = bpy.data.objects.get("Cam_Aerial34")
    if aerial:
        aerial.location = (bounds["xmax"] + span * 0.9, bounds["ymin"] - span * 0.9, cz + span * 0.9)
        look_at(aerial, target)

    eye = bpy.data.objects.get("Cam_EyeLevel")
    if eye:
        eye.location = (cx - span * 0.6, bounds["ymin"] - span * 0.4, 1.7)
        look_at(eye, target)


def resolve_sun(args, data):
    if not args.latlong:
        print("NOTE: no --latlong given (massing.json has no site.latLong field yet — see README). "
              "Sun left at the template's generic default (45deg elevation, due-south azimuth).")
        return
    lat_str, lon_str = args.latlong.split(",")
    lat, lon = float(lat_str), float(lon_str)

    if args.date:
        y, m, d = (int(x) for x in args.date.split("-"))
    else:
        today = datetime.date.today()
        y, m, d = today.year, today.month, today.day

    hour_utc = args.hour_utc if args.hour_utc is not None else ml.solar_noon_utc_hour(lon, y, m, d)
    elev, az = ml.solar_elevation_azimuth(lat, lon, y, m, d, hour_utc)
    ml.set_sun(elev, az)
    print("SUN SET: lat={0} lon={1} date={2}-{3:02d}-{4:02d} hour_utc={5:.2f} -> elevation={6:.2f} azimuth={7:.2f}"
          .format(lat, lon, y, m, d, hour_utc, elev, az))


def main():
    args = parse_args()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = args.template or os.path.join(script_dir, "_Massing-Template.blend")

    load_template(template_path)
    data = load_interchange(args.json)

    site_coll = bpy.data.collections.get("Site") or bpy.context.scene.collection
    volumes, bounds = build_volumes(data)
    lot_obj, lot_xy = build_lot_boundary(data, site_coll)
    build_north_arrow(data, site_coll, lot_xy)
    reframe_cameras(bounds)
    resolve_sun(args, data)

    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=args.out)

    print("PROJECT_SAVED:", args.out)
    print("VOLUME_COUNT:", len(volumes))
    print("BY_TYPE:", {t: len(bpy.data.collections[t].objects) for t in ml.VOLUME_TYPES if t in bpy.data.collections})
    print("LOT_BOUNDARY:", "yes" if lot_obj else "no")


if __name__ == "__main__":
    main()
