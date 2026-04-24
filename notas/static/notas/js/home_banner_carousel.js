document.addEventListener("DOMContentLoaded", () => {
    const root = document.querySelector(".home-hero-copy");
    if (!root) return;
  
    const carousel = root.querySelector(".js-home-banner-carousel");
    if (!carousel) return;
  
    const slides = Array.from(root.querySelectorAll(".home-banner-slide"));
    const dots = Array.from(root.querySelectorAll(".js-home-banner-dot"));
    const prevBtn = root.querySelector(".js-home-banner-prev");
    const nextBtn = root.querySelector(".js-home-banner-next");
  
    if (!slides.length) return;
  
    let currentIndex = 0;
    let intervalId = null;
    let touchStartX = 0;
    let touchEndX = 0;
  
    function render(index) {
      slides.forEach((slide, i) => {
        slide.classList.toggle("is-active", i === index);
      });
  
      dots.forEach((dot, i) => {
        dot.classList.toggle("is-active", i === index);
      });
  
      currentIndex = index;
    }
  
    function nextSlide() {
      const nextIndex = (currentIndex + 1) % slides.length;
      render(nextIndex);
    }
  
    function prevSlide() {
      const prevIndex = (currentIndex - 1 + slides.length) % slides.length;
      render(prevIndex);
    }
  
    function goToSlide(index) {
      if (index < 0 || index >= slides.length) return;
      render(index);
    }
  
    function startAutoPlay() {
      stopAutoPlay();
      intervalId = window.setInterval(() => {
        nextSlide();
      }, 4000);
    }
  
    function stopAutoPlay() {
      if (intervalId) {
        window.clearInterval(intervalId);
        intervalId = null;
      }
    }
  
    if (nextBtn) {
      nextBtn.addEventListener("click", () => {
        nextSlide();
        startAutoPlay();
      });
    }
  
    if (prevBtn) {
      prevBtn.addEventListener("click", () => {
        prevSlide();
        startAutoPlay();
      });
    }
  
    dots.forEach((dot) => {
      dot.addEventListener("click", () => {
        const index = Number(dot.dataset.slide);
        goToSlide(index);
        startAutoPlay();
      });
    });
  
    carousel.addEventListener("mouseenter", stopAutoPlay);
    carousel.addEventListener("mouseleave", startAutoPlay);
  
    carousel.addEventListener("touchstart", (event) => {
      touchStartX = event.changedTouches[0].clientX;
      touchEndX = touchStartX;
      stopAutoPlay();
    }, { passive: true });
  
    carousel.addEventListener("touchmove", (event) => {
      touchEndX = event.changedTouches[0].clientX;
    }, { passive: true });
  
    carousel.addEventListener("touchend", () => {
      const deltaX = touchEndX - touchStartX;
      const minSwipeDistance = 50;
  
      if (Math.abs(deltaX) > minSwipeDistance) {
        if (deltaX < 0) {
          nextSlide();
        } else {
          prevSlide();
        }
      }
  
      startAutoPlay();
    });
  
    render(0);
    startAutoPlay();
  });