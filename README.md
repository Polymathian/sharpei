# Sharpei

Python watchdog to sync file changes to AWS S3

Requires Python 3.6+

## Usage

Install from [PyPI](https://pypi.org/project/sharpei/)

```bash
pip install sharpei
```

#### CLI

```bash
# Monitor the current directory and send all files
> sharpei . s3://bucket/key-prefix/
```

Use `sharpei --help` to discover additional options

#### DockerHub

You will need to mount a directory to the Docker image.

```bash
> docker run --mount type=bind,source=YOUR_DIRECTORY,target=/data sharpei s3://bucket/key-prefix
```

For example, given a folder structure:

```
working-dir
│   README.md
|
└───target-folder
        file011.txt
        file012.txt
```

To monitor file changes in `target-folder`, run:

```bash
> docker run --mount type=bind,source="$(pwd)"/target-folder,target=/data sharpei s3://my-bucket/my-prefix
```
