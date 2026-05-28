export function renderAllocBar({ value, kind, kind2 = "" }) {
  const pct = Math.round(Number(value) || 0);
  const safeKind2 = String(kind2 || "").trim();

  return `
    <div class="picker-alloc-item">
      ${safeKind2 ? `<p class="kind2">${safeKind2}</p>` : ""}

      <div class="alloc-pct micro alloc-bar-fill--${kind}">
        <p>${pct}%</p>
      </div>

      <div
        class="alloc-bar-comp mini"
        style="--alloc: ${pct};"
      >
        <div class="alloc-bar-bg"></div>
        <div class="alloc-bar-fill alloc-bar-fill--${kind}"></div>
      </div>
    </div>
  `;
}