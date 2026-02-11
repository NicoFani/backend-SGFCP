const state = {
  data: {
    trips: [],
    expenses: [],
    advances: [],
    drivers: [],
    trucks: [],
    clients: [],
  },
  filtered: {
    trips: [],
    expenses: [],
    advances: [],
  },
  charts: {},
  modal: {
    activeChartId: null,
    originalParent: null,
    originalNext: null,
  },
  theme: localStorage.getItem('sgfcp_theme') || 'light',
};

// Initialize theme
function initTheme() {
  document.documentElement.setAttribute('data-theme', state.theme);
  updateThemeIcon();
}

function updateThemeIcon() {
  const sunIcon = document.getElementById('sunIcon');
  const moonIcon = document.getElementById('moonIcon');
  if (state.theme === 'dark') {
    sunIcon.style.display = 'none';
    moonIcon.style.display = 'block';
  } else {
    sunIcon.style.display = 'block';
    moonIcon.style.display = 'none';
  }
}

function toggleTheme() {
  state.theme = state.theme === 'light' ? 'dark' : 'light';
  localStorage.setItem('sgfcp_theme', state.theme);
  document.documentElement.setAttribute('data-theme', state.theme);
  updateThemeIcon();
  // Regenerar gráficos con nuevos colores
  renderCharts();
}

const $ = (id) => document.getElementById(id);

// Helper para detectar tema actual
function isDarkMode() {
  return state.theme === 'dark';
}

// Paleta de colores que cambia según el tema
function getChartColors() {
  const dark = isDarkMode();
  return {
    primary: "#fca311",
    primaryBg: "rgba(252, 163, 17, 0.25)",
    primaryBar: "rgba(252, 163, 17, 0.8)",
    secondary: dark ? "#6b9bd1" : "#000a24",
    secondaryBg: dark ? "rgba(107, 155, 209, 0.2)" : "rgba(0, 10, 36, 0.2)",
    secondaryBar: dark ? "rgba(107, 155, 209, 0.8)" : "rgba(0, 10, 36, 0.7)",
    doughnut: dark
      ? ["#fca311", "#6b9bd1", "#ffd58a", "#8ba9cc", "#f7b955", "#4a7bb7"]
      : ["#fca311", "#1f3b73", "#ffd58a", "#6b7a99", "#f7b955", "#101a35"],
  };
}

const currency = new Intl.NumberFormat("es-AR", {
  style: "currency",
  currency: "ARS",
  maximumFractionDigits: 0,
});

const number = new Intl.NumberFormat("es-AR");

function setStatus(message, tone = "info") {
  const status = $("status");
  if (!status) return;
  status.textContent = message;
  status.dataset.tone = tone;
}

function getBaseUrl() {
  const stored = localStorage.getItem("sgfcp_base_url");
  const baseInput = document.getElementById("baseUrl");
  const inputValue = baseInput ? baseInput.value.trim() : "";
  const value = inputValue || stored || "http://localhost:5000";
  localStorage.setItem("sgfcp_base_url", value);
  return value.replace(/\/$/, "");
}

function getToken() {
  return (localStorage.getItem("sgfcp_token") || "").trim();
}

function setToken(token) {
  localStorage.setItem("sgfcp_token", token);
}

function clearToken() {
  localStorage.removeItem("sgfcp_token");
}

async function fetchJson(path) {
  const baseUrl = getBaseUrl();
  const token = getToken();

  const response = await fetch(`${baseUrl}${path}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });

  if (!response.ok) {
    throw new Error(`Error en ${path}`);
  }

  return response.json();
}

async function loadData() {
  setStatus("Cargando datos...", "info");
  try {
    const [trips, expenses, advances, drivers, trucks, clients] =
      await Promise.all([
        fetchJson("/trips/"),
        fetchJson("/expenses/"),
        fetchJson("/advance-payments/"),
        fetchJson("/drivers/"),
        fetchJson("/trucks/"),
        fetchJson("/clients/"),
      ]);

    state.data = { trips, expenses, advances, drivers, trucks, clients };
    applyFilters();
    setStatus("Datos cargados", "ok");
  } catch (error) {
    setStatus("No se pudo cargar data. Revisa token y backend", "error");
  }
}

function parseDate(value) {
  if (!value) return null;
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : date;
}

function withinRange(date, from, to) {
  if (!date) return false;
  if (from && date < from) return false;
  if (to && date > to) return false;
  return true;
}

function applyFilters() {
  const from = parseDate($("fromDate").value);
  const to = parseDate($("toDate").value);

  state.filtered.trips = state.data.trips.filter((trip) =>
    withinRange(parseDate(trip.start_date), from, to)
  );
  state.filtered.expenses = state.data.expenses.filter((expense) =>
    withinRange(parseDate(expense.date), from, to)
  );
  state.filtered.advances = state.data.advances.filter((advance) =>
    withinRange(parseDate(advance.date), from, to)
  );

  render();
}

function resetFilters() {
  $("fromDate").value = "";
  $("toDate").value = "";
  applyFilters();
}

function getClientName(clientId) {
  const client = state.data.clients.find((c) => c.id === clientId);
  return client ? client.name : "Sin cliente";
}

function getDriverName(driverId) {
  const driver = state.data.drivers.find((d) => d.id === driverId);
  if (!driver) return `Chofer ${driverId}`;
  return `${driver.name || ""} ${driver.surname || ""}`.trim();
}

function calcTripRevenue(trip) {
  if (!trip) return 0;
  const rate = Number(trip.rate || 0);
  const kms = Number(trip.estimated_kms || 0);
  if (trip.calculated_per_km && kms > 0) {
    return rate * kms;
  }
  return rate;
}

function groupByMonth(items, dateKey, valueFn) {
  const map = new Map();
  items.forEach((item) => {
    const date = parseDate(item[dateKey]);
    if (!date) return;
    const key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(
      2,
      "0"
    )}`;
    const current = map.get(key) || 0;
    map.set(key, current + valueFn(item));
  });

  return Array.from(map.entries()).sort((a, b) => a[0].localeCompare(b[0]));
}

function renderKpis() {
  const trips = state.filtered.trips;
  const expenses = state.filtered.expenses;
  const advances = state.filtered.advances;

  const revenue = trips.reduce((sum, trip) => sum + calcTripRevenue(trip), 0);
  const expenseTotal = expenses.reduce(
    (sum, expense) => sum + Number(expense.amount || 0),
    0
  );
  const margin = revenue - expenseTotal;
  const tripCount = trips.length;
  const avgRevenue = tripCount ? revenue / tripCount : 0;
  const kmTotal = trips.reduce(
    (sum, trip) => sum + Number(trip.estimated_kms || 0),
    0
  );
  const advancesTotal = advances.reduce(
    (sum, advance) => sum + Number(advance.amount || 0),
    0
  );
  const activeDrivers = state.data.drivers.filter((d) => d.active).length;
  const operationalTrucks = state.data.trucks.filter((t) => t.operational)
    .length;

  const revenueByMonth = groupByMonth(trips, "start_date", calcTripRevenue);
  const lastMonth = revenueByMonth[revenueByMonth.length - 1];
  const prevMonth = revenueByMonth[revenueByMonth.length - 2];
  let revenueDelta = 0;
  if (lastMonth && prevMonth && prevMonth[1] !== 0) {
    revenueDelta = ((lastMonth[1] - prevMonth[1]) / prevMonth[1]) * 100;
  }

  const kpis = [
    {
      label: "Ingresos",
      value: currency.format(revenue),
      sub: lastMonth ? `${lastMonth[0]} ${revenueDelta.toFixed(1)}%` : "N/A",
    },
    {
      label: "Gastos",
      value: currency.format(expenseTotal),
      sub: `${expenses.length} registros`,
    },
    {
      label: "Margen",
      value: currency.format(margin),
      sub: tripCount ? `${number.format(tripCount)} viajes` : "N/A",
    },
    {
      label: "Ingreso por viaje",
      value: currency.format(avgRevenue),
      sub: `${number.format(kmTotal)} km`,
    },
    {
      label: "Anticipos",
      value: currency.format(advancesTotal),
      sub: `${advances.length} adelantos`,
    },
    {
      label: "Choferes activos",
      value: number.format(activeDrivers),
      sub: `${number.format(state.data.drivers.length)} total`,
    },
    {
      label: "Flota operativa",
      value: number.format(operationalTrucks),
      sub: `${number.format(state.data.trucks.length)} camiones`,
    },
  ];

  const kpiContainer = $("kpis");
  kpiContainer.innerHTML = kpis
    .map(
      (kpi) => `
      <div class="kpi-card">
        <div class="kpi-label">${kpi.label}</div>
        <div class="kpi-value">${kpi.value}</div>
        <div class="kpi-sub">${kpi.sub}</div>
      </div>
    `
    )
    .join("");
}

function renderCharts() {
  const trips = state.filtered.trips;
  const expenses = state.filtered.expenses;
  const advances = state.filtered.advances;

  const revenueByMonth = groupByMonth(trips, "start_date", calcTripRevenue);
  const expensesByMonth = groupByMonth(expenses, "date", (e) =>
    Number(e.amount || 0)
  );
  const monthLabels = Array.from(
    new Set([...revenueByMonth, ...expensesByMonth].map((item) => item[0]))
  ).sort();

  const revenueSeries = monthLabels.map((label) => {
    const entry = revenueByMonth.find((item) => item[0] === label);
    return entry ? entry[1] : 0;
  });

  const expenseSeries = monthLabels.map((label) => {
    const entry = expensesByMonth.find((item) => item[0] === label);
    return entry ? entry[1] : 0;
  });

  const colors = getChartColors();
  buildChart("chartRevenue", "line", {
    labels: monthLabels,
    datasets: [
      {
        label: "Ingresos",
        data: revenueSeries,
        borderColor: colors.primary,
        backgroundColor: colors.primaryBg,
        tension: 0.35,
      },
      {
        label: "Gastos",
        data: expenseSeries,
        borderColor: colors.secondary,
        backgroundColor: colors.secondaryBg,
        tension: 0.35,
      },
    ],
  });

  const expenseTypes = new Map();
  expenses.forEach((expense) => {
    const rawKey =
      typeof expense.expense_type === "string"
        ? expense.expense_type.trim()
        : "";
    const normalizedKey = rawKey.toLowerCase();
    if (!rawKey || normalizedKey === "undefined" || normalizedKey === "none") {
      return;
    }
    const key = rawKey;
    expenseTypes.set(key, (expenseTypes.get(key) || 0) + Number(expense.amount));
  });
  const expenseLabels = Array.from(expenseTypes.keys());
  const expenseValues = expenseLabels.map((label) => expenseTypes.get(label));

  buildChart("chartExpenses", "doughnut", {
    labels: expenseLabels,
    datasets: [
      {
        data: expenseValues,
        backgroundColor: colors.doughnut,
      },
    ],
  });

  const tripsByState = new Map();
  trips.forEach((trip) => {
    const key = trip.state_id || "Sin estado";
    tripsByState.set(key, (tripsByState.get(key) || 0) + 1);
  });
  buildChart("chartTripState", "bar", {
    labels: Array.from(tripsByState.keys()),
    datasets: [
      {
        label: "Viajes",
        data: Array.from(tripsByState.values()),
        backgroundColor: colors.secondaryBar,
      },
    ],
  });

  const clientRevenue = new Map();
  trips.forEach((trip) => {
    const clientName = trip.client?.name || getClientName(trip.client_id);
    clientRevenue.set(
      clientName,
      (clientRevenue.get(clientName) || 0) + calcTripRevenue(trip)
    );
  });
  const topClients = Array.from(clientRevenue.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  buildChart("chartClients", "bar", {
    labels: topClients.map((item) => item[0]),
    datasets: [
      {
        label: "Ingresos",
        data: topClients.map((item) => item[1]),
        backgroundColor: colors.primaryBar,
      },
    ],
  });

  const advancesByDriver = new Map();
  advances.forEach((advance) => {
    const name = getDriverName(advance.driver_id);
    advancesByDriver.set(
      name,
      (advancesByDriver.get(name) || 0) + Number(advance.amount || 0)
    );
  });
  const advanceTop = Array.from(advancesByDriver.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 8);

  buildChart("chartAdvances", "bar", {
    labels: advanceTop.map((item) => item[0]),
    datasets: [
      {
        label: "Anticipos",
        data: advanceTop.map((item) => item[1]),
        backgroundColor: colors.secondaryBar,
      },
    ],
  });
}

function buildChart(id, type, data) {
  const element = $(id);
  if (!element) return;

  if (state.charts[id]) {
    state.charts[id].destroy();
  }

  const isCountChart = id === "chartTripState";
  const isDoughnut = type === "doughnut";
  const enableZoom = id === "chartRevenue";
  const formatValue = (value) =>
    isCountChart ? number.format(value) : currency.format(value);

  state.charts[id] = new Chart(element, {
    type,
    data,
    options: {
      responsive: true,
      maintainAspectRatio: !isDoughnut,
      aspectRatio: isDoughnut ? 1.1 : undefined,
      plugins: {
        legend: { display: type !== "bar" || id === "chartRevenue" },
        tooltip: {
          callbacks: {
            label: (context) => {
              const value = context.parsed.y ?? context.parsed;
              const label = context.label || context.dataset.label || "";
              if (typeof value === "number") {
                return label
                  ? `${label}: ${formatValue(value)}`
                  : `${formatValue(value)}`;
              }
              return label;
            },
          },
        },
        zoom: enableZoom
          ? {
              pan: {
                enabled: true,
                mode: "x",
              },
              zoom: {
                wheel: {
                  enabled: true,
                },
                pinch: {
                  enabled: true,
                },
                mode: "x",
              },
            }
          : undefined,
      },
      scales:
        type === "doughnut"
          ? {}
          : {
              y: {
                ticks: {
                  callback: (value) => formatValue(value),
                },
              },
            },
    },
  });
}

function renderTables() {
  renderTripTable();
  renderMarginTable();
  renderExpenseTable();
  renderServiceTable();
  renderAdvanceTable();
  renderClientTable();
}

function renderTripTable() {
  const rows = state.filtered.trips
    .slice()
    .sort((a, b) => (b.start_date || "").localeCompare(a.start_date || ""))
    .slice(0, 10)
    .map((trip) => {
      const route = `${trip.origin} - ${trip.destination}`;
      return [
        trip.start_date || "-",
        trip.client?.name || getClientName(trip.client_id),
        route,
        currency.format(calcTripRevenue(trip)),
      ];
    });

  renderTable($("tableTrips"), ["Fecha", "Cliente", "Ruta", "Ingreso"], rows);
}

function renderMarginTable() {
  const expensesByTrip = new Map();
  state.filtered.expenses.forEach((expense) => {
    if (!expense.trip_id) return;
    expensesByTrip.set(
      expense.trip_id,
      (expensesByTrip.get(expense.trip_id) || 0) + Number(expense.amount || 0)
    );
  });

  const rows = state.filtered.trips
    .map((trip) => {
      const revenue = calcTripRevenue(trip);
      const cost = expensesByTrip.get(trip.id) || 0;
      const margin = revenue - cost;
      return {
        trip,
        margin,
      };
    })
    .sort((a, b) => a.margin - b.margin)
    .slice(0, 5)
    .map(({ trip, margin }) => [
      `#${trip.id}`,
      getDriverName(trip.driver_id),
      currency.format(margin),
      trip.state_id || "-",
    ]);

  renderTable(
    $("tableMargins"),
    ["Viaje", "Chofer", "Margen", "Estado"],
    rows
  );
}

function renderExpenseTable() {
  const rows = state.filtered.expenses
    .slice()
    .sort((a, b) => (b.date || "").localeCompare(a.date || ""))
    .slice(0, 12)
    .map((expense) => [
      expense.date || "-",
      expense.expense_type || "-",
      currency.format(expense.amount || 0),
      getDriverName(expense.driver_id),
    ]);

  renderTable(
    $("tableExpenses"),
    ["Fecha", "Tipo", "Monto", "Chofer"],
    rows
  );
}

function renderServiceTable() {
  const soon = [];
  const now = new Date();
  const threshold = new Date();
  threshold.setDate(threshold.getDate() + 30);

  state.data.trucks.forEach((truck) => {
    const checks = [
      { label: "Service", date: truck.service_due_date },
      { label: "VTV", date: truck.vtv_due_date },
      { label: "Patente", date: truck.plate_due_date },
    ];

    checks.forEach((check) => {
      const date = parseDate(check.date);
      if (date && date <= threshold) {
        soon.push({
          truck,
          label: check.label,
          date: check.date,
        });
      }
    });
  });

  const rows = soon.slice(0, 8).map((item) => [
    item.truck.plate,
    item.label,
    item.date,
    item.truck.operational ? "OK" : "No",
  ]);

  renderTable(
    $("tableServices"),
    ["Camion", "Tipo", "Vence", "Operativo"],
    rows
  );

  const fleetKpis = $("fleetKpis");
  fleetKpis.innerHTML = [
    {
      label: "Operativos",
      value: state.data.trucks.filter((t) => t.operational).length,
    },
    { label: "Total", value: state.data.trucks.length },
    {
      label: "Choferes activos",
      value: state.data.drivers.filter((d) => d.active).length,
    },
  ]
    .map(
      (item) => `
      <div class="kpi-pill">
        <span>${item.label}</span>
        <strong>${number.format(item.value)}</strong>
      </div>
    `
    )
    .join("");
}

function renderAdvanceTable() {
  const rows = state.filtered.advances
    .slice()
    .sort((a, b) => (b.date || "").localeCompare(a.date || ""))
    .slice(0, 12)
    .map((advance) => [
      advance.date || "-",
      getDriverName(advance.driver_id),
      currency.format(advance.amount || 0),
    ]);

  renderTable(
    $("tableAdvances"),
    ["Fecha", "Chofer", "Monto"],
    rows
  );
}

function renderClientTable() {
  const clientTotals = new Map();
  const clientTrips = new Map();

  state.filtered.trips.forEach((trip) => {
    const clientName = trip.client?.name || getClientName(trip.client_id);
    clientTotals.set(
      clientName,
      (clientTotals.get(clientName) || 0) + calcTripRevenue(trip)
    );
    clientTrips.set(clientName, (clientTrips.get(clientName) || 0) + 1);
  });

  const rows = Array.from(clientTotals.entries())
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map((entry) => [
      entry[0],
      number.format(clientTrips.get(entry[0]) || 0),
      currency.format(entry[1]),
      entry[1] > 0 ? "Activo" : "-",
    ]);

  renderTable(
    $("tableClients"),
    ["Cliente", "Viajes", "Ingreso", "Estado"],
    rows
  );

  const totalClients = state.data.clients.length;
  const activeClients = clientTotals.size;
  const clientKpis = $("clientKpis");
  clientKpis.innerHTML = [
    { label: "Clientes activos", value: activeClients },
    { label: "Total clientes", value: totalClients },
  ]
    .map(
      (item) => `
      <div class="kpi-pill">
        <span>${item.label}</span>
        <strong>${number.format(item.value)}</strong>
      </div>
    `
    )
    .join("");
}

function renderTable(container, headers, rows) {
  if (!container) return;
  if (!rows.length) {
    container.innerHTML = `<div class="table-row">Sin datos</div>`;
    return;
  }

  const headerRow = `
    <div class="table-row header">
      ${headers.map((h) => `<div>${h}</div>`).join("")}
    </div>
  `;

  const bodyRows = rows
    .map(
      (row) => `
      <div class="table-row">
        ${row.map((cell) => `<div>${cell}</div>`).join("")}
      </div>
    `
    )
    .join("");

  container.innerHTML = headerRow + bodyRows;
}

function render() {
  renderKpis();
  renderCharts();
  renderTables();
}

function bindEvents() {
  document.querySelectorAll(".nav-item").forEach((item) => {
    item.addEventListener("click", () => {
      document.querySelectorAll(".nav-item").forEach((btn) => {
        btn.classList.remove("active");
      });
      item.classList.add("active");

      const view = item.dataset.view;
      document.querySelectorAll(".view").forEach((section) => {
        section.classList.toggle("active", section.id === view);
      });
    });
  });

  $("applyFilters").addEventListener("click", applyFilters);
  $("resetFilters").addEventListener("click", resetFilters);
  $("reloadBtn").addEventListener("click", loadData);
  $("themeToggle").addEventListener("click", toggleTheme);
  $("logoutBtn").addEventListener("click", () => {
    clearToken();
    window.location.href = "login.html";
  });

  const modal = $("chartModal");
  const modalBody = $("chartModalBody");
  const modalTitle = $("chartModalTitle");
  const modalClose = $("chartModalClose");
  const modalBackdrop = modal.querySelector(".chart-modal__backdrop");

  function closeModal() {
    if (!state.modal.activeChartId) return;
    const chartId = state.modal.activeChartId;
    const canvas = $(chartId);
    if (canvas && state.modal.originalParent) {
      if (state.modal.originalNext) {
        state.modal.originalParent.insertBefore(
          canvas,
          state.modal.originalNext
        );
      } else {
        state.modal.originalParent.appendChild(canvas);
      }
    }
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
    state.modal.activeChartId = null;
    state.modal.originalParent = null;
    state.modal.originalNext = null;

    if (canvas && state.charts[chartId]) {
      state.charts[chartId].resize();
    }
  }

  document.querySelectorAll(".chart-expand").forEach((button) => {
    button.addEventListener("click", () => {
      const chartId = button.dataset.chart;
      const canvas = $(chartId);
      if (!canvas) return;

      state.modal.activeChartId = chartId;
      state.modal.originalParent = canvas.parentElement;
      state.modal.originalNext = canvas.nextElementSibling;

      const cardTitle =
        canvas.closest(".card")?.querySelector("h3")?.textContent || "Grafico";
      modalTitle.textContent = cardTitle;

      modalBody.appendChild(canvas);
      modal.classList.add("active");
      modal.setAttribute("aria-hidden", "false");

      if (state.charts[chartId]) {
        state.charts[chartId].resize();
      }
    });
  });

  modalClose.addEventListener("click", closeModal);
  modalBackdrop.addEventListener("click", closeModal);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      closeModal();
    }
  });
}

async function bootstrap() {
  const token = getToken();
  if (!token) {
    window.location.href = "login.html";
    return;
  }

  setStatus("Validando sesion...", "info");
  try {
    const response = await fetch(`${getBaseUrl()}/auth/me`, {
      headers: { Authorization: `Bearer ${token}` },
    });

    if (!response.ok) {
      throw new Error("Token invalido");
    }

    const user = await response.json();
    if (!user.is_admin) {
      clearToken();
      window.location.href = "login.html";
      return;
    }

    setStatus(`Sesion activa. Hola ${user.name || "admin"}`, "ok");
    loadData();
  } catch (error) {
    clearToken();
    window.location.href = "login.html";
  }
}

initTheme();
bindEvents();
bootstrap();
