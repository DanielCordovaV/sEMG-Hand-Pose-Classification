import os
import numpy as np
import pandas as pd

ROOT = os.getcwd()
LABELS = os.listdir(os.path.join(ROOT, 'myo_data'))
NB_CHANNELS = 8
LABEL_DIRS = {label: os.path.join(ROOT, 'myo_data', label) for label in LABELS}
LABEL_FILES = {label: [os.path.join(ROOT, 'myo_data', label, file) for file in os.listdir(os.path.join(ROOT, 'myo_data', label))] for label in LABELS}
SAMPLES = [f'ch{channel}_sample_{sample}' for channel in range(1,NB_CHANNELS + 1)  for sample in range(1,51) ]
LABEL_DFS = {key: pd.DataFrame(np.array([pd.read_csv(file).transpose().values.flatten() for file in LABEL_FILES[key]]), columns=SAMPLES) for key in LABELS}
for key in LABELS:
    LABEL_DFS[key] = LABEL_DFS[key].reindex(np.random.permutation(LABEL_DFS[key].index))
    LABEL_DFS[key]['label'] = np.repeat(key, LABEL_DFS[key].shape[0])
train = pd.concat([LABEL_DFS[label].iloc[:int(LABEL_DFS[label].shape[0]*.75)] for label in LABELS], sort=False, ignore_index=True)
train = train.reindex(np.random.permutation(train.index))
test = pd.concat([LABEL_DFS[label].iloc[int(LABEL_DFS[label].shape[0]*.75):] for label in LABELS], sort=False, ignore_index=True)
test = test.reindex(np.random.permutation(test.index))
train.to_csv('train.csv', index=False)
test.to_csv('test.csv', index=False)