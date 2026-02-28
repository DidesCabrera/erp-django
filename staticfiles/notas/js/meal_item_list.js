import { renderAllocBar } from "./alloc_bar_component.js";

export function renderMealItem(meal) {
  if (!meal || !meal.name) return "";

  const kcal = Math.round(meal.total_kcal ?? 0);

  const protein = Math.round(meal.protein ?? 0);
  const carbs   = Math.round(meal.carbs ?? 0);
  const fat     = Math.round(meal.fat ?? 0);

  const alloc = meal.alloc || {};
  const proteinPct = Number(alloc.protein) || 0;
  const carbsPct   = Number(alloc.carbs)   || 0;
  const fatPct     = Number(alloc.fat)     || 0;

  // 🔥 FOODS PROJECTION
  const foods = (meal.foods || [])
      .map(f => f.name)
      .join(" · ");

  return `
    <div class="picker-item">

      <div class="picker-item-header">
        <div class="picker-item-name">${meal.name}</div>
      </div>

      <div class="picker-item-meta">
        ${kcal} kcal ·
        P ${protein}g ·
        C ${carbs}g ·
        F ${fat}g
      </div>

      ${
        foods
          ? `<div class="picker-item-foods">${foods}</div>`
          : ""
      }

      <div class="picker-alloc-group"> 
        ${renderAllocBar({ value: proteinPct, kind: "protein", kind2: "P"})}
        ${renderAllocBar({ value: carbsPct,   kind: "carbs", kind2: "C"})}
        ${renderAllocBar({ value: fatPct,     kind: "fat", kind2: "F"})}
      </div>

    </div>
  `;
}
