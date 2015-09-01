#!/usr/bin/env python

import copy
import itertools
import re
import sys
import time
import subprocess as sp
import threading
import json
import csv
from threading import Thread
from datetime import datetime
from types import NoneType
from pprint import pprint


qos_rgx = re.compile(r'begin_QOS_statistics\s+(.+?)\s+end_QOS_statistics',
                     re.DOTALL | re.IGNORECASE | re.MULTILINE)
qos_part_rgx = re.compile(r'(?:(\w+)\t(.+?)$)+',
                          re.MULTILINE | re.DOTALL)

with open('/mnt/xtr/build/newvids/patterns_qos.txt', 'r') as F:
    log = F.read()
qos_logs = qos_rgx.findall(log)
qos_ss = {}
hdrs = {}


def slot_row(ss, row, key, val, vtype):
    global hdrs
    if vtype not in ss:
        ss[vtype] = []
    ss[vtype].append(row)
    if vtype not in hdrs:
        hdrs[vtype] = []
    for key in row.keys():
        if key not in hdrs[vtype]:
            hdrs[vtype].append(key)
    row = {}

for qos_log in qos_logs:
    qos_parts = qos_part_rgx.findall(qos_log)
    row = None
    for q in qos_parts:
        key = q[0]
        try:
            val = int(q[1])
        except ValueError:
            try:
                val = float(q[1])
            except ValueError:
                val = q[1]
        if key == 'subsession':
            vtype = val
            if row is not None:  # second subsession of this log?
                slot_row(qos_ss, row, key, val, vtype)
            row = {'type': vtype}
        else:
            row[key] = val

    slot_row(qos_ss, row, key, val, vtype)


for vtype in hdrs.keys():
    safe_path = re.sub(r'[/\'"]+', '_', 'qos%s.csv' % vtype)
    with open(safe_path, 'w') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=hdrs[vtype])
        writer.writeheader()
        for row in qos_ss[vtype]:
            writer.writerow(row)
