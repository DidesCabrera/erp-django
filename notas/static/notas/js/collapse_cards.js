document.addEventListener("DOMContentLoaded", function () {

  const globalBtn = document.getElementById("collapse-list-btn");

  const allTables = document.querySelectorAll(".card-table-foods");
  const allAggregations = document.querySelectorAll(".card-foods-aggregation");

  const allCollapsables = [
    ...allTables,
    ...allAggregations
  ];

  let allCollapsed = true;

  /* ============================
     INITIAL STATE
     ============================ */

  allCollapsables.forEach((el) => {
    el.classList.add("is-collapsed");
  });

  /* ============================
     GLOBAL BUTTON
     ============================ */

  if (globalBtn) {

    globalBtn.addEventListener("click", function () {

      allCollapsed = !allCollapsed;

      allCollapsables.forEach((el) => {
        el.classList.toggle("is-collapsed", allCollapsed);
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

    /* TABLA NUTRICIONAL */
    const btnTabla = e.target.closest(".btn-desplegar-tabla");

    if (btnTabla) {

      const card = btnTabla.closest(".card");
      if (!card) return;

      const table = card.querySelector(".card-table-foods");
      if (!table) return;

      table.classList.toggle("is-collapsed");

    }

    /* LISTA DE ALIMENTOS */
    const btnMenu = e.target.closest(".btn-desplegar-menu");

    if (btnMenu) {

      const card = btnMenu.closest(".card");
      if (!card) return;

      const aggregation = card.querySelector(".card-foods-aggregation");
      if (!aggregation) return;

      aggregation.classList.toggle("is-collapsed");

    }

  });

});