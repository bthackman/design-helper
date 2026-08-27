# massing_to_revit.py  —  Dynamo Python Script node
# Revit MVP receiver for the Massing Studio.
# Reads a "massing-interchange/v1" JSON (from the Studio's Export JSON button) and builds:
#   1. Levels from site.storeys
#   2. one MassBox family instance per volume (conceptual mass), on the right level
#   3. Mass Floors at each level a mass passes through  -> native GFA schedule
#
# Compatible with IronPython 2.7 (Revit 2020-2022) AND CPython3 (Revit 2023+).
#   - no f-strings (IronPython 2.7 doesn't support them) -> uses .format()
#   - metres->feet done by hand (no version-specific UnitUtils call)
#
# Dynamo node ports (right-click node -> add inputs to match):
#   IN[0]  jsonPath     : full path to the exported massing json (string)
#   IN[1]  familyName   : mass family type name, default "MassBox" (string)
#   IN[2]  run          : Boolean toggle so the graph only writes when you flip it True
# OUT     : a text log of what was created / skipped

import clr
import json
import os

clr.AddReference('RevitAPI')
clr.AddReference('RevitServices')
from Autodesk.Revit.DB import (
    FilteredElementCollector, Level, XYZ, FamilySymbol,
    Structure, MassInstanceUtils
)
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

doc = DocumentManager.Instance.CurrentDBDocument

# ---------- inputs ----------
jsonPath   = IN[0]
familyName = IN[1] if (len(IN) > 1 and IN[1]) else "MassBox"
run        = IN[2] if (len(IN) > 2) else True

FT = 0.3048                      # 1 foot = 0.3048 m
def m2ft(v): return float(v) / FT

log = []
def note(msg): log.append(msg)

if not run:
    OUT = "run = False. Flip the Boolean to True to write to the model."
else:
    # ---------- read interchange ----------
    if not jsonPath or not os.path.isfile(jsonPath):
        OUT = "ERROR: jsonPath not found: {0}".format(jsonPath)
    else:
        f = open(jsonPath, 'r')
        data = json.load(f)
        f.close()

        volumes = data.get("volumes", [])
        storeys = data.get("site", {}).get("storeys", [])
        note("Loaded {0} ({1}), {2} volumes.".format(
            data.get("project", "?"), data.get("schemeName", data.get("scheme", "?")), len(volumes)))

        # ---------- find the mass family symbol ----------
        symbol = None
        for fs in FilteredElementCollector(doc).OfClass(FamilySymbol):
            try:
                if fs.Family.Name == familyName:
                    symbol = fs
                    break
            except:
                pass

        if symbol is None:
            OUT = ("ERROR: family '{0}' not loaded. Build/load MassBox.rfa first "
                   "(see 00_MassBox-family-recipe.md), then re-run.").format(familyName)
        else:
            TransactionManager.Instance.EnsureInTransaction(doc)

            if not symbol.IsActive:
                symbol.Activate()
                doc.Regenerate()

            # ---------- levels from storeys (create if missing) ----------
            def get_or_create_level(elev_ft, name):
                for lv in FilteredElementCollector(doc).OfClass(Level):
                    if abs(lv.Elevation - elev_ft) < 1e-6:
                        return lv
                lv = Level.Create(doc, elev_ft)
                try:
                    lv.Name = name
                except:
                    pass
                return lv

            levels = []   # (elev_ft, Level)
            if storeys:
                for s in storeys:
                    e_ft = m2ft(s.get("elev", 0))
                    lv = get_or_create_level(e_ft, s.get("name", "L"))
                    levels.append((e_ft, lv))
            else:
                levels.append((0.0, get_or_create_level(0.0, "L1")))
            note("Levels ready: {0}".format(", ".join(
                ["{0}@{1:.2f}m".format(l[1].Name, l[0]*FT) for l in levels])))

            # ---------- helpers ----------
            def set_p(inst, name, val):
                p = inst.LookupParameter(name)
                if p is not None and not p.IsReadOnly:
                    try:
                        p.Set(val)
                        return True
                    except:
                        return False
                return False

            made = 0
            for v in volumes:
                w  = float(v["w"]); d = float(v["d"]); h = float(v["h"])
                x  = float(v["x"]); z = float(v["z"]); base = float(v.get("base", 0))
                # axis map: interchange x=East -> Revit +X ; z=South -> Revit -Y ; y=up -> +Z
                px = m2ft(x + w / 2.0)
                py = m2ft(-(z + d / 2.0))
                pz = m2ft(base)
                pt = XYZ(px, py, pz)

                inst = doc.Create.NewFamilyInstance(pt, symbol, Structure.StructuralType.NonStructural)

                # dimensions (family params drive extents; see recipe for names)
                set_p(inst, "Length", m2ft(w))     # X / East extent
                set_p(inst, "Width",  m2ft(d))     # Y / North extent
                set_p(inst, "Height", m2ft(h))     # Z / up
                # metadata
                set_p(inst, "Glazing_%", float(v.get("glaz", 0)))
                mk = inst.LookupParameter("Mark")
                if mk is not None and not mk.IsReadOnly:
                    try: mk.Set(str(v.get("id", "")))
                    except: pass
                cm = inst.LookupParameter("Comments")
                if cm is not None and not cm.IsReadOnly:
                    try: cm.Set("{0} | glaz {1}%".format(v.get("type", ""), v.get("glaz", 0)))
                    except: pass

                # ---------- mass floors at every level the mass spans ----------
                top = base + h
                for (e_ft, lv) in levels:
                    e_m = e_ft * FT
                    if (e_m >= base - 1e-4) and (e_m < top - 1e-4):
                        try:
                            MassInstanceUtils.AddMassLevelDataToMassInstance(doc, inst.Id, lv.Id)
                        except Exception as ex:
                            note("  mass-floor skip on {0}@{1}: {2}".format(v.get("id"), lv.Name, ex))
                made += 1

            TransactionManager.Instance.ForceCloseTransaction()
            note("Created {0} mass instances of '{1}'.".format(made, familyName))
            note("Add a 'Mass Floors (Gross Area)' schedule to read GFA natively; "
                 "cross-check against interchange metrics.dwelling = {0} m2.".format(
                     data.get("metrics", {}).get("dwelling", "?")))
            OUT = "\n".join(log)
