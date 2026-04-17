// ======================================================
// dpm_food_picker.js
// Picker DPM Food
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

  const ctx = window.FOOD_PICKER_CONTEXT;
  const foods = Array.isArray(window.FOOD_PICKER_FOODS)
  ? window.FOOD_PICKER_FOODS
  : [];

  const picker = document.getElementById("food-picker");
  if (!picker) return;

  // ---------------------------
  // DOM
  // ---------------------------
  const input = document.getElementById("food-search");
  const list = document.getElementById("food-list");
  const preview = document.getElementById("food-preview");
  const quantityInput = document.getElementById("food-quantity");

  const form = document.getElementById("form-preview");

  const title = document.getElementById("food-form-title");

  const btnAdd = document.getElementById("btn-add-food");
  const btnUpdate = document.getElementById("btn-update-food");
  const btnCancel = document.getElementById("btn-cancel-edit");
  const btnCancelInline = document.getElementById("btn-cancel-picker-inline-dpm");

  const hiddenFoodId = document.getElementById("selected-food-id");
  const hiddenQuantity = document.getElementById("selected-food-quantity");

  const hiddenPickerMode = document.getElementById("food-picker-mode");
  const hiddenEditingMealfoodId = document.getElementById("editing-mealfood-id");
  const hiddenEditingOriginalQuantity = document.getElementById("editing-original-quantity");

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

  function syncHiddenState() {
    if (hiddenPickerMode) {
      hiddenPickerMode.value = ctx.mode || "add";
    }
  
    if (ctx.editing) {
      if (hiddenEditingMealfoodId) {
        hiddenEditingMealfoodId.value = String(ctx.editing.mealfood_id ?? "");
      }
      if (hiddenEditingOriginalQuantity) {
        hiddenEditingOriginalQuantity.value = String(ctx.editing.original_quantity ?? "");
      }
    } else {
      if (hiddenEditingMealfoodId) {
        hiddenEditingMealfoodId.value = "";
      }
      if (hiddenEditingOriginalQuantity) {
        hiddenEditingOriginalQuantity.value = "";
      }
    }
  }

  function setAddMode() {
    ctx.mode = "add";
    ctx.editing = null;

    title.textContent = "Agrega un Alimento";
    btnAdd.style.display = "inline-block";
    btnUpdate.style.display = "none";
    btnCancel.style.display = "inline-block";

    form.action = form.dataset.defaultAction || form.action;

    syncHiddenState();
  }

  function setEditMode({ mealfoodId, foodId, originalQuantity, updateUrl }) {
    ctx.mode = "edit";
    ctx.editing = {
      mealfood_id: Number(mealfoodId),
      food_id: Number(foodId),
      original_quantity: Number(originalQuantity)
    };
  
    title.textContent = "Edita el Alimento";
    btnAdd.style.display = "none";
    btnUpdate.style.display = "inline-block";
    btnCancel.style.display = "inline-block";
  
    form.action = updateUrl;
  
    syncHiddenState();
  }

  function resetPickerState() {
    selectedFood = null;

    hiddenFoodId.value = "";
    hiddenQuantity.value = "";

    input.value = "";
    quantityInput.value = "100";

    preview.style.display = "none";
    closeList();
  }

  function findFoodById(foodId) {
    return foods.find(food => Number(food.id) === Number(foodId)) || null;
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

    renderBase(selectedFood);

    quantityInput.value = isEdit()
      ? String(ctx.editing.original_quantity)
      : "100";

    updateQuantity();
  }

  function updateQuantity() {
    if (!selectedFood) return;

    const quantity = Number(quantityInput.value);
    if (!quantity || quantity <= 0) return;

    hiddenQuantity.value = String(quantity);

    // -------- FOOD PORTION --------
    const newPortion = portionFromFood(selectedFood, quantity);
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

    // -------- DAILYPLAN BASE --------
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

    const previewDailyPlan = previewTotals(baseDailyPlan, newPortion);

    renderDailyPlanPreview(previewDailyPlan);
    renderDpmAlloc(previewMeal, previewDailyPlan);
  }

  // ---------------------------
  // Input events
  // ---------------------------
  input.addEventListener("focus", () => {
    renderFoodList(foods);
    openList();
  });

  input.addEventListener("input", () => {
    const value = input.value.toLowerCase();

    renderFoodList(
      foods.filter(food => food.name.toLowerCase().includes(value))
    );

    openList();
  });

  quantityInput.addEventListener("input", updateQuantity);

  document.addEventListener("mousedown", event => {
    if (!picker.contains(event.target)) {
      closeList();
    }
  });

  // ---------------------------
  // Edit mode
  // ---------------------------
  document.querySelectorAll(".edit-food-btn").forEach(button => {
    button.addEventListener("click", () => {
      setEditMode({
        mealfoodId: button.dataset.id,
        foodId: button.dataset.foodId,
        originalQuantity: button.dataset.qty,
        updateUrl: button.dataset.updateUrl
      });

      document.dispatchEvent(new CustomEvent("picker:open", {
        detail: { sectionId: "dpm-picker-section" }
      }));
  
      selectedFood = findFoodById(ctx.editing.food_id);
      if (!selectedFood) return;
  
      input.value = selectedFood.name;
      showPreview();
    });
  });

  // ---------------------------
  // Cancel
  // ---------------------------
  btnCancel.addEventListener("click", () => {
    setAddMode();
    resetPickerState();

    document.dispatchEvent(new CustomEvent("picker:close", {
      detail: { sectionId: "dpm-picker-section" }
    }));
  });

  if (btnCancelInline) {
    btnCancelInline.addEventListener("click", () => {
      setAddMode();
      resetPickerState();
  
      document.dispatchEvent(new CustomEvent("picker:close", {
        detail: { sectionId: "dpm-picker-section" }
      }));
    });
  }

  // ---------------------------
  // Init
  // ---------------------------
  if (!form.dataset.defaultAction) {
    form.dataset.defaultAction = form.action;
  }

  syncHiddenState();
});