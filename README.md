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
