"""Pavilion Cerebro agents. Every agent implements agents.base.BaseAgent."""

import warnings

# numpy 2 + Apple Accelerate emits spurious floating-point warnings from matmul on finite inputs
warnings.filterwarnings("ignore", message=r".*encountered in matmul", category=RuntimeWarning)
