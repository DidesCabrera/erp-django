import { getFoodKcal } from "./food_math.js";
import { renderAllocBar } from "./alloc_bar_component.js";

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function normalizeSourceLabel(source) {
  if (!source) return "";

  const normalized = String(source).toLowerCase();

  if (normalized === "usda") return "USDA";
  if (normalized === "open_food_facts") return "Open Food Facts";
  if (normalized === "latinfoods") return "LATINFOODS";
  if (normalized === "inta_chile") return "INTA Chile";
  if (normalized === "manual") return "Manual";
  if (normalized === "global") return "Global";
  if (normalized === "system") return "Sistema";
  if (normalized === "user") return "Usuario";

  return String(source)
    .replaceAll("_", " ")
    .replace(/\b\w/g, char => char.toUpperCase());
}

function resolvePrimaryBadge(food) {
  if (food?.is_user_food) {
    return {
      label: food.picker_label || "Tu alimento",
      modifier: "user"
    };
  }

  if (food?.is_global_food) {
    return {
      label: food.picker_label || "Global",
      modifier: "global"
    };
  }

  if (food?.picker_label) {
    return {
      label: food.picker_label,
      modifier: "system"
    };
  }

  return null;
}

function buildBadges(food) {
  const badges = [];

  const primaryBadge = resolvePrimaryBadge(food);
  if (primaryBadge) {
    badges.push(primaryBadge);
  }

  if (food?.is_verified) {
    badges.push({
      label: "Verificado",
      modifier: "verified"
    });
  }

  const sourceLabel = normalizeSourceLabel(food?.source);
  const shouldShowSource =
    sourceLabel &&
    !["Usuario", "Global", "Sistema"].includes(sourceLabel);

  if (shouldShowSource) {
    badges.push({
      label: sourceLabel,
      modifier: "source"
    });
  }

  if (food?.visibility === "core") {
    badges.push({
      label: "Core",
      modifier: "core"
    });
  }

  return badges;
}

function renderFoodBadges(food) {
  const badges = buildBadges(food);

  if (!badges.length) return "";

  return `
    <div class="picker-item-badges" aria-label="Características del alimento">
      ${badges.map(badge => `
        <span class="picker-item-badge picker-item-badge--${escapeHtml(badge.modifier)}">
          ${escapeHtml(badge.label)}
        </span>
      `).join("")}
    </div>
  `;
}

export function renderFoodItem(food) {
  if (!food || !food.name) return "";

  const kcal = getFoodKcal(food);

  const proteinPct = food.alloc?.protein ?? 0;
  const carbsPct = food.alloc?.carbs ?? 0;
  const fatPct = food.alloc?.fat ?? 0;

  return `
    <div class="picker-item">

      <div class="picker-item-header">
        <div class="picker-item-name">${escapeHtml(food.name)}</div>
        <div class="picker-item-unit">100g</div>
      </div>

      ${renderFoodBadges(food)}

      <div class="picker-item-meta">
        ${kcal} kcal ·
        P ${Math.round(food.protein ?? 0)}g ·
        C ${Math.round(food.carbs ?? 0)}g ·
        F ${Math.round(food.fat ?? 0)}g
      </div>

      <div class="picker-alloc-group">
        ${renderAllocBar({ value: proteinPct, kind: "protein", kind2: "P" })}
        ${renderAllocBar({ value: carbsPct, kind: "carbs", kind2: "C" })}
        ${renderAllocBar({ value: fatPct, kind: "fat", kind2: "F" })}
      </div>

    </div>
  `;
}