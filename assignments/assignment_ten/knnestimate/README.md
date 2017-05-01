# kNN

## Results using the PCI code

&nbsp;

    >>> import clusters
    >>> import numpredict
    >>> from tabulate import tabulate
    >>> from collections import OrderedDict
    >>> blognames, words, data = clusters.readfile('../../data/assignment_eight_wordcount.dat')
    >>> f_measure_table = OrderedDict()
    >>> for k in [1, 2, 5, 10, 20]:
    ...     numpredict.knnestimate(data, data[blognames.index('F-Measure')], k=k)
    ...
    >>> tabulate(f_measure_table, headers='keys', tablefmt='rst')
    =============  ===============  ====================  ====================  =============================================
    k = 1          k = 2            k = 5                 k = 10                k = 20
    =============  ===============  ====================  ====================  =============================================
    Laganas rock!  Laganas rock!    Laganas rock!         Laganas rock!         Laganas rock!
                   Banging Windows  Banging Windows       Banging Windows       Banging Windows
                                    The Travels of Dave   The Travels of Dave   The Travels of Dave
                                    Design Your World     Design Your World     Design Your World
                                    Myths.. MyThoughts..  Myths.. MyThoughts..  Myths.. MyThoughts..
                                                          The Wizard and I.     The Wizard and I.
                                                          Girl Informer         Girl Informer
                                                          SOPHIE PATTERSON      SOPHIE PATTERSON
                                                          RED PAPER ONLINE      RED PAPER ONLINE
                                                          Kaleidoscope          Kaleidoscope
                                                                                Star's Adventures at Camp Half Blood
                                                                                Dream, sports, and Travel Blogs
                                                                                What's in my head...
                                                                                The Fat Lady
                                                                                The Original Runaway Heart
                                                                                Brent and Paulette's Excellent RV Adventure's
                                                                                Serendipity
                                                                                The Pink Lady of Hollywood
                                                                                poetic illusions
                                                                                All Feet are the Same!
    =============  ===============  ====================  ====================  =============================================
    >>> web_science_table = {}
    >>> for k in [1, 2, 5, 10, 20]:
    ...     numpredict.knnestimate(data, data[blognames.index('Web Science and Digital Libraries Research Group')], k=k)
    ...
    >>> tabulate(f_measure_table, headers='keys', tablefmt='rst')
    =============  =================  =================  ====================  ==============================
    k = 1          k = 2              k = 5              k = 10                k = 20
    =============  =================  =================  ====================  ==============================
    Girl Informer  Girl Informer      Girl Informer      Girl Informer         Girl Informer
                   Design Your World  Design Your World  Design Your World     Design Your World
                                      The Wizard and I.  The Wizard and I.     The Wizard and I.
                                      mayur              mayur                 mayur
                                      RED PAPER ONLINE   RED PAPER ONLINE      RED PAPER ONLINE
                                                         Kaleidoscope          Kaleidoscope
                                                         Random Thoughts       Random Thoughts
                                                         Myths.. MyThoughts..  Myths.. MyThoughts..
                                                         SOPHIE PATTERSON      SOPHIE PATTERSON
                                                         The Fat Lady          The Fat Lady
                                                                               poetic illusions
                                                                               The Travels of Dave
                                                                               Rhiannon's A2 Media Coursework
                                                                               Banging Windows
                                                                               NOSTALGIA
                                                                               What's in my head...
                                                                               the silhouette of a dream.
                                                                               Babe in Old Town
                                                                               Damon @ Awahono School
                                                                               The Original Runaway Heart
    =============  =================  =================  ====================  ==============================

&nbsp;

## PCI Code Modifications

&nbsp;
`clusters.py`:

```python
def readfile(filename):
    lines = [line for line in open(filename, 'r')]

    .
    .
    .

```

&nbsp;
`numpredict.py`

```python
from scipy import spatial
def cosine(v1, v2):
    return spatial.distance.cosine(v1, v2)


def getdistances(data,vec1):
    distancelist = []

    # Loop over every item in the dataset
    for i in range(len(data)):
        vec2 = data[i]

        # Add the distance and the index
        distancelist.append((cosine(vec1, vec2), i))

    # Sort by distance
    distancelist.sort()
    return distancelist


def knnestimate(data, vec1, k=5):
    # Get sorted distances
    dlist = getdistances(data, vec1)

    # Take the average of the top k results
    for i in range(k):
        nns_idx += dlist[i][1]
    return nns_idx
```
