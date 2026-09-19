# ADR-0001: Use a Modular Monolith

## Status
Accepted

## Context
DevFlow needs realistic backend architecture and clear domain boundaries, but it does not currently require independently deployable services.

## Decision
Build the backend as a modular monolith.

## Consequences

### Positive
- Simpler deployment and local development
- Easier debugging
- Fewer distributed-system failure modes
- Clear internal boundaries can still be enforced

### Negative
- Modules share one deployment unit
- Discipline is needed to prevent accidental coupling

## Revisit when
A real scaling, ownership, or deployment requirement justifies splitting a module into an independent service.
