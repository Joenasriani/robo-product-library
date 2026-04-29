# Product Sellability Audit

This audit is aligned with `products/catalog.yaml` and uses the actual repository paths under `products/`. It treats every listed product as a real commercial SKU candidate and classifies each item by what can truthfully be delivered now.

## Classification summary

- Ready for self-serve online sale: 0
- Ready for inquiry/manual sale: 15
- Needs review/internal-only: 0

No product should be presented as instant checkout or fully automated fulfillment until checkout, license acceptance, delivery, and customer qualification workflows are implemented.

| product name | canonical path | status | ready for online sale | ready for inquiry/manual sale | blockers | product-readiness decision | recommended next step |
|---|---|---|---|---|---|---|---|
| GCC Base Civility Pack | products/protocols/gcc_base_civility_pack | inquiry_only | false | true | Manual inquiry and fulfillment flow required; buyer robot/runtime review required | Sellable as a protocol/configuration bundle after customer scoping | Confirm robot middleware, supported languages, and venue rules before delivery. |
| GCC Clinic Patient Interaction Protocol | products/protocols/gcc_clinic_patient_interaction_protocol | inquiry_only | false | true | Manual inquiry and fulfillment flow required; healthcare review required | Sellable only with human clinical/operations review; not medical advice | Confirm clinic workflow, escalation rules, privacy requirements, and local compliance review. |
| GCC Event Reception Protocol | products/protocols/gcc_event_reception_protocol | inquiry_only | false | true | Manual inquiry and fulfillment flow required; event-specific scripting required | Sellable as an event-reception protocol pack after event scope review | Confirm event type, guest flow, languages, venue map, and operator escalation flow. |
| GCC Hospital Reception Protocol | products/protocols/gcc_hospital_reception_protocol | inquiry_only | false | true | Manual inquiry and fulfillment flow required; healthcare/safety review required | Sellable only with hospital operator review; not medical advice or triage | Confirm reception boundaries, emergency escalation, patient privacy, and local healthcare review. |
| GCC Hotel Concierge Protocol | products/protocols/gcc_hotel_concierge_protocol | inquiry_only | false | true | Manual inquiry and fulfillment flow required; hotel PMS/integration assumptions need review | Sellable as a hospitality protocol/configuration pack after integration scoping | Confirm robot model, concierge workflows, escalation paths, and supported languages. |
| GCC Mall Navigation & Wayfinding Protocol | products/protocols/gcc_mall_navigation_wayfinding_protocol | inquiry_only | false | true | Manual inquiry and fulfillment flow required; venue map/data required | Sellable as a wayfinding protocol pack after mall data review | Confirm maps, tenant directory source, accessibility routes, and safety zones. |
| GCC Pharmacy Assistance Protocol | products/protocols/gcc_pharmacy_assistance_protocol | inquiry_only | false | true | Manual inquiry and fulfillment flow required; pharmacy/legal review required | Sellable only as non-medical assistance protocol; not medical advice | Confirm allowed prompts, pharmacist escalation, privacy rules, and local regulatory boundaries. |
| GCC Privacy Zone Protocol Pack | products/protocols/gcc_privacy_zone_protocol_pack | inquiry_only | false | true | Manual inquiry and fulfillment flow required; privacy-sensitive behavior review required | Sellable as a privacy-zone behavior/configuration pack after local review | Confirm venue privacy rules, sensor constraints, restricted zones, and operator override behavior. |
| GCC Restaurant Host Protocol | products/protocols/gcc_restaurant_host_protocol | inquiry_only | false | true | Manual inquiry and fulfillment flow required; restaurant workflow scoping required | Sellable as a restaurant hosting protocol pack after operations review | Confirm reservation/queue workflow, seating scripts, escalation rules, and language requirements. |
| GCC Retail Floor Assistance Protocol | products/protocols/gcc_retail_floor_assistance_protocol | inquiry_only | false | true | Manual inquiry and fulfillment flow required; retailer catalog/process scoping required | Sellable as a retail assistance protocol pack after store workflow review | Confirm product catalog source, store zones, staff escalation, and customer-service boundaries. |
| GCC Royal + Privacy Protocol v1 | products/protocols/gcc_royal_privacy_protocol_v1 | inquiry_only | false | true | Manual inquiry and fulfillment flow required; VIP/privacy/high-authority review required | Sellable only after strict local human review; not legal, diplomatic, or identity verification | Confirm authority metadata source, VIP escalation, privacy-zone rules, and human protocol officer approval. |
| GCC Royal Protocol Pack | products/protocols/gcc_royal_protocol_pack | inquiry_only | false | true | Manual inquiry and fulfillment flow required; royal/VIP context review required | Sellable as a protocol/configuration pack only after human protocol review | Confirm local protocol rules, event/VIP context, operator escalation, and approved scripts. |
| GCC Security & Access Control Protocol | products/protocols/gcc_security_access_control_protocol | inquiry_only | false | true | Manual inquiry and fulfillment flow required; security/compliance review required | Sellable only as an assistance protocol; not identity verification or access-control authority | Confirm access-control integration, human guard escalation, privacy boundaries, and compliance review. |
| RAG as a Service | products/ai/rag-as-a-service | inquiry_only | false | true | Manual inquiry and fulfillment flow required; buyer must provide model key/data/hosting | Sellable as a runnable FastAPI RAG package for evaluation/integration; production hardening separate | Confirm provider key, documents, deployment target, authentication, and security requirements. |
| GCC Royal + Privacy Protocol v1 Downloadable Bundle | products/downloadables/gcc-royal-privacy-protocol-v1 | manual-fulfillment | false | true | Manual delivery, license acceptance, and buyer qualification required | Deliverable as a manually fulfilled downloadable bundle after inquiry approval | Confirm source protocol version, buyer approval, license terms, and delivery package contents. |

## Corrections made in this audit pass

- Corrected audit paths from deprecated `protocols/products/...` references to actual `products/protocols/...` paths.
- Added the AI product and downloadable bundle to the audit; they were missing from the prior audit artifact.
- Clarified that all current products are inquiry/manual-fulfillment products, not self-serve checkout products.
- Clarified that protocol products are protocol/configuration bundles, not complete robots, hosted SaaS systems, autonomous deployments, legal/compliance certifications, medical advice, or identity-verification systems.

## Remaining operational blocker

The catalog can be commercially presented as inquiry/manual fulfillment, but not as instant checkout, until RoboMarket has implemented checkout, license acceptance, delivery packaging, buyer qualification, and support-tracking workflows.
