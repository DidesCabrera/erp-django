// ======================================================
// meal_picker.js
// ADD / EDIT explícito vía MEAL_PICKER_CONTEXT
// ======================================================

import {
  addKpis,
  subtractKpis,
  computeAlloc,
  computePPK
} from "./meal_math.js";

import {
  renderSelectedMeal,
  renderDayPreview,
  renderFoodsAggregation
} from "./meal_preview.js";

import { renderMealItem } from "./meal_item_list.js";


document.addEventListener("DOMContentLoaded", () => {

  const ctx   = window.MEAL_PICKER_CONTEXT;
  const meals = window.MEAL_PICKER_MEALS || [];

  const picker = document.getElementById("meal-picker");
  const previewRoot = document.getElementById("dp-preview");

  if (!picker) return;

  // ---------------------------
  // DOM
  // ---------------------------

  const input      = document.getElementById("meal-search");
  const list       = document.getElementById("meal-list");
  const hidden     = document.getElementById("dp-selected-meal-id");
  const previewBox = document.getElementById("dp-preview");
  const form       = document.getElementById("dp-form");

  const hourInput  = form.querySelector('input[name="hour"]');
  const noteInput  = form.querySelector('input[name="note"]');
  const title      = document.getElementById("meal-form-title");

  const btnAdd     = document.getElementById("btn-add-meal");
  const btnUpdate  = document.getElementById("btn-update-meal");
  const btnCancel  = document.getElementById("btn-cancel-meal-edit");

  const ADD_ACTION = form.action;

  let selectedMeal = null;

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

  function enterAddMode() {
    ctx.mode = "add";
    ctx.editing = null;
    form.action = ADD_ACTION;

    btnAdd.style.display    = "inline-block";
    btnUpdate.style.display = "none";
    btnCancel.style.display = "inline-block";

    if (hourInput) hourInput.value = "";
    if (noteInput) noteInput.value = "";

    title.textContent = "Add meal";
  }

  function enterEditMode() {
    btnAdd.style.display    = "none";
    btnUpdate.style.display = "inline-block";
    btnCancel.style.display = "inline-block";
  }

  // ---------------------------
  // Meal list
  // ---------------------------

  function renderMealList(items) {

    list.innerHTML = "";

    if (!items.length) {
      list.innerHTML = `<li class="empty">No meals found</li>`;
      return;
    }

    items.forEach(meal => {

      if (!meal || !meal.name) return;

      const li = document.createElement("li");
      li.className = "food-item";

      li.innerHTML = renderMealItem(meal);

      li.addEventListener("click", () => {

        selectedMeal = meal;

        window.__DEBUG_MEAL = selectedMeal;
        console.log("__DEBUG_MEAL", window.__DEBUG_MEAL);

        hidden.value = meal.id;
        input.value  = meal.name;

        closeList();
        showPreview();

        form.classList.add("has-selection");
      });

      list.appendChild(li);
    });
  }

  // ---------------------------
  // Preview
  // ---------------------------

  function showPreview() {

    if (!selectedMeal) return;

    let basePlanKpis = ctx.dailyplan.kpis;

    if (isEdit()) {
      basePlanKpis = subtractKpis(
        ctx.dailyplan.kpis,
        ctx.editing.original_kpis
      );
    }

    const selectedMealKpis = {
      protein: selectedMeal.protein,
      carbs: selectedMeal.carbs,
      fat: selectedMeal.fat,
      total_kcal: selectedMeal.total_kcal,
    };

    const previewPlanKpis = addKpis(basePlanKpis, selectedMealKpis);

    const currentWithAlloc = {
      ...basePlanKpis,
      alloc: computeAlloc(basePlanKpis),
    };

    const previewWithAlloc = {
      ...previewPlanKpis,
      alloc: computeAlloc(previewPlanKpis),
    };
    const weight = ctx.dailyplan.kpis.weight;

    currentWithAlloc.ppk = computePPK(currentWithAlloc.protein, weight);
    previewWithAlloc.ppk = computePPK(previewWithAlloc.protein, weight);

    renderSelectedMeal(previewRoot, selectedMeal);
    renderFoodsAggregation(previewRoot, selectedMeal.foods);
    renderDayPreview(previewRoot, currentWithAlloc, previewWithAlloc, selectedMeal);



    previewBox.style.display = "block";
  }

  // ---------------------------
  // Events
  // ---------------------------

  input.addEventListener("focus", () => {
    renderMealList(meals);
    openList();
  });

  input.addEventListener("input", () => {

    if (!input.value) {

      selectedMeal = null;
      hidden.value = "";

      previewBox.style.display = "none";
      form.classList.remove("has-selection");

      enterAddMode();
    }

    const q = input.value.toLowerCase();

    renderMealList(
      meals.filter(m => m.name.toLowerCase().includes(q))
    );

    openList();
  });

  document.addEventListener("mousedown", e => {
    if (!picker.contains(e.target)) closeList();
  });

  // ---------------------------
  // EDIT / REPLACE
  // ---------------------------

  document.querySelectorAll(".edit-meal-btn").forEach(btn => {

    btn.addEventListener("click", () => {

      title.textContent = "Replace meal";

      ctx.mode = "edit";
      ctx.editing = {
        dailyplanmeal_id: Number(btn.dataset.dpmId),
        hour: btn.dataset.hour || "",
        note: btn.dataset.note || "",
        original_kpis: {
          protein: Number(btn.dataset.protein),
          carbs: Number(btn.dataset.carbs),
          fat: Number(btn.dataset.fat),
          total_kcal: Number(btn.dataset.kcal),
        }
      };

      if (hourInput) hourInput.value = ctx.editing.hour;
      if (noteInput) noteInput.value = ctx.editing.note;

      const mealId = Number(btn.dataset.mealId);

      selectedMeal = meals.find(m => m.id === mealId);
      if (!selectedMeal) return;

      hidden.value = mealId;
      input.value  = btn.dataset.mealName;

      form.action = `/dailyplans/${ctx.dailyplan.id}/meals/${ctx.editing.dailyplanmeal_id}/update/`;

      enterEditMode();
      showPreview();

      form.classList.add("has-selection");
    });
  });

  // ---------------------------
  // CANCEL EDIT
  // ---------------------------

  btnCancel.addEventListener("click", () => {

    selectedMeal = null;
    hidden.value = "";
    input.value  = "";

    previewBox.style.display = "none";
    form.classList.remove("has-selection");

    enterAddMode();
  });

  // ---------------------------
  // INITIAL MEAL FROM URL
  // ---------------------------

  const initialMealId = window.dailyplanInitialMeal;

  if (initialMealId) {

    const meal = meals.find(m => m.id === Number(initialMealId));

    if (meal) {

      selectedMeal = meal;

      hidden.value = meal.id;
      input.value  = meal.name;

      showPreview();

      form.classList.add("has-selection");

      // limpiar la URL para evitar repetir la acción al refrescar
      const url = new URL(window.location);
      url.searchParams.delete("select_meal");
      window.history.replaceState({}, "", url);
    }
  }

});
