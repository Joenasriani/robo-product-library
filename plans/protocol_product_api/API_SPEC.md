Protocol Product API Plan

Purpose:
Serve downloadable protocol products separately from AI agent applications.

Product Type:
- Protocol packs
- Behavior-policy downloads
- Inquiry-first products
- Later: gated paid downloads

Endpoints:

1. GET /api/v1/protocol-products
- list active protocol products

2. GET /api/v1/protocol-products/{slug}
- return single protocol product metadata

3. POST /api/v1/protocol-products/inquiry
Input:
- name
- email
- company
- use_case
- product_id

Action:
- store inquiry
- notify admin
- send confirmation to user

4. POST /api/v1/admin/protocol-products/approve
- admin only
- marks inquiry approved
- triggers manual or automated delivery

5. POST /api/v1/admin/protocol-products/deliver
- admin only
- attaches delivery asset
- logs delivery record

Phase 1:
- inquiry + manual fulfillment

Phase 2:
- payment + gated download

Rule:
Protocol products remain separate from AI agent runtime apps.
