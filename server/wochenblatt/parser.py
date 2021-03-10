import re

from odf.opendocument import load
from odf.text import P
import datetime
from typing import Dict, Tuple, List, Union

wt_re = re.compile(
    r"^(?P<wd>Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag), (?P<date>\d{1,2}\.\d{1,2}\.)(?P<rest>.*)"
)
time_re = re.compile(r"^(?P<start>\d{1,2}:\d\d)(?: – (?P<end>\d{1,2}:\d\d))?(?P<rest>.*)")
lj_re = re.compile(r"^L e s e j a h r (\w)(.*)")


def parse_wochenblatt(file) -> \
        Dict[str, Union[Tuple[str, ...], List[Dict[str, Union[Tuple[str, ...], str, datetime.datetime]]], str]]:
    doc = load(file)
    events: List[Dict[str, Union[Tuple[str, ...], List, datetime.date]]] = []
    lj = ''
    lj_info = ''
    e = -1
    se = -1
    prev = None
    additional_text = ()
    info = False

    for child in doc.getElementsByType(P):
        text = str(child)
        if match := wt_re.match(text):
            e += 1
            date = match.group('date')
            day, month, _ = tuple(date.split('.'))
            events.append({'date': datetime.date.today().replace(month=int(month), day=int(day))})
            if match.group('rest'):
                events[e]['data'] = (match.group('rest'),)
            se = -1
        elif e >= 0:
            if 'data' not in events[e]:
                events[e]['data'] = ()
            if 'events' not in events[e]:
                events[e]['events'] = []
            if match := time_re.match(text):
                se = len(events[e]['events'])
                start = match.group('start')
                start_hour, start_minute = tuple(start.split(':'))
                events[e]['events'].append({
                    'start': datetime.time(int(start_hour), int(start_minute)),
                    'name': match.group('rest'),
                    'data': ()
                })
                end = match.group('end')
                if end:
                    end_hour, end_minute = tuple(end.split(':'))
                    events[e]['events'][se]['end'] = datetime.time(int(end_hour), int(end_minute))
                else:
                    events[e]['events'][se]['end'] = None
            else:
                if se >= 0:
                    events[e]['events'][se]['data'] += (text,)
                else:
                    events[e]['data'] += (text,)
            if prev == '' and text == '':
                e = -1
        else:
            if match := lj_re.match(text):
                lj = match.group(1)
                lj_info = match.group(2)
            elif 'Wir informieren:' in text:
                info = True
                additional_text += (text,)
            elif info and not (prev == '' and text == ''):
                additional_text += (text,)
        prev = text

    parsed = {
        'events': [],
        'lesejahr': lj,
        'lesejahr_info': lj_info,
        'info_text': additional_text
    }

    for evt in events:
        for sub in evt['events']:
            sub: dict
            p = {
                'start': datetime.datetime.combine(evt['date'], sub['start']),
                'name': sub['name'],
                'data': evt['data'] + sub['data']
            }
            if sub['end']:
                p['end'] = datetime.datetime.combine(evt['date'], sub['end'])
            parsed['events'].append(p)
    return parsed
