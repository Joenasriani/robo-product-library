from fastapi import HTTPException, status
from src import settings

PLAN_MAP = {
    "starter": settings.STRIPE_PRICE_STARTER,
    "growth": settings.STRIPE_PRICE_GROWTH,
    "enterprise": settings.STRIPE_PRICE_ENTERPRISE,
}

def stripe_enabled() -> bool:
    return bool(settings.STRIPE_SECRET_KEY)

def create_checkout_session(client_id: int, plan: str, success_url: str, cancel_url: str):
    if not stripe_enabled():
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Stripe billing is not configured")
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    price_ref = PLAN_MAP.get(plan)
    if not price_ref:
        raise HTTPException(status_code=400, detail="Unknown plan or missing Stripe price id")
    session = stripe.checkout.Session.create(
        mode="payment",
        line_items=[{"price": price_ref, "quantity": 1}],
        success_url=success_url,
        cancel_url=cancel_url,
        metadata={"client_id": str(client_id), "plan": plan},
    )
    return {"checkout_url": session.url, "session_id": session.id}
