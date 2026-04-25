document.addEventListener("DOMContentLoaded", function () {
  const FADE_OUT_DURATION = 100;
  const FADE_IN_DURATION = 180;
  const MOBILE_BREAKPOINT = 980;
  const HIDDEN_PANEL_KEY = "__hidden__";

  const TAB_SELECTOR = [
    ".card-detail-tabs--desktop [data-target]",
    ".card-detail-tabs-mobile [data-target]",
    ".card-detail-tabs--desktop [data-panel-action='hide']",
    ".card-detail-tabs-mobile [data-panel-action='hide']",
  ].join(", ");

  function isMobileViewport() {
    return window.innerWidth <= MOBILE_BREAKPOINT;
  }

  function isHideButton(button) {
    return button.dataset.panelAction === "hide";
  }

  function getButtonKey(button) {
    if (isHideButton(button)) {
      return HIDDEN_PANEL_KEY;
    }

    return button.dataset.target || null;
  }

  function getButtons(detailBlock) {
    return Array.from(detailBlock.querySelectorAll(TAB_SELECTOR));
  }

  function getButtonsForViewport(detailBlock) {
    if (isMobileViewport()) {
      return Array.from(
        detailBlock.querySelectorAll(
          ".card-detail-tabs-mobile [data-target], .card-detail-tabs-mobile [data-panel-action='hide']"
        )
      );
    }

    return Array.from(
      detailBlock.querySelectorAll(
        ".card-detail-tabs--desktop [data-target], .card-detail-tabs--desktop [data-panel-action='hide']"
      )
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

  function syncHideButtonIcon(detailBlock, activeKey) {
    const hideButtons = Array.from(
      detailBlock.querySelectorAll("[data-panel-action='hide']")
    );
  
    const isHiddenState = activeKey === HIDDEN_PANEL_KEY;
    const iconName = isHiddenState ? "chevron-right" : "chevron-down";
  
    hideButtons.forEach((button) => {
      const icon = button.querySelector("[data-lucide]");
  
      if (!icon) return;
  
      icon.setAttribute("data-lucide", iconName);
    });
  
    if (window.lucide) {
      window.lucide.createIcons();
    }
  }
  
  function syncButtons(detailBlock, activeKey) {
    getButtons(detailBlock).forEach((button) => {
      button.classList.toggle("is-active", getButtonKey(button) === activeKey);
    });
  
    syncHideButtonIcon(detailBlock, activeKey);
  }

  function activateHiddenState(detailBlock) {
    if (!detailBlock) return;
    if (detailBlock.dataset.switching === "true") return;

    const currentPanel = getVisiblePanel(detailBlock);

    syncButtons(detailBlock, HIDDEN_PANEL_KEY);
    detailBlock.dataset.switching = "true";

    hidePanel(currentPanel, () => {
      detailBlock.dataset.switching = "false";
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
        (btn.dataset.target || "").includes("edit")
      );
      return editButton ? editButton.dataset.target : null;
    }

    if (requestedPanel === "nutrition") {
      const nutritionButton = buttons.find((btn) => {
        const target = btn.dataset.target || "";
        return target.includes("grid-foods") || target.includes("grid-meals");
      });

      return nutritionButton ? nutritionButton.dataset.target : null;
    }

    if (requestedPanel === "menu") {
      const menuButton = buttons.find((btn) =>
        (btn.dataset.target || "").includes("menu")
      );

      return menuButton ? menuButton.dataset.target : null;
    }

    return null;
  }

  function getDefaultKey(detailBlock) {
    const viewportButtons = getButtonsForViewport(detailBlock);
    if (!viewportButtons.length) return null;

    const requestedSelector = getRequestedSelector(detailBlock);
    if (requestedSelector) return requestedSelector;

    const activeButton =
      viewportButtons.find((button) => button.classList.contains("is-active")) ||
      viewportButtons[0];

    return activeButton ? getButtonKey(activeButton) : null;
  }

  function initDetailBlock(detailBlock) {
    const buttons = getButtons(detailBlock);
    if (!buttons.length) return;

    getPanels(detailBlock).forEach((panel) => {
      hideImmediately(panel);
    });

    const defaultKey = getDefaultKey(detailBlock);
    if (!defaultKey) return;

    syncButtons(detailBlock, defaultKey);

    if (defaultKey !== HIDDEN_PANEL_KEY) {
      const defaultPanel = detailBlock.querySelector(defaultKey);

      if (defaultPanel) {
        defaultPanel.style.display = "block";
        defaultPanel.style.opacity = "1";
        defaultPanel.classList.add("is-visible");
      }
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
    const button = event.target.closest(TAB_SELECTOR);
    if (!button) return;

    const detailBlock = button.closest(".card-detail-block");
    if (!detailBlock) return;

    if (isHideButton(button)) {
      activateHiddenState(detailBlock);
      return;
    }

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