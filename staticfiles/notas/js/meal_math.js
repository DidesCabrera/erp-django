// ======================================================
// meal_math.js
// Matemática pura de KPIs (Meal / DailyPlan)
// ======================================================

/**
 * Suma dos estructuras de KPIs
 * Usado para previews
 */
 export function addKpis(base, added) {
  return {
    protein: base.protein + added.protein,
    carbs: base.carbs + added.carbs,
    fat: base.fat + added.fat,
    total_kcal: base.total_kcal + added.total_kcal,
  };
}

/**
 * Resta KPIs (EDIT mode)
 * Ej: DailyPlan - Meal original
 */
export function subtractKpis(base, removed) {
  return {
    protein: base.protein - removed.protein,
    carbs: base.carbs - removed.carbs,
    fat: base.fat - removed.fat,
    total_kcal: base.total_kcal - removed.total_kcal,
  };
}

/**
 * Calcula el % calórico de cada macro
 * Requiere KPIs normalizados (total_kcal obligatorio)
 */
export function computeAlloc(kpis) {
  const energy = kpis.total_kcal;

  if (!energy || energy <= 0) {
    return { protein: 0, carbs: 0, fat: 0 };
  }

  return {
    protein: ((kpis.protein * 4) / energy) * 100,
    carbs: ((kpis.carbs * 4) / energy) * 100,
    fat: ((kpis.fat * 9) / energy) * 100,
  };
}

export function computePPK(protein, weight) {

  if (!weight || weight <= 0) return 0;

  return protein / weight;
}

