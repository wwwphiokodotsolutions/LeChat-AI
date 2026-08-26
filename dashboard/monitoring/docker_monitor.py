"""
Docker Monitor
Monitors Docker containers, images, and system resources
"""

import docker
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class DockerMonitor:
    """Monitor Docker containers and resources"""
    
    def __init__(self, socket_path: str = None, enabled: bool = True):
        """
        Initialize Docker monitor
        
        Args:
            socket_path: Docker socket path
            enabled: Whether Docker monitoring is enabled
        """
        self.enabled = enabled
        self.socket_path = socket_path
        self.client = None
        self.connected = False
        
        if enabled:
            self._connect()
    
    def _connect(self) -> bool:
        """Connect to Docker daemon"""
        try:
            if self.socket_path:
                self.client = docker.DockerClient(base_url=self.socket_path)
            else:
                self.client = docker.from_env()
            
            # Test connection
            self.client.ping()
            self.connected = True
            return True
        except Exception as e:
            print(f"Error connecting to Docker: {e}")
            self.connected = False
            return False
    
    def is_available(self) -> bool:
        """Check if Docker is available"""
        return self.enabled and self.connected
    
    def get_docker_info(self) -> Optional[Dict[str, Any]]:
        """Get Docker system information"""
        if not self.is_available():
            return None
        
        try:
            info = self.client.info()
            return {
                'containers_total': info.get('Containers', 0),
                'containers_running': info.get('ContainersRunning', 0),
                'containers_stopped': info.get('ContainersStopped', 0),
                'containers_paused': info.get('ContainersPaused', 0),
                'images_total': info.get('Images', 0),
                'docker_version': info.get('ServerVersion', 'Unknown'),
                'os': info.get('OperatingSystem', 'Unknown'),
                'architecture': info.get('Architecture', 'Unknown'),
                'cpus': info.get('NCPU', 0),
                'memory_total': info.get('MemTotal', 0),
                'docker_root_dir': info.get('DockerRootDir', 'Unknown')
            }
        except Exception as e:
            print(f"Error getting Docker info: {e}")
            return None
    
    def get_containers(self, all_containers: bool = False) -> List[Dict[str, Any]]:
        """Get list of containers"""
        if not self.is_available():
            return []
        
        try:
            containers = self.client.containers.list(all=all_containers)
            container_list = []
            
            for container in containers:
                try:
                    container.reload()  # Get latest status
                    attrs = container.attrs
                    
                    container_list.append({
                        'id': attrs.get('Id', '')[:12],
                        'name': attrs.get('Name', '').lstrip('/'),
                        'status': attrs.get('State', {}).get('Status', 'Unknown'),
                        'image': attrs.get('Config', {}).get('Image', 'Unknown'),
                        'created': attrs.get('Created', ''),
                        'ports': self._get_container_ports(attrs),
                        'labels': attrs.get('Config', {}).get('Labels', {}),
                        'state': {
                            'running': attrs.get('State', {}).get('Running', False),
                            'paused': attrs.get('State', {}).get('Paused', False),
                            'restarting': attrs.get('State', {}).get('Restarting', False),
                            'exit_code': attrs.get('State', {}).get('ExitCode', 0)
                        },
                        'resources': self._get_container_resources(container)
                    })
                except Exception as e:
                    print(f"Error getting container info: {e}")
                    continue
            
            return container_list
        except Exception as e:
            print(f"Error listing containers: {e}")
            return []
    
    def _get_container_ports(self, attrs: Dict) -> Dict[str, Any]:
        """Extract port mappings from container attributes"""
        ports = {}
        network_settings = attrs.get('NetworkSettings', {})
        port_bindings = network_settings.get('Ports', {})
        
        for container_port, bindings in port_bindings.items():
            if bindings:
                ports[container_port] = [
                    {
                        'host_ip': binding.get('HostIp', '0.0.0.0'),
                        'host_port': binding.get('HostPort', '')
                    }
                    for binding in bindings
                ]
        
        return ports
    
    def _get_container_resources(self, container) -> Dict[str, Any]:
        """Get container resource usage"""
        try:
            stats = container.stats(stream=False)
            return {
                'cpu_percent': stats.get('cpu_stats', {}).get('cpu_usage', {}).get('total_usage', 0),
                'memory_usage': stats.get('memory_stats', {}).get('usage', 0),
                'memory_limit': stats.get('memory_stats', {}).get('limit', 0),
                'memory_percent': (stats.get('memory_stats', {}).get('usage', 0) / 
                                 stats.get('memory_stats', {}).get('limit', 1)) * 100 if stats.get('memory_stats', {}).get('limit', 0) > 0 else 0
            }
        except Exception:
            return {
                'cpu_percent': 0,
                'memory_usage': 0,
                'memory_limit': 0,
                'memory_percent': 0
            }
    
    def get_images(self) -> List[Dict[str, Any]]:
        """Get list of Docker images"""
        if not self.is_available():
            return []
        
        try:
            images = self.client.images.list()
            image_list = []
            
            for image in images:
                try:
                    attrs = image.attrs
                    tags = attrs.get('RepoTags', [])
                    
                    image_list.append({
                        'id': attrs.get('Id', '')[:12],
                        'tags': tags,
                        'created': attrs.get('Created', ''),
                        'size': attrs.get('Size', 0),
                        'virtual_size': attrs.get('VirtualSize', 0),
                        'labels': attrs.get('Labels', {}),
                        'architecture': attrs.get('Architecture', 'Unknown')
                    })
                except Exception:
                    continue
            
            return image_list
        except Exception as e:
            print(f"Error listing images: {e}")
            return []
    
    def get_container_stats(self, container_id: str = None) -> Optional[Dict[str, Any]]:
        """Get detailed statistics for a specific container"""
        if not self.is_available():
            return None
        
        try:
            if container_id:
                container = self.client.containers.get(container_id)
            else:
                # Get first running container
                containers = self.client.containers.list()
                if not containers:
                    return None
                container = containers[0]
            
            stats = container.stats(stream=False)
            
            return {
                'id': container.id[:12],
                'name': container.name,
                'cpu': {
                    'total_usage': stats.get('cpu_stats', {}).get('cpu_usage', {}).get('total_usage', 0),
                    'per_cpu_usage': stats.get('cpu_stats', {}).get('cpu_usage', {}).get('percpu_usage', []),
                    'usage_in_kernelmode': stats.get('cpu_stats', {}).get('cpu_usage', {}).get('usage_in_kernelmode', 0),
                    'usage_in_usermode': stats.get('cpu_stats', {}).get('cpu_usage', {}).get('usage_in_usermode', 0)
                },
                'memory': {
                    'usage': stats.get('memory_stats', {}).get('usage', 0),
                    'max_usage': stats.get('memory_stats', {}).get('max_usage', 0),
                    'limit': stats.get('memory_stats', {}).get('limit', 0),
                    'cache': stats.get('memory_stats', {}).get('cache', 0),
                    'rss': stats.get('memory_stats', {}).get('rss', 0)
                },
                'network': {
                    'rx_bytes': stats.get('networks', {}).get('eth0', {}).get('rx_bytes', 0),
                    'tx_bytes': stats.get('networks', {}).get('eth0', {}).get('tx_bytes', 0),
                    'rx_packets': stats.get('networks', {}).get('eth0', {}).get('rx_packets', 0),
                    'tx_packets': stats.get('networks', {}).get('eth0', {}).get('tx_packets', 0)
                },
                'pids': stats.get('pids_stats', {}).get('current', 0)
            }
        except Exception as e:
            print(f"Error getting container stats: {e}")
            return None
    
    def get_networks(self) -> List[Dict[str, Any]]:
        """Get Docker networks"""
        if not self.is_available():
            return []
        
        try:
            networks = self.client.networks.list()
            network_list = []
            
            for network in networks:
                try:
                    attrs = network.attrs
                    network_list.append({
                        'id': attrs.get('Id', '')[:12],
                        'name': attrs.get('Name', 'Unknown'),
                        'driver': attrs.get('Driver', 'Unknown'),
                        'scope': attrs.get('Scope', 'Unknown'),
                        'created': attrs.get('Created', ''),
                        'containers': len(attrs.get('Containers', {}))
                    })
                except Exception:
                    continue
            
            return network_list
        except Exception as e:
            print(f"Error listing networks: {e}")
            return []
    
    def get_volumes(self) -> List[Dict[str, Any]]:
        """Get Docker volumes"""
        if not self.is_available():
            return []
        
        try:
            volumes = self.client.volumes.list()
            volume_list = []
            
            for volume in volumes:
                try:
                    attrs = volume.attrs
                    volume_list.append({
                        'name': attrs.get('Name', 'Unknown'),
                        'driver': attrs.get('Driver', 'Unknown'),
                        'mountpoint': attrs.get('Mountpoint', 'Unknown'),
                        'created': attrs.get('CreatedAt', '')
                    })
                except Exception:
                    continue
            
            return volume_list
        except Exception as e:
            print(f"Error listing volumes: {e}")
            return []
    
    def get_events(self, since: datetime = None) -> List[Dict[str, Any]]:
        """Get Docker events"""
        if not self.is_available():
            return []
        
        try:
            if since:
                since_str = since.strftime('%Y-%m-%dT%H:%M:%S')
                events = self.client.events(since=since_str, decode_stream=True)
            else:
                events = self.client.events(decode_stream=True)
            
            event_list = []
            for event in events:
                try:
                    event_list.append({
                        'type': event.get('Type', 'Unknown'),
                        'action': event.get('Action', 'Unknown'),
                        'actor': event.get('Actor', {}).get('Attributes', {}).get('name', 'Unknown'),
                        'time': event.get('Time', 0),
                        'id': event.get('ID', '')[:12]
                    })
                except Exception:
                    continue
            
            return event_list
        except Exception as e:
            print(f"Error getting events: {e}")
            return []
    
    def get_resource_usage(self) -> Dict[str, Any]:
        """Get overall Docker resource usage"""
        if not self.is_available():
            return {}
        
        try:
            containers = self.get_containers()
            total_cpu = 0
            total_memory = 0
            running_count = 0
            
            for container in containers:
                if container['state']['running']:
                    total_cpu += container['resources'].get('cpu_percent', 0)
                    total_memory += container['resources'].get('memory_usage', 0)
                    running_count += 1
            
            return {
                'total_containers': len(containers),
                'running_containers': running_count,
                'total_cpu_percent': total_cpu,
                'total_memory_bytes': total_memory,
                'avg_cpu_percent': total_cpu / running_count if running_count > 0 else 0,
                'avg_memory_bytes': total_memory / running_count if running_count > 0 else 0
            }
        except Exception as e:
            print(f"Error calculating resource usage: {e}")
            return {}
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Docker system health status"""
        if not self.enabled:
            return {'status': 'disabled', 'message': 'Docker monitoring is disabled'}
        
        if not self.connected:
            return {'status': 'error', 'message': 'Cannot connect to Docker daemon'}
        
        try:
            docker_info = self.get_docker_info()
            resource_usage = self.get_resource_usage()
            containers = self.get_containers()
            
            issues = []
            health_score = 100
            
            # Check Docker daemon
            if not docker_info:
                health_score -= 50
                issues.append("Cannot retrieve Docker information")
            
            # Check containers
            stopped_containers = [c for c in containers if not c['state']['running']]
            if stopped_containers:
                health_score -= 10
                issues.append(f"{len(stopped_containers)} stopped containers")
            
            # Check resource usage
            if resource_usage.get('total_cpu_percent', 0) > 80:
                health_score -= 15
                issues.append(f"High CPU usage: {resource_usage['total_cpu_percent']}%")
            
            if resource_usage.get('total_memory_bytes', 0) > 85:
                health_score -= 15
                issues.append(f"High memory usage: {resource_usage['total_memory_bytes']} bytes")
            
            health_score = max(0, health_score)
            
            return {
                'status': 'healthy' if health_score >= 80 else 'warning' if health_score >= 50 else 'error',
                'score': health_score,
                'issues': issues,
                'docker_version': docker_info.get('docker_version', 'Unknown') if docker_info else 'Unknown',
                'containers_running': resource_usage.get('running_containers', 0),
                'containers_total': resource_usage.get('total_containers', 0)
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'score': 0
            }
    
    def reconnect(self) -> bool:
        """Reconnect to Docker daemon"""
        self.connected = False
        self.client = None
        return self._connect()


# Singleton instance
docker_monitor = DockerMonitor()

if __name__ == '__main__':
    # Test the Docker monitor
    monitor = DockerMonitor()
    
    if monitor.is_available():
        print("Docker Monitor Test")
        print("=" * 50)
        
        print("\nDocker Info:")
        info = monitor.get_docker_info()
        print(json.dumps(info, indent=2))
        
        print("\nContainers:")
        containers = monitor.get_containers(all_containers=True)
        for container in containers:
            print(f"  {container['name']}: {container['status']}")
        
        print("\nImages:")
        images = monitor.get_images()
        for image in images:
            print(f"  {image['tags']}: {image['size']} bytes")
        
        print("\nHealth Status:")
        health = monitor.get_health_status()
        print(json.dumps(health, indent=2))
    else:
        print("Docker is not available or monitoring is disabled")