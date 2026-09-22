// Scrui Content Script — Extracts full live DOM and computed metadata
(() => {
  const getFullHtml = () => {
    return document.documentElement.outerHTML;
  };

  const getMetadata = () => {
    return {
      url: window.location.href,
      title: document.title,
      html: getFullHtml(),
      viewport: {
        width: window.innerWidth,
        height: window.innerHeight,
        devicePixelRatio: window.devicePixelRatio
      },
      timestamp: Date.now()
    };
  };

  // Listen for messages from popup
  chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'extract') {
      sendResponse(getMetadata());
    }
  });
})();
