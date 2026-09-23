# Phase D — Breed Identity Semantic Review

## Scope

Phase A+B established the Ω12 breed identity provider and `resolve_breed()` facade.
Phase C observed disagreements between legacy BreedNode matching and Ω12.
Phase D records the human/domain/product decisions still required.

This artifact does not decide breed meaning. Cursor is not the reviewer.
No aliases were added. No resolver rules changed. No Core consumer migrated.
No API or B2C UI changed.

- mapping_config_version: 1.0.0
- warehouse version: 5.0.0-biology
- review cases: 21
- REQUIRES_HUMAN_DECISION: 21
- ACCEPT_OMEGA12_SEMANTICS: 0
- RETAIN_LEGACY_SEMANTICS: 0
- ADD_APPROVED_KNOWLEDGE: 0
- DEFER: 0

Review groups are organizational only. They are not a priority ranking.

## Evidence rules

- EXISTING_RUNTIME_BEHAVIOR: what BreedNode or Ω12 currently returns.
- EXISTING_TEST_CONTRACT: a test currently asserts that current behavior.
  A capture test is not a product-meaning contract.
- EXISTING_APPROVED_MAPPING: an alias already present in `breed_aliases.csv`.
- EXISTING_WAREHOUSE_IDENTITY: a canonical row in `warehouse/biology/breeds.csv`.
- NO_EXPLICIT_CONTRACT: the repository does not establish intended identity meaning.

Legacy selected X is runtime behavior. It is not automatically Waggy's intended identity.
Ω12 AMBIGUOUS/UNRESOLVED/MIXED is current resolver behavior. It is not automatically
final product policy, and it does not by itself require a B2C clarification prompt.

## Review matrix

| Case | Input | Category | Legacy | Ω12 | Evidence | Decision |
|------|-------|----------|--------|-----|----------|----------|
| D-01 | 'Cocker' | shared_token | BREED_A00AD6C7 American Cocker Spaniel | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-02 | 'Collie' | shared_token | BREED_BC63A662 Border Collie | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-03 | 'Dachshund' | shared_token | BREED_3905DBDB Wirehaired Dachshund | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-04 | 'Dog' | shared_token | BREED_08E4F037 French Bulldog | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-05 | 'English' | shared_token | BREED_617BE9EB Old English Sheepdog | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-06 | 'Hound' | shared_token | BREED_3E1561D4 Afghan Hound | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-07 | 'Inu' | shared_token | BREED_3A7AB996 Shiba Inu | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-08 | 'Pinscher' | shared_token | BREED_2641DA99 Miniature Pinscher | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-09 | 'Retriever' | shared_token | BREED_4C2466ED Golden Retriever | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-10 | 'Sheepdog' | shared_token | BREED_617BE9EB Old English Sheepdog | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-11 | 'Spaniel' | shared_token | BREED_10A53062 Cavalier King Charles Spaniel | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-12 | 'Terrier' | shared_token | BREED_6DB4AA40 Boston Terrier | status=AMBIGUOUS canonical_id=None rule=shared_name_token | EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-13 | 'Corgi' | unique_token | BREED_6CBDD78C Pembroke Welsh Corgi | status=UNRESOLVED canonical_id=None rule=no_approved_mapping | EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-14 | 'Husky' | unique_token | BREED_D7352671 Siberian Husky | status=UNRESOLVED canonical_id=None rule=no_approved_mapping | EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-15 | 'Bulldog' | unique_token | BREED_08E4F037 French Bulldog | status=UNRESOLVED canonical_id=None rule=no_approved_mapping | EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-16 | '' | blank | BREED_23ECEA52 Beagle | status=UNRESOLVED canonical_id=None rule=blank_or_missing | EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-17 | '   ' | blank | BREED_23ECEA52 Beagle | status=UNRESOLVED canonical_id=None rule=blank_or_missing | EXISTING_RUNTIME_BEHAVIOR, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-18 | 'Lab x Golden' | mixed | selected=no | status=MIXED canonical_id=None rule=mixed_breed_separator | EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_APPROVED_MAPPING, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-19 | 'Lab × Golden' | mixed | selected=no | status=MIXED canonical_id=None rule=mixed_breed_separator | EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_APPROVED_MAPPING, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-20 | 'Lab / Golden' | mixed | selected=no | status=MIXED canonical_id=None rule=mixed_breed_separator | EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_APPROVED_MAPPING, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |
| D-21 | 'Beagle x French Bulldog' | mixed | selected=no | status=MIXED canonical_id=None rule=mixed_breed_separator | EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT | REQUIRES_HUMAN_DECISION |

## Review cases

### GROUP_A_SHARED_TOKEN

#### D-01 — 'Cocker'

- Category: shared_token
- Legacy result: BREED_A00AD6C7 American Cocker Spaniel
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_A00AD6C7 American Cocker Spaniel; BREED_5D7A8061 English Cocker Spaniel
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected American Cocker Spaniel. Ω12 status is AMBIGUOUS with 2 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Cocker' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (American Cocker Spaniel, English Cocker Spaniel)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-02 — 'Collie'

- Category: shared_token
- Legacy result: BREED_BC63A662 Border Collie
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_BC63A662 Border Collie; BREED_5A2BD646 Rough Collie
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected Border Collie. Ω12 status is AMBIGUOUS with 2 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Collie' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Border Collie, Rough Collie)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-03 — 'Dachshund'

- Category: shared_token
- Legacy result: BREED_3905DBDB Wirehaired Dachshund
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_3905DBDB Wirehaired Dachshund; BREED_1D54BB3A Smooth Dachshund; BREED_0EFE6C40 Longhaired Dachshund
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected Wirehaired Dachshund. Ω12 status is AMBIGUOUS with 3 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Dachshund' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Wirehaired Dachshund, Smooth Dachshund, Longhaired Dachshund)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-04 — 'Dog'

- Category: shared_token
- Legacy result: BREED_08E4F037 French Bulldog
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_2E91411B German Shepherd Dog; BREED_82C42678 Bernese Mountain Dog; BREED_EE6CB0D6 Chinese Rural Dog
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected French Bulldog. Ω12 status is AMBIGUOUS with 3 candidates and selected none. Ω12 rule is shared_name_token. Legacy selected French Bulldog, which is not in the Ω12 candidate set.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Dog' remain identity-ambiguous across the Ω12 candidates (German Shepherd Dog, Bernese Mountain Dog, Chinese Rural Dog), remain unresolved, or resolve to a single canonical breed? Legacy currently selects French Bulldog, which is not in the Ω12 candidate set.
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-05 — 'English'

- Category: shared_token
- Legacy result: BREED_617BE9EB Old English Sheepdog
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_617BE9EB Old English Sheepdog; BREED_F0A0C6D9 English Springer Spaniel; BREED_5D7A8061 English Cocker Spaniel
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected Old English Sheepdog. Ω12 status is AMBIGUOUS with 3 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'English' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Old English Sheepdog, English Springer Spaniel, English Cocker Spaniel)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-06 — 'Hound'

- Category: shared_token
- Legacy result: BREED_3E1561D4 Afghan Hound
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_3E1561D4 Afghan Hound; BREED_C87E70CA Basset Hound
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected Afghan Hound. Ω12 status is AMBIGUOUS with 2 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Hound' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Afghan Hound, Basset Hound)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-07 — 'Inu'

- Category: shared_token
- Legacy result: BREED_3A7AB996 Shiba Inu
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_3A7AB996 Shiba Inu; BREED_4E0A4CB0 Akita Inu
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected Shiba Inu. Ω12 status is AMBIGUOUS with 2 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Inu' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Shiba Inu, Akita Inu)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-08 — 'Pinscher'

- Category: shared_token
- Legacy result: BREED_2641DA99 Miniature Pinscher
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_2641DA99 Miniature Pinscher; BREED_C687F403 Doberman Pinscher
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected Miniature Pinscher. Ω12 status is AMBIGUOUS with 2 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Pinscher' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Miniature Pinscher, Doberman Pinscher)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-09 — 'Retriever'

- Category: shared_token
- Legacy result: BREED_4C2466ED Golden Retriever
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_4C2466ED Golden Retriever; BREED_B02F1BE9 Labrador Retriever
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Named tests freeze current resolver/capture behavior: tests/normalization/test_omega12_mapping.py::test_f_ambiguous_retriever; tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved; tests/data/test_breed_node_baseline.py::test_contains_retriever_is_first_dataframe_contains_hit (current-behavior capture; not a product-meaning contract) Ω12 candidates are current warehouse canonical names containing this token. docs/WAGGY_SYSTEM.md documents that Ω12 does not pick Labrador for retriever. That describes current Ω12 design, not a Core-consumer migration decision.
- Observed difference: Legacy selected Golden Retriever. Ω12 status is AMBIGUOUS with 2 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Retriever' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Golden Retriever, Labrador Retriever)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-10 — 'Sheepdog'

- Category: shared_token
- Legacy result: BREED_617BE9EB Old English Sheepdog
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_617BE9EB Old English Sheepdog; BREED_571535AE Shetland Sheepdog
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected Old English Sheepdog. Ω12 status is AMBIGUOUS with 2 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Sheepdog' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Old English Sheepdog, Shetland Sheepdog)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-11 — 'Spaniel'

- Category: shared_token
- Legacy result: BREED_10A53062 Cavalier King Charles Spaniel
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_10A53062 Cavalier King Charles Spaniel; BREED_A00AD6C7 American Cocker Spaniel; BREED_F0A0C6D9 English Springer Spaniel; BREED_5D7A8061 English Cocker Spaniel
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected Cavalier King Charles Spaniel. Ω12 status is AMBIGUOUS with 4 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Spaniel' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Cavalier King Charles Spaniel, American Cocker Spaniel, English Springer Spaniel, English Cocker Spaniel)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-12 — 'Terrier'

- Category: shared_token
- Legacy result: BREED_6DB4AA40 Boston Terrier
- Ω12 result: status=AMBIGUOUS canonical_id=None rule=shared_name_token
- Candidates: BREED_6DB4AA40 Boston Terrier; BREED_43DD399E Bedlington Terrier; BREED_1B953788 Jack Russell Terrier; BREED_074A355B Kerry Blue Terrier; BREED_AB5D5A28 Bull Terrier; BREED_46D833A4 West Highland White Terrier; BREED_D8797FDC Yorkshire Terrier
- Ω12 rule: shared_name_token
- Existing evidence: EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Named tests freeze current resolver/capture behavior: tests/normalization/test_omega12_mapping.py::test_f_ambiguous_terrier Ω12 candidates are current warehouse canonical names containing this token.
- Observed difference: Legacy selected Boston Terrier. Ω12 status is AMBIGUOUS with 7 candidates and selected none. Ω12 rule is shared_name_token.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Terrier' resolve to a single canonical breed, remain unresolved, or remain identity-ambiguous across the Ω12 candidates (Boston Terrier, Bedlington Terrier, Jack Russell Terrier, Kerry Blue Terrier, Bull Terrier, West Highland White Terrier, Yorkshire Terrier)?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

### GROUP_B_UNIQUE_TOKEN

#### D-13 — 'Corgi'

- Category: unique_token
- Legacy result: BREED_6CBDD78C Pembroke Welsh Corgi
- Ω12 result: status=UNRESOLVED canonical_id=None rule=no_approved_mapping
- Candidates: (none)
- Ω12 rule: no_approved_mapping
- Existing evidence: EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Named tests freeze current resolver/capture behavior: tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved; tests/normalization/test_omega12_breed_identity.py::test_provider_does_not_expose_split_tokens_as_variants A warehouse canonical name contains this token once. That token is not in warehouse/mapping/breed_aliases.csv.
- Observed difference: Legacy selected Pembroke Welsh Corgi. Ω12 status is UNRESOLVED (no_approved_mapping). Catalog uniqueness is not an approved mapping.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Corgi' be treated as an approved alias for a specific canonical breed, or remain unresolved?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

- Candidate knowledge: INACTIVE candidate knowledge: 'Corgi' is not an approved alias. Legacy selected Pembroke Welsh Corgi. Ω12 is UNRESOLVED. No canonical target is assigned. Do not write this into breed_aliases.csv until a human supplies ADD_APPROVED_KNOWLEDGE with an explicit identity.

#### D-14 — 'Husky'

- Category: unique_token
- Legacy result: BREED_D7352671 Siberian Husky
- Ω12 result: status=UNRESOLVED canonical_id=None rule=no_approved_mapping
- Candidates: (none)
- Ω12 rule: no_approved_mapping
- Existing evidence: EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Named tests freeze current resolver/capture behavior: tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved; tests/normalization/test_omega12_breed_identity.py::test_provider_does_not_expose_split_tokens_as_variants A warehouse canonical name contains this token once. That token is not in warehouse/mapping/breed_aliases.csv.
- Observed difference: Legacy selected Siberian Husky. Ω12 status is UNRESOLVED (no_approved_mapping). Catalog uniqueness is not an approved mapping.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Husky' be treated as an approved alias for a specific canonical breed, or remain unresolved?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

- Candidate knowledge: INACTIVE candidate knowledge: 'Husky' is not an approved alias. Legacy selected Siberian Husky. Ω12 is UNRESOLVED. No canonical target is assigned. Do not write this into breed_aliases.csv until a human supplies ADD_APPROVED_KNOWLEDGE with an explicit identity.

#### D-15 — 'Bulldog'

- Category: unique_token
- Legacy result: BREED_08E4F037 French Bulldog
- Ω12 result: status=UNRESOLVED canonical_id=None rule=no_approved_mapping
- Candidates: (none)
- Ω12 rule: no_approved_mapping
- Existing evidence: EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Named tests freeze current resolver/capture behavior: tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_shared_token_ambiguous_and_unique_unresolved; tests/normalization/test_omega12_breed_identity.py::test_provider_does_not_expose_split_tokens_as_variants A warehouse canonical name contains this token once. That token is not in warehouse/mapping/breed_aliases.csv.
- Observed difference: Legacy selected French Bulldog. Ω12 status is UNRESOLVED (no_approved_mapping). Catalog uniqueness is not an approved mapping.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should bare 'Bulldog' be treated as an approved alias for a specific canonical breed, or remain unresolved?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

- Candidate knowledge: INACTIVE candidate knowledge: 'Bulldog' is not an approved alias. Legacy selected French Bulldog. Ω12 is UNRESOLVED. No canonical target is assigned. Do not write this into breed_aliases.csv until a human supplies ADD_APPROVED_KNOWLEDGE with an explicit identity.

### GROUP_C_BLANK

#### D-16 — ''

- Category: blank
- Legacy result: BREED_23ECEA52 Beagle
- Ω12 result: status=UNRESOLVED canonical_id=None rule=blank_or_missing
- Candidates: (none)
- Ω12 rule: blank_or_missing
- Existing evidence: EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Named tests freeze current resolver/capture behavior: tests/normalization/test_omega12_mapping.py::test_q_blank_breed_is_not_provided; tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_blank_mixed_hyphen_and_intra_word_x; tests/data/test_breed_node_baseline.py::test_empty_primary_contains_all_and_takes_first_dataframe_row (current-behavior capture; not a product-meaning contract)
- Observed difference: Legacy selected Beagle. Ω12 status is UNRESOLVED (blank_or_missing).
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should blank breed input remain unresolved rather than inherit a legacy first-row result?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

#### D-17 — '   '

- Category: blank
- Legacy result: BREED_23ECEA52 Beagle
- Ω12 result: status=UNRESOLVED canonical_id=None rule=blank_or_missing
- Candidates: (none)
- Ω12 rule: blank_or_missing
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract.
- Observed difference: Legacy selected Beagle. Ω12 status is UNRESOLVED (blank_or_missing).
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should blank breed input remain unresolved rather than inherit a legacy first-row result?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

### GROUP_D_MIXED

#### D-18 — 'Lab x Golden'

- Category: mixed
- Legacy result: selected=no
- Ω12 result: status=MIXED canonical_id=None rule=mixed_breed_separator
- Candidates: (none)
- Ω12 rule: mixed_breed_separator
- Existing evidence: EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_APPROVED_MAPPING, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Named tests freeze current resolver/capture behavior: tests/normalization/test_omega12_mapping.py::test_r_mixed_breed_is_not_a_new_canonical_breed (exact test string is 'Labrador x Golden'; same mixed_breed_separator rule) Mixed components resolve through existing canonical names or approved aliases. docs/WAGGY_SYSTEM.md documents MIXED as not a new canonical breed.
- Observed difference: Ω12 status is MIXED with 2 components in expression order and no inferred percentages. Legacy treated the input as a single matcher string and selected none.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should mixed breed strings using x / × remain multi-component MIXED identities in expression order without inferred percentages, rather than a single matcher string?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

- Components:
  - RESOLVED BREED_B02F1BE9 Labrador Retriever rule=explicit_alias
  - RESOLVED BREED_4C2466ED Golden Retriever rule=explicit_alias

#### D-19 — 'Lab × Golden'

- Category: mixed
- Legacy result: selected=no
- Ω12 result: status=MIXED canonical_id=None rule=mixed_breed_separator
- Candidates: (none)
- Ω12 rule: mixed_breed_separator
- Existing evidence: EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_APPROVED_MAPPING, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Named tests freeze current resolver/capture behavior: tests/normalization/test_omega12_breed_identity.py::test_resolve_breed_blank_mixed_hyphen_and_intra_word_x (uses 'Labrador × Golden') Mixed components resolve through existing canonical names or approved aliases. docs/WAGGY_SYSTEM.md documents MIXED as not a new canonical breed.
- Observed difference: Ω12 status is MIXED with 2 components in expression order and no inferred percentages. Legacy treated the input as a single matcher string and selected none.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should mixed breed strings using x / × remain multi-component MIXED identities in expression order without inferred percentages, rather than a single matcher string?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

- Components:
  - RESOLVED BREED_B02F1BE9 Labrador Retriever rule=explicit_alias
  - RESOLVED BREED_4C2466ED Golden Retriever rule=explicit_alias

#### D-20 — 'Lab / Golden'

- Category: mixed
- Legacy result: selected=no
- Ω12 result: status=MIXED canonical_id=None rule=mixed_breed_separator
- Candidates: (none)
- Ω12 rule: mixed_breed_separator
- Existing evidence: EXISTING_TEST_CONTRACT, EXISTING_RUNTIME_BEHAVIOR, EXISTING_APPROVED_MAPPING, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. Named tests freeze current resolver/capture behavior: tests/normalization/test_omega12_mapping.py::test_r_slash_mixed_breed (uses 'Labrador Retriever / Golden Retriever') Mixed components resolve through existing canonical names or approved aliases. docs/WAGGY_SYSTEM.md documents MIXED as not a new canonical breed.
- Observed difference: Ω12 status is MIXED with 2 components in expression order and no inferred percentages. Legacy treated the input as a single matcher string and selected none.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should mixed breed strings using x / × remain multi-component MIXED identities in expression order without inferred percentages, rather than a single matcher string?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

- Components:
  - RESOLVED BREED_B02F1BE9 Labrador Retriever rule=explicit_alias
  - RESOLVED BREED_4C2466ED Golden Retriever rule=explicit_alias

#### D-21 — 'Beagle x French Bulldog'

- Category: mixed
- Legacy result: selected=no
- Ω12 result: status=MIXED canonical_id=None rule=mixed_breed_separator
- Candidates: (none)
- Ω12 rule: mixed_breed_separator
- Existing evidence: EXISTING_RUNTIME_BEHAVIOR, EXISTING_WAREHOUSE_IDENTITY, NO_EXPLICIT_CONTRACT
- Evidence notes: Observed current behavior is not automatically intended product meaning. Ω12 current rules are not automatically final product policy. BreedNode baseline tests are current-behavior capture, not a meaning contract. docs/WAGGY_SYSTEM.md documents MIXED as not a new canonical breed.
- Observed difference: Ω12 status is MIXED with 2 components in expression order and no inferred percentages. Legacy treated the input as a single matcher string and selected none.
- Decision status: REQUIRES_HUMAN_DECISION
- Proposed action: NONE
- Human decision question: Should mixed breed strings using x / × remain multi-component MIXED identities in expression order without inferred percentages, rather than a single matcher string?
- Notes: Observation only. proposed_action remains NONE. No B2C clarification flow is implied.

- Components:
  - RESOLVED BREED_23ECEA52 Beagle rule=exact_canonical_name
  - RESOLVED BREED_08E4F037 French Bulldog rule=exact_canonical_name

## Candidate knowledge changes

These rows are inactive. They must not be written to mapping CSVs,
the Ω12 provider, or KindIndex until a human supplies ADD_APPROVED_KNOWLEDGE
with an explicit canonical identity.

- D-13 'Corgi': INACTIVE candidate knowledge: 'Corgi' is not an approved alias. Legacy selected Pembroke Welsh Corgi. Ω12 is UNRESOLVED. No canonical target is assigned. Do not write this into breed_aliases.csv until a human supplies ADD_APPROVED_KNOWLEDGE with an explicit identity.
- D-14 'Husky': INACTIVE candidate knowledge: 'Husky' is not an approved alias. Legacy selected Siberian Husky. Ω12 is UNRESOLVED. No canonical target is assigned. Do not write this into breed_aliases.csv until a human supplies ADD_APPROVED_KNOWLEDGE with an explicit identity.
- D-15 'Bulldog': INACTIVE candidate knowledge: 'Bulldog' is not an approved alias. Legacy selected French Bulldog. Ω12 is UNRESOLVED. No canonical target is assigned. Do not write this into breed_aliases.csv until a human supplies ADD_APPROVED_KNOWLEDGE with an explicit identity.

## Future product implications

Non-binding architecture notes only. Not implemented in this phase.

- IDENTITY ENGINE vs PRODUCT UX remain separate layers.
- AMBIGUOUS means Ω12 did not establish a single identity. A future product
  layer may present candidates without ranking, or may choose another policy.
  Candidate order is warehouse encounter order, not recommendation.
- UNRESOLVED means Ω12 has no approved mapping. A future product layer may
  ask for refinement, show supported breeds, allow uncertainty, or continue
  without breed-specific reasoning. Phase D does not choose among these.
- MIXED already carries component identities in expression order and must not
  infer 50/50 or collapse to one canonical breed unless a later human decision
  says otherwise.
- Structured profile fields `primary_breed` / `secondary_breed` / `breed_split_pct`
  remain separate from mixed identity strings.

FUTURE_PRODUCT_DECISION applies to UX strategy. It is not a substitute for the
identity-meaning questions above.

## Explicit non-decisions

- no aliases were added
- no resolver rules changed
- no Core consumer migrated
- no API changed
- no B2C UI changed
- no Mongo added
- no LLM used
- no fuzzy matching added
- no semantic winner was selected
