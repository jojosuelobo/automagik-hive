"""
Code Understanding Agent - Deep Code Analysis and Comprehension

Specialized agent for analyzing codebases, understanding project structure,
and providing insights about code architecture and dependencies.
"""

from lib.utils.version_factory import create_agent


async def get_code_understanding_agent(**kwargs):
    """
    Create code understanding agent with dynamic configuration.
    
    This factory function creates an agent specialized in code analysis
    and architectural understanding.
    
    Args:
        **kwargs: Context parameters for template rendering including:
            - user_id: User identifier for context loading
            - session_id: Session identifier
            - debug_mode: Enable debug features
            - tenant_id: Tenant/organization identifier
            - custom_context: Additional template variables
    
    Returns:
        Agent instance configured for code understanding operations
    """
    return await create_agent("code-understanding-agent", **kwargs)