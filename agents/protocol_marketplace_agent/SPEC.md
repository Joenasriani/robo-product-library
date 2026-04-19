# Protocol Marketplace Agent Spec

## Goal
Create a real marketplace system for browsing, inquiring about, and receiving delivery of robot protocol packs.

## Product Definition
Each protocol product must include:
- product_id
- name
- category
- country or region
- description
- price_aed
- delivery_type
- included_files
- hardware_requirements
- risk_level
- version
- status

## Core Functions

### 1. Protocol Catalog
The system must:
- list available protocol packs
- group by category and country
- show product metadata clearly
- hide products with no real deliverables

### 2. Product Validation
A protocol cannot be published unless:
- RULES.yaml exists
- SCENARIOS.md exists
- README.md exists
- downloadable assets are real
- inquiry flow is connected
- delivery flow is defined

### 3. Inquiry and Approval Flow
The system must support:
- inquiry submission
- entitlement creation after admin approval
- order record creation
- post-approval delivery trigger

### 4. Entitlement Logic
After purchase, buyer must receive:
- access to the purchased protocol only
- downloadable asset access
- version visibility
- product ownership record

### 5. Delivery Logic
Supported delivery methods:
- dashboard download
- signed file link
- email fulfillment
- admin-assisted enterprise delivery

### 6. Admin Controls
Admin must be able to:
- create protocol products
- activate/deactivate products
- update pricing
- replace downloadable files
- revoke broken listings
- inspect entitlement records

## No-Fake Rules
- no buy button without real files
- no live listing without real delivery
- no placeholder packs in production
- no fake compatibility claims
- no dummy purchase success states

## Recommended Data Model

### Protocol Product
- product_id
- slug
- name
- category
- region
- description
- price_aed
- status
- version
- risk_level
- hardware_requirements
- included_files
- created_at
- updated_at

### Entitlement
- entitlement_id
- buyer_id
- product_id
- order_id
- granted_at
- expires_at
- status

### Delivery Record
- delivery_id
- entitlement_id
- delivery_type
- file_path
- delivered_at
- delivery_status

## Initial Products
- UAE Localization Pack
- Saudi Localization Pack

## Next Expansion
- Qatar Localization Pack
- Kuwait Localization Pack
- Bahrain Localization Pack
- Oman Localization Pack
