#!/usr/bin/env python
import random
import time
from urllib2 import urlopen
from bs4 import BeautifulSoup
import simplejson as json
import sys
import math


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


timezones = {
    'NYJ' : 'EDT',
    'NE' : 'EDT',
    'CLE' : 'EDT',
    'BAL' : 'EDT',
    'SD': 'PDT',
    'PHI': 'EDT',
    'DAL': 'CDT',
    'KC': 'CDT',
    'TEN': 'EDT',
    'HOU': 'CDT',
    'WAS': 'EDT',
    'GB': 'CDT',
    'MIA': 'EDT',
    'IND': 'EDT',
    'MIN': 'CDT',
    'CHI': 'CDT',
    'CAR': 'EDT',
    'BUF': 'EDT',
    'STL': 'CDT',
    'ATL': 'EDT',
    'NO': 'CDT',
    'TB': 'EDT',
    'DET': 'EDT',
    'ARI': 'MST',
    'DEN': 'MDT',
    'NYG': 'EDT',
    'JAC': 'EDT',
    'OAK': 'PDT',
    'SF': 'PDT',
    'SEA': 'PDT',
    'PIT': 'EDT',
    'CIN': 'EDT'}


timezone_numbers = {'EDT': -4,
        'CDT': -5,
        'MDT': -6,
        'MST': -7,
        'PDT': -7 }


number_rounds = 25


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


def compute_powerrank_bias(home_pr, away_pr):
    spread = away_pr - home_pr
    bias = (spread / 32.0) * 0.25
    return bias

def absval(num):
    return math.sqrt(num**2)

def get_tz_range(tz):
    # build a list from the timezone dictionary
    tz_list = []
    for key in tz:
        tz_list.append(tz[key])
    return absval( max(tz_list) - min(tz_list) )


def compute_timezone_bias(home_tz, away_tz):
    home_tz_num = timezone_numbers[home_tz]
    away_tz_num = timezone_numbers[away_tz]
    delta = (home_tz_num - away_tz_num) / get_tz_range(timezone_numbers)
    if delta > 0:
        # away team is travelling east
        bias = delta * 0.1
    else:
        # away team is travelling west
        bias = delta * 0.05
    return absval(bias)


def compute_altitude_bias(home_alt, away_alt):
    pass


def compute_vegas_bias(home, away):
    # ingest lines from vegas
    # http://www.footballlocks.com/nfl_lines.shtml
    pass


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
        home_bias = compute_powerrank_bias(home_pr, away_pr) + 0.5
        tz_bias = compute_timezone_bias( timezones[home], timezones[away] )
        home_bias += tz_bias
        print "Game %d, TZ Bias: %f, odds %f (%s) to %f (%s):" % (game['game_id'], tz_bias, home_bias, home_espn, 1.0 - home_bias,away_espn),
        home_win = 0
        away_win = 0
        for i in xrange(number_rounds):
            if random.random() > home_bias:
                away_win += 1
            else:
                home_win += 1
        if home_win > away_win:
            print home_espn, " (%d/%d)" % (home_win, number_rounds)
        else:
            print away_espn, " (%d/%d)" % (away_win, number_rounds)


if '__main__' == __name__:
    main()
