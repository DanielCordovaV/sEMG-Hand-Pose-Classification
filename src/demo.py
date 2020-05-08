from EmgCollector import EmgCollector
from myo import init, Hub
from collections import deque, Counter
import pandas as pd
import numpy as np
import sys, os
from tensorflow.keras.models import load_model
from scipy.signal import spectrogram
from time import sleep
import csv

'''Constants'''

LABELS = ['Flexion', 'Extension', 'Fist', 'Neutral']
NB_LABELS = len(LABELS)
NB_CHANNELS = 8
SAMPLE_RATE = 200
TIMES = list(range(0,200,10))
CHANNELS = [f'ch{n}' for n in range(1, NB_CHANNELS + 1)]

'''Setting workspace'''

os.chdir('..')
ROOT = os.getcwd()
model = load_model(os.path.join(ROOT, 'models', 'spec_model.h5'))

'''Globals'''

g_index = 0
g_ch_data = {ch: deque() for ch in CHANNELS}
noverlap = 8
actions = []
prev_action = 4
ts = 10

'''Spectrogram hyperparameters'''

sg_shape = (6, 21, 8)
nperseg = 10 #increasing nperseg increases frequency resolution and decreases time res
noverlap = 8 #increasing time resolution requires increasing overlap
window = 'hann' #hann provides good time and frequency resolution properties

def buildSpectrogram(data):
    samp = np.zeros((1, *sg_shape))
    img = np.zeros(sg_shape)
    for i, ch in enumerate(data.keys()):
        _, _, spec = spectrogram(x=data[ch],
                                 fs=200,
                                 nperseg=nperseg,
                                 noverlap=noverlap,
                                 window=window)
        img[:,:,i] = spec
    samp[0] = img
    return(samp)


def predict(x, threshold):

    logits = model.predict(x)
    indexes = logits < threshold
    logits[indexes] = 0
    if logits.sum() > 0:
        pred = np.argmax(logits)
        return(LABELS[pred], logits[0, pred])
    else:
        return(LABELS[3], .42)

def collect_data(collector):
    global g_index, g_ch_data, prev_action

    emg = collector.get_EMG()
    if emg == []:
        return

    for n in range(1, NB_CHANNELS + 1):
        ch = f'ch{n}'
        if g_index >= 50:
            g_ch_data[ch].popleft()
        g_ch_data[ch].append(emg[n - 1])

    g_index += 1
    
    if g_index % 200 in TIMES and g_index >= 50:
        x = buildSpectrogram(pd.DataFrame(g_ch_data))
        action, confidence = predict(x, .65)
        actions.append(action)
        if len(actions) > ts:
            del actions[0]
        sum_actions = np.concatenate([np.repeat(val,(ind + 1)) for ind, val in enumerate(actions)])
        c = Counter(sum_actions)
        value, _ = c.most_common()[0]
        action_index = LABELS.index(value)
        print(' '*80, end="\r")
        print(f'Action: {value} Confidence: {confidence*100:.1f}%', end="\r")
        prev_action = action_index

if __name__ == "__main__":
    print('--------------------')
    print("-- MYO  Collector --")
    print('--------------------')
    print('--------------------')

    init()
    hub = Hub()
    collector = EmgCollector()

    while hub.run(collector.on_event, 1):
        collect_data(collector)