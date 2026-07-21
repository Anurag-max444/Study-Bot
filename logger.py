"""
Centralized logging configuration. Every module just does `import logging`
and calls logging.info/.exception/etc as normal — this file's only job is to
call basicConfig() exactly once, in one place, instead of scattering the
setup call across the codebase.
"""
import logging


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


setup_logging()
