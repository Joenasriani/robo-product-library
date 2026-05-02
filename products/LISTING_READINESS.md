# Product Listing Readiness Standard

This repository prepares products for later RoboMarket.ae marketplace listing. It does not need to contain payment checkout, Stripe logic, marketplace order routing, or automated fulfillment yet.

## Listing-ready definition

A product is listing-ready when a robotics buyer can clearly understand:

- what the product is
- who it is for
- what files or services the buyer receives
- how a robotics developer or integrator can review and adapt it
- what is excluded
- what needs venue-specific validation before deployment
- whether it is buy-now, downloadable, inquiry-only, or staged for later fulfillment

## Required listing evidence

Every product listed in `products/catalog.yaml` should have:

- `manifest.yaml`
- `README.md`
- manifest fields: `id`, `slug`, `name`, `version`, `deliverable_type`
- commercial boundary fields: `commercial_status`, `status`, `sales_mode`, `fulfillment_method`
- buyer-facing fields: `customer_receives`, `limitations`
- README section: `Usage`
- either `bundle`, `deliverable_manifest`, or clear `customer_receives`

## Payment boundary

Do not add or claim the following inside product folders unless the marketplace app actually implements them:

- working checkout
- Stripe payment flow
- automated file delivery
- order routing
- buyer account provisioning
- fulfillment tracking

Products may be marked `ready_for_marketplace_listing_review` when they are ready to be listed later, even if checkout is not live.

## Robotics truth boundary

Protocol products are not live robot controllers unless they include controller code. They must not claim to provide certified safety, legal compliance, medical advice, official royal protocol, firmware, perception models, or hardware drivers unless those deliverables exist.

## Valid sales modes

- `inquiry_only` — product can be listed with an inquiry CTA and manual review.
- `staged_downloadable_package_review` — package is being prepared for later download fulfillment.
- `buy_now_future` — product is intended for later payment integration but checkout is not implemented here.

## Marketplace listing copy rule

Marketplace listing copy must say exactly what exists now. Example:

> This is a robotics protocol pack for integrators. It includes structured behavior logic, integration notes, validation guidance, and deployment boundaries. It does not include robot firmware, certified safety approval, payment checkout, or automated delivery.
