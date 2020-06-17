# Wikipedia Cross Edit Pattern Exploration
This repository is created to host exploratory code for the Wikipedia Revision Dataset, as part of the Cross Edit Pattern Detection Project. <br />
This repository is forked from a Google corporate repository and will push changes regularly. <br />
Author: Haoran Fei (haoranfei@google.com) <br />
Host: Zainan Zhou (zzn@google.com) <br />
Date: June 8th, 2020 <br />

# Open-Source Dependencies and Licensing
Python3: GPL-Compatible License. GPL-compatible doesn’t mean that we’re distributing Python under the GPL. All Python licenses, unlike the GPL, let you distribute a modified version without making your changes open source. <br />
Pandas: New BSD License.
Matplotlib: License based on PSF license. 

# Usage Example
Loading the First json data file and run article-based analysis: <br />
$ python3 article_analytics.py --path ./data/cross_edits_tmp_ttl=72_revisioninfo_20200605_1023_segment-000##-of-00037.json --start 0 --stop 1 <br />
Loading all 37 json data files and run article-based analysis: <br />
$ python3 article_analytics.py --path ./data/1023/segment-000##-of-00037.json --start 0 --stop 37 <br />
Loading the First json data file and run author-based analysis: <br />
$ python3 author_analytics.py --path ./data/cross_edits_tmp_ttl=72_revisioninfo_20200605_1023_segment-000##-of-00037.json --start 0 --stop 1 <br />
Loading all 37 json data files and run author-based analysis: <br />
$ python3 author_analytics.py --path ./data/1023/segment-000##-of-00037.json --start 0 --stop 37 <br />

# Formula for Sliding Window Anomaly Detection
A window will be flagged as anomaly if it satisfies the following condition: <br />
<img src="https://render.githubusercontent.com/render/math?math=(M(W) - M(S)) * k / M(S) > t"> <br />
M: metric considerd. Currently supports mean and median. <br />
W: the window frame under consideration. <br />
S: the complete dataset of the given key. This can be all edits on the same article/by the same author, depending on the key used. <br />
k: value is either 1 or -1. It is 1 if we are concerned with abnormally high values only, and -1 if we are concerned with abnormally
low values only. <br />
t: a percentage threshold for flagging anomal. Currently set at 50%. <br/> 

# Log Files and Format
All log files are located in the cross-edits-analysis/log directory. Each directory holds the logs for the corresponding analysis script. <br />
Format of log line: Anomaly of (metric name) of (column name) detected for (key: this can be article/author or article/author pair) during period from 
(starting time of window) to (ending time of window), with a () percent difference from baseline. <br />






