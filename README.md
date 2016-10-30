# COMS6111-proj2

* Group name: Project 1 Group 23
  Qi Wang (qw2197), Yongjia Huo (yh2796)

* Submitted files:
  main.py – the main program, implement classification and content summary
  READEME.md
  folders:
  	- query: 	contain the query text that professor given to us, like Root.txt, Health.txt, Sports.txt, Computer.txt
  	- summary:  contain the content summary for each node
  	- cache: 	cache locally the results that we get from Bing so that we only send a query to Bing if we haven't issued the exact same query before.

* Use the following command to run our program:
  python main.py <BING_ACCOUNT_KEY> <t_es> <t_ec> <host>
  For example, 
      python main.py 'HIWkFhlcqfV0SsO9ac7smysylCtGDsuMVyqgSWPPDZI' 0.6 100 'health.com'

* Description of Internal Design:
	part 1)
		This part implements the classification algorithm discussed in class.
			1. Read the query files and organize the queries as key-value pairs, use the category as key and the set containing corresponding queries as value
			2. Issue these queries to Bing API and get the total number of matches (do not need to retrieve the documents)
			3. Calculate the metrics, coverage and specificity, for each visited node. If these two metrics are all satisfied the input values, then we continue to move deep. Stop when the current node is leaf or there is no children of current node satisfy the input metrics.
			4. Return the nodes visited with coverage and specificity values, return the classification result
	part 2)
	


* Bing Search Account Key: 'HIWkFhlcqfV0SsO9ac7smysylCtGDsuMVyqgSWPPDZI' or 'VpF0+1+uCEJrUKT5cFOV7eeG8cowehPtdV+sgVA4Tw0'


