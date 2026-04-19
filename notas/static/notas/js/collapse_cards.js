document.addEventListener("DOMContentLoaded", function () {
  const FADE_OUT_DURATION = 100;
  const FADE_IN_DURATION = 180;
  const MOBILE_BREAKPOINT = 980;

  function isMobileViewport() {
    return window.innerWidth <= MOBILE_BREAKPOINT;
  }

  function getButtons(detailBlock) {
    return Array.from(
      detailBlock.querySelectorAll(
        ".card-detail-tabs--desktop [data-target], .card-detail-tabs-mobile [data-target]"
      )
    );
  }

  function getButtonsForViewport(detailBlock) {
    if (isMobileViewport()) {
      return Array.from(
        detailBlock.querySelectorAll(".card-detail-tabs-mobile [data-target]")
      );
    }

    return Array.from(
      detailBlock.querySelectorAll(".card-detail-tabs--desktop [data-target]")
    );
  }

  function getPanels(detailBlock) {
    const selectors = getButtons(detailBlock)
      .map((button) => button.dataset.target)
      .filter(Boolean);

    const uniqueSelectors = [...new Set(selectors)];

    return uniqueSelectors
      .map((selector) => detailBlock.querySelector(selector))
      .filter(Boolean);
  }

  function getVisiblePanel(detailBlock) {
    return getPanels(detailBlock).find((panel) =>
      panel.classList.contains("is-visible")
    );
  }

  function resetPanel(panel) {
    panel.classList.remove("is-visible", "is-fading-in", "is-fading-out");
  }

  function hideImmediately(panel) {
    resetPanel(panel);
    panel.style.display = "none";
    panel.style.opacity = "0";
  }

  function showPanel(panel) {
    resetPanel(panel);
    panel.style.display = "block";
    panel.style.opacity = "0";

    requestAnimationFrame(() => {
      panel.classList.add("is-visible", "is-fading-in");
      panel.style.opacity = "1";
    });

    window.setTimeout(() => {
      panel.classList.remove("is-fading-in");
    }, FADE_IN_DURATION);
  }

  function hidePanel(panel, callback) {
    if (!panel) {
      if (callback) callback();
      return;
    }

    resetPanel(panel);
    panel.classList.add("is-visible", "is-fading-out");
    panel.style.display = "block";
    panel.style.opacity = "1";

    requestAnimationFrame(() => {
      panel.style.opacity = "0";
    });

    window.setTimeout(() => {
      hideImmediately(panel);
      if (callback) callback();
    }, FADE_OUT_DURATION);
  }

  function syncButtons(detailBlock, selector) {
    getButtons(detailBlock).forEach((button) => {
      button.classList.toggle("is-active", button.dataset.target === selector);
    });
  }

  function activatePanel(detailBlock, selector) {
    if (!detailBlock || !selector) return;
    if (detailBlock.dataset.switching === "true") return;

    const nextPanel = detailBlock.querySelector(selector);
    if (!nextPanel) return;

    const currentPanel = getVisiblePanel(detailBlock);

    if (currentPanel === nextPanel) {
      syncButtons(detailBlock, selector);
      return;
    }

    syncButtons(detailBlock, selector);
    detailBlock.dataset.switching = "true";

    hidePanel(currentPanel, () => {
      showPanel(nextPanel);

      window.setTimeout(() => {
        detailBlock.dataset.switching = "false";
      }, FADE_IN_DURATION);
    });
  }

  function getRequestedSelector(detailBlock) {
    const params = new URLSearchParams(window.location.search);
    const requestedPanel = params.get("panel");

    if (!requestedPanel) return null;

    const buttons = getButtonsForViewport(detailBlock);

    if (requestedPanel === "edit") {
      const editButton = buttons.find((btn) =>
        btn.dataset.target.includes("edit")
      );
      return editButton ? editButton.dataset.target : null;
    }

    if (requestedPanel === "nutrition") {
      const nutritionButton = buttons.find((btn) =>
        btn.dataset.target.includes("grid-foods") ||
        btn.dataset.target.includes("grid-meals")
      );
      return nutritionButton ? nutritionButton.dataset.target : null;
    }

    if (requestedPanel === "menu") {
      const menuButton = buttons.find((btn) =>
        btn.dataset.target.includes("menu")
      );
      return menuButton ? menuButton.dataset.target : null;
    }

    return null;
  }

  function getDefaultSelector(detailBlock) {
    const viewportButtons = getButtonsForViewport(detailBlock);
    if (!viewportButtons.length) return null;

    const requestedSelector = getRequestedSelector(detailBlock);
    if (requestedSelector) return requestedSelector;

    const activeButton =
      viewportButtons.find((button) => button.classList.contains("is-active")) ||
      viewportButtons[0];

    return activeButton ? activeButton.dataset.target : null;
  }

  function initDetailBlock(detailBlock) {
    const buttons = getButtons(detailBlock);
    if (!buttons.length) return;

    getPanels(detailBlock).forEach((panel) => {
      hideImmediately(panel);
    });

    const selector = getDefaultSelector(detailBlock);
    if (!selector) return;

    const defaultPanel = detailBlock.querySelector(selector);

    syncButtons(detailBlock, selector);

    if (defaultPanel) {
      defaultPanel.style.display = "block";
      defaultPanel.style.opacity = "1";
      defaultPanel.classList.add("is-visible");
    }

    detailBlock.dataset.switching = "false";
  }

  function reinitAllDetailBlocks() {
    document.querySelectorAll(".card-detail-block").forEach((detailBlock) => {
      initDetailBlock(detailBlock);
    });
  }

  reinitAllDetailBlocks();

  document.addEventListener("click", function (event) {
    const button = event.target.closest(
      ".card-detail-tabs--desktop [data-target], .card-detail-tabs-mobile [data-target]"
    );

    if (!button) return;

    const detailBlock = button.closest(".card-detail-block");
    if (!detailBlock) return;

    activatePanel(detailBlock, button.dataset.target);
  });

  let lastIsMobile = isMobileViewport();

  window.addEventListener("resize", function () {
    const currentIsMobile = isMobileViewport();
    if (currentIsMobile === lastIsMobile) return;

    lastIsMobile = currentIsMobile;
    reinitAllDetailBlocks();
  });
});