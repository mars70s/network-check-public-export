function clearElement(element) {
  if (!element) {
    return;
  }
  while (element.firstChild) {
    element.removeChild(element.firstChild);
  }
}

function appendTextElement(parent, tagName, text, className) {
  const element = document.createElement(tagName);
  if (className) {
    element.className = className;
  }
  element.textContent = text;
  parent.appendChild(element);
  return element;
}

function appendBilingualText(parent, primaryText, secondaryText) {
  appendTextElement(parent, "span", primaryText, "multi-en");
  if (secondaryText) {
    appendTextElement(parent, "span", secondaryText, "multi-ja");
  }
}

function isPublicView() {
  return document.body && document.body.classList.contains("public-view");
}

function publicText(publicValue, defaultValue) {
  return isPublicView() ? publicValue : defaultValue;
}

function setStatus(primaryText, secondaryText) {
  const statusElement = document.getElementById("multi-check-status");
  if (statusElement) {
    clearElement(statusElement);
    appendBilingualText(statusElement, primaryText, secondaryText);
  }
}

function setSummary(primaryText, secondaryText) {
  const summaryElement = document.getElementById("multi-check-summary");
  if (summaryElement) {
    clearElement(summaryElement);
    if (primaryText) {
      appendBilingualText(summaryElement, primaryText, secondaryText);
    }
  }
}

function setClearVisible(visible) {
  const clearButton = document.getElementById("multi-check-clear");
  if (clearButton) {
    clearButton.hidden = !visible;
    const clearActions = clearButton.closest(".multi-clear-actions");
    if (clearActions) {
      clearActions.hidden = !visible;
    }
  }
}

function setStatusWarning(active) {
  const statusPanel = document.querySelector(".multi-status-panel");
  if (statusPanel) {
    statusPanel.classList.toggle("validation-warning", active);
  }
}

function setFormDisabled(form, disabled) {
  if (!form) {
    return;
  }
  Array.from(form.elements).forEach((element) => {
    element.disabled = disabled;
  });
}

function normalizeLevel(wrapper, result) {
  if (!wrapper || wrapper.ok === false) {
    return "failed";
  }
  if (result && typeof result.level === "string") {
    if (result.level === "good") {
      return "good";
    }
    if (result.level === "warn" || result.level === "warning") {
      return "warning";
    }
    if (result.level === "bad") {
      return "failed";
    }
  }
  return "completed";
}

function levelLabel(level) {
  if (level === "good") {
    return publicText("見つかりました", "Good");
  }
  if (level === "warning") {
    return publicText("気になる点があります", "Warning");
  }
  if (level === "failed") {
    return publicText("確認できませんでした", "Failed");
  }
  return publicText("確認しました", "Completed");
}

function addSummaryLine(lines, value) {
  if (typeof value === "string" && value.trim()) {
    lines.push(value);
  }
}

function summarizeResult(result) {
  if (!result || typeof result !== "object") {
    return [];
  }

  const lines = [];
  addSummaryLine(lines, result.status);
  addSummaryLine(lines, result.message);
  addSummaryLine(lines, result.summary);
  if (result.preference) {
    lines.push(`Preference: ${result.preference}`);
  }
  addSummaryLine(lines, result.error);
  return lines;
}

function addNamedValue(lines, label, value) {
  if (value === undefined || value === null) {
    return;
  }
  const text = String(value).trim();
  if (text) {
    lines.push(`${label}: ${text}`);
  }
}

function addArrayLine(lines, label, values) {
  if (Array.isArray(values) && values.length) {
    lines.push(`${label}: ${values.join(", ")}`);
  }
}

function formatRecord(record) {
  if (typeof record === "string") {
    return record;
  }
  if (!record || typeof record !== "object") {
    return String(record);
  }

  const parts = [];
  ["preference", "exchange", "flags", "tag", "value", "raw"].forEach((key) => {
    if (record[key] !== undefined && record[key] !== null && String(record[key]).trim()) {
      parts.push(`${key}=${record[key]}`);
    }
  });

  return parts.length ? parts.join(", ") : JSON.stringify(record);
}

function addRecordList(lines, label, records) {
  if (Array.isArray(records) && records.length) {
    lines.push(`${label}: ${records.map(formatRecord).join(" | ")}`);
  }
}

function collectRecordLines(result) {
  if (!result || typeof result !== "object") {
    return [];
  }

  const lines = [];

  addArrayLine(lines, "A", result.a_records);
  addArrayLine(lines, "AAAA", result.aaaa_records);
  addArrayLine(lines, "CNAME", result.cname_records);
  addArrayLine(lines, "NS", result.ns_records);
  addArrayLine(lines, "SOA", result.soa_records);

  addRecordList(lines, "Records", result.records);
  addRecordList(lines, "CAA", result.caa_records);

  addNamedValue(lines, "Query domain", result.query_domain);

  addNamedValue(lines, "TLS", result.tls_version);
  addNamedValue(lines, "Cipher", result.cipher);
  addNamedValue(lines, "Certificate expires", result.certificate_expires_at);
  addNamedValue(lines, "Days remaining", result.certificate_remaining_days);

  addNamedValue(lines, "HTTP version", result.http_version);
  addNamedValue(lines, "HTTP status", result.status_code);
  addNamedValue(lines, "Final URL", result.final_url);

  if (result.a_result && typeof result.a_result.elapsed_ms !== "undefined") {
    lines.push(`A timing: ${result.a_result.elapsed_ms} ms`);
    addNamedValue(lines, "A timing error", result.a_result.error);
  }
  if (result.aaaa_result && typeof result.aaaa_result.elapsed_ms !== "undefined") {
    lines.push(`AAAA timing: ${result.aaaa_result.elapsed_ms} ms`);
    addNamedValue(lines, "AAAA timing error", result.aaaa_result.error);
  }

  return lines;
}

function appendLineList(parent, heading, lines, className) {
  if (!lines.length) {
    return;
  }
  const section = document.createElement("div");
  section.className = "multi-result-section";
  appendTextElement(section, "h3", heading);
  const list = document.createElement("ul");
  list.className = className;
  lines.forEach((line) => appendTextElement(list, "li", line));
  section.appendChild(list);
  parent.appendChild(section);
}

function appendRawDetails(parent, result) {
  const details = document.createElement("details");
  details.className = "multi-details";
  const summary = document.createElement("summary");
  appendBilingualText(summary, "Raw result", "生データ");
  const raw = document.createElement("pre");
  raw.className = "mono wrap";
  raw.textContent = JSON.stringify(result, null, 2);
  details.appendChild(summary);
  details.appendChild(raw);
  parent.appendChild(details);
}

function appendBasicResultCard(resultsElement, checkId, checkLabels, level, labelText, messageText) {
  const card = document.createElement("article");
  card.className = `multi-result-card ${level}`;

  const header = document.createElement("div");
  header.className = "multi-result-header";
  appendTextElement(header, "h2", checkLabels[checkId] || checkId);
  appendTextElement(header, "span", labelText, `multi-badge ${level}`);
  card.appendChild(header);

  const message = document.createElement("p");
  message.className = "empty multi-empty-message";
  message.textContent = messageText;
  card.appendChild(message);
  resultsElement.appendChild(card);
}

function renderPendingCards(selectedChecks, checkLabels) {
  const resultsElement = document.getElementById("multi-check-results");
  if (!resultsElement) {
    return;
  }

  clearElement(resultsElement);
  selectedChecks.forEach((checkId) => {
    appendBasicResultCard(
      resultsElement,
      checkId,
      checkLabels,
      "pending",
      publicText("確認中", "Pending"),
      publicText("選んだ項目を確認しています。", "Waiting for batch response.")
    );
  });
}

function renderFailedCards(selectedChecks, checkLabels) {
  const resultsElement = document.getElementById("multi-check-results");
  if (!resultsElement) {
    return;
  }

  clearElement(resultsElement);
  selectedChecks.forEach((checkId) => {
    appendBasicResultCard(
      resultsElement,
      checkId,
      checkLabels,
      "failed",
      publicText("確認できませんでした", "Failed"),
      publicText("結果を取得できませんでした。少し時間をおいて再度お試しください。", "Batch request failed before results were returned.")
    );
  });
  setSummary(
    publicText(
      `${selectedChecks.length}件を選択、結果は取得できませんでした。`,
      `${selectedChecks.length} selected checks. 0 returned results.`
    )
  );
  setClearVisible(true);
}

function renderResults(payload, selectedChecks, checkLabels) {
  const resultsElement = document.getElementById("multi-check-results");
  if (!resultsElement) {
    return;
  }

  clearElement(resultsElement);

  selectedChecks.forEach((checkId) => {
    const wrapper = payload.results ? payload.results[checkId] : null;
    const result = wrapper ? wrapper.result : null;
    const level = normalizeLevel(wrapper, result);
    const card = document.createElement("article");
    card.className = `multi-result-card ${level}`;

    const header = document.createElement("div");
    header.className = "multi-result-header";
    appendTextElement(header, "h2", checkLabels[checkId] || checkId);
    appendTextElement(header, "span", levelLabel(level), `multi-badge ${level}`);
    card.appendChild(header);

    if (!wrapper) {
      const emptyMessage = document.createElement("p");
      emptyMessage.className = "empty multi-empty-message";
      appendBilingualText(
        emptyMessage,
        publicText("結果が返されませんでした。", "No result returned."),
        publicText("No result returned.", "結果が返されませんでした。")
      );
      card.appendChild(emptyMessage);
      resultsElement.appendChild(card);
      return;
    }

    const summaryLines = summarizeResult(result);
    const recordLines = collectRecordLines(result);
    appendLineList(
      card,
      publicText("見えたこと / What was shown", "Summary / 概要"),
      summaryLines,
      "multi-summary-list"
    );
    appendLineList(
      card,
      publicText("見えた内容 / What was found", "Key details / 主な詳細"),
      recordLines,
      "multi-key-list"
    );

    if (!summaryLines.length && !recordLines.length) {
      const emptyMessage = document.createElement("p");
      emptyMessage.className = "empty multi-empty-message";
      appendBilingualText(
        emptyMessage,
        publicText("確認しました。", "Completed."),
        publicText("Completed.", "完了しました。")
      );
      card.appendChild(emptyMessage);
    }

    appendRawDetails(card, result);
    resultsElement.appendChild(card);
  });

  const returnedCount = payload.results ? Object.keys(payload.results).length : 0;
  setSummary(
    `${selectedChecks.length} selected checks. ${returnedCount} returned results.`,
    `${selectedChecks.length}件を選択、${returnedCount}件の結果を受信しました。`
  );
  setClearVisible(true);
}

window.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("multi-check-form");
  const resultsElement = document.getElementById("multi-check-results");
  const clearButton = document.getElementById("multi-check-clear");
  let activeRunId = 0;

  if (clearButton) {
    clearButton.addEventListener("click", () => {
      activeRunId += 1;
      clearElement(resultsElement);
      setStatusWarning(false);
      setClearVisible(false);
      setStatus(
        publicText("確認したい項目を選んでから、このドメインを見るを押してください。", "Select one or more checks, then run the batch."),
        publicText("Select one or more items, then check this domain.", "1つ以上のチェックを選択してから実行してください。")
      );
      setSummary("");
    });
  }

  if (!form) {
    return;
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const domainInput = document.getElementById("multi-check-domain");
    const domain = domainInput ? domainInput.value.trim() : "";
    const selectedInputs = Array.from(form.querySelectorAll('input[name="checks"]:checked'));
    const selectedChecks = selectedInputs.map((input) => input.value);
    const checkLabels = Object.fromEntries(
      selectedInputs.map((input) => [input.value, input.dataset.label || input.value])
    );

    if (!domain) {
      setStatus(
        publicText("ドメイン名を入力してください。", "Domain is required."),
        publicText("example.com のように入力してください。", "ドメイン名を入力してください。")
      );
      setSummary("");
      setStatusWarning(true);
      return;
    }

    if (!selectedChecks.length) {
      setStatus(
        publicText("確認したい項目を1つ以上選んでください。", "Select at least one check."),
        publicText("見たい内容のカードを選択してください。", "1つ以上の確認項目を選択してください。")
      );
      setSummary("");
      setStatusWarning(true);
      return;
    }

    setStatusWarning(false);
    setClearVisible(false);
    setStatus(
      publicText("選んだ項目を確認しています。", "Running selected checks..."),
      publicText("Checking the selected items...", "選択したチェックを実行しています。")
    );
    setSummary("");
    renderPendingCards(selectedChecks, checkLabels);
    setFormDisabled(form, true);
    const runId = activeRunId + 1;
    activeRunId = runId;

    try {
      const response = await fetch(form.dataset.apiUrl, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          domain,
          checks: selectedChecks,
        }),
      });
      const payload = await response.json();

      if (runId !== activeRunId) {
        return;
      }

      if (!payload.ok) {
        setStatus(
          publicText("入力内容を確認できませんでした。", payload.error || "Request failed."),
          publicText("入力形式と選択項目を見直してください。", "リクエストに失敗しました。")
        );
        setSummary("");
        renderFailedCards(selectedChecks, checkLabels);
        return;
      }

      setStatus(
        publicText("選んだ項目の確認が完了しました。", "Completed selected checks."),
        publicText("Finished checking the selected items.", "選択したチェックが完了しました。")
      );
      renderResults(payload, selectedChecks, checkLabels);
    } catch (error) {
      if (runId !== activeRunId) {
        return;
      }
      setStatus(
        publicText("結果を取得できませんでした。", `Request failed: ${error}`),
        publicText("少し時間をおいて再度お試しください。", "リクエストに失敗しました。")
      );
      setSummary("");
      renderFailedCards(selectedChecks, checkLabels);
    } finally {
      setFormDisabled(form, false);
    }
  });
});
