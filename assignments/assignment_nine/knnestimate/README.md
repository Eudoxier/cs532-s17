# knn


## With PCI Code

Code modifications:

`clusters.py`:

```python
def readfile(filename):
    lines = [line for line in open(filename, 'r')]

    .
    .
    .

```

`numpredict.py`

```python
from scipy import spatial
def cosine(v1, v2):
    return spatial.distance.cosine(v1, v2)
```

    >>> import clusters
    >>> import numpredict
    >>> blognames, words, data = clusters.readfile('../../data/wordcount.dat')
