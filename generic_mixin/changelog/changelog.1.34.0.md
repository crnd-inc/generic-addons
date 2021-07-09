- Added `@pre_create` and `@post_create` decorators, that allow to run
  some method before or after creation of record.
  The syntax is same as for `@pre_write` and `@post_write` decorators.
  Also, it is possible to decorate same method with pair of `@pre_` or `@post_`
  decorators, to run some method after creation and after changes of some fields
  of record.
- `changes` argument provided to tracking handler, now use *namedtuples* to represent field changes.
  Now it is possible to easily access *new* or *old* value as attribute.
  So, instead of old version `new_val = changes['my_field'][1]` now you can use `new_val = changes['my_field'].new_val`
