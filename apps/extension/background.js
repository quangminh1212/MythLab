// Clicking the toolbar icon opens the side panel; it stays open while the user browses other tabs,
// so the story keeps playing wherever they are.
chrome.runtime.onInstalled.addListener(() => {
  chrome.sidePanel.setPanelBehavior({ openPanelOnActionClick: true }).catch(() => {});
});
