"""
DevOps Dashboard Flask Application
Main application with routes and API endpoints
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
from .config import config
from .monitoring.system_monitor import system_monitor
from .monitoring.github_monitor import github_monitor
from .monitoring.docker_monitor import docker_monitor
import threading
import time
from datetime import datetime
import json


def create_app(config_obj=None):
    """Create and configure the Flask application"""
    
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    if config_obj:
        app.config.from_object(config_obj)
    else:
        app.config.from_object(config)
    
    # Initialize Socket.IO
    socketio = SocketIO(app, 
                       message_queue=config.SOCKETIO_MESSAGE_QUEUE,
                       cors_allowed_origins=config.ALLOWED_ORIGINS)
    
    # Initialize monitors with config
    system_monitor.alert_thresholds = {
        'cpu': config.ALERT_THRESHOLD_CPU,
        'memory': config.ALERT_THRESHOLD_MEMORY,
        'disk': config.ALERT_THRESHOLD_DISK
    }
    
    if config.GITHUB_TOKEN:
        github_monitor.set_token(config.GITHUB_TOKEN)
    if config.GITHUB_REPO:
        github_monitor.set_repo(config.GITHUB_REPO)
    
    docker_monitor.enabled = config.DOCKER_ENABLED
    
    # Global state for monitoring threads
    monitoring_threads = []
    
    def broadcast_metrics():
        """Broadcast metrics to all connected clients"""
        try:
            # Collect all metrics
            system_metrics = system_monitor.collect_metrics()
            system_alerts = system_monitor.get_alerts()
            
            github_stats = github_monitor.get_repo_stats() if github_monitor.repo else {}
            github_health = github_monitor.check_health() if github_monitor.repo else {}
            
            docker_info = docker_monitor.get_docker_info() if docker_monitor.is_available() else None
            docker_containers = docker_monitor.get_containers() if docker_monitor.is_available() else []
            docker_health = docker_monitor.get_health_status()
            
            docker_stats = {
                'info': docker_info,
                'containers': docker_containers,
                'health': docker_health
            }
            
            # Broadcast to all clients
            socketio.emit('metrics_update', {
                'timestamp': datetime.now().isoformat(),
                'system': system_metrics,
                'alerts': system_alerts,
                'github': github_stats,
                'github_health': github_health,
                'docker': docker_stats
            })
        except Exception as e:
            print(f"Error broadcasting metrics: {e}")
    
    def start_monitoring():
        """Start background monitoring"""
        while True:
            broadcast_metrics()
            time.sleep(config.MONITORING_INTERVAL)
    
    # Start monitoring thread
    if not any(t.name == 'monitoring-thread' for t in threading.enumerate()):
        monitoring_thread = threading.Thread(
            target=start_monitoring,
            daemon=True,
            name='monitoring-thread'
        )
        monitoring_thread.start()
        monitoring_threads.append(monitoring_thread)
    
    # Routes
    @app.route('/')
    def index():
        """Main dashboard page"""
        return render_template('index.html', 
                             title=config.DASHBOARD_TITLE,
                             theme_color=config.THEME_COLOR)
    
    @app.route('/system')
    def system_dashboard():
        """System monitoring dashboard"""
        return render_template('system.html',
                             title=f"{config.DASHBOARD_TITLE} - System Monitoring",
                             theme_color=config.THEME_COLOR)
    
    @app.route('/github')
    def github_dashboard():
        """GitHub monitoring dashboard"""
        return render_template('github.html',
                             title=f"{config.DASHBOARD_TITLE} - GitHub Monitoring",
                             theme_color=config.THEME_COLOR,
                             repo=config.GITHUB_REPO)
    
    @app.route('/docker')
    def docker_dashboard():
        """Docker monitoring dashboard"""
        return render_template('docker.html',
                             title=f"{config.DASHBOARD_TITLE} - Docker Monitoring",
                             theme_color=config.THEME_COLOR)
    
    @app.route('/alerts')
    def alerts_dashboard():
        """Alerts dashboard"""
        return render_template('alerts.html',
                             title=f"{config.DASHBOARD_TITLE} - Alerts",
                             theme_color=config.THEME_COLOR)
    
    # API Endpoints
    @app.route('/api/metrics/system')
    def get_system_metrics():
        """Get system metrics"""
        try:
            metrics = system_monitor.collect_metrics()
            return jsonify(metrics)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/metrics/system/alerts')
    def get_system_alerts():
        """Get system alerts"""
        try:
            alerts = system_monitor.get_alerts()
            return jsonify(alerts)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/metrics/system/history')
    def get_system_history():
        """Get system metrics history"""
        try:
            limit = request.args.get('limit', default=10, type=int)
            history = system_monitor.get_history(limit)
            return jsonify(history)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/metrics/github')
    def get_github_metrics():
        """Get GitHub repository metrics"""
        try:
            stats = github_monitor.get_repo_stats()
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/metrics/github/health')
    def get_github_health():
        """Get GitHub repository health"""
        try:
            health = github_monitor.check_health()
            return jsonify(health)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/metrics/github/issues')
    def get_github_issues():
        """Get GitHub issues"""
        try:
            state = request.args.get('state', default='open', type=str)
            limit = request.args.get('limit', default=50, type=int)
            issues = github_monitor.get_open_issues(state, limit)
            return jsonify(issues)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/metrics/github/pulls')
    def get_github_pulls():
        """Get GitHub pull requests"""
        try:
            state = request.args.get('state', default='open', type=str)
            limit = request.args.get('limit', default=50, type=int)
            pulls = github_monitor.get_pull_requests(state, limit)
            return jsonify(pulls)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/metrics/docker')
    def get_docker_metrics():
        """Get Docker metrics"""
        try:
            if not docker_monitor.is_available():
                return jsonify({'error': 'Docker not available'}), 503
            
            metrics = {
                'info': docker_monitor.get_docker_info(),
                'containers': docker_monitor.get_containers(),
                'images': docker_monitor.get_images(),
                'networks': docker_monitor.get_networks(),
                'volumes': docker_monitor.get_volumes(),
                'health': docker_monitor.get_health_status()
            }
            return jsonify(metrics)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/metrics/docker/containers/<container_id>')
    def get_docker_container_stats(container_id):
        """Get specific container statistics"""
        try:
            if not docker_monitor.is_available():
                return jsonify({'error': 'Docker not available'}), 503
            
            stats = docker_monitor.get_container_stats(container_id)
            if stats:
                return jsonify(stats)
            else:
                return jsonify({'error': 'Container not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/metrics/all')
    def get_all_metrics():
        """Get all metrics combined"""
        try:
            metrics = {
                'timestamp': datetime.now().isoformat(),
                'system': system_monitor.collect_metrics(),
                'alerts': system_monitor.get_alerts(),
                'github': github_monitor.get_repo_stats() if github_monitor.repo else {},
                'github_health': github_monitor.check_health() if github_monitor.repo else {},
                'docker': {
                    'info': docker_monitor.get_docker_info() if docker_monitor.is_available() else None,
                    'containers': docker_monitor.get_containers() if docker_monitor.is_available() else [],
                    'health': docker_monitor.get_health_status()
                }
            }
            return jsonify(metrics)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/config')
    def get_config():
        """Get dashboard configuration"""
        try:
            config_data = {
                'title': config.DASHBOARD_TITLE,
                'theme_color': config.THEME_COLOR,
                'monitoring_interval': config.MONITORING_INTERVAL,
                'github_repo': config.GITHUB_REPO,
                'docker_enabled': config.DOCKER_ENABLED,
                'alert_thresholds': {
                    'cpu': config.ALERT_THRESHOLD_CPU,
                    'memory': config.ALERT_THRESHOLD_MEMORY,
                    'disk': config.ALERT_THRESHOLD_DISK
                }
            }
            return jsonify(config_data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # Socket.IO Events
    @socketio.on('connect')
    def handle_connect():
        """Handle new client connection"""
        print(f"Client connected: {request.sid}")
        emit('connected', {'message': 'Connected to DevOps Dashboard'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        print(f"Client disconnected: {request.sid}")
    
    @socketio.on('request_metrics')
    def handle_metrics_request(data):
        """Handle manual metrics request"""
        broadcast_metrics()
    
    @socketio.on('set_repo')
    def handle_set_repo(data):
        """Set GitHub repository to monitor"""
        repo = data.get('repo')
        if repo:
            github_monitor.set_repo(repo)
            emit('repo_updated', {'repo': repo})
            broadcast_metrics()
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'system_monitor': 'ok',
            'github_monitor': 'ok',
            'docker_monitor': 'ok' if docker_monitor.is_available() else 'disabled'
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    # Add socketio to app for external access
    app.socketio = socketio
    app.monitoring_threads = monitoring_threads
    
    return app


# Create default app instance
app = create_app()

if __name__ == '__main__':
    print(f"Starting {config.DASHBOARD_TITLE}")
    print(f"Listening on {config.HOST}:{config.PORT}")
    print(f"Debug mode: {config.DEBUG}")
    
    # Run the application
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
