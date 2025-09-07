// Authentication JavaScript

class AuthManager {
    constructor() {
        this.isLoginPage = window.location.pathname.includes('login');
        this.isSignupPage = window.location.pathname.includes('signup');
        
        this.initializeElements();
        this.bindEvents();
        this.checkAuthStatus();
    }
    
    initializeElements() {
        // Form elements
        this.loginForm = document.getElementById('loginForm');
        this.signupForm = document.getElementById('signupForm');
        
        // Input elements
        this.emailInput = document.getElementById('email');
        this.passwordInput = document.getElementById('password');
        this.confirmPasswordInput = document.getElementById('confirmPassword');
        this.fullNameInput = document.getElementById('fullName');
        this.rememberMeInput = document.getElementById('rememberMe');
        this.agreeTermsInput = document.getElementById('agreeTerms');
        
        // Button elements
        this.loginBtn = document.getElementById('loginBtn');
        this.signupBtn = document.getElementById('signupBtn');
        
        // Notification container
        this.notificationContainer = document.getElementById('notificationContainer');
    }
    
    bindEvents() {
        if (this.isLoginPage && this.loginForm) {
            this.loginForm.addEventListener('submit', (e) => this.handleLogin(e));
        }
        
        if (this.isSignupPage && this.signupForm) {
            this.signupForm.addEventListener('submit', (e) => this.handleSignup(e));
        }
        
        // Real-time validation
        if (this.passwordInput) {
            this.passwordInput.addEventListener('input', () => this.validatePassword());
        }
        
        if (this.confirmPasswordInput) {
            this.confirmPasswordInput.addEventListener('input', () => this.validatePasswordMatch());
        }
        
        if (this.emailInput) {
            this.emailInput.addEventListener('input', () => this.validateEmail());
        }
    }
    
    checkAuthStatus() {
        // Check if user is already logged in
        const token = localStorage.getItem('authToken');
        if (token) {
            // Redirect to main page if already authenticated
            window.location.href = '/';
        }
    }
    
    async handleLogin(e) {
        e.preventDefault();
        
        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;
        const rememberMe = this.rememberMeInput.checked;
        
        // Validate inputs
        if (!this.validateLoginForm(email, password)) {
            return;
        }
        
        this.setButtonLoading(this.loginBtn, true);
        
        try {
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email,
                    password,
                    rememberMe
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Store authentication token
                localStorage.setItem('authToken', data.token);
                localStorage.setItem('user', JSON.stringify(data.user));
                
                this.showNotification('Login successful! Redirecting...', 'success');
                
                // Redirect to main page
                setTimeout(() => {
                    window.location.href = '/';
                }, 1500);
            } else {
                throw new Error(data.message || 'Login failed');
            }
            
        } catch (error) {
            console.error('Login error:', error);
            this.showNotification(`Login failed: ${error.message}`, 'error');
        } finally {
            this.setButtonLoading(this.loginBtn, false);
        }
    }
    
    async handleSignup(e) {
        e.preventDefault();
        
        const fullName = this.fullNameInput.value.trim();
        const email = this.emailInput.value.trim();
        const password = this.passwordInput.value;
        const confirmPassword = this.confirmPasswordInput.value;
        const agreeTerms = this.agreeTermsInput.checked;
        
        // Validate inputs
        if (!this.validateSignupForm(fullName, email, password, confirmPassword, agreeTerms)) {
            return;
        }
        
        this.setButtonLoading(this.signupBtn, true);
        
        try {
            const response = await fetch('/api/auth/signup', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    fullName,
                    email,
                    password,
                    confirmPassword
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                this.showNotification('Account created successfully! Please sign in.', 'success');
                
                // Redirect to login page
                setTimeout(() => {
                    window.location.href = '/login';
                }, 2000);
            } else {
                throw new Error(data.message || 'Signup failed');
            }
            
        } catch (error) {
            console.error('Signup error:', error);
            this.showNotification(`Signup failed: ${error.message}`, 'error');
        } finally {
            this.setButtonLoading(this.signupBtn, false);
        }
    }
    
    validateLoginForm(email, password) {
        let isValid = true;
        
        // Validate email
        if (!email) {
            this.showFieldError(this.emailInput, 'Email is required');
            isValid = false;
        } else if (!this.isValidEmail(email)) {
            this.showFieldError(this.emailInput, 'Please enter a valid email address');
            isValid = false;
        } else {
            this.showFieldSuccess(this.emailInput);
        }
        
        // Validate password
        if (!password) {
            this.showFieldError(this.passwordInput, 'Password is required');
            isValid = false;
        } else {
            this.showFieldSuccess(this.passwordInput);
        }
        
        return isValid;
    }
    
    validateSignupForm(fullName, email, password, confirmPassword, agreeTerms) {
        let isValid = true;
        
        // Validate full name
        if (!fullName) {
            this.showFieldError(this.fullNameInput, 'Full name is required');
            isValid = false;
        } else if (fullName.length < 2) {
            this.showFieldError(this.fullNameInput, 'Full name must be at least 2 characters');
            isValid = false;
        } else {
            this.showFieldSuccess(this.fullNameInput);
        }
        
        // Validate email
        if (!email) {
            this.showFieldError(this.emailInput, 'Email is required');
            isValid = false;
        } else if (!this.isValidEmail(email)) {
            this.showFieldError(this.emailInput, 'Please enter a valid email address');
            isValid = false;
        } else {
            this.showFieldSuccess(this.emailInput);
        }
        
        // Validate password
        if (!password) {
            this.showFieldError(this.passwordInput, 'Password is required');
            isValid = false;
        } else if (password.length < 8) {
            this.showFieldError(this.passwordInput, 'Password must be at least 8 characters');
            isValid = false;
        } else {
            this.showFieldSuccess(this.passwordInput);
        }
        
        // Validate password confirmation
        if (!confirmPassword) {
            this.showFieldError(this.confirmPasswordInput, 'Please confirm your password');
            isValid = false;
        } else if (password !== confirmPassword) {
            this.showFieldError(this.confirmPasswordInput, 'Passwords do not match');
            isValid = false;
        } else {
            this.showFieldSuccess(this.confirmPasswordInput);
        }
        
        // Validate terms agreement
        if (!agreeTerms) {
            this.showNotification('Please agree to the Terms of Service and Privacy Policy', 'error');
            isValid = false;
        }
        
        return isValid;
    }
    
    validateEmail() {
        const email = this.emailInput.value.trim();
        if (email && !this.isValidEmail(email)) {
            this.showFieldError(this.emailInput, 'Please enter a valid email address');
        } else if (email) {
            this.showFieldSuccess(this.emailInput);
        }
    }
    
    validatePassword() {
        const password = this.passwordInput.value;
        if (password && password.length < 8) {
            this.showFieldError(this.passwordInput, 'Password must be at least 8 characters');
        } else if (password) {
            this.showFieldSuccess(this.passwordInput);
        }
    }
    
    validatePasswordMatch() {
        const password = this.passwordInput.value;
        const confirmPassword = this.confirmPasswordInput.value;
        
        if (confirmPassword && password !== confirmPassword) {
            this.showFieldError(this.confirmPasswordInput, 'Passwords do not match');
        } else if (confirmPassword && password === confirmPassword) {
            this.showFieldSuccess(this.confirmPasswordInput);
        }
    }
    
    isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    showFieldError(input, message) {
        input.classList.add('error');
        input.classList.remove('success');
        
        // Remove existing error message
        const existingError = input.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
        
        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message show';
        errorDiv.textContent = message;
        input.parentNode.appendChild(errorDiv);
    }
    
    showFieldSuccess(input) {
        input.classList.add('success');
        input.classList.remove('error');
        
        // Remove error message
        const existingError = input.parentNode.querySelector('.error-message');
        if (existingError) {
            existingError.remove();
        }
    }
    
    setButtonLoading(button, loading) {
        const btnText = button.querySelector('.btn-text');
        const spinner = button.querySelector('.spinner');
        
        if (loading) {
            button.disabled = true;
            button.classList.add('loading');
            btnText.style.opacity = '0.7';
            spinner.style.display = 'block';
        } else {
            button.disabled = false;
            button.classList.remove('loading');
            btnText.style.opacity = '1';
            spinner.style.display = 'none';
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.textContent = message;
        
        this.notificationContainer.appendChild(notification);
        
        // Show notification
        setTimeout(() => {
            notification.classList.add('show');
        }, 100);
        
        // Hide notification after 4 seconds
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 4000);
    }
}

// Initialize the auth manager when the page loads
let authManager;
document.addEventListener('DOMContentLoaded', () => {
    authManager = new AuthManager();
});
