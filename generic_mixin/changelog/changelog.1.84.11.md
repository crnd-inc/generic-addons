- Fixed `AccessRulesFixMixinST`/`AccessRulesFixMixinMT` test mixins for
  Odoo 20: `ir.rule` model was removed and its records were merged into
  `ir.access`. Test helpers now deactivate `ir.access` records from
  uninitialized modules instead, and `deactivate_records_for_model`
  safely skips models that are not present in the registry.
