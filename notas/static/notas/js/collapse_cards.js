document.addEventListener("DOMContentLoaded", function () {

  const DETAIL_SELECTORS = [
    ".card-table-foods",
    ".card-menu",
    ".card-foods-aggregation"
  ];

  function getCssTimeMs(variableName, fallbackMs) {
    const value = getComputedStyle(document.documentElement)
      .getPropertyValue(variableName)
      .trim();

    if (!value) return fallbackMs;

    if (value.endsWith("ms")) {
      return parseFloat(value);
    }

    if (value.endsWith("s")) {
      return parseFloat(value) * 1000;
    }

    const numeric = parseFloat(value);
    return Number.isNaN(numeric) ? fallbackMs : numeric;
  }

  function getBlocks(container) {
    return DETAIL_SELECTORS
      .map(selector => container.querySelector(selector))
      .filter(Boolean);
  }

  function getVisibleBlock(container) {
    return getBlocks(container).find(block => block.classList.contains("is-visible"));
  }

  function stopRunningAnimation(block) {
    block.getAnimations().forEach(animation => animation.cancel());
  }

  async function fadeOutBlock(block, duration) {
    if (!block) return;

    stopRunningAnimation(block);

    block.style.display = "block";
    block.style.opacity = "1";

    const animation = block.animate(
      [
        { opacity: 1 },
        { opacity: 0 }
      ],
      {
        duration,
        easing: "ease",
        fill: "forwards"
      }
    );

    await animation.finished;

    block.classList.remove("is-visible");
    block.style.display = "none";
    block.style.opacity = "0";
  }

  async function fadeInBlock(block, duration) {
    if (!block) return;

    stopRunningAnimation(block);

    block.classList.add("is-visible");
    block.style.display = "block";
    block.style.opacity = "0";

    const animation = block.animate(
      [
        { opacity: 0 },
        { opacity: 1 }
      ],
      {
        duration,
        easing: "ease",
        fill: "forwards"
      }
    );

    await animation.finished;

    block.style.opacity = "1";
  }

  async function activateTab(detailBlock, btn) {
    if (!detailBlock || !btn) return;
    if (detailBlock.dataset.switching === "true") return;

    const selector = btn.dataset.target;
    if (!selector) return;

    const nextBlock = detailBlock.querySelector(selector);
    if (!nextBlock) return;

    const currentBlock = getVisibleBlock(detailBlock);
    if (currentBlock === nextBlock) return;

    const tabsContainer = btn.closest(".card-detail-tabs");
    if (!tabsContainer) return;

    const buttons = tabsContainer.querySelectorAll(".btn-desplegar");
    buttons.forEach(button => button.classList.remove("is-active"));
    btn.classList.add("is-active");

    const fadeOutDuration = getCssTimeMs("--tab-fade-out-duration", 180);
    const fadeInDuration = getCssTimeMs("--tab-fade-in-duration", 220);

    detailBlock.dataset.switching = "true";

    try {
      await fadeOutBlock(currentBlock, fadeOutDuration);
      await fadeInBlock(nextBlock, fadeInDuration);
    } finally {
      detailBlock.dataset.switching = "false";
    }
  }

  function initDetailBlock(detailBlock) {
    const tabsContainer = detailBlock.querySelector(".card-detail-tabs");
    if (!tabsContainer) return;

    const buttons = tabsContainer.querySelectorAll(".btn-desplegar");
    if (!buttons.length) return;

    const blocks = getBlocks(detailBlock);

    blocks.forEach(block => {
      stopRunningAnimation(block);
      block.classList.remove("is-visible");
      block.style.display = "none";
      block.style.opacity = "0";
    });

    buttons.forEach(button => {
      button.classList.remove("is-active");
    });

    const defaultBtn =
      tabsContainer.querySelector(".btn-desplegar.is-active") || buttons[0];

    const selector = defaultBtn.dataset.target;
    const defaultBlock = detailBlock.querySelector(selector);

    defaultBtn.classList.add("is-active");

    if (defaultBlock) {
      defaultBlock.classList.add("is-visible");
      defaultBlock.style.display = "block";
      defaultBlock.style.opacity = "1";
    }

    detailBlock.dataset.switching = "false";
  }

  document.querySelectorAll(".card-detail-block").forEach(initDetailBlock);

  document.addEventListener("click", function (e) {
    const btn = e.target.closest(".btn-desplegar");
    if (!btn) return;

    const detailBlock = btn.closest(".card-detail-block");
    if (!detailBlock) return;

    activateTab(detailBlock, btn);
  });

});