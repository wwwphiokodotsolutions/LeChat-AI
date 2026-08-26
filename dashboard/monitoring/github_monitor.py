"""
GitHub Monitor
Monitors GitHub repositories for issues, PRs, commits, and other activities
"""

import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json


class GitHubMonitor:
    """Monitor GitHub repository activities"""
    
    GITHUB_API_URL = "https://api.github.com"
    
    def __init__(self, token: str = None, repo: str = None):
        """
        Initialize GitHub monitor
        
        Args:
            token: GitHub personal access token
            repo: Repository in format 'owner/repo'
        """
        self.token = token
        self.repo = repo
        self.session = requests.Session()
        
        if token:
            self.session.headers.update({
                'Authorization': f'token {token}',
                'Accept': 'application/vnd.github.v3+json'
            })
        else:
            self.session.headers.update({
                'Accept': 'application/vnd.github.v3+json'
            })
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to GitHub API"""
        try:
            url = f"{self.GITHUB_API_URL}/{endpoint}"
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 403:
                # Rate limit exceeded
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                print(f"Rate limit exceeded. Reset at: {datetime.fromtimestamp(reset_time)}")
                return None
            else:
                print(f"GitHub API error: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"Error making GitHub API request: {e}")
            return None
    
    def get_repo_info(self) -> Optional[Dict[str, Any]]:
        """Get repository information"""
        if not self.repo:
            return None
        
        data = self._make_request(f"repos/{self.repo}")
        if data:
            return {
                'name': data.get('name'),
                'full_name': data.get('full_name'),
                'description': data.get('description'),
                'stars': data.get('stargazers_count', 0),
                'forks': data.get('forks_count', 0),
                'open_issues': data.get('open_issues_count', 0),
                'language': data.get('language'),
                'created_at': data.get('created_at'),
                'updated_at': data.get('updated_at'),
                'pushed_at': data.get('pushed_at'),
                'size': data.get('size'),
                'license': data.get('license', {}).get('name') if data.get('license') else None,
                'html_url': data.get('html_url')
            }
        return None
    
    def get_open_issues(self, state: str = 'open', limit: int = 50) -> List[Dict[str, Any]]:
        """Get open issues"""
        if not self.repo:
            return []
        
        params = {
            'state': state,
            'per_page': min(limit, 100),  # GitHub max per_page is 100
            'sort': 'created',
            'direction': 'desc'
        }
        
        data = self._make_request(f"repos/{self.repo}/issues", params)
        if data:
            issues = []
            for issue in data:
                if 'pull_request' in issue:
                    continue  # Skip pull requests
                
                issues.append({
                    'id': issue.get('id'),
                    'number': issue.get('number'),
                    'title': issue.get('title'),
                    'state': issue.get('state'),
                    'created_at': issue.get('created_at'),
                    'updated_at': issue.get('updated_at'),
                    'labels': [label.get('name') for label in issue.get('labels', [])],
                    'assignee': issue.get('assignee', {}).get('login') if issue.get('assignee') else None,
                    'comments': issue.get('comments'),
                    'html_url': issue.get('html_url')
                })
            return issues
        return []
    
    def get_pull_requests(self, state: str = 'open', limit: int = 50) -> List[Dict[str, Any]]:
        """Get pull requests"""
        if not self.repo:
            return []
        
        params = {
            'state': state,
            'per_page': min(limit, 100),
            'sort': 'created',
            'direction': 'desc'
        }
        
        data = self._make_request(f"repos/{self.repo}/pulls", params)
        if data:
            prs = []
            for pr in data:
                prs.append({
                    'id': pr.get('id'),
                    'number': pr.get('number'),
                    'title': pr.get('title'),
                    'state': pr.get('state'),
                    'created_at': pr.get('created_at'),
                    'updated_at': pr.get('updated_at'),
                    'merged_at': pr.get('merged_at'),
                    'labels': [label.get('name') for label in pr.get('labels', [])],
                    'assignee': pr.get('assignee', {}).get('login') if pr.get('assignee') else None,
                    'comments': pr.get('comments'),
                    'commits': pr.get('commits'),
                    'additions': pr.get('additions'),
                    'deletions': pr.get('deletions'),
                    'changed_files': pr.get('changed_files'),
                    'html_url': pr.get('html_url')
                })
            return prs
        return []
    
    def get_recent_commits(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent commits"""
        if not self.repo:
            return []
        
        params = {
            'per_page': min(limit, 100),
            'sha': 'main'  # or 'master'
        }
        
        data = self._make_request(f"repos/{self.repo}/commits", params)
        if data:
            commits = []
            for commit in data:
                commits.append({
                    'sha': commit.get('sha')[:7],
                    'message': commit.get('commit', {}).get('message', '').split('\n')[0],
                    'author': commit.get('commit', {}).get('author', {}).get('name'),
                    'date': commit.get('commit', {}).get('author', {}).get('date'),
                    'html_url': commit.get('html_url')
                })
            return commits
        return []
    
    def get_contributors(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get repository contributors"""
        if not self.repo:
            return []
        
        params = {
            'per_page': min(limit, 100),
            'anon': 'false'
        }
        
        data = self._make_request(f"repos/{self.repo}/contributors", params)
        if data:
            contributors = []
            for contributor in data:
                contributors.append({
                    'login': contributor.get('login'),
                    'avatar_url': contributor.get('avatar_url'),
                    'contributions': contributor.get('contributions'),
                    'html_url': contributor.get('html_url')
                })
            return contributors
        return []
    
    def get_workflow_runs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent workflow runs"""
        if not self.repo:
            return []
        
        params = {
            'per_page': min(limit, 100)
        }
        
        data = self._make_request(f"repos/{self.repo}/actions/runs", params)
        if data and 'workflow_runs' in data:
            runs = []
            for run in data['workflow_runs']:
                runs.append({
                    'id': run.get('id'),
                    'name': run.get('name'),
                    'status': run.get('status'),
                    'conclusion': run.get('conclusion'),
                    'event': run.get('event'),
                    'created_at': run.get('created_at'),
                    'updated_at': run.get('updated_at'),
                    'html_url': run.get('html_url')
                })
            return runs
        return []
    
    def get_repo_stats(self) -> Dict[str, Any]:
        """Get comprehensive repository statistics"""
        if not self.repo:
            return {}
        
        repo_info = self.get_repo_info()
        issues = self.get_open_issues()
        prs = self.get_pull_requests()
        commits = self.get_recent_commits(10)
        contributors = self.get_contributors(10)
        workflow_runs = self.get_workflow_runs(10)
        
        return {
            'repo': repo_info,
            'issues': {
                'total': len(issues),
                'open': len([i for i in issues if i['state'] == 'open']),
                'closed': len([i for i in issues if i['state'] == 'closed']),
                'recent': issues[:5]
            },
            'pull_requests': {
                'total': len(prs),
                'open': len([p for p in prs if p['state'] == 'open']),
                'closed': len([p for p in prs if p['state'] == 'closed']),
                'merged': len([p for p in prs if p['merged_at']]),
                'recent': prs[:5]
            },
            'commits': {
                'total': len(commits),
                'recent': commits
            },
            'contributors': {
                'total': len(contributors),
                'recent': contributors
            },
            'workflows': {
                'total': len(workflow_runs),
                'recent': workflow_runs
            }
        }
    
    def check_health(self) -> Dict[str, Any]:
        """Check repository health and activity"""
        stats = self.get_repo_stats()
        
        health_score = 100
        issues = []
        
        # Check for stale issues
        if stats.get('issues', {}).get('open', 0) > 10:
            health_score -= 10
            issues.append(f"High number of open issues: {stats['issues']['open']}")
        
        # Check for stale PRs
        if stats.get('pull_requests', {}).get('open', 0) > 5:
            health_score -= 10
            issues.append(f"High number of open PRs: {stats['pull_requests']['open']}")
        
        # Check for recent commits
        recent_commits = stats.get('commits', {}).get('total', 0)
        if recent_commits == 0:
            health_score -= 20
            issues.append("No recent commits detected")
        
        # Check workflow status
        workflow_runs = stats.get('workflows', {}).get('recent', [])
        failed_workflows = [w for w in workflow_runs if w.get('status') == 'completed' and w.get('conclusion') == 'failure']
        if failed_workflows:
            health_score -= 15
            issues.append(f"Failed workflows: {len(failed_workflows)}")
        
        health_score = max(0, health_score)
        
        return {
            'score': health_score,
            'grade': self._get_grade(health_score),
            'issues': issues,
            'last_updated': datetime.now().isoformat()
        }
    
    def _get_grade(self, score: int) -> str:
        """Convert health score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 80:
            return 'A'
        elif score >= 70:
            return 'B'
        elif score >= 60:
            return 'C'
        elif score >= 50:
            return 'D'
        else:
            return 'F'
    
    def set_repo(self, repo: str):
        """Set the repository to monitor"""
        self.repo = repo
    
    def set_token(self, token: str):
        """Set GitHub token"""
        self.token = token
        if token:
            self.session.headers['Authorization'] = f'token {token}'
        else:
            if 'Authorization' in self.session.headers:
                del self.session.headers['Authorization']


# Singleton instance
github_monitor = GitHubMonitor()

if __name__ == '__main__':
    # Test the GitHub monitor
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    token = os.getenv('GITHUB_TOKEN')
    repo = os.getenv('GITHUB_REPO', 'wwwphiokodotsolutions/LeChat-AI')
    
    monitor = GitHubMonitor(token, repo)
    
    print("Repository Info:")
    repo_info = monitor.get_repo_info()
    print(json.dumps(repo_info, indent=2))
    
    print("\nRepository Stats:")
    stats = monitor.get_repo_stats()
    print(f"  Issues: {stats['issues']['total']} (open: {stats['issues']['open']})")
    print(f"  PRs: {stats['pull_requests']['total']} (open: {stats['pull_requests']['open']})")
    print(f"  Commits: {stats['commits']['total']}")
    print(f"  Contributors: {stats['contributors']['total']}")
    
    print("\nHealth Check:")
    health = monitor.check_health()
    print(f"  Score: {health['score']} ({health['grade']})")
    if health['issues']:
        for issue in health['issues']:
            print(f"    - {issue}")