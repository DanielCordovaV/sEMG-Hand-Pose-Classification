
import myo
from collections import deque


class EmgCollector(myo.DeviceListener):
  def __init__(self):
    self.emg_data = []

  def on_paired(self, event):
    event.device.vibrate(myo.VibrationType.short)

  def on_unpaired(self, event):
    return False

  def on_connected(self, event):
    event.device.stream_emg(True)

  def on_emg(self, event):
    self.emg_data = event.emg

  def get_EMG(self):
    return self.emg_data