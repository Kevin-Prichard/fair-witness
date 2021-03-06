from types import NoneType

OR_settings = {
    'pathname': {'key': None, 'type': str, 'tmpl': ['{val}'], 'order': -10**9,
                 'msg': 'Pathname to openRTSP executable, must come first'},
    'tcp': {'key': 't', 'type': NoneType, 'tmpl': ['-{key}'], 'order': 80,
            'msg': 'Transmit over TCP'},
    'udp': {'key': '', 'type': NoneType, 'tmpl': [''], 'order': 80,
            'msg': 'Transmit over UDP (default)'},
    'abort': {'key': 'D', 'type': int, 'tmpl': ['-{key}', '{val: d}'],
              'order': 5, 'msg': 'Abort after N seconds dropped output'},
    'buffer_in': {'key': 'B', 'type': int, 'tmpl': ['-{key}', '{val: d}'],
                  'order': 10, 'msg': 'Input buffer (bytes)'},
    'buffer_out': {'key': 'b', 'type': int, 'tmpl': ['-{key}', '{val: d}'],
                   'order': 20, 'msg': 'Output buffer (bytes)'},
    'quicktime': {'key': 'q', 'type': NoneType, 'tmpl': ['-{key}'],
                  'order': 30, 'msg': 'Output in QuickTime MOV format'},
    'mp4': {'key': '4', 'type': NoneType, 'tmpl': ['-{key}'], 'order': 30,
            'msg': 'Use the MP4 container format when writing video to file'},
    'avi': {'key': 'i', 'type': NoneType, 'tmpl': ['-{key}'], 'order': 30,
            'msg': 'Use the AVI container format when writing video to file'},
    'qos': {'key': 'Q', 'type': NoneType, 'tmpl': ['-{key}'], 'order': 40,
            'msg': 'Output QOS statistics'},
    'quiet': {'key': 'V', 'type': NoneType, 'tmpl': ['-{key}'], 'order': 40,
              'msg': 'Less verbose'},
    'duration': {'key': 'd', 'type': float, 'tmpl': ['-{key}', '{val: f}'],
                 'order': 60, 'msg': 'Overall capture duration'},
    'file_dur': {'key': 'P', 'type': float, 'tmpl': ['-{key}', '{val: f}'],
                 'order': 70, 'msg': 'Per-file duration'},
    'file_prefix': {'key': 'F', 'type': str, 'tmpl': ['-{key}', '{val}'],
                    'order': 50,
                    'msg': 'Prefix output filenames with this value'},
    'credentials': {'key': 'u', 'type': dict, 'tmpl': ['-{key}', '{username}',
                    '{password}'], 'order': 90,
                    'msg': 'Username and password string'},
    'url': {'key': '', 'type': dict, 'tmpl': ['rtsp: //{host}: {port}{path}'],
            'order': 1000,
            'msg': 'URL to the AV resource (rtsp://hostname:port/path)'},
    'video_width': {'key': 'w', 'type': int, 'tmpl': ['-{key} {val: d}'],
                    'order': 53, 'msg': 'Width of the video image area'},
    'video_height': {'key': 'h', 'type': int, 'tmpl': ['-{key} {val: d}'],
                     'order': 54, 'msg': 'Height of the video image area'},
    'video_fps': {'key': 'f', 'type': int, 'tmpl': ['-{key} {val: d}'],
                  'order': 54, 'msg': 'Framerate of the source video stream'},
    'output_pathname': {'key': None, 'type': str, 'tmpl': [], 'order': 10**9,
                        'msg': 'Empty def in lieu of refactor'},
    'logfile_pathname': {'key': None, 'type': str, 'tmpl': [], 'order': 10**9,
                         'msg': 'Empty def in lieu of refactor'},
    # Placeholder definitions: these settings are not extruded to the CLI
    'cameraId': {'key': None, 'type': str, 'tmpl': '', 'order': 10**9,
                 'msg': 'Placeholder to allow <cameraId> to travel with ' +
                        'other settings, though it\'s not extruded to CLI'},
    'clip_length_secs': {'key': None, 'type': int, 'tmpl': '', 'order': 10**9,
                         'msg': 'Placeholder to allow <cameraId> to travel ' +
                                'with other settings, though it\'s not ' +
                                'extruded to CLI'},
}
