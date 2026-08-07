function vntgToggleNav() {
  document.querySelector('.vntg-nav-pill').classList.toggle('vntg-nav-open');
}

function vntgToggleFaq(button) {
  const item = button.parentElement;
  document.querySelectorAll('.vntg-faq-item').forEach(faq => {
    if (faq !== item) faq.classList.remove('vntg-open');
  });
  item.classList.toggle('vntg-open');
}

document.addEventListener('DOMContentLoaded', () => {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('vntg-is-visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1 });

  document.querySelectorAll('.vntg-animate').forEach(el => observer.observe(el));

  document.querySelectorAll('.vntg-region-link[data-region]').forEach(link => {
    link.addEventListener('mouseenter', () => document.getElementById('region-' + link.dataset.region)?.classList.add('is-active'));
    link.addEventListener('mouseleave', () => document.getElementById('region-' + link.dataset.region)?.classList.remove('is-active'));
  });
});
