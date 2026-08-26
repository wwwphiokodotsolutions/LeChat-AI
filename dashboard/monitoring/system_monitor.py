"""
System Monitor
Monitors CPU, memory, disk, and network usage
"""

import psutil
import time
from datetime import datetime
from typing import Dict, Any, List
import json


class SystemMonitor:
    """Monitor system resources and collect metrics"""
    
    def __init__(self, alert_thresholds: Dict[str, float] = None):
        """
        Initialize the system monitor
        
        Args:
            alert_thresholds: Dictionary with alert thresholds for CPU, memory, disk
        """
        self.alert_thresholds = alert_thresholds or {
            'cpu': 80.0,
            'memory': 85.0,
            'disk': 90.0
        }
        self.history = []
        self.max_history = 100
        
    def get_cpu_usage(self) -> Dict[str, Any]:
        """Get CPU usage statistics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_count = psutil.cpu_count()
        cpu_freq = psutil.cpu_freq()
        
        return {
            'usage_percent': cpu_percent,
            'cores': cpu_count,
            'frequency_mhz': cpu_freq.freq if cpu_freq else 0,
            'min_frequency': cpu_freq.min if cpu_freq else 0,
            'max_frequency': cpu_freq.max if cpu_freq else 0,
            'alert': cpu_percent > self.alert_thresholds['cpu']
        }
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get memory usage statistics"""
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        return {
            'total_gb': round(memory.total / (1024**3), 2),
            'used_gb': round(memory.used / (1024**3), 2),
            'free_gb': round(memory.free / (1024**3), 2),
            'usage_percent': memory.percent,
            'swap_total_gb': round(swap.total / (1024**3), 2),
            'swap_used_gb': round(swap.used / (1024**3), 2),
            'swap_usage_percent': swap.percent,
            'alert': memory.percent > self.alert_thresholds['memory']
        }
    
    def get_disk_usage(self) -> List[Dict[str, Any]]:
        """Get disk usage statistics for all partitions"""
        disks = []
        for partition in psutil.disk_partitions():
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                disks.append({
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'total_gb': round(usage.total / (1024**3), 2),
                    'used_gb': round(usage.used / (1024**3), 2),
                    'free_gb': round(usage.free / (1024**3), 2),
                    'usage_percent': usage.percent,
                    'alert': usage.percent > self.alert_thresholds['disk']
                })
            except Exception:
                continue
        return disks
    
    def get_network_stats(self) -> Dict[str, Any]:
        """Get network statistics"""
        net_io = psutil.net_io_counters()
        connections = len(psutil.net_connections())
        
        return {
            'bytes_sent_mb': round(net_io.bytes_sent / (1024**2), 2),
            'bytes_recv_mb': round(net_io.bytes_recv / (1024**2), 2),
            'packets_sent': net_io.packets_sent,
            'packets_recv': net_io.packets_recv,
            'connections': connections,
            'errin': net_io.errin,
            'errout': net_io.errout,
            'dropin': net_io.dropin,
            'dropout': net_io.dropout
        }
    
    def get_system_info(self) -> Dict[str, Any]:
        """Get basic system information"""
        import platform
        import socket
        
        return {
            'hostname': socket.gethostname(),
            'os': platform.system(),
            'os_version': platform.version(),
            'os_release': platform.release(),
            'python_version': platform.python_version(),
            'processor': platform.processor(),
            'machine': platform.machine(),
            'boot_time': datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def get_process_stats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top processes by CPU usage"""
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'user': proc.info['username'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage and limit
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes[:limit]
    
    def collect_metrics(self) -> Dict[str, Any]:
        """Collect all system metrics"""
        timestamp = datetime.now().isoformat()
        
        metrics = {
            'timestamp': timestamp,
            'system': self.get_system_info(),
            'cpu': self.get_cpu_usage(),
            'memory': self.get_memory_usage(),
            'disk': self.get_disk_usage(),
            'network': self.get_network_stats(),
            'processes': self.get_process_stats()
        }
        
        # Store in history
        self.history.append(metrics)
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        return metrics
    
    def get_alerts(self) -> List[Dict[str, Any]]:
        """Check for any active alerts"""
        alerts = []
        
        # Check CPU
        cpu = self.get_cpu_usage()
        if cpu['alert']:
            alerts.append({
                'type': 'cpu',
                'severity': 'high',
                'message': f"CPU usage at {cpu['usage_percent']}% exceeds threshold of {self.alert_thresholds['cpu']}%",
                'value': cpu['usage_percent'],
                'threshold': self.alert_thresholds['cpu']
            })
        
        # Check Memory
        memory = self.get_memory_usage()
        if memory['alert']:
            alerts.append({
                'type': 'memory',
                'severity': 'high',
                'message': f"Memory usage at {memory['usage_percent']}% exceeds threshold of {self.alert_thresholds['memory']}%",
                'value': memory['usage_percent'],
                'threshold': self.alert_thresholds['memory']
            })
        
        # Check Disk
        for disk in self.get_disk_usage():
            if disk['alert']:
                alerts.append({
                    'type': 'disk',
                    'severity': 'warning',
                    'message': f"Disk {disk['mountpoint']} usage at {disk['usage_percent']}% exceeds threshold of {self.alert_thresholds['disk']}%",
                    'value': disk['usage_percent'],
                    'threshold': self.alert_thresholds['disk'],
                    'mountpoint': disk['mountpoint']
                })
        
        return alerts
    
    def get_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get historical metrics"""
        if limit:
            return self.history[-limit:]
        return self.history.copy()
    
    def start_monitoring(self, interval: int = 60, callback: callable = None):
        """
        Start continuous monitoring
        
        Args:
            interval: Monitoring interval in seconds
            callback: Optional callback function to receive metrics
        """
        import threading
        
        def monitor_loop():
            while True:
                metrics = self.collect_metrics()
                if callback:
                    callback(metrics)
                time.sleep(interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        return thread


# Singleton instance
system_monitor = SystemMonitor()

if __name__ == '__main__':
    # Test the system monitor
    monitor = SystemMonitor()
    metrics = monitor.collect_metrics()
    print(json.dumps(metrics, indent=2))
    
    alerts = monitor.get_alerts()
    if alerts:
        print("\nAlerts:")
        for alert in alerts:
            print(f"  {alert['severity'].upper()}: {alert['message']}")
    else:
        print("\nNo active alerts")