import argparse
import urllib.request

# parse input arguments
parser = argparse.ArgumentParser()
parser.add_argument('--search-query', type=str,
                    default='cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.NE+OR+cat:stat.ML',
                    help='query used for arxiv API. See http://arxiv.org/help/api/user-manual#detailed_examples')
parser.add_argument('--start-index', type=int, default=0, help='0 = most recent API result')
parser.add_argument('--max-index', type=int, default=10000, help='upper bound on paper index we will fetch')
parser.add_argument('--results-per-iteration', type=int, default=100, help='passed to arxiv API')
parser.add_argument('--wait-time', type=float, default=5.0,
                    help='lets be gentle to arxiv API (in number of seconds)')
parser.add_argument('--break-on-no-added', type=int, default=1,
                    help='break out early if all returned query papers are already in db? 1=yes, 0=no')
args = parser.parse_args()

# misc hardcoded variables
base_url = 'http://export.arxiv.org/api/query?'

for i in range(args.start_index, args.max_index, args.results_per_iteration):


query = 'search_query=%s&sortBy=lastUpdatedDate&start=%i&max_results=%i' % ('cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.NE+OR+cat:stat.ML',
i, )
