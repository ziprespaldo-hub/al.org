// Aplicación Principal ForensicWeb Dashboard

class App {
    constructor() {
        this.currentPage = 'dashboard';
        this.pageData = {};
        this.init();
    }

    init() {
        this.setupNavigation();
        this.setupEventListeners();
        
        // Esperar a que la autenticación esté lista
        this.waitForAuth();
    }

    async waitForAuth() {
        // Esperar hasta que el módulo de autenticación esté listo
        const checkAuth = () => {
            if (window.auth && window.auth.isAuthenticated !== undefined) {
                if (window.auth.isAuthenticated) {
                    this.loadPage('dashboard');
                } else {
                    // El módulo de auth ya manejará mostrar el login
                }
            } else {
                setTimeout(checkAuth, 100);
            }
        };
        checkAuth();
    }

    setupNavigation() {
        // Configurar navegación del header
        const headerLinks = document.querySelectorAll('.header-nav .nav-link');
        headerLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                if (page) {
                    this.loadPage(page);
                }
            });
        });

        // Configurar navegación del sidebar
        const sidebarLinks = document.querySelectorAll('.sidebar-nav .sidebar-link');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const page = link.getAttribute('data-page');
                if (page) {
                    this.loadPage(page);
                }
            });
        });
    }

    setupEventListeners() {
        // Cerrar modal al hacer clic fuera
        window.addEventListener('click', (e) => {
            const modal = document.getElementById('login-modal');
            if (e.target === modal) {
                // No cerrar el modal de login automáticamente
                // modal.style.display = 'none';
            }
        });

        // Manejar tecla Escape
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const modal = document.getElementById('login-modal');
                if (modal && modal.style.display === 'flex') {
                    // No cerrar el modal de login con Escape si no está autenticado
                    if (window.auth && window.auth.isAuthenticated) {
                        modal.style.display = 'none';
                    }
                }
            }
        });
    }

    async loadPage(pageName, data = {}) {
        // Verificar autenticación
        if (!window.auth || !window.auth.isAuthenticated) {
            window.auth.showLogin();
            return;
        }

        this.currentPage = pageName;
        this.pageData = data;

        // Actualizar navegación activa
        this.updateActiveNavigation(pageName);

        // Actualizar título y breadcrumb
        this.updatePageHeader(pageName);

        // Mostrar loading
        this.showLoading();

        try {
            // Cargar contenido de la página
            await this.renderPage(pageName, data);
        } catch (error) {
            handleAPIError(error, `carga de página ${pageName}`);
            this.showError('Error al cargar la página');
        }
    }

    updateActiveNavigation(pageName) {
        // Actualizar header navigation
        const headerLinks = document.querySelectorAll('.header-nav .nav-link');
        headerLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === pageName) {
                link.classList.add('active');
            }
        });

        // Actualizar sidebar navigation
        const sidebarLinks = document.querySelectorAll('.sidebar-nav .sidebar-link');
        sidebarLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('data-page') === pageName) {
                link.classList.add('active');
            }
        });
    }

    updatePageHeader(pageName) {
        const titles = {
            dashboard: 'Dashboard',
            stats: 'Estadísticas',
            cases: 'Gestión de Casos',
            clients: 'Gestión de Clientes',
            equipment: 'Gestión de Equipos',
            contacts: 'Mensajes de Contacto',
            calendar: 'Agenda Legal'
        };

        const breadcrumbs = {
            dashboard: 'Dashboard',
            stats: 'Dashboard > Estadísticas',
            cases: 'Gestión > Casos',
            clients: 'Gestión > Clientes',
            equipment: 'Gestión > Equipos',
            contacts: 'Comunicación > Mensajes',
            calendar: 'Comunicación > Agenda'
        };

        const titleElement = document.getElementById('page-title');
        const breadcrumbElement = document.getElementById('breadcrumb-content');

        if (titleElement) {
            titleElement.textContent = titles[pageName] || 'Página';
        }

        if (breadcrumbElement) {
            breadcrumbElement.textContent = breadcrumbs[pageName] || 'Dashboard';
        }
    }

    showLoading() {
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="loading">
                    <div class="spinner"></div>
                    <p>Cargando...</p>
                </div>
            `;
        }
    }

    showError(message) {
        const mainContent = document.getElementById('main-content');
        if (mainContent) {
            mainContent.innerHTML = `
                <div class="error-message">
                    <h3>Error</h3>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="app.loadPage('dashboard')">
                        Volver al Dashboard
                    </button>
                </div>
            `;
        }
    }

    async renderPage(pageName, data) {
        const mainContent = document.getElementById('main-content');
        if (!mainContent) return;

        let content = '';

        switch (pageName) {
            case 'dashboard':
                content = window.dashboard.render();
                mainContent.innerHTML = content;
                await window.dashboard.init();
                break;

            case 'stats':
                content = await this.renderStatsPage();
                mainContent.innerHTML = content;
                break;

            case 'cases':
                content = await this.renderCasesPage(data);
                mainContent.innerHTML = content;
                break;

            case 'clients':
                content = await this.renderClientsPage(data);
                mainContent.innerHTML = content;
                break;

            case 'equipment':
                content = await this.renderEquipmentPage(data);
                mainContent.innerHTML = content;
                break;

            case 'contacts':
                content = await this.renderContactsPage(data);
                mainContent.innerHTML = content;
                break;

            case 'calendar':
                content = await this.renderCalendarPage(data);
                mainContent.innerHTML = content;
                break;

            default:
                content = `
                    <div class="page-placeholder">
                        <h3>Página en Desarrollo</h3>
                        <p>La página "${pageName}" está en desarrollo.</p>
                        <button class="btn btn-primary" onclick="app.loadPage('dashboard')">
                            Volver al Dashboard
                        </button>
                    </div>
                `;
                mainContent.innerHTML = content;
        }
    }

    async renderStatsPage() {
        return `
            <div class="stats-page">
                <h3>Estadísticas Detalladas</h3>
                <p>Esta página mostrará estadísticas detalladas del sistema.</p>
                <div class="charts-grid">
                    <div class="chart-container">
                        <h4>Gráfico de Rendimiento</h4>
                        <p>Gráfico en desarrollo...</p>
                    </div>
                </div>
            </div>
        `;
    }

    async renderCasesPage(data) {
        try {
            const response = await api.getCases();
            const cases = response.cases || [];

            const casesHTML = cases.map(case_ => `
                <tr>
                    <td>${case_.numero_caso}</td>
                    <td>${case_.titulo}</td>
                    <td>${case_.cliente_nombre || 'N/A'}</td>
                    <td><span class="badge badge-${case_.estado}">${case_.estado}</span></td>
                    <td><span class="badge badge-${case_.prioridad}">${case_.prioridad}</span></td>
                    <td>${formatDate(case_.fecha_apertura)}</td>
                    <td>
                        <button class="btn btn-sm" onclick="viewCase(${case_.id})">Ver</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteCase(${case_.id})">Eliminar</button>
                    </td>
                </tr>
            `).join('');

            return `
                <div class="cases-page">
                    <div class="page-actions">
                        <button class="btn btn-primary" onclick="createNewCase()">Nuevo Caso</button>
                    </div>
                    
                    <div class="table-container">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Número</th>
                                    <th>Título</th>
                                    <th>Cliente</th>
                                    <th>Estado</th>
                                    <th>Prioridad</th>
                                    <th>Fecha Apertura</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${casesHTML || '<tr><td colspan="7">No hay casos registrados</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            return `<div class="error">Error al cargar casos: ${error.message}</div>`;
        }
    }

    async renderClientsPage(data) {
        try {
            const response = await api.getClients();
            const clients = response.clients || [];

            const clientsHTML = clients.map(client => `
                <tr>
                    <td>${client.nombre_completo}</td>
                    <td>${client.email}</td>
                    <td>${client.telefono || 'N/A'}</td>
                    <td>${formatDate(client.fecha_registro)}</td>
                    <td>
                        <button class="btn btn-sm" onclick="viewClient(${client.id})">Ver</button>
                        <button class="btn btn-sm btn-danger" onclick="deleteClient(${client.id})">Eliminar</button>
                    </td>
                </tr>
            `).join('');

            return `
                <div class="clients-page">
                    <div class="page-actions">
                        <button class="btn btn-primary" onclick="createNewClient()">Nuevo Cliente</button>
                    </div>
                    
                    <div class="table-container">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Email</th>
                                    <th>Teléfono</th>
                                    <th>Fecha Registro</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${clientsHTML || '<tr><td colspan="5">No hay clientes registrados</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            return `<div class="error">Error al cargar clientes: ${error.message}</div>`;
        }
    }

    async renderEquipmentPage(data) {
        return `
            <div class="equipment-page">
                <h3>Gestión de Equipos</h3>
                <p>Esta página mostrará la gestión de equipos forenses.</p>
                <div class="page-actions">
                    <button class="btn btn-primary">Registrar Equipo</button>
                </div>
            </div>
        `;
    }

    async renderContactsPage(data) {
        try {
            const response = await api.getContacts();
            const contacts = response.contacts || [];

            const contactsHTML = contacts.map(contact => `
                <tr class="${contact.leido ? '' : 'unread'}">
                    <td>${contact.nombre}</td>
                    <td>${contact.email}</td>
                    <td>${contact.asunto || 'Sin asunto'}</td>
                    <td>${formatDate(contact.fecha_envio)}</td>
                    <td>${contact.leido ? 'Leído' : 'No leído'}</td>
                    <td>
                        <button class="btn btn-sm" onclick="viewContact(${contact.id})">Ver</button>
                        ${!contact.leido ? `<button class="btn btn-sm" onclick="markAsRead(${contact.id})">Marcar Leído</button>` : ''}
                    </td>
                </tr>
            `).join('');

            return `
                <div class="contacts-page">
                    <div class="table-container">
                        <table class="table">
                            <thead>
                                <tr>
                                    <th>Nombre</th>
                                    <th>Email</th>
                                    <th>Asunto</th>
                                    <th>Fecha</th>
                                    <th>Estado</th>
                                    <th>Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${contactsHTML || '<tr><td colspan="6">No hay mensajes</td></tr>'}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        } catch (error) {
            return `<div class="error">Error al cargar mensajes: ${error.message}</div>`;
        }
    }

    async renderCalendarPage(data) {
        return `
            <div class="calendar-page">
                <h3>Agenda Legal</h3>
                <p>Esta página mostrará el calendario de eventos legales.</p>
                <div class="page-actions">
                    <button class="btn btn-primary">Nuevo Evento</button>
                </div>
            </div>
        `;
    }
}

// Crear instancia global de la aplicación
window.app = new App();

// Funciones globales para acciones (usadas en el HTML)
window.createNewCase = function() {
    showNotification('Función de crear caso en desarrollo', 'info');
};

window.createNewClient = function() {
    showNotification('Función de crear cliente en desarrollo', 'info');
};

window.viewClient = function(clientId) {
    showNotification(`Ver cliente ${clientId} - En desarrollo`, 'info');
};

window.deleteClient = function(clientId) {
    if (confirm('¿Estás seguro de que quieres eliminar este cliente?')) {
        showNotification(`Eliminar cliente ${clientId} - En desarrollo`, 'info');
    }
};

window.deleteCase = function(caseId) {
    if (confirm('¿Estás seguro de que quieres eliminar este caso?')) {
        showNotification(`Eliminar caso ${caseId} - En desarrollo`, 'info');
    }
};

window.viewContact = function(contactId) {
    showNotification(`Ver mensaje ${contactId} - En desarrollo`, 'info');
};

window.markAsRead = function(contactId) {
    api.markContactAsRead(contactId)
        .then(() => {
            showNotification('Mensaje marcado como leído', 'success');
            app.loadPage('contacts');
        })
        .catch(error => handleAPIError(error, 'marcar mensaje como leído'));
};

console.log('App module loaded successfully');

