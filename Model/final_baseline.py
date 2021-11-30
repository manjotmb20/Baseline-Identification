# -*- coding: utf-8 -*-
"""scibert_han_change2 (1).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1Y9dade-nX5A2fVO-rZ-9CwjErzvZb7Yu
"""

import re

import pickle
context=pickle.load(open("Model/Data/reduced_context.pkl",'rb'))

import pickle
context2=pickle.load(open("Model/Data/all_contexts.pkl",'rb'))

location_feature = pickle.load(open("Model/Data/location_feature.pkl","rb"))
title_overlap = pickle.load(open("Model/Data/title_overlap.pkl","rb"))
popularity = pickle.load(open("Model/Data/popularity_feat.pkl", "rb"))
# paper_info = pickle.load(open("Model/Data/paper_info (1).pickle", "rb"))
num_table = pickle.load(open("Model/Data/num_tables.pkl","rb"))
context_count = pickle.load(open("Model/Data/context_count.pkl","rb"))
weighted_cue = pickle.load(open("Model/Data/weighted_cue_words.pkl", "rb"))

output = []
count = 0
extra = []
for key in context :
    for paper in context[key] :
        output.append(paper['tag'])
        extra_val = []
        name = paper['paper_name']
        for pap in location_feature[key] :
            if(pap['paper_name']==name) :
                extra_val.extend(pap['location_feature'])
                break
            
        for pap in title_overlap[key] :
            if(pap['paper_name']==name) :
                extra_val.append(pap['overlap'])
                break

        for pap in popularity[key] :
            if(pap['paper_name']==name) :
                extra_val.append(pap['popularity'])
                break


        for pap in num_table[key] :
            if(pap['paper_name']==name) :
                extra_val.append(pap['num_table'])
                break

        for pap in weighted_cue[key] :
            if(pap['paper_name']==name) :
                max_data = pap['cue_weights_max']
                data_wcue = []
                for key1 in max_data :
                    data_wcue.append(max_data[key1])
                extra_val.extend(data_wcue)
                break

#         for pap in language_mod[key] :
#             if(pap['paper_name']==name) :
#                 extra_val.append(pap['lmp'])
#                 break

        for pap in context_count[key]:
            if(pap['paper_name']==name) :
                extra_val.append(pap['context_count'])
                break
                
        extra.append(extra_val) 
                
        count+=1
print(count)
print(len(extra)) #extra has 53 features for all the contexts

data=[]
tag=[]
title=[]
emb_text=[]

count=0
for key in context.keys():
  for paper in context[key]:
    title.append(paper['paper_name'])
    data.append(paper['context'])
    tag.append(paper['tag'])
    # emb_text.append(model([paper['paper_name']+" "+paper['context']])[0].numpy().tolist())
    count=count+1

import tensorflow as tf
import tensorflow_hub as hub
import numpy as np

# module_url = "https://tfhub.dev/google/universal-sentence-encoder/4" 
# model = hub.load(module_url)
# print ("module %s loaded" % module_url)

data2=[]
tag2=[]
title2=[]

count=0
for key in context.keys():
    i=0
    for paper in context[key]:
      try:
        if paper['paper_name']==context2[key][i]['paper_name']:
            title2.append(paper['paper_name'])
            try:
                data2.append(context2[key][i]['context'][0])
            except:
                data2.append('')
            tag2.append(paper['tag'])
      except:
        data2.append('')
        tag2.append(0)
      i=i+1  
      count=count+1

!pip install transformers

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
import re
import copy
from tqdm.notebook import tqdm
import gc

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch import optim
from torch.utils.data import Dataset, DataLoader,WeightedRandomSampler

from sklearn.metrics import (
    accuracy_score, 
    f1_score, 
    classification_report
)

from transformers import (
    AutoTokenizer, 
    AutoModel,
    get_linear_schedule_with_warmup
)

import pandas as pd
df=pd.DataFrame()
df['TITLE']=title
df['ABSTRACT']=data
df['CONTEXT']=data2
# df['text_vector']=emb_text
df['Extra']=extra
df['tag']=tag

for i in range(len(df)):
  df['ABSTRACT'][i]=df['TITLE'][i]+' '+df['ABSTRACT'][i]

cont=[]
c_len=[]
for i in range(len(df)):
  cont.append(df['ABSTRACT'][i].split(". "))
  c_len.append(len(df['ABSTRACT'][i].split(". ")))
df['cont']=cont

for i in range(len(df)):
  df['ABSTRACT'][i]=re.sub(r'\([\da-z\wA-z\s,-/+|]*\s*[\da-z\wA-z\s,-/+|]*\s*\)*', '_citation_', df['ABSTRACT'][i])

for i in range(len(df)):
  df['ABSTRACT'][i]=re.sub(r'[0-9]+', '', df['ABSTRACT'][i])

df=df[['TITLE','ABSTRACT','CONTEXT','Extra','cont','tag']]

# df2=pd.DataFrame()
# df2['text']=df['ABSTRACT'].to_list()

import string

def preprocess(df):
    df.insert(1,'Processed Post', np.zeros(len(df),dtype=str))
    for i in range(len(df)):
        text = df['ABSTRACT'][i]
        text = text.lower()
        # ### Converting Every URL to https://someurl
        text = re.sub('http[a-zA-Z0-9./:]*', 'https://someurl',text)
        
        # ### Converting Every User Mention to @Someuser
        text = re.sub('#[a-zA-Z0-9_]*', '#someuser', text)
        
    
        
        # ### Removing Punctuations
        table = str.maketrans("","", string.punctuation)
        text = text.translate(table)



        df.at[i,'Processed Post'] = text

    return df

import string

df=preprocess(df)

df['ABSTRACT']=df['Processed Post']

df.drop(labels=['Processed Post'],axis=1,inplace=True)

# df2.to_csv('baseline2.txt',header=False,index=False)

test_df=df[44833:]
train_df=df[:44833]

def clean_text(text):
    # text = text.split()
    # text = [x.strip() for x in text]
    # text = [x.replace('\n', ' ').replace('\t', ' ') for x in text]
    # text = ' '.join(text)
    # text = re.sub('([.,!?()])', r'  ', text)
    return text
    

def get_texts(df):
    titles = df['TITLE'].apply(clean_text)
    titles = titles.values.tolist()
    abstracts = df['ABSTRACT'].apply(clean_text)
    abstracts = abstracts.values.tolist()
    contexts = df['CONTEXT'].apply(clean_text)
    contexts = contexts.values.tolist()
    extra=df['Extra'].tolist()
    cont=df['cont'].values.tolist()
    return titles, abstracts,contexts,extra,cont


def get_labels(df):
    labels = df.iloc[:, 5:].values
    return labels

titles, abstracts,contexts,extra,cont = get_texts(train_df)
labels = get_labels(train_df)


for t, a,c,e, l in zip(titles[:5], abstracts[:5],contexts[:5],extra[:5], labels[:5]):
    print(f'TITLE -\t{t}')
    print(f'ABSTRACT -\t{a}')
    print(f'CONTEXT -\t{c}')
    print(f'Extra -\t{e}')
    print(f'LABEL -\t{l}')
    print('_' * 80)
    print()

class Config:
    def __init__(self):
        super(Config, self).__init__()

        self.SEED = 42
        self.MODEL_PATH = 'allenai/scibert_scivocab_uncased'
        self.NUM_LABELS = 1

        # data
        self.TOKENIZER = AutoTokenizer.from_pretrained(self.MODEL_PATH)
        self.MAX_LENGTH1 = 20
        self.MAX_LENGTH2 = 200
        self.MAX_LENGTH3 = 200
        self.BATCH_SIZE = 8
        self.VALIDATION_SPLIT = 0.15

        # model
        self.DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.FULL_FINETUNING = True
        self.LR = 2e-5
        self.OPTIMIZER = 'AdamW'
        # class_weight = torch.FloatTensor([2.0])
        # self.CRITERION = torch.nn.BCEWithLogitsLoss(pos_weight=class_weight)
        self.CRITERION = 'BCEWithLogitsLoss'
        self.SAVE_BEST_ONLY = True
        self.N_VALIDATE_DUR_TRAIN = 3
        self.EPOCHS = 20

config = Config()

class Attention(nn.Module):
    def __init__(self, hidden_dim, seq_len):
        super(Attention, self).__init__()

        self.hidden_dim = hidden_dim
        self.seq_len = seq_len
        self.weight = nn.Parameter(nn.init.kaiming_normal_(torch.Tensor(hidden_dim, 1)))
        self.bias = nn.Parameter(torch.zeros(seq_len))

    def forward(self, inp):
        # 1. Matrix Multiplication
        x = inp.contiguous().view(-1, self.hidden_dim)
        u = torch.tanh_(torch.mm(x, self.weight).view(-1, self.seq_len) + self.bias)
        # 2. Softmax on 'u_{it}' directly
        a = F.softmax(u, dim=1)
        # 3. Braodcasting and out
        s = (inp * torch.unsqueeze(a, 2)).sum(1)
        return a, s

class TransformerDataset(Dataset):
    def __init__(self, df, indices, set_type=None):
        super(TransformerDataset, self).__init__()

        df = df.iloc[indices]
        self.titles, self.abstracts,self.contexts,self.extra,self.cont = get_texts(df)
        self.set_type = set_type
        if self.set_type != 'test':
            self.labels = get_labels(df)

        self.max_length1 = config.MAX_LENGTH1
        self.max_length2 = config.MAX_LENGTH2
        self.max_length3 = config.MAX_LENGTH3
        self.tokenizer = config.TOKENIZER

    def __len__(self):
        return len(self.titles)
    
    def __getitem__(self, index):

        # input=[]
        # mask=[]
        # for i in self.cont[index]:
        #   tokenized=tokenizer.encode_plus(i,max_length=config.MAX_LENGTH1,pad_to_max_length=True,truncation=True,return_attention_mask=True,return_token_type_ids=False,return_tensors='pt')
        #   input.append(tokenized['input_ids'].squeeze().long())
        #   mask.append(tokenized['attention_mask'].squeeze().long())
        # for j in range(len(self.cont[index]),max(c_len)):
        #   input.append(pad_t['input_ids'].squeeze().long())
        #   mask.append(pad_t['attention_mask'].squeeze().long())

        tokenized_titles = self.tokenizer.encode_plus(
            self.titles[index], 
            max_length=self.max_length1,
            pad_to_max_length=True,
            truncation=True,
            return_attention_mask=True,
            return_token_type_ids=False,
            return_tensors='pt'
        )
        input_ids_titles = tokenized_titles['input_ids'].squeeze()
        attention_mask_titles = tokenized_titles['attention_mask'].squeeze()
        
        tokenized_abstracts = self.tokenizer.encode_plus(
            self.abstracts[index], 
            max_length=self.max_length2,
            pad_to_max_length=True,
            truncation=True,
            return_attention_mask=True,
            return_token_type_ids=False,
            return_tensors='pt'
        )
        input_ids_abstracts = tokenized_abstracts['input_ids'].squeeze()
        attention_mask_abstracts = tokenized_abstracts['attention_mask'].squeeze()

        tokenized_contexts = self.tokenizer.encode_plus(
            self.contexts[index], 
            max_length=self.max_length3,
            pad_to_max_length=True,
            truncation=True,
            return_attention_mask=True,
            return_token_type_ids=False,
            return_tensors='pt'
        )
        input_ids_contexts = tokenized_contexts['input_ids'].squeeze()
        attention_mask_contexts = tokenized_contexts['attention_mask'].squeeze()

        

        if self.set_type != 'test':
            return {
                'titles': {
                    'input_ids': input_ids_titles.long(),
                    'attention_mask': attention_mask_titles.long(),
                },
                'abstracts': {
                    'input_ids': input_ids_abstracts.long(),
                    'attention_mask': attention_mask_abstracts.long(),
                },
                'contexts': {
                    'input_ids': input_ids_contexts.long(),
                    'attention_mask': attention_mask_contexts.long(),
                },
                # 'cont':{
                #     'input_ids':input,
                #     'attention_mask':mask,
                # },
                'extra':{
                    'extra':torch.Tensor(self.extra[index]).float(),
                },
                'labels': torch.Tensor(self.labels[index]).float(),
            }

        return {
            'titles': {
                'input_ids': input_ids_titles.long(),
                'attention_mask': attention_mask_titles.long(),
            },
            'abstracts': {
                'input_ids': input_ids_abstracts.long(),
                'attention_mask': attention_mask_abstracts.long(),
            },
            'contexts': {
                'input_ids': input_ids_contexts.long(),
                'attention_mask': attention_mask_contexts.long(),
            },
            # 'cont':{
            #     'input_ids':input,
            #     'attention_mask':mask,
            # },
            'extra':{
                    'extra':torch.Tensor(self.extra[index]).float(),
                }

        }

np.random.seed(config.SEED)

dataset_size = len(train_df)
indices = list(range(dataset_size))
split = int(np.floor(config.VALIDATION_SPLIT * dataset_size))
np.random.shuffle(indices)

train_indices, val_indices = indices[split:], indices[:split]

train_data = TransformerDataset(train_df, train_indices)
val_data = TransformerDataset(train_df, val_indices)

class SelfAttention(nn.Module):
    def __init__(self, attention_size, batch_first=False, non_linearity="tanh"):
        super(SelfAttention, self).__init__()

        self.batch_first = batch_first
        self.attention_weights = Parameter(torch.FloatTensor(attention_size))
        self.softmax = nn.Softmax(dim=-1)

        if non_linearity == "relu":
            self.non_linearity = nn.ReLU()
        else:
            self.non_linearity = nn.Tanh()

        init.uniform(self.attention_weights.data, -0.005, 0.005)

    def get_mask(self, attentions, lengths):
        """
        Construct mask for padded itemsteps, based on lengths
        """
        max_len = max(lengths.data)
        mask = Variable(torch.ones(attentions.size())).detach()

        if attentions.data.is_cuda:
            mask = mask.cuda()

        for i, l in enumerate(lengths.data):  # skip the first sentence
            if l < max_len:
                mask[i, l:] = 0
        return mask

    def forward(self, inputs, lengths):

        

        # inputs is a 3D Tensor: batch, len, hidden_size
        # scores is a 2D Tensor: batch, len
        scores = self.non_linearity(inputs.matmul(self.attention_weights))
        scores = self.softmax(scores)

 

        # construct a mask, based on the sentence lengths
        mask = self.get_mask(scores, lengths)

        # apply the mask - zero out masked timesteps
        masked_scores = scores * mask

        # re-normalize the masked scores
        _sums = masked_scores.sum(-1, keepdim=True)  # sums per row
        scores = masked_scores.div(_sums)  # divide by row sum

 

        # multiply each hidden state with the attention weights
        weighted = torch.mul(inputs, scores.unsqueeze(-1).expand_as(inputs))

        # sum the hidden states
        representations = weighted.sum(1).squeeze()

        return representations, scores

train_dataloader = DataLoader(train_data, batch_size=config.BATCH_SIZE)
val_dataloader = DataLoader(val_data, batch_size=config.BATCH_SIZE)

b = next(iter(train_dataloader))
for k, v in b.items():
  
    if k == 'titles' or k == 'abstracts' or k== 'contexts' or k=='extra':
        print(k)
        for k_, v_ in b[k].items():
            print(f'{k_} shape: {v_.shape}\n')
    else:
        print(f'{k} shape: {v.shape}')

class WeightDrop(nn.Module):
    def __init__(self, module, weights, dropout=0, variational=False):
        super(WeightDrop, self).__init__()
        self.module = module
        self.weights = weights
        self.dropout = dropout
        self.variational = variational
        self._setup()

    def _setup(self):
        for name_w in self.weights:
            w = getattr(self.module, name_w)
            del self.module._parameters[name_w]
            self.module.register_parameter(name_w + "_raw", nn.Parameter(w.data))

    def _setweights(self):
        for name_w in self.weights:
            raw_w = getattr(self.module, name_w + "_raw")
            w = None
            if self.variational:
                mask = torch.ones(raw_w.size(0), 1)
                if raw_w.is_cuda: mask = mask.cuda()
                mask = torch.nn.functional.dropout(mask, p=self.dropout, 
                training=self.training)
                w = nn.Parameter(mask.expand_as(raw_w) * raw_w)
            else:
                w = nn.Parameter(
                    torch.nn.functional.dropout(raw_w, p=self.dropout, 
                    training=self.training))
            setattr(self.module, name_w, w)

    def forward(self, *args):
        self._setweights()
        return self.module.forward(*args)

class LockedDropout(nn.Module):
    def __init__(self):
        super().__init__()

    def forward(self, x, dropout=0.5):
        if not self.training or not dropout:
            return x
        mask = x.data.new(1, x.size(1), x.size(2)).bernoulli_(
          1 - dropout) / (1 - dropout)
        mask = mask.expand_as(x)
        return mask * x

class AttentionWithContext(nn.Module):
    def __init__(self, hidden_dim):
        super(AttentionWithContext, self).__init__()

        self.attn = nn.Linear(hidden_dim, hidden_dim)
        self.contx = nn.Linear(hidden_dim, 1, bias=False)

    def forward(self, inp):
        u = torch.tanh_(self.attn(inp))
        a = F.softmax(self.contx(u), dim=1)
        s = (a * inp).sum(1)
        return a.permute(0, 2, 1), s

class WordAttnNet(nn.Module):
    def __init__(self, vocab_size=320, hidden_dim=768, padding_idx=1, embed_dim=768, 
        weight_drop=0.0, embed_drop=0.0, locked_drop=0.0, embedding_matrix=None):
        super(WordAttnNet, self).__init__()

        self.lockdrop = LockedDropout()
        self.embed_drop = embed_drop
        self.weight_drop = weight_drop
        self.locked_drop = locked_drop

        self.word_embed = nn.Embedding(vocab_size, embed_dim, padding_idx=padding_idx)
        self.rnn = nn.GRU(embed_dim, hidden_dim, bidirectional=True, batch_first=True)
        if weight_drop:
            self.rnn = WeightDrop(self.rnn, ["weight_hh_l0", "weight_hh_l0_reverse"],
                dropout=weight_drop)
        self.word_attn = AttentionWithContext(hidden_dim * 2)

    def forward(self, X, h_n):
        # print("Forward")
        # print(X.shape)
        # if self.embed_drop:
        #     embed = embedded_dropout(
        #         self.word_embed, X.long(), dropout=self.embed_drop if self.training else 0
        #     )
        # else:
        #     embed = self.word_embed(X.long())
        # if self.locked_drop:
        #     embed = self.lockdrop(embed, self.locked_drop)
        # print(embed.shape)    
        h_t, h_n = self.rnn(X, h_n)
        # print(h_t.shape)
        a, s = self.word_attn(h_t)
        # print("word_att")
        # print(a.shape)
        # print(s.shape)
        return a, s.unsqueeze(1), h_n

class SentAttnNet(nn.Module):
    def __init__(self, word_hidden_dim=768, sent_hidden_dim=384, padding_idx=1, 
        weight_drop=0.0):
        super(SentAttnNet, self).__init__()

        self.rnn = nn.GRU( word_hidden_dim * 2, sent_hidden_dim, bidirectional=True,
            batch_first=True)
        if weight_drop:
            self.rnn = WeightDrop(self.rnn, ["weight_hh_l0", "weight_hh_l0_reverse"],
                dropout=weight_drop)
        self.sent_attn = AttentionWithContext(sent_hidden_dim * 2)

    def forward(self, X):
        h_t, h_n = self.rnn(X)
        a, v = self.sent_attn(h_t)
        return a, v

class HierAttnNet(nn.Module):

    def __init__( self, vocab_size, maxlen_sent, maxlen_doc, word_hidden_dim=32,
        sent_hidden_dim=32, padding_idx=1, embed_dim=50, weight_drop=0.0, embed_drop=0.0,
        locked_drop=0.0, last_drop=0.0, embedding_matrix=None, num_class=4):
        super(HierAttnNet, self).__init__()

        self.word_hidden_dim = word_hidden_dim
        self.wordattnnet = WordAttnNet(vocab_size, word_hidden_dim, padding_idx, embed_dim,
            weight_drop, embed_drop, locked_drop, embedding_matrix)
        self.sentattnnet = SentAttnNet(word_hidden_dim, sent_hidden_dim, padding_idx,
            weight_drop)
        self.ld = nn.Dropout(p=last_drop)
        self.fc = nn.Linear(sent_hidden_dim * 2, num_class)

    def forward(self, X):
        x = X.permute(1, 0, 2)
        word_h_n = nn.init.zeros_(torch.Tensor(2, X.shape[0], self.word_hidden_dim))
        if use_cuda:
            word_h_n = word_h_n.cuda()
        word_a_list, word_s_list = [], []
        for sent in x:
            word_a, word_s, word_h_n = self.wordattnnet(sent, word_h_n)
            word_a_list.append(word_a)
            word_s_list.append(word_s)
        self.sent_a = torch.cat(word_a_list, 1)
        sent_s = torch.cat(word_s_list, 1)
        doc_a, doc_s = self.sentattnnet(sent_s)
        self.doc_a = doc_a.permute(0, 2, 1)
        return self.doc_a

class DualSciBert(nn.Module):
    def __init__(self):
        super(DualSciBert, self).__init__()

        self.kernel_1=2
        self.stride=1
        self.wordattnnet = WordAttnNet()
        self.sentattnnet = SentAttnNet()
        self.titles_model = AutoModel.from_pretrained(config.MODEL_PATH)
        self.abstracts_model = AutoModel.from_pretrained(config.MODEL_PATH,output_hidden_states=True)
        self.encoder_layer=nn.TransformerEncoderLayer(d_model=768, nhead=8)
        self.transformer_encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=6)
        self.contexts_model = AutoModel.from_pretrained(config.MODEL_PATH)
        self.attention_layer = Attention(768)
        self.att_in=Attention(768,200)
        self.lstm_in=nn.LSTM(768,64,batch_first=True,bidirectional=True)
        # self.lstm=nn.LSTM(768,384,bidirectional=True,batch_first=True)
        # self.lstm_title=nn.LSTM(768,384,bidirectional=True,batch_first=True)
        # self.cnn_1=nn.Conv1d(768,384,self.kernel_1,self.stride)
        # self.lstm_extra=nn.LSTM(53,32,batch_first=True)
        # self.maxpool=nn.MaxPool1d(3,3)
        # self.dropout = nn.Dropout(0.25)
        # self.e_linear=nn.Linear(53,32)
        # self.avgpool = nn.AvgPool1d(2, 2)
        # self.output_1=nn.Linear(2432,256)
        # self.output = nn.Linear(256, config.NUM_LABELS)
        self.toutput=nn.Linear(25600,128)
        self.gru=nn.GRU(300, 128, 1, batch_first=True)
        self.dropout = nn.Dropout(0.25)
        self.att_conv = Attention(192,128)
        self.att_lstm=Attention(768,200)
        self.tlstm=nn.LSTM(300,64,batch_first=True,bidirectional=True)
        self.lstm=nn.LSTM(768,64,batch_first=True,bidirectional=True)
        self.conv1=nn.Conv1d(200,128,2,2)
        self.e_linear=nn.Linear(53,32)
        self.pool1=nn.MaxPool1d(2,2)
        self.avgpool = nn.AvgPool1d(2, 2)
        self.output_cnn=nn.Linear(319488,128)
        self.output_lstm=nn.Linear(332800,128)
        self.output_1=nn.Linear(9984,256)
        self.output = nn.Linear(256, config.NUM_LABELS)

    def forward(
        self,
        input_ids_titles, 
        attention_mask_titles=None, 
        input_ids_abstracts=None,
        attention_mask_abstracts=None,
        # input_ids_contexts=None,
        # attention_mask_contexts=None,
        # extra_t=None,
        ):
        
        hidden_title,titles_features = self.titles_model(
            input_ids=input_ids_titles,
            attention_mask=attention_mask_titles
        ).values()
        titles_features = titles_features.unsqueeze(1)
        titles_features_pooled = self.avgpool(titles_features)
        titles_features_pooled = titles_features_pooled.squeeze(1)

        
        x,_=self.lstm_title(hidden_title)

        query_t=torch.unsqueeze(x,1)
        out_c,weights_c=self.attention_layer(x,hidden_title)
        print(hidden_title.shape)
        
        
        query_t=torch.unsqueeze(titles_features,1)
        out_c,weights_c=self.attention_layer(query_t,x)
        print(x.shape)


        
        extra=self.e_linear(extra_t)
        hidden_context,context_features = self.contexts_model(
            input_ids=input_ids_contexts,
            attention_mask=attention_mask_contexts
        ).values()

        
        x1=hidden_context.unsqueeze(0)
        # print(x.shape)
        word_h_n = nn.init.zeros_(torch.Tensor(2, context_features.shape[0], context_features.shape[1]))
        word_h_n = word_h_n.cuda()
        word_a_list, word_s_list = [], []
        # print("loop starts")
        for sent in x1:
            # print(sent.shape)
            word_a, word_s, word_h_n = self.wordattnnet(sent,word_h_n)
            word_a_list.append(word_a)
            word_s_list.append(word_s)
        
        # print("loop over")
        self.sent_cont = torch.cat(word_a_list, 1).squeeze(1)
        # print(self.sent_cont.shape)
        sent_s = torch.cat(word_s_list, 1)
        # print(sent_s.shape)
        doc_a1, doc_s1 = self.sentattnnet(sent_s)

        # input = hidden_context.transpose(1, 2).contiguous()
        # print(hidden_context.shape)
        # print(input.shape)
        # print("--------")
        cnn_output=self.cnn_1(input)
        cnn_o2 = cnn_output.transpose(1, 2).contiguous()
        # print(cnn_o2.shape)
        maxpool1=self.maxpool(cnn_o2)
        # print(cnn_o2.shape)
        # print(maxpool1.shape)
        context_o=torch.sum(maxpool1,2)
        print(context_o.shape)

        query_c=torch.unsqueeze(context_features,1)
        out_c,weights_c=self.attention_layer(query_c,hidden_context)
        # print(out.shape)
        context_features1=torch.squeeze(out_c,1)
        context_features1 = context_features1.unsqueeze(1)
        context_features_pooled = self.avgpool(context_features1)
        context_features_pooled = context_features_pooled.squeeze(1)

        l_out_c,l_h_c=self.lstm(hidden_context)
        q_c=torch.sum(l_out_c,2)


        hidden_abstract,abstracts_features,b = self.abstracts_model(
            input_ids=input_ids_abstracts,
            attention_mask=attention_mask_abstracts
        ).values()


        for i in range(len(b)):
          l=b[i].permute((1,0,2))
          l_out=self.transformer_encoder(l)
          l_out=l_out.permute((1,0,2))
          l_out=torch.relu(l_out)
          _,l_out=self.att_lstm(l_out)
          if i==0:
              l_out_l=l_out
          else:
              l_out_l=torch.cat((l_out_l,l_out),dim=1)

        for i in range(len(b)):
          l_out,_=self.lstm_in(b[i])
          l_out=torch.relu(l_out)
          _,l_out=self.att_in(l_out)
          if i==0:
              l_out_l=l_out
          else:
              l_out_l=torch.cat((l_out_l,l_out),dim=1)
        
        # # print(hidden_abstract.shape)
        # # print(abstracts_features.shape)
        # x2,x3=self.lstm(hidden_abstract)
        # # print(x2.shape)
        # # print(x3.shape)
        # # query_t_a=torch.unsqueeze(x2,1)
        # # out_c_a,weights_c_a=self.attention_layer(x2,hidden_abstract)
        
        x=hidden_abstract.unsqueeze(0)
        # print(x.shape)
        word_h_n = nn.init.zeros_(torch.Tensor(2, abstracts_features.shape[0], abstracts_features.shape[1]))
        word_h_n = word_h_n.cuda()
        word_a_list, word_s_list = [], []
        # print("loop starts")
        for sent in x:
            # print(sent.shape)
            word_a, word_s, word_h_n = self.wordattnnet(sent,word_h_n)
            # print(word_a.shape)
            # print(word_s.shape)
            # print(word_h_n.shape)
            word_a_list.append(word_a)
            word_s_list.append(word_s)
        
        # print("loop over")
        self.sent_abs = torch.cat(word_a_list, 1).squeeze(1)
        # print(self.sent_abs.shape)
        sent_s = torch.cat(word_s_list, 1)
        # print(sent_s.shape)
        doc_a, doc_s = self.sentattnnet(sent_s)
        # print(doc_s.shape)
        # print(doc_a.shape)
        # # print("Start")
        # # print(hidden_abstract.shape)
        # # print(abstracts_features.shape)
        query=torch.unsqueeze(abstracts_features,1)
        out,weights=self.attention_layer(query,hidden_abstract)
        print(out.shape)
        abstracts_features1=torch.squeeze(out,1)
        # print(abstracts_features1.shape)
        abstracts_features1 = abstracts_features1.unsqueeze(1)
        # print(abstracts_features1.shape)
        # print("END")
        abstracts_features_pooled = self.avgpool(abstracts_features1)
        # print("--++++")
        # print(abstracts_features_pooled.shape)
        abstracts_features_pooled = abstracts_features_pooled.squeeze(1)
        print("-----")
        print(abstracts_features_pooled.shape)
        l_out,l_h=self.lstm(hidden_abstract)
        q=torch.sum(l_out,2)
        
        
        x = self.dropout(combined_features2)
        x = self.output_1(x)
        x = self.output(x) 
        
        return x,self.sent_abs
        l_out_c,l_h_c=self.lstm(hidden_abstract)
        q_c=torch.sum(l_out_c,1)


        for i in range(len(b)):
          l_out,_=self.lstm(b[i])
          l=torch.sum(l_out,1)
          if i==0:
            q_c_l=l
          else:
            q_c_l=torch.cat((q_c_l,l),dim=1)


        for i in range(len(b)):
          l_out,_=self.lstm(b[i])
          l_out=torch.relu(l_out)
          _,l_out=self.att_lstm(l_out)
          if i==0:
              l_out_l=l_out
          else:
              l_out_l=torch.cat((l_out_l,l_out),dim=1)
        # # l_out_l=l_out_l.reshape(l_out_l.size(0),-1)
        # # q_lstm=self.output_lstm(l_out_l)


        for i in range(len(b)):
          c_out=self.conv1(b[i])
          c_out=torch.relu(c_out)
          c_out=self.pool1(c_out)
          _,c_out=self.att_conv(c_out)
          if i==0:
              c_out_l=c_out
          else:
              c_out_l=torch.cat((c_out_l,c_out),dim=1)
        c_out_l=c_out_l.reshape(c_out_l.size(0),-1)
        # q_conv=self.output_cnn(c_out_l)

        # # print(q_conv.shape)
        





        # print(l_out_c.shape)
        # print(q_c.shape)

        combined_features2 = torch.cat((
            q_c, 
            l_out_l), 
            dim=1
        )
        combined_features3 = torch.cat((
            combined_features2,
            c_out_l
            ), 
            dim=1
        )

        combined_features4 = torch.cat((
            combined_features3,
            emoji
            ), 
            dim=1
        )
        combined_features5 = torch.cat((
            combined_features4,
            lex
            ), 
            dim=1
        )
        print(combined_features3.shape)

        
        
        x = self.dropout(l_out_l)
        x = self.output_1(x)
        x = self.output(x) 
        
        return x

device = config.DEVICE
device

def val(model, val_dataloader, criterion):
    
    val_loss = 0
    true, pred = [], []
    
    # set model.eval() every time during evaluation
    model.eval()
    
    for step, batch in enumerate(val_dataloader):
        # unpack the batch contents and push them to the device (cuda or cpu).
        b_input_ids_titles = batch['titles']['input_ids'].to(device)
        b_attention_mask_titles = batch['titles']['attention_mask'].to(device)
        b_input_ids_abstracts = batch['abstracts']['input_ids'].to(device)
        b_attention_mask_abstracts = batch['abstracts']['attention_mask'].to(device)
        # b_input_ids_contexts = batch['contexts']['input_ids'].to(device)
        # b_attention_mask_contexts = batch['contexts']['attention_mask'].to(device)
        # b_extra=batch['extra']['extra'].to(device)
        b_labels = batch['labels'].to(device)

        # using torch.no_grad() during validation/inference is faster -
        # - since it does not update gradients.
        with torch.no_grad():
            # forward pass
            logits= model(
                b_input_ids_titles, 
                b_attention_mask_titles,
                b_input_ids_abstracts,
                b_attention_mask_abstracts,
                # b_input_ids_contexts,
                # b_attention_mask_contexts,
                # b_extra
            )
            
            # calculate loss
            loss = criterion(logits, b_labels)
            val_loss += loss.item()

            # since we're using BCEWithLogitsLoss, to get the predictions -
            # - sigmoid has to be applied on the logits first
            logits = torch.sigmoid(logits)
            logits = np.round(logits.cpu().numpy())
            labels = b_labels.cpu().numpy()
            
            # the tensors are detached from the gpu and put back on -
            # - the cpu, and then converted to numpy in order to -
            # - use sklearn's metrics.

            pred.extend(logits)
            true.extend(labels)

    avg_val_loss = val_loss / len(val_dataloader)
    print('Val loss:', avg_val_loss)
    print('Val accuracy:', accuracy_score(true, pred))

    val_micro_f1_score = f1_score(true, pred, average='micro')
    print('Val micro f1 score:', val_micro_f1_score)
    return val_micro_f1_score


def train(
    model, 
    train_dataloader, 
    val_dataloader, 
    criterion, 
    optimizer, 
    scheduler, 
    epoch
    ):
    
    # we validate config.N_VALIDATE_DUR_TRAIN times during the training loop
    nv = config.N_VALIDATE_DUR_TRAIN
    temp = len(train_dataloader) // nv
    temp = temp - (temp % 100)
    validate_at_steps = [temp * x for x in range(1, nv + 1)]
    
    train_loss = 0
    for step, batch in enumerate(tqdm(train_dataloader, 
                                      desc='Epoch ' + str(epoch))):
        # set model.eval() every time during training
        model.train()
        
        # unpack the batch contents and push them to the device (cuda or cpu).
        b_input_ids_titles = batch['titles']['input_ids'].to(device)
        b_attention_mask_titles = batch['titles']['attention_mask'].to(device)
        b_input_ids_abstracts = batch['abstracts']['input_ids'].to(device)
        b_attention_mask_abstracts = batch['abstracts']['attention_mask'].to(device)
        # b_input_ids_contexts = batch['contexts']['input_ids'].to(device)
        # b_attention_mask_contexts = batch['contexts']['attention_mask'].to(device)
        # b_extra=batch['extra']['extra'].to(device)
        b_labels = batch['labels'].to(device)

        # clear accumulated gradients
        optimizer.zero_grad()

        # forward pass
        logits = model(
            b_input_ids_titles, 
            b_attention_mask_titles,
            b_input_ids_abstracts,
            b_attention_mask_abstracts,
            # b_input_ids_contexts,
            # b_attention_mask_contexts,
            # b_extra
        )
        
        # calculate loss
        loss = criterion(logits, b_labels)
        train_loss += loss.item()

        # backward pass
        loss.backward()

        # update weights
        optimizer.step()
        
        # update scheduler
        scheduler.step()

        if step in validate_at_steps:
            print(f'-- Step: {step}')
            _ = val(model, val_dataloader, criterion)
    
    avg_train_loss = train_loss / len(train_dataloader)
    print('Training loss:', avg_train_loss)

def run():
    # setting a seed ensures reproducible results.
    # seed may affect the performance too.
    torch.manual_seed(config.SEED)

    criterion = nn.BCEWithLogitsLoss()
    
    # define the parameters to be optmized -
    # - and add regularization
    if config.FULL_FINETUNING:
        param_optimizer = list(model.named_parameters())
        no_decay = ["bias", "LayerNorm.bias", "LayerNorm.weight"]
        optimizer_parameters = [
            {
                "params": [
                    p for n, p in param_optimizer if not any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.001,
            },
            {
                "params": [
                    p for n, p in param_optimizer if any(nd in n for nd in no_decay)
                ],
                "weight_decay": 0.0,
            },
        ]
        optimizer = optim.AdamW(optimizer_parameters, lr=config.LR)

    num_training_steps = len(train_dataloader) * config.EPOCHS
    scheduler = get_linear_schedule_with_warmup(
        optimizer,
        num_warmup_steps=0,
        num_training_steps=num_training_steps
    )

    max_val_micro_f1_score = float('-inf')
    for epoch in range(config.EPOCHS):
        train(model, train_dataloader, val_dataloader, criterion, optimizer, scheduler, epoch)
        val_micro_f1_score = val(model, val_dataloader, criterion)

        if config.SAVE_BEST_ONLY:
            if val_micro_f1_score > max_val_micro_f1_score:
                best_model = copy.deepcopy(model)
                best_val_micro_f1_score = val_micro_f1_score

                model_name = 'scibertfft_dualinput_best_model_new'
                torch.save(best_model.state_dict(), model_name + '.pt')

                print(f'--- Best Model. Val loss: {max_val_micro_f1_score} -> {val_micro_f1_score}')
                max_val_micro_f1_score = val_micro_f1_score

    return best_model, best_val_micro_f1_score

model = DualSciBert()
model.to(device);

import torch

best_model, best_val_micro_f1_score = run()

dataset_size = len(test_df)
test_indices = list(range(dataset_size))

test_data = TransformerDataset(test_df, test_indices, set_type='test')
test_dataloader = DataLoader(test_data, batch_size=config.BATCH_SIZE)

def predict(model):
    val_loss = 0
    test_pred = []
    model.eval()
    for step, batch in tqdm(enumerate(test_dataloader), total=len(test_dataloader)):
        b_input_ids_titles = batch['titles']['input_ids'].to(device)
        b_attention_mask_titles = batch['titles']['attention_mask'].to(device)
        b_input_ids_abstracts = batch['abstracts']['input_ids'].to(device)
        b_attention_mask_abstracts = batch['abstracts']['attention_mask'].to(device)
        # b_input_ids_contexts = batch['contexts']['input_ids'].to(device)
        # b_attention_mask_contexts = batch['contexts']['attention_mask'].to(device)
        # b_extra=batch['extra']['extra'].to(device)

        with torch.no_grad():
            logits= model(
                b_input_ids_titles, 
                b_attention_mask_titles,
                b_input_ids_abstracts,
                b_attention_mask_abstracts,
                # b_input_ids_contexts,
                # b_attention_mask_contexts,
                # b_extra

            )
            logits = torch.sigmoid(logits)
            logits = np.round(logits.cpu().numpy())
            test_pred.extend(logits)

    test_pred = np.array(test_pred)
    return test_pred

test_pred = predict(best_model)

from sklearn.metrics import f1_score,accuracy_score,recall_score,precision_score,confusion_matrix,classification_report

