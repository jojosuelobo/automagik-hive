"""
Project Orchestration Agent - Multi-Component Coordination

Master coordination agent for managing complex multi-file operations
and orchestrating collaboration between specialized agents.
"""

from lib.utils.version_factory import create_agent


async def get_project_orchestration_agent(**kwargs):
    """
    Create project orchestration agent with dynamic configuration.
    
    This factory function creates an agent specialized in project-level
    coordination and multi-agent collaboration.
    
    Args:
        **kwargs: Context parameters for template rendering including:
            - user_id: User identifier for context loading
            - session_id: Session identifier
            - debug_mode: Enable debug features
            - tenant_id: Tenant/organization identifier
            - custom_context: Additional template variables
    
    Returns:
        Agent instance configured for project orchestration
    """
    return await create_agent("project-orchestration-agent", **kwargs)