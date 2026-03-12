# Install once

## Standard install

=== "uv"
`     $ uv add once
    `

=== "pip"
`     $ python -m pip install once
    `

## With Parquet support

=== "uv"
`     $ uv add once[parquet]
    `

=== "pip"
`     $ python -m pip install once[parquet]
    `

Parquet support requires `pyarrow` and enables the `.parquet` backend. See [Choose a Backend](choose-a-backend.md) for when this is useful.

## Install from GitHub

To install the latest development version directly from GitHub:

=== "uv"
`     $ uv add git+https://github.com/drvinceknight/once.git
    `

=== "pip"
`     $ python -m pip install git+https://github.com/drvinceknight/once.git
    `

To install a specific branch or tag:

=== "uv"
`     $ uv add git+https://github.com/drvinceknight/once.git@main
    `

=== "pip"
`     $ python -m pip install git+https://github.com/drvinceknight/once.git@main
    `

To install a specific released version:

=== "uv"
`     $ uv add git+https://github.com/drvinceknight/once.git@v0.1.0
    `

=== "pip"
`     $ python -m pip install git+https://github.com/drvinceknight/once.git@v0.0.1
    `
