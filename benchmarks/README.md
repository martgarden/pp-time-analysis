## Reproducing benchmarks

The CONCUR'18 benchmarks can be reproduced by running:

```
python3 main.py concur18.json | tee output.json
```

The results can be converted into a LaTeX table by running:

```
python3 format.py output.json
```

The raw data of the benchmarks generated from concur18.json and appearing in the paper are available in concur18_output.json.

## New benchmarks

New benchmarks can be obtained by writing a new JSON configuration
file; concur18.json can serve as a basis to write such a new file.
