// Módulo Dashboard para ForensicWeb

class Dashboard {
    constructor() {
        this.charts = {};
        this.stats = {};
        this.refreshInterval = null;
    }

    async init() {
        await this.loadDashboardData();
        this.setupAutoRefresh();
    }

    async loadDashboardData() {
        try {
            // Cargar estadísticas principales
            await this.loadStats();
            
            // Cargar actividad reciente
            await this.loadRecentActivity();
            
            // Cargar casos pendientes
            await this.loadPendingCases();
            
            // Cargar gráficos
            await this.loadCharts();
            
        } catch (error) {
            handleAPIError(error, 'carga del dashboard');
        }
    }

    async loadStats() {
        try {
            const response = await api.getDashboardStats();
            this.stats = response;
            this.renderStats();
        } catch (error) {
            console.error('Error loading stats:', error);
        }
    }

    renderStats() {
        const statsHTML = `
            <div class="stats-grid">
                <div class="stat-card">
                    <h3 class="stat-number">${this.stats.basic_stats?.total_cases || 0}</h3>
                    <p class="stat-label">Total de Casos</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-number">${this.stats.basic_stats?.active_cases || 0}</h3>
                    <p class="stat-label">Casos Activos</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-number">${this.stats.basic_stats?.total_clients || 0}</h3>
                    <p class="stat-label">Total de Clientes</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-number">${this.stats.basic_stats?.total_equipment || 0}</h3>
                    <p class="stat-label">Equipos Registrados</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-number">${this.stats.case_stats?.urgent || 0}</h3>
                    <p class="stat-label">Casos Urgentes</p>
                </div>
                <div class="stat-card">
                    <h3 class="stat-number">${formatCurrency(this.stats.financial?.monthly_income || 0)}</h3>
                    <p class="stat-label">Ingresos del Mes</p>
                </div>
            </div>
        `;

        const statsContainer = document.getElementById('dashboard-stats');
        if (statsContainer) {
            statsContainer.innerHTML = statsHTML;
        }
    }

    async loadRecentActivity() {
        try {
            const response = await api.getRecentActivity();
            this.renderRecentActivity(response.activity);
        } catch (error) {
            console.error('Error loading recent activity:', error);
        }
    }

    renderRecentActivity(activities) {
        const activityHTML = activities.map(activity => {
            const timeAgo = this.getTimeAgo(activity.time);
            const iconClass = this.getActivityIcon(activity.type);
            
            return `
                <div class="activity-item">
                    <div class="activity-icon ${iconClass}"></div>
                    <div class="activity-content">
                        <p class="activity-description">${activity.description}</p>
                        <span class="activity-time">${timeAgo}</span>
                    </div>
                </div>
            `;
        }).join('');

        const activityContainer = document.getElementById('recent-activity');
        if (activityContainer) {
            activityContainer.innerHTML = activityHTML || '<p>No hay actividad reciente</p>';
        }
    }

    async loadPendingCases() {
        try {
            const response = await api.getPendingCases();
            this.renderPendingCases(response.pending_cases);
        } catch (error) {
            console.error('Error loading pending cases:', error);
        }
    }

    renderPendingCases(cases) {
        const casesHTML = cases.map(case_ => {
            const priorityClass = this.getPriorityClass(case_.prioridad);
            const statusClass = this.getStatusClass(case_.estado);
            
            return `
                <tr>
                    <td>${case_.numero_caso}</td>
                    <td>${case_.titulo}</td>
                    <td>${case_.cliente_nombre || 'N/A'}</td>
                    <td><span class="badge ${statusClass}">${case_.estado}</span></td>
                    <td><span class="badge ${priorityClass}">${case_.prioridad}</span></td>
                    <td>${case_.days_open} días</td>
                    <td>
                        <button class="btn btn-sm" onclick="viewCase(${case_.id})">Ver</button>
                    </td>
                </tr>
            `;
        }).join('');

        const casesContainer = document.getElementById('pending-cases-table');
        if (casesContainer) {
            casesContainer.innerHTML = casesHTML || '<tr><td colspan="7">No hay casos pendientes</td></tr>';
        }
    }

    async loadCharts() {
        try {
            // Cargar datos para todos los gráficos
            const [casesByMonth, casesByStatus, revenueByMonth] = await Promise.all([
                api.getCasesByMonth(),
                api.getCasesByStatus(),
                api.getRevenueByMonth()
            ]);

            // Renderizar gráficos
            this.renderCasesByMonthChart(casesByMonth);
            this.renderCasesByStatusChart(casesByStatus);
            this.renderRevenueChart(revenueByMonth);
            
        } catch (error) {
            console.error('Error loading charts:', error);
        }
    }

    renderCasesByMonthChart(data) {
        const ctx = document.getElementById('cases-by-month-chart');
        if (!ctx) return;

        if (this.charts.casesByMonth) {
            this.charts.casesByMonth.destroy();
        }

        this.charts.casesByMonth = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Casos por Mes',
                    data: data.data,
                    borderColor: '#3498db',
                    backgroundColor: 'rgba(52, 152, 219, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }

    renderCasesByStatusChart(data) {
        const ctx = document.getElementById('cases-by-status-chart');
        if (!ctx) return;

        if (this.charts.casesByStatus) {
            this.charts.casesByStatus.destroy();
        }

        this.charts.casesByStatus = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: data.labels,
                datasets: [{
                    data: data.data,
                    backgroundColor: data.colors,
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    renderRevenueChart(data) {
        const ctx = document.getElementById('revenue-chart');
        if (!ctx) return;

        if (this.charts.revenue) {
            this.charts.revenue.destroy();
        }

        this.charts.revenue = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: data.labels,
                datasets: [{
                    label: 'Ingresos (€)',
                    data: data.data,
                    backgroundColor: 'rgba(39, 174, 96, 0.8)',
                    borderColor: '#27ae60',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            callback: function(value) {
                                return formatCurrency(value);
                            }
                        }
                    }
                }
            }
        });
    }

    setupAutoRefresh() {
        // Refrescar datos cada 5 minutos
        this.refreshInterval = setInterval(() => {
            this.loadDashboardData();
        }, 5 * 60 * 1000);
    }

    destroy() {
        // Limpiar gráficos
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
        this.charts = {};

        // Limpiar interval
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
        }
    }

    // Utilidades
    getTimeAgo(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) return 'Hace un momento';
        if (diffInSeconds < 3600) return `Hace ${Math.floor(diffInSeconds / 60)} minutos`;
        if (diffInSeconds < 86400) return `Hace ${Math.floor(diffInSeconds / 3600)} horas`;
        return `Hace ${Math.floor(diffInSeconds / 86400)} días`;
    }

    getActivityIcon(type) {
        const icons = {
            case: 'icon-case',
            client: 'icon-client',
            contact: 'icon-contact',
            equipment: 'icon-equipment'
        };
        return icons[type] || 'icon-default';
    }

    getPriorityClass(priority) {
        const classes = {
            baja: 'badge-success',
            media: 'badge-warning',
            alta: 'badge-danger',
            urgente: 'badge-critical'
        };
        return classes[priority] || 'badge-secondary';
    }

    getStatusClass(status) {
        const classes = {
            pendiente: 'badge-warning',
            en_proceso: 'badge-info',
            cerrado: 'badge-success',
            archivado: 'badge-secondary'
        };
        return classes[status] || 'badge-secondary';
    }

    // Método para renderizar el contenido completo del dashboard
    render() {
        return `
            <div id="dashboard-stats"></div>
            
            <div class="dashboard-grid">
                <div class="dashboard-section">
                    <h3>Actividad Reciente</h3>
                    <div id="recent-activity" class="activity-list">
                        <div class="loading">
                            <div class="spinner"></div>
                            <p>Cargando actividad...</p>
                        </div>
                    </div>
                </div>
                
                <div class="dashboard-section">
                    <h3>Casos Pendientes</h3>
                    <div class="table-container">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Número</th>
                                    <th>Título</th>
                                    <th>Cliente</th>
                                    <th>Estado</th>
                                    <th>Prioridad</th>
                                    <th>Días Abierto</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody id="pending-cases-table">
                                <tr><td colspan="7">Cargando casos...</td></tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
            
            <div class="charts-grid">
                <div class="chart-container">
                    <h3>Casos por Mes</h3>
                    <canvas id="cases-by-month-chart" height="300"></canvas>
                </div>
                
                <div class="chart-container">
                    <h3>Casos por Estado</h3>
                    <canvas id="cases-by-status-chart" height="300"></canvas>
                </div>
                
                <div class="chart-container">
                    <h3>Ingresos por Mes</h3>
                    <canvas id="revenue-chart" height="300"></canvas>
                </div>
            </div>
        `;
    }
}

// Crear instancia global del dashboard
window.dashboard = new Dashboard();

// Función global para ver caso (usada en el HTML)
window.viewCase = function(caseId) {
    if (window.app && window.app.loadPage) {
        window.app.loadPage('cases', { caseId });
    }
};

console.log('Dashboard module loaded successfully');

