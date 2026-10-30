"""Render public GitHub contribution data as self-hosted README cards.

Uses the public contribution calendar; no API token or third-party card service.
Failed downloads/parsing leave the previous SVG files untouched.
"""
from datetime import date, datetime, timedelta, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
import argparse
import json
import re
import urllib.request


class CalendarParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.labels = {}
        self.tooltip = None
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'data-date' in attrs and 'id' in attrs:
            self.cells[attrs['id']] = (attrs['data-date'], int(attrs.get('data-level', 0)))
        if tag == 'tool-tip' and 'for' in attrs:
            self.tooltip = attrs['for']
            self.labels[self.tooltip] = ''
    def handle_data(self, text):
        if self.tooltip:
            self.labels[self.tooltip] += text
    def handle_endtag(self, tag):
        if tag == 'tool-tip':
            self.tooltip = None


def parse_calendar(html):
    parser = CalendarParser()
    parser.feed(html)
    result = []
    for cell_id, (day, level) in parser.cells.items():
        label = parser.labels.get(cell_id, '').strip()
        match = re.match(r'([\d,]+) contributions?\b', label)
        if match:
            count = int(match.group(1).replace(',', ''))
        elif label.startswith('No contributions'):
            count = 0
        else:
            raise ValueError(f'Cannot parse contribution count for {day}: {label}')
        result.append({'date': day, 'count': count, 'level': level})
    result.sort(key=lambda day: day['date'])
    if len(result) < 300 or len({d['date'] for d in result}) != len(result):
        raise ValueError('Incomplete or duplicated GitHub contribution calendar')
    return result


BG = '#1f242c'
FG = '#e6edf3'
MUTED = '#a0b3c4'
BLUE = '#58a6ff'
def text(x, y, value, size=16, color=FG, anchor='middle', bold=False):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="DejaVu Sans, sans-serif" font-size="{size}" text-anchor="{anchor}" font-weight="{600 if bold else 400}">{escape(str(value))}</text>'
def wrap(width, height, body, title):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img"><title>{escape(title)}</title><rect x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="8" fill="{BG}" stroke="#30363d"/>{body}</svg>'


def render(days, output, user):
    today = datetime.now(timezone.utc).date()
    days = [d for d in days if date.fromisoformat(d['date']) <= today]
    latest = date.fromisoformat(days[-1]['date'])
    if latest < today - timedelta(days=2):
        raise ValueError('Contribution calendar is stale')
    by_date = {d['date']: d['count'] for d in days}
    total = sum(d['count'] for d in days)
    longest = run = 0
    for day in days:
        run = run + 1 if day['count'] else 0
        longest = max(longest, run)
    cursor = today if by_date.get(today.isoformat(), 0) else today - timedelta(days=1)
    current = 0
    while by_date.get(cursor.isoformat(), 0):
        current += 1
        cursor -= timedelta(days=1)
    stats = text(160, 66, f'{total:,}', 34, bold=True) + text(160, 102, 'Total contributions', 16, MUTED)
    stats += text(160, 133, 'Public calendar · past year', 12, MUTED)
    stats += '<path d="M310 30V158M610 30V158" stroke="#46515f"/>'
    stats += '<circle cx="460" cy="65" r="41" fill="none" stroke="#4a7188" stroke-width="3"/>'
    stats += text(460, 77, current, 34, BLUE, bold=True) + text(460, 132, 'Current streak', 16, MUTED)
    stats += text(760, 66, longest, 34, bold=True) + text(760, 102, 'Longest streak', 16, MUTED)
    stats += text(760, 133, 'Days · within displayed year', 12, MUTED)
    stats += text(460, 178, f'Updated {today.isoformat()} · UTC', 11, MUTED)
    cards = {'stats.svg': wrap(920, 196, stats, f'{user}: {total} contributions in the displayed year; current streak {current} days; longest {longest} days')}

    recent = [{'date': (today-timedelta(days=29-i)).isoformat(), 'count': by_date.get((today-timedelta(days=29-i)).isoformat(), 0)} for i in range(30)]
    high = max(1, max(d['count'] for d in recent))
    chart = text(460, 32, f"{user}'s contribution graph", 17, bold=True)
    for i in range(5):
        y=65+i*45
        chart += f'<path d="M65 {y}H880" stroke="#35404b" stroke-width="1"/>'
        chart += text(51, y+4, round(high*(4-i)/4), 11, MUTED, 'end')
    pts = [(65+i*815/29, 245-d['count']*180/high) for i,d in enumerate(recent)]
    points = ' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)
    chart += f'<polygon points="65,245 {points} 880,245" fill="#58a6ff" opacity="0.1"/>'
    chart += f'<polyline points="{points}" fill="none" stroke="{BLUE}" stroke-width="2"/>'
    for x,y in pts: chart += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.7" fill="#8abfff"/>'
    for i in [0,7,14,21,29]:chart += text(pts[i][0], 273, recent[i]['date'][5:], 11, MUTED)
    chart += text(460, 300, 'Daily contributions · last 30 days · UTC', 11, MUTED)
    cards['activity.svg'] = wrap(920, 322, chart, f'{user}: contribution activity during the last 30 days')

    grid = text(460, 29, 'A year in commits, pull requests, issues & reviews', 15, bold=True)
    colors = ['#2b333e', '#24465c', '#2c678c', '#388cba', '#58a6ff']
    start = date.fromisoformat(days[0]['date'])
    first = start - timedelta(days=(start.weekday()+1)%7)
    animated = []
    for d in days:
        day = date.fromisoformat(d['date']); delta=(day-first).days
        x=40+(delta//7)*16;y=60+(delta%7)*16
        grid += f'<rect x="{x}" y="{y}" width="12" height="12" rx="2" fill="{colors[min(d["level"],4)]}"/>'
        if d['count']:animated.append((x+6,y+6))
    if animated:
        points=';'.join(f'{x},{y}' for x,y in animated)
        grid += f'<circle r="3" fill="#d7eaff"><animateMotion dur="24s" repeatCount="indefinite" calcMode="discrete" values="{points}"/></circle>'
    grid += text(40, 201, days[0]['date'], 11, MUTED,'start')+text(880,201,days[-1]['date'],11,MUTED,'end')
    cards['commits.svg'] = wrap(920, 222, grid, f'{user}: public contribution calendar with an animated trail')
    output.mkdir(parents=True, exist_ok=True)
    for name, svg in cards.items(): (output/name).write_text(svg)
    (output/'contributions.json').write_text(json.dumps({'username':user,'updated':today.isoformat(),'days':days},indent=2))
    print(f'{total} contributions; {current} day current streak; {longest} day longest streak; {len(days)} calendar days')


def main():
    p=argparse.ArgumentParser();p.add_argument('--user',default='yedmahos');p.add_argument('--input',type=Path);args=p.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9-]+',args.user):raise ValueError('Invalid username')
    if args.input: html=args.input.read_text()
    else:
        req=urllib.request.Request(f'https://github.com/users/{args.user}/contributions',headers={'User-Agent':'GitHub-Profile-Stats','Accept-Language':'en-US,en;q=0.9'})
        with urllib.request.urlopen(req,timeout=30) as r: html=r.read().decode()
    render(parse_calendar(html),Path(__file__).resolve().parents[1]/'assets',args.user)

if __name__=='__main__':main()
