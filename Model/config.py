# -*- coding: utf-8 -*-
"""config.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Mw2DAWnbgqRRPqs-aGvfQny-vjcTloTc
"""

SEED = 42
MODEL_PATH = '/content/drive/MyDrive/scibert-pretrained2'
NUM_LABELS = 1

# data
TOKENIZER = AutoTokenizer.from_pretrained(MODEL_PATH)
MAX_LENGTH1 = 20
MAX_LENGTH2 = 200
MAX_LENGTH3 = 200
BATCH_SIZE = 8
VALIDATION_SPLIT = 0.15

# model
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
FULL_FINETUNING = True
LR = 2e-4
OPTIMIZER = 'AdamW'
# class_weight = torch.FloatTensor([2.0])
# CRITERION = torch.nn.BCEWithLogitsLoss(pos_weight=class_weight)
CRITERION = 'BCEWithLogitsLoss'
SAVE_BEST_ONLY = True
N_VALIDATE_DUR_TRAIN = 3
EPOCHS = 6