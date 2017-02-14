# Assignment Two

&nbsp;

[Assignment two report PDF](#)

&nbsp;

-------------------------------

## Benxihu

A program to extract unique links from twitter filtered by keyword.
Verifies that both the final redirect are unique and valid.

### Usage

    usage: cli.py [-h] [-f INFILE] [-c COUNT] [-q] [-k KEYS]
                  keywords [keywords ...]

    Filter streaming tweets by keywords.

    positional arguments:
      keywords              Words to filter tweets with.

    optional arguments:
      -h, --help            show this help message and exit
      -f INFILE, --infile INFILE
                            Input file instead of stream.
      -c COUNT, --count COUNT
                            Number of tweets to get with the filters applied.
      -q, --quiet           Suppress output.
      -k KEYS, --keys KEYS  File containing OAuth twitter credentials.

### Output

Tweets containing links will be written one per line to the file
`data/{basename}_data_{unix_time}.json` where `{basename}` is the
first keyword passed and `{unix_time}` is the current number of
whole seconds since the Unix epoch. Similarly each corresponding
link will be written to the corresponding line number in the file
`data/{basename}_links_{unix_time}.dat`.
Detailed debugging information is also logged to `main.log`.

## Download and display the TimeMaps for each of the 1000 target URIs

To install the jupyter notebook requirements:

    cat notebook-requirements.txt | xargs -n 1 -L 1 pip install
    sudo apt-get update
    sudo apt-get install libzmq3-dev r-base r-base-dev libatlas3-base \
        libopenblas-base libssh2-1-dev libcurl4-openssl-dev libxml2-dev \
        libxslt-dev libssl-dev
    sudo R

Now using the R terminal:

    > install.packages(c('crayon', 'pbdZMQ', 'devtools'))
    > devtools::install_github(paste0('IRkernel/', c('httr', 'repr', 'IRdisplay', 'IRkernel')))
    > q()

Other R packages:

    *   plotly
    *   ggplot2
    *   scales
    *   grid
    *   RColorBrewer
    *   anytime
    *   webshot

### If install errors

Currently there is a version dependant bug affecting the install
of the kernel, if errors try adding:

    sudo echo "deb http://cran.rstudio.com/bin/linux/debian jessie-cran3/" >> /etc/apt/sources.list
    sudo apt-key adv --keyserver keys.gnupg.net --recv-key 6212B7B7931C4BB16280BA1306F90DE5381BA480
    sudo apt-get update && sudo apt-get install r-base/jessie-cran3 r-base-dev/jessie-cran3

Pin the repsoitory by creating the file `/etc/apt/preferences.d/prefer-r-cran.pref`
with:

    Package: *
    Pin: release a=jessie-cran3
    Pin-Priority: 900

See [the CRAN documentation](https://cran.r-project.org/bin/linux/debian/)
about installing on Debian for more detailed information.

    > options(repos='http://cran.rstudio.com/')
    > install.packages("devtools")
    > install.packages(c('repr', 'pbdZMQ', 'devtools'))
    > options(download.file.method = "wget")
    > install.packages('RCurl')
    > devtools::install_github(c('IRkernel/IRdisplay', 'IRkernel/IRkernel'))
    > IRkernel::installspec()
    > q()

To use R magic also install:

    > install.packages('httr', 'RJSONIO')

### Make the kernel available in Jupyter

Only for the user:

    > IRkernel::installspec()

System wide:

    > IRkernel::installspec(user = FALSE)

Jupyter notebook can now be started with `jupyter notebook` and
the R kernel will be available for use.

## Estimate the age of the URIs with "Carbon Date"

Carbon Date is dockerized by gitlab continuous integration using the
`.gitlab-ci.yml` file in the project root directory and pushed to 
this repositories registery. The script in the `carbondate`
directory demonstrates its use.

## Assignment Description

CS 432/532 Web Science
Spring 2017
http://phonedude.github.io/cs532-s17/

Assignment #2
Due: 11:59pm February 9

1.  Write a Python program that extracts 1000 unique links from
Twitter.  You might want to take a look at:

http://adilmoujahid.com/posts/2014/07/twitter-analytics/

see also:

http://docs.tweepy.org/en/v3.5.0/index.html
https://github.com/bear/python-twitter
https://dev.twitter.com/rest/public

But there are many other similar resources available on the web.
Note that only Twitter API 1.1 is currently available; version 1
code will no longer work.

Also note that you need to verify that the final target URI (i.e.,
the one that responds with a 200) is unique.  You could have many
different shortened URIs for www.cnn.com (t.co, bit.ly, goo.gl,
etc.).  For example:

$ curl -IL --silent https://t.co/DpO767Md1v | egrep -i "(HTTP/1.1|^location:)"
HTTP/1.1 301 Moved Permanently
location: https://goo.gl/40yQo2
HTTP/1.1 301 Moved Permanently
Location: https://soundcloud.com/roanoketimes/ep-95-talking-hokies-recruiting-one-week-before-signing-day
HTTP/1.1 200 OK

You might want to use the search feature to find URIs, or you can
pull them from the feed of someone famous (e.g., Tim O'Reilly).  If
you find something inappropriate for any reason you see fit, just
discard it and get some more links.  We just want 1000 links that
were shared via Twitter.

Hold on to this collection and upload it to github -- we'll use it
later throughout the semester.

2.  Download the TimeMaps for each of the target URIs.  We'll use the ODU 
Memento Aggregator, so for example:

URI-R = http://www.cs.odu.edu/

URI-T = http://memgator.cs.odu.edu/timemap/link/http://www.cs.odu.edu/

or:

URI-T = http://memgator.cs.odu.edu/timemap/json/http://www.cs.odu.edu/

(depending on which format you'd prefer to parse)

Create a histogram* of URIs vs. number of Mementos (as computed
from the TimeMaps).  For example, 100 URIs with 0 Mementos, 300
URIs with 1 Memento, 400 URIs with 2 Mementos, etc.  The x-axis
will have the number of mementos, and the y-axis will have the
frequency of occurence.

* = https://en.wikipedia.org/wiki/Histogram

What's a TimeMap?  
See: http://www.mementoweb.org/guide/quick-intro/
And the week 4 lecture.  

3.  Estimate the age of each of the 1000 URIs using the "Carbon
Date" tool:

http://ws-dl.blogspot.com/2016/09/2016-09-20-carbon-dating-web-version-30.html

Note: you should use "docker" and install it locally.  You can do
it like this:

http://cd.cs.odu.edu/cd?url=http://www.cs.odu.edu/

But it will inevitably crash when everyone tries to use it at the
last minute.

For URIs that have > 0 Mementos and an estimated creation date,
create a graph with age (in days) on the x-axis and number of
mementos on the y-axis.

Not all URIs will have Mementos, and not all URIs will have an
estimated creation date.  Show how many fall into either categories.
For example,

total URIs:         1000
no mementos:         137  
no date estimate:    212
