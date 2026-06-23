"""
Subscription plan limits.
"""

from typing import TypedDict

PLAN_LIMITS: dict[str, dict[str, int]] = {
    "starter": {"max_books": 500, "max_users": 25, "max_ebooks": 50},
    "pro": {"max_books": 5000, "max_users": 100, "max_ebooks": 500},
    "professional": {"max_books": 5000, "max_users": 100, "max_ebooks": 500},
    "enterprise": {"max_books": 100_000, "max_users": 1000, "max_ebooks": 10_000},
}


class PlanLimits(TypedDict):
    max_books: int
    max_users: int
    max_ebooks: int


def get_plan_limits(plan: str) -> PlanLimits:
    return PLAN_LIMITS.get(plan, PLAN_LIMITS["starter"])  # type: ignore[return-value]
