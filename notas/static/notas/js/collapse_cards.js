document.addEventListener("DOMContentLoaded", function () {

  const globalBtn = document.getElementById("collapse-list-btn");

  const allCollapsables = document.querySelectorAll(
    ".card-table-foods, .card-menu, .card-foods-aggregation"
  );

  let allCollapsed = true;

  /* ============================
     INITIAL STATE
     ============================ */

  allCollapsables.forEach(el => {
    el.classList.add("is-collapsed");
  });


  /* ============================
     GLOBAL BUTTON
     ============================ */

  if (globalBtn) {

    globalBtn.addEventListener("click", function () {

      allCollapsed = !allCollapsed;

      allCollapsables.forEach(el => {
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
     INDIVIDUAL BUTTONS
     ============================ */

     document.addEventListener("click", function (e) {

      const btn = e.target.closest(".btn-desplegar");
      if (!btn) return;
    
      const selector = btn.dataset.target;
      if (!selector) return;
    
      const card = btn.closest(".card");
      if (!card) return;
    
      const block = card.querySelector(selector);
      if (!block) return;
    
      const isCollapsed = block.classList.toggle("is-collapsed");
    
      btn.classList.toggle("is-open", !isCollapsed);
    
    });

});