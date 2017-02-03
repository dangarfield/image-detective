## Overview

App.py is the entry point. If takes a number of arguments (look at the help function):
`cd image-detective`
`python DET\app.py -h`

Make sure that you always execute the calls in the root directory.

Example usage:
* Generate test images: `python DET\app.py generate`
* Index all images: `python DET\app.py index`
* Index selected images: `python DET\app.py index -i 2*.jpg`
* Query all images with all algorithms using full and feature hashes `python DET\app.py query` > CSV output in root directory
* Query selected images with all algorithms using feature hashes only `python DET\app.py query -i 3*.jpg -ft` > CSV output in root directory
* Query all images with the phash algorithm only using full hashes only `python DET\app.py query -a phash -fl` > CSV output in root directory

## Installation (Windows only, linux/mac is much easier)

We need python with the following libraries:
* numpy - Scientific computer python library
* scipy - Scientific computer python library
* pillow - Python imaging library (to create test images)
* imagehash - Python image hashing library
* cv2 - OpenCV python wrapper
* six - Some python utility functions
* elasticsearch - Elasticsearch wrapper
* certifi - Remove SSL exceptions
* requests - http requests
* boto3 - AWS cli


Installing scipy and numpy on windows is a pain. I would strongly suggest installing Anaconda directly instead of python (Anaconda is a bundled version of python that also contains key computer science libraries like numpy and scipy) - `https://www.continuum.io/downloads`
* Download Anaconda with base of Python 2.7 (although 3.x will probably work, the examples of hashing tend to use 2.7)
* Unzip to a local directory. I use `C:\path_installations\Anaconda2`
* Add above directory to PATH environment variable
* After all is done, open a cmd and install the above libraries `pip install six` (You should only need to do pillow, imagehash, six & elasticsearch)

Install elasticsearch - A lucene based search engine similar to solr
* Download from `https://www.elastic.co/downloads/elasticsearch`
* Follow installation steps (use defaults, add windows service by executing `elasticsearch-service install` from bin directory)

Install OpenCV - The most popular computer vision library
* Download 2.4.13 from `http://opencv.org/downloads.html`
* Unzip to a local directory. I use `C:\path_installations\opencv-2.4.13`
* Copy and paste the file `C:\path_installations\opencv-2.4.13\build\python\2.7\x64\cv2.pyd` to your python site-packages directory `C:\path_installations\Anaconda2\Lib\site-packages`


## AWS 

pip install awscli

Run: aws configure

Access: (ask for this)
Secret: (ask for this)
Region: eu-central-1

You can now download the source images.

For creating a lambda function, copy the contents from the lib folder into the root and zip the whole lot (remove some of the unneeded folders, reports, images etc).
This should run on a lambda function as the python libraries have been pre-compiled and packaged.

## IDE

For simple projects like this I tend to you Visual Studio Code as it is basically Sublime Text + git + console + auto-linting + good and quick to install plugins
Any decent IDE will work.

## Reports

Many as above, although I also tweaked it slightly and there are some older reports in the `old_style_reports` directory

## Limitations

There are many, this is just a starting point...
