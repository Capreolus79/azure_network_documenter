"""
Shared utilities for Azure Network Documenter.
"""

import logging
import sys
from typing import Optional


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """Configure and return the application logger."""
    logger = logging.getLogger("azure_network_documenter")

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(level)
    return logger


def extract_name_from_id(resource_id: Optional[str]) -> str:
    """
    Extract resource name from Azure resource ID.

    Azure resource IDs follow the pattern:
    /subscriptions/{sub}/resourceGroups/{rg}/providers/{provider}/{type}/{name}

    Args:
        resource_id: Full Azure resource ID

    Returns:
        The resource name (last segment of the ID) or empty string
    """
    if not resource_id:
        return ""
    parts = resource_id.split("/")
    return parts[-1] if parts else ""


# Create default logger instance
logger = setup_logging()
