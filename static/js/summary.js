async function loadSummary() {
  try {
    const response = await fetch('/summary_data');
    if (!response.ok) throw new Error('Failed to load summary');

    const data = await response.json();

    document.getElementById('vipSold').textContent = data.vip_sold;
    document.getElementById('regularSold').textContent = data.regular_sold;
    document.getElementById('vipRemaining').textContent = data.vip_remaining;
    document.getElementById('regularRemaining').textContent = data.regular_remaining;
    document.getElementById('totalSold').textContent = data.total_sold;
    document.getElementById('totalRemaining').textContent = data.total_remaining;

    const status = document.getElementById('summaryStatus');
    if (status) status.textContent = "Summary updated";
  } catch (error) {
    console.error('Error loading summary:', error);
    const status = document.getElementById('summaryStatus');
    if (status) status.textContent = "Error loading summary";
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadSummary();
  setInterval(loadSummary, 5000); // auto-refresh
});

window.refreshSummary = loadSummary;
