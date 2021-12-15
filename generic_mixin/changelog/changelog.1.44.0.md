Added ability to delay refresh view notifications,
and send some group of such notifications with a single call.
This could be used to improve performance in long-running operations that
produce a lot of updates.

To use this feature, you can use following example:

```python
with self.env['generic.mixin.refresh.view'].with_delay_refresh():
    # Do some long running operation with a lot of refresh view calls.
```

All notifications will be sent after `with` block completed.
Also, `with` blocks could be nested, and in this case,
all notofications will be sent after top-level with block completed.
