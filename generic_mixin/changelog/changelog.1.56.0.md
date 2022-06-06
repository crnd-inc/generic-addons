Added new mixin `generic.mixin.entity.lifecycle` that adds
`lifecycle_state` field and dates of `lifecycle_state` changes.
Also, this mixin added additional logic to prevent deletion of *active*
entities and control changes of lifecycle states.
