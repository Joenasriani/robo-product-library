Frontend Logic – RoboMarket Product

Product Card:
- title
- category
- price
- readiness note: inquiry-only (no instant checkout)
- buttons: View details / Inquire

---

Product Page:

Sections:
- Title
- Subtitle
- Description
- Deliverables / Included files
- Requirements
- Use cases / best fit
- Limitations
- Support & fulfillment mode

---

Buttons:

View:
- opens product page

Inquire:
- opens modal form

Form fields:
- Name
- Email
- Company
- Use case

Submit:
- POST /api/inquiry

---

Buy:
- not shown while checkout flow is not implemented
- product pages must explicitly state inquiry-only fulfillment

---

Future:
- enable Stripe checkout
- redirect to success page
- trigger download
