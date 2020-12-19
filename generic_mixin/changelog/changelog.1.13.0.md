Added new mixin `generic.mixin.get.action` that could be used for compatability
with 14.0 for cases, when python method have to return action read from xml
by xmlid.

Also added definition for variables *TEST_URL*, *HOST*, *PORT*
in `generic_mixin.tests.common` module. this is also for compatability
with 14.0, so, using this variables in 12.0+ could help to write code that
is easier to port to next odoo versions
