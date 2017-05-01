# Assignment Nine
&nbsp;

*   [Assignment Ten Report PDF](http://datenstrom.gitlab.io/cs532-s17/pdfs/assignment_ten.pdf)

&nbsp;
## Question One

The data is stored in `data/assignment_eight_wordcount.dat` and the code in the `knnestimate` directory. I just walked through it in the interpreter but recorded what I did and the results in `knnestimate/README.md`.

## Question Two


-----------------------------------------------------------------------

&nbsp;
# Assignment #10

Due: 11:59pm May 1 2017

Support your answer: include all relevant discussion, assumptions, examples, etc.

## 1.  Using the data from A8:

* Consider each row in the blog-term matrix as a 1000 dimension vector, corresponding to a blog.
* From chapter 8, replace numpredict.euclidean() with cosine as the distance metric.  In other words, you'll be computing the cosine between vectors of 1000 dimensions.
* Use knnestimate() to compute the nearest neighbors for both:
    * http://f-measure.blogspot.com/
    * http://ws-dl.blogspot.com/

for k = {1,2,5,10,20}.

## 2.  Rerun A9, Q2 but this time using LIBSVM

Assignment Nine Question Two:

>Train the Fisher classifier on the first 50 entries (the "training set"),
>then use the classifier to guess the classification of the next 50 entries
>(the "test set").
>
>Create a table with 50 rows, like
>
>    title			actual		predicted
>    -----			------		---------
>    Donnie Iris - 		80s		80s
>    "Ah! Leah!" 
>    (Forgotten Song)	
>
>    Black Sabbath - 	metal		metal
>    "Vol. 4" (LP Review)
>
>    Catherine Wheel - 	alternative	metal
>    "Ferment" (LP Review)
>
>Assess the performance of your classifier in each of your categories
>by computing precision, recall, and F-measure.  Use the "macro-averaged"
>label based method, as per:
>[this post](http://stats.stackexchange.com/questions/21551/how-to-compute-precision-recall-for-multiclass-multilabel-classification)
>
>For example, if you have 5 categories (e.g., 80s, metal,
>alternative, electronic, cover), you will compute 
>precision, recall, and F-measure for each category,
>and then compute the average across the 5 categories.

If you have `n` categories, you'll have to run it `n` times.  For example, if you're classifying music and have the categories:

* metal
* electronic
* ambient
* folk
* hip-hop
* pop

You'll have to classify things as:

* metal / not-metal
* electronic / not-electronic
* ambient / not-ambient
* etc.

Use the 1000 term vectors describing each blog as the features, and your manually assigned classifications as the true values.  Use 10-fold cross-validation (as per slide 46, which shows 4-fold cross-validation) and report the percentage correct for each of your categories.


## 3. Re-download the 1000 TimeMaps from A2, Q2.  

> 3 Points extra credit

Create a graph where the x-axis represents the 1000 TimeMaps.  If a TimeMap has "shrunk", it will have a negative value below the x-axis corresponding to the size difference between the two TimeMaps.  If it has stayed the same, it will have a "0" value.  If it has grown, the value will be positive and correspond to the increase in size between the two TimeMaps.

As always, upload all the TimeMap data.  If the A2 github has the original TimeMaps, then you can just point to where they are in the report.


## 4.  Repeat A3, Q1.  

> 3 Points extra credit

Compare the resulting text from February to the text you have now.  Do all 1000 URIs still return a "200 OK" as their final response (i.e., at the end of possible redirects)?

Create two graphs similar to that described in Q3, except this time the y-axis corresponds to difference in bytes (and not difference in TimeMap magnitudes).  For the first graph, use the difference in the raw (unprocessed) results.  For the second graph, use the difference in the processed (as per A3, Q1) results.

Of the URIs that still terminate in a "200 OK" response, pick the top 3 most changed (processed) pairs of pages and use the Unix "diff" command to explore the differences in the version pairs.
