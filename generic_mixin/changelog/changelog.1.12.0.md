Make `post_write` and `pre_write` decorators propagatable.
Now when you override same `post_write` method in different subclasses,
all dependency fields will be merged,
and same method will will be called on change of each field.

Additionally added `priority` param for `pre_write` and `post_write` handlers,
thus you can define the order handlers will be executred in.
