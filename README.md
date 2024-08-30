# methods-graph

A python package for creating and analyzing graphs of methods in scientific papers.

## Creating an MVP
- [x] Get the graph of an example paper using connectedpapers API
- [x] Download the PDFs of the papers connected to it by reading the graph
- [ ] Anlyse the PDFs with Gemini to extract the methods
- [ ] Create a graph of the methods in the papers

## Create a conda environment and install the package
```bash
conda create -n methods-graph python=3.7
conda activate methods-graph
pip install -e .
```

## Download example graph and related PDFs
```bash
python scripts/download_example_data.py
```