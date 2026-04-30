# Product Functionality Audit

Repository: `Joenasriani/robo-product-library`  
Branch: `vice-coding-product-audit`  
Purpose: verify whether each product package can stand as a functional, independent sellable deliverable later, regardless of marketplace checkout/payment readiness.

## Correct audit framing

Marketplace/payment readiness is not the current goal.

The current goal is stricter and more basic:

> Each product folder must be internally functional as a future sellable product package.

A product is considered functionally ready only when it has:

- unique product identity;
- a canonical manifest;
- a buyer/integrator README;
- real deliverable files;
- clear setup/use instructions;
- rules/configuration files where promised;
- docs for limitations, compatibility, deliverables, setup, and support;
- test scenarios or acceptance criteria;
- a package artifact, if `bundle.zip` is promised;
- no duplicate SKU identity elsewhere in `products/`;
- no unsupported claims that imply autonomy, certification, medical/legal/security authority, or complete robot deployment.

## Key repository-level finding

The canonical product catalog lists 15 products, but repository search shows additional `products/downloadables/...` folders that appear to duplicate protocol products by ID and content.

This is a functionality problem, not just a marketplace problem:

- duplicate product IDs can corrupt future catalog imports;
- duplicate packages can confuse which artifact is canonical;
- staged downloadable folders can accidentally become sellable SKUs;
- buyer-facing delivery can point to the wrong package.

## Critical functional issues found

### 1. Duplicate downloadable product folders

Several `products/downloadables/...` directories appear to mirror protocol products and contain their own `manifest.yaml`/`README.md` files while sharing IDs with canonical protocol products.

Observed examples include:

- `products/downloadables/gcc-base-civility-pack-v1/`
- `products/downloadables/gcc-clinic-patient-interaction-protocol-v1/`
- `products/downloadables/gcc-event-reception-protocol-v1/`
- `products/downloadables/gcc-hospital-reception-protocol-v1/`
- `products/downloadables/gcc-hotel-concierge-protocol-v1/`
- `products/downloadables/gcc-mall-navigation-wayfinding-protocol-v1/`
- `products/downloadables/gcc-pharmacy-assistance-protocol-v1/`
- `products/downloadables/gcc-privacy-zone-protocol-pack-v1/`
- `products/downloadables/gcc-restaurant-host-protocol-v1/`
- `products/downloadables/gcc-retail-floor-assistance-protocol-v1/`
- `products/downloadables/gcc-royal-protocol-pack-v1/`
- `products/downloadables/gcc-security-access-control-protocol-v1/`

Functional verdict:

**Not safe as-is.** These folders must either be:

1. promoted into canonical products with distinct downloadable IDs; or
2. moved out of `products/`; or
3. explicitly marked non-canonical/internal staging and excluded from future product indexing.

### 2. Ambiguous README status wording

Many product READMEs say:

```text
Status: product-ready
```

This is too ambiguous because the products are not marketplace/payment-ready. For this repo, `product-ready` should be replaced with a functional-deliverable status such as:

```text
Status: functional-package / inquiry-only
```

or:

```text
Status: functional-package; future marketplace listing requires checkout, license, fulfillment, and support workflow.
```

Functional verdict:

**Fix recommended.** The product can still be functional, but status wording must not imply automatic sale or automatic fulfillment.

### 3. Hospital README status conflict

`products/protocols/gcc_hospital_reception_protocol/README.md` says:

```text
Status: research-and-specification
```

But the product manifest and marketplace listing classify it as `inquiry_only` with price and deliverables.

Functional verdict:

**Needs correction.** If it remains in `products/`, it should be a functional package, not merely research/specification.

### 4. ZIP artifact verification is now partially possible through GitHub

GitHub can fetch `bundle.zip` files as base64 using the repository content API. For the checked `gcc_base_civility_pack/bundle.zip`, the ZIP central directory exposed expected files, including:

- `README.md`
- `RULES.yaml`
- `core/base_policy.yaml`
- `core/country_overlays.yaml`
- `core/dialogue_templates.yaml`
- `core/venue_modes.yaml`
- `docs/compatibility.md`
- `docs/deliverables.md`
- `docs/limitations.md`
- `docs/product_page_copy.md`
- `docs/setup.md`
- `docs/support.md`
- `manifest.yaml`
- `tests/acceptance_criteria.yaml`
- `tests/qa_checklist.md`
- `tests/scenarios.yaml`

Functional verdict:

**ZIP presence and partial internal listing can be verified through GitHub.** Full artifact validation still requires local or CI unzip/hash/testing.

## Product-by-product functional audit

| Product | Functional package verdict | Main blocker to full confidence |
|---|---|---|
| GCC Base Civility Pack | Likely functional protocol package | Duplicate downloadable folder with same product identity must be resolved. |
| GCC Clinic Patient Interaction Protocol | Likely functional protocol package | Healthcare limitations must stay explicit; duplicate downloadable folder must be resolved. |
| GCC Event Reception Protocol | Likely functional protocol package | Event-specific integration claims must stay limited; duplicate downloadable folder must be resolved. |
| GCC Hospital Reception Protocol | Needs status correction | README says `research-and-specification` while manifest/listing treat it as sellable inquiry-only. |
| GCC Hotel Concierge Protocol | Likely functional protocol package | Must not imply PMS/booking/payment integration; duplicate downloadable folder must be resolved. |
| GCC Mall Navigation & Wayfinding Protocol | Likely functional protocol package | Must not imply full navigation stack; duplicate downloadable folder must be resolved. |
| GCC Pharmacy Assistance Protocol | Likely functional protocol package | Must not imply medical advice; duplicate downloadable folder must be resolved. |
| GCC Privacy Zone Protocol Pack | Likely functional protocol package | Must not imply legal privacy compliance; duplicate downloadable folder must be resolved. |
| GCC Restaurant Host Protocol | Likely functional protocol package | Must not imply POS/reservation integration; duplicate downloadable folder must be resolved. |
| GCC Retail Floor Assistance Protocol | Likely functional protocol package | Must not imply inventory/live catalog integration; duplicate downloadable folder must be resolved. |
| GCC Royal + Privacy Protocol v1 | Functionally sensitive; keep inquiry-only | High VIP/privacy risk; artifact and naming must remain tightly controlled. |
| GCC Royal Protocol Pack | Functionally sensitive; keep inquiry-only | Must not imply official royal/government protocol authority; duplicate downloadable folder must be resolved. |
| GCC Security & Access Control Protocol | Functionally sensitive; keep inquiry-only | Must not imply autonomous identity verification/access authority; duplicate downloadable folder must be resolved. |
| RAG as a Service | Likely functional runnable package | Requires clean install/test run before verified functional status. |
| GCC Royal + Privacy Protocol v1 Downloadable Bundle | Needs artifact/license verification | Downloadable delivery must prove package contents and license gating. |

## Validator added

This PR adds:

```text
tools/validate_product_functionality.py
```

The script checks product-library invariants:

- every manifest has an `id`;
- IDs are unique across `products/`;
- every manifest has a sibling README;
- every manifest that references `bundle.zip` has a sibling `bundle.zip`;
- every product README has a sibling manifest;
- ambiguous `Status: product-ready` is warned;
- `Status: research-and-specification` inside `products/` is treated as an error.

Run:

```bash
python tools/validate_product_functionality.py
```

## Required fixes to make products fully functional

1. Resolve duplicate downloadable folders.
   - Either give every downloadable a distinct product ID and catalog entry, or move non-canonical staging folders out of `products/`.

2. Replace ambiguous README statuses.
   - Use `functional-package / inquiry-only` for packages that are deliverable but not self-serve marketplace-ready.

3. Fix the hospital protocol README.
   - Replace `research-and-specification` with the correct functional status if all files are present.

4. Add CI.
   - Run `python tools/validate_product_functionality.py` on every PR.

5. Add ZIP validation.
   - Add a CI job that unzips every `products/**/bundle.zip` and checks it contains the same required files promised by the manifest and README.

6. Run the RAG package tests.
   - Install dependencies and run tests in a clean environment before marking it `VERIFIED_FUNCTIONAL`.

## Final functionality verdict

The catalog products are not fake concepts. Most appear to be valid protocol/configuration packages. But the repository is not yet fully clean as a product library because duplicate downloadable folders and ambiguous statuses can break future catalog ingestion and commercial delivery.

The next PR should be a **functional hardening PR**, not another audit-only PR.
