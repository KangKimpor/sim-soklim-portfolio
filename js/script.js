(function () {
  'use strict';
  document.documentElement.classList.add('js-enabled');
  var toggle = document.getElementById('navToggle');
  var panel = document.getElementById('navPanel');
  var close = document.getElementById('navClose');
  var backdrop = document.getElementById('navBackdrop');
  var main = document.getElementById('main');
  var desktop = window.matchMedia('(min-width: 1001px)');
  function setMenu(open, restoreFocus) {
    panel.hidden = !open;
    backdrop.hidden = !open;
    panel.setAttribute('aria-hidden', String(!open));
    panel.toggleAttribute('inert', !open);
    main.toggleAttribute('inert', open);
    toggle.setAttribute('aria-expanded', String(open));
    document.body.classList.toggle('menu-open', open);
    if (open) { close.focus(); }
    else if (restoreFocus) { toggle.focus(); }
  }
  toggle.addEventListener('click', function () { setMenu(panel.hidden, true); });
  close.addEventListener('click', function () { setMenu(false, true); });
  backdrop.addEventListener('click', function () { setMenu(false, true); });
  panel.addEventListener('click', function (event) {
    var link = event.target.closest('a');
    if (!link) { return; }
    setMenu(false, false);
    var href = link.getAttribute('href');
    if (href.charAt(0) === '#') {
      var target = document.getElementById(href.slice(1));
      if (target) { target.focus({ preventScroll: true }); }
    }
  });
  document.addEventListener('keydown', function (event) {
    if (panel.hidden) { return; }
    if (event.key === 'Escape') { event.preventDefault(); setMenu(false, true); return; }
    if (event.key !== 'Tab') { return; }
    var items = panel.querySelectorAll('a[href], button:not([disabled])');
    var first = items[0];
    var last = items[items.length - 1];
    var active = document.activeElement;
    if (event.shiftKey && (active === first || !panel.contains(active))) {
      event.preventDefault(); last.focus();
    } else if (!event.shiftKey && (active === last || !panel.contains(active))) {
      event.preventDefault(); first.focus();
    }
  });
  function closeOnDesktop(event) {
    if (event.matches && !panel.hidden) {
      var focused = panel.contains(document.activeElement);
      setMenu(false, false);
      if (focused) { document.querySelector('.brand').focus(); }
    }
  }
  if (desktop.addEventListener) { desktop.addEventListener('change', closeOnDesktop); }
  else { desktop.addListener(closeOnDesktop); }
  var links = document.querySelectorAll('[data-nav]');
  var sections = document.querySelectorAll('section[id]');
  function markActive(id) {
    links.forEach(function (link) {
      var active = link.getAttribute('href') === '#' + id;
      link.classList.toggle('is-active', active);
      if (active) { link.setAttribute('aria-current', 'location'); }
      else { link.removeAttribute('aria-current'); }
    });
  }
  markActive('overview');
  if ('IntersectionObserver' in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) { markActive(entry.target.id); }
      });
    }, { rootMargin: '-20% 0px -60% 0px' });
    sections.forEach(function (section) { observer.observe(section); });
  }
  document.querySelectorAll('.portrait-frame img').forEach(function (img) {
    function markMissing() { img.parentElement.classList.add('is-empty'); }
    img.addEventListener('error', markMissing);
    if (img.complete && !img.naturalWidth) { markMissing(); }
  });
  document.getElementById('year').textContent = new Date().getFullYear();
})();
