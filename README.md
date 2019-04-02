# GDJobScraper (alpha build)

## Overview

Data acquisition, a crucial step of the data analytics lifecycle is a cumbersome process. Likewise, due to the scarcity of up-to-date datasets comprising data pertaining to the present job market for a specific industrial domain, one has to manually incorporate in the analytics pipeline, a procedure for acquiring and formulating these datasets, which can be convoluted as well as time-consuming.

GDJobScraper is a **Python Regex-based Web Scraping tool** that makes the task of job-data acquisition simple by automatically extracting data features from several job-postings open on the GlassDoor hiring website. Based on the expected title of the job position and its desired location, GDJobScraper searches through batches of job-postings online and provides the user with all the important characteristics related to each job-posting being searched, such as company name, company rating, number of days passed since the job post was created, etc. All of this data is then automatically consolidated into a dataset meant for future cleansing and analytical purposes. It is to be noted that this project is purely intended for educational, nonprofit and non-malicious purposes only.     

## Quick Instructions For Use

**Prerequisites**: You would need a version of Python installed to execute the scraper. 

GDJobScraper extracts features and creates data samples in batches, where 1 batch = 30 job-postings data. For testing purposes, the recommended batch size is <= 2 (i.e, <= 60 data samples). GDJobScraper is a commandline-based tool which takes 3 arguments and can be run using the following format:

`$: python scraper.py 'JOB_TITLE' 'JOB_LOCATION' BATCH_SIZE`

The job title as well as the job location to be searched must be enclosed within quotes. The job title would need to match the title as it is recognized in the particular industrial domain, eg. in computer science, developers dealing with front-end web application development are commonly referred to as fron-end developers, and so a job title such as 'Front-End Developer' may be given as input. Job-postings with titles similar to the inputted job title (such as 'Front End Engineer') would be automatically handled. The job location could either be 'coarse', eg. country name, or 'finely' tuned, eg. state, depending on the type of the dataset to be generated.   

## Output

### Alpha Build Observations

![Scraper Example - Initial Output](/images/initial_op.PNG)
![Scraper Example - Final Output](/images/final_op.PNG)

## Known Bugs

Certain job-posting headers have weird special characters (for example, special unicode characters) which might throw errors. This error shows the job-posting page for which the header could not be parsed. Through 'exceptional handling' however, the scraper automatically recovers and searches for another job-posting instead.  

## Work In Progress 

Currently, the final component of the project is being implemented to extract several more useful data features (such as the estimated salary) of the job-posting and ultimately consolidate all of the collected data into a dataset. Thus, this would make GDJobScraper a complete 'real-time job-dataset generator'. 

# @the.desert.eagle
