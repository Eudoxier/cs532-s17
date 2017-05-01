# Train Validate

The main program is `train-validate.py` is now upgraded removing the `pci_code` but still making use of the hylang libraries in the `lib` directory. The `pci_code` is replaced with the [scikit-learn](http://scikit-learn.org/stable/documentation.html) package [SVM library](http://scikit-learn.org/stable/modules/svm.html). The libraries in `lib` are from another personal project that happened to include dictionary manipulations that I needed. The `stats` directory holds ReSTructured text formatted tables of detailed confusion matrix statistics and `heatmap` holds heatmap graphs of the confusion matrices.

The files in `lib` are written in [hy](https://github.com/hylang/hy) or "hylang." Think `(+ python LISP)` but it maintains bidirectional compatibility with Python, any hy module can be imported in Python and any Python module can be imported to hy. In fact hy uses Pythons Abstract Syntax Trees to compile to actual python so technically it is Python, just with a different syntax.

> hy is to Python what Clojure is to Java.

## scikit-learn svm

The classifiers offered are [SVC](http://scikit-learn.org/stable/modules/generated/sklearn.svm.SVC.html#sklearn.svm.SVC), [NuSVC](http://scikit-learn.org/stable/modules/generated/sklearn.svm.NuSVC.html#sklearn.svm.NuSVC), and [LinearSVC](http://scikit-learn.org/stable/modules/generated/sklearn.svm.LinearSVC.html#sklearn.svm.LinearSVC). They all support multi-class classification; however, SVC and NuSVC use a "one-against-one" approach and LinearSVC uses a one against the rest approach. LinearSVC will not be used since this is against the method described in the course assignment. Both SVC and NuSVC are based on `libsvm` the only difference noted in the documentation is:

> Similar to SVC but uses a parameter to control the number of support vectors.

## SVC and Data Preprocessing

I am not sure how to find the appropriate value for `nu` that NuSVC requires so I am using SVC. It's `preprocessing` library provides a `scale()` function for easy data normalization and also the `LableEncoder` class which can be used to prepare non-numerical labels. From the docs:

    >>> le = preprocessing.LabelEncoder()
    >>> le.fit(["paris", "paris", "tokyo", "amsterdam"])
    LabelEncoder()
    >>> list(le.classes_)
    ['amsterdam', 'paris', 'tokyo']
    >>> le.transform(["tokyo", "tokyo", "paris"])
    array([2, 2, 1]...)
    >>> list(le.inverse_transform([2, 2, 1]))
    ['tokyo', 'tokyo', 'paris']
