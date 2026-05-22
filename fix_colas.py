import json

f = r'E:\0000ew V2Claude\backend\db\players\joticalindo.json'
with open(f, encoding='utf-8') as fp:
    d = json.load(fp)

for c in d['cities']:
    c['COLAS'] = []

with open(f, 'w', encoding='utf-8') as fp:
    json.dump(d, fp, ensure_ascii=False, indent=2)

print("OK — COLAS vaciadas en todas las ciudades")
