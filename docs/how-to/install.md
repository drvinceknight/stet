# Install stet

## Standard install

=== "uv"

    ```
    $ uv add stet
    ```

=== "pip"

    ```
    $ python -m pip install stet
    ```

## With Parquet support

=== "uv"

    ```
    $ uv add stet[parquet]
    ```

=== "pip"

    ```
    $ python -m pip install stet[parquet]
    ```

Parquet support requires `pyarrow` and enables the `.parquet` backend. See
[Choose a Backend](choose-a-backend.md) for when this is useful.

## Install from GitHub

To install the latest development version directly from GitHub:

=== "uv"

    ```
    $ uv add git+https://github.com/drvinceknight/stet.git
    ```

=== "pip"

    ```
    $ python -m pip install git+https://github.com/drvinceknight/stet.git
    ```

To install a specific branch or tag:

=== "uv"

    ```
    $ uv add git+https://github.com/drvinceknight/stet.git@main
    ```

=== "pip"

    ```
    $ python -m pip install git+https://github.com/drvinceknight/stet.git@main
    ```

To install a specific released version:

=== "uv"

    ```
    $ uv add git+https://github.com/drvinceknight/stet.git@v0.1.0
    ```

=== "pip"

    ```
    $ python -m pip install git+https://github.com/drvinceknight/stet.git@v0.1.0
    ```
