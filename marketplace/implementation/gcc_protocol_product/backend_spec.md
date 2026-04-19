Backend Logic – GCC Protocol Product

Endpoints:

POST /api/inquiry
- name
- email
- company
- use_case
- product_id

Action:
- store in database
- send email to admin
- send confirmation email to user

---

GET /api/product/:id
- returns product.json

---

POST /api/admin/approve
- admin_token required
- marks inquiry as approved
- triggers delivery

---

Delivery Phase 1:
- manual email with ZIP

Delivery Phase 2 (future, when payment flow is integrated):
- generate signed download link
- send email with download URL
