# dictmatcher
Dictionary matching Django app.

Most of the actual information is, per the spec, in the comments (especially the comments in util.py),
so there's not so much to say here.

This is already in the comments, but a proper implementation would probably be better off using a database
containing every possible multi-word anagram made by every single word in the dictionary - expensive to calculate
upfront, and would use significant disk space, but it could reasonably be maintained when adding / removing words later
on and would make this efficient even for searches with a massive number of hits.
