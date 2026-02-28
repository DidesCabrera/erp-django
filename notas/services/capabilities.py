def get_capabilities(user):
    if not user or not user.is_authenticated:
        return None

    if not hasattr(user, "profile"):
        return None

    return Capabilities(user.profile)


class Capabilities:
    def __init__(self, profile):
        self.profile = profile
        self.plan = profile.plan
        self.role = profile.role

    # -----------------
    # CREATION
    # -----------------

    def can_create_food(self):
        return bool(self.plan and self.plan.can_create_food)

    def can_create_meal(self):
        return bool(self.plan and self.plan.can_create_meal)

    def can_create_dailyplan(self):
        return bool(self.plan and self.plan.can_create_dailyplan)

    def can_create_program(self):
        return bool(self.plan and self.plan.can_create_program)

    # -----------------
    # VISIBILITY
    # -----------------

    def can_publish(self):
        return bool(self.plan and self.plan.can_publish)

    # -----------------
    # FORK / COPY
    # -----------------

    def can_fork(self):
        return bool(self.plan and self.plan.can_fork)

    def can_copy(self):
        return bool(self.plan and self.plan.can_copy)

    # -----------------
    # EDITING
    # -----------------

    def can_edit_own_content(self):
        return True  # regla base del producto

    def can_replace_meal(self):
        return True  # MVP: permitido

    # -----------------
    # ROLE OVERRIDES
    # -----------------

    def is_admin(self):
        return self.role == "admin"
