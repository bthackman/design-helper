Cairn Youth Centre (RAIC 400): site CAD set, generated 2026-10-05 by 2_Site/data/site_dxf.py

UNITS: metres.  COORDINATES: local, origin (0,0) at each site's anchor; both DXFs of a site share it.
REAL POSITION: NAD83 / Alberta 3TM ref. merid. 114 W (EPSG:3776). Origin coordinates below and on layer Z-ORIGIN.
ELEVATIONS (topo): true heights in metres, NRCan HRDEM 1 m DTM, 2020 LiDAR, CGVD2013 datum.

FILES PER SITE
  *_site-plan.dxf        flat 2D base: all linework layers (contours flattened, for reference)
  *_topo.dxf             600 m square centred on the site parcel(s): 1 m / 5 m contours as 3D polylines at true elevation
                         TOPO-EXTENT and TOPO-REF-SITE are 2D reference only: leave them out when building the Toposolid
  *_topo-points-5m.csv   x,y,z every 5 m (local metres), raw DTM; backup for Revit 'Toposolid from points' on flat ground

SOURCES: City of Calgary Open Data (assessment parcels, street centrelines, buildings, hydrology, regulatory flood map,
tree canopy 2022, Impervious Surface 2021, Tracks - Non-LRT); NRCan HRDEM. Parcels are assessment parcels, not survey lines.
The 50 m water setback is a design assumption drawn from all mapped water. Contours lightly smoothed (sigma 1.5 m).
Layers SITE-DRIVEWAY and SITE-ROAD-CL are switched off. $LTSCALE = 2.

Glenmore Landing (B): origin E -6819.70  N 5648879.79; frame (-550, 550, -500, 950) m from origin; topo centre (29, 115) m from origin, 1066.9-1082.0 m; 51 minor + 10 major contours; 14641 points
Inglewood (A): origin E -743.53  N 5654935.56; frame (-400, 800, -650, 500) m from origin; topo centre (58, -117) m from origin, 1029.8-1040.1 m; 74 minor + 28 major contours; 14641 points
