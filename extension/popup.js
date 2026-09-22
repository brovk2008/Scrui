document.addEventListener('DOMContentLoaded', () => {
  const btn = document.getElementById('capture-btn');
  const statusEl = document.getElementById('status');
  const dotEl = document.getElementById('relay-dot');

  // Check relay server status
  fetch('http://127.0.0.1:9222/status')
    .then(res => res.json())
    .then(data => {
      dotEl.style.background = '#22c55e';
      statusEl.innerText = 'Connected to Scrui Relay daemon.';
    })
    .catch(() => {
      dotEl.style.background = '#ef4444';
      statusEl.innerHTML = '<span style="color:#ef4444;">Relay offline. Run: <br><code>scrui listen</code></span>';
    });

  btn.addEventListener('click', async () => {
    btn.disabled = true;
    statusEl.innerText = 'Extracting tab DOM...';

    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
    if (!tab) {
      statusEl.innerText = 'Error: No active tab found.';
      btn.disabled = false;
      return;
    }

    try {
      // Execute content script if not already injected
      await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        files: ['content.js']
      });

      chrome.tabs.sendMessage(tab.id, { action: 'extract' }, async (response) => {
        if (!response || !response.html) {
          statusEl.innerText = 'Extraction failed or empty.';
          btn.disabled = false;
          return;
        }

        statusEl.innerText = `Sending ${Math.round(response.html.length / 1024)} KB to relay...`;

        try {
          const res = await fetch('http://127.0.0.1:9222/relay', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(response)
          });

          const result = await res.json();
          if (result.status === 'success') {
            statusEl.innerHTML = '<span style="color:#22c55e;">✅ Cloned & Prompt Ready!</span>';
          } else {
            statusEl.innerText = 'Relay error: ' + (result.message || 'unknown');
          }
        } catch (err) {
          statusEl.innerText = 'Failed to connect to relay server: ' + err.message;
        } finally {
          btn.disabled = false;
        }
      });
    } catch (e) {
      statusEl.innerText = 'Error: ' + e.message;
      btn.disabled = false;
    }
  });
});
