from typing import Any, List
import os
import shutil
import pathlib
import mimetypes
import uuid
from datetime import datetime
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP server
mcp = FastMCP("filesystem")

# Security settings
ALLOWED_EXTENSIONS = {
    '.txt', '.md', '.json', '.csv', '.xml', '.html', '.css', '.js', '.py', '.java', 
    '.cpp', '.c', '.h', '.rb', '.go', '.rs', '.php', '.sql', '.yaml', '.yml', 
    '.ini', '.cfg', '.conf', '.log', '.dockerfile', '.gitignore', '.env.example',
    '.pdf', '.docx', '.xlsx', '.pptx', '.zip', '.tar', '.gz'
}

# Base directory for user workspaces (relative to server execution directory)
USER_WORKSPACE_BASE = "./user-workspaces"

# Maximum file size (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024

def get_user_workspace(user_id: str = None) -> str:
    """
    Get or create user workspace directory based on user_id.
    If no user_id provided, creates a session-based workspace.
    """
    if not user_id:
        # If no user_id provided, use a session-based UUID
        # In production, this should be passed from the MCP client
        user_id = str(uuid.uuid4())
    
    # Ensure user_id is a valid UUID format (for security)
    try:
        uuid.UUID(user_id)
    except ValueError:
        # If not a valid UUID, hash it to create one
        import hashlib
        user_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, user_id))
    
    workspace_path = os.path.join(USER_WORKSPACE_BASE, user_id)
    
    # Create workspace directory if it doesn't exist
    os.makedirs(workspace_path, exist_ok=True)
    
    return workspace_path

def resolve_user_path(path: str, user_id: str = None) -> str:
    """
    Resolve a user-provided path to an absolute path within the user's workspace.
    All paths are contained within the user's isolated directory.
    """
    user_workspace = get_user_workspace(user_id)
    
    # Handle relative paths and absolute paths
    if os.path.isabs(path):
        # Remove leading slash to make it relative
        path = path.lstrip('/')
    
    # Join with user workspace
    resolved_path = os.path.join(user_workspace, path)
    
    # Ensure the resolved path is within the user workspace (prevent path traversal)
    resolved_path = os.path.abspath(resolved_path)
    workspace_abs = os.path.abspath(user_workspace)
    
    if not resolved_path.startswith(workspace_abs):
        raise ValueError(f"Path '{path}' is outside user workspace")
    
    return resolved_path

def is_safe_path(resolved_path: str, user_workspace: str) -> bool:
    """Check if resolved path is safe and within user workspace."""
    try:
        # Ensure path is within user workspace
        workspace_abs = os.path.abspath(user_workspace)
        path_abs = os.path.abspath(resolved_path)
        
        return path_abs.startswith(workspace_abs)
    except:
        return False

def get_file_info(path: str) -> dict:
    """Get file information."""
    try:
        stat = os.stat(path)
        return {
            'size': stat.st_size,
            'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
            'is_file': os.path.isfile(path),
            'is_dir': os.path.isdir(path),
            'permissions': oct(stat.st_mode)[-3:],
            'mime_type': mimetypes.guess_type(path)[0] if os.path.isfile(path) else None
        }
    except Exception as e:
        return {'error': str(e)}

@mcp.tool()
async def list_directory(path: str = ".", show_hidden: bool = False, max_items: int = 100, user_id: str = None) -> str:
    """List contents of a directory within user workspace.
    
    Args:
        path: Directory path relative to user workspace (default: current directory)
        show_hidden: Show hidden files/directories (default: False)
        max_items: Maximum number of items to show (default: 100)
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        resolved_path = resolve_user_path(path, user_id)
        
        if not is_safe_path(resolved_path, user_workspace):
            return f"Error: Access denied to path: {path}"
        
        if not os.path.exists(resolved_path):
            return f"Error: Path does not exist: {path}"
        
        if not os.path.isdir(resolved_path):
            return f"Error: Path is not a directory: {path}"
        
        items = []
        count = 0
        
        for item in sorted(os.listdir(resolved_path)):
            if count >= max_items:
                break
            
            if not show_hidden and item.startswith('.'):
                continue
            
            item_path = os.path.join(resolved_path, item)
            info = get_file_info(item_path)
            
            if 'error' in info:
                continue
            
            item_type = "DIR" if info['is_dir'] else "FILE"
            size_str = f"{info['size']} bytes" if info['is_file'] else ""
            
            # Show path relative to user workspace
            relative_item_path = os.path.relpath(item_path, user_workspace)
            
            items.append(f"""
Name: {item}
Type: {item_type}
Path: {relative_item_path}
Size: {size_str}
Modified: {info['modified']}
Permissions: {info['permissions']}
""")
            count += 1
        
        if not items:
            return f"Directory {path} is empty or no accessible items found."
        
        # Show path relative to user workspace
        relative_display_path = os.path.relpath(resolved_path, user_workspace)
        header = f"Contents of {relative_display_path} ({count} items):\n"
        return header + "\n---\n".join(items)
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error listing directory: {str(e)}"

@mcp.tool()
async def read_file(path: str, encoding: str = "utf-8", max_lines: int = 1000, user_id: str = None) -> str:
    """Read content of a text file within user workspace.
    
    Args:
        path: File path relative to user workspace
        encoding: File encoding (default: 'utf-8')
        max_lines: Maximum number of lines to read (default: 1000)
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        resolved_path = resolve_user_path(path, user_id)
        
        if not is_safe_path(resolved_path, user_workspace):
            return f"Error: Access denied to path: {path}"
        
        if not os.path.exists(resolved_path):
            return f"Error: File does not exist: {path}"
        
        if not os.path.isfile(resolved_path):
            return f"Error: Path is not a file: {path}"
        
        # Check file size
        file_size = os.path.getsize(resolved_path)
        if file_size > MAX_FILE_SIZE:
            return f"Error: File too large ({file_size} bytes). Maximum allowed: {MAX_FILE_SIZE} bytes"
        
        # Check file extension
        _, ext = os.path.splitext(resolved_path)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            return f"Error: File type '{ext}' not allowed for reading"
        
        with open(resolved_path, 'r', encoding=encoding) as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    lines.append(f"\n... (truncated after {max_lines} lines)")
                    break
                lines.append(line.rstrip())
        
        info = get_file_info(resolved_path)
        relative_path = os.path.relpath(resolved_path, user_workspace)
        
        return f"""
File: {relative_path}
Size: {info.get('size', 0)} bytes
Modified: {info.get('modified', 'Unknown')}
Encoding: {encoding}
Lines shown: {min(len(lines), max_lines)}

Content:
{''.join(lines)}
"""
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except UnicodeDecodeError:
        return f"Error: Cannot decode file with {encoding} encoding. File may be binary."
    except Exception as e:
        return f"Error reading file: {str(e)}"

@mcp.tool()
async def write_file(path: str, content: str, encoding: str = "utf-8", append: bool = False, user_id: str = None) -> str:
    """Write content to a file within user workspace.
    
    Args:
        path: File path relative to user workspace
        content: Content to write
        encoding: File encoding (default: 'utf-8')
        append: Append to file instead of overwriting (default: False)
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        resolved_path = resolve_user_path(path, user_id)
        
        if not is_safe_path(resolved_path, user_workspace):
            return f"Error: Access denied to path: {path}"
        
        # Check file extension
        _, ext = os.path.splitext(resolved_path)
        if ext.lower() not in ALLOWED_EXTENSIONS:
            return f"Error: File type '{ext}' not allowed for writing"
        
        # Create directory if it doesn't exist
        directory = os.path.dirname(resolved_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)
        
        mode = 'a' if append else 'w'
        with open(resolved_path, mode, encoding=encoding) as f:
            f.write(content)
        
        info = get_file_info(resolved_path)
        relative_path = os.path.relpath(resolved_path, user_workspace)
        action = "appended to" if append else "written to"
        
        return f"""
Content {action} file successfully!
File: {relative_path}
Size: {info.get('size', 0)} bytes
Modified: {info.get('modified', 'Unknown')}
Content length: {len(content)} characters
"""
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error writing file: {str(e)}"

@mcp.tool()
async def copy_file(source: str, destination: str, user_id: str = None) -> str:
    """Copy a file from source to destination within user workspace.
    
    Args:
        source: Source file path relative to user workspace
        destination: Destination file path relative to user workspace
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        source_resolved = resolve_user_path(source, user_id)
        dest_resolved = resolve_user_path(destination, user_id)
        
        if not is_safe_path(source_resolved, user_workspace) or not is_safe_path(dest_resolved, user_workspace):
            return f"Error: Access denied to one or both paths"
        
        if not os.path.exists(source_resolved):
            return f"Error: Source file does not exist: {source}"
        
        if not os.path.isfile(source_resolved):
            return f"Error: Source is not a file: {source}"
        
        # Check file size
        file_size = os.path.getsize(source_resolved)
        if file_size > MAX_FILE_SIZE:
            return f"Error: File too large ({file_size} bytes). Maximum allowed: {MAX_FILE_SIZE} bytes"
        
        # Create destination directory if needed
        dest_dir = os.path.dirname(dest_resolved)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        shutil.copy2(source_resolved, dest_resolved)
        
        src_info = get_file_info(source_resolved)
        dest_info = get_file_info(dest_resolved)
        
        src_relative = os.path.relpath(source_resolved, user_workspace)
        dest_relative = os.path.relpath(dest_resolved, user_workspace)
        
        return f"""
File copied successfully!
Source: {src_relative}
Destination: {dest_relative}
Size: {dest_info.get('size', 0)} bytes
Source modified: {src_info.get('modified', 'Unknown')}
Destination modified: {dest_info.get('modified', 'Unknown')}
"""
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error copying file: {str(e)}"

@mcp.tool()
async def move_file(source: str, destination: str, user_id: str = None) -> str:
    """Move/rename a file from source to destination within user workspace.
    
    Args:
        source: Source file path relative to user workspace
        destination: Destination file path relative to user workspace
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        source_resolved = resolve_user_path(source, user_id)
        dest_resolved = resolve_user_path(destination, user_id)
        
        if not is_safe_path(source_resolved, user_workspace) or not is_safe_path(dest_resolved, user_workspace):
            return f"Error: Access denied to one or both paths"
        
        if not os.path.exists(source_resolved):
            return f"Error: Source file does not exist: {source}"
        
        # Create destination directory if needed
        dest_dir = os.path.dirname(dest_resolved)
        if dest_dir and not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
        
        old_info = get_file_info(source_resolved)
        shutil.move(source_resolved, dest_resolved)
        new_info = get_file_info(dest_resolved)
        
        src_relative = os.path.relpath(source, user_workspace) if source != source_resolved else source
        dest_relative = os.path.relpath(dest_resolved, user_workspace)
        
        return f"""
File moved successfully!
From: {src_relative}
To: {dest_relative}
Size: {new_info.get('size', 0)} bytes
Modified: {new_info.get('modified', 'Unknown')}
"""
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error moving file: {str(e)}"

@mcp.tool()
async def delete_file(path: str, force: bool = False, user_id: str = None) -> str:
    """Delete a file or directory within user workspace.
    
    Args:
        path: File or directory path relative to user workspace
        force: Force deletion of non-empty directories (default: False)
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        resolved_path = resolve_user_path(path, user_id)
        
        if not is_safe_path(resolved_path, user_workspace):
            return f"Error: Access denied to path: {path}"
        
        if not os.path.exists(resolved_path):
            return f"Error: Path does not exist: {path}"
        
        info = get_file_info(resolved_path)
        relative_path = os.path.relpath(resolved_path, user_workspace)
        
        if os.path.isfile(resolved_path):
            os.remove(resolved_path)
            return f"File deleted successfully: {relative_path}"
        elif os.path.isdir(resolved_path):
            if force:
                shutil.rmtree(resolved_path)
                return f"Directory deleted successfully (forced): {relative_path}"
            else:
                os.rmdir(resolved_path)  # Only works for empty directories
                return f"Empty directory deleted successfully: {relative_path}"
        else:
            return f"Error: Unknown file type: {path}"
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except OSError as e:
        if e.errno == 39:  # Directory not empty
            return f"Error: Directory not empty. Use force=True to delete non-empty directory: {path}"
        return f"Error deleting path: {str(e)}"
    except Exception as e:
        return f"Error deleting path: {str(e)}"

@mcp.tool()
async def search_files(directory: str = ".", pattern: str = "*", file_only: bool = True, max_results: int = 50, user_id: str = None) -> str:
    """Search for files matching a pattern in user workspace directory tree.
    
    Args:
        directory: Directory to search in relative to user workspace (default: root)
        pattern: Search pattern (supports wildcards like *.py, *test*) (default: all files)
        file_only: Search only files, not directories (default: True)
        max_results: Maximum number of results (default: 50)
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        resolved_dir = resolve_user_path(directory, user_id)
        
        if not is_safe_path(resolved_dir, user_workspace):
            return f"Error: Access denied to directory: {directory}"
        
        if not os.path.exists(resolved_dir):
            return f"Error: Directory does not exist: {directory}"
        
        if not os.path.isdir(resolved_dir):
            return f"Error: Path is not a directory: {directory}"
        
        import glob
        import fnmatch
        
        matches = []
        count = 0
        
        for root, dirs, files in os.walk(resolved_dir):
            if count >= max_results:
                break
            
            # Ensure we stay within user workspace
            if not is_safe_path(root, user_workspace):
                continue
            
            items = files if file_only else files + dirs
            
            for item in items:
                if count >= max_results:
                    break
                
                if fnmatch.fnmatch(item, pattern):
                    item_path = os.path.join(root, item)
                    if is_safe_path(item_path, user_workspace):
                        info = get_file_info(item_path)
                        rel_path = os.path.relpath(item_path, user_workspace)
                        
                        item_type = "FILE" if info['is_file'] else "DIR"
                        size_str = f"{info['size']} bytes" if info['is_file'] else ""
                        
                        matches.append(f"""
Path: {rel_path}
Type: {item_type}
Size: {size_str}
Modified: {info['modified']}
""")
                        count += 1
        
        if not matches:
            return f"No files matching pattern '{pattern}' found in {directory}"
        
        relative_search_dir = os.path.relpath(resolved_dir, user_workspace)
        return f"Found {len(matches)} matches for '{pattern}' in {relative_search_dir}:\n" + "\n---\n".join(matches)
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error searching files: {str(e)}"

@mcp.tool()
async def get_file_info_tool(path: str, user_id: str = None) -> str:
    """Get detailed information about a file or directory within user workspace.
    
    Args:
        path: File or directory path relative to user workspace
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        resolved_path = resolve_user_path(path, user_id)
        
        if not is_safe_path(resolved_path, user_workspace):
            return f"Error: Access denied to path: {path}"
        
        if not os.path.exists(resolved_path):
            return f"Error: Path does not exist: {path}"
        
        info = get_file_info(resolved_path)
        relative_path = os.path.relpath(resolved_path, user_workspace)
        
        item_type = "File" if info['is_file'] else "Directory"
        
        result = f"""
Path: {relative_path}
Type: {item_type}
Size: {info['size']} bytes
Created: {info['created']}
Modified: {info['modified']}
Permissions: {info['permissions']}
"""
        
        if info.get('mime_type'):
            result += f"MIME Type: {info['mime_type']}\n"
        
        # Additional info for directories
        if info['is_dir']:
            try:
                items = os.listdir(resolved_path)
                result += f"Items: {len(items)} (files and directories)\n"
            except PermissionError:
                result += "Items: Permission denied\n"
        
        return result
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error getting file info: {str(e)}"

@mcp.tool()
async def create_directory(path: str, parents: bool = True, user_id: str = None) -> str:
    """Create a new directory within user workspace.
    
    Args:
        path: Directory path to create relative to user workspace
        parents: Create parent directories if they don't exist (default: True)
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        resolved_path = resolve_user_path(path, user_id)
        
        # Debug information
        debug_info = f"""
DEBUG INFO:
- Original path: {path}
- User workspace: {user_workspace}
- Resolved path: {resolved_path}
- User workspace exists: {os.path.exists(user_workspace)}
- User workspace is dir: {os.path.isdir(user_workspace) if os.path.exists(user_workspace) else 'N/A'}
- User workspace permissions: {oct(os.stat(user_workspace).st_mode)[-3:] if os.path.exists(user_workspace) else 'N/A'}
"""
        print(debug_info)
        
        if not is_safe_path(resolved_path, user_workspace):
            return f"Error: Access denied to path: {path}\n{debug_info}"
        
        if os.path.exists(resolved_path):
            return f"Error: Path already exists: {path}"
        
        # Ensure user workspace exists and is writable
        if not os.path.exists(user_workspace):
            try:
                os.makedirs(user_workspace, exist_ok=True)
                print(f"Created user workspace: {user_workspace}")
            except Exception as workspace_error:
                return f"Error: Cannot create user workspace: {workspace_error}\n{debug_info}"
        
        # Check if we can write to the user workspace
        if not os.access(user_workspace, os.W_OK):
            return f"Error: No write permission to user workspace: {user_workspace}\n{debug_info}"
        
        # Create the directory
        try:
            if parents:
                os.makedirs(resolved_path, exist_ok=True)
            else:
                os.mkdir(resolved_path)
        except PermissionError as perm_error:
            return f"Error: Permission denied when creating directory: {perm_error}\n{debug_info}"
        except OSError as os_error:
            return f"Error: OS error when creating directory: {os_error}\n{debug_info}"
        
        info = get_file_info(resolved_path)
        relative_path = os.path.relpath(resolved_path, user_workspace)
        
        return f"""
Directory created successfully!
Path: {relative_path}
Created: {info.get('created', 'Unknown')}
Permissions: {info.get('permissions', 'Unknown')}
"""
    
    except ValueError as e:
        return f"Error: {str(e)}"
    except Exception as e:
        return f"Error creating directory: {str(e)}"

@mcp.tool()
async def get_workspace_info(user_id: str = None) -> str:
    """Get information about the current user workspace.
    
    Args:
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        user_workspace = get_user_workspace(user_id)
        workspace_abs = os.path.abspath(user_workspace)
        
        # Get workspace statistics
        total_files = 0
        total_dirs = 0
        total_size = 0
        
        for root, dirs, files in os.walk(user_workspace):
            total_dirs += len(dirs)
            total_files += len(files)
            for file in files:
                try:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    continue
        
        return f"""
User Workspace Information:
Workspace ID: {os.path.basename(user_workspace)}
Workspace Path: {workspace_abs}
Total Files: {total_files}
Total Directories: {total_dirs}
Total Size: {total_size:,} bytes ({total_size / (1024*1024):.2f} MB)
Max File Size Limit: {MAX_FILE_SIZE:,} bytes ({MAX_FILE_SIZE / (1024*1024):.1f} MB)
Allowed Extensions: {', '.join(sorted(ALLOWED_EXTENSIONS))}
"""
    
    except Exception as e:
        return f"Error getting workspace info: {str(e)}"

@mcp.tool()
async def debug_workspace(user_id: str = None) -> str:
    """Debug workspace permissions and setup.
    
    Args:
        user_id: User UUID for workspace isolation (optional)
    """
    try:
        import pwd
        import grp
        
        user_workspace = get_user_workspace(user_id)
        workspace_abs = os.path.abspath(user_workspace)
        
        debug_info = []
        debug_info.append("=== WORKSPACE DEBUG INFO ===")
        debug_info.append(f"User ID: {user_id}")
        debug_info.append(f"User workspace: {user_workspace}")
        debug_info.append(f"Workspace absolute: {workspace_abs}")
        debug_info.append(f"Current working directory: {os.getcwd()}")
        
        # Check workspace existence
        debug_info.append(f"Workspace exists: {os.path.exists(workspace_abs)}")
        
        if os.path.exists(workspace_abs):
            stat_info = os.stat(workspace_abs)
            debug_info.append(f"Is directory: {os.path.isdir(workspace_abs)}")
            debug_info.append(f"Permissions (octal): {oct(stat_info.st_mode)[-3:]}")
            debug_info.append(f"Owner UID: {stat_info.st_uid}")
            debug_info.append(f"Group GID: {stat_info.st_gid}")
            debug_info.append(f"Readable: {os.access(workspace_abs, os.R_OK)}")
            debug_info.append(f"Writable: {os.access(workspace_abs, os.W_OK)}")
            debug_info.append(f"Executable: {os.access(workspace_abs, os.X_OK)}")
        
        # Check parent directory
        parent_dir = os.path.dirname(workspace_abs)
        debug_info.append(f"Parent directory: {parent_dir}")
        debug_info.append(f"Parent exists: {os.path.exists(parent_dir)}")
        
        if os.path.exists(parent_dir):
            parent_stat = os.stat(parent_dir)
            debug_info.append(f"Parent permissions: {oct(parent_stat.st_mode)[-3:]}")
            debug_info.append(f"Parent writable: {os.access(parent_dir, os.W_OK)}")
        
        # Current process info
        debug_info.append(f"Process UID: {os.getuid()}")
        debug_info.append(f"Process GID: {os.getgid()}")
        
        try:
            user_info = pwd.getpwuid(os.getuid())
            debug_info.append(f"Process user: {user_info.pw_name}")
        except:
            debug_info.append("Process user: Unknown")
        
        # Try to create workspace if it doesn't exist
        if not os.path.exists(workspace_abs):
            debug_info.append("--- Attempting to create workspace ---")
            try:
                os.makedirs(workspace_abs, exist_ok=True)
                debug_info.append("✅ Workspace created successfully")
            except Exception as e:
                debug_info.append(f"❌ Failed to create workspace: {e}")
        
        return "\n".join(debug_info)
        
    except Exception as e:
        return f"Error in workspace debug: {str(e)}"

def main():
    """Initialize and run the Filesystem MCP server."""
    # Ensure the user workspace base directory exists
    os.makedirs(USER_WORKSPACE_BASE, exist_ok=True)
    print(f"Filesystem MCP Server starting...")
    print(f"User workspaces base: {os.path.abspath(USER_WORKSPACE_BASE)}")
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()