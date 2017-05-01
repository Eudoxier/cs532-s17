# Train Validate

The main program is `train-validate.py` which makes use of the files in `pci_code` and `lib` as libraries. The `pci_code` is not my work, it is the example code from _Programming Collective Intelligence_. The libraries in `lib` are from another personal project that happened to include dictionary manipulations that I needed. The `stats` directory holds ReSTructured text formatted tables of detailed confusion matrix statistics and `heatmap` holds heatmap graphs of the confusion matrices.

The files in `lib` are written in [hy](https://github.com/hylang/hy) or "hylang." Think `(+ python LISP)` but it maintains bidirectional compatibility with Python, any hy module can be imported in Python and any Python module can be imported to hy. In fact hy uses Pythons Abstract Syntax Trees to compile to actual python so technically it is Python, just with a different syntax.

> hy is to Python what Clojure is to Java.

This program licensing is different from the rest of the repository see below.

## Licence

### Code from the Programming Collective Intelligence book

The files `docclass.py` and `feedfilter.py` in the `pci_code` directory are example code from a book used in the course. It's copyright remains with the owner. Because it is not freely licensed no GNU GPLv3 code (the rest of this project) may link with it.

### Other files in this directory 

Licensed under the BSD licence:

>Copyright 2017 Derek Goddeau
>
>Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
>
>1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
>
>2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
>
>3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
>
>THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

### Files in `lib`

Are part of the utilities for my Home dotfile management, system configuration, and package manager project. They remain under their original GNU GPLv3+ licence.
