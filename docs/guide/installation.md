# Installation

## Prerequisites

- Python >= 3.12
- conda (recommended) or pip

## Using pip

The package installs directly from the GitHub repository:

```sh
pip install git+https://github.com/esther-poniatowski/stelion.git
```

## Using conda

The package is available on the `eresthanaconda` channel:

```sh
conda install -c eresthanaconda stelion
```

## From Source

1. Clone the repository:

   ```sh
   git clone https://github.com/esther-poniatowski/stelion.git
   ```

2. Create a dedicated environment and install:

   ```sh
   cd stelion
   conda env create -f environment.yml
   conda activate stelion
   pip install -e .
   ```
