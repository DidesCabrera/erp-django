import { renderAllocBar } from "./alloc_bar_component.js";

export function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

export function roundNumber(value, fallback = 0) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return fallback;
  }

  return Math.round(number);
}

export function renderPickerResultBadges(badges = []) {
  const safeBadges = Array.isArray(badges)
    ? badges.filter((badge) => badge && badge.label)
    : [];

  if (!safeBadges.length) return "";

  return `
    <div class="picker-result-badges" aria-label="Características">
      ${safeBadges.map((badge) => `
        <span class="picker-result-badge picker-result-badge--${escapeHtml(badge.modifier || "default")}">
          ${escapeHtml(badge.label)}
        </span>
      `).join("")}
    </div>
  `;
}

export function renderPickerResultTitle({
  name,
  subtitle = "",
  icon = "",
  iconClass = "",
  badges = [],
  structuralIndicators = null,
  unitLabel = "",
}) {
  const shouldRenderStructural =
    structuralIndicators || unitLabel;

  return `
    <div class="picker-result-title">
      <div class="picker-result-title__main">
        <div class="picker-result-title__name-row">
          ${icon ? `
            <i data-lucide="${escapeHtml(icon)}" class="picker-result-title__icon ${escapeHtml(iconClass)}"></i>
          ` : ""}

          <div class="picker-result-title__name">
            ${escapeHtml(name)}
          </div>
        </div>

        ${subtitle ? `
          <div class="picker-result-title__subtitle">
            ${escapeHtml(subtitle)}
          </div>
        ` : ""}

        ${renderPickerResultBadges(badges)}
      </div>

      ${shouldRenderStructural ? `
        <div class="picker-result-structural">
          ${unitLabel ? `
            <span class="picker-result-structural__item picker-result-structural__item--unit">
              <span>${escapeHtml(unitLabel)}</span>
            </span>
          ` : ""}

          ${structuralIndicators && Number.isFinite(Number(structuralIndicators.mealsCount)) ? `
            <span class="picker-result-structural__item">
              <span>${roundNumber(structuralIndicators.mealsCount)}</span>
              <i data-lucide="utensils" class="picker-result-structural__icon"></i>
            </span>
          ` : ""}

          ${structuralIndicators && Number.isFinite(Number(structuralIndicators.foodsCount)) ? `
            <span class="picker-result-structural__item">
              <span>${roundNumber(structuralIndicators.foodsCount)}</span>
              <i data-lucide="carrot" class="picker-result-structural__icon"></i>
            </span>
          ` : ""}
        </div>
      ` : ""}
    </div>
  `;
}

export function renderPickerResultKpis({
  kcal = 0,
  protein = 0,
  carbs = 0,
  fat = 0,
  alloc = {},
  ppk = null,
}) {
  const proteinPct = Number(alloc?.protein) || 0;
  const carbsPct = Number(alloc?.carbs) || 0;
  const fatPct = Number(alloc?.fat) || 0;

  const ppkValue = Number(ppk);
  const hasPpk = Number.isFinite(ppkValue) && ppkValue > 0;

  return `
    <div class="picker-result-kpi">
      <div class="picker-result-kpi__total">
        <p>Calories</p>
        <strong>${roundNumber(kcal)}</strong>
      </div>

      <div class="picker-result-kpi__macros">

        <div class="picker-result-kpi__row">
          <div class="picker-result-kpi__label">Protein</div>

          <div class="picker-result-kpi__ppk ${hasPpk ? "" : "is-empty"}">
            ${hasPpk ? `${ppkValue.toFixed(1)}g/kg` : ""}
          </div>

          <div class="picker-result-kpi__grams">
            ${roundNumber(protein)}g
          </div>

          <div class="picker-result-kpi__alloc">
            ${renderAllocBar({ value: proteinPct, kind: "protein" })}
          </div>
        </div>

        <div class="picker-result-kpi__row">
          <div class="picker-result-kpi__label">Carbs</div>
          <div></div>

          <div class="picker-result-kpi__grams">
            ${roundNumber(carbs)}g
          </div>

          <div class="picker-result-kpi__alloc">
            ${renderAllocBar({ value: carbsPct, kind: "carbs" })}
          </div>
        </div>

        <div class="picker-result-kpi__row">
          <div class="picker-result-kpi__label">Fat</div>
          <div></div>

          <div class="picker-result-kpi__grams">
            ${roundNumber(fat)}g
          </div>

          <div class="picker-result-kpi__alloc">
            ${renderAllocBar({ value: fatPct, kind: "fat" })}
          </div>
        </div>

      </div>
    </div>
  `;
}

export function renderPickerResultFoods(foods = []) {
  const safeFoods = Array.isArray(foods)
    ? foods
        .map((food) => {
          if (!food) return "";
          if (typeof food === "string") return food;
          return food.name || food.display_name || "";
        })
        .filter(Boolean)
    : [];

  if (!safeFoods.length) return "";

  return `
    <div class="picker-result-foods">
      ${escapeHtml(safeFoods.join(", "))}
    </div>
  `;
}