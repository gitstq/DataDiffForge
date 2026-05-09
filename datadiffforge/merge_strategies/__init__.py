"""
Merge strategies package for DataDiffForge.

Provides different strategies for resolving merge conflicts.
"""

from .base import StrategyInterface
from .keep_both import KeepBothStrategy
from .left_wins import LeftWinsStrategy
from .right_wins import RightWinsStrategy
from .smart import SmartStrategy

__all__ = [
    "StrategyInterface",
    "KeepBothStrategy",
    "LeftWinsStrategy",
    "RightWinsStrategy",
    "SmartStrategy",
]

# Registry mapping strategy names to strategy classes
STRATEGY_REGISTRY = {
    "keep-both": KeepBothStrategy,
    "left-wins": LeftWinsStrategy,
    "right-wins": RightWinsStrategy,
    "smart": SmartStrategy,
}


def get_strategy(name: str) -> StrategyInterface:
    """
    Get a merge strategy instance by name.

    Args:
        name: The strategy name (e.g., 'smart', 'left-wins').

    Returns:
        An instance of the requested strategy.

    Raises:
        ValueError: If the strategy name is not recognized.
    """
    if name not in STRATEGY_REGISTRY:
        available = ', '.join(sorted(STRATEGY_REGISTRY.keys()))
        raise ValueError(
            f"Unknown strategy '{name}'. Available strategies: {available}"
        )
    return STRATEGY_REGISTRY[name]()
