"""Subscription plan helper tests."""

from app.core.subscription import PLAN_LIMITS, get_plan_limits


def test_get_plan_limits_known_plan():
    limits = get_plan_limits("pro")
    assert limits["max_books"] == 5000
    assert limits["max_users"] == 100


def test_get_plan_limits_unknown_defaults_to_starter():
    limits = get_plan_limits("unknown-plan")
    assert limits == PLAN_LIMITS["starter"]
