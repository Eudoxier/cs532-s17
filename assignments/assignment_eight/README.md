# Assignment Eight
&nbsp;

*   [Assignment Eight Report PDF](http://datenstrom.gitlab.io/cs532-s17/pdfs/assignment_eight.pdf)

&nbsp;
## Create a blog-term matrix

See the glutton program, the data is saved in the `data` folder both pickled and in ASCII.

## 2.  Create an ASCII and JPEG dendrogram that clusters (i.e., HAC)

The dendrograms are located in the `art` folder.

## 3.  Cluster the blogs using K-Means, using k=5,10,20.

*  **K = 5:** 5 Iterations
*  **K = 10:** 7 Iterations
*  **K = 20:** 3 Iterations

## 4.  Use MDS to create a JPEG of the blogs

This JPEG of the blogs is also located in the `art` folder. It took 3 iterations.

-----------------------------------------------------------------------

&nbsp;
# Assignment #8
Due: 11:59pm April 13 2017

> (10 points; 2 points for each question and 2 points for aesthetics)

Support your answer: include all relevant discussion, assumptions,
examples, etc.

## 1.  Create a blog-term matrix.

Start by grabbing 100 blogs; include:

* [http://f-measure.blogspot.com/](http://f-measure.blogspot.com/)
* [http://ws-dl.blogspot.com/](http://ws-dl.blogspot.com/)

and grab 98 more as per the method shown in class.  Note that this
method randomly chooses blogs and each student will separately do
this process, so it is unlikely that these 98 blogs will be shared
among students.  In other words, no sharing of blog data.  Upload
to github your code for grabbing the blogs and provide a list of
blog URIs, both in the report and in github.

Use the blog title as the identifier for each blog (and row of the
matrix).  Use the terms from every item/title (RSS) or entry/title
(Atom) for the columns of the matrix.  The values are the frequency
of occurrence.  Essentially you are replicating the format of the
"blogdata.txt" file included with the PCI book code.  Limit the
number of terms to the most "popular" (i.e., frequent) 1000 terms,
this is *after* the criteria on p. 32 (slide 7) has been satisfied.
Remember that blogs are paginated.

## 2.  Create an ASCII and JPEG dendrogram that clusters (i.e., HAC)

The most similar blogs (see slides 12 & 13).  Include the JPEG in
your report and upload the ascii file to github (it will be too
unwieldy for inclusion in the report).

## 3.  Cluster the blogs using K-Means, using k=5,10,20.

See slide 18

Print the values in each centroid, for each value of k.  How
many iterations were required for each value of k?

## 4.  Use MDS to create a JPEG of the blogs similar to slide 29 of the
week 12 lecture.  How many iterations were required?

## 5.  Re-run question 2, but this time with proper TFIDF calculations

> 3 points extra credit

Instead of the hack discussed on slide 7 (p. 32).  Use the same 1000
words, but this time replace their frequency count with TFIDF scores
as computed in assignment #3.  Document the code, techniques,
methods, etc. used to generate these TFIDF values.  Upload the new
data file to github.

Compare and contrast the resulting dendrogram with the dendrogram
from question #2.

Note: ideally you would not reuse the same 1000 terms and instead
come up with TFIDF scores for all the terms and then choose the top
1000 from that list, but I'm trying to limit the amount of work
necessary.

## 6.  Re-run questions 1-4 with different blogs, 

> 5 points extra credit

This time instead of using the 98
"random" blogs, use 98 blogs that should be "similar" to:

* [http://f-measure.blogspot.com/ ](http://f-measure.blogspot.com/)
* [http://ws-dl.blogspot.com/ ](http://ws-dl.blogspot.com/)

Choose approximately equal numbers for both blog sets (it doesn't
have to be a perfect 49-49 split, but it should be close).
Explain in detail your strategy for locating these blogs.

Compare and contrast the results from the 98 "random" blogs and
the 98 "targeted" blogs.
