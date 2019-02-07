import json

localDict = {}

with open('CET4.txt', 'r', encoding='utf-8') as f1:
    lst1 = f1.readlines()
    for i in lst1:
        print(i.split())
        word = i.split()[0]
        trans = i.split()[1]
        localDict[word] = trans
with open('CET6.txt', 'r', encoding='utf-8') as f2:
    lst2 = f2.readlines()
    for i in lst2:
        word = i.split()[0]
        trans = i.split()[1]
        localDict[word] = trans

dictfile = open('LocalDict.json', 'w', encoding='utf-8')
json.dump(localDict, dictfile, ensure_ascii=False)
dictfile.close()
