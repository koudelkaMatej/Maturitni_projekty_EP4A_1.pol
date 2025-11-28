/**
 * Section-by-section scroll snapping for homepage
 * Only active when html.home class is present
 */

(function () {
  // Aktivní pouze na homepage
  if (!document.documentElement.classList.contains('home')) return;

  const sections = Array.from(document.querySelectorAll('.fullpage-section'));
  if (!sections.length) return;

  // Pokud prohlížeč podporuje CSS scroll-snap, nepřidávej vlastní JS snapping
  // (náš offset 24px navíc způsoboval to, že malý kousek předchozí sekce zůstal vidět).
  if (CSS.supports('scroll-snap-type', 'y mandatory')) {
    return; // čisté CSS stačí a je přesnější
  }

  const navbarHeight = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--navbar-height')) || 72;
  let isSnapping = false;
  let scrollTimeout;

  function getNearestSection() {
    const center = window.scrollY + window.innerHeight / 2;
    let nearest = sections[0];
    let minDist = Math.abs(nearest.offsetTop - center);
    for (const s of sections) {
      const d = Math.abs(s.offsetTop - center);
      if (d < minDist) {
        minDist = d;
        nearest = s;
      }
    }
    return nearest;
  }

  function scrollToSection(section) {
    isSnapping = true;
    // Zarovnej sekci tak, aby její začátek byl přesně pod navbar (bez dodatečných offsetů)
    const targetY = section.offsetTop - navbarHeight;
    window.scrollTo({ top: targetY, behavior: 'smooth' });
    setTimeout(() => { isSnapping = false; }, 600);
  }

  function handleScroll() {
    if (isSnapping) return;
    clearTimeout(scrollTimeout);
    scrollTimeout = setTimeout(() => {
      scrollToSection(getNearestSection());
    }, 90);
  }

  if (window.innerWidth > 768) {
    window.addEventListener('scroll', handleScroll, { passive: true });
  }
})();


