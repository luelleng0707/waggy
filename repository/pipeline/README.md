# Runtime Pipeline Contracts

Permanent pipeline order:

1. Dog Resolver
2. Life Stage Resolver
3. Environment Resolver
4. Trait Resolver
5. Observation Resolver
6. Resolved Dog Validator
7. Evidence Collector
8. Evidence Graph Builder
9. (stop)

## Data Flow Contracts

- Dog Resolver
  - Input: `DogProfile`
  - Output: `ResolvedDog`
- Life Stage Resolver
  - Input: `ResolvedDog`
  - Output: `LifeStage`
- Environment Resolver
  - Input: `DogProfile`
  - Output: `ResolvedEnvironment`
- Trait Resolver
  - Input: `ResolvedDog`
  - Output: `ResolvedTraits`
- Observation Resolver
  - Input: `DogProfile`, `ResolvedTraits`
  - Output: `ResolvedTraits`
- Resolved Dog Validator
  - Input: `ResolvedDog`, `ResolvedEnvironment`, `ResolvedTraits`
  - Output: `ValidationResult`
- Evidence Collector
  - Inputs: `ResolvedDog`, `LifeStage`, `ResolvedEnvironment`, `ResolvedTraits`
  - Output: `EvidenceCollection`
- Evidence Graph Builder
  - Input: `EvidenceCollection`
  - Output: `EvidenceGraph`

Rules:
- Only `DogResolver` may consume raw `DogProfile`.
- Each stage consumes exactly the prior stage output.
- No stage may bypass the sequence.
