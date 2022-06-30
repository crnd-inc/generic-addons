import re
import logging
import functools
from .utils import V

_logger = logging.getLogger(__name__)

RE_VERSION = re.compile(
    r"^"
    r"(?P<serie>\d+\.\d+)\."
    r"(?P<version>\d+(\.\d+){0,2})"
    r"$")


def ensure_version(version):
    """ Ensure that migration will be running only if installed version is
        less then expected.
        This decorator could be useful to handle database migrations between
        different odoo series.

        Note: it is required to use standard version numbering to use this
        decorator. Standard versions numbering means that versions in modules
        and migrations have to be specified as five-number string, like:
            - X.X.Y.Y.Y
            - 15.0.0.1.3
        Where:
            - X.X - odoo version (odoo server version)
            - Y.Y.Y - Module version

        This guard, allows to avoid running migration on server-version change,
        if module version kept same (or below).

        :param str version: expected module version to run migration.
            This must not include odoo serie!
    """
    def wrapper(fn):
        @functools.wraps(fn)
        def migrate(cr, installed_version):
            match = RE_VERSION.match(installed_version)
            if not match:
                _logger.warning(
                    "Installed version of module has non-standard version! "
                    "Ensure version guard will not work in this case. \n"
                    "Running migration...")
                return fn(cr, installed_version)
            installed_ver = match.group('version')
            if V(installed_ver) < V(version):
                return fn(cr, installed_version)
            _logger.info(
                "Skipping migration, because installed module version is "
                "greater or equal to migration version.")
            return None
        return migrate
    return wrapper
