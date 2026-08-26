# DevOps Dashboard

A comprehensive DevOps dashboard for monitoring system resources, GitHub repositories, Docker containers, and managing alerts.

## Features

### System Monitoring
- **CPU Usage**: Real-time CPU usage monitoring with history
- **Memory Usage**: Track memory consumption and usage patterns
- **Disk Usage**: Monitor disk space across all partitions
- **Network Statistics**: Track network traffic and connections
- **Process Monitoring**: View top processes by CPU and memory usage
- **System Information**: Display OS, architecture, uptime, and more

### GitHub Integration
- **Repository Monitoring**: Track stars, forks, issues, and pull requests
- **Health Checks**: Monitor repository health and activity
- **Issue Tracking**: View and manage open issues
- **Pull Request Monitoring**: Track open, closed, and merged PRs
- **Commit History**: View recent commits and contributors
- **Workflow Monitoring**: Track GitHub Actions workflow runs

### Docker Monitoring
- **Container Management**: View all containers with status, ports, and resource usage
- **Image Management**: Track Docker images and their sizes
- **Network Monitoring**: Monitor Docker networks and connections
- **Volume Management**: Track Docker volumes
- **Event Monitoring**: View recent Docker events
- **Health Checks**: Monitor Docker daemon health

### Alerts & Notifications
- **System Alerts**: Receive alerts for high CPU, memory, or disk usage
- **GitHub Alerts**: Get notified of repository issues
- **Docker Alerts**: Monitor container and daemon health
- **Alert History**: Track and manage all alerts
- **Export Alerts**: Export alerts to CSV

### Real-time Updates
- **WebSocket Integration**: Real-time updates using Socket.IO
- **Automatic Refresh**: Configurable monitoring intervals
- **Live Charts**: Real-time charts for system metrics

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Git

### Required Dependencies
```bash
pip install Flask Flask-SocketIO psutil docker PyGithub python-dotenv
```

### Optional Dependencies
- For production: `gunicorn`, `eventlet`, or `gevent`
- For Redis support: `redis`

### Quick Start

1. **Clone the repository** (if not already cloned):
   ```bash
   git clone https://github.com/wwwphiokodotsolutions/LeChat-AI.git
   cd LeChat-AI/dashboard
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the dashboard**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the dashboard**:
   ```bash
   python run_dashboard.py
   ```

5. **Open in browser**:
   Navigate to `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Flask Configuration
DASHBOARD_SECRET_KEY=your-secret-key-here
DASHBOARD_DEBUG=True
DASHBOARD_HOST=0.0.0.0
DASHBOARD_PORT=5000

# GitHub Integration
GITHUB_TOKEN=your-github-personal-access-token
GITHUB_REPO=owner/repository

# Docker Configuration
DOCKER_ENABLED=True
DOCKER_SOCKET=unix:///var/run/docker.sock

# Monitoring Thresholds
ALERT_THRESHOLD_CPU=80.0
ALERT_THRESHOLD_MEMORY=85.0
ALERT_THRESHOLD_DISK=90.0
MONITORING_INTERVAL=60

# Theme
DASHBOARD_TITLE=My DevOps Dashboard
THEME_COLOR=#2563eb
```

### GitHub Token Setup

1. Go to [GitHub Settings > Developer Settings > Personal Access Tokens](https://github.com/settings/tokens)
2. Click "Generate new token"
3. Select the following scopes:
   - `repo` (for repository access)
   - `read:org` (for organization access)
4. Generate the token and add it to your `.env` file

### Docker Setup

Ensure Docker is installed and running on your system. The dashboard will automatically connect to the Docker daemon using the default socket.

For remote Docker hosts, set the `DOCKER_SOCKET` environment variable:
```env
DOCKER_SOCKET=tcp://remote-host:2375
```

## Usage

### Running in Development
```bash
python run_dashboard.py
```

### Running in Production

For production, use a WSGI server like Gunicorn:

```bash
# Install gunicorn
gunicorn -w 4 -k gevent -b 0.0.0.0:5000 app:app
```

Or with eventlet:
```bash
gunicorn -w 4 -k eventlet -b 0.0.0.0:5000 app:app
```

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Install system dependencies for psutil
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

EXPOSE 5000
CMD ["python", "run_dashboard.py"]
```

Build and run:
```bash
docker build -t devops-dashboard .
docker run -p 5000:5000 -v /var/run/docker.sock:/var/run/docker.sock devops-dashboard
```

## API Endpoints

### System Metrics
- `GET /api/metrics/system` - Get system metrics
- `GET /api/metrics/system/alerts` - Get system alerts
- `GET /api/metrics/system/history` - Get system metrics history

### GitHub Metrics
- `GET /api/metrics/github` - Get GitHub repository metrics
- `GET /api/metrics/github/health` - Get GitHub repository health
- `GET /api/metrics/github/issues` - Get GitHub issues
- `GET /api/metrics/github/pulls` - Get GitHub pull requests

### Docker Metrics
- `GET /api/metrics/docker` - Get Docker metrics
- `GET /api/metrics/docker/containers/<id>` - Get specific container stats

### Combined Metrics
- `GET /api/metrics/all` - Get all metrics combined

### Configuration
- `GET /api/config` - Get dashboard configuration

### Health Check
- `GET /health` - Health check endpoint

## Dashboard Pages

- `/` - Overview dashboard with all metrics
- `/system` - System monitoring dashboard
- `/github` - GitHub repository monitoring
- `/docker` - Docker monitoring dashboard
- `/alerts` - Alerts management dashboard

## Customization

### Adding New Monitors

1. Create a new monitor class in the `monitoring` directory:
   ```python
   class MyMonitor:
       def __init__(self):
           pass
       
       def get_metrics(self):
           return {}
   ```

2. Add the monitor to the `monitoring/__init__.py`:
   ```python
   from .my_monitor import MyMonitor
   ```

3. Integrate with the Flask app in `app.py`

### Custom Themes

Create a custom CSS file in `static/css/` and include it in your templates:
```html
{% block extra_css %}
<link rel="stylesheet" href="{{ url_for('static', filename='css/custom.css') }}">
{% endblock %}
```

### Custom Alerts

Add custom alert logic in your monitor classes:
```python
def get_alerts(self):
    alerts = []
    if self.metric > threshold:
        alerts.append({
            'type': 'custom',
            'severity': 'high',
            'message': 'Custom alert message',
            'value': self.metric,
            'threshold': threshold
        })
    return alerts
```

## Troubleshooting

### Common Issues

1. **Docker connection failed**:
   - Ensure Docker is running
   - Check the Docker socket path
   - Verify permissions on the Docker socket

2. **GitHub API rate limiting**:
   - Add a GitHub token to your `.env` file
   - Check rate limit headers in API responses

3. **Socket.IO connection issues**:
   - Ensure the server is running
   - Check the WebSocket URL
   - Verify CORS settings

4. **High CPU usage**:
   - Reduce the monitoring interval
   - Disable unnecessary monitors

### Debug Mode

Enable debug mode for detailed logging:
```env
DASHBOARD_DEBUG=True
```

## Security Considerations

- **GitHub Token**: Keep your GitHub token secure. Never commit it to version control.
- **Docker Socket**: The Docker socket provides full access to your Docker daemon. Ensure proper permissions.
- **Secret Key**: Use a strong secret key for Flask sessions.
- **HTTPS**: Always use HTTPS in production to encrypt traffic.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guide](CONTRIBUTING.md) for details on how to contribute.

## Support

For issues, questions, or feature requests, please open an issue on GitHub.
