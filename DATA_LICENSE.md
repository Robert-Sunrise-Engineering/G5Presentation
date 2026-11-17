# Data License and Attribution

This file covers the parcel data in this repository — the File Geodatabase at
`demo/GDBs/iron_county_parcels.gdb` and any data derived from it. It does **not**
cover the source code, which is licensed separately under the MIT License
(see `LICENSE`).

## Source

| | |
|---|---|
| Dataset | Utah Iron County Parcels LIR |
| Publisher | Utah Geospatial Resource Center (UGRC), formerly AGRC |
| ArcGIS item | `555d3282b06d44a1a1a2fb7571e200a1` |
| Item page | https://www.arcgis.com/home/item.html?id=555d3282b06d44a1a1a2fb7571e200a1 |
| Feature service | https://services1.arcgis.com/99lidPhWCzftIe9K/ArcGIS/rest/services/Parcels_Iron_LIR/FeatureServer/0 |
| Original data source | Iron County, Utah |
| Access date | 2026-11-17 |
| Data vintage in this extract | `CURRENT_ASOF` = 2024-07-18 |
| Service metadata last data edit | 2026-03-06 (as observed 2026-11-17) |

"LIR" refers to the statewide Land Information Records parcel program
coordinated by UGRC with Utah county assessors and recorders.

## License

**Creative Commons Attribution 4.0 International (CC BY 4.0)**
https://creativecommons.org/licenses/by/4.0/

The license is declared in the ArcGIS item's `licenseInfo` field.

## Required attribution

UGRC asks for credit to UGRC and the SGID, a link to the license, and a note of
any changes made. A suitable attribution line is:

> Data: Utah Iron County Parcels LIR, Utah Geospatial Resource Center (UGRC) /
> SGID, CC BY 4.0. Source data: Iron County, Utah. Accessed 2026-11-17.

For maps and slides, the short form is sufficient:

> Data: UGRC / SGID, Utah Iron County Parcels LIR, CC BY 4.0.

Citations should include the data's last-updated date, or the access date where
that is unavailable.

## Changes to the data

The geodatabase is the unmodified extract downloaded on 2026-11-17. The scripts
in `analysis/` read the data but do not modify it.

If you subset, edit, or otherwise derive data from this extract, record the
change here. CC BY 4.0 and UGRC's policy require indicating that changes were
made.

## Disclaimer

The following is the disclaimer published with the source item, reproduced
without modification:

> The data, including but not limited to geographic data, tabular data, and
> analytical data, are provided "as is" and "as available", with no guarantees
> relating to the availability, completeness, or accuracy of data, and without
> any express or implied warranties. These data are provided as a public
> service for informational purposes only. You are solely responsible for
> obtaining the proper evaluation of a location and associated data by a
> qualified professional. UGRC reserves the right to change, revise, suspend or
> discontinue published data and services without notice at any time. Neither
> UGRC nor the State of Utah are responsible for any misuse or misrepresentation
> of the data. UGRC and the State of Utah are not obligated to provide you with
> any maintenance or support. The user assumes the entire risk as to the quality
> and performance of the data. You agree to hold the State of Utah harmless for
> any claims, liability, costs, and damages relating to your use of the data.
> You agree that your sole remedy for any dissatisfaction or claims is to
> discontinue use of the data.

UGRC's policy asks that republished UGRC data include this disclaimer in
unmodified form.

## Additional county notice

Iron County's own parcel viewer carries additional disclaimers, including that
the data are not to be used for navigation, as a legal document, for property
descriptions, or for determination of legal title, and are not a substitute for
survey or deed information. See the Iron County UPD Map item:
https://www.arcgis.com/home/item.html?id=734b0996af674f828036751756abf514

This is a disclaimer from the county's mapping application, not a separate data
license. It is noted here because the parcel records originate with Iron County.

## Policy reference

UGRC data license and disclaimer policy:
https://gis.utah.gov/documentation/policy/license/

UGRC SGID parcels page:
https://gis.utah.gov/products/sgid/cadastre/parcels/
