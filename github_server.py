from typing import Any, List
import httpx
from mcp.server.fastmcp import FastMCP
import os
import base64

# Initialize FastMCP server
mcp = FastMCP("github")

# Get GitHub token from environment
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_API_BASE = "https://api.github.com"

async def make_github_request(endpoint: str, method: str = "GET", data: dict = None) -> dict[str, Any] | None:
    """Make a request to GitHub API with proper error handling."""
    if not GITHUB_TOKEN:
        return {"error": "GITHUB_TOKEN environment variable not set"}
    
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "MCP-GitHub-Server/1.0"
    }
    
    url = f"{GITHUB_API_BASE}/{endpoint}"
    
    async with httpx.AsyncClient() as client:
        try:
            if method == "GET":
                response = await client.get(url, headers=headers, params=data or {})
            elif method == "POST":
                response = await client.post(url, headers=headers, json=data or {})
            elif method == "PATCH":
                response = await client.patch(url, headers=headers, json=data or {})
            elif method == "DELETE":
                response = await client.delete(url, headers=headers)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

@mcp.tool()
async def list_repositories(username: str = "", org: str = "", type: str = "all") -> str:
    """List repositories for a user or organization.
    
    Args:
        username: GitHub username (optional, uses authenticated user if not provided)
        org: Organization name (optional)
        type: Repository type - 'all', 'owner', 'public', 'private', 'member' (default: 'all')
    """
    try:
        if org:
            endpoint = f"orgs/{org}/repos"
        elif username:
            endpoint = f"users/{username}/repos"
        else:
            endpoint = "user/repos"
        
        params = {"type": type, "per_page": 30, "sort": "updated"}
        data = await make_github_request(endpoint, "GET", params)
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not isinstance(data, list):
            return f"GitHub API error: {data.get('message', 'Unknown error')}"
        
        if not data:
            return "No repositories found."
        
        repo_list = []
        for repo in data:
            repo_info = f"""
Name: {repo['name']}
Full Name: {repo['full_name']}
Description: {repo.get('description', 'No description')}
Language: {repo.get('language', 'Unknown')}
Stars: {repo['stargazers_count']}
Forks: {repo['forks_count']}
Private: {repo['private']}
URL: {repo['html_url']}
"""
            repo_list.append(repo_info)
        
        return "\n---\n".join(repo_list)
    
    except Exception as e:
        return f"Error listing repositories: {str(e)}"

@mcp.tool()
async def get_repository_info(owner: str, repo: str) -> str:
    """Get detailed information about a specific repository.
    
    Args:
        owner: Repository owner (username or organization)
        repo: Repository name
    """
    try:
        data = await make_github_request(f"repos/{owner}/{repo}")
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if "message" in data:
            return f"GitHub API error: {data['message']}"
        
        return f"""
Repository: {data['full_name']}
Description: {data.get('description', 'No description')}
Language: {data.get('language', 'Unknown')}
Stars: {data['stargazers_count']}
Forks: {data['forks_count']}
Watchers: {data['watchers_count']}
Open Issues: {data['open_issues_count']}
Default Branch: {data['default_branch']}
Created: {data['created_at']}
Updated: {data['updated_at']}
License: {data.get('license', {}).get('name', 'No license') if data.get('license') else 'No license'}
Homepage: {data.get('homepage', 'None')}
Topics: {', '.join(data.get('topics', [])) if data.get('topics') else 'None'}
Private: {data['private']}
Fork: {data['fork']}
Archived: {data['archived']}
URL: {data['html_url']}
Clone URL: {data['clone_url']}
"""
    
    except Exception as e:
        return f"Error getting repository info: {str(e)}"

@mcp.tool()
async def list_issues(owner: str, repo: str, state: str = "open", labels: str = "") -> str:
    """List issues for a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        state: Issue state - 'open', 'closed', 'all' (default: 'open')
        labels: Comma-separated list of label names to filter by (optional)
    """
    try:
        params = {"state": state, "per_page": 20}
        if labels:
            params["labels"] = labels
        
        data = await make_github_request(f"repos/{owner}/{repo}/issues", "GET", params)
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not isinstance(data, list):
            return f"GitHub API error: {data.get('message', 'Unknown error')}"
        
        if not data:
            return f"No {state} issues found."
        
        issue_list = []
        for issue in data:
            # Skip pull requests (they appear in issues API)
            if "pull_request" in issue:
                continue
            
            labels_str = ", ".join([label["name"] for label in issue.get("labels", [])])
            
            issue_info = f"""
Title: {issue['title']}
Number: #{issue['number']}
State: {issue['state']}
Author: {issue['user']['login']}
Labels: {labels_str if labels_str else 'None'}
Created: {issue['created_at']}
Updated: {issue['updated_at']}
Comments: {issue['comments']}
URL: {issue['html_url']}
"""
            issue_list.append(issue_info)
        
        return "\n---\n".join(issue_list)
    
    except Exception as e:
        return f"Error listing issues: {str(e)}"

@mcp.tool()
async def create_issue(owner: str, repo: str, title: str, body: str = "", labels: str = "") -> str:
    """Create a new issue in a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        title: Issue title
        body: Issue description (optional)
        labels: Comma-separated list of label names (optional)
    """
    try:
        issue_data = {
            "title": title,
            "body": body
        }
        
        if labels:
            issue_data["labels"] = [label.strip() for label in labels.split(",")]
        
        data = await make_github_request(f"repos/{owner}/{repo}/issues", "POST", issue_data)
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if "message" in data:
            return f"GitHub API error: {data['message']}"
        
        return f"""
Issue created successfully!
Title: {data['title']}
Number: #{data['number']}
URL: {data['html_url']}
State: {data['state']}
Created: {data['created_at']}
"""
    
    except Exception as e:
        return f"Error creating issue: {str(e)}"

@mcp.tool()
async def get_file_content(owner: str, repo: str, path: str, branch: str = "") -> str:
    """Get the content of a file from a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        path: Path to the file
        branch: Branch name (optional, defaults to default branch)
    """
    try:
        params = {}
        if branch:
            params["ref"] = branch
        
        data = await make_github_request(f"repos/{owner}/{repo}/contents/{path}", "GET", params)
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if "message" in data:
            return f"GitHub API error: {data['message']}"
        
        if data.get("type") != "file":
            return f"Error: {path} is not a file"
        
        # Decode base64 content
        content = base64.b64decode(data["content"]).decode('utf-8')
        
        return f"""
File: {path}
Size: {data['size']} bytes
SHA: {data['sha']}
URL: {data['html_url']}

Content:
{content}
"""
    
    except Exception as e:
        return f"Error getting file content: {str(e)}"

@mcp.tool()
async def list_pull_requests(owner: str, repo: str, state: str = "open") -> str:
    """List pull requests for a repository.
    
    Args:
        owner: Repository owner
        repo: Repository name
        state: PR state - 'open', 'closed', 'all' (default: 'open')
    """
    try:
        params = {"state": state, "per_page": 20}
        data = await make_github_request(f"repos/{owner}/{repo}/pulls", "GET", params)
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if not isinstance(data, list):
            return f"GitHub API error: {data.get('message', 'Unknown error')}"
        
        if not data:
            return f"No {state} pull requests found."
        
        pr_list = []
        for pr in data:
            pr_info = f"""
Title: {pr['title']}
Number: #{pr['number']}
State: {pr['state']}
Author: {pr['user']['login']}
Base: {pr['base']['ref']}
Head: {pr['head']['ref']}
Created: {pr['created_at']}
Updated: {pr['updated_at']}
Mergeable: {pr.get('mergeable', 'Unknown')}
Comments: {pr['comments']}
Commits: {pr['commits']}
URL: {pr['html_url']}
"""
            pr_list.append(pr_info)
        
        return "\n---\n".join(pr_list)
    
    except Exception as e:
        return f"Error listing pull requests: {str(e)}"

@mcp.tool()
async def search_repositories(query: str, sort: str = "stars", order: str = "desc") -> str:
    """Search GitHub repositories.
    
    Args:
        query: Search query
        sort: Sort field - 'stars', 'forks', 'updated' (default: 'stars')
        order: Sort order - 'asc', 'desc' (default: 'desc')
    """
    try:
        params = {
            "q": query,
            "sort": sort,
            "order": order,
            "per_page": 20
        }
        
        data = await make_github_request("search/repositories", "GET", params)
        
        if "error" in data:
            return f"Error: {data['error']}"
        
        if "message" in data:
            return f"GitHub API error: {data['message']}"
        
        items = data.get("items", [])
        if not items:
            return f"No repositories found for query: {query}"
        
        repo_list = []
        for repo in items:
            repo_info = f"""
Name: {repo['full_name']}
Description: {repo.get('description', 'No description')}
Language: {repo.get('language', 'Unknown')}
Stars: {repo['stargazers_count']}
Forks: {repo['forks_count']}
Score: {repo['score']:.2f}
URL: {repo['html_url']}
"""
            repo_list.append(repo_info)
        
        return f"Found {data['total_count']} repositories. Showing top {len(items)}:\n" + "\n---\n".join(repo_list)
    
    except Exception as e:
        return f"Error searching repositories: {str(e)}"

def main():
    """Initialize and run the GitHub MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()