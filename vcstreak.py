#!/usr/bin/env python

# vcstreak.py -- Copyright (C) 2014, 2020 Wojciech Polak
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

import os
import datetime
import subprocess
from email.utils import mktime_tz, parsedate_tz, formatdate


def calculate(options=None, args=None):
    options = options or {}
    args = args or ['.']
    cwd = args[0]

    commit_fields = [
        'id',
        'author_name',
        'author_email',
        'date',
    ]

    vcs = False
    if os.path.isdir(os.path.join(cwd, '.git/')):
        vcs = 'git'
    elif os.path.isdir(os.path.join(cwd, '.hg/')):
        vcs = 'hg'
    elif os.path.isdir(os.path.join(cwd, '.svn/')):
        vcs = 'svn'

    if vcs == 'git':
        log_format = ['%H', '%an', '%ae', '%aD']
        log_format = '%x1f'.join(log_format) + '%x1e'
        cmd_opts = ''

        if options.author:
            cmd_opts += ' --author="%s"' % options.author
        if options.since:
            cmd_opts += ' --since="%s"' % options.since

        cmd_opts += ' %s' % (options.branch or '--all')
        cmd_opts += ' --format="%s"' % log_format
        cmd = 'git log' + cmd_opts

    elif vcs == 'hg':
        log_format = [
            '{rev}:{node}',
            '{author|person}',
            '{author|email}',
            '{date|rfc822date}',
        ]
        log_format = ';;'.join(log_format) + '\n'
        cmd_opts = ''

        if options.author:
            cmd_opts += ' --user="%s"' % options.author
        if options.since:
            cmd_opts += ' --date="%s"' % options.since

        cmd_opts += ' --template="%s"' % log_format
        cmd = 'hg log' + cmd_opts

    elif vcs == 'svn':
        cmd = 'svn log --xml'

    else:
        raise Exception('Unknown VCS')

    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, cwd=cwd)
    log, _ = proc.communicate()

    if vcs == 'git':
        log = log.decode('utf-8', 'ignore').strip('\n\x1e').split('\x1e')
        log = [row.strip().split('\x1f') for row in log]
    elif vcs == 'hg':
        log = log.decode('utf-8', 'ignore').split('\n')
        log = [row.strip().split(';;') for row in log]
    elif vcs == 'svn':
        from xml.dom.minidom import parseString
        tmplog = []
        dom = parseString(log)
        entries = dom.getElementsByTagName('logentry')
        for elem in entries:
            row = [elem.getAttribute('revision')]
            for subc in elem.childNodes:
                if subc.nodeName == 'author':
                    author = subc.firstChild.nodeValue
                    row.append(author)
                    row.append(author)
                elif subc.nodeName == 'date':
                    date = subc.firstChild.nodeValue
                    dt = datetime.datetime.strptime(
                        date, '%Y-%m-%dT%H:%M:%S.%fZ')
                    rfcdate = formatdate(float(dt.strftime('%s')))
                    row.append(rfcdate)
            if len(row) == 4:
                tmplog.append(row)
        log = tmplog

    log = [dict(list(zip(commit_fields, row))) for row in log]
    data = {}

    id_author_strategy = 'author_email'
    if options.id_author == 'name':
        id_author_strategy = 'author_name'

    for entry in reversed(log):
        if 'author_email' not in entry:
            continue
        author_id = entry[id_author_strategy]

        ### Normalize IDs
        author_id = author_id.lower()  # normalize IDs
        if options.normalize_ids:
            for norm in options.normalize_ids.split(','):
                source, target = norm.split(':')
                author_id = author_id.replace(source, target)

        if author_id not in data:
            data[author_id] = {
                'info': {
                    'author_name': author_id if id_author_strategy == 'author_name' else entry['author_name'],
                    'author_email': author_id if id_author_strategy == 'author_email' else entry['author_email'],
                },
                'streaks': {},
                'commits': [],
            }
        data[author_id]['commits'].append({
            'id': entry['id'],
            'date': datetime.datetime.utcfromtimestamp(
                mktime_tz(parsedate_tz(entry['date']))).date(),
        })

    for author_id in data:
        d = data[author_id]

        streaks = d['streaks']
        streak_id = 0
        streak_last_date = None

        for entry in d['commits']:
            if streak_last_date:
                diff_days = (entry['date'] - streak_last_date).days
            else:
                diff_days = 0

            if diff_days > 1:
                if diff_days == 3 and options.exclude_weekends:
                    day1 = entry['date'] - datetime.timedelta(days=1)
                    day2 = entry['date'] - datetime.timedelta(days=2)
                    if day1.weekday() == 6 and day2.weekday() == 5:  # weekend
                        pass
                    else:
                        streak_id += 1
                else:
                    streak_id += 1

            if streak_id not in streaks:
                streaks[streak_id] = {
                    'count': 1,
                    'id_start': entry['id'],
                    'id_end': entry['id'],
                    'date_start': entry['date'],
                    'date_end': entry['date'],
                }

            if diff_days == 0:
                streaks[streak_id].update({
                    'id_end': entry['id'],
                    'date_end': entry['date'],
                })
            elif diff_days == 1:
                streaks[streak_id].update({
                    'id_end': entry['id'],
                    'date_end': entry['date'],
                })
                streaks[streak_id]['count'] += 1

            if diff_days >= 0:
                streak_last_date = entry['date']

    # sort streaks, setup data
    for author_id in data:
        d = data[author_id]
        d['streaks'] = list(d['streaks'].values())
        d['streaks'].sort(key=lambda x: x['count'], reverse=True)
        d['info']['longest_streak'] = d['streaks'][0]['count']
        d['info']['commits'] = len(d['commits'])
        d['streaks'] = d['streaks'][:options.streaks]
        del d['commits']

    # sort users by...
    users = list(data.values())
    if options.sortby == 'commits':
        users.sort(key=lambda x: x['info']['longest_streak'], reverse=True)
        users.sort(key=lambda x: x['info']['commits'], reverse=True)
    else:
        users.sort(key=lambda x: x['info']['commits'], reverse=True)
        users.sort(key=lambda x: x['info']['longest_streak'], reverse=True)

    timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

    for i, user in enumerate(users, 1):
        user['info']['place'] = i
        user['info']['timestamp'] = timestamp

    if options.top:
        users = users[:options.top]

    if options.reverse:
        users = reversed(users)

    return users


def main():
    import sys
    from optparse import OptionParser

    if sys.version_info < (3, 0):
        import codecs
        sys.stdout = codecs.getwriter('utf8')(sys.stdout)

    usage = 'Usage: %prog [options] REPO-PATH'
    parser = OptionParser(usage=usage)

    parser.add_option('-r', '--reverse', action='store_true', dest='reverse',
                      default=False,
                      help='Reverse output results')

    parser.add_option('-t', '--top', type='int', dest='top', default=0,
                      metavar='NUM',
                      help='Show NUM top users (0 is unlimited and default)')

    parser.add_option('-s', '--streaks', type='int', dest='streaks', default=5,
                      metavar='NUM',
                      help='Show NUM longest streaks')

    parser.add_option('-e', '--exclude-weekends', action='store_true',
                      dest='exclude_weekends',
                      help='Exclude weekends')

    parser.add_option('-n', '--name', dest='id_author', const='name',
                      action='store_const',
                      help='Alias for --id-author=name')

    parser.add_option('--id-author', dest='id_author', default='email',
                      metavar='ID',
                      help='Author ID strategy [name, email]. email is default')

    parser.add_option('--author', dest='author',
                      metavar='PATTERN',
                      help='Limit the commits output to ones with author header')

    parser.add_option('--since', dest='since',
                      metavar='DATE',
                      help='Show commits more recent than a specific date')

    parser.add_option('--branch', dest='branch', default=None,
                      metavar='NAME',
                      help='Branch name (all branches by default)')

    parser.add_option('--sortby', dest='sortby', default='streaks',
                      metavar='NAME',
                      help='Sort by [streaks, commits] (streaks is default)')

    parser.add_option('--show', dest='show', default='all',
                      metavar='NAME',
                      help='Show data [all, streaks, commits] (all is default)')

    parser.add_option('--normalize-ids', dest='normalize_ids', default='',
                      metavar='FORMAT',
                      help='Normalize IDs (e.g. emails): s1:t1,s2:t2,...')

    parser.add_option('--output', dest='output', default='simple',
                      metavar='FORMAT',
                      help='Output format [simple, json, xml, yaml]')

    options, args = parser.parse_args()
    if not args:
        parser.error('REPO-PATH not given')

    data = calculate(options, args)

    if options.output == 'json':
        import json
        def date_handler(obj):
            return obj.isoformat() if hasattr(obj, 'isoformat') else obj
        print(json.dumps(list(data), default=date_handler, indent=4,
                         sort_keys=True, ensure_ascii=False))

    elif options.output == 'yaml':
        import yaml
        print(yaml.safe_dump(list(data), encoding='utf-8',
                             default_flow_style=False, indent=4, width=70))

    elif options.output == 'xml':
        import dicttoxml
        print(dicttoxml.dicttoxml(list(data)))

    else:
        for entry in data:
            info = entry['info']
            if options.id_author == 'name':
                author_str = info['author_name']
            else:
                if info['author_name'] == info['author_email']:
                    author_str = info['author_name']
                else:
                    author_str = '%s <%s>' % (info['author_name'],
                                              info['author_email'])

            if options.show == 'all' or options.show == 'commits':
                print('%5d) %s (%d commits)' %
                      (info['place'],
                       author_str.encode('utf-8', 'ignore').decode('utf-8'),
                       info['commits']))
            elif options.show == 'streaks':
                print('%5d) %s' %
                      (info['place'],
                       author_str.encode('utf-8', 'ignore').decode('utf-8')))

            if options.show == 'all' or options.show == 'streaks':
                for streak in entry['streaks']:
                    print('\t%4d %s: %s - %s (%s..%s)' %
                          (streak['count'],
                           'days' if streak['count'] > 1 else 'day ',
                           streak['date_start'],
                           streak['date_end'],
                           streak['id_start'][:10],
                           streak['id_end'][:10]))
        if len(data):
            print(data[0]['info']['timestamp'])


if __name__ == '__main__':
    main()
