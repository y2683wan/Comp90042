from torch.utils.data import Dataset
import json
import torch
from utils import clean_text

class MyDataset(Dataset):
    def __init__(self, mode):
        super().__init__()
        self.mode = mode
        self.sep = ' '
        instance_file = './project-data/' + mode + '.data.txt'   
        rm_file = './project-data/logs.txt' 

        with open(rm_file, 'r') as f:
            temp = f.readlines()
        
        with open(instance_file, 'r') as f:
            instance_lines = f.readlines()

        rm_instances = []
        for item in temp:
            rm_instances += item.strip('\n').split(',')

        self.instances = []
        not_found = []
        for i in range(0, len(instance_lines)):
            temp = instance_lines[i].strip('\n').split(',')
            cur = []
            for id in temp:
                if id not in rm_instances:
                    cur.append(id)
            if len(cur) != 0:
                self.instances.append(cur)
            else:
                not_found.append(i)

        
        if self.mode != 'test':
            label_file = './project-data/' + mode + '.label.txt'
            self.labels = []
            with open(label_file) as f:
                label_lines = f.readlines()

            for i in range(0, len(label_lines)):
                if i not in not_found:
                    self.labels.append(label_lines[i])

            assert len(self.instances) == len(self.labels), "Inconsistant number between instances and labels"

    def __getitem__(self, index):
        temp = self.instances[index]
        text = ""
        for item in temp:
            f = open('./project-data/' +self.mode+ '-tweet-objects/' + item + '.json', 'r', encoding='utf-8')
            content = json.load(f)
            text += clean_text(content['text']).strip() + self.sep
            f.close()
        text = text.strip()
        if self.mode != 'test':       
            if self.labels[index].strip('\n') == "rumour": 
                label = 1
            else:
                label = 0
            return {
                'text': text, 
                'label': label
            }
        else:
            return {
                'text': text
            }

    def __len__(self):
        return len(self.instances)


class Collator(object):
    def __init__(self, tokenizer, max_length=512):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, batch):
        text = [item['text'] for item in batch]
        text = self.tokenizer.batch_encode_plus(
            text,
            max_length=self.max_length if self.max_length > 0 else None,
            padding = 'max_length',
            return_tensors='pt',
            truncation=True if self.max_length > 0 else False,
        )

        if 'label' in batch[0]:
            label = torch.tensor([item['label'] for item in batch])
            return (text, label)   
        else:
            return text


if __name__ == '__main__':
    import re
    flag = True
    while flag:
        num = 0
        train_set = MyDataset(mode = 'dev')
        for i in range(0, len(train_set)):
            try:
                train_set[i]
            except Exception as e:
                print(e)
                with open('./project-data/logs.txt', 'a+') as f:
                    f.write(re.findall(r'[0-9]+', str(e))[1] + '\n')
                    num += 1
                    f.close()
            
        if num == 0:
            flag = False
