// ======================================================
// food_math.js
// Motor matemático para Food Pickers
// ======================================================

/**
 * Suma una porción a un total de meal
 */
 export function previewTotals(current, added) {
  return {
    protein: current.protein + added.protein,
    carbs: current.carbs + added.carbs,
    fat: current.fat + added.fat,
    total_kcal: current.total_kcal + added.total_kcal,
  };
}

/**
 * Calcula la porción nutricional de un food según gramos
 */
export function portionFromFood(food, grams) {
  const factor = grams / 100;

  return {
    protein: food.protein * factor,
    carbs: food.carbs * factor,
    fat: food.fat * factor,
    total_kcal: food.total_kcal * factor,
  };
}

/**
 * Calcula una porción a partir de food_id + gramos
 * (útil en EDIT cuando el food original no es el seleccionado)
 */
export function portionFromFoodById(foods, foodId, grams) {
  const food = foods.find(f => f.id === foodId);
  if (!food) return null;

  return portionFromFood(food, grams);
}

/**
 * Resta una porción a un total de meal
 */
export function removePortionTotals(current, portion) {
  if (!portion) return current;

  return {
    protein: current.protein - portion.protein,
    carbs: current.carbs - portion.carbs,
    fat: current.fat - portion.fat,
    total_kcal: current.total_kcal - portion.total_kcal,
  };
}

/**
 * Calcula el % calórico de cada macro
 * Acepta total_kcal (nuevo) o kcal (legacy)
 */
export function computeAlloc({ protein, carbs, fat, total_kcal, kcal }) {
  const energy = total_kcal ?? kcal ?? 0;

  if (!energy || energy <= 0) {
    return { protein: 0, carbs: 0, fat: 0 };
  }

  return {
    protein: ((protein * 4) / energy) * 100,
    carbs: ((carbs * 4) / energy) * 100,
    fat: ((fat * 9) / energy) * 100,
  };
}

export function computePPK(protein, weight) {
  if (!weight || weight <= 0) return 0;
  return protein / weight;
}
