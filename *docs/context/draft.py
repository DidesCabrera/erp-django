
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



