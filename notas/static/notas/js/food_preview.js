// ======================================================
// food_preview.js
// Funciones dedicadas a pintar el preview en el DOM.
// (No hacen cálculos — solo reciben datos listos)
// ======================================================

import { computeAlloc } from "./food_math.js";

function setAlloc(cellId, textId, value) {
  document.getElementById(cellId)
    .style.setProperty("--alloc", value.toFixed(0));

  document.getElementById(textId).textContent =
    value.toFixed(0) + "%";
}

// -------- BASE (100 g)
export function renderBase(food) {
  const base = {
    protein: food.protein,
    carbs:   food.carbs,
    fat:     food.fat,
    total_kcal:    food.total_kcal,
  };

  const alloc = computeAlloc(base);

  document.getElementById("base-protein").textContent = base.protein.toFixed(1);
  document.getElementById("base-carbs").textContent   = base.carbs.toFixed(1);
  document.getElementById("base-fat").textContent     = base.fat.toFixed(1);
  document.getElementById("base-kcal").textContent    = base.total_kcal.toFixed(0);

  setAlloc("base-alloc-protein-cell", "base-alloc-protein-text", alloc.protein);
  setAlloc("base-alloc-carbs-cell",   "base-alloc-carbs-text",   alloc.carbs);
  setAlloc("base-alloc-fat-cell",     "base-alloc-fat-text",     alloc.fat);
}

// -------- PORCIÓN (cantidad seleccionada)
export function renderPortion(portion) {
  const alloc = computeAlloc(portion);

  document.getElementById("qty-protein").textContent = portion.protein.toFixed(1);
  document.getElementById("qty-carbs").textContent   = portion.carbs.toFixed(1);
  document.getElementById("qty-fat").textContent     = portion.fat.toFixed(1);
  document.getElementById("qty-kcal").textContent    = portion.total_kcal.toFixed(0);

  setAlloc("qty-alloc-protein-cell", "qty-alloc-protein-text", alloc.protein);
  setAlloc("qty-alloc-carbs-cell",   "qty-alloc-carbs-text",   alloc.carbs);
  setAlloc("qty-alloc-fat-cell",     "qty-alloc-fat-text",     alloc.fat);
}

// -------- MEAL ACTUAL
export function renderMeal(mealTotals) {
  const alloc = computeAlloc(mealTotals);

  document.getElementById("meal-kcal").textContent    = mealTotals.total_kcal.toFixed(0);
  document.getElementById("meal-protein").textContent = mealTotals.protein.toFixed(1);
  document.getElementById("meal-carbs").textContent   = mealTotals.carbs.toFixed(1);
  document.getElementById("meal-fat").textContent     = mealTotals.fat.toFixed(1);

  setAlloc("meal-alloc-protein-cell", "meal-alloc-protein-text", alloc.protein);
  setAlloc("meal-alloc-carbs-cell",   "meal-alloc-carbs-text",   alloc.carbs);
  setAlloc("meal-alloc-fat-cell",     "meal-alloc-fat-text",     alloc.fat);
}

// -------- PREVIEW RESULTANTE
export function renderPreviewTotals(previewTotals) {
  const alloc = computeAlloc(previewTotals);

  document.getElementById("meal-prev-kcal").textContent    = previewTotals.total_kcal.toFixed(0);
  document.getElementById("meal-prev-protein").textContent = previewTotals.protein.toFixed(1);
  document.getElementById("meal-prev-carbs").textContent   = previewTotals.carbs.toFixed(1);
  document.getElementById("meal-prev-fat").textContent     = previewTotals.fat.toFixed(1);

  setAlloc("meal-prev-alloc-protein-cell", "meal-prev-alloc-protein-text", alloc.protein);
  setAlloc("meal-prev-alloc-carbs-cell",   "meal-prev-alloc-carbs-text",   alloc.carbs);
  setAlloc("meal-prev-alloc-fat-cell",     "meal-prev-alloc-fat-text",     alloc.fat);
  const ppkNode = document.querySelector('[data-role="prev-ppk"]');

  if (ppkNode && previewTotals.ppk !== undefined) {
      ppkNode.textContent = `${previewTotals.ppk.toFixed(1)} g/kg`;
  }

}
