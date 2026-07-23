"""Re-export centralized logging from pobi_agent.

This module re-exports the logging utilities from pobi_agent.logging
for backwards compatibility and convenience, without shadowing the
standard library ``logging`` module.

Usage:
    from pobi.cli_logging import logger, setup_logging

    # Setup logging at startup (typically in RPC server or main)
    setup_logging(level=logging.DEBUG)

    # Use logger anywhere
    logger.debug("Debug message")
    logger.info("Info message")
"""

from pobi_agent.logging import (
    logger,
    setup_logging,
    get_module_logger,
    LOGGER_NAME,
)

__all__ = ["logger", "setup_logging", "get_module_logger", "LOGGER_NAME"]


