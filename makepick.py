#!/usr/bin/env python
import random
import time
from urllib2 import urlopen
from bs4 import BeautifulSoup
import simplejson as json
import sys


# need a mapping between notsoexpert.com and espn
notsoexpert_to_espn = {
    'NYJ' : 'Jets',
    'NE' : 'Patriots',
    'CLE' : 'Browns',
    'BAL' : 'Ravens',
    'SD': 'Chargers',
    'PHI': 'Eagles',
    'DAL': 'Cowboys',
    'KC': 'Chiefs',
    'TEN': 'Titans',
    'HOU': 'Texans',
    'WAS': 'Redskins',
    'GB': 'Packers',
    'MIA': 'Dolphins',
    'IND': 'Colts',
    'MIN': 'Vikings',
    'CHI': 'Bears',
    'CAR': 'Panthers',
    'BUF': 'Bills',
    'STL': 'Rams',
    'ATL': 'Falcons',
    'NO': 'Saints',
    'TB': 'Buccaneers',
    'DET': 'Lions',
    'ARI': 'Cardinals',
    'DEN': 'Broncos',
    'NYG': 'Giants',
    'JAC': 'Jaguars',
    'OAK': 'Raiders',
    'SF': '49ers',
    'SEA': 'Seahawks',
    'PIT': 'Steelers',
    'CIN': 'Bengals'}


def get_power_rankings():
    power_rankings = {}
    bsoup = BeautifulSoup(urlopen('http://espn.go.com/nfl/powerrankings'))
    td_list = bsoup('td', attrs={'class': 'pr-rank'})
    for td in td_list:
        sibling = td.findNextSibling()
        team_name = sibling('a')[1].text
        rank = int(td.text)
        power_rankings[team_name] = rank
    return power_rankings

def get_matchups_for_week(week_num):
    url = 'http://notsoexpert-dev.elasticbeanstalk.com/api/schedule/%d' % week_num
    jsondata = urlopen(url).read()
    week_data = json.loads(jsondata)
    return week_data

def usage():
    print >> sys.stderr, "Please provide a week number."

def compute_bias(home_pr, away_pr):
    spread = away_pr - home_pr
    bias = (spread / 32.0) * 0.25
    return bias

def main():
    if len(sys.argv) is 1:
        usage()
        sys.exit(-1)

    random.seed(time.time())
    matchups = get_matchups_for_week(int(sys.argv[1]))
    power_rankings = get_power_rankings()
    for game in matchups['schedule']:
        home = game['home_team']
        away = game['away_team']
        home_espn = notsoexpert_to_espn[home]
        away_espn = notsoexpert_to_espn[away]
        home_pr = power_rankings[home_espn]
        away_pr = power_rankings[away_espn]
        home_bias = compute_bias(home_pr, away_pr) + 0.5
        print "Game %d, odds %f (%s) to %f (%s):" % (game['game_id'], home_bias,home_espn, 1.0 - home_bias,away_espn),
        home_win = 0
        away_win = 0
        for i in xrange(101):
            if random.random() > home_bias:
                away_win += 1
            else:
                home_win += 1
        if home_win > away_win:
            print home_espn, " (%d/101)" % home_win
        else:
            print away_espn, " (%d/101)" % away_win


if '__main__' == __name__:
    main()
