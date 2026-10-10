// ============================================================
// Configuration
// Replace API_BASE_URL with your Azure Function URL once deployed.
// Example: "https://my-resume-api.azurewebsites.net/api"
// ============================================================
const API_BASE_URL = "https://cloud-resume-func-alex26649.azurewebsites.net/api";
const VISITOR_ENDPOINT = `${API_BASE_URL}/visitor`;

// ============================================================
// Visitor Counter
// Fetches the current count from the Azure Function and
// updates the DOM. Fails gracefully if the API is unreachable.
// ============================================================
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
    // Backend not deployed yet, or CORS/network issue.
    console.warn("Visitor counter unavailable:", err.message);
    counterEl.textContent = "—";
    counterEl.title = "Visitor counter will appear once the backend is deployed.";
  }
}

// ============================================================
// Init
// ============================================================
document.addEventListener("DOMContentLoaded", updateVisitorCount);