// Main JavaScript for University AI Chatbot

// AI Chat Helper Functions
const AIChat = {
    // Format the chat message with source information
    formatMessage: function(message, source) {
        if (source) {
            const sourceLabels = {
                'knowledge_base': 'Knowledge Base',
                'openai': 'AI Assistant',
                'hybrid': 'Hybrid'
            };
            const sourceLabel = sourceLabels[source] || source;
            return `<div class="message-content">${message}</div><div class="message-source">Source: ${sourceLabel}</div>`;
        }
        return message;
    },
    
    // Save chat history to local storage
    saveHistory: function(userMessage, botResponse, source) {
        try {
            let history = JSON.parse(localStorage.getItem('chatHistory')) || [];
            history.push({
                user: userMessage,
                bot: botResponse,
                source: source,
                timestamp: new Date().toISOString()
            });
            // Keep only the last 50 messages
            if (history.length > 50) {
                history = history.slice(history.length - 50);
            }
            localStorage.setItem('chatHistory', JSON.stringify(history));
        } catch (e) {
            console.error('Error saving chat history:', e);
        }
    }
};

// Password visibility toggle function
function setupPasswordToggles() {
    // Login form password toggle
    const showPasswordCheckbox = document.querySelector('#show_password');
    if (showPasswordCheckbox) {
        showPasswordCheckbox.addEventListener('change', function() {
            const passwordField = document.querySelector('#password');
            passwordField.type = this.checked ? 'text' : 'password';
        });
    }
    
    // Registration form password toggles
    const showRegPasswordCheckbox = document.querySelector('#show_password');
    const showConfirmPasswordCheckbox = document.querySelector('#show_confirm_password');
    
    if (showRegPasswordCheckbox) {
        showRegPasswordCheckbox.addEventListener('change', function() {
            const passwordField = document.querySelector('#password');
            passwordField.type = this.checked ? 'text' : 'password';
        });
    }
    
    if (showConfirmPasswordCheckbox) {
        showConfirmPasswordCheckbox.addEventListener('change', function() {
            const confirmPasswordField = document.querySelector('#confirm_password');
            confirmPasswordField.type = this.checked ? 'text' : 'password';
        });
    }
    
    // Profile page password toggles
    const showCurrentPasswordCheckbox = document.querySelector('#show_current_password');
    if (showCurrentPasswordCheckbox) {
        showCurrentPasswordCheckbox.addEventListener('change', function() {
            const currentPasswordField = document.querySelector('#current_password');
            currentPasswordField.type = this.checked ? 'text' : 'password';
        });
    }
    
    const showNewPasswordCheckbox = document.querySelector('#show_new_password');
    if (showNewPasswordCheckbox) {
        showNewPasswordCheckbox.addEventListener('change', function() {
            const newPasswordField = document.querySelector('#new_password');
            newPasswordField.type = this.checked ? 'text' : 'password';
        });
    }
    
    const showConfirmNewPasswordCheckbox = document.querySelector('#show_confirm_password');
    if (showConfirmNewPasswordCheckbox) {
        showConfirmNewPasswordCheckbox.addEventListener('change', function() {
            const confirmNewPasswordField = document.querySelector('#confirm_new_password');
            confirmNewPasswordField.type = this.checked ? 'text' : 'password';
        });
    }
}

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Bootstrap tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Setup password visibility toggles
    setupPasswordToggles();
    
    // Add current year to footer
    const footerYear = document.querySelector('.footer-year');
    if (footerYear) {
        footerYear.textContent = new Date().getFullYear();
    }
    
    // Handle mobile navigation
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
        navbarToggler.addEventListener('click', function() {
            document.querySelector('.navbar-collapse').classList.toggle('show');
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
});