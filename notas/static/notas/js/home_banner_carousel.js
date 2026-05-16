document.addEventListener("DOMContentLoaded", () => {
  const root = document.querySelector(".home-hero-copy");
  if (!root) return;

  const carousel = root.querySelector(".js-home-banner-carousel");
  if (!carousel) return;

  const track = carousel.querySelector(".home-banner-track");
  const originalSlides = Array.from(track.querySelectorAll(".home-banner-slide"));
  const dots = Array.from(root.querySelectorAll(".js-home-banner-dot"));
  const prevBtn = root.querySelector(".js-home-banner-prev");
  const nextBtn = root.querySelector(".js-home-banner-next");

  if (!track || !originalSlides.length) return;

  const hasLoop = originalSlides.length > 1;

  let slides = originalSlides;
  let currentIndex = hasLoop ? 1 : 0;
  let intervalId = null;
  let touchStartX = 0;
  let touchEndX = 0;
  let isAnimating = false;

  if (hasLoop) {
    const firstClone = originalSlides[0].cloneNode(true);
    const lastClone = originalSlides[originalSlides.length - 1].cloneNode(true);

    firstClone.classList.add("is-clone");
    lastClone.classList.add("is-clone");

    track.insertBefore(lastClone, originalSlides[0]);
    track.appendChild(firstClone);

    slides = Array.from(track.querySelectorAll(".home-banner-slide"));
  }

  function getRealIndex(index) {
    if (!hasLoop) return index;

    if (index === 0) {
      return originalSlides.length - 1;
    }

    if (index === slides.length - 1) {
      return 0;
    }

    return index - 1;
  }

  function updateDots(index) {
    const realIndex = getRealIndex(index);

    dots.forEach((dot, i) => {
      dot.classList.toggle("is-active", i === realIndex);
    });
  }

  function updateActiveSlide(index) {
    slides.forEach((slide, i) => {
      slide.classList.toggle("is-active", i === index);
    });
  }

  function moveTo(index, shouldAnimate = true) {
    if (!shouldAnimate) {
      track.style.transition = "none";
    } else {
      track.style.transition = "";
    }

    track.style.transform = `translateX(-${index * 100}%)`;

    updateActiveSlide(index);
    updateDots(index);
    currentIndex = index;

    if (!shouldAnimate) {
      track.offsetHeight;
      track.style.transition = "";
    }
  }

  function nextSlide() {
    if (isAnimating || !hasLoop) return;

    isAnimating = true;
    moveTo(currentIndex + 1);
  }

  function prevSlide() {
    if (isAnimating || !hasLoop) return;

    isAnimating = true;
    moveTo(currentIndex - 1);
  }

  function goToSlide(realIndex) {
    if (realIndex < 0 || realIndex >= originalSlides.length) return;

    const targetIndex = hasLoop ? realIndex + 1 : realIndex;

    if (targetIndex === currentIndex) return;

    isAnimating = true;
    moveTo(targetIndex);
  }

  function startAutoPlay() {
    stopAutoPlay();

    if (!hasLoop) return;

    intervalId = window.setInterval(() => {
      nextSlide();
    }, 9000);
  }

  function stopAutoPlay() {
    if (intervalId) {
      window.clearInterval(intervalId);
      intervalId = null;
    }
  }

  track.addEventListener("transitionend", () => {
    if (!hasLoop) {
      isAnimating = false;
      return;
    }

    if (currentIndex === slides.length - 1) {
      moveTo(1, false);
    }

    if (currentIndex === 0) {
      moveTo(slides.length - 2, false);
    }

    isAnimating = false;
  });

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

  carousel.addEventListener(
    "touchstart",
    (event) => {
      touchStartX = event.changedTouches[0].clientX;
      touchEndX = touchStartX;
      stopAutoPlay();
    },
    { passive: true }
  );

  carousel.addEventListener(
    "touchmove",
    (event) => {
      touchEndX = event.changedTouches[0].clientX;
    },
    { passive: true }
  );

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

  moveTo(currentIndex, false);
  startAutoPlay();
});