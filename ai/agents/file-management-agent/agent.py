"""
File Management Agent - File System Operations and Organization

Specialized agent for file and directory operations, project organization,
and maintaining clean file system structure.
"""

from lib.utils.version_factory import create_agent


async def get_file_management_agent(**kwargs):
    """
    Create file management agent with dynamic configuration.
    
    This factory function creates an agent specialized in file system
    operations and project organization.
    
    Args:
        **kwargs: Context parameters for template rendering including:
            - user_id: User identifier for context loading
            - session_id: Session identifier
            - debug_mode: Enable debug features
            - tenant_id: Tenant/organization identifier
            - custom_context: Additional template variables
    
    Returns:
        Agent instance configured for file management operations
    """
    return await create_agent("file-management-agent", **kwargs)