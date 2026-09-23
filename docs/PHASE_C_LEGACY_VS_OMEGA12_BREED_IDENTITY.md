# Phase C — Legacy vs Ω12 Breed Identity Comparison

Observe only. This report does not rank resolvers or recommend a migration.

## Environment / versions

- mapping_config_version: 1.0.0
- warehouse version: 5.0.0-biology
- comparison basis: canonical_id
- corpus counts: 81 inputs

## Corpus composition

- canonical: 48
- approved_alias: 5
- shared_token: 12
- unique_token: 3
- blank: 2
- mixed: 4
- intra_word_x: 1
- punctuation_boundary: 1
- unknown: 1
- normalization: 4

## Summary

Counts are tallies, not scores.

- SAME: 60
- AMBIGUOUS: 16
- UNRESOLVED: 5
- REGRESSION: 0

## Detailed results — disagreements

### Input: 'Cocker'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_A00AD6C7 canonical_name=American Cocker Spaniel resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_A00AD6C7 American Cocker Spaniel; BREED_5D7A8061 English Cocker Spaniel
- Rule: shared_name_token
- Related canonical names: American Cocker Spaniel, English Cocker Spaniel
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (American Cocker Spaniel). Candidates: American Cocker Spaniel, English Cocker Spaniel.

### Input: 'Collie'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_BC63A662 canonical_name=Border Collie resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_BC63A662 Border Collie; BREED_5A2BD646 Rough Collie
- Rule: shared_name_token
- Related canonical names: Border Collie, Rough Collie
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Border Collie). Candidates: Border Collie, Rough Collie.

### Input: 'Dachshund'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_3905DBDB canonical_name=Wirehaired Dachshund resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_3905DBDB Wirehaired Dachshund; BREED_1D54BB3A Smooth Dachshund; BREED_0EFE6C40 Longhaired Dachshund
- Rule: shared_name_token
- Related canonical names: Wirehaired Dachshund, Smooth Dachshund, Longhaired Dachshund
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Wirehaired Dachshund). Candidates: Wirehaired Dachshund, Smooth Dachshund, Longhaired Dachshund.

### Input: 'Dog'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_08E4F037 canonical_name=French Bulldog resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_2E91411B German Shepherd Dog; BREED_82C42678 Bernese Mountain Dog; BREED_EE6CB0D6 Chinese Rural Dog
- Rule: shared_name_token
- Related canonical names: German Shepherd Dog, Bernese Mountain Dog, Chinese Rural Dog
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (French Bulldog). Candidates: German Shepherd Dog, Bernese Mountain Dog, Chinese Rural Dog.

### Input: 'English'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_617BE9EB canonical_name=Old English Sheepdog resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_617BE9EB Old English Sheepdog; BREED_F0A0C6D9 English Springer Spaniel; BREED_5D7A8061 English Cocker Spaniel
- Rule: shared_name_token
- Related canonical names: Old English Sheepdog, English Springer Spaniel, English Cocker Spaniel
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Old English Sheepdog). Candidates: Old English Sheepdog, English Springer Spaniel, English Cocker Spaniel.

### Input: 'Hound'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_3E1561D4 canonical_name=Afghan Hound resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_3E1561D4 Afghan Hound; BREED_C87E70CA Basset Hound
- Rule: shared_name_token
- Related canonical names: Afghan Hound, Basset Hound
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Afghan Hound). Candidates: Afghan Hound, Basset Hound.

### Input: 'Inu'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_3A7AB996 canonical_name=Shiba Inu resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_3A7AB996 Shiba Inu; BREED_4E0A4CB0 Akita Inu
- Rule: shared_name_token
- Related canonical names: Shiba Inu, Akita Inu
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Shiba Inu). Candidates: Shiba Inu, Akita Inu.

### Input: 'Pinscher'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_2641DA99 canonical_name=Miniature Pinscher resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_2641DA99 Miniature Pinscher; BREED_C687F403 Doberman Pinscher
- Rule: shared_name_token
- Related canonical names: Miniature Pinscher, Doberman Pinscher
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Miniature Pinscher). Candidates: Miniature Pinscher, Doberman Pinscher.

### Input: 'Retriever'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_4C2466ED canonical_name=Golden Retriever resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_4C2466ED Golden Retriever; BREED_B02F1BE9 Labrador Retriever
- Rule: shared_name_token
- Related canonical names: Golden Retriever, Labrador Retriever
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Golden Retriever). Candidates: Golden Retriever, Labrador Retriever.

### Input: 'Sheepdog'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_617BE9EB canonical_name=Old English Sheepdog resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_617BE9EB Old English Sheepdog; BREED_571535AE Shetland Sheepdog
- Rule: shared_name_token
- Related canonical names: Old English Sheepdog, Shetland Sheepdog
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Old English Sheepdog). Candidates: Old English Sheepdog, Shetland Sheepdog.

### Input: 'Spaniel'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_10A53062 canonical_name=Cavalier King Charles Spaniel resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_10A53062 Cavalier King Charles Spaniel; BREED_A00AD6C7 American Cocker Spaniel; BREED_F0A0C6D9 English Springer Spaniel; BREED_5D7A8061 English Cocker Spaniel
- Rule: shared_name_token
- Related canonical names: Cavalier King Charles Spaniel, American Cocker Spaniel, English Springer Spaniel, English Cocker Spaniel
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Cavalier King Charles Spaniel). Candidates: Cavalier King Charles Spaniel, American Cocker Spaniel, English Springer Spaniel, English Cocker Spaniel.

### Input: 'Terrier'

- Category: shared_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_6DB4AA40 canonical_name=Boston Terrier resolved_count=1
- Ω12: status=AMBIGUOUS canonical_id=None canonical_name=None rule=shared_name_token
- Classification: AMBIGUOUS
- Candidates: BREED_6DB4AA40 Boston Terrier; BREED_43DD399E Bedlington Terrier; BREED_1B953788 Jack Russell Terrier; BREED_074A355B Kerry Blue Terrier; BREED_AB5D5A28 Bull Terrier; BREED_46D833A4 West Highland White Terrier; BREED_D8797FDC Yorkshire Terrier
- Rule: shared_name_token
- Related canonical names: Boston Terrier, Bedlington Terrier, Jack Russell Terrier, Kerry Blue Terrier, Bull Terrier, West Highland White Terrier, Yorkshire Terrier
- Notes: Ω12 identified multiple canonical candidates and selected none; legacy returned a single result (Boston Terrier). Candidates: Boston Terrier, Bedlington Terrier, Jack Russell Terrier, Kerry Blue Terrier, Bull Terrier, West Highland White Terrier, Yorkshire Terrier.

### Input: 'Corgi'

- Category: unique_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_6CBDD78C canonical_name=Pembroke Welsh Corgi resolved_count=1
- Ω12: status=UNRESOLVED canonical_id=None canonical_name=None rule=no_approved_mapping
- Classification: UNRESOLVED
- Candidates: (none)
- Rule: no_approved_mapping
- Related canonical names: Pembroke Welsh Corgi
- Notes: Ω12 did not establish an identity; legacy returned Pembroke Welsh Corgi.

### Input: 'Husky'

- Category: unique_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_D7352671 canonical_name=Siberian Husky resolved_count=1
- Ω12: status=UNRESOLVED canonical_id=None canonical_name=None rule=no_approved_mapping
- Classification: UNRESOLVED
- Candidates: (none)
- Rule: no_approved_mapping
- Related canonical names: Siberian Husky
- Notes: Ω12 did not establish an identity; legacy returned Siberian Husky.

### Input: 'Bulldog'

- Category: unique_token
- Source: derived_from_warehouse_identity
- Legacy: selected=yes canonical_id=BREED_08E4F037 canonical_name=French Bulldog resolved_count=1
- Ω12: status=UNRESOLVED canonical_id=None canonical_name=None rule=no_approved_mapping
- Classification: UNRESOLVED
- Candidates: (none)
- Rule: no_approved_mapping
- Related canonical names: French Bulldog
- Notes: Ω12 did not establish an identity; legacy returned French Bulldog.

### Input: ''

- Category: blank
- Source: boundary_input
- Legacy: selected=yes canonical_id=BREED_23ECEA52 canonical_name=Beagle resolved_count=1
- Ω12: status=UNRESOLVED canonical_id=None canonical_name=None rule=blank_or_missing
- Classification: UNRESOLVED
- Candidates: (none)
- Rule: blank_or_missing
- Related canonical names: (none)
- Notes: Ω12 did not establish an identity; legacy returned Beagle.

### Input: '   '

- Category: blank
- Source: boundary_input
- Legacy: selected=yes canonical_id=BREED_23ECEA52 canonical_name=Beagle resolved_count=1
- Ω12: status=UNRESOLVED canonical_id=None canonical_name=None rule=blank_or_missing
- Classification: UNRESOLVED
- Candidates: (none)
- Rule: blank_or_missing
- Related canonical names: (none)
- Notes: Ω12 did not establish an identity; legacy returned Beagle.

### Input: 'Lab x Golden'

- Category: mixed
- Source: derived_from_omega12_mapping
- Legacy: selected=no
- Ω12: status=MIXED canonical_id=None canonical_name=None rule=mixed_breed_separator
- Classification: AMBIGUOUS
- Candidates: (none)
- Rule: mixed_breed_separator
- Related canonical names: Labrador Retriever, Golden Retriever
- Notes: Ω12 status is MIXED with 2 components in expression order; legacy treated the input as a single matcher string and selected none.

- Components:
  - RESOLVED BREED_B02F1BE9 Labrador Retriever rule=explicit_alias
  - RESOLVED BREED_4C2466ED Golden Retriever rule=explicit_alias

### Input: 'Lab × Golden'

- Category: mixed
- Source: derived_from_omega12_mapping
- Legacy: selected=no
- Ω12: status=MIXED canonical_id=None canonical_name=None rule=mixed_breed_separator
- Classification: AMBIGUOUS
- Candidates: (none)
- Rule: mixed_breed_separator
- Related canonical names: Labrador Retriever, Golden Retriever
- Notes: Ω12 status is MIXED with 2 components in expression order; legacy treated the input as a single matcher string and selected none.

- Components:
  - RESOLVED BREED_B02F1BE9 Labrador Retriever rule=explicit_alias
  - RESOLVED BREED_4C2466ED Golden Retriever rule=explicit_alias

### Input: 'Lab / Golden'

- Category: mixed
- Source: derived_from_omega12_mapping
- Legacy: selected=no
- Ω12: status=MIXED canonical_id=None canonical_name=None rule=mixed_breed_separator
- Classification: AMBIGUOUS
- Candidates: (none)
- Rule: mixed_breed_separator
- Related canonical names: Labrador Retriever, Golden Retriever
- Notes: Ω12 status is MIXED with 2 components in expression order; legacy treated the input as a single matcher string and selected none.

- Components:
  - RESOLVED BREED_B02F1BE9 Labrador Retriever rule=explicit_alias
  - RESOLVED BREED_4C2466ED Golden Retriever rule=explicit_alias

### Input: 'Beagle x French Bulldog'

- Category: mixed
- Source: derived_from_warehouse_identity
- Legacy: selected=no
- Ω12: status=MIXED canonical_id=None canonical_name=None rule=mixed_breed_separator
- Classification: AMBIGUOUS
- Candidates: (none)
- Rule: mixed_breed_separator
- Related canonical names: Beagle, French Bulldog
- Notes: Ω12 status is MIXED with 2 components in expression order; legacy treated the input as a single matcher string and selected none.

- Components:
  - RESOLVED BREED_23ECEA52 Beagle rule=exact_canonical_name
  - RESOLVED BREED_08E4F037 French Bulldog rule=exact_canonical_name


## SAME cases (compact)

- 'Beagle' [canonical] → BREED_23ECEA52 Beagle
- 'French Bulldog' [canonical] → BREED_08E4F037 French Bulldog
- 'German Shepherd Dog' [canonical] → BREED_2E91411B German Shepherd Dog
- 'Golden Retriever' [canonical] → BREED_4C2466ED Golden Retriever
- 'Labrador Retriever' [canonical] → BREED_B02F1BE9 Labrador Retriever
- 'Miniature Pinscher' [canonical] → BREED_2641DA99 Miniature Pinscher
- 'Pembroke Welsh Corgi' [canonical] → BREED_6CBDD78C Pembroke Welsh Corgi
- 'Pug' [canonical] → BREED_06F902AB Pug
- 'Siberian Husky' [canonical] → BREED_D7352671 Siberian Husky
- 'Alaskan Malamute' [canonical] → BREED_DAB74007 Alaskan Malamute
- 'Afghan Hound' [canonical] → BREED_3E1561D4 Afghan Hound
- 'Border Collie' [canonical] → BREED_BC63A662 Border Collie
- 'Bernese Mountain Dog' [canonical] → BREED_82C42678 Bernese Mountain Dog
- 'Pomeranian' [canonical] → BREED_CB646D54 Pomeranian
- 'Pekingese' [canonical] → BREED_A4B7D238 Pekingese
- 'Boston Terrier' [canonical] → BREED_6DB4AA40 Boston Terrier
- 'Basset Hound' [canonical] → BREED_C87E70CA Basset Hound
- 'Bichon Frise' [canonical] → BREED_14624D63 Bichon Frise
- 'Bedlington Terrier' [canonical] → BREED_43DD399E Bedlington Terrier
- 'Shiba Inu' [canonical] → BREED_3A7AB996 Shiba Inu
- 'Cavalier King Charles Spaniel' [canonical] → BREED_10A53062 Cavalier King Charles Spaniel
- 'Great Pyrenees' [canonical] → BREED_58CB38F4 Great Pyrenees
- 'Doberman Pinscher' [canonical] → BREED_C687F403 Doberman Pinscher
- 'Dalmatian' [canonical] → BREED_F06D13A1 Dalmatian
- 'Old English Sheepdog' [canonical] → BREED_617BE9EB Old English Sheepdog
- 'Wirehaired Dachshund' [canonical] → BREED_3905DBDB Wirehaired Dachshund
- 'Poodle' [canonical] → BREED_9FC60FFF Poodle
- 'Chihuahua' [canonical] → BREED_4D52D378 Chihuahua
- 'Jack Russell Terrier' [canonical] → BREED_1B953788 Jack Russell Terrier
- 'Kerry Blue Terrier' [canonical] → BREED_074A355B Kerry Blue Terrier
- 'Foxhound' [canonical] → BREED_6C4486EF Foxhound
- 'Greyhound' [canonical] → BREED_889A3EBF Greyhound
- 'Smooth Dachshund' [canonical] → BREED_1D54BB3A Smooth Dachshund
- 'American Cocker Spaniel' [canonical] → BREED_A00AD6C7 American Cocker Spaniel
- 'Maltese' [canonical] → BREED_40006713 Maltese
- 'Bull Terrier' [canonical] → BREED_AB5D5A28 Bull Terrier
- 'Akita Inu' [canonical] → BREED_4E0A4CB0 Akita Inu
- 'Samoyed' [canonical] → BREED_5B3AA685 Samoyed
- 'Rough Collie' [canonical] → BREED_5A2BD646 Rough Collie
- 'Chow Chow' [canonical] → BREED_0AFC0521 Chow Chow
- 'English Springer Spaniel' [canonical] → BREED_F0A0C6D9 English Springer Spaniel
- 'Chinese Rural Dog' [canonical] → BREED_EE6CB0D6 Chinese Rural Dog
- 'West Highland White Terrier' [canonical] → BREED_46D833A4 West Highland White Terrier
- 'Shetland Sheepdog' [canonical] → BREED_571535AE Shetland Sheepdog
- 'Shih Tzu' [canonical] → BREED_50042913 Shih Tzu
- 'English Cocker Spaniel' [canonical] → BREED_5D7A8061 English Cocker Spaniel
- 'Yorkshire Terrier' [canonical] → BREED_D8797FDC Yorkshire Terrier
- 'Longhaired Dachshund' [canonical] → BREED_0EFE6C40 Longhaired Dachshund
- 'Lab' [approved_alias] → BREED_B02F1BE9 Labrador Retriever
- 'Labrador' [approved_alias] → BREED_B02F1BE9 Labrador Retriever
- 'Golden' [approved_alias] → BREED_4C2466ED Golden Retriever
- 'German Shepherd' [approved_alias] → BREED_2E91411B German Shepherd Dog
- 'GSD' [approved_alias] → BREED_2E91411B German Shepherd Dog
- 'Foxhound' [intra_word_x] → BREED_6C4486EF Foxhound
- 'French-Bulldog' [punctuation_boundary] → (no identity)
- '__unknown_breed_phase_c__' [unknown] → (no identity)
- '  Beagle  ' [normalization] → BREED_23ECEA52 Beagle
- 'beagle' [normalization] → BREED_23ECEA52 Beagle
- 'BEAGLE' [normalization] → BREED_23ECEA52 Beagle
- '  Lab  ' [normalization] → BREED_B02F1BE9 Labrador Retriever
