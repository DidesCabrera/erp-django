document.addEventListener("DOMContentLoaded", () => {
    const toggles = document.querySelectorAll(".js-picker-toggle");
  
    function setExpanded(toggle, isExpanded) {
      const targetId = toggle.getAttribute("aria-controls");
      if (!targetId) return;
  
      const section = document.getElementById(targetId);
      if (!section) return;
  
      section.classList.toggle("is-collapsed", !isExpanded);
      toggle.setAttribute("aria-expanded", isExpanded ? "true" : "false");
    }
  
    function toggleSection(toggle) {
      const expanded = toggle.getAttribute("aria-expanded") === "true";
      setExpanded(toggle, !expanded);
    }
  
    toggles.forEach(toggle => {
      setExpanded(toggle, false);
  
      toggle.addEventListener("click", () => {
        toggleSection(toggle);
      });
  
      toggle.addEventListener("keydown", event => {
        if (event.key === "Enter" || event.key === " ") {
          event.preventDefault();
          toggleSection(toggle);
        }
      });
    });
  
    document.addEventListener("picker:open", event => {
      const sectionId = event.detail?.sectionId;
      if (!sectionId) return;
  
      const toggle = document.querySelector(
        `.js-picker-toggle[aria-controls="${sectionId}"]`
      );
  
      if (!toggle) return;
  
      setExpanded(toggle, true);
    });
    
    document.addEventListener("picker:close", event => {
        const sectionId = event.detail?.sectionId;
        if (!sectionId) return;
      
        const toggle = document.querySelector(
          `.js-picker-toggle[aria-controls="${sectionId}"]`
        );
      
        if (!toggle) return;
      
        setExpanded(toggle, false);
      });
  });