// Módulo de Autenticación para ForensicWeb Dashboard

class Auth {
    constructor() {
        this.currentUser = null;
        this.isAuthenticated = false;
        this.loginModal = null;
        this.init();
    }

    init() {
        this.loginModal = document.getElementById('login-modal');
        this.setupLoginForm();
        this.checkAuthStatus();
    }

    setupLoginForm() {
        const loginForm = document.getElementById('login-form');
        if (loginForm) {
            loginForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleLogin();
            });
        }
    }

    async checkAuthStatus() {
        try {
            const response = await api.checkAuth();
            if (response.authenticated) {
                this.setUser(response.user);
                this.hideLogin();
            } else {
                this.showLogin();
            }
        } catch (error) {
            console.error('Error checking auth status:', error);
            this.showLogin();
        }
    }

    async handleLogin() {
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        if (!email || !password) {
            showNotification('Por favor, completa todos los campos', 'warning');
            return;
        }

        try {
            // Mostrar loading
            const submitBtn = document.querySelector('#login-form button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Iniciando sesión...';
            submitBtn.disabled = true;

            const response = await api.login(email, password);
            
            if (response.success) {
                this.setUser(response.user);
                this.hideLogin();
                showNotification('Sesión iniciada correctamente', 'success');
                
                // Cargar el dashboard
                if (window.app && window.app.loadPage) {
                    window.app.loadPage('dashboard');
                }
            }
        } catch (error) {
            handleAPIError(error, 'login');
        } finally {
            // Restaurar botón
            const submitBtn = document.querySelector('#login-form button[type="submit"]');
            submitBtn.textContent = 'Iniciar Sesión';
            submitBtn.disabled = false;
        }
    }

    async logout() {
        try {
            await api.logout();
            this.clearUser();
            this.showLogin();
            showNotification('Sesión cerrada correctamente', 'info');
        } catch (error) {
            handleAPIError(error, 'logout');
            // Incluso si hay error, limpiar la sesión local
            this.clearUser();
            this.showLogin();
        }
    }

    setUser(user) {
        this.currentUser = user;
        this.isAuthenticated = true;
        this.updateUserInterface();
    }

    clearUser() {
        this.currentUser = null;
        this.isAuthenticated = false;
        this.updateUserInterface();
    }

    updateUserInterface() {
        const userNameElement = document.getElementById('user-name');
        if (userNameElement && this.currentUser) {
            userNameElement.textContent = this.currentUser.nombre_completo;
        }

        // Mostrar/ocultar elementos según el estado de autenticación
        const authElements = document.querySelectorAll('[data-auth-required]');
        authElements.forEach(element => {
            element.style.display = this.isAuthenticated ? 'block' : 'none';
        });

        const noAuthElements = document.querySelectorAll('[data-no-auth]');
        noAuthElements.forEach(element => {
            element.style.display = this.isAuthenticated ? 'none' : 'block';
        });
    }

    showLogin() {
        if (this.loginModal) {
            this.loginModal.classList.add('show');
            this.loginModal.style.display = 'flex';
            
            // Focus en el campo email
            const emailField = document.getElementById('email');
            if (emailField) {
                setTimeout(() => emailField.focus(), 100);
            }
        }
    }

    hideLogin() {
        if (this.loginModal) {
            this.loginModal.classList.remove('show');
            this.loginModal.style.display = 'none';
            
            // Limpiar formulario
            const loginForm = document.getElementById('login-form');
            if (loginForm) {
                loginForm.reset();
            }
        }
    }

    // Verificar si el usuario tiene un rol específico
    hasRole(role) {
        return this.currentUser && this.currentUser.rol === role;
    }

    // Verificar si el usuario es administrador
    isAdmin() {
        return this.hasRole('admin');
    }

    // Verificar si el usuario es abogado
    isLawyer() {
        return this.hasRole('abogado');
    }

    // Middleware para verificar autenticación antes de ejecutar funciones
    requireAuth(callback) {
        if (this.isAuthenticated) {
            return callback();
        } else {
            showNotification('Debes iniciar sesión para acceder a esta función', 'warning');
            this.showLogin();
        }
    }

    // Middleware para verificar rol de administrador
    requireAdmin(callback) {
        return this.requireAuth(() => {
            if (this.isAdmin()) {
                return callback();
            } else {
                showNotification('Necesitas permisos de administrador para esta acción', 'error');
            }
        });
    }
}

// Crear instancia global de autenticación
window.auth = new Auth();

// Función global para logout (usada en el HTML)
window.logout = function() {
    if (confirm('¿Estás seguro de que quieres cerrar sesión?')) {
        window.auth.logout();
    }
};

// Interceptor para manejar errores de autenticación en las respuestas de la API
const originalRequest = window.api.request;
window.api.request = async function(endpoint, options = {}) {
    try {
        return await originalRequest.call(this, endpoint, options);
    } catch (error) {
        // Si es error 401, mostrar login
        if (error.message.includes('401') || error.message.includes('No autenticado')) {
            window.auth.clearUser();
            window.auth.showLogin();
        }
        throw error;
    }
};

console.log('Auth module loaded successfully');

