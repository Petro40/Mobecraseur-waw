document.addEventListener("DOMContentLoaded", function () {
  document.body.classList.add("is-entering");

  requestAnimationFrame(function () {
    requestAnimationFrame(function () {
      document.body.classList.remove("is-entering");
    });
  });

  document.querySelectorAll("a[href]").forEach(function (link) {
    link.addEventListener("click", function (event) {
      var href = link.getAttribute("href");

      if (!href || href.startsWith("#") || href.startsWith("mailto:") || href.startsWith("tel:")) {
        return;
      }

      if (link.target === "_blank" || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) {
        return;
      }

      event.preventDefault();
      document.body.classList.add("is-leaving");

      window.setTimeout(function () {
        window.location.href = href;
      }, 300);
    });
  });
});
