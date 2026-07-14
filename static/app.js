function normalizeCurrentPageProtocol(protocol) {
  if (!protocol) {
    return "Unavailable / 取得不可";
  }

  const normalized = String(protocol).trim().toLowerCase();

  if (normalized === "h2") {
    return "HTTP/2";
  }

  if (normalized === "h3") {
    return "HTTP/3";
  }

  if (normalized === "http/1.1" || normalized === "http/1") {
    return "HTTP/1.1";
  }

  return "Unavailable / 取得不可";
}

function detectCurrentPageProtocol() {
  try {
    if (!window.performance || !window.performance.getEntriesByType) {
      return "unavailable";
    }

    const navigationEntries = window.performance.getEntriesByType("navigation");

    if (!navigationEntries || navigationEntries.length === 0) {
      return "unavailable";
    }

    return normalizeCurrentPageProtocol(navigationEntries[0].nextHopProtocol);
  } catch (e) {
    return "unavailable";
  }
}

function updateClientInfo() {
  const timezoneEl = document.getElementById("timezone");
  const screenSizeEl = document.getElementById("screen-size");
  const currentProtocolEl = document.getElementById("current-protocol");

  if (currentProtocolEl) {
    currentProtocolEl.textContent = detectCurrentPageProtocol();
  }

  if (timezoneEl) {
    try {
      timezoneEl.textContent = Intl.DateTimeFormat().resolvedOptions().timeZone || "Unknown / 不明";
    } catch (e) {
      timezoneEl.textContent = "Unable to detect / 取得できませんでした";
    }
  }

  if (screenSizeEl) {
    const width = window.innerWidth;
    const height = window.innerHeight;
    const pixelRatio = window.devicePixelRatio || 1;
    screenSizeEl.textContent = `${width} × ${height} / DPR ${pixelRatio}`;
  }
}

window.addEventListener("DOMContentLoaded", updateClientInfo);
window.addEventListener("resize", updateClientInfo);
