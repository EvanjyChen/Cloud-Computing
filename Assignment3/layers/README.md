# Matplotlib Lambda layer

`matplotlib-python311-x86_64.zip` is prebuilt so CloudShell can run `cdk
deploy` without Docker or an additional dependency-build step.

To rebuild the layer:

```bash
rm -rf build
mkdir -p build/python
python3 -m pip install \
  --platform manylinux2014_x86_64 \
  --implementation cp \
  --python-version 3.11 \
  --only-binary=:all: \
  --target build/python \
  -r requirements.txt
(cd build && zip -qr ../matplotlib-python311-x86_64.zip python)
```

The archive must have `python/` at its root and contain Linux x86-64 wheels
compatible with the plotting function's Python 3.11 runtime.
