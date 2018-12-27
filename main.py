"""
Queries arxiv API and downloads papers (the query is a parameter).
The script is intended to enrich an existing database pickle (by default db.p),
so this file will be loaded first, and then new results will be added to it.
"""

import os
import time
import pickle
import random
import argparse
import urllib.request
import feedparser

mega = []

last = '1812.10464'
def encode_feedparser_dict(d):
    """
    helper function to get rid of feedparser bs with a deep copy.
    I hate when libs wrap simple things in their own classes.
    """
    if isinstance(d, feedparser.FeedParserDict) or isinstance(d, dict):
        j = {}
        for k in d.keys():
            j[k] = encode_feedparser_dict(d[k])
        return j
    elif isinstance(d, list):
        l = []
        for k in d:
            l.append(encode_feedparser_dict(k))
        return l
    else:
        return d


def parse_arxiv_url(url):
    """
    examples is http://arxiv.org/abs/1512.08756v2
    we want to extract the raw id and the version
    """
    ix = url.rfind('/')
    idversion = url[ix + 1:]  # extract just the id (and the version)
    parts = idversion.split('v')
    assert len(parts) == 2, 'error parsing url ' + url
    return parts[0], int(parts[1])


if __name__ == "__main__":

    # parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--search-query', type=str,
                        default='cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.NE+OR+cat:stat.ML',
                        help='query used for arxiv API. See http://arxiv.org/help/api/user-manual#detailed_examples')
    parser.add_argument('--start-index', type=int, default=0, help='0 = most recent API result')
    parser.add_argument('--max-index', type=int, default=20, help='upper bound on paper index we will fetch')
    parser.add_argument('--results-per-iteration', type=int, default=10, help='passed to arxiv API')
    parser.add_argument('--wait-time', type=float, default=5.0,
                        help='lets be gentle to arxiv API (in number of seconds)')
    parser.add_argument('--break-on-no-added', type=int, default=1,
                        help='break out early if all returned query papers are already in db? 1=yes, 0=no')
    args = parser.parse_args()

    # misc hardcoded variables
    base_url = 'http://export.arxiv.org/api/query?'  # base api query url
    print('Searching arXiv for %s' % (args.search_query,))

    # -----------------------------------------------------------------------------
    # main loop where we fetch the new results
    # print('database has %d entries at start' % (len(db),))

    num_added_total = 0
    for i in range(args.start_index, args.max_index, args.results_per_iteration):

        print("Results %i - %i" % (i, i + args.results_per_iteration))
        query = 'search_query=%s&sortBy=lastUpdatedDate&start=%i&max_results=%i' % (args.search_query,
                                                                                    i, args.results_per_iteration)
        with urllib.request.urlopen(base_url + query) as url:
            response = url.read()
        parse = feedparser.parse(response)
        num_added = 0
        num_skipped = 0

        for e in parse.entries:
            print(e)
            j = encode_feedparser_dict(e)

            # extract just the raw arxiv id and version for this paper
            rawid, version = parse_arxiv_url(j['id'])

            print(rawid == last)
            j['_rawid'] = rawid
            j['_version'] = version


        mega.append(j)


    print(mega)