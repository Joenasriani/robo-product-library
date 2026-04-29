# Product Readiness Standard

This standard defines how products in `robo-product-library` must be documented before they are listed as individual sellable products on RoboMarket.ae.

## Repository placement rules

- `products/` contains only sellable, deliverable product SKUs.
- `systems/` contains runtime systems and internal applications.
- `plans/` contains non-sellable concepts, planning notes, and legacy material.
- `marketplace/` contains storefront metadata and listing assets.
- `archive/` contains paused or deprecated work.

## Minimum buyer-facing requirements

Every sellable product must state:

- Product name and product ID.
- Product type, such as protocol pack, configuration pack, API service, template, data package, or implementation module.
- Intended buyer and technical user.
- Primary use case.
- What the buyer receives.
- What technical files are included.
- What the buyer must provide.
- Setup or deployment steps.
- Compatibility and integration assumptions.
- Known limitations.
- Validation or testing notes.
- Support and maintenance expectations.
- Commercial status.

## Commercial status rules

Use explicit statuses only:

- `ready-to-list` when the product is complete enough to sell as a deliverable package.
- `inquiry-only` when manual review, custom integration, or buyer scoping is required.
- `manual-fulfillment` when delivery is possible but checkout automation is not implemented.
- `internal-only` when the material should not appear as a sellable product.
- `needs-review` when claims, scope, pricing, or technical completeness are uncertain.

Do not imply that checkout, automatic fulfillment, SaaS hosting, robot deployment, or legal/compliance approval exists unless the repository contains working implementation evidence.

## Protocol and configuration pack rules

A protocol, YAML policy, behavior tree, adapter mapping, localization pack, or ruleset must be described as a protocol/specification/configuration product unless the repository also includes a complete runtime implementation.

Do not describe a protocol pack as:

- a complete robot,
- an autonomous deployment,
- a SaaS platform,
- a compliance-certified system,
- a replacement for local staff or human review.

## GCC cultural product rules

GCC-focused protocol products must be factual, respectful, operational, and careful.

They must not include stereotypes, religious certainty, legal certainty, diplomatic certainty, or assumptions about all users in a country or culture.

They must clearly state that local human review is required before use in high-stakes environments, government contexts, royal/VIP contexts, healthcare contexts, security contexts, or public-facing deployments.

## Healthcare, security, privacy, and access-control boundaries

Products touching healthcare, pharmacy, clinic workflows, security, access control, privacy, VIP handling, or identity-sensitive interactions must explicitly state:

- Not medical advice.
- Not legal advice.
- Not identity verification by itself.
- Not a replacement for licensed professionals, security staff, compliance officers, or trained local operators.
- Requires human approval before deployment in regulated or high-stakes environments.

## Listing consistency requirements

For every sellable product, these files must agree when present:

- Product README.
- Product manifest YAML.
- Product catalog entry.
- Marketplace catalog/listing metadata.
- Product page copy.
- License/support docs.

Names, IDs, pricing, status, tags, deliverables, dependencies, and limitations must not conflict across these files.

## Price and fulfillment rules

Only include a numeric price when there is a clear commercial basis and the listing state is consistent across product and marketplace metadata.

If checkout or fulfillment automation is not implemented, mark the product as `inquiry-only` or `manual-fulfillment`.

## Demo and sample files

Demo files and sample data may remain if they help buyers understand integration. They must be labeled clearly as samples and must not be represented as customer-specific data, production data, or live deployments.

## Audit checklist

For each product, confirm:

- The product is in the correct repository section.
- The product has a buyer-readable README.
- The product has developer/integrator setup instructions.
- Commercial status is explicit and truthful.
- Capabilities are supported by files in the repo.
- Limitations and buyer responsibilities are clear.
- Marketplace metadata matches product metadata.
- Demo/sample content is labeled.
- No secrets, private keys, credentials, or customer data are committed.
