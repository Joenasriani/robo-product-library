# GCC Privacy Zone Protocol Pack

Status: product-ready

Purpose:
Standalone privacy-first protocol for women-sensitive and restricted interaction spaces.

Included Files:
- core/base_policy.yaml
- core/country_overlays.yaml
- core/venue_modes.yaml
- core/privacy_mode.yaml
- core/safety_overrides.yaml
- core/dialogue_templates.yaml
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
