"""
Mute cmdstanpy / Prophet console spam.

cmdstanpy often adds StreamHandlers to its loggers; changing the logger level alone
does not stop INFO lines. Clearing handlers + propagate False + NullHandler fixes that.
"""

from __future__ import annotations

import logging


def _mute_logger(name: str) -> None:
    log = logging.getLogger(name)
    log.handlers.clear()
    log.propagate = False
    log.setLevel(logging.CRITICAL)
    log.addHandler(logging.NullHandler())


def silence_cmdstan_loggers() -> None:
    """Call on startup and again before Prophet.fit (cmdstanpy may register loggers lazily)."""
    for base in ("cmdstanpy", "prophet", "pystan", "fbprophet"):
        _mute_logger(base)

    for key in list(logging.root.manager.loggerDict.keys()):
        if not isinstance(key, str):
            continue
        if key.startswith("cmdstanpy.") or key.startswith("prophet."):
            _mute_logger(key)
