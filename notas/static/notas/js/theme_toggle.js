(function () {
    const STORAGE_KEY = "myscoope-theme";
    const THEMES = {
      light: {
        nextTheme: "dark",
        label: "Modo oscuro",
        ariaLabel: "Cambiar a modo oscuro",
        icon: "moon",
        pressed: "false",
        isDark: false,
      },
      dark: {
        nextTheme: "light",
        label: "Modo claro",
        ariaLabel: "Cambiar a modo claro",
        icon: "sun",
        pressed: "true",
        isDark: true,
      },
    };
  
    function getCurrentTheme() {
      const current = document.documentElement.dataset.theme;
      return current === "dark" ? "dark" : "light";
    }
  
    function setTheme(theme) {
      const safeTheme = theme === "dark" ? "dark" : "light";
      document.documentElement.dataset.theme = safeTheme;
      localStorage.setItem(STORAGE_KEY, safeTheme);
      syncToggleButtons();
    }
  
    function renderIcon(container, iconName) {
      if (!container) return;
  
      container.innerHTML = `<i data-lucide="${iconName}"></i>`;
  
      if (window.lucide && typeof window.lucide.createIcons === "function") {
        window.lucide.createIcons();
      }
    }
  
    function syncToggleButton(button) {
      const currentTheme = getCurrentTheme();
      const config = THEMES[currentTheme];
  
      const label = button.querySelector("[data-theme-toggle-label]");
      const icon = button.querySelector("[data-theme-toggle-icon]");
  
      button.classList.toggle("is-dark", config.isDark);
      button.setAttribute("aria-label", config.ariaLabel);
      button.setAttribute("aria-pressed", config.pressed);
  
      if (label) {
        label.textContent = config.label;
      }
  
      renderIcon(icon, config.icon);
    }
  
    function syncToggleButtons() {
      const buttons = document.querySelectorAll("[data-theme-toggle]");
      buttons.forEach(syncToggleButton);
    }
  
    function bindToggleButtons() {
      const buttons = document.querySelectorAll("[data-theme-toggle]");
  
      buttons.forEach((button) => {
        button.addEventListener("click", () => {
          const currentTheme = getCurrentTheme();
          const nextTheme = THEMES[currentTheme].nextTheme;
          setTheme(nextTheme);
        });
      });
    }
  
    document.addEventListener("DOMContentLoaded", () => {
      syncToggleButtons();
      bindToggleButtons();
    });
  })();