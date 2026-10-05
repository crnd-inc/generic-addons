- Re-enabled automatic refresh of views (disabled during forwardport on 17.0)
  and ported its javascript to the Odoo 19 API:
  new `patch` signature, `useSetupAction` hook instead of removed
  `useSetupView`, `KeepLast` instead of removed `MutexedDropPrevious`
  and own throttling instead of removed underscore.js.
- Switched bus subscription to `bus_service.subscribe`, because since Odoo 17
  notifications are dispatched per notification type and the generic
  'notification' event is not triggered anymore.
- Fixed refresh notifications sent from `with_delay_refresh` blocks: record ids
  were sent to the browser as a string representation of a python set
  (`"{1}"`) instead of a list, thus web client was not able to match them
  with displayed records.
- Restored highlighting of created/updated records in list and kanban views.
  Changed records are now passed to renderers via a shared reactive store,
  instead of the legacy renderer widget api.
