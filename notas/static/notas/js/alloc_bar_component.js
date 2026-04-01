export function renderAllocBar({ value, kind, kind2 }) {
  const pct = Math.round(Number(value) || 0);

  return `
    <div class="picker-alloc-item">
      <p class="kind2">${kind2}</p>

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