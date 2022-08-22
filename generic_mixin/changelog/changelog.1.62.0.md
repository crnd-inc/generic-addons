Added few new methods to `generic_mixin.tools.sql`:
- `xmlid_to_id(cr, xmlid)` that could be used to convert `xmlid` to ID of referenced object
- `unlink_view(cr, xmlid)` that could be used to remove view by xmlid. This could be helpful during migrations.
