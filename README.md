# fsot
Honors thesis project in linguistics. Software package for evaluating ranked sets of regular expressions as OT phonologies.

For a background in Optimality Theory, read Prince and Smolensky (1993). In short, the program contains a number of hardcoded regex formulae that assign a penalty to an utput segment for each occurrence of the regex. It then produces a collection of all the output strings in \Sigma^* that could possibly be optimal - that is, incur the fewest violations at the highest rank with an uneven number of violations - under some ranking of the constraint set. The program contains one basic test case and one case for data from Kinywarwanda, detailed in the paper. It can print out some wicked finite state machines if you know how to use the dot language that comes with GraphViz.

From a perspective completely outside of linguistic theory, the program simply computes a restricted version of the Pareto frontier for elements of \Sigma^* for some finite alphabet \Sigma with respect to a set of preferences that take the form of regex over \Sigma.

Read the thesis for a full documentation. Please let me know if you use this for anything cool.
