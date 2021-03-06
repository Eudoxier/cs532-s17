# Assignment One

&nbsp;

[Assignment one report PDF](http://datenstrom.gitlab.io/cs532-s17/pdfs/assignment_one.pdf)

&nbsp;

[Assignment one graph analysis Jupyter notebook](http://datenstrom.gitlab.io/cs532-s17/notebooks/graph_structure.html)

&nbsp;

-------------------------------

## Common House Spider

For when google hacking is not enough.

*   Python 2 and 3 compatible, run either of the following to install version dependencies.

    * `sudo pip install -r requirements.txt`
    * `sudo pip3 install -r requirements.txt`

*   To see usage information run `common_house_spider/cli.py -h`.
*   To run tests: `python setup.py test`

## Curl

The `curl_post.sh` script searches [nostarch.com](nostarch.com) for the
given command line argument.

## Graph Structure

Installation and config problems:

*   Debian systems need: `apt-get install libfreetype6-dev`
*   Must run `python3 -m ipykernel install` to make Python 3 kernel available
*   Note that for some reason the graphviz package was not in python `PATH` without installing via `apt-get install graphviz` in my environment for some reason.
*   Numpy must be installed before Matplotlib, there is no real solution to this but this works.

    cat notebook-requirements.txt | xargs -n 1 -L 1 pip install


## Assignment Description

CS 432/532 Web Science
Spring 2017
http://phonedude.github.io/cs532-s17/

Due: 11:59pm Sept 26

1.  Demonstrate that you know how to use "curl" well enough to
correctly POST data to a form.  Show that the HTML response that
is returned is "correct".  That is, the server should take the
arguments you POSTed and build a response accordingly.  Save the
HTML response to a file and then view that file in a browser and
take a screen shot.

2.  Write a Python program that:

  1. takes as a command line argument a web page
  2. extracts all the links from the page
  3. lists all the links that result in PDF files, and prints out the bytes for each of the links.  (note: be sure to follow all the redirects until the link terminates with a "200 OK".)
  4. show that the program works on 3 different URIs, one of which needs to be: [http://www.cs.odu.edu/~mln/teaching/cs532-s17/test/pdfs.html](http://www.cs.odu.edu/~mln/teaching/cs532-s17/test/pdfs.html)

3.  Consider the "bow-tie" graph in the Broder et al. paper (fig 9): [http://www9.org/w9cdrom/160/160.html](http://www9.org/w9cdrom/160/160.html)

Now consider the following graph:

    A --> B
    B --> C
    C --> D
    C --> A
    C --> G
    E --> F
    G --> C
    G --> H
    I --> H
    I --> K
    L --> D
    M --> A
    M --> N
    N --> D
    O --> A
    P --> G 
    
For the above graph, give the values for:

    IN: 
    SCC: 
    OUT: 
    Tendrils: 
    Tubes: 
    Disconnected:
