# ssb-parquedit-dashboard

An example Marimo dashboard for editing Parquedit tables

## Development

```sh
nix develop
uvx marimo edit --watch --sandbox dashboards/app.py
```

The `--watch` flag makes it possible to develop the app in any editor while still seeing the results in Marimo.

The app can also be checked with Marimo:

```sh
uvx marimo check dashboards/app.py
```

This checks that the app doesn't have any dependency cycles, among other things.
