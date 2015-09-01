#!/usr/bin/env python

from __future__ import print_function
import os
import sys
import json
import time
import datetime
import logging
from configs.env import pathnames as env
import configs
from configs.OR_settings_template import OR_settings
from configs.cameras import cameras
from configs.static import my_settings_static
from configs.vary import my_settings_vary
import copy
import itertools
import re
import time
import subprocess as sp
import threading
from threading import Thread, Lock
from types import NoneType
import configs
from enum import Enum

sys.path.append('.')
sys.path.append('/home/kev')

"""
    'file_prefix': lambda s,d,p,n: '%s_%d_%d_%s' % (s,d,p,n),
    openRTSP -D 1 -c -B $TEN_MB -b $TEN_MB -q -Q -F tcTcpQtM -d 28800 -P 900 \
             -t -u admin 123456 rtsp://192.168.1.108:554/11
"""


class FWLogger(object):
    log_filename = os.path.join(env['prefix_log'],
                                env['global_log_filename'])
    print("Log filename=%s" % log_filename)
    logging.basicConfig(filename=log_filename)
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    E_EARLY_TERM = "early_term"
    E_TERMINATION = "termination"
    E_STALLED = "stalled"
    E_START_CRON = "start_cron"
    E_END_CRON = "end_cron"
    E_START_RESTART = "restart"
    L_CRITICAL = logger.critical
    L_DEBUG = logger.debug
    L_DISABLED = logger.disabled
    L_ERROR = logger.error
    L_EXCEPTION = logger.exception
    L_FATAL = logger.fatal
    L_INFO = logger.info
    L_WARN = logger.warn
    L_WARNING = logger.warning

    @classmethod
    def log(klass, level_fn, cam_id, time_sig, event_type, msg):
        try:
            rec = '%s|%s|%s|%s|%f|%s' % (level_fn.__name__, cam_id, time_sig,
                                         event_type, time.time(), msg)
            getattr(klass.logger, level_fn.__name__)(rec)
            print(rec)
        except:
            print("FWLogger.log prob...")


def make_filename(vary_tokens):
    name = re.sub(' ', '', '_'.join(vary_tokens))
    name = re.sub('^-', '', name)
    name = re.sub('-', '_', name)
    return name


# synthesize CLI settings for openRTSP
def merge_settings(template, static, vary, camera):
    # flatten the static settings
    # if val is not None else '-%s' % template[key]['key'])
    variation_inputs = [var for key, var in vary.iteritems()]
    variations = list(itertools.product(*variation_inputs))
    for variation_set in variations:
        settings = copy.deepcopy(static)
        for variation_component in variation_set:
            for key, val in variation_component.iteritems():
                settings[key] = val
        # Filename_settings = ['%s%s' % (key, str(val)) \
        #    if val is not None else key for kv_pair in variation_set \
        #        for key,val in kv_pair.iteritems() ]
        # settings['file_prefix'] = make_filename(filename_settings)
        yield settings


def extrude_settings(OR_settings, settings):
    set_list = []
    for setname, val in settings.iteritems():
        if setname not in OR_settings:
            raise Exception("Unknown setting(%s=%s)" % (setname, str(val)))
        if type(val) != OR_settings[setname]['type']:
            raise Exception("Invalid setting type(%s=%s): expected %s, got %s"
                            % (setname, str(val),
                               str(OR_settings[setname]['type']),
                               str(type(val))))
        if type(val) == dict:
            settings_pair = {'key': OR_settings[setname]['key']}
            settings_pair.update(val)
        else:
            settings_pair = {'key': OR_settings[setname]['key'], 'val': val}
        for settings_template in OR_settings[setname]['tmpl']:
            settings_comp = settings_template.format(**settings_pair)
            if settings_comp:
                set_list.append({'setting': settings_comp,
                                 'order': OR_settings[setname]['order']})
    ordered_set_list = [item['setting'] for item in sorted(set_list,
                        key=lambda d: d['order'])]
    return ordered_set_list


class OpenRTSPTimedMonitor(Thread):
    time_last_delta_thresh = 2.5
    run_over_grace = 1.0
    parent_create_lock = Lock()

    def __init__(self, name, client_settings, env):
        print('OpenRTSPTimedMonitor.init ...')
        super(OpenRTSPTimedMonitor, self).__init__(group=None)
        self.settings = client_settings
        self.duration = 0.0 + self.settings['duration']
        self.duration_original = self.duration
        self.env = env
        self.__name__ = name
        self.client = None
        self.stdout = None
        self.stderr = None
        self.edition = 0
        self.size_anomaly = False
        self.time_start = time.time()
        self.now = datetime.datetime.now()

    def log(self, level, event, msg):
        FWLogger.log(level, self.settings['cameraId'],
                     '%s_%s' % (self.now.strftime('%Y%m%d'),
                                self.now.strftime('%H%M%S')),
                     event, msg)

    def set_size_anomaly_time(self):
        now_ts = time.time()
        if self.size_anomaly_time_start is not None:
            # print('File size did not change: %d\t%f\t%s' % (self.size_last,
            #       now_ts, self.settings['output_pathname']) )
            if now_ts-self.size_anomaly_time_start >\
                    self.time_last_delta_thresh:
                self.size_anomaly = True
                self.log(FWLogger.L_INFO, FWLogger.E_STALLED,
                         "Stream stalled at %d of %d secs." %
                         (now_ts-self.time_start, self.duration))
                print("RESTART! (%f / %f) %s" % (now_ts -
                      self.size_anomaly_time_start,
                      now_ts - self.time_start,
                      self.settings['output_pathname']))

        else:
            self.size_anomaly_time_start = now_ts

    def reset_size_anomaly_time(self):
        self.size_anomaly_time_start = None

    def status_check(self):
        if not os.path.exists(self.settings['output_pathname']):
            self.set_size_anomaly_time()
        else:
            size_now = os.path.getsize(self.settings['output_pathname'])
            if size_now == 0:
                self.set_size_anomaly_time()
            else:
                delta = size_now - self.size_last
                self.size_last = size_now
                file_size_changed = delta != 0
                if not file_size_changed:
                    self.set_size_anomaly_time()
                else:
                    self.time_last_delta = time.time()
                    self.reset_size_anomaly_time()

    def make_parent_path(self, pathname):
        parent_path = os.path.dirname(pathname)
        if OpenRTSPTimedMonitor.parent_create_lock.acquire():
            try:
                if not os.path.exists(parent_path):
                    os.makedirs(parent_path)
            finally:
                OpenRTSPTimedMonitor.parent_create_lock.release()

    def invoke_openRTSP(self, kind=FWLogger.E_START_CRON):
        flat_settings = extrude_settings(OR_settings, self.settings)
        print('Popen: %s [%s]' % (' '.join(flat_settings),
                                  self.settings['output_pathname']))
        self.make_parent_path(self.settings['output_pathname'])
        self.output_fh = open(self.settings['output_pathname'], 'wb')
        self.client = sp.Popen(args=flat_settings, stdout=self.output_fh,
                               stderr=sp.PIPE, shell=False)
        self.stdout = self.client.stdout
        self.stderr = self.client.stderr
        self.log(FWLogger.L_INFO, kind,
                 "Stream started, duration %d secs." %
                 self.duration)

    def get_openRTSP_response(self):
        return {'stderr': self.stderr.read()}

    def prep_client_session(self, duration):
        self.size_last = 0
        self.time_last_delta = time.time()
        self.size_anomaly_time_start = None
        self.size_anomaly = False
        self.settings['duration'] = duration
        self.settings['output_pathname'] =\
            '%s/%s' % (self.env["video_output_folder"],
                       self.env["video_filename_template"] % (
                    self.now.strftime('%Y'),
                    self.now.strftime('%m'),
                    self.now.strftime('%d'),
                    self.settings['cameraId'],
                    self.now.strftime('%Y%m%d'),
                    self.now.strftime('%H%M%S'),
                    self.now.strftime('%s'),
                    self.edition,
                    duration))
        self.settings['logfile_pathname'] =\
            '%s/%s' % (self.env["openRTSP_logfile_folder"],
                       self.env["openRTSP_logfile_template"] % (
                    self.now.strftime('%Y'),
                    self.now.strftime('%m'),
                    self.now.strftime('%d'),
                    self.settings['cameraId'],
                    self.now.strftime('%Y%m%d'),
                    self.now.strftime('%H%M%S'),
                    self.now.strftime('%s'),
                    self.edition,
                    duration))

    def cleanup_client(self, self_terminated):
        log = self.get_openRTSP_response()
        self.make_parent_path(self.settings['logfile_pathname'])
        with open(self.settings['logfile_pathname'], 'w') as f:
            f.write(log['stderr'])
        # Time is up but openRTSP client still running, so kill it
        if not self_terminated:
            self.client.terminate()
        self.output_fh.flush()
        self.output_fh.close()
        return log

    def run(self):
        self.prep_client_session(self.duration_original)
        self.invoke_openRTSP()
        time_check_freq = 1/30.0
        self_terminated = False
        while(time.time() < self.time_start + self.duration +
              self.run_over_grace):
            self_terminated = self.client.poll() is not None
            time.sleep(time_check_freq)
            self.status_check()
            if (self_terminated and time.time() < self.time_start +
                    self.duration) or self.size_anomaly:
                if self_terminated:
                    print("self-terminate time: %f < %f = %f" % (time.time(),
                          self.time_start + self.duration +
                          self.run_over_grace,
                          time.time() - (self.time_start + self.duration +
                                         self.run_over_grace)))
                # a) Client self-terminated EARLY, or-
                # b) video output file no longer grows.
                # Kill the openRTSP client and restart
                stderr_log = self.cleanup_client(self_terminated)

                # Deduct time elapsed so far, to time-box the next session
                # , self.settings['duration'] - time.time()<self.time_start)
                self.edition += 1
                dura = self.duration
                self.duration -= (time.time()-self.time_start)
                print('Orig duration: %f. Elapsed: %f. Remaining: %f. ' +
                      'New duration: %f' % (
                        dura, time.time() - self.time_start,
                        dura -
                        (time.time() - self.time_start), self.duration))
                if self.duration >= 1:
                    self.prep_client_session(duration=self.duration)
                    self.invoke_openRTSP(kind=FWLogger.E_START_RESTART)

        if self_terminated:
            self.log(FWLogger.L_INFO, FWLogger.E_END_CRON,
                     "Stream terminated, duration %d secs." %
                     self.duration)
            print("CLIENT SELF-TERMINATED %f " % (time.time()-self.time_start))
        else:
            self.log(FWLogger.L_INFO, FWLogger.E_END_CRON,
                     "Stream terminated, duration %d secs." %
                     self.duration)
            print("TIMED EXIT %f ... %f" % (
                # Elapsed time
                time.time()-self.time_start,
                # Remaining time
                time.time() - (self.time_start + self.duration +
                               self.run_over_grace)))
        stderr_log = self.cleanup_client(self_terminated)
        return stderr_log

    def __str__(self):
        return '(%s) %s: %s' % (self.now.strftime("%D %T.%f"), self.__name__,
                                str(self))

    def __call__(self):
        result = self.run()
