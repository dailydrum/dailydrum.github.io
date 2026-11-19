/* Progressive enhancement: the timing marks remain useful without JavaScript. */
(() => {
  "use strict";

  let disposePage = () => {};

  function localURL(value) {
    const path = String(value || "").trim();
    if (!path || path.startsWith("//") || path.includes("\\") || /^[a-z][a-z\d+.-]*:/i.test(path)) return null;
    try {
      const url = new URL(path, window.location.href);
      return url.origin === window.location.origin && url.protocol === window.location.protocol ? url : null;
    } catch (_) {
      return null;
    }
  }

  function enhanceLanguageSelect(select) {
    const currentPath = window.location.pathname.replace(/index\.html$/, "").replace(/\/$/, "");
    const options = Array.from(select.options);
    const current = options.find((option) => {
      const url = localURL(option.value);
      return url && url.pathname.replace(/index\.html$/, "").replace(/\/$/, "") === currentPath;
    });
    // A restored page must show its own language, not the option used to leave it.
    if (current) select.value = current.value;
    const originalValue = select.value;
    for (const option of options) {
      if (!localURL(option.value)) option.disabled = true;
    }
    const onChange = () => {
      const selected = select.selectedOptions[0];
      const url = selected && !selected.disabled ? localURL(selected.value) : null;
      if (!url) {
        select.value = originalValue;
        return;
      }
      if (url.href !== window.location.href) window.location.assign(url.href);
    };
    select.addEventListener("change", onChange);
    return () => select.removeEventListener("change", onChange);
  }

  function enhanceTimingDemo(root) {
    const play = root.querySelector("[data-demo-play]");
    const reset = root.querySelector("[data-demo-reset]");
    const status = root.querySelector("[data-demo-status]");
    const beats = Array.from(root.querySelectorAll(".beat-column[data-beat]"))
      .sort((a, b) => Number(a.dataset.beat) - Number(b.dataset.beat));
    if (!play || !reset || beats.length === 0) return () => {};

    const motion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const playLabel = root.dataset.play || play.textContent;
    const resetLabel = root.dataset.reset || reset.textContent;
    const initialStatus = status ? status.textContent : "";
    if (status && !status.hasAttribute("aria-live")) status.setAttribute("aria-live", "polite");
    const timers = new Set();
    let playing = false;
    let generation = 0;

    function cancelTimers() {
      generation += 1;
      timers.forEach((timer) => window.clearTimeout(timer));
      timers.clear();
    }

    function setPlaying(value) {
      playing = value;
      root.classList.toggle("is-playing", value);
      play.disabled = value;
      play.setAttribute("aria-pressed", String(value));
      play.textContent = value ? (root.dataset.playing || playLabel) : playLabel;
      reset.disabled = false;
      reset.textContent = resetLabel;
    }

    function clearMarks() {
      beats.forEach((beat) => beat.classList.remove("is-active", "is-revealed"));
    }

    function finish() {
      cancelTimers();
      beats.forEach((beat) => {
        beat.classList.remove("is-active");
        beat.classList.add("is-revealed");
      });
      setPlaying(false);
      if (status) status.textContent = root.dataset.done || initialStatus;
    }

    function later(callback, delay) {
      const token = generation;
      const timer = window.setTimeout(() => {
        timers.delete(timer);
        if (token === generation) callback();
      }, delay);
      timers.add(timer);
    }

    function onPlay() {
      cancelTimers();
      clearMarks();
      setPlaying(true);
      if (status) status.textContent = root.dataset.playing || initialStatus;
      if (motion.matches || document.hidden) {
        finish();
        return;
      }
      // Illustration only: these fixed samples do not access audio or a microphone.
      const offsets = [-65, 0, 48, 0];
      beats.forEach((beat, index) => {
        const at = 600 * (index + 1);
        later(() => {
          beats.forEach((other) => other.classList.remove("is-active"));
          beat.classList.add("is-active");
        }, at);
        later(() => beat.classList.add("is-revealed"), at + (offsets[Number(beat.dataset.beat)] || 0));
      });
      later(finish, 600 * (beats.length + 1));
    }

    function onReset() {
      cancelTimers();
      clearMarks();
      setPlaying(false);
      if (status) status.textContent = initialStatus;
    }

    function onVisibility() {
      if (document.hidden && playing) finish();
    }

    function onMotionChange() {
      if (motion.matches && playing) finish();
    }

    // Keep the complete static example visible on first visit and browser back.
    beats.forEach((beat) => { beat.classList.remove("is-active"); beat.classList.add("is-revealed"); });
    setPlaying(false);
    play.addEventListener("click", onPlay);
    reset.addEventListener("click", onReset);
    document.addEventListener("visibilitychange", onVisibility);
    motion.addEventListener("change", onMotionChange);
    return () => {
      cancelTimers();
      beats.forEach((beat) => beat.classList.remove("is-active"));
      setPlaying(false);
      play.removeEventListener("click", onPlay);
      reset.removeEventListener("click", onReset);
      document.removeEventListener("visibilitychange", onVisibility);
      motion.removeEventListener("change", onMotionChange);
    };
  }

  function enhancePage() {
    disposePage();
    const cleanups = [
      ...Array.from(document.querySelectorAll("[data-timing-demo]"), enhanceTimingDemo),
      ...Array.from(document.querySelectorAll("[data-language-select]"), enhanceLanguageSelect),
    ];
    disposePage = () => cleanups.forEach((cleanup) => cleanup());
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", enhancePage, { once: true });
  } else {
    enhancePage();
  }
  window.addEventListener("pagehide", () => disposePage());
  window.addEventListener("pageshow", (event) => {
    if (event.persisted) enhancePage();
  });
})();
