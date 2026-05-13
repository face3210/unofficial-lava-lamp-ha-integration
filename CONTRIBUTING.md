# Contribution Guidelines

Contributing to this project should be as easy and transparent as possible,
whether you are:

- Reporting a bug.
- Discussing the current state of the code.
- Submitting a fix.
- Proposing a feature.

## GitHub Is Used For Everything

GitHub is used to host code, track issues and feature requests, and accept pull
requests.

Pull requests are the best way to propose changes to the codebase.

1. Fork the repository and create your branch from `main`.
2. If you changed behavior, update the documentation.
3. Run `scripts/lint`.
4. Run `scripts/test`.
5. Open a pull request.

## Development Environment

This custom integration includes a development container based on the
`integration_blueprint` setup. The container installs Python 3.12, `uv`, Home
Assistant, and editor tooling for Ruff and Python.

Run the setup command after opening the container:

```bash
scripts/setup
```

Start a standalone Home Assistant instance for local testing:

```bash
scripts/develop
```

The development server uses `config/configuration.yaml` and loads the
`lava_lamp` integration by linking `custom_components/lava_lamp` into
`config/custom_components/lava_lamp`.

If Home Assistant keeps loading old integrations from an earlier local run, reset
the generated config files:

```bash
scripts/reset-config
scripts/develop
```

## Coding Style

Ruff is used for formatting and linting.

```bash
scripts/lint
```

To check formatting without changing files:

```bash
uv run ruff format . --check
```

## Tests

Run tests with:

```bash
scripts/test
```

or directly with:

```bash
uv run pytest
```

## Report Bugs Using GitHub Issues

Report a bug by opening a new issue at
https://github.com/face3210/unofficial-lava-lamp-ha-integration/issues/new/choose.

Great bug reports include:

- A quick summary and background.
- Home Assistant System Health details.
- Steps to reproduce.
- What you expected would happen.
- What actually happened.
- Debug logs from startup through the failure.

## License

By contributing, you agree that your contributions will be licensed under the
MIT License.
