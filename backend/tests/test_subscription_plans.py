"""Subscription plan and gate tests."""

from app.core.subscription import PLAN_LIMITS, get_plan_limits


def test_plan_limits_starter():
    limits = get_plan_limits("starter")
    assert limits["max_books"] == PLAN_LIMITS["starter"]["max_books"]


def test_plan_limits_unknown_defaults_to_starter():
    limits = get_plan_limits("unknown_plan")
    assert limits["max_books"] == 500
