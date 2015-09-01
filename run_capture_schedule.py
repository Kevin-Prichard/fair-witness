#!/usr/bin/env python

import os
import sys
import copy
import signal
import schedule
import threading
from datetime import datetime
import time
from rtspRunner import merge_settings, extrude_settings, OpenRTSPTimedMonitor
from configs.OR_settings_template import OR_settings
from configs.vary import my_settings_vary
from configs.static import my_settings_static
from configs.cameras import cameras
from configs.env import pathnames as env
from configs.capture_sched import capture_schedules


def signal_handler(signal, frame):
    threading.enumerate
    print "SIGINT receivied, terminating."
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)


def run_cameras(cameras, OR_settings, my_settings_static, my_settings_vary):
    runcount = 0
    schedule_default = 'quarter hour'
    settings_variations = merge_settings(OR_settings, my_settings_static,
                                         my_settings_vary, cameras)
    for settings in settings_variations:
        camera_names = cameras.keys()
        camera_threads = {}
        for cam_handle in camera_names:
            session_settings = copy.deepcopy(settings)
            session_settings['url'] = cameras[cam_handle]
            session_settings['credentials'] = \
                cameras[cam_handle]['credentials']
            # session_settings['video_width'] = \
            #    cameras[cam_handle]['media']['video_width']
            # session_settings['video_height'] = \
            #    cameras[cam_handle]['media']['video_height']
            # session_settings['video_fps'] = \
            #    cameras[cam_handle]['media']['video_fps']
            session_settings['cameraId'] = cam_handle
            if 'overrides' in cameras[cam_handle]:
                session_settings.update(cameras[cam_handle]['overrides'])

            schedule_this = cameras[cam_handle]['schedule'] \
                if 'schedule' in cameras[cam_handle] else schedule_default
            sched = capture_schedules[schedule_this]
            task = sched['run_target'](params=sched,
                                       client_settings=session_settings,
                                       env=env)
            # 1. Schedule the task - it runs *after* 'duration' seconds, so...
            schedule.every(sched['duration']).seconds.do(task)
            # 2. We run the task straightaway, to cover the 'duration' gap
            task()
            runcount += 1

    while(True):
        schedule.run_pending()
        time.sleep(1)

        """
        for cam_handle in camera_threads:
            print cam_handle
            camera_threads[cam_handle].join()
        """


run_cameras(cameras, OR_settings, my_settings_static, my_settings_vary)


"""
camera_threads[cam_handle] = OpenRTSPExecMonitor(args=settings_flattened,
                                 name=session_settings['file_prefix'])
camera_threads[cam_handle].start()
session_settings['file_prefix'] = '%s_%s_%s' % (cam_handle,
    session_settings['file_prefix'],
    datetime.now().strftime("%Y%m%d_%H%M%S.%f"))
settings_flattened = extrude_settings(OR_settings, session_settings)
"""
