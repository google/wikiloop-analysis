# Google_Cross_Edit_Pattern_Exploration
This repository is created to host exploratory code for the Wikipedia Revision Dataset, as part of the Cross Edit Pattern Detection Project. <br />
This repository will be migrated to a Google corporate repository on June 10th, 2020. <br />
Author: Haoran Fei (haoranfei@google.com) <br />
Date: June 8th, 2020 <br />

# Open-Source Dependencies and Licensing
Python3: GPL-Compatible License. GPL-compatible doesn’t mean that we’re distributing Python under the GPL. All Python licenses, unlike the GPL, let you distribute a modified version without making your changes open source. <br />
Pandas: New BSD License.
Matplotlib: License based on PSF license. 

# Usage-Example
Loading the First json data file and run article-based analysis: <br />
$ python3 article_analytics.py --path ./data/cross_edits_tmp_ttl=72_revisioninfo_20200605_1023_segment-000##-of-00037.json --start 0 --stop 1 <br />
Loading all 37 json data files and run article-based analysis: <br />
$ python3 article_analytics.py --path ./data/cross_edits_tmp_ttl=72_revisioninfo_20200605_1023_segment-000##-of-00037.json --start 0 --stop 37 <br />
Loading the First json data file and run author-based analysis: <br />
$ python3 author_analytics.py --path ./data/cross_edits_tmp_ttl=72_revisioninfo_20200605_1023_segment-000##-of-00037.json --start 0 --stop 1 <br />
Loading all 37 json data files and run author-based analysis: <br />
$ python3 author_analytics.py --path ./data/cross_edits_tmp_ttl=72_revisioninfo_20200605_1023_segment-000##-of-00037.json --start 0 --stop 37 <br />



