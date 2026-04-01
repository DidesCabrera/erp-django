import { renderAllocBar } from "./alloc_bar_component.js";

export function renderMealItem(meal) {
  if (!meal || !meal.name) return "";

  const kcal = Math.round(Number(meal.total_kcal) || 0);
  const protein = Math.round(Number(meal.protein) || 0);
  const carbs = Math.round(Number(meal.carbs) || 0);
  const fat = Math.round(Number(meal.fat) || 0);

  const alloc = meal.alloc || {};
  const proteinPct = Number(alloc.protein) || 0;
  const carbsPct = Number(alloc.carbs) || 0;
  const fatPct = Number(alloc.fat) || 0;

  const foods = Array.isArray(meal.foods)
    ? meal.foods
        .map(food => {
          if (!food) return "";
          if (typeof food === "string") return food;
          return food.name || "";
        })
        .filter(Boolean)
        .join(" · ")
    : "";

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
        ${renderAllocBar({ value: proteinPct, kind: "protein", kind2: "P" })}
        ${renderAllocBar({ value: carbsPct, kind: "carbs", kind2: "C" })}
        ${renderAllocBar({ value: fatPct, kind: "fat", kind2: "F" })}
      </div>
    </div>
  `;
}