# GCC Clinic Patient Interaction Protocol

Status: product-ready

Purpose:
Behavior protocol for robots operating in GCC clinic environments with patient, visitor, and family-facing interaction logic.

Included Files:
- core/base_policy.yaml
- core/role_rules.yaml
- core/country_overlays.yaml
- core/safety_overrides.yaml
- docs/product_page_copy.md
- docs/limitations.md
- docs/compatibility.md
- tests/scenarios.yaml
- tests/acceptance_criteria.yaml

## Usage

1. Review `manifest.yaml` and `RULES.yaml` for deployment constraints.
2. Apply policy files from `core/` to your robot behavior runtime.
3. Validate with `tests/acceptance_criteria.yaml` and `tests/scenarios.yaml`.
4. Follow environment integration steps in `docs/setup.md` and `docs/compatibility.md`.
5. Deliver `bundle.zip` to customers as the canonical package artifact.
