let marketData = [];
let priceChart, dominanceChart;
let rotationIndex = 0;
let rotationTimer;

document.addEventListener("DOMContentLoaded", () => {
  initApp();
  setupEventListeners();
});

async function initApp() {
  await fetchSummary();
  await fetchMarketData();
}

function setupEventListeners() {
  document.getElementById("refreshBtn").addEventListener("click", initApp);
  document
    .getElementById("coinSearch")
    .addEventListener("input", (e) => handleSearch(e.target.value));

  // Sidebar Navigation
  const navLinks = document.querySelectorAll('#sidebar-nav a');
  navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
      e.preventDefault();
      const viewName = link.getAttribute('data-view');
      if (viewName) switchView(viewName);
    });
  });

  // Auto refresh every 60 seconds
  setInterval(initApp, 60000);

  // Modal close
  document.querySelector(".close").onclick = () => {
    document.getElementById("coinModal").style.display = "none";
  };

  window.onclick = (event) => {
    if (event.target == document.getElementById("coinModal")) {
      document.getElementById("coinModal").style.display = "none";
    }
  };
}

async function fetchSummary() {
  try {
    const response = await fetch("/api/summary");
    const data = await response.json();

    if (data.error) return;

    document.getElementById("val-market-cap").innerText =
      `$${(data.total_market_cap / 1e12).toFixed(2)}T`;
    document.getElementById("val-top-gainer").innerText =
      data.highest_gainer.symbol.toUpperCase();
    document.getElementById("delta-top-gainer").innerText =
      `+${data.highest_gainer.price_change_24h.toFixed(2)}%`;

    document.getElementById("val-volatility").innerText =
      data.most_volatile.symbol.toUpperCase();
    document.getElementById("delta-volatility").innerText =
      `Impact: ${data.most_volatile.volatility_score.toLocaleString()}`;

    document.getElementById("val-avg-price").innerText =
      `$${data.avg_price.toLocaleString()}`;

    const lastSync = new Date(data.last_updated);
    document.getElementById("lastUpdated").innerText =
      `Last sync: ${lastSync.toLocaleTimeString()}`;
  } catch (err) {
    console.error("Error fetching summary:", err);
  }
}

async function fetchMarketData() {
  try {
    const response = await fetch("/api/market-data");
    marketData = await response.json();

    if (marketData.error) return;

    renderTable(marketData);
    updateCharts(marketData);
        
    // Start or Reset Rotation
    startRotation();
  } catch (err) {
    console.error("Error fetching market data:", err);
  }
}

function renderTable(data) {
  const body = document.getElementById("assetBody");
  body.innerHTML = "";

  data.forEach((coin, index) => {
    const tr = document.createElement("tr");
    const deltaClass = coin.price_change_24h >= 0 ? "positive" : "negative";

    tr.innerHTML = `
            <td>${index + 1}</td>
            <td>
                <div class="coin-name">
                    <span>${coin.name}</span>
                    <span class="coin-symbol">${coin.symbol.toUpperCase()}</span>
                </div>
            </td>
            <td>$${coin.current_price.toLocaleString()}</td>
            <td class="delta ${deltaClass}">${coin.price_change_24h.toFixed(2)}%</td>
            <td>$${(coin.market_cap / 1e9).toFixed(2)}B</td>
            <td>$${(coin.total_volume / 1e6).toFixed(1)}M</td>
            <td><button class="btn-view" onclick="showDetail('${coin.coin_id}')">View</button></td>
        `;
    body.appendChild(tr);
  });
}

function startRotation() {
    if (rotationTimer) clearInterval(rotationTimer);
    updateRotatingCards();
    rotationTimer = setInterval(() => {
        rotationIndex = (rotationIndex + 1) % marketData.length;
        updateRotatingCards();
    }, 30000);
}

function updateRotatingCards() {
    if (marketData.length === 0) return;
    
    const coin = marketData[rotationIndex];
    const topGainer = [...marketData].sort((a,b) => b.price_change_24h - a.price_change_24h)[0];
    const mostVolatile = [...marketData].sort((a,b) => b.volatility_score - a.volatility_score)[0];

    // Card 2: Spotlight (Cycling every coin)
    const spotlightCard = document.getElementById('kpi-top-gainer');
    const spotlightHeader = spotlightCard.querySelector('.title');
    spotlightHeader.innerHTML = `Spotlight: ${coin.name}`;
    
    document.getElementById('val-top-gainer').innerText = coin.symbol.toUpperCase();
    const gainerDelta = document.getElementById('delta-top-gainer');
    gainerDelta.innerText = `${coin.price_change_24h >= 0 ? '+' : ''}${coin.price_change_24h.toFixed(2)}%`;
    gainerDelta.className = `delta ${coin.price_change_24h >= 0 ? 'positive' : 'negative'}`;

    // Card 3: Volatility/Market Stats (Cycling every coin)
    const volCard = document.getElementById('kpi-volatility');
    volCard.querySelector('.title').innerText = `${coin.name} Volume`;
    document.getElementById('val-volatility').innerText = `$${(coin.total_volume / 1e6).toFixed(1)}M`;
    document.getElementById('delta-volatility').innerText = `Rank #${coin.market_cap_rank}`;
    document.getElementById('delta-volatility').className = 'delta';

    // Add update animation
    [spotlightCard, volCard].forEach(card => {
        card.style.animation = 'none';
        card.offsetHeight; // trigger reflow
        card.style.animation = 'cardUpdate 0.5s ease-out';
    });
}

function switchView(viewName) {
  // Update Sidebar
  const navLinks = document.querySelectorAll('#sidebar-nav a');
  navLinks.forEach(link => {
    if (link.getAttribute('data-view') === viewName) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });

  // Update Sections
  const sections = document.querySelectorAll('.view-section');
  sections.forEach(section => {
    if (section.id === `view-${viewName}`) {
      section.classList.add('active');
    } else {
      section.classList.remove('active');
    }
  });

  // Refresh extra view components
  if (viewName === 'analytics') {
    initAnalyticsCharts();
  }
}

function initAnalyticsCharts() {
  const top10 = marketData.slice(0, 10);

  // Volatility Index Chart
  const ctxVol = document.getElementById('volatilityChart').getContext('2d');
  new Chart(ctxVol, {
    type: 'bar',
    data: {
      labels: top10.map(c => c.name),
      datasets: [{
        label: 'Volatility Score',
        data: top10.map(c => c.volatility_score),
        backgroundColor: '#ef4444'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { y: { beginAtZero: true } },
      onClick: (e, activeEls) => {
        if (activeEls.length > 0) {
          const index = activeEls[0].index;
          const label = ctxVol.chart.data.labels[index];
          const coin = marketData.find(c => c.name === label);
          if (coin) showDetail(coin.coin_id);
        }
      }
    }
  });

  // Volume Distribution Chart (Replacing Sector Distribution)
  const ctxSector = document.getElementById('sectorChart').getContext('2d');
  const top5Volume = [...marketData].sort((a,b) => b.total_volume - a.total_volume).slice(0, 5);
  
  new Chart(ctxSector, {
    type: 'polarArea',
    data: {
      labels: top5Volume.map(c => c.name),
      datasets: [{
        data: top5Volume.map(c => c.total_volume),
        backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899']
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { 
        legend: { position: 'bottom' },
        tooltip: {
            callbacks: {
                label: (context) => {
                    return ` ${context.label}: $${(context.raw / 1e6).toFixed(1)}M`;
                }
            }
        }
      },
      onClick: (e, activeEls) => {
        if (activeEls.length > 0) {
          const index = activeEls[0].index;
          const label = top5Volume[index].name;
          if (label) {
            const coin = marketData.find(c => c.name === label);
            if (coin) showDetail(coin.coin_id);
          }
        }
      }
    }
  });
}

function handleSearch(query) {
  const filtered = marketData.filter(
    (coin) =>
      coin.name.toLowerCase().includes(query.toLowerCase()) ||
      coin.symbol.toLowerCase().includes(query.toLowerCase()),
  );
  renderTable(filtered);

  // Auto-pop exact matches
  if (query.length >= 2) {
    const exactMatch = marketData.find(c => 
      c.symbol.toLowerCase() === query.toLowerCase() || 
      c.name.toLowerCase() === query.toLowerCase()
    );
    if (exactMatch) showDetail(exactMatch.coin_id);
  }
}

function updateCharts(data) {
  const top15 = data.slice(0, 15);
  const top10 = data.slice(0, 10);

  // Set global defaults for dark mode
  Chart.defaults.color = "#888";
  Chart.defaults.borderColor = "rgba(255,255,255,0.05)";

  // Price Distribution Chart
  if (priceChart) priceChart.destroy();
  const ctxPrice = document.getElementById("priceChart").getContext("2d");
  priceChart = new Chart(ctxPrice, {
    type: "line",
    data: {
      labels: top15.map((c) => c.name),
      datasets: [
        {
          label: "Price (USD)",
          data: top15.map((c) => c.current_price),
          borderColor: "#3b82f6",
          backgroundColor: "rgba(59, 130, 246, 0.1)",
          fill: true,
          tension: 0.4,
          pointRadius: 4,
          pointBackgroundColor: "#3b82f6",
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: "#111",
          titleColor: "#3b82f6",
          bodyColor: "#fff",
          borderColor: "#333",
          borderWidth: 1,
        },
      },
      onClick: (e, activeEls) => {
        if (activeEls.length > 0) {
          const index = activeEls[0].index;
          const label = priceChart.data.labels[index];
          const coin = marketData.find(c => c.name === label);
          if (coin) showDetail(coin.coin_id);
        }
      },
      scales: {
        y: {
          grid: { color: "rgba(255,255,255,0.05)" },
          ticks: { callback: (value) => "$" + value.toLocaleString() },
        },
        x: { grid: { display: false } },
      },
    },
  });

  // Market Dominance Chart
  if (dominanceChart) dominanceChart.destroy();
  const ctxDom = document.getElementById("dominanceChart").getContext("2d");
  dominanceChart = new Chart(ctxDom, {
    type: "doughnut",
    data: {
      labels: top10.map((c) => c.name),
      datasets: [
        {
          data: top10.map((c) => c.market_cap),
          backgroundColor: [
            "#3b82f6",
            "#10b981",
            "#f59e0b",
            "#ef4444",
            "#8b5cf6",
            "#ec4899",
            "#06b6d4",
            "#84cc16",
            "#f97316",
            "#6366f1",
          ],
          borderWidth: 0,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      onClick: (e, activeEls) => {
        if (activeEls.length > 0) {
          const index = activeEls[0].index;
          const label = dominanceChart.data.labels[index];
          const coin = marketData.find(c => c.name === label);
          if (coin) showDetail(coin.coin_id);
        }
      },
      plugins: {
        legend: {
          position: "bottom",
          labels: { color: "#888", usePointStyle: true },
        },
      },
    },
  });
}

async function showDetail(coinId) {
  try {
    const response = await fetch(`/api/search?q=${coinId}`);
    const result = await response.json();
    const coin = result[0];

    const container = document.getElementById("modalData");
    const deltaClass = coin.price_change_24h >= 0 ? "positive" : "negative";

    container.innerHTML = `
            <div style="display: flex; align-items: center; gap: 20px; margin-bottom: 30px;">
                <div class="avatar" style="width: 60px; height: 60px; font-size: 1.5rem;">${coin.symbol[0].toUpperCase()}</div>
                <div>
                    <h2 style="font-size: 2rem;">${coin.name} (${coin.symbol.toUpperCase()})</h2>
                    <span style="color: #3b82f6; font-weight: 800;">MARKET RANK #${coin.market_cap_rank}</span>
                </div>
            </div>
            
            <div style="grid-template-columns: repeat(3, 1fr); display: grid; gap: 20px;">
                <div class="kpi-card" style="background: rgba(255,255,255,0.02)">
                    <p style="color: #888; font-size: 0.8rem;">CURRENT PRICE</p>
                    <p style="font-size: 1.5rem; font-weight: 800;">$${coin.current_price.toLocaleString()}</p>
                    <span class="delta ${deltaClass}">${coin.price_change_24h.toFixed(2)}%</span>
                </div>
                <div class="kpi-card" style="background: rgba(255,255,255,0.02)">
                    <p style="color: #888; font-size: 0.8rem;">MARKET CAP</p>
                    <p style="font-size: 1.5rem; font-weight: 800;">$${(coin.market_cap / 1e9).toFixed(2)}B</p>
                </div>
                <div class="kpi-card" style="background: rgba(255,255,255,0.02)">
                    <p style="color: #888; font-size: 0.8rem;">TOTAL VOLUME</p>
                    <p style="font-size: 1.5rem; font-weight: 800;">$${(coin.total_volume / 1e6).toFixed(1)}M</p>
                </div>
            </div>

            <div style="margin-top: 30px; padding: 20px; background: rgba(59, 130, 246, 0.05); border-radius: 12px; border: 1px solid rgba(59, 130, 246, 0.2);">
                <i class="fa-solid fa-circle-info"></i> <strong>Volatility Insights:</strong> 
                This asset has a current volatility score of ${coin.volatility_score.toLocaleString()}. 
                Calculated based on 24h price swing relative to trading volume.
            </div>
        `;

    document.getElementById("coinModal").style.display = "block";
  } catch (err) {
    console.error("Error showing detail:", err);
  }
}
