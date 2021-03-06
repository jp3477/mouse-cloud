"""Models for objects in the runner database.

Note: avoid using nullable charfields throughout. This creates two
possible values for NULL: Null/None, and ''. The django convention is to use
''. Other code will interpret '' as equivalent to "not specified", so
do not attempt to store the empty string as a meaningful value.

At the moment all C parameters are required to be CharFields because they
need to be strings, but perhaps it would be better to have allow other types
(eg BooleanField) and then convert before writing to the Autosketch.
"""

from __future__ import unicode_literals

from django.db import models

def get_latest_daily_plan():
    return None


class Mouse(models.Model):
    name = models.CharField(max_length=20)
    
    # Python params
    stimulus_set = models.CharField(max_length=50)
    step_first_rotation = models.IntegerField()
    timeout = models.IntegerField(null=True, blank=True)
    scheduler = models.CharField(max_length=50)
    max_rewards_per_trial = models.IntegerField(default=1)
    
    # build params
    protocol_name = models.CharField(max_length=50)
    script_name = models.CharField(max_length=50)
    default_board = models.CharField(max_length=50, null=True, blank=True)
    default_box = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return str(self.name)

class Box(models.Model):
    """Hardware info about individual boxes"""
    name = models.CharField(max_length=20)
    l_reward_duration = models.IntegerField()
    r_reward_duration = models.IntegerField(null=True, blank=True)
    serial_port = models.CharField(max_length=20)
    video_device = models.CharField(max_length=20, null=True, blank=True)
    
    video_window_position_x = models.IntegerField(null=True, blank=True)
    video_window_position_y = models.IntegerField(null=True, blank=True)
    gui_window_position_x = models.IntegerField(null=True, blank=True)
    gui_window_position_y = models.IntegerField(null=True, blank=True)
    window_position_IR_plot_x = models.IntegerField(null=True, blank=True)
    window_position_IR_plot_y = models.IntegerField(null=True, blank=True)
    subprocess_window_ypos = models.IntegerField(null=True, blank=True)
    
    video_brightness = models.IntegerField(null=True, blank=True)
    video_gain = models.IntegerField(null=True, blank=True)
    video_exposure = models.IntegerField(null=True, blank=True)
    
    @property
    def video_window_position(self):
        return (self.video_window_position_x, self.video_window_position_y)
    @video_window_position.setter
    def video_window_position(self, obj):
        self.video_window_position_x = obj[0]
        self.video_window_position_y = obj[1]

    @property
    def gui_window_position(self):
        return (self.gui_window_position_x, self.gui_window_position_y)
    @gui_window_position.setter
    def gui_window_position(self, obj):
        self.gui_window_position_x = obj[0]
        self.gui_window_position_y = obj[1]

    @property
    def window_position_IR_plot(self):
        return (self.window_position_IR_plot_x, self.window_position_IR_plot_y)        
    @window_position_IR_plot.setter
    def window_position_IR_plot(self, obj):
        self.window_position_IR_plot_x = obj[0]
        self.window_position_IR_plot_y = obj[1]
    
    @property
    def mean_water_consumed(self):
        """Return mean water consumed over last N sessions"""
        return self.session_list[0].name

    def __str__(self):
        return str(self.name)
    
    class Meta:
        ordering = ['name']

class Board(models.Model):
    """Hardware info about individual boards"""
    name = models.CharField(max_length=20)
    
    has_side_HE_sensor = models.BooleanField()
    l_ir_detector_thresh = models.IntegerField(null=True, blank=True)
    r_ir_detector_thresh = models.IntegerField(null=True, blank=True)
    
    # This is both a Python parameter and a C parameter
    # Downstream logic will have to generate '1' for the C parameter
    use_ir_detector = models.NullBooleanField()
    
    # C parameters, need to be strings
    stepper_driver = models.CharField(max_length=10, null=True, blank=True)
    side_HE_sensor_thresh = models.CharField(max_length=10, null=True, blank=True)
    microstep = models.CharField(max_length=10, null=True, blank=True)
    invert_stepper_direction = models.CharField(max_length=10, 
        null=True, blank=True)
    
    def __str__(self):
        return str(self.name)

    class Meta:
        ordering = ['name']

class ArduinoProtocol(models.Model):
    """Info about the Arduino protocol, eg TwoChoice.ino"""
    name = models.CharField(max_length=20)
    path = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.name)

class PythonProtocol(models.Model):
    """Info about the Python code used to interact with an Aruduino protocol"""
    name = models.CharField(max_length=20)
    path = models.CharField(max_length=100)
    
    def __str__(self):
        return str(self.name)

class Session(models.Model):
    """Info about a single behavioral session"""
    # The name will be constructed from the date, mouse, etc
    name = models.CharField(max_length=200, primary_key=True)
    
    # Which mouse it was
    mouse = models.ForeignKey(Mouse)
    
    # The logfile
    logfile = models.CharField(max_length=200)

    # Where it physically took place
    # Note multiple boxes may share the same serial port
    board = models.ForeignKey(Board, null=True, blank=True)
    box = models.ForeignKey(Box, null=True, blank=True)
    
    # This is not necessary because it's part of box
    serial_port = models.CharField(max_length=50, null=True, blank=True)
    
    # The protocol that was run
    autosketch_path = models.CharField(max_length=200)
    script_path = models.CharField(max_length=200)
    
    # The sandbox where the protocol was compiled
    sandbox = models.CharField(max_length=200)
    
    # Protocol parameters
    python_param_scheduler_name = models.CharField(max_length=100,
        verbose_name='Scheduler', null=True, blank=True)
    python_param_stimulus_set = models.CharField(max_length=100,
        verbose_name='StimSet', null=True, blank=True)
    
    # Real-life parameters
    irl_param_stimulus_arm = models.CharField(max_length=100,
        verbose_name='StimArm', null=True, blank=True)
    
    # When it began and ended, maybe other stuff
    date_time_start = models.DateTimeField(null=True, blank=True,
        verbose_name='Start')
    date_time_stop = models.DateTimeField(null=True, blank=True,
        verbose_name='Stop')
    
    # Stuff the user provides
    user_data_water_pipe_position_start = models.FloatField(
        null=True, blank=True, verbose_name='Pipe Start')
    user_data_water_pipe_position_stop = models.FloatField(
        null=True, blank=True, verbose_name='Pipe Stop')
    user_data_left_water_consumption = models.FloatField(null=True, blank=True)
    user_data_right_water_consumption = models.FloatField(null=True, blank=True)
    user_data_left_valve_mean = models.FloatField(null=True, blank=True)
    user_data_right_valve_mean = models.FloatField(null=True, blank=True)
    user_data_left_perf = models.FloatField(null=True, blank=True,
        verbose_name='L perf')
    user_data_right_perf = models.FloatField(null=True, blank=True,
        verbose_name='R perf')
    user_data_bias_summary = models.CharField(max_length=100,
        null=True, blank=True, verbose_name='Bias')
    user_data_weight = models.FloatField(
        null=True, blank=True, verbose_name='Weight')

    def __str__(self):
        if self.name:
            return str(self.name)
        else:
            return 'Unstarted'
    
    def left_valve_summary(self):
        res = ''
        if self.user_data_left_water_consumption:
            res += '%0.2f' % self.user_data_left_water_consumption
        if self.user_data_left_valve_mean:
            res += u' @%0.1f \N{GREEK SMALL LETTER MU}L' % (
                1000 * self.user_data_left_valve_mean)
        return res
    left_valve_summary.short_description = 'L water'

    def right_valve_summary(self):
        res = ''
        if self.user_data_right_water_consumption:
            res += '%0.2f' % self.user_data_right_water_consumption
        if self.user_data_right_valve_mean:
            res += u' @%0.1f \N{GREEK SMALL LETTER MU}L' % (
                1000 * self.user_data_right_valve_mean)
        return res
    right_valve_summary.short_description = 'R water'
    
    def display_left_perf(self):
        try:
            return '%.0f' % (100 * self.user_data_left_perf)
        except:
            return 'NA'
    display_left_perf.short_description = 'L perf'

    def display_right_perf(self):
        try:
            return '%.0f' % (100 * self.user_data_right_perf)
        except:
            return 'NA'
    display_right_perf.short_description = 'R perf'
    
