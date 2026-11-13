/**
 * YouTube Big Data Studio - Interactive Application Engine
 * Handles dynamic data loading, Chart.js rendering, filtering, and tab switching.
 */

// Embedded fallback dataset (ensures instant zero-config launch even on file:// protocol)
let APP_DATA = {
  summary: {
    total_videos: 800,
    total_views: 45787617,
    total_channels: 10,
    avg_engagement: 0.0655,
    countries: ["CA", "GB", "US", "IN"]
  },
  top_videos: [
    { country: "CA", video_id: "CA_41489_0002", title: "Behind The Scenes: Making Of A Blockbuster (Part 3)", channel: "Unbox Therapy", category: "Science & Technology", views: 8303323, likes: 503009, comments: 39079, engagement: 0.076 },
    { country: "GB", video_id: "GB_12306_0076", title: "How Neural Networks Actually Work Under The Hood", channel: "Gordon Ramsay", category: "Howto & Style", views: 6044972, likes: 299837, comments: 84599, engagement: 0.0711 },
    { country: "CA", video_id: "CA_53576_0014", title: "Every Student Before The Exams | Comedy Drama", channel: "The Weeknd", category: "Music", views: 5815197, likes: 458474, comments: 74648, engagement: 0.0977 },
    { country: "US", video_id: "US_80687_0143", title: "Top 10 Hidden Car Features You Didn't Know About", channel: "PewDiePie", category: "Gaming", views: 1552784, likes: 71576, comments: 25826, engagement: 0.0765 },
    { country: "CA", video_id: "CA_51185_0148", title: "Full Match Highlights - Final Thriller (Part 2)", channel: "The Weeknd", category: "Music", views: 1227999, likes: 28073, comments: 15332, engagement: 0.0453 },
    { country: "US", video_id: "US_72314_0088", title: "Why The World's Biggest Supercomputer Was Built Here", channel: "Vox", category: "News & Politics", views: 1184200, likes: 74200, comments: 18450, engagement: 0.082 },
    { country: "IN", video_id: "IN_93412_0055", title: "Official Movie Teaser Trailer [HD]", channel: "T-Series", category: "Music", views: 1102450, likes: 62100, comments: 14200, engagement: 0.072 },
    { country: "GB", video_id: "GB_64210_0112", title: "24-Hour Road Trip Challenge Across The Country", channel: "Top Gear", category: "Autos & Vehicles", views: 980400, likes: 51200, comments: 11200, engagement: 0.067 }
  ],
  top_channels: [
    { channel: "Unbox Therapy", video_count: 55, total_views: 11895856, total_likes: 680404, total_comments: 72655, avg_engagement: 0.0634 },
    { channel: "The Weeknd", video_count: 56, total_views: 10511387, total_likes: 646582, total_comments: 125874, avg_engagement: 0.0657 },
    { channel: "Gordon Ramsay", video_count: 33, total_views: 8259227, total_likes: 402720, total_comments: 105588, avg_engagement: 0.0642 },
    { channel: "BBC News", video_count: 44, total_views: 3832270, total_likes: 158289, total_comments: 41318, avg_engagement: 0.0663 },
    { channel: "PewDiePie", video_count: 17, total_views: 3499203, total_likes: 146204, total_comments: 37461, avg_engagement: 0.0688 },
    { channel: "Linus Tech Tips", video_count: 54, total_views: 3177747, total_likes: 139696, total_comments: 34571, avg_engagement: 0.0622 },
    { channel: "Vox", video_count: 24, total_views: 2970439, total_likes: 163657, total_comments: 37136, avg_engagement: 0.0662 },
    { channel: "Marques Brownlee", video_count: 28, total_views: 2861966, total_likes: 121949, total_comments: 27405, avg_engagement: 0.063 }
  ],
  categories: [
    { category: "Gaming", video_count: 17, avg_views: 205835, avg_likes: 8600, engagement: 0.0688 },
    { category: "Howto & Style", video_count: 74, avg_views: 147440, avg_likes: 7367, engagement: 0.0656 },
    { category: "Science & Technology", video_count: 155, avg_views: 126478, avg_likes: 6586, engagement: 0.0631 },
    { category: "Sports", video_count: 36, avg_views: 124902, avg_likes: 4546, engagement: 0.069 },
    { category: "Music", video_count: 137, avg_views: 113523, avg_likes: 6342, engagement: 0.0653 },
    { category: "News & Politics", video_count: 97, avg_views: 97304, avg_likes: 4795, engagement: 0.0665 },
    { category: "Film & Animation", video_count: 28, avg_views: 77789, avg_likes: 3801, engagement: 0.0673 },
    { category: "Comedy", video_count: 65, avg_views: 61451, avg_likes: 3145, engagement: 0.0644 }
  ],
  countries: [
    { country: "CA", unique_videos: 200, avg_views: 136350, avg_likes: 7675, engagement: 0.0633, days_to_trend: 5.9 },
    { country: "GB", unique_videos: 200, avg_views: 92731, avg_likes: 4357, engagement: 0.0668, days_to_trend: 6.1 },
    { country: "US", unique_videos: 200, avg_views: 92273, avg_likes: 4400, engagement: 0.0682, days_to_trend: 5.9 },
    { country: "IN", unique_videos: 200, avg_views: 76508, avg_likes: 3473, engagement: 0.0636, days_to_trend: 6.4 }
  ],
  timing: [
    { hour: 0, count: 18, avg_views: 45000 }, { hour: 2, count: 12, avg_views: 38000 },
    { hour: 4, count: 9, avg_views: 31000 }, { hour: 6, count: 14, avg_views: 42000 },
    { hour: 8, count: 28, avg_views: 65000 }, { hour: 10, count: 42, avg_views: 89000 },
    { hour: 12, count: 58, avg_views: 112000 }, { hour: 14, count: 84, avg_views: 148000 },
    { hour: 16, count: 96, avg_views: 182000 }, { hour: 18, count: 88, avg_views: 165000 },
    { hour: 20, count: 64, avg_views: 120000 }, { hour: 22, count: 32, avg_views: 75000 }
  ],
  mllib: {
    regression: [
      { model: "Linear Regression", rmse: 78741.87, r2: 0.8412, mae: 27457.21 },
      { model: "Random Forest Regressor", rmse: 79964.69, r2: 0.8362, mae: 27861.72 }
    ],
    feature_importances: [
      { feature: "Likes Velocity", importance: 0.4721 },
      { feature: "Comment Density", importance: 0.2483 },
      { feature: "Days to Trend", importance: 0.1147 },
      { feature: "Category Genre", importance: 0.0732 },
      { feature: "Tag Count", importance: 0.0461 },
      { feature: "Title Length", importance: 0.0284 }
    ],
    clusters: [
      { cluster: 0, label: "Mega Viral Blockbuster", count: 3, avg_views: 6721164, avg_likes: 420440, engagement: 0.0816 },
      { cluster: 1, label: "Consistent Mid-Tier Performer", count: 295, avg_views: 58828, avg_likes: 2565, engagement: 0.064 },
      { cluster: 2, label: "High Community Engagement", count: 282, avg_views: 81456, avg_likes: 5308, engagement: 0.0875 },
      { cluster: 3, label: "Emerging / Niche Trending", count: 220, avg_views: 86746, avg_likes: 2120, engagement: 0.0391 }
    ]
  },
  correlation: {
    labels: ["Views", "Likes", "Dislikes", "Comments"],
    matrix: [
      [1.000, 0.975, 0.964, 0.895],
      [0.975, 1.000, 0.920, 0.879],
      [0.964, 0.920, 1.000, 0.792],
      [0.895, 0.879, 0.792, 1.000]
    ]
  },
  benchmarks: {
    storage_and_io: { csv_read_scan_sec: 14.82, parquet_read_scan_sec: 2.14, scan_speedup_factor: 6.93, compression_ratio: 4.35 },
    caching_optimization: { uncached_query_sec: 0.495, cached_query_sec: 0.076, caching_speedup_factor: 6.51 },
    partition_pruning: { full_scan_sec: 0.495, pruned_partition_scan_sec: 0.0648, pruning_speedup_factor: 7.64 },
    cluster_scaling: { single_node_sec: 38.4, cluster_3_workers_sec: 11.2, speedup_factor: 3.43 }
  }
};

let activeCountry = "ALL";
let activeCharts = {};

// Number Formatter
function formatNumber(num) {
  if (num >= 1e9) return (num / 1e9).toFixed(2) + "B";
  if (num >= 1e6) return (num / 1e6).toFixed(2) + "M";
  if (num >= 1e3) return (num / 1e3).toFixed(1) + "k";
  return num ? num.toLocaleString() : "0";
}

// Format Percent
function formatPercent(num) {
  return (num * 100).toFixed(2) + "%";
}

// Tab Switching
function setupTabs() {
  const tabButtons = document.querySelectorAll(".tab-btn");
  tabButtons.forEach(btn => {
    btn.addEventListener("click", () => {
      tabButtons.forEach(b => b.classList.remove("active"));
      document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));
      
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetContent = document.getElementById(targetId);
      if (targetContent) {
        targetContent.classList.add("active");
      }
    });
  });
}

// Theme Switcher
function setupThemeToggle() {
  const toggleBtn = document.getElementById("themeToggle");
  if (!toggleBtn) return;
  
  const savedTheme = localStorage.getItem("yt_theme") || "dark";
  document.documentElement.setAttribute("data-theme", savedTheme);
  toggleBtn.textContent = savedTheme === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode";
  
  toggleBtn.addEventListener("click", () => {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    document.documentElement.setAttribute("data-theme", next);
    localStorage.setItem("yt_theme", next);
    toggleBtn.textContent = next === "dark" ? "☀️ Light Mode" : "🌙 Dark Mode";
    reRenderCharts();
  });
}

// Render KPI Cards
function renderKPIs() {
  let summary = APP_DATA.summary;
  if (APP_DATA.summary_by_country && APP_DATA.summary_by_country[activeCountry]) {
    summary = APP_DATA.summary_by_country[activeCountry];
  }
  
  document.getElementById("kpiTotalVideos").textContent = (summary.total_videos || 0).toLocaleString();
  document.getElementById("kpiTotalViews").textContent = formatNumber(summary.total_views || 0);
  document.getElementById("kpiTotalChannels").textContent = (summary.total_channels || 0).toLocaleString();
  document.getElementById("kpiAvgEngagement").textContent = formatPercent(summary.avg_engagement || 0);
}

// Render Top Videos Table
function renderVideosTable(searchQuery = "") {
  const tbody = document.getElementById("topVideosTableBody");
  if (!tbody) return;
  
  let videos = APP_DATA.top_videos || [];
  if (activeCountry !== "ALL") {
    videos = videos.filter(v => v.country === activeCountry);
  }
  
  if (searchQuery) {
    const q = searchQuery.toLowerCase();
    videos = videos.filter(v => v.title.toLowerCase().includes(q) || v.channel.toLowerCase().includes(q));
  }
  
  tbody.innerHTML = videos.map((v, idx) => `
    <tr>
      <td><strong style="color: var(--accent-red)">#${idx + 1}</strong></td>
      <td>
        <span class="country-pill">${v.country}</span>
        <strong>${v.title}</strong>
        <div style="font-size: 0.78rem; color: var(--text-muted); margin-top: 2px;">Channel: ${v.channel}</div>
      </td>
      <td><span style="font-size: 0.8rem; background: rgba(148,163,184,0.1); padding: 3px 8px; border-radius: 4px;">${v.category}</span></td>
      <td style="font-weight: 700; color: var(--accent-blue);">${formatNumber(v.views)}</td>
      <td>${formatNumber(v.likes)}</td>
      <td>${formatNumber(v.comments)}</td>
      <td><strong style="color: var(--accent-emerald);">${formatPercent(v.engagement)}</strong></td>
    </tr>
  `).join("");
}

// Render Country Comparison Table
function renderCountryComparisonTable() {
  const tbody = document.getElementById("countryComparisonTableBody");
  if (!tbody || !APP_DATA.countries) return;
  
  const countryNames = {
    US: { name: "United States", flag: "🇺🇸" },
    IN: { name: "India", flag: "🇮🇳" },
    GB: { name: "Great Britain", flag: "🇬🇧" },
    CA: { name: "Canada", flag: "🇨🇦" }
  };
  
  tbody.innerHTML = APP_DATA.countries.map(c => {
    const meta = countryNames[c.country] || { name: c.country, flag: "🌐" };
    const isSelected = activeCountry === c.country;
    return `
      <tr style="${isSelected ? 'background: rgba(59, 130, 246, 0.08); font-weight: 600;' : ''}">
        <td>
          <span style="font-size: 1.2rem; margin-right: 6px;">${meta.flag}</span>
          <strong>${meta.name} (${c.country})</strong>
        </td>
        <td><strong>${c.unique_videos.toLocaleString()}</strong></td>
        <td style="color: var(--accent-blue); font-weight: 700;">${formatNumber(c.total_views)}</td>
        <td>${formatNumber(c.avg_views)}</td>
        <td>${formatNumber(c.avg_likes)}</td>
        <td>${formatNumber(c.avg_comments)}</td>
        <td style="color: var(--accent-emerald); font-weight: 700;">${formatPercent(c.engagement)}</td>
        <td><strong>${c.days_to_trend} days</strong></td>
        <td>
          <button class="btn" style="padding: 4px 10px; font-size: 0.78rem;" onclick="selectCountry('${c.country}')">
            ${isSelected ? '✓ Viewing' : 'Select'}
          </button>
        </td>
      </tr>
    `;
  }).join("");
}

function selectCountry(code) {
  activeCountry = code;
  const select = document.getElementById("countrySelect");
  if (select) select.value = code;
  renderKPIs();
  renderVideosTable();
  renderChannelsChart();
  renderCategoryChart();
  renderTimingChart();
  renderCountryComparisonTable();
  
  const badge = document.querySelector(".header-controls .badge");
  if (badge) {
    const count = APP_DATA.summary_by_country && APP_DATA.summary_by_country[activeCountry] 
      ? APP_DATA.summary_by_country[activeCountry].total_videos.toLocaleString()
      : (APP_DATA.summary ? APP_DATA.summary.total_videos.toLocaleString() : "Active");
    badge.innerHTML = `<span class="badge-dot"></span> ${activeCountry === "ALL" ? "All Regions" : activeCountry}: ${count} Records`;
  }
}

// Render Charts via Chart.js
function renderChannelsChart() {
  const ctx = document.getElementById("channelsChart");
  if (!ctx || typeof Chart === "undefined") return;
  
  if (activeCharts.channels) activeCharts.channels.destroy();
  
  let channelsList = APP_DATA.top_channels;
  if (APP_DATA.top_channels_by_country && APP_DATA.top_channels_by_country[activeCountry]) {
    channelsList = APP_DATA.top_channels_by_country[activeCountry];
  } else if (activeCountry !== "ALL" && APP_DATA.top_channels) {
    channelsList = APP_DATA.top_channels.filter(c => c.country === activeCountry);
  }
  
  const channels = (channelsList && channelsList.length > 0 ? channelsList : APP_DATA.top_channels || []).slice(0, 8);
  activeCharts.channels = new Chart(ctx, {
    type: "bar",
    data: {
      labels: channels.map(c => c.channel),
      datasets: [
        {
          label: "Total Views",
          data: channels.map(c => c.total_views),
          backgroundColor: "#3b82f6",
          borderRadius: 6
        },
        {
          label: "Total Likes (x10)",
          data: channels.map(c => c.total_likes * 10), // scaled for visualization
          backgroundColor: "#ef4444",
          borderRadius: 6
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { position: "top", labels: { color: getComputedStyle(document.body).color } }
      },
      scales: {
        y: {
          ticks: { callback: v => formatNumber(v) }
        }
      }
    }
  });
}

function renderCategoryChart() {
  const ctx = document.getElementById("categoryChart");
  if (!ctx || typeof Chart === "undefined") return;
  
  if (activeCharts.category) activeCharts.category.destroy();
  
  let catList = APP_DATA.categories;
  if (APP_DATA.categories_by_country && APP_DATA.categories_by_country[activeCountry]) {
    catList = APP_DATA.categories_by_country[activeCountry];
  } else if (activeCountry !== "ALL" && APP_DATA.categories) {
    catList = APP_DATA.categories.filter(c => c.country === activeCountry);
  }
  
  const cats = (catList && catList.length > 0 ? catList : APP_DATA.categories || []).slice(0, 8);
  activeCharts.category = new Chart(ctx, {
    type: "bar",
    data: {
      labels: cats.map(c => c.category),
      datasets: [
        {
          type: "bar",
          label: "Average Views",
          data: cats.map(c => c.avg_views),
          backgroundColor: "rgba(16, 185, 129, 0.75)",
          borderRadius: 6,
          yAxisID: "y"
        },
        {
          type: "line",
          label: "Engagement Rate (%)",
          data: cats.map(c => (c.engagement * 100).toFixed(2)),
          borderColor: "#ef4444",
          borderWidth: 3,
          pointBackgroundColor: "#ef4444",
          yAxisID: "y1"
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          type: "linear",
          position: "left",
          ticks: { callback: v => formatNumber(v) }
        },
        y1: {
          type: "linear",
          position: "right",
          grid: { drawOnChartArea: false },
          ticks: { callback: v => v + "%" }
        }
      }
    }
  });
}

function renderTimingChart() {
  const ctx = document.getElementById("timingChart");
  if (!ctx || typeof Chart === "undefined") return;
  
  if (activeCharts.timing) activeCharts.timing.destroy();
  
  let timingData = APP_DATA.timing || [];
  if (APP_DATA.timing_by_country && APP_DATA.timing_by_country[activeCountry]) {
    timingData = APP_DATA.timing_by_country[activeCountry];
  }
  
  activeCharts.timing = new Chart(ctx, {
    type: "line",
    data: {
      labels: timingData.map(t => `${t.hour}:00`),
      datasets: [{
        label: `Upload Volume by Hour (UTC) [${activeCountry}]`,
        data: timingData.map(t => t.count),
        borderColor: "#8b5cf6",
        backgroundColor: "rgba(139, 92, 246, 0.15)",
        fill: true,
        tension: 0.35,
        borderWidth: 3
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false
    }
  });
}

function renderCorrelationHeatmap() {
  const container = document.getElementById("corrMatrixContainer");
  if (!container) return;
  
  const labels = APP_DATA.correlation.labels;
  const matrix = APP_DATA.correlation.matrix;
  
  let html = `<table class="data-table" style="text-align: center;"><tr><th></th>`;
  labels.forEach(l => html += `<th>${l}</th>`);
  html += `</tr>`;
  
  matrix.forEach((row, i) => {
    html += `<tr><th>${labels[i]}</th>`;
    row.forEach(val => {
      const alpha = Math.max(0.1, val).toFixed(2);
      const bg = `rgba(239, 68, 68, ${alpha})`;
      html += `<td style="background:${bg}; color:#fff; font-weight:700;">${val.toFixed(3)}</td>`;
    });
    html += `</tr>`;
  });
  html += `</table>`;
  container.innerHTML = html;
}

function renderMLlibSection() {
  // Feature importances
  const fiContainer = document.getElementById("featureImportancesList");
  if (fiContainer) {
    const fi = APP_DATA.mllib.feature_importances;
    fiContainer.innerHTML = fi.map(item => `
      <div class="bar-row">
        <div class="bar-label">${item.feature}</div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${item.importance * 100}%; background: var(--accent-emerald);"></div>
        </div>
        <div class="bar-val">${(item.importance * 100).toFixed(1)}%</div>
      </div>
    `).join("");
  }
  
  // Clusters
  const clusterGrid = document.getElementById("clusterCardsGrid");
  if (clusterGrid) {
    const clusters = APP_DATA.mllib.clusters;
    const colors = ["var(--accent-red)", "var(--accent-blue)", "var(--accent-emerald)", "var(--accent-amber)"];
    clusterGrid.innerHTML = clusters.map((c, i) => `
      <div class="kpi-card" style="border-top: 4px solid ${colors[i % colors.length]};">
        <div class="kpi-title" style="color: ${colors[i % colors.length]};">Cluster ${c.cluster}: ${c.label}</div>
        <div class="kpi-val">${formatNumber(c.avg_views)}</div>
        <div class="kpi-sub">Average Views (${c.count} videos)</div>
        <div style="font-size: 0.85rem; margin-top: 10px; color: var(--text-secondary);">
          <div>• Avg Likes: <strong>${formatNumber(c.avg_likes)}</strong></div>
          <div>• Engagement Rate: <strong style="color: var(--accent-emerald);">${formatPercent(c.engagement)}</strong></div>
        </div>
      </div>
    `).join("");
  }
}

function reRenderCharts() {
  renderChannelsChart();
  renderCategoryChart();
  renderTimingChart();
}

// Fetch live data from backend or data.json if available
async function loadData() {
  try {
    const res = await fetch("data.json");
    if (res.ok) {
      const json = await res.json();
      APP_DATA = json;
      console.log("[+] Loaded live data from data.json");
    }
  } catch (err) {
    console.log("[*] Using embedded dataset (standalone mode)");
  }
  
  renderKPIs();
  renderVideosTable();
  reRenderCharts();
  renderCountryComparisonTable();
  renderCorrelationHeatmap();
  renderMLlibSection();
}

// Setup Event Listeners
function setupEvents() {
  const countrySelect = document.getElementById("countrySelect");
  if (countrySelect) {
    countrySelect.addEventListener("change", (e) => {
      activeCountry = e.target.value;
      renderKPIs();
      renderVideosTable();
      renderChannelsChart();
      renderCategoryChart();
      renderTimingChart();
      renderCountryComparisonTable();
      
      // Update badge
      const badge = document.querySelector(".header-controls .badge");
      if (badge) {
        const count = APP_DATA.summary_by_country && APP_DATA.summary_by_country[activeCountry] 
          ? APP_DATA.summary_by_country[activeCountry].total_videos.toLocaleString()
          : (APP_DATA.summary ? APP_DATA.summary.total_videos.toLocaleString() : "Active");
        badge.innerHTML = `<span class="badge-dot"></span> ${activeCountry === "ALL" ? "All Regions" : activeCountry}: ${count} Records`;
      }
    });
  }
  
  const searchInput = document.getElementById("videoSearch");
  if (searchInput) {
    searchInput.addEventListener("input", (e) => {
      renderVideosTable(e.target.value);
    });
  }
  
  const runBtn = document.getElementById("runPipelineBtn");
  if (runBtn) {
    runBtn.addEventListener("click", async () => {
      runBtn.disabled = true;
      runBtn.textContent = "⏳ Running Pipeline...";
      try {
        const res = await fetch("/api/run-pipeline", { method: "POST" });
        if (res.ok) {
          alert("Pipeline run started! Refreshing data in 10 seconds...");
          setTimeout(loadData, 10000);
        } else {
          alert("Pipeline triggered. To run manually, execute 'python run_all.py' in terminal.");
        }
      } catch (e) {
        alert("To re-run the full Spark pipeline, execute 'python run_all.py' in your terminal!");
      } finally {
        runBtn.disabled = false;
        runBtn.textContent = "⚡ Run Pipeline";
      }
    });
  }
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  setupTabs();
  setupThemeToggle();
  setupEvents();
  loadData();
});

