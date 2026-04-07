document.addEventListener("DOMContentLoaded", function () {
  const FADE_OUT_DURATION = 100;
  const FADE_IN_DURATION = 180;

  function getButtons(detailBlock) {
    return Array.from(
      detailBlock.querySelectorAll(
        ".card-detail-tabs--desktop [data-target], .card-detail-tabs-mobile [data-target]"
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

  function initDetailBlock(detailBlock) {
    const buttons = getButtons(detailBlock);
    if (!buttons.length) return;

    getPanels(detailBlock).forEach((panel) => {
      hideImmediately(panel);
    });

    const defaultButton =
      detailBlock.querySelector(".card-detail-tabs--desktop .is-active[data-target]") ||
      detailBlock.querySelector(".card-detail-tabs-mobile .is-active[data-target]") ||
      buttons[0];

    const selector = defaultButton.dataset.target;
    const defaultPanel = detailBlock.querySelector(selector);

    syncButtons(detailBlock, selector);

    if (defaultPanel) {
      defaultPanel.style.display = "block";
      defaultPanel.style.opacity = "1";
      defaultPanel.classList.add("is-visible");
    }

    detailBlock.dataset.switching = "false";
  }

  document.querySelectorAll(".card-detail-block").forEach((detailBlock) => {
    initDetailBlock(detailBlock);
  });

  document.addEventListener("click", function (event) {
    const button = event.target.closest(
      ".card-detail-tabs--desktop [data-target], .card-detail-tabs-mobile [data-target]"
    );

    if (!button) return;

    const detailBlock = button.closest(".card-detail-block");
    if (!detailBlock) return;

    activatePanel(detailBlock, button.dataset.target);
  });
});