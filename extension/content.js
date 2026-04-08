// Runs automatically when user is on Nykaa, Amazon or 1mg
const currentUrl = window.location.href;

// Tell background worker the current URL
chrome.runtime.sendMessage({
  type: "PAGE_URL",
  url: currentUrl
});