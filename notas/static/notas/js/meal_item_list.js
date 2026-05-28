import {
  renderPickerResultFoods,
  renderPickerResultKpis,
  renderPickerResultTitle,
} from "./picker_result_components.js";

function getFoodsCount(meal) {
  if (!Array.isArray(meal?.foods)) return 0;
  return meal.foods.length;
}

export function renderMealItem(meal) {
  if (!meal || !meal.name) return "";

  return `
    <div class="picker-item picker-result picker-result--meal">

      ${renderPickerResultTitle({
        name: meal.name,
        icon: "utensils",
        iconClass: "meal",
        structuralIndicators: {
          foodsCount: getFoodsCount(meal),
        },
      })}

      ${renderPickerResultKpis({
        kcal: meal.total_kcal,
        protein: meal.protein,
        carbs: meal.carbs,
        fat: meal.fat,
        alloc: meal.alloc,
        ppk: meal.ppk,
      })}

      ${renderPickerResultFoods(meal.foods)}

    </div>
  `;
}