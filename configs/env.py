import re

app_name = "Fair Witness"
app_name_safe = re.sub('\W+', '_', app_name)
app_name_short = "fairwit"
prefix_vid = "/mnt/raid/S8/fairwit/video"
prefix_log = "/mnt/raid/S8/fairwit/log"
global_log_filename = "%s.log" % app_name_safe
pathnames = {
    "global_log_filename": global_log_filename,
    "prefix_vid": prefix_vid,
    "prefix_log": prefix_log,
    "app_name_safe": app_name_safe,
    "video_output_folder": prefix_vid,
    # date, time, epoch, cameraId, seconds duration, edition
    "video_filename_template": "%s/%s/%s/video_%s_%s_%s_%s_%d_%d.avi",
    "openRTSP_logfile_folder": prefix_log,
    "openRTSP_logfile_template": "%s/%s/%s/video_%s_%s_%s_%s_%d_%d.log",
}
