function updateClientInfo() {
  const timezoneEl = document.getElementById("timezone");
  const screenSizeEl = document.getElementById("screen-size");

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

