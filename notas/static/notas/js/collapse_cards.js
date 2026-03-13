document.addEventListener("DOMContentLoaded", function () {

  const globalBtn = document.getElementById("collapse-list-btn");
  const allTables = document.querySelectorAll(".card-table-foods");

  let allCollapsed = true;

  /* estado inicial: TODO colapsado */
  allTables.forEach((table) => {
    table.classList.add("is-collapsed");
  });

  if (globalBtn) {

    globalBtn.addEventListener("click", function () {

      allCollapsed = !allCollapsed;

      allTables.forEach((table) => {
        table.classList.toggle("is-collapsed", allCollapsed);
      });

      const iconName = allCollapsed
        ? "list-chevrons-up-down"
        : "list-chevrons-down-up";

      globalBtn.innerHTML = `
        <i data-lucide="${iconName}" class="collapse-list-icon"></i>
      `;

      lucide.createIcons();

    });

  }

  /* ============================
     INDIVIDUAL CARD BUTTONS
     ============================ */

  document.addEventListener("click", function (e) {

    const btn = e.target.closest(".btn-desplegar-tabla");
    if (!btn) return;

    const card = btn.closest(".card");
    if (!card) return;

    const table = card.querySelector(".card-table-foods");
    if (!table) return;

    table.classList.toggle("is-collapsed");

  });

});