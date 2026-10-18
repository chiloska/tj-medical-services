// Quote form: no backend, so build a pre-filled email to the clinic.
(function () {
  var form = document.getElementById("quote-form");
  if (!form) return;
  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!form.reportValidity()) return;
    var es = form.dataset.lang === "es";
    var d = new FormData(form);
    var lines = [
      (es ? "Nombre: " : "Name: ") + d.get("name"),
      (es ? "Correo: " : "Email: ") + d.get("email"),
      (es ? "Teléfono: " : "Phone: ") + (d.get("phone") || "-"),
      (es ? "Tratamiento: " : "Treatment: ") + d.get("treatment"),
      (es ? "Fechas: " : "Dates: ") + (d.get("dates") || "-"),
      "",
      d.get("notes") || ""
    ];
    var subject = (es ? "Solicitud de cotización: " : "Quote request: ") + d.get("treatment");
    window.location.href = "mailto:" + form.dataset.email +
      "?subject=" + encodeURIComponent(subject) +
      "&body=" + encodeURIComponent(lines.join("\n"));
  });
})();
