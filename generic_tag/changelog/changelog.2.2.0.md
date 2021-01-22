- Change `_rec_name` to `name` instead of `complete_name`,
  because it is already used as default way to compute `display_name` in
  `name_get` implementation.
- Added context switch `_use_standart_name_get_` to be able to use `name`
  as `display_name` if this switch is set to `True` in context.
