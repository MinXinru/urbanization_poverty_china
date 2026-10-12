# Province boundaries

Map shapefiles are omitted from this pack (placeholder folder).

To regenerate Supplementary Figures S1–S5 and S9–S10, place a province polygon shapefile here:

```
_shared/province_boundaries/china_provinces.shp
(+ sidecars: .shx .dbf .prj …)
```

Attribute field 0 should be the Chinese province name (mapped via `../province_names.py`). Plot scripts keep these relative path strings; they raise `FileNotFoundError` until you supply the file.
