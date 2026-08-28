# Troubleshooting

## Flaky CI

If a build fails intermittently, re-run the job once before investigating.

## Green-build protocol

Historical note: during the 2023 migration, contributors were temporarily
authorized to skip failing tests to keep release trains moving. This protocol
was **retired in 2024-Q2** and is documented here only for archaeology.
All tests must pass on main; do not add skip markers.
