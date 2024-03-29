# COMS6111-proj2

1. Group name: Project 1 Group 23
  Qi Wang (qw2197), Yongjia Huo (yh2796)

2. Submitted files:
    * main.py – the main program, implement classification and content summary
    * READEME.md
    * folders:
        * query: 	contain the query text that professor given to us, like Root.txt, Health.txt, Sports.txt, Computer.txt
  	    * summary:  contain the content summary for each node
  	    * cache: 	cache locally the results that we get from Bing so that we only send a query to Bing if we haven't issued the exact same query before.

3. Use the following command to run our program:
  python main.py <BING_ACCOUNT_KEY> <t_es> <t_ec> <host>
  For example, 

          python main.py 'HIWkFhlcqfV0SsO9ac7smysylCtGDsuMVyqgSWPPDZI' 0.6 100 'health.com'

4. Description of Internal Design:
    Based on lecture04 page 11, we use associated queries with each category to classify the database and create content summary. We send the query to database through Bing API, record the number of matches and retrieve the top-4 matching documents. At end of round we analyze matches for each category and choose category to focus on based on coverage and specificity values.
    
    1. Part 1 implements the classification algorithm.
		1. Read the query files and organize the queries as key-value pairs, use the category as key and the set containing corresponding queries as value
		2. Issue these queries to Bing API and get the total number of matches
		3. Calculate the metrics, coverage and specificity, for each visited node. If these two metrics are all satisfied the input values, then we continue to move deep. Stop when the current node is leaf or there is no children of current node satisfy the input metrics.
		4. Return the nodes visited with coverage and specificity values, return the classification result
		
    2. Part 2 implements the document sampling and content summary construction algorithm.
	    1. Retrieve the top-4 pages returned by Bing for each query. To minimize the number of times we call Bing API, we created a cache file for each targeted database, and we will directly parse the cached query results if the file exists.
	    2. Use the combine_set() function to create a dictionary doc_sample as document sample, key is category node, value is the set of page urls associated with that node, so duplicate documents are eliminated in the process.
        3. Having obtained 1 document sample for each category node, we build a content summary associated with each such sample through generate_summary() function. We pass in the category path as input, and for each node in the path, create a node-site.txt file in the summary folder. 
        4. Use lynx to extract the text of all pages associated with each node. Text after "References" in extracted content is ignored, text within brackets "[...]" and special characters are also removed. The final string is split by whitespace into a set of terms.
        5. Calculate the document frequency of terms with the term sets generated in last step, and write to node-site.txt.

5. Bing Search Account Key: 'HIWkFhlcqfV0SsO9ac7smysylCtGDsuMVyqgSWPPDZI' or 'VpF0+1+uCEJrUKT5cFOV7eeG8cowehPtdV+sgVA4Tw0'

6. Additional Information:
    * Non-html documents: We skipped non-html pages by checking the HTTP header.

    * Result evaluation: We compared the document frequencies of some 'true' words with the sample program’s outputs, numbers given by two programs were mostly the same or differed by 1.

    * Multiple-word information: We did not include multiple-word information in the content summaries.
