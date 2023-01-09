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


def migrate_xmlids_to_module(cr, src_module, dst_module, models,
                             cleanup=False):
    """ Move XMLID references (ir.model.data) from namespace of 'src_module',
        to namespace of 'dst_module' for modules 'models'.

        This is used, when you need to move data from one module to another,
        or when you need to merge one module into another.

        :param str src_module: Name of source module to migrate xmlids from
        :param str dst_module: Name of destination module to migrate
            xmlids to
        :param list[str] models: List of models to migrate
        :param bool cleanup: If true, then records that were not migrated
            will be removed.
    """
    cr.execute("""
        UPDATE ir_model_data
        SET module = %(dst_module)s
        WHERE module = %(src_module)s
          AND model IN %(models)s
          AND name NOT IN (
              SELECT name FROM ir_model_data WHERE module = %(dst_module)s);
    """, {
        'src_module': src_module,
        'dst_module': dst_module,
        'models': tuple(models),
    })

    if cleanup:
        cr.execute("""
            /* Cleanup records, that were not moved to dst_module
               (because, there are already existing records
               with same name present) */
            DELETE FROM ir_model_data
            WHERE module = %(src_module)s
              AND model IN %(models)s;
        """, {
            'src_module': src_module,
            'dst_module': dst_module,
            'models': tuple(models),
        })


def cleanup_module_data(cr, module_name):
    """ Delete views, constraints, relations, etc that were not migrated

        Usually this func could be used when merging one module into another.
        And in this case, all required data have to be migrated,
        but the references to views constraints and relations have to be
        removed after all previous migrations done. These objects will be
        recreated automatically when needed based on xml.
    """
    cr.execute("""
        -- Delete views
        DELETE FROM ir_ui_view WHERE id IN (
            SELECT res_id
            FROM ir_model_data
            WHERE model = 'ir.ui.view'
              AND module = %(module_name)s
        );
        DELETE FROM ir_model_data
        WHERE model = 'ir.ui.view'
          AND module = %(module_name)s;

        -- Delete constraints (these models do not have related xmlids)
        DELETE FROM ir_model_constraint WHERE module = (
            SELECT id
            FROM ir_module_module
            WHERE name = %(module_name)s
        );
        DELETE FROM ir_model_relation WHERE module = (
            SELECT id
            FROM ir_module_module
            WHERE name = %(module_name)s
        );

        -- DELETE references to ir_model
        DELETE FROM ir_model_data
        WHERE model = 'ir.model'
          AND module = %(module_name)s;
    """, {
        'module_name': module_name,
    })


def fix_view_inheritance(cr, original_view, replace_view):
    """ Fix view inheritance chain.
        This function will find all views inherited from original view,
        and changes their inheritance to 'replace_view'.

        :param cr: Database cursor
        :param str original_view: fully qualified XMLID of original view
        :param str replace_view: fully qualified XMLID of replacement view.
    """
    o_module, o_name = original_view.split('.')
    r_module, r_name = replace_view.split('.')

    cr.execute("""
        UPDATE ir_ui_view AS iuv
        SET inherit_id = (
            SELECT res_id
            FROM ir_model_data AS imd
            WHERE imd.module = %(r_module)s
              AND imd.model = 'ir.ui.view'
              AND imd.name = %(r_name)s
        )
        WHERE iuv.inherit_id IN (
            SELECT res_id
            FROM ir_model_data AS imd
            WHERE imd.module = %(o_module)s
              AND imd.model = 'ir.ui.view'
              AND imd.name = %(o_name)s
        )
    """, {
        'r_module': r_module,
        'r_name': r_name,
        'o_module': o_module,
        'o_name': o_name,
    })
