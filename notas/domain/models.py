from django.db import models
from django.db.models import Prefetch
from django.contrib.auth.models import User
from notas.domain.constants.nutrition import (
    PROTEIN_KCAL_PER_GRAM,
    CARBS_KCAL_PER_GRAM,
    FAT_KCAL_PER_GRAM,
)
import uuid
from notas.domain.services.nutrition import compute_meal_nutrition



# ==================================================
# PLANS / PROFILES / SUBSCRIPTIONS
# ==================================================

class Plan(models.Model):
    ROLE_CHOICES = (
        ("member", "Member"),
        ("nutritionist", "Nutritionist"),
    )

    name = models.CharField(max_length=50)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    can_create_meal = models.BooleanField(default=False)
    can_create_dailyplan = models.BooleanField(default=False)
    can_create_program = models.BooleanField(default=False)
    can_publish = models.BooleanField(default=False)

    can_fork = models.BooleanField(default=True)
    can_copy = models.BooleanField(default=False)



    max_program_duration_days = models.PositiveIntegerField(null=True, blank=True)
    max_active_subscriptions = models.PositiveIntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.role})"


class Profile(models.Model):
    ROLE_CHOICES = (
        ("member", "Member"),
        ("nutritionist", "Nutritionist"),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    plan = models.ForeignKey(Plan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="profiles")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} ({self.role})"


class Subscription(models.Model):
    nutritionist = models.ForeignKey(
        User, related_name="subscriptions_received", on_delete=models.CASCADE
    )
    member = models.ForeignKey(
        User, related_name="subscriptions_made", on_delete=models.CASCADE
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("nutritionist", "member")

    def __str__(self):
        return f"{self.member} → {self.nutritionist}"


# ==================================================
# FOOD
# ==================================================

class Food(models.Model):
    name = models.CharField(max_length=100)

    protein = models.FloatField()
    carbs = models.FloatField()
    fat = models.FloatField()

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # ---- kcal por macro (por 100g) ----
    @property
    def kcal_protein(self):
        return self.protein * PROTEIN_KCAL_PER_GRAM

    @property
    def kcal_carbs(self):
        return self.carbs * CARBS_KCAL_PER_GRAM

    @property
    def kcal_fat(self):
        return self.fat * FAT_KCAL_PER_GRAM

    @property
    def total_kcal(self):
        return self.kcal_protein + self.kcal_carbs + self.kcal_fat

    # ---- alloc por food ----
    @property
    def alloc(self):
        if self.total_kcal == 0:
            return {"protein": 0, "carbs": 0, "fat": 0}

        return {
            "protein": self.kcal_protein / self.total_kcal * 100,
            "carbs": self.kcal_carbs / self.total_kcal * 100,
            "fat": self.kcal_fat / self.total_kcal * 100,
        }

    @property
    def category(self):
        if self.created_by_id is None:
            return "system"
        return "user"


# ==================================================
# MEAL + MEAL FOOD
# ==================================================

class Meal(models.Model):
    name = models.CharField(max_length=100)

    foods = models.ManyToManyField(Food, through="MealFood")

    is_public = models.BooleanField(default=False)
    is_forkable = models.BooleanField(default=True)
    is_copiable = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    
    pending_dailyplan = models.ForeignKey(
        "DailyPlan",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+"
    )

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    original_author = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    forked_from = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="variants"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def kind(self):
        return "Meal"

    def __str__(self):
        return self.name

    # ==================================================
    # DOMAIN STATE HELPERS
    # ==================================================

    @property
    def is_dpm_instance(self):
        """Meal que vive dentro de un DailyPlanMeal."""
        return self.dailyplanmeal_set.exists()


    @property
    def is_original(self):
        """Meal creada desde cero por el usuario."""
        return (
            self.forked_from is None
            and not self.is_dpm_instance
        )

    @property
    def is_duplicate(self):
        """Meal copiada desde otra meal pero guardada en la biblioteca."""
        return (
            self.forked_from is not None
            and not self.is_dpm_instance
        )

    @property
    def category(self):
        """
        Categoría lógica de la meal.
        """
        if self.is_dpm_instance:
            return "en plan"

        if self.forked_from:
            return "duplicada"

        return "original"

    # ---- gramos ----

    @property
    def protein(self):
        if self.protein_cached is not None:
            return self.protein_cached
        return compute_meal_nutrition(self)["protein"]

    @property
    def carbs(self):
        if self.carbs_cached is not None:
            return self.carbs_cached
        return compute_meal_nutrition(self)["carbs"]

    @property
    def fat(self):
        if self.fat_cached is not None:
            return self.fat_cached
        return compute_meal_nutrition(self)["fat"]


    # ---- kcal ----
    @property
    def kcal_protein(self):
        return sum(mf.kcal_protein for mf in self.meal_food_set.all())

    @property
    def kcal_carbs(self):
        return sum(mf.kcal_carbs for mf in self.meal_food_set.all())

    @property
    def kcal_fat(self):
        return sum(mf.kcal_fat for mf in self.meal_food_set.all())

    @property
    def total_kcal(self):
        return self.kcal_protein + self.kcal_carbs + self.kcal_fat

    @property
    def alloc(self):
        if self.total_kcal == 0:
            return {"protein": 0, "carbs": 0, "fat": 0}

        return {
            "protein": self.kcal_protein / self.total_kcal * 100,
            "carbs": self.kcal_carbs / self.total_kcal * 100,
            "fat": self.kcal_fat / self.total_kcal * 100,
        }

    # ==================================================
    # CACHED
    # ==================================================

    protein_cached = models.FloatField(null=True, blank=True)
    carbs_cached = models.FloatField(null=True, blank=True)
    fat_cached = models.FloatField(null=True, blank=True)

    kcal_protein_cached = models.FloatField(null=True, blank=True)
    kcal_carbs_cached = models.FloatField(null=True, blank=True)
    kcal_fat_cached = models.FloatField(null=True, blank=True)
    total_kcal_cached = models.FloatField(null=True, blank=True)

    alloc_protein_cached = models.FloatField(null=True, blank=True)
    alloc_carbs_cached = models.FloatField(null=True, blank=True)
    alloc_fat_cached = models.FloatField(null=True, blank=True)

    foods_aggregation_cached = models.JSONField(null=True, blank=True)



    # ==================================================
    # DOMAIN API (delegates to services)
    # ==================================================

    def update_draft_status(self):
        if self.meal_food_set.exists():
            if self.is_draft:
                self.is_draft = False
                self.save(update_fields=["is_draft"])



class MealFood(models.Model):
    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name="meal_food_set")
    
    food = models.ForeignKey(Food, on_delete=models.CASCADE)

    quantity = models.FloatField(help_text="grams")

    def __str__(self):
        return f"{self.food} in {self.meal}"

    @property
    def factor(self):
        return self.quantity / 100

    @property
    def protein(self):
        return self.food.protein * self.factor

    @property
    def carbs(self):
        return self.food.carbs * self.factor

    @property
    def fat(self):
        return self.food.fat * self.factor

    @property
    def kcal_protein(self):
        return self.food.kcal_protein * self.factor

    @property
    def kcal_carbs(self):
        return self.food.kcal_carbs * self.factor

    @property
    def kcal_fat(self):
        return self.food.kcal_fat * self.factor

    @property
    def total_kcal(self):
        return self.kcal_protein + self.kcal_carbs + self.kcal_fat


    # ---------- alloc por macro dentro de la meal ----------

    @property
    def alloc_protein(self):
        total = self.meal.kcal_protein
        if total == 0:
            return 0
        return self.kcal_protein / total * 100

    @property
    def alloc_carbs(self):
        total = self.meal.kcal_carbs
        if total == 0:
            return 0
        return self.kcal_carbs / total * 100

    @property
    def alloc_fat(self):
        total = self.meal.kcal_fat
        if total == 0:
            return 0
        return self.kcal_fat / total * 100

    @property
    def alloc(self):
        return {
            "protein": self.alloc_protein,
            "carbs": self.alloc_carbs,
            "fat": self.alloc_fat,
        }


# ==================================================
# DAILY PLAN + PROGRAM
# ==================================================

class DailyPlan(models.Model):
    name = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    original_author = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )
    forked_from = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="variants"
    )

    is_public = models.BooleanField(default=False)
    is_forkable = models.BooleanField(default=True)
    is_copiable = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def kind(self):
        return "Daily Plan"

    def __str__(self):
        return self.name

    # ==================================================
    # DOMAIN STATE HELPERS
    # ==================================================

    @property
    def is_original(self):
        """
        DailyPlan creado desde cero por el usuario.
        """
        return self.forked_from is None


    @property
    def is_duplicate(self):
        """
        DailyPlan fork/copied desde otro plan.
        """
        return self.forked_from is not None


    @property
    def category(self):
        """Categoría lógica del DailyPlan."""
        # FUTURO: instancia dentro de programa
        if hasattr(self, "programdailyplan_set") and self.programdailyplan_set.exists():
            return "en plan"

        if self.forked_from:
            return "duplicado"

        return "original"


    @property
    def protein(self):
        return sum(dpm.meal.protein for dpm in self.dailyplan_meals.all())

    @property
    def carbs(self):
        return sum(dpm.meal.carbs for dpm in self.dailyplan_meals.all())

    @property
    def fat(self):
        return sum(dpm.meal.fat for dpm in self.dailyplan_meals.all())

    @property
    def kcal_protein(self):
        return sum(dpm.meal.kcal_protein for dpm in self.dailyplan_meals.all())

    @property
    def kcal_carbs(self):
        return sum(dpm.meal.kcal_carbs for dpm in self.dailyplan_meals.all())

    @property
    def kcal_fat(self):
        return sum(dpm.meal.kcal_fat for dpm in self.dailyplan_meals.all())

    @property
    def total_kcal(self):
        return self.kcal_protein + self.kcal_carbs + self.kcal_fat

    @property
    def alloc(self):
        if self.total_kcal == 0:
            return {"protein": 0, "carbs": 0, "fat": 0}

        return {
            "protein": self.kcal_protein / self.total_kcal * 100,
            "carbs": self.kcal_carbs / self.total_kcal * 100,
            "fat": self.kcal_fat / self.total_kcal * 100,
        }
    
    def meals_with_foods(self):
        return (
            self.dailyplan_meals
            .select_related("meal")
            .prefetch_related(
                Prefetch(
                    "meal__meal_food_set",
                    queryset=MealFood.objects.select_related("food")
                )
            )
        )
    
    # ==================================================
    # DOMAIN API (delegates to services)
    # ==================================================

    def update_draft_status(self):

        if not self.is_draft:
            return

        if self.dailyplan_meals.exists():
            self.is_draft = False
            self.save(update_fields=["is_draft"])


class DailyPlanMeal(models.Model):
    dailyplan = models.ForeignKey(
        DailyPlan,
        on_delete=models.CASCADE,
        related_name="dailyplan_meals"
    )
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)

    note = models.CharField(max_length=255, blank=True, null=True)
    hour = models.TimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "id"]

    def __str__(self):
        return f"{self.dailyplan.name} ({self.meal.name})"

    # ------------------
    # Totales
    # ------------------

    @property
    def total_kcal(self):
        return (
            self.meal.kcal_protein +
            self.meal.kcal_carbs +
            self.meal.kcal_fat
        )

    # ------------------
    # Alloc relativo (%)
    # ------------------

    def _safe_alloc(self, part, total):
        if not total or total <= 0:
            return 0.0
        return (part / total) * 100

    @property
    def alloc_protein(self):
        return self._safe_alloc(
            self.meal.kcal_protein,
            self.dailyplan.kcal_protein
        )

    @property
    def alloc_carbs(self):
        return self._safe_alloc(
            self.meal.kcal_carbs,
            self.dailyplan.kcal_carbs
        )

    @property
    def alloc_fat(self):
        return self._safe_alloc(
            self.meal.kcal_fat,
            self.dailyplan.kcal_fat
        )

    @property
    def alloc(self):
        return {
            "protein": self.alloc_protein,
            "carbs": self.alloc_carbs,
            "fat": self.alloc_fat,
        }




class Program(models.Model):
    name = models.CharField(max_length=100)

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="programs"
    )
    original_author = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    forked_from = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="variants"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_public = models.BooleanField(default=False)
    is_forkable = models.BooleanField(default=True)
    is_copiable = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def kind(self):
        return "Program"

    def __str__(self):
        return self.name

    @property
    def protein(self):
        return sum(day.dailyplan.protein for day in self.program_dailyplan.all())

    @property
    def carbs(self):
        return sum(day.dailyplan.carbs for day in self.program_dailyplan.all())

    @property
    def fat(self):
        return sum(day.dailyplan.fat for day in self.program_dailyplan.all())

    @property
    def kcal_protein(self):
        return sum(day.dailyplan.kcal_protein for day in self.program_dailyplan.all())

    @property
    def kcal_carbs(self):
        return sum(day.dailyplan.kcal_carbs for day in self.program_dailyplan.all())

    @property
    def kcal_fat(self):
        return sum(day.dailyplan.kcal_fat for day in self.program_dailyplan.all())

    @property
    def total_kcal(self):
        return self.kcal_protein + self.kcal_carbs + self.kcal_fat

    @property
    def alloc(self):
        if self.total_kcal == 0:
            return {"protein": 0, "carbs": 0, "fat": 0}

        return {
            "protein": self.kcal_protein / self.total_kcal * 100,
            "carbs": self.kcal_carbs / self.total_kcal * 100,
            "fat": self.kcal_fat / self.total_kcal * 100,
        }



class ProgramDay(models.Model):
    program = models.ForeignKey(
        Program,
        on_delete=models.CASCADE,
        related_name="program_dailyplan"
    )
    dailyplan = models.ForeignKey(DailyPlan, on_delete=models.CASCADE)
    date = models.DateField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["date"]

    def __str__(self):
        return f"{self.program.name} - {self.date}"


# ==================================================
# ACCESS
# ==================================================

class MealAccess(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    granted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)


# ==================================================
# WEIGHT TRACKING (PROGRESS)
# ==================================================


class WeightLog(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="weight_logs"
    )

    date = models.DateField()
    weight_kg = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        unique_together = ("user", "date")   # opcional: un registro por día

    def __str__(self):
        return f"{self.user.username} - {self.weight_kg} kg ({self.date})"




class DailyPlanShare(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="dailyplan_shares_sent"
    )

    recipient_email = models.EmailField()

    dailyplan = models.ForeignKey(
        DailyPlan,
        on_delete=models.CASCADE,
        related_name="shares"
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True)

    accepted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="dailyplan_shares_received"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    dismissed = models.BooleanField(default=False)      # inbox
    removed = models.BooleanField(default=False)        # librería

    class Meta:
        unique_together = ("recipient_email", "dailyplan")

    def __str__(self):
        return f"{self.sender} shared {self.dailyplan} → {self.recipient_email}"


class MealShare(models.Model):
    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="meal_shares_sent"
    )

    recipient_email = models.EmailField()

    meal = models.ForeignKey(
        Meal,
        on_delete=models.CASCADE,
        related_name="shares"
    )

    token = models.UUIDField(default=uuid.uuid4, unique=True)

    accepted_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="meal_shares_received"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    
    dismissed = models.BooleanField(default=False)      # inbox
    removed = models.BooleanField(default=False)        # librería

    class Meta:
        unique_together = ("recipient_email", "meal")

    def __str__(self):
        return f"{self.sender} shared {self.meal} → {self.recipient_email}"
