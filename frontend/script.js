const API_BASE_URL = "https://cloud-resume-func-alex26649.azurewebsites.net/api";
const VISITOR_ENDPOINT = `${API_BASE_URL}/visitor`;

async function updateVisitorCount() {
  const counterEl = document.getElementById("visitor-count");
  if (!counterEl) return;

  try {
    const response = await fetch(VISITOR_ENDPOINT, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();

    if (typeof data.count !== "number") {
      throw new Error("Invalid response shape");
    }

    counterEl.textContent = data.count.toLocaleString();
  } catch (err) {
    console.warn("Visitor counter unavailable:", err.message);
    counterEl.textContent = "—";
    counterEl.title = "Visitor counter will appear once the backend is deployed.";
  }
}

document.addEventListener("DOMContentLoaded", updateVisitorCount);