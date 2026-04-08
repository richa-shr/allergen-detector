// let pollingInterval = null;
// let lastState = null;

// document.addEventListener("DOMContentLoaded", () => {
//   loadAllergens();
//   document.getElementById("save-btn").addEventListener("click", saveAllergens);
//   document.getElementById("see-alternatives-btn").addEventListener("click", showAlternatives);
//   startPolling();
// });

// function startPolling() {
//   loadResult();
//   pollingInterval = setInterval(loadResult, 2000);
// }

// function stopPolling() {
//   if (pollingInterval) {
//     clearInterval(pollingInterval);
//     pollingInterval = null;
//   }
// }

// function loadResult() {
//   chrome.storage.local.get("latest_result", (data) => {
//     const result = data.latest_result;
//     const statusEl = document.getElementById("status");
//     const substatusEl = document.getElementById("substatus");
//     const altBtn = document.getElementById("see-alternatives-btn");
//     const altEl = document.getElementById("alternatives");

//     // Reset
//     altBtn.style.display = "none";
//     altEl.style.display = "none";

//     if (!result || result.loading) {
//       statusEl.className = "loading";
//       statusEl.textContent = "⏳ Checking ingredients...";
//       substatusEl.textContent = "Please wait while we scan this product.";
//       return;
//     }

//     if (result.error) {
//       stopPolling();
//       statusEl.className = "error";
//       statusEl.textContent = "⚠️ Error";
//       substatusEl.textContent = result.error;
//       return;
//     }

//     if (result.is_safe === null) {
//       stopPolling();
//       statusEl.className = "error";
//       statusEl.textContent = "⚠️ Could not read ingredients";
//       substatusEl.textContent = "Ingredients not found on this page.";
//       return;
//     }

//     if (result.is_safe) {
//       stopPolling();
//       statusEl.className = "safe";
//       statusEl.textContent = "✅ Product is Safe!";
//       substatusEl.textContent = "No allergens detected in this product.";
//       return;
//     }

//     // Allergen found
//     statusEl.className = "unsafe";
//     statusEl.textContent = "⚠️ Allergen Detected!";

//     // Phase 1 — allergen found, searching alternatives
//     if (!result.safe_alternatives || result.safe_alternatives.length === 0) {
//       substatusEl.textContent = `Contains: ${result.allergens_found.join(", ")}. Searching for safe alternatives, please wait...`;
//       return; // keep polling
//     }

//     // Phase 2 — alternatives found
//     stopPolling();
//     substatusEl.textContent = `Contains: ${result.allergens_found.join(", ")}.`;
//     altBtn.style.display = "block";
//     altBtn.textContent = `✅ ${result.safe_alternatives.length} Safe Alternative(s) Found — Click to See`;

//     // Store for when user clicks
//     lastState = result;
//   });
// }

// function showAlternatives() {
//   if (!lastState) return;
//   const altEl = document.getElementById("alternatives");
//   altEl.style.display = "block";
//   altEl.innerHTML = "<strong style='font-size:13px;'>Safe Alternatives:</strong>";
//   lastState.safe_alternatives.forEach(alt => {
//     altEl.innerHTML += `
//       <div class="alt-item">
//         <a href="${alt.url}" target="_blank">${alt.url}</a>
//       </div>`;
//   });
//   document.getElementById("see-alternatives-btn").style.display = "none";
// }

// function saveAllergens() {
//   const input = document.getElementById("allergen-input").value;
//   const allergens = input.split(",").map(a => a.trim().toLowerCase()).filter(a => a);
//   chrome.storage.local.set({ user_allergens: allergens }, () => {
//     loadAllergens();
//     document.getElementById("allergen-input").value = "";
//   });
// }

// function loadAllergens() {
//   chrome.storage.local.get("user_allergens", (data) => {
//     const allergens = data.user_allergens || [];
//     const listEl = document.getElementById("allergen-list");
//     listEl.textContent = allergens.length > 0
//       ? "Current: " + allergens.join(", ")
//       : "No allergens saved yet.";
//   });
// }


let pollingInterval = null;
let lastState = null;
let currentJobId = null;

document.addEventListener("DOMContentLoaded", () => {
    loadAllergens();
    document.getElementById("save-btn").addEventListener("click", saveAllergens);
    document.getElementById("see-alternatives-btn").addEventListener("click", showAlternatives);
    startPolling();
});

function startPolling() {
    loadResult();
    pollingInterval = setInterval(loadResult, 3000);
}

function stopPolling() {
    if (pollingInterval) {
        clearInterval(pollingInterval);
        pollingInterval = null;
    }
}

async function loadResult() {
    const statusEl = document.getElementById("status");
    const substatusEl = document.getElementById("substatus");
    const altBtn = document.getElementById("see-alternatives-btn");
    const altEl = document.getElementById("alternatives");

    altBtn.style.display = "none";
    altEl.style.display = "none";

    // Get job_id from storage
    const data = await chrome.storage.local.get("job_id");
    const job_id = data.job_id;

    if (!job_id) {
        statusEl.className = "loading";
        statusEl.textContent = "⏳ Waiting...";
        substatusEl.textContent = "Navigate to a product page to check ingredients.";
        return;
    }

    try {
        // Poll FastAPI directly
        const response = await fetch(`http://localhost:8000/job-status/${job_id}`);
        const result = await response.json();

        if (result.status === "loading") {
            statusEl.className = "loading";
            statusEl.textContent = "⏳ Checking ingredients...";
            substatusEl.textContent = "Please wait while we scan this product.";
            return;
        }

        if (result.status === "error") {
            stopPolling();
            statusEl.className = "error";
            statusEl.textContent = "⚠️ Error";
            substatusEl.textContent = result.error;
            return;
        }

        if (result.is_safe === null) {
            stopPolling();
            statusEl.className = "error";
            statusEl.textContent = "⚠️ Could not read ingredients";
            substatusEl.textContent = "Ingredients not found on this page.";
            return;
        }

        if (result.is_safe) {
            stopPolling();
            statusEl.className = "safe";
            statusEl.textContent = "✅ Product is Safe!";
            substatusEl.textContent = "No allergens detected in this product.";
            return;
        }

        // Allergen found
        statusEl.className = "unsafe";
        statusEl.textContent = "⚠️ Allergen Detected!";

        // Phase 1 done but alternatives still loading
        if (result.status === "allergen_checked") {
            const allergenText = result.allergens_found && result.allergens_found.length > 0
                ? `Contains: ${result.allergens_found.join(", ")}. Searching for safe alternatives...`
                : "Allergen detected. Searching for safe alternatives...";
            substatusEl.textContent = allergenText;
            return; // keep polling
        }

        // Phase 2 done — show alternatives
        if (result.status === "done") {
            stopPolling();
            substatusEl.textContent = `Contains: ${result.allergens_found.join(", ")}.`;

            if (result.safe_alternatives && result.safe_alternatives.length > 0) {
                altBtn.style.display = "block";
                altBtn.textContent = `✅ ${result.safe_alternatives.length} Safe Alternative(s) Found — Click to See`;
                lastState = result;
            } else {
                substatusEl.textContent += " No safe alternatives found.";
            }
        }

    } catch (error) {
        console.error("Poll error:", error);
    }
}

function showAlternatives() {
    if (!lastState) return;
    const altEl = document.getElementById("alternatives");
    altEl.style.display = "block";
    altEl.innerHTML = "<strong style='font-size:13px;'>Safe Alternatives:</strong>";
    lastState.safe_alternatives.forEach(alt => {
        altEl.innerHTML += `
            <div class="alt-item">
                <a href="${alt.url}" target="_blank">${alt.url}</a>
            </div>`;
    });
    document.getElementById("see-alternatives-btn").style.display = "none";
}

function saveAllergens() {
    const input = document.getElementById("allergen-input").value;
    const allergens = input.split(",").map(a => a.trim().toLowerCase()).filter(a => a);
    chrome.storage.local.set({ user_allergens: allergens }, () => {
        loadAllergens();
        document.getElementById("allergen-input").value = "";
    });
}

function loadAllergens() {
    chrome.storage.local.get("user_allergens", (data) => {
        const allergens = data.user_allergens || [];
        const listEl = document.getElementById("allergen-list");
        listEl.textContent = allergens.length > 0
            ? "Current: " + allergens.join(", ")
            : "No allergens saved yet.";
    });
}