"""
Utility functions for the convert module.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def safe_get_nested(data: Dict[str, Any], *keys: str, default: Any = None) -> Any:
    """
    Safely get nested dictionary values with fallback.

    Args:
        data: Dictionary to search
        *keys: Sequence of keys to traverse
        default: Default value if key path doesn't exist

    Returns:
        Value at the nested key path or default
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def validate_required_fields(data: Dict[str, Any], required_fields: list[str]) -> bool:
    """
    Validate that required fields exist in a dictionary.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names

    Returns:
        True if all required fields exist, False otherwise
    """
    for field in required_fields:
        if field not in data:
            logger.warning(f"Missing required field: {field}")
            return False
    return True


def normalize_restart_policy(policy: str) -> str:
    """
    Normalize restart policy names to Docker Compose format.

    Args:
        policy: Original restart policy name

    Returns:
        Normalized restart policy name
    """
    policy_map = {
        "onfailure": "on-failure",
        "always": "always",
        "unless-stopped": "unless-stopped",
        "no": "no",
    }
    return policy_map.get(policy.lower(), policy)


def format_memory_limit(memory: Optional[int]) -> Optional[str]:
    """
    Format memory limit for Docker Compose.

    Args:
        memory: Memory limit in MB

    Returns:
        Formatted memory string or None
    """
    if memory is None:
        return None
    return f"{memory}m"


def format_cpu_limit(cpu: Optional[Any]) -> Optional[str]:
    """
    Format CPU limit for Docker Compose.

    Args:
        cpu: CPU limit value

    Returns:
        Formatted CPU string or None
    """
    if cpu is None:
        return None
    return str(cpu)
