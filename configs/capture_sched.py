import copy
from types import NoneType
from rtspRunner import OpenRTSPTimedMonitor
import schedule

"""
camera info
static info
variable info

merge settings

every N send merged settings to run on monitored thread
#cameras+static+vary & capture_schedule => run
"""


class RunTimedMonitor(object):
    def __init__(self, params, client_settings, env):
        self.settings(params=params, client_settings=client_settings, env=env)

    def settings(self, params, client_settings, env):
        print "RunTimedMonitor.settings..."
        self.client_settings = copy.deepcopy(client_settings)
        self.ThreadClass = params['thread_class']
        self.env = env
        self.__name__ = params['run_target'].__name__

    def __call__(self):
        print "*** DURATION: %f ***" % self.client_settings['duration']
        settings_copy = copy.deepcopy(self.client_settings)
        thread = self.ThreadClass(name='sesssion',
                                  client_settings=settings_copy, env=self.env)
        thread.start()


capture_schedules = {
    'quarter hour': {
        'duration': 900,
        'run_target': RunTimedMonitor,
        'thread_class': OpenRTSPTimedMonitor,
    },
    'minute': {
        'duration': 60,
        'run_target': RunTimedMonitor,
        'thread_class': OpenRTSPTimedMonitor,
    },
}
