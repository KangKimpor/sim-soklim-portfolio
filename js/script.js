(function () {
  'use strict';

  // Mobile Drawer Navigation
  var navToggle = document.getElementById('navToggle');
  var navPanel = document.getElementById('navPanel');
  var navClose = document.getElementById('navClose');
  var navBackdrop = document.getElementById('navBackdrop');

  // `restoreFocus` is false only when the panel closes because a link inside it
  // was followed: the browser moves the sequential focus point to the target
  // section, so pulling focus back up to the burger would undo that.
  function setMenu(open, restoreFocus) {
    if (!navPanel || !navToggle) { return; }
    navPanel.classList.toggle('is-open', open);
    navPanel.setAttribute('aria-hidden', open ? 'false' : 'true');
    if (navBackdrop) {
      navBackdrop.classList.toggle('is-open', open);
    }
    // Keep off-canvas links out of tab order when closed
    if (open) {
      navPanel.removeAttribute('inert');
    } else {
      navPanel.setAttribute('inert', '');
    }
    navToggle.classList.toggle('is-open', open);
    navToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    navToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    document.body.classList.toggle('menu-open', open);

    if (open && navClose) {
      navClose.focus();
    } else if (!open && restoreFocus && navToggle) {
      navToggle.focus();
    }
  }

  if (navToggle && navPanel) {
    navToggle.addEventListener('click', function () {
      setMenu(!navPanel.classList.contains('is-open'), true);
    });
    if (navClose) {
      navClose.addEventListener('click', function () { setMenu(false, true); });
    }
    if (navBackdrop) {
      navBackdrop.addEventListener('click', function () { setMenu(false, true); });
    }

    navPanel.addEventListener('click', function (e) {
      if (e.target.closest('a')) { setMenu(false, false); }
    });

    document.addEventListener('keydown', function (e) {
      if (!navPanel.classList.contains('is-open')) { return; }

      if (e.key === 'Escape') {
        setMenu(false, true);
        return;
      }

      // Trap Tab in the open panel: the page behind it is still focusable, so
      // without this the browser would tab into content the drawer covers.
      if (e.key !== 'Tab') { return; }
      var focusables = navPanel.querySelectorAll('a[href], button:not([disabled])');
      if (!focusables.length) { return; }
      var first = focusables[0];
      var last = focusables[focusables.length - 1];
      var active = document.activeElement;

      if (e.shiftKey && (active === first || !navPanel.contains(active))) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && (active === last || !navPanel.contains(active))) {
        e.preventDefault();
        first.focus();
      }
    });
  }

  // Scroll-spy: Highlight active nav link as user scrolls
  var sections = document.querySelectorAll('section[id]');
  var navLinks = document.querySelectorAll('[data-nav]');

  if ('IntersectionObserver' in window && sections.length && navLinks.length) {
    var sectionObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) { return; }
        var target = '#' + entry.target.id;
        navLinks.forEach(function (link) {
          link.classList.toggle('is-active', link.getAttribute('href') === target);
        });
      });
    }, { rootMargin: '-40% 0px -50% 0px' });

    sections.forEach(function (section) {
      sectionObserver.observe(section);
    });
  }

  // Scroll progress: fills the 2px rule under the top bar
  var progressBar = document.getElementById('progressBar');
  if (progressBar) {
    var ticking = false;

    function drawProgress() {
      var scrollable = document.documentElement.scrollHeight - window.innerHeight;
      var ratio = scrollable > 0 ? window.pageYOffset / scrollable : 0;
      progressBar.style.width = (Math.min(Math.max(ratio, 0), 1) * 100).toFixed(2) + '%';
      ticking = false;
    }

    function requestProgress() {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(drawProgress);
      }
    }

    window.addEventListener('scroll', requestProgress, { passive: true });
    window.addEventListener('resize', requestProgress);
    drawProgress();
  }

  // Portrait fallback handler
  var portraitImgs = document.querySelectorAll('.portrait-frame img');
  portraitImgs.forEach(function (img) {
    var frame = img.closest('.portrait-frame');
    if (!frame) { return; }
    function markMissing() {
      frame.classList.add('is-empty');
    }
    img.addEventListener('error', markMissing);
    if (img.complete && img.naturalWidth === 0) {
      markMissing();
    }
  });

  // Back to Top button
  var backToTop = document.getElementById('backToTop');
  if (backToTop) {
    backToTop.addEventListener('click', function (e) {
      e.preventDefault();
      var overview = document.getElementById('overview');
      if (overview) {
        overview.scrollIntoView({ behavior: 'smooth' });
      } else {
        window.scrollTo({ top: 0, behavior: 'smooth' });
      }
      if (history.pushState) {
        history.pushState(null, null, '#overview');
      } else {
        window.location.hash = '#overview';
      }
    });
  }

  // Dynamic Year in Footer
  var yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }

})();
