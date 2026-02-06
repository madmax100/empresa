import json
try:
    data = json.load(open('debug_json_out.txt', encoding='utf-16'))
    for idx, item in enumerate(data):
        print(f"{idx} | {item['doc']} | {item['valor']}")
except Exception as e:
    print(e)
