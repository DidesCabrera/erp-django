document.addEventListener("DOMContentLoaded", () => {
    const button = document.querySelector(".js-copy-chatgpt-prompt");
    const promptTemplate = document.getElementById("sidebar-ai-prompt");
    const feedback = document.querySelector(".js-copy-chatgpt-feedback");
  
    if (!button || !promptTemplate) return;
  
    function setFeedback(message) {
      if (!feedback) return;
      feedback.textContent = message;
    }
  
    async function copyText(text) {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        return;
      }
  
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "fixed";
      textarea.style.top = "-9999px";
      textarea.style.left = "-9999px";
  
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
    }
  
    button.addEventListener("click", async () => {
      const prompt = promptTemplate.textContent.trim();
      const chatgptUrl = button.dataset.chatgptUrl || "https://chatgpt.com/";
  
      if (!prompt) {
        setFeedback("No se encontró el prompt.");
        return;
      }
  
      try {
        await copyText(prompt);
  
        setFeedback("Prompt copiado. Pégalo en ChatGPT.");
  
        const openedWindow = window.open(chatgptUrl, "_blank", "noopener,noreferrer");
  
        if (!openedWindow) {
          setFeedback("Prompt copiado. Abre ChatGPT y pégalo manualmente.");
        }
      } catch (error) {
        setFeedback("No se pudo copiar. Inténtalo manualmente.");
        console.error("Could not copy ChatGPT prompt:", error);
      }
    });
  });