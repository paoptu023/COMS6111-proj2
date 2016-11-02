# COMS6111-proj2

1. Group name: Project 1 Group 23
  Qi Wang (qw2197), Yongjia Huo (yh2796)

2. Submitted files:
  main.py – the main program, implement classification and content summary
  READEME.md
  folders:
  	* query: 	contain the query text that professor given to us, like Root.txt, Health.txt, Sports.txt, Computer.txt
  	* summary:  contain the content summary for each node
  	* cache: 	cache locally the results that we get from Bing so that we only send a query to Bing if we haven't issued the exact same query before.

3. Use the following command to run our program:
  python main.py <BING_ACCOUNT_KEY> <t_es> <t_ec> <host>
  For example, 

          python main.py 'HIWkFhlcqfV0SsO9ac7smysylCtGDsuMVyqgSWPPDZI' 0.6 100 'health.com'

4. Description of Internal Design:
    1. Part 1 implements the classification algorithm.
		1. Read the query files and organize the queries as key-value pairs, use the category as key and the set containing corresponding queries as value
		2. Issue these queries to Bing API and get the total number of matches (do not need to retrieve the documents)
		3. Calculate the metrics, coverage and specificity, for each visited node. If these two metrics are all satisfied the input values, then we continue to move deep. Stop when the current node is leaf or there is no children of current node satisfy the input metrics.
		4. Return the nodes visited with coverage and specificity values, return the classification result
		
    2. Part 2 implements the document sampling and content summary construction algorithm.
	    1. We retrieve the top-4 pages returned by Bing for each query. To minimize the number of times we call Bing API, we created a cache file for each targeted database, and we will directly parse the cached query results if the file exists.
	        We use the combine_set() function to create a dictionary doc_sample as document sample, key is category node, value is the set of page urls associated with that node, so duplicate documents are eliminated in the process.
        2. Having obtained 1 document sample for each category node, we build a content summary associated with each such sample through generate_summary() function. We pass in the category path as input, and for each node in the path, create a node-site.txt file in the summary folder.
            We use lynx to extract the text of all pages associated with each node, and we skip non-html pages by checking the HTTP header.
        3. We find the position of "References" in extracted content and ignore any text after it. Then we convert the content to lower case, use process_page() to remove text within brackets "[...]" and special characters, the final string is split by whitespace into a set of terms.
        4. Finally, we calculate the document frequency of terms with the term sets generated in step 3, and write to node-site.txt.

5. Bing Search Account Key: 'HIWkFhlcqfV0SsO9ac7smysylCtGDsuMVyqgSWPPDZI'

6. Additional Information:
    * Result evaluation: We compared the document frequencies of some 'true' words with the sample program’s outputs, numbers given by two programs were mostly the same or differed by 1.

    * Multiple-word information: We did not include multiple-word information in the content summaries.
