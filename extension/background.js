// // Listen for URL from content script
// chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
//     if (message.type === "PAGE_URL") {
//       handleProductPage(message.url, sender.tab.id);
//     }
  
//     if (message.type === "GET_RESULT") {
//       // Popup is asking for the latest result
//       chrome.storage.local.get("latest_result", (data) => {
//         sendResponse(data.latest_result || null);
//       });
//       return true; // keeps message channel open for async response
//     }
//   });
  
//   async function handleProductPage(url, tabId) {
//     // Get user's allergens from storage
//     const data = await chrome.storage.local.get("user_allergens");
//     const allergens = data.user_allergens || [];
  
//     if (allergens.length === 0) {
//       chrome.storage.local.set({
//         latest_result: { error: "No allergens set. Please add your allergens first." }
//       });
//       return;
//     }
  
//     // Store loading state
//     chrome.storage.local.set({ latest_result: { loading: true } });
  
//     try {
//       const controller = new AbortController();
//       const timeoutId = setTimeout(() => controller.abort(), 300000); // 5 minutes

//       const response = await fetch("http://localhost:8000/check", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ url, allergens })
//       });
//       clearTimeout(timeoutId);
//       const result = await response.json();
  
//       // Store result so popup can read it
//       chrome.storage.local.set({ latest_result: result });
  
//     } catch (error) {
//       if (error.name === "AbortError") {
//         chrome.storage.local.set({
//             latest_result: { error: "Request timed out — scraping took too long." }
//         });
//     } else {
//       chrome.storage.local.set({
//         latest_result: { error: "Could not reach backend. Is the server running?" }
//       });
//     }
      
//     }
//   }

// Keep service worker alive during long operations (version2)



// let keepAliveInterval = null;

// function keepAlive() {
//     keepAliveInterval = setInterval(() => {
//         chrome.runtime.getPlatformInfo(() => {});
//     }, 20000); // ping every 20 seconds
// }

// function stopKeepAlive() {
//     if (keepAliveInterval) {
//         clearInterval(keepAliveInterval);
//         keepAliveInterval = null;
//     }
// }

// chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
//   if (message.type === "PAGE_URL") {
//       handleProductPage(message.url, sender.tab.id);
//   }

//   if (message.type === "GET_RESULT") {
//       chrome.storage.local.get("latest_result", (data) => {
//           sendResponse(data.latest_result || null);
//       });
//       return true;
//   }
// });

// // async function handleProductPage(url, tabId) {
// //   const data = await chrome.storage.local.get("user_allergens");
// //   const allergens = data.user_allergens || [];

// //   if (allergens.length === 0) {
// //       chrome.storage.local.set({
// //           latest_result: { error: "No allergens set. Please add your allergens first." }
// //       });
// //       return;
// //   }

// //   // Show scanning badge
// //   chrome.action.setBadgeText({ text: "...", tabId });
// //   chrome.action.setBadgeBackgroundColor({ color: "#856404", tabId });
// //   chrome.storage.local.set({ latest_result: { loading: true } });

// //   // Show scanning banner on page
// //   showBanner(tabId, "⏳ Scanning ingredients for allergens...", "#856404");

// //   try {
// //       const controller = new AbortController();
// //       const timeoutId = setTimeout(() => controller.abort(), 300000);

// //       const response = await fetch("http://localhost:8000/check", {
// //           method: "POST",
// //           headers: { "Content-Type": "application/json" },
// //           body: JSON.stringify({ url, allergens }),
// //           signal: controller.signal
// //       });

// //       clearTimeout(timeoutId);
// //       const result = await response.json();
// //       chrome.storage.local.set({ latest_result: result });

// //       if (result.is_safe === null) {
// //           chrome.action.setBadgeText({ text: "?", tabId });
// //           chrome.action.setBadgeBackgroundColor({ color: "#6c757d", tabId });
// //           showBanner(tabId, "⚠️ Could not read ingredients from this page.", "#6c757d");

// //       } else if (result.is_safe) {
// //           chrome.action.setBadgeText({ text: "✓", tabId });
// //           chrome.action.setBadgeBackgroundColor({ color: "#28a745", tabId });
// //           showBanner(tabId, "✅ Product is Safe! No allergens detected.", "#28a745");

// //       } else {
// //           chrome.action.setBadgeText({ text: "!", tabId });
// //           chrome.action.setBadgeBackgroundColor({ color: "#dc3545", tabId });

// //           // Phase 1 banner — allergen found, searching alternatives
// //           showBanner(
// //               tabId,
// //               `⚠️ Contains: ${result.allergens_found.join(", ")}. Searching for safe alternatives...`,
// //               "#dc3545",
// //               0  // 0 = don't auto-dismiss, stays until alternatives are found
// //           );

// //           // Phase 2 banner — alternatives ready
// //           if (result.safe_alternatives && result.safe_alternatives.length > 0) {
// //               showBanner(
// //                   tabId,
// //                   `⚠️ Contains: ${result.allergens_found.join(", ")}. Click the extension icon to see ${result.safe_alternatives.length} safe alternative(s).`,
// //                   "#dc3545",
// //                   8000  // stays for 8 seconds
// //               );
// //           }
// //       }

// //   } catch (error) {
// //       chrome.action.setBadgeText({ text: "!", tabId });
// //       chrome.action.setBadgeBackgroundColor({ color: "#6c757d", tabId });

// //       if (error.name === "AbortError") {
// //           showBanner(tabId, "⚠️ Scan timed out. Try again.", "#6c757d");
// //       } else {
// //           showBanner(tabId, "⚠️ Could not reach backend. Is the server running?", "#6c757d");
// //       }

// //       chrome.storage.local.set({
// //           latest_result: { error: "Could not reach backend. Is the server running?" }
// //       });
// //   }
// // }



// async function handleProductPage(url, tabId) {
//   keepAlive(); // ← start keep alive

//   const data = await chrome.storage.local.get("user_allergens");
//   const allergens = data.user_allergens || [];

//   if (allergens.length === 0) {
//       chrome.storage.local.set({
//           latest_result: { error: "No allergens set. Please add your allergens first." }
//       });
//       stopKeepAlive();
//       return;
//   }

//   chrome.storage.local.set({ latest_result: { loading: true } });
//   chrome.action.setBadgeText({ text: "...", tabId });
//   chrome.action.setBadgeBackgroundColor({ color: "#856404", tabId });

//   try {
//       const phase1Response = await fetch("http://localhost:8000/check-allergens", {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ url, allergens })
//       });
//       const phase1Result = await phase1Response.json();

//       chrome.storage.local.set({ latest_result: phase1Result });

//       if (phase1Result.is_safe) {
//           chrome.action.setBadgeText({ text: "✓", tabId });
//           chrome.action.setBadgeBackgroundColor({ color: "#28a745", tabId });
//           stopKeepAlive();
//           return;
//       }

//       chrome.action.setBadgeText({ text: "!", tabId });
//       chrome.action.setBadgeBackgroundColor({ color: "#dc3545", tabId });

//       const phase2Response = await fetch("http://localhost:8000/find-alternatives", {
//           method: "POST",
//           headers: { "Content-Type": "application/json" },
//           body: JSON.stringify({ url, allergens })
//       });
//       const phase2Result = await phase2Response.json();

//       chrome.storage.local.set({
//           latest_result: {
//               ...phase1Result,
//               safe_alternatives: phase2Result.safe_alternatives
//           }
//       });

//   } catch (error) {
//       console.error("Error:", error);
//       chrome.storage.local.set({
//           latest_result: { error: "Could not reach backend. Is the server running?" }
//       });
//   } finally {
//       stopKeepAlive(); // ← always stop keep alive when done
//   }
// }

// function showBanner(tabId, message, color, duration = 5000) {
//   chrome.scripting.executeScript({
//       target: { tabId },
//       func: (message, color, duration) => {
//           // Remove existing banner if any
//           const existing = document.getElementById("allergen-detector-banner");
//           if (existing) existing.remove();

//           const banner = document.createElement("div");
//           banner.id = "allergen-detector-banner";
//           banner.style.cssText = `
//               position: fixed;
//               top: 0;
//               left: 0;
//               right: 0;
//               z-index: 999999;
//               background: ${color};
//               color: white;
//               padding: 14px 20px;
//               font-family: Arial, sans-serif;
//               font-size: 14px;
//               font-weight: bold;
//               text-align: center;
//               box-shadow: 0 2px 8px rgba(0,0,0,0.3);
//           `;
//           banner.textContent = message;

//           // Close button
//           const closeBtn = document.createElement("span");
//           closeBtn.textContent = " ✕";
//           closeBtn.style.cssText = "cursor: pointer; margin-left: 12px; opacity: 0.8;";
//           closeBtn.onclick = () => banner.remove();
//           banner.appendChild(closeBtn);

//           document.body.prepend(banner);

//           // Auto dismiss if duration > 0
//           if (duration > 0) {
//               setTimeout(() => {
//                   if (banner.parentNode) banner.remove();
//               }, duration);
//           }
//       },
//       args: [message, color, duration]
//   });
// }



chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === "PAGE_URL") {
      startCheck(message.url, sender.tab.id);
  }
  if (message.type === "GET_JOB_ID") {
      chrome.storage.local.get("job_id", (data) => {
          sendResponse(data.job_id || null);
      });
      return true;
  }
});

async function startCheck(url, tabId) {
  const data = await chrome.storage.local.get("user_allergens");
  const allergens = data.user_allergens || [];

  if (allergens.length === 0) {
      chrome.storage.local.set({ job_id: null });
      return;
  }

  chrome.action.setBadgeText({ text: "...", tabId });
  chrome.action.setBadgeBackgroundColor({ color: "#856404", tabId });

  try {
      // Fire and forget — just get job_id back immediately
      const response = await fetch("http://localhost:8000/start-check", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url, allergens })
      });
      const { job_id } = await response.json();

      // Store job_id so popup can poll
      chrome.storage.local.set({ job_id });

  } catch (error) {
      console.error("Error starting check:", error);
      chrome.storage.local.set({ job_id: null });
  }
}