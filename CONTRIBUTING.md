# Contributing

Contributions to DocForge are welcome.

## Development setup

1. Install Python 3.12 or newer.
2. Install Poetry.
3. Create a virtual environment and install dependencies:
   ```bash
   poetry install
   ```
4. Copy the example environment file if needed:
   ```bash
   copy .env.example .env
   ```

## Testing

Run the test suite before submitting changes:

```bash
poetry run pytest
```

Run lint checks as well:

```bash
poetry run ruff check .
```

## Contribution guidelines

- Keep changes focused and easy to review.
- Update documentation when behavior or setup changes.
- Add or update tests for user-visible behavior changes.
- Follow the existing architecture and keep application code changes separate from documentation and metadata updates.

## Pull requests

Please describe the problem being solved, the approach taken, and any relevant testing performed in the pull request description.
