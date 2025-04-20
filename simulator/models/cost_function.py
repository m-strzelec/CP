"""Implements the priority cost function for scheduling."""

import math


def compute_cost(size: float, wait_time: float, m: float, k: float) -> float:
    """Calculate cost function. Lower cost => higher scheduling priority.

    Parameters
    ----------
    size : float
        Size of the file.
    wait_time : float
        Time in seconds that file waited since its arrival.
    m : float
        TODO: Param 1
    k : float
        TODO: Param 2

    Returns
    -------
    float
        Cost function for scheduling.
    """
    safe_wait_time: float = max(wait_time, 0.001)
    size_cost: float = (1.0 / m) * math.log(size + 1)
    wait_cost: float = k / math.sqrt(safe_wait_time)
    return size_cost + wait_cost
