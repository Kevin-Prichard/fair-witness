
my_settings_vary = {
    'network':  [{'tcp': None}],
    'abort': [{'abort': 5}],
    'duration': [{'duration': float(dur_secs)} for dur_secs in [915]],
    'clip_length_secs': [{'clip_length_secs': 915}],
    'file_format': [{'avi': None}],
    'qos': [{'qos': None}],
}

"""
my_settings_vary = {
#    'network':  [{'tcp': None}, {'udp': None}],
    'duration': [{'duration': float(dur_secs)} for dur_secs in [15, 30]],
    'file_dur': [{'file_dur': float(file_secs)} for file_secs in [15, 30]],
    'file_format': [{'quicktime': None}, {'mp4': None}, {'avi': None}],
    'qos': [{'qos': None}],
}

    # 'network':  [{'tcp': None}, {'udp': None}],
    # 'duration': [{'duration': float(dur_secs)} for dur_secs in [15]],
    # 'file_dur': [{'file_dur': float(file_secs)} for file_secs in [15]],
"""
