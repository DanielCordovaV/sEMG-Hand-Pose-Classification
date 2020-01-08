from time import time
from myo import init, Hub
from EmgCollector import EmgCollector

if __name__ == '__main__':
  init()
  hub = Hub()
  collector = EmgCollector()
  i = 0
  while hub.run(collector.on_event, 5):
      emg = collector.get_EMG()
      if emg == []:
          continue
      i += 1
      print(emg)
      if i == 50:
          break