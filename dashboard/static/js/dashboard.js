/**
 * DevOps Dashboard - Main JavaScript
 * Handles Socket.IO connections, real-time updates, and common functionality
 */

// Socket.IO connection
const socket = io({
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 20000
});

// Global state
let dashboardConfig = {};
let metricsHistory = {
    system: [],
    github: [],
    docker: []
};

/**
 * Initialize the dashboard
 */
function initDashboard() {
    console.log('Initializing DevOps Dashboard...');
    
    // Load configuration
    loadConfig();
    
    // Setup event handlers
    setupSocketHandlers();
    setupGlobalHandlers();
    
    // Initialize components
    initComponents();
    
    console.log('Dashboard initialized');
}

/**
 * Load dashboard configuration
 */
function loadConfig() {
    fetch('/api/config')
        .then(response => response.json())
        .then(config => {
            dashboardConfig = config;
            console.log('Configuration loaded:', config);
            
            // Apply theme color
            if (config.theme_color) {
                document.documentElement.style.setProperty('--theme-color', config.theme_color);
            }
            
            // Update page title
            if (config.title) {
                document.title = config.title;
            }
        })
        .catch(error => {
            console.error('Error loading configuration:', error);
        });
}

/**
 * Setup Socket.IO event handlers
 */
function setupSocketHandlers() {
    // Connection events
    socket.on('connect', () => {
        console.log('Connected to Socket.IO server');
        updateConnectionStatus(true);
        
        // Request initial data
        socket.emit('request_metrics');
    });
    
    socket.on('disconnect', () => {
        console.log('Disconnected from Socket.IO server');
        updateConnectionStatus(false);
    });
    
    socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        updateConnectionStatus(false);
    });
    
    socket.on('reconnect', () => {
        console.log('Reconnected to Socket.IO server');
        updateConnectionStatus(true);
        socket.emit('request_metrics');
    });
    
    // Metrics update
    socket.on('metrics_update', (data) => {
        console.log('Metrics updated:', new Date().toISOString());
        handleMetricsUpdate(data);
    });
    
    // Custom events
    socket.on('connected', (data) => {
        console.log('Server message:', data.message);
    });
    
    socket.on('repo_updated', (data) => {
        console.log('Repository updated:', data.repo);
        // Refresh GitHub data
        if (typeof refreshGitHubData === 'function') {
            refreshGitHubData();
        }
    });
}

/**
 * Setup global event handlers
 */
function setupGlobalHandlers() {
    // Window focus/blur events
    window.addEventListener('focus', () => {
        // Request fresh data when window regains focus
        socket.emit('request_metrics');
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (event) => {
        // Ctrl/Cmd + R to refresh
        if ((event.ctrlKey || event.metaKey) && event.key === 'r') {
            event.preventDefault();
            socket.emit('request_metrics');
        }
    });
    
    // Visibility change
    document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
            socket.emit('request_metrics');
        }
    });
}

/**
 * Initialize dashboard components
 */
function initComponents() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        Chart.defaults.font.family = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif";
        Chart.defaults.color = '#6c757d';
    }
    
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    // Start clock
    startClock();
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    const statusIndicator = document.querySelector('.status-indicator');
    const statusDot = document.querySelector('.status-dot');
    const statusText = document.querySelector('.status-text');
    
    if (!statusIndicator || !statusDot || !statusText) return;
    
    if (connected) {
        statusDot.classList.remove('bg-danger');
        statusDot.classList.add('bg-success');
        statusText.textContent = 'Connected';
    } else {
        statusDot.classList.remove('bg-success');
        statusDot.classList.add('bg-danger');
        statusText.textContent = 'Disconnected';
    }
}

/**
 * Handle metrics update from server
 */
function handleMetricsUpdate(data) {
    // Store in history
    if (data.system) {
        metricsHistory.system.push({
            timestamp: data.timestamp || new Date().toISOString(),
            data: data.system
        });
        if (metricsHistory.system.length > 100) {
            metricsHistory.system.shift();
        }
    }
    
    if (data.github) {
        metricsHistory.github.push({
            timestamp: data.timestamp || new Date().toISOString(),
            data: data.github
        });
        if (metricsHistory.github.length > 100) {
            metricsHistory.github.shift();
        }
    }
    
    if (data.docker) {
        metricsHistory.docker.push({
            timestamp: data.timestamp || new Date().toISOString(),
            data: data.docker
        });
        if (metricsHistory.docker.length > 100) {
            metricsHistory.docker.shift();
        }
    }
    
    // Trigger page-specific update functions if they exist
    if (typeof updateSystemInfo === 'function') {
        updateSystemInfo(data);
    }
    if (typeof updateGitHubInfo === 'function') {
        updateGitHubInfo(data);
    }
    if (typeof updateDockerInfo === 'function') {
        updateDockerInfo(data);
    }
    if (typeof updateAlerts === 'function') {
        updateAlerts(data);
    }
    if (typeof updateSystemMetrics === 'function') {
        updateSystemMetrics(data);
    }
    if (typeof updateDockerStatus === 'function') {
        updateDockerStatus(data);
    }
}

/**
 * Start the clock
 */
function startClock() {
    const currentTimeElement = document.getElementById('current-time');
    
    if (!currentTimeElement) return;
    
    function updateClock() {
        const now = new Date();
        const timeString = now.toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        });
        currentTimeElement.textContent = timeString;
    }
    
    // Update immediately
    updateClock();
    
    // Update every second
    setInterval(updateClock, 1000);
}

/**
 * Format bytes to human readable string
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Format number with suffix (K, M, B)
 */
function formatNumber(num) {
    if (num === 0) return '0';
    
    const abs = Math.abs(num);
    const sign = num < 0 ? '-' : '';
    
    if (abs >= 1e9) {
        return sign + (abs / 1e9).toFixed(2) + 'B';
    }
    if (abs >= 1e6) {
        return sign + (abs / 1e6).toFixed(2) + 'M';
    }
    if (abs >= 1e3) {
        return sign + (abs / 1e3).toFixed(2) + 'K';
    }
    return sign + num;
}

/**
 * Format percentage with color class
 */
function getPercentageColor(percentage) {
    if (percentage > 90) return 'text-danger';
    if (percentage > 75) return 'text-warning';
    return 'text-success';
}

/**
 * Get health status color class
 */
function getHealthStatusColor(score) {
    if (score >= 90) return 'bg-success';
    if (score >= 70) return 'bg-warning';
    if (score >= 50) return 'bg-orange';
    return 'bg-danger';
}

/**
 * Debounce function for performance
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle function for performance
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Show notification toast
 */
function showToast(message, type = 'info') {
    const toastContainer = document.getElementById('toast-container');
    
    if (!toastContainer) {
        // Create toast container if it doesn't exist
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '11';
        document.body.appendChild(container);
    }
    
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast align-items-center text-white bg-${type} border-0" role="alert" aria-live="assertive" aria-atomic="true">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fa fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        </div>
    `;
    
    document.getElementById('toast-container').insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement, { autohide: true, delay: 5000 });
    toast.show();
    
    // Remove toast after it's hidden
    toastElement.addEventListener('hidden.bs.toast', () => {
        toastElement.remove();
    });
}

/**
 * Copy text to clipboard
 */
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(err => {
        console.error('Failed to copy: ', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}

/**
 * Format date relative to now
 */
function formatRelativeDate(dateString) {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) {
        return days + ' day' + (days > 1 ? 's' : '') + ' ago';
    }
    if (hours > 0) {
        return hours + ' hour' + (hours > 1 ? 's' : '') + ' ago';
    }
    if (minutes > 0) {
        return minutes + ' minute' + (minutes > 1 ? 's' : '') + ' ago';
    }
    if (seconds > 0) {
        return seconds + ' second' + (seconds > 1 ? 's' : '') + ' ago';
    }
    return 'Just now';
}

/**
 * Format uptime from boot time
 */
function formatUptime(bootTime) {
    if (!bootTime) return '-';
    
    const bootDate = new Date(bootTime);
    const now = new Date();
    const diff = now - bootDate;
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    const parts = [];
    if (days > 0) parts.push(days + 'd');
    if (hours % 24 > 0) parts.push((hours % 24) + 'h');
    if (minutes % 60 > 0) parts.push((minutes % 60) + 'm');
    if (seconds % 60 > 0 && days === 0) parts.push((seconds % 60) + 's');
    
    return parts.join(' ') || '0s';
}

/**
 * Get color for health score
 */
function getHealthColor(score) {
    if (score >= 90) return '#10b981';
    if (score >= 70) return '#f59e0b';
    if (score >= 50) return '#f97316';
    return '#dc3545';
}

/**
 * Get color for severity
 */
function getSeverityColor(severity) {
    switch (severity) {
        case 'high': return '#dc3545';
        case 'warning': return '#f59e0b';
        case 'info': return '#17a2b8';
        default: return '#6c757d';
    }
}

/**
 * Initialize when DOM is ready
 */
document.addEventListener('DOMContentLoaded', initDashboard);

// Export for use in other scripts
window.DashboardUtils = {
    formatBytes,
    formatNumber,
    formatRelativeDate,
    formatUptime,
    getHealthColor,
    getSeverityColor,
    getPercentageColor,
    showToast,
    copyToClipboard,
    debounce,
    throttle
};
