"""
Code Editing Agent - Symbol-Aware Code Modifications

Advanced code editing agent specializing in safe code modifications,
symbol-aware refactoring, and automated code transformations.
"""

from lib.utils.version_factory import create_agent


async def get_code_editing_agent(**kwargs):
    """
    Create code editing agent with dynamic configuration.
    
    This factory function creates an agent specialized in symbol-aware
    code editing and refactoring operations.
    
    Args:
        **kwargs: Context parameters for template rendering including:
            - user_id: User identifier for context loading
            - session_id: Session identifier
            - debug_mode: Enable debug features
            - tenant_id: Tenant/organization identifier
            - custom_context: Additional template variables
    
    Returns:
        Agent instance configured for code editing operations
    """
    return await create_agent("code-editing-agent", **kwargs)