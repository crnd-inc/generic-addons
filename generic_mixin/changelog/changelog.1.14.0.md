- Added new method to `generic.mixin.transaction.utils` - `_iter_in_transact`,
  thus it is possible to iterate over records and process each record in separate transaction.
- Added new function `generic_mixin.tools.jinja.render_jinja_string` that
  could be imported via `from odoo.addons.generic_mixin import render_jinja_string`.
  This function allows to render jinja template passed as a string.
