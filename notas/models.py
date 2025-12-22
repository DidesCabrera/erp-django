from django.db import models
from django.db.models import Prefetch
from django.contrib.auth.models import User
from django.urls import reverse
from notas.services.nutrition import (
    PROTEIN_KCAL_PER_GRAM,
    CARBS_KCAL_PER_GRAM,
    FAT_KCAL_PER_GRAM,
)

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
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)

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

    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    original_author = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL, related_name="+"
    )

    forked_from = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="variants"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    # ---- gramos ----
    @property
    def protein(self):
        return sum(mf.protein for mf in self.mealfood_set.all())

    @property
    def carbs(self):
        return sum(mf.carbs for mf in self.mealfood_set.all())

    @property
    def fat(self):
        return sum(mf.fat for mf in self.mealfood_set.all())

    # ---- kcal ----
    @property
    def kcal_protein(self):
        return sum(mf.kcal_protein for mf in self.mealfood_set.all())

    @property
    def kcal_carbs(self):
        return sum(mf.kcal_carbs for mf in self.mealfood_set.all())

    @property
    def kcal_fat(self):
        return sum(mf.kcal_fat for mf in self.mealfood_set.all())

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

    def available_action_keys(self):
        return [
            "detail",
            "fork",
            "copy",
            "add_to_dailyplan",
            "replace",
            "edit",
            "delete",
        ]

    def get_absolute_url(self):
        return reverse("meal_detail", args=[self.pk])

    def get_canonical_url(self):
        """
        Canonical (context-free) URL for this Meal.
        Do NOT use for contextual navigation.
        """
        return reverse("meal_detail", args=[self.pk])


    def get_configure_url(self):
        return reverse("configure_meal", args=[self.pk])



class MealFood(models.Model):
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)
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
        total = self.meal.total_kcal
        if total == 0:
            return 0
        return self.kcal_protein / total * 100

    @property
    def alloc_carbs(self):
        total = self.meal.total_kcal
        if total == 0:
            return 0
        return self.kcal_carbs / total * 100

    @property
    def alloc_fat(self):
        total = self.meal.total_kcal
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

    is_public = models.BooleanField(default=False)
    is_forkable = models.BooleanField(default=True)
    is_copiable = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def protein(self):
        return sum(dpm.meal.protein for dpm in self.daily_plan_meals.all())

    @property
    def carbs(self):
        return sum(dpm.meal.carbs for dpm in self.daily_plan_meals.all())

    @property
    def fat(self):
        return sum(dpm.meal.fat for dpm in self.daily_plan_meals.all())

    @property
    def kcal_protein(self):
        return sum(dpm.meal.kcal_protein for dpm in self.daily_plan_meals.all())

    @property
    def kcal_carbs(self):
        return sum(dpm.meal.kcal_carbs for dpm in self.daily_plan_meals.all())

    @property
    def kcal_fat(self):
        return sum(dpm.meal.kcal_fat for dpm in self.daily_plan_meals.all())

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
            self.daily_plan_meals
            .select_related("meal")
            .prefetch_related(
                Prefetch(
                    "meal__mealfood_set",
                    queryset=MealFood.objects.select_related("food")
                )
            )
        )
    
    def get_absolute_url(self):
        return reverse("dailyplan_detail", args=[self.pk])

    def get_configure_url(self):
        return reverse("configure_dailyplan", args=[self.pk])


class DailyPlanMeal(models.Model):
    daily_plan = models.ForeignKey(
        DailyPlan, on_delete=models.CASCADE, related_name="daily_plan_meals"
    )
    meal = models.ForeignKey(Meal, on_delete=models.CASCADE)

    note = models.CharField(max_length=255, blank=True, null=True)
    hour = models.TimeField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["hour", "order"]

    def available_action_keys(self):
        return [
            "replace_meal",
            "remove_meal",
        ]

    def __str__(self):
        return f"{self.daily_plan.name} ({self.meal.name})"


class Program(models.Model):
    name = models.CharField(max_length=100)

    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="programs"
    )

    start_date = models.DateField()
    end_date = models.DateField()

    is_public = models.BooleanField(default=False)
    is_forkable = models.BooleanField(default=True)
    is_copiable = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @property
    def protein(self):
        return sum(day.daily_plan.protein for day in self.program_days.all())

    @property
    def carbs(self):
        return sum(day.daily_plan.carbs for day in self.program_days.all())

    @property
    def fat(self):
        return sum(day.daily_plan.fat for day in self.program_days.all())

    @property
    def kcal_protein(self):
        return sum(day.daily_plan.kcal_protein for day in self.program_days.all())

    @property
    def kcal_carbs(self):
        return sum(day.daily_plan.kcal_carbs for day in self.program_days.all())

    @property
    def kcal_fat(self):
        return sum(day.daily_plan.kcal_fat for day in self.program_days.all())

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

    def get_absolute_url(self):
        return reverse("program_detail", args=[self.pk])

    def get_configure_url(self):
        return reverse("configure_program", args=[self.pk])



class ProgramDay(models.Model):
    program = models.ForeignKey(
        Program, on_delete=models.CASCADE, related_name="program_days"
    )
    daily_plan = models.ForeignKey(DailyPlan, on_delete=models.CASCADE)
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
