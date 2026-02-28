document.addEventListener("DOMContentLoaded", function () {

  /* ============================
     GLOBAL BUTTON
     ============================ */

  const globalBtn = document.getElementById("collapse-list-btn");
  const allTables = document.querySelectorAll(".card-table-foods");

  let allCollapsed = true; // por defecto TODO EXPANDIDO

  if (globalBtn) {
    globalBtn.addEventListener("click", function () {

      allCollapsed = !allCollapsed;

      allTables.forEach((table) => {
        table.classList.toggle("is-collapsed", allCollapsed);
      });

      globalBtn.textContent = allCollapsed
        ? "Expand List"
        : "Collapse List";
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
