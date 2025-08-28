// Módulo API para ForensicWeb Dashboard

class API {
    constructor() {
        this.baseURL = '/api';
        this.defaultHeaders = {
            'Content-Type': 'application/json'
        };
    }

    // Método genérico para hacer requests
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: this.defaultHeaders,
            credentials: 'include', // Para incluir cookies de sesión
            ...options
        };

        try {
            const response = await fetch(url, config);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || `HTTP error! status: ${response.status}`);
            }

            return data;
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }

    // Métodos de autenticación
    async login(email, password) {
        return this.request('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, password })
        });
    }

    async logout() {
        return this.request('/auth/logout', {
            method: 'POST'
        });
    }

    async checkAuth() {
        return this.request('/auth/check');
    }

    async getProfile() {
        return this.request('/auth/profile');
    }

    // Métodos del dashboard
    async getDashboardStats() {
        return this.request('/dashboard/stats');
    }

    async getRecentActivity() {
        return this.request('/dashboard/recent-activity');
    }

    async getPendingCases() {
        return this.request('/dashboard/pending-cases');
    }

    // Métodos para gráficos
    async getCasesByMonth() {
        return this.request('/dashboard/charts/cases-by-month');
    }

    async getCasesByStatus() {
        return this.request('/dashboard/charts/cases-by-status');
    }

    async getRevenueByMonth() {
        return this.request('/dashboard/charts/revenue-by-month');
    }

    // Métodos de casos
    async getCases(page = 1, perPage = 10, estado = null) {
        let endpoint = `/cases?page=${page}&per_page=${perPage}`;
        if (estado) {
            endpoint += `&estado=${estado}`;
        }
        return this.request(endpoint);
    }

    async getCase(id) {
        return this.request(`/cases/${id}`);
    }

    async createCase(caseData) {
        return this.request('/cases', {
            method: 'POST',
            body: JSON.stringify(caseData)
        });
    }

    async updateCase(id, caseData) {
        return this.request(`/cases/${id}`, {
            method: 'PUT',
            body: JSON.stringify(caseData)
        });
    }

    async deleteCase(id) {
        return this.request(`/cases/${id}`, {
            method: 'DELETE'
        });
    }

    async addEquipment(caseId, equipmentData) {
        return this.request(`/cases/${caseId}/equipment`, {
            method: 'POST',
            body: JSON.stringify(equipmentData)
        });
    }

    async getCaseStats() {
        return this.request('/cases/stats');
    }

    // Métodos de clientes
    async getClients(page = 1, perPage = 10, search = '') {
        let endpoint = `/clients?page=${page}&per_page=${perPage}`;
        if (search) {
            endpoint += `&search=${encodeURIComponent(search)}`;
        }
        return this.request(endpoint);
    }

    async getClient(id) {
        return this.request(`/clients/${id}`);
    }

    async createClient(clientData) {
        return this.request('/clients', {
            method: 'POST',
            body: JSON.stringify(clientData)
        });
    }

    async updateClient(id, clientData) {
        return this.request(`/clients/${id}`, {
            method: 'PUT',
            body: JSON.stringify(clientData)
        });
    }

    async deleteClient(id) {
        return this.request(`/clients/${id}`, {
            method: 'DELETE'
        });
    }

    async getClientStats() {
        return this.request('/clients/stats');
    }

    // Métodos de contacto
    async getContacts(page = 1, perPage = 10, unreadOnly = false) {
        let endpoint = `/contact?page=${page}&per_page=${perPage}`;
        if (unreadOnly) {
            endpoint += '&unread_only=true';
        }
        return this.request(endpoint);
    }

    async markContactAsRead(id) {
        return this.request(`/contact/${id}/read`, {
            method: 'PUT'
        });
    }

    async getContactStats() {
        return this.request('/contact/stats');
    }

    // Método para enviar mensaje de contacto (desde el sitio público)
    async submitContact(contactData) {
        return this.request('/contact', {
            method: 'POST',
            body: JSON.stringify(contactData)
        });
    }

    // Método de verificación de salud de la API
    async healthCheck() {
        return this.request('/health');
    }
}

// Crear instancia global de la API
window.api = new API();

// Utilidades para manejo de errores
window.handleAPIError = function(error, context = '') {
    console.error(`Error en ${context}:`, error);
    
    // Mostrar notificación de error al usuario
    if (window.showNotification) {
        let message = 'Error de conexión';
        
        if (error.message.includes('401') || error.message.includes('Autenticación')) {
            message = 'Sesión expirada. Por favor, inicia sesión nuevamente.';
            // Redirigir al login
            if (window.auth && window.auth.showLogin) {
                window.auth.showLogin();
            }
        } else if (error.message.includes('403')) {
            message = 'No tienes permisos para realizar esta acción.';
        } else if (error.message.includes('404')) {
            message = 'Recurso no encontrado.';
        } else if (error.message.includes('500')) {
            message = 'Error interno del servidor.';
        } else {
            message = error.message || 'Error desconocido';
        }
        
        window.showNotification(message, 'error');
    }
    
    return error;
};

// Utilidad para mostrar notificaciones
window.showNotification = function(message, type = 'info') {
    // Crear elemento de notificación
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Estilos
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 8px;
        color: white;
        z-index: 1000;
        opacity: 0;
        transition: opacity 0.3s ease;
        max-width: 300px;
        word-wrap: break-word;
    `;

    // Colores según el tipo
    const colors = {
        info: '#3498db',
        success: '#27ae60',
        warning: '#f39c12',
        error: '#e74c3c'
    };
    notification.style.backgroundColor = colors[type] || colors.info;

    document.body.appendChild(notification);
    
    // Mostrar con animación
    setTimeout(() => notification.style.opacity = '1', 100);
    
    // Ocultar después de 5 segundos
    setTimeout(() => {
        notification.style.opacity = '0';
        setTimeout(() => {
            if (document.body.contains(notification)) {
                document.body.removeChild(notification);
            }
        }, 300);
    }, 5000);
};

// Utilidad para formatear fechas
window.formatDate = function(dateString) {
    if (!dateString) return 'N/A';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
};

// Utilidad para formatear números como moneda
window.formatCurrency = function(amount) {
    return new Intl.NumberFormat('es-ES', {
        style: 'currency',
        currency: 'EUR'
    }).format(amount);
};

console.log('API module loaded successfully');

