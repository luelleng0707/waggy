# Science Validation Report

Generated: `2026-07-20T21:57:38.971649+00:00`
Status: **PASS**

- Errors: 0
- Warnings: 10

## Errors

_None_

## Warnings

- 3 conditions lack supported_by paper edges
- 7 evidence rows missing DOI
- 5 products missing composition rows
- 5 isolated graph nodes
- Circular reference involving trait:size:large -> condition:hip_dysplasia
- Circular reference involving breed:labrador_retriever -> trait:body_type:athletic
- Circular reference involving breed:golden_retriever -> trait:body_type:athletic
- Circular reference involving breed:golden_retriever -> trait:coat_type:double_coat
- Circular reference involving trait:skull_type:mesocephalic -> condition:hip_dysplasia
- 3 conditions missing outbound evidence paths

## Sections

### evidence

- `missing_doi`: 7
- `invalid_year`: 0
- `unsupported_study_type`: 0
- `duplicate_quotes`: 0
- `duplicate_paper_ids_in_table`: 0

### biology

- `invalid_breeds`: 0
- `missing_prevalence`: 0
- `impossible_prevalence`: 0
- `breed_count`: 48

### ingredients

- `negative_dose`: 0
- `max_lt_min`: 0
- `missing_mechanisms`: 0
- `invalid_bioavailability`: 0

### products

- `missing_ingredients`: 0
- `impossible_serving`: 0
- `missing_composition`: 5
- `product_count`: 16

### graph

- `isolated_nodes`: 5
- `circular_references`: 43
- `duplicate_edges`: 0
- `conditions_missing_paths`: 3
- `node_count`: 353
- `edge_count`: 791

