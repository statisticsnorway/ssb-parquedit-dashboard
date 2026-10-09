# ssb-parquedit-dashboard

Marimo Studio application for simple row editing of [Parquedit](https://github.com/statisticsnorway/ssb-parquedit) tables.

## Development

1. [Install `uv`](https://docs.astral.sh/uv/getting-started/installation/) or run `nix develop` (if you have `nix` installed).

2. Run:

    ```sh
    uvx marimo edit --watch --sandbox dashboards/app.py
    ```

The `--watch` flag makes it possible to develop the app in any editor while still seeing the results in Marimo.
If you only want to develop in your own editor, it's useful to replace `edit` with `run`, which will only show the application in the browser (not the Marimo editor).

The app can also be checked with Marimo:

```sh
uvx marimo check dashboards/app.py
```

This checks that the app doesn't have any dependency cycles, among other things.

The first time you run the app locally, it will create a local `Parquedit` database with mock data.
The `con` variable will be a connection to this database, while in Dapla production the `con` variable will be a connection to the production `Parquedit` database.
This is done as follows:

```py
is_dapla_prod = os.environ.get("DAPLA_ENVIRONMENT", "").lower() == "prod"
con = ParquEdit() if is_dapla_prod else LocalParquEdit().with_mock_tables()
```

## Disclaimer

A significant part of the app has been developed with the help of AI, especially the presentational layer/view of the notebook (see [dashboards/views/parqueditor/index.html](dashboards/views/parqueditor/index.html)). 
