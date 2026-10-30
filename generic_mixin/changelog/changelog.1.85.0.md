Fixed web tour tests to work with new versions of Chrome (>= 132),
where the `--headless=old` switch is no longer supported:
`ChromeBrowser._find_websocket` patched in `generic_mixin.tests.common`
to select the devtools `page` target explicitly, because the `/json`
endpoint may list non-page targets (browser UI, extension background
pages) before the actual page, which made every tour test fail.
