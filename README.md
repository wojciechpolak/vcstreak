VC The Longest Streak
=====================

The `vcstreak.py` finds the longest streak of consecutive commit dates.
It supports local Git, Mercurial, and Subversion repositories.

	Usage: vcstreak.py [options] REPO-PATH

	Options:
	-h, --help            show this help message and exit
	-r, --reverse         Reverse output results
	-t NUM, --top=NUM     Show NUM top users (0 is unlimited and default)
	-s NUM, --streaks=NUM Show NUM longest streaks
	-e, --exclude-weekends
	                      Exclude weekends
	-n, --name            Alias for --id-author=name
	--id-author=ID        Author ID strategy [name, email]. email is default
	--author=PATTERN      Limit the commits output to ones with author header
	--since=DATE          Show commits more recent than a specific date
	--branch=NAME         Branch name (all branches by default)
	--sortby=NAME         Sort by [streaks, commits] (streaks is default)
	--output=FORMAT       Output format [simple, json, xml, yaml]

Author
------

* Wojciech Polak (http://wojciechpolak.org/)

Example Usage
-------------

	$ vcstreak.py ~/src/repo/
		1) Wojciech Polak (2065 commits)
			53 days: 2011-11-29 - 2012-01-20 (89da9804fb..a1fdd91e35)
			28 days: 2012-08-08 - 2012-09-04 (66a1bbe0f3..dbce082f1c)
			27 days: 2011-08-26 - 2011-09-21 (3232fe6a43..8025cbc197)
			26 days: 2011-05-03 - 2011-05-28 (c509a7cab7..6378b723a7)
			24 days: 2012-02-09 - 2012-03-03 (6ec70fa2d1..47d7bd0f0d)
		...

	$ vcstreak.py --name --top 3 ~/src/git/
		1) Junio C Hamano (15962 commits)
			83 days: 2006-12-16 - 2007-03-08 (1576f5f7b2..bd1fc628b8)
			54 days: 2005-09-30 - 2005-11-22 (6dc88cc0dc..302ebfe521)
			48 days: 2006-03-24 - 2006-05-10 (84a9b58c42..618faa1dc7)
			37 days: 2005-08-23 - 2005-09-28 (f5e375c9a9..bf7960eb51)
			33 days: 2006-02-09 - 2006-03-13 (5f73076c1a..ea75cb7284)
		2) Linus Torvalds (1109 commits)
			30 days: 2005-04-07 - 2005-05-06 (e83c516331..ee267527aa)
			14 days: 2005-06-17 - 2005-06-30 (c538d2d34a..d0efc8a71d)
			12 days: 2005-05-29 - 2005-06-09 (b97e3dfa76..aa16021efc)
			11 days: 2005-05-17 - 2005-05-27 (c9049d41b8..84c1afd7e7)
			 8 days: 2005-07-03 - 2005-07-10 (8a65ff7666..cf219196a8)
		3) Shawn O. Pearce (1334 commits)
			12 days: 2007-01-20 - 2007-01-31 (81c0f29a56..76f8a302c7)
			11 days: 2007-09-17 - 2007-09-27 (3849bfba84..0b2bc460fc)
			 8 days: 2006-11-21 - 2006-11-28 (f18e40a1a6..67ffa11425)
			 6 days: 2006-11-04 - 2006-11-09 (dfb960920d..2d19516db4)
			 6 days: 2006-11-11 - 2006-11-16 (49b86f010c..c1237ae288)
	2014-11-11T09:30:50Z
