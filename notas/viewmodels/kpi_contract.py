class KPIContract:
    """
    Adaptador universal → cualquier entidad nutricional
    a contrato FLAT estándar del proyecto.
    """

    def __init__(self, source, ppk=None):
        # opcional: si el servicio ya calcula ppk lo pasamos
        self.ppk = ppk

        # total kcal (dual por ahora)
        self.total_kcal = getattr(source, "total_kcal", 0)
        self.total_kcal_sql = getattr(source, "total_kcal_sql", None)

        # gramos
        self.g_protein = source.protein
        self.g_carbs = source.carbs
        self.g_fat = source.fat

        # kcal por macro
        self.kcal_protein = source.kcal_protein
        self.kcal_carbs = source.kcal_carbs
        self.kcal_fat = source.kcal_fat

        # alloc
        alloc = getattr(source, "alloc", {})
        self.alloc_protein = alloc.get("protein", 0)
        self.alloc_carbs = alloc.get("carbs", 0)
        self.alloc_fat = alloc.get("fat", 0)
