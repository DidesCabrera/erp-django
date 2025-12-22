"""
Permission helpers.

These functions centralize business rules related to
what a user can or cannot do.

IMPORTANT:
- Views and templates should NEVER check profile.role directly.
- All permission logic should live here.
- In the future, these rules can be moved to Plan-based logic
  without changing the rest of the codebase.
"""


def can_publish(profile):
    """
    Determines whether the user can make content public.

    Current rule:
    - Only nutritionists can publish public content.
    """
    return profile.role == "nutritionist"


def can_fork(profile):
    """
    Determines whether the user can fork content.

    Current rule:
    - All users can fork content.
    """
    return True


def can_copy(profile):
    """
    Determines whether the user can create independent copies.

    Current rule:
    - Only nutritionists can copy content.
    """
    return profile.role == "nutritionist"
