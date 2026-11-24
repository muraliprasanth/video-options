/* Anonymous feedback box for Murali's public sites (added 2026-11-24).
   Put <section data-feedback-site="KEY"></section> where the box should be and load this file with defer.
   It sends one text message to the shared feedback API of the Watch Map project (Cloudflare D1 "mcu-feedback").
   KEY must be listed in SITES in mcu-watch-map/lib/feedback.js for this page's origin, or the API refuses it.
   Nothing about the visitor is stored here; the server keeps the text, the time and a keyed hash of the IP
   address (only to limit how often one address can post). Messages are mailed to the owner, never shown publicly. */
(function () {
  "use strict";
  var API = "https://mcu-watch-map.pages.dev/api/feedback";
  var MAX = 1000;

  function el(tag, props, style) {
    var n = document.createElement(tag);
    Object.keys(props || {}).forEach(function (k) { n[k] = props[k]; });
    Object.keys(style || {}).forEach(function (k) { n.style[k] = style[k]; });
    return n;
  }

  function mount(box) {
    var site = box.getAttribute("data-feedback-site");
    if (!site || box.getAttribute("data-feedback-ready")) return;
    box.setAttribute("data-feedback-ready", "1");
    box.style.margin = box.style.margin || "2rem auto";
    box.style.maxWidth = box.style.maxWidth || "40rem";

    var details = el("details");
    var summary = el("summary", { textContent: "Send feedback" }, { cursor: "pointer", fontWeight: "600" });
    var form = el("form", { noValidate: true }, { display: "grid", gap: "0.5rem", marginTop: "0.75rem" });
    var id = "site-feedback-text-" + site;
    var label = el("label", { htmlFor: id, textContent: "Anything you want to say: feedback, ideas, what you like or do not, or a thank-you. Anonymous, text only, no links." });
    var text = el("textarea", { id: id, name: "text", rows: 4, maxLength: MAX, required: true },
      { width: "100%", boxSizing: "border-box", font: "inherit", color: "inherit", background: "transparent", border: "1px solid currentColor", borderRadius: "6px", padding: "0.5rem" });
    /* a trap field that people never see; bots fill it in */
    var trap = el("input", { type: "text", name: "website", tabIndex: -1, autocomplete: "off" }, { position: "absolute", left: "-9999px", width: "1px", height: "1px", opacity: "0" });
    trap.setAttribute("aria-hidden", "true");
    var send = el("button", { type: "submit", textContent: "Send" },
      { justifySelf: "start", font: "inherit", color: "inherit", background: "transparent", border: "1px solid currentColor", borderRadius: "6px", padding: "0.35rem 1rem", cursor: "pointer" });
    var status = el("p", {}, { margin: "0", minHeight: "1.2em" });
    status.setAttribute("role", "status");

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var value = text.value.trim();
      if (value.length < 3) { status.textContent = "Write a little more first."; text.focus(); return; }
      send.disabled = true;
      status.textContent = "Sending…";
      fetch(API, {
        method: "POST",
        mode: "cors",
        credentials: "omit",
        referrerPolicy: "no-referrer",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ text: value, website: trap.value, site: site })
      }).then(function (r) {
        return r.json().catch(function () { return {}; }).then(function (d) { return { ok: r.ok, d: d }; });
      }).then(function (res) {
        if (res.ok) { status.textContent = "Thank you! Your message was sent."; text.value = ""; }
        else { status.textContent = (res.d && res.d.error) || "That did not work. Please try again later."; }
      }).catch(function () {
        status.textContent = "Could not reach the feedback box. Please try again later.";
      }).then(function () { send.disabled = false; });
    });

    form.appendChild(label);
    form.appendChild(text);
    form.appendChild(trap);
    form.appendChild(send);
    form.appendChild(status);
    details.appendChild(summary);
    details.appendChild(form);
    box.appendChild(details);
  }

  function start() { Array.prototype.forEach.call(document.querySelectorAll("[data-feedback-site]"), mount); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", start); else start();
})();
