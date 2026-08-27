# Phase 2 — Site analysis and design

Output: `2_Site/Site-Strategy.md` — a facts table with design implications, a computed buildable envelope, and a site strategy where every move is traceable to a fact or driver.

## Facts before moves
Fill the site facts table first: context, zoning (setbacks, height, FAR, use, parking ratios), climate and solar orientation, access and servicing, topography, views, neighbours, easements/utilities. Every fact gets a **design implication** — a fact without an implication is trivia. Research what you can (zoning bylaws are usually online — search the municipality); ask the user for what you can't (survey, geotech).

## Required assessment battery
Every site assessment covers these, at concept grade, before the strategy is drafted. "No data available" is an acceptable answer; skipping the row is not.

- **Elevation & topography** — spot elevations, slope direction/grade (national DEM APIs give concept-grade; flag as too coarse for micro-grading).
- **Views** — what's seen from the parcel in each direction, and from a plausible upper level; distinguish views *earned* (there now) from *speculative* (need height or clearing). Tie to client motives.
- **Surrounding landscape context** — vegetation pattern on and around the lot, landform (escarpment, valley, flat), water bodies, ecological edges. What landscape can the site borrow?
- **Sun study** — sun path at winter solstice, equinox, summer solstice for the site latitude; shadows cast by neighbours, vegetation, and landform onto the buildable area; identify which parts of the envelope get winter sun. Compute, don't assume. **Always produce a sun-section diagram**: 1–2 section cuts through the critical obstruction(s) showing summer and winter noon rays at the computed angles, the shadow they cast, where winter sun crosses the wall plane, and the optimal-overhang ratio (depth = glass height / tan(summer noon alt)). Draw proportionally true; save to `diagrams/`, embed in the site doc.
- **Wind study (if data available)** — prevailing directions by season from the nearest climate-normals station; local modifiers (gaps, escarpments, channeling). Note the winter-wind × outdoor-space interaction explicitly.
- **Acoustic study** — inventory every noise source within earshot: roads (with traffic class), rail, flight paths, industry, sports fields/schoolyards, mechanical (lift stations, substations). Record distance, direction, and whether prevailing wind carries it to the site. Public noise maps are rare; a source inventory with distances is the concept-grade substitute.

## Broader context scan (two rings)
The parcel is not the site. Scan two rings and log what matters:

1. **Adjacent ring** — abutting parcels + across each street: what every edge actually touches, verified per the adjacency protocol (never from mid-scale satellite).
2. **Neighbourhood ring (~1–2 km)** — both sides of the ledger:
   - *Amenities:* parks and paths, transit access (stops, frequency), schools, shops/daily needs, recreation.
   - *Nuisances:* busy roads, train tracks, airports/flight paths, industry, stagnant water/wetlands (mosquito breeding), odour sources (lift stations, lagoons, feedlots), powerlines, nightlife.

Some entries are double-signed and only resolve against the client: an elementary school across the street is an amenity for a young family, a nuisance for a home-office writer; a wetland is habitat *and* a mosquito nursery — log both readings and resolve the sign against client motives, not in the abstract. Always add client-specific variables the checklist doesn't name (commute targets, gear, guests).

## Compute the envelope
Turn zoning into numbers: max footprint after setbacks, max height/storeys, max GFA from FAR. Compare against the brief's target GSF immediately — if the program doesn't fit the envelope, that's a phase-4-sized problem discovered early, and it goes straight to open questions and the user's attention.

## Strategy
Propose 2–3 site strategies (entry, orientation, massing zones, open space, servicing) as options, not one answer. Each move in the chosen strategy gets a row in the moves table: move → responds to (fact or driver) → rationale. Diagrams are the user's work in their tools; the file records the logic. Offer relevant lessons from phase 1.

## Gate questions worth asking
Which move dies if the zoning variance isn't granted? Where does servicing conflict with the "good" frontage? What does the site want that the brief doesn't ask for?
