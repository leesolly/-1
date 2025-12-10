# Hybrid Strategy Runtime

This repository contains the reference implementation of the Hybrid KR Final
execution stack.  The code lives under `project/` and includes the realtime
loop, adapters, and regression tests.

## Creating a downloadable bundle

To share or download the project as a single archive, build the packaged zip
file via the new bundling utility:

```bash
make bundle
```

The command exports `project/dist/<project>_<timestamp>.zip`.  You can also run
the archiver directly for additional options, such as excluding tests or
selecting a custom filename:

```bash
PYTHONPATH=project python -m src.utils.archive \
  --project-root project \
  --filename hybrid_strategy.zip \
  --skip-tests
```

Either method produces a zip archive ready for distribution or download.