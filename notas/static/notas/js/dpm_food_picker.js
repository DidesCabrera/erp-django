// ======================================================
// dpm_food_picker.js
// CLON funcional de food_picker + DailyPlan preview
// ======================================================

import {
  portionFromFood,
  portionFromFoodById,
  previewTotals,
  removePortionTotals
} from "./dpm_food_math.js";

import {
  renderBase,
  renderPortion,
  renderPreviewTotals,
  renderDailyPlanPreview,
  renderDpmAlloc
} from "./dpm_food_preview.js";

import { renderFoodItem } from "./food_item_list.js";

document.addEventListener("DOMContentLoaded", () => {

  const ctx   = window.FOOD_PICKER_CONTEXT;
  const foods = window.FOOD_PICKER_FOODS;

  const picker = document.getElementById("food-picker");
  if (!picker) return;

  // ---------------------------
  // DOM
  // ---------------------------
  const input         = document.getElementById("food-search");
  const list          = document.getElementById("food-list");
  const preview       = document.getElementById("food-preview");
  const quantityInput = document.getElementById("food-quantity");

  const form   = document.getElementById("form-preview");
  const mealId = form.dataset.mealId;

  const title = document.getElementById("food-form-title");

  const btnAdd    = document.getElementById("btn-add-food");
  const btnUpdate = document.getElementById("btn-update-food");
  const btnCancel = document.getElementById("btn-cancel-edit");

  const hiddenFoodId   = document.getElementById("selected-food-id");
  const hiddenQuantity = document.getElementById("selected-food-quantity");

  let selectedFood = null;

  // ---------------------------
  // Helpers
  // ---------------------------
  function isEdit() {
    return ctx.mode === "edit";
  }

  function openList() {
    list.style.display = "block";
  }

  function closeList() {
    list.style.display = "none";
  }

  // ---------------------------
  // Food list
  // ---------------------------

  function renderFoodList(items) {
    list.innerHTML = "";

    items.forEach(food => {
      if (!food || !food.name) return;

      const li = document.createElement("li");
      li.className = "food-item";

      li.innerHTML = renderFoodItem(food);

      li.addEventListener("click", () => {
        selectedFood = food;
        input.value = food.name;
        closeList();
        showPreview();
      });

      list.appendChild(li);
    });
  }

  // ---------------------------
  // Preview
  // ---------------------------
  function showPreview() {
    if (!selectedFood) return;

    preview.style.display = "block";
    document.getElementById("preview-name").textContent = selectedFood.name;

    hiddenFoodId.value = selectedFood.id;

    // BASE 100g
    renderBase(selectedFood);

    quantityInput.value = isEdit()
      ? ctx.editing.original_quantity
      : 100;

    updateQuantity();
  }

  function updateQuantity() {
    if (!selectedFood) return;

    const q = Number(quantityInput.value);
    if (!q || q <= 0) return;

    hiddenQuantity.value = q;

    // -------- FOOD PORTION --------
    const newPortion = portionFromFood(selectedFood, q);
    renderPortion(newPortion);

    // -------- MEAL BASE --------
    let baseMeal = ctx.meal.kpis;

    if (isEdit()) {
      const oldPortion = portionFromFoodById(
        foods,
        ctx.editing.food_id,
        ctx.editing.original_quantity
      );
      baseMeal = removePortionTotals(ctx.meal.kpis, oldPortion);
    }

    const previewMeal = previewTotals(baseMeal, newPortion);
    renderPreviewTotals(previewMeal);

    // -------- DAILYPLAN (DPM EXTRA) --------
    let baseDailyPlan = ctx.dailyplan.kpis;

    if (isEdit()) {
      const oldPortion = portionFromFoodById(
        foods,
        ctx.editing.food_id,
        ctx.editing.original_quantity
      );
      baseDailyPlan = removePortionTotals(
        ctx.dailyplan.kpis,
        oldPortion
      );
    }

    const previewDailyPlan = previewTotals(
      baseDailyPlan,
      newPortion
    );

    renderDailyPlanPreview(previewDailyPlan);
    renderDpmAlloc(previewMeal, previewDailyPlan);
  }

  // ---------------------------
  // Events
  // ---------------------------
  input.addEventListener("focus", () => {
    renderFoodList(foods);
    openList();
  });

  input.addEventListener("input", () => {
    const v = input.value.toLowerCase();
    renderFoodList(
      foods.filter(f => f.name.toLowerCase().includes(v))
    );
    openList();
  });

  quantityInput.addEventListener("input", updateQuantity);

  document.addEventListener("mousedown", e => {
    if (!picker.contains(e.target)) closeList();
  });

  // ---------------------------
  // EDIT MODE
  // ---------------------------
  document.querySelectorAll(".edit-food-btn").forEach(btn => {
    btn.addEventListener("click", () => {

      ctx.mode = "edit";
      ctx.editing = {
        mealfood_id: Number(btn.dataset.id),
        food_id: Number(btn.dataset.foodId),
        original_quantity: Number(btn.dataset.qty)
      };

      selectedFood = foods.find(
        f => f.id === ctx.editing.food_id
      );
      if (!selectedFood) return;

      title.textContent = "Edita el Alimento";
      btnAdd.style.display = "none";
      btnUpdate.style.display = "inline-block";
      btnCancel.style.display = "inline-block";

      form.action =
        `/meals/${mealId}/mealfoods/${ctx.editing.mealfood_id}/update/`;

      showPreview();
    });
  });

  // ---------------------------
  // CANCEL EDIT
  // ---------------------------
  btnCancel.addEventListener("click", () => {

    ctx.mode = "add";
    ctx.editing = null;

    title.textContent = "Agrega un Alimento";
    btnAdd.style.display = "inline-block";
    btnUpdate.style.display = "none";

    hiddenFoodId.value = "";
    hiddenQuantity.value = "";

    input.value = "";
    quantityInput.value = 100;

    preview.style.display = "none";
  });

});
