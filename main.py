"""
Queries arxiv API and downloads papers (the query is a parameter).
The script is intended to enrich an existing database pickle (by default db.p),
so this file will be loaded first, and then new results will be added to it.
"""
import argparse
import ujson
import urllib.request
import feedparser
from time import sleep

from slackHelper import SlackHelper

last = '1606.07461'
base_url = 'http://export.arxiv.org/api/query?'


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


def getlastpapers():
    papers = []
    global last
    dic = ujson.load(open('data.json'))
    nb_send = 0
    for i in range(args.start_index, args.max_index, args.results_per_iteration):

        print("Results %i - %i" % (i, i + args.results_per_iteration))
        query = 'search_query=%s&sortBy=lastUpdatedDate&start=%i&max_results=%i' % (args.search_query, i, args.results_per_iteration)
        with urllib.request.urlopen(base_url + query) as url:
            response = url.read()
        parse = feedparser.parse(response)
        for e in parse.entries:

            j = encode_feedparser_dict(e)

            rawid, version = parse_arxiv_url(j['id'])

            if rawid == last:
                print(i, 'Break ! ! !')
                break
            else:

                j['_rawid'] = rawid
                j['_version'] = version

                tuse = []
                for user in dic:
                    for w in dic[user]:
                        w = w.replace('_', ' ')
                        test = w in j['summary_detail']['value'] or w in j['title_detail']['value']
                        if test:
                            tuse.append(user)
                            break
                if len(tuse) > 0:
                    make_message(tuse, j)
                    nb_send += 1

            papers.append(j)
    if len(papers) > 0:
        last = papers[0]['_rawid']

    return len(papers), nb_send


def make_message(userlist, paper):
    men = ''
    for u in userlist:
        men += ' <@' + u + '>, '

    att = [
        {
            "fallback": 'The paper : ' + paper['title_detail']['value'].replace('\n', ' ') + ' written by ' + paper['authors'][0]['name'] + '  \n You may want to check it out at ' + paper['id'] + ' !',
            "color": "#36a64f",
            "attachment_type": "default",
            "text": "You may want to check it out at : " + paper['id'],
            "fields": [
                {
                    "title": "\" " + paper['title_detail']['value'].replace('\n', ' ') + "\"",
                    "value": " written by *" + paper['authors'][0]['name'] + "* et al.",
                    "short": False
                }
            ]

        }
    ]

    slackhelper.post_message_to_channel("Hey " + men + "this paper just came out ! ", att)


if __name__ == "__main__":
    # parse input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--search-query', type=str,
                        default='cat:cs.CV+OR+cat:cs.AI+OR+cat:cs.LG+OR+cat:cs.CL+OR+cat:cs.NE+OR+cat:stat.ML',
                        help='query used for arxiv API. See http://arxiv.org/help/api/user-manual#detailed_examples')
    parser.add_argument('--start-index', type=int, default=0, help='0 = most recent API result')
    parser.add_argument('--max-index', type=int, default=50, help='upper bound on paper index we will fetch')
    parser.add_argument('--results-per-iteration', type=int, default=50, help='passed to arxiv API')
    parser.add_argument('--wait-time', type=float, default=30,
                        help='lets be gentle to arxiv API (in minutes)')

    args = parser.parse_args()

    slackhelper = SlackHelper()

    while True:
        nbp, nbn = getlastpapers()
        print('-- update --')
        print('number of new papers : ', nbp)
        print('number sent :', nbn)
        sleep(args.wait_time * 60)
