<img src="media/47_ronin.png" title="I wanted to be Oshi, but they made me Ori" style="width:100%;">

# Simpsons Haiku Bot

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![PyPI license](https://img.shields.io/pypi/l/ansicolortags.svg)](https://github.com/mwestt/simpsons-haiku/blob/main/LICENSE)
[![Twitter](https://badgen.net/badge/icon/twitter?icon=twitter&label)](https://twitter.com/SimpsonsHaiku)

This repository hosts code for a Twitter bot ([@SimpsonsHaiku](https://twitter.com/SimpsonsHaiku)) that tweets haikus mined from episodes of The Simpsons. 

This project was inspired by [@nythaikus](https://twitter.com/nythaikus). The dataset used here is hosted [on Kaggle here](https://www.kaggle.com/datasets/prashant111/the-simpsons-dataset), and was originally scraped by [Todd Schneider](https://toddwschneider.com/posts/the-simpsons-by-the-data/) from the dearly departed simpsonsworld.com, covering the first 26 seasons. 

## Installation

To run the project and generate your own haikus, you'll need to clone the repository in the usual way, and install the relevant packages/activate the conda environment shared in `environment.yaml`.

```
git clone https://github.com/mwestt/simpsons-haiku.git
conda env create -f environment.yaml
conda activate simpsons_haiku
```

## Example Usage

We start by instantiating the core haiku object, of class `SimpsonsHaiku` from `haiku.py` and extracting a DataFrame of haikus. We can then call the `generate_haiku` method to sample a haiku along with associated metadata.

```python
from haiku import SimpsonsHaiku

simpsons_haiku = SimpsonsHaiku()
simpsons_haiku.generate_haiku_df()

haiku, metadata = simpsons_haiku.generate_haiku()
```
```python
>>> print(haiku)
```
```
It doesn't take a
whiz to see that you're looking
out for number one
```
