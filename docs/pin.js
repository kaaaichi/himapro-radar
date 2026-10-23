// 記事のピン留め。ブラウザの localStorage にだけ保存する(端末・ブラウザごとに別管理)。
(function () {
  var KEY = "himapro-radar-pins";

  function load() {
    try {
      var v = JSON.parse(localStorage.getItem(KEY) || "[]");
      return Array.isArray(v) ? v : [];
    } catch (e) {
      return [];
    }
  }

  function save(pins) {
    try {
      localStorage.setItem(KEY, JSON.stringify(pins));
    } catch (e) {
      // private モード等で保存できない場合は何もしない
    }
  }

  function isPinned(pins, url) {
    return pins.some(function (p) { return p.url === url; });
  }

  function text(root, sel) {
    var el = root.querySelector(sel);
    return el ? el.textContent : "";
  }

  function snapshot(article) {
    return {
      url: article.dataset.url,
      day: article.dataset.day || "",
      neta: text(article, ".neta"),
      title: text(article, "h3 a"),
      source: text(article, ".src"),
      published: text(article, ".pub"),
      summary: text(article, ".summary"),
      hook: text(article, ".hook"),
      pinnedAt: new Date().toISOString()
    };
  }

  function setButton(btn, on) {
    btn.textContent = on ? "★" : "☆";
    btn.setAttribute("aria-pressed", on ? "true" : "false");
    btn.title = on ? "ピン留めを外す" : "ピン留め";
  }

  function el(tag, cls, txt) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (txt) e.textContent = txt;
    return e;
  }

  function renderPinned(pins) {
    var box = document.getElementById("pins");
    if (!box) return;
    var sec = box.closest(".pins-sec");
    box.textContent = "";
    if (sec) sec.hidden = pins.length === 0;
    pins.slice().reverse().forEach(function (p) {
      var art = el("article", "item neta-" + (/^[SAB]$/.test(p.neta) ? p.neta : "B"));
      art.dataset.url = p.url;
      var head = el("div", "item-head");
      head.appendChild(el("span", "neta", p.neta || "B"));
      head.appendChild(el("span", "src", p.source));
      if (p.published) head.appendChild(el("time", "pub", p.published));
      var btn = el("button", "pin");
      btn.type = "button";
      setButton(btn, true);
      head.appendChild(btn);
      art.appendChild(head);
      var h3 = el("h3");
      var a = el("a", "", p.title || p.url);
      if (/^https?:\/\//.test(p.url)) a.href = p.url;
      h3.appendChild(a);
      art.appendChild(h3);
      if (p.summary) art.appendChild(el("p", "summary", p.summary));
      if (p.hook) art.appendChild(el("p", "hook", p.hook));
      if (p.day && /^\d{4}-\d{2}-\d{2}$/.test(p.day)) {
        var meta = el("p", "pin-day");
        var link = el("a", "", p.day + " のレーダー");
        link.href = "daily/" + p.day + ".html";
        meta.appendChild(link);
        art.appendChild(meta);
      }
      box.appendChild(art);
    });
  }

  function syncButtons(pins) {
    document.querySelectorAll("main > section:not(.pins-sec) article[data-url] .pin").forEach(function (btn) {
      setButton(btn, isPinned(pins, btn.closest("article").dataset.url));
    });
  }

  function refresh() {
    var pins = load();
    renderPinned(pins);
    syncButtons(pins);
  }

  document.addEventListener("click", function (ev) {
    var btn = ev.target.closest(".pin");
    if (!btn) return;
    var article = btn.closest("article[data-url]");
    if (!article || !article.dataset.url) return;
    var url = article.dataset.url;
    var pins = load();
    if (isPinned(pins, url)) {
      pins = pins.filter(function (p) { return p.url !== url; });
    } else {
      pins.push(snapshot(article));
    }
    save(pins);
    refresh();
  });

  window.addEventListener("storage", function (ev) {
    if (ev.key === KEY) refresh();
  });

  refresh();
})();
