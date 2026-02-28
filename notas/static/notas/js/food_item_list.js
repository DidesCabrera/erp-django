import { getFoodKcal } from "./food_math.js";
import { renderAllocBar } from "./alloc_bar_component.js";

export function renderFoodItem(food) {
  if (!food || !food.name) return "";

  const kcal = getFoodKcal(food);

  const proteinPct = food.alloc?.protein ?? 0;
  const carbsPct   = food.alloc?.carbs ?? 0;
  const fatPct     = food.alloc?.fat ?? 0;

  return `
    <div class="picker-item">

      <div class="picker-item-header">
        <div class="picker-item-name">${food.name}</div>
        <div class="picker-item-unit">100g</div>
      </div>

      <div class="picker-item-meta">
        ${kcal} kcal ·
        P ${Math.round(food.protein ?? 0)}g ·
        C ${Math.round(food.carbs ?? 0)}g ·
        F ${Math.round(food.fat ?? 0)}g
      </div>

      <div class="picker-alloc-group"> 
        ${renderAllocBar({ value: proteinPct, kind: "protein", kind2: "P"})}
        ${renderAllocBar({ value: carbsPct,   kind: "carbs", kind2: "C"})}
        ${renderAllocBar({ value: fatPct,     kind: "fat", kind2: "F"})}
      </div>

    </div>
  `;
}
