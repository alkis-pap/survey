import json
import random
import sys

def make_survey(json_file):
    data = []
    with open(json_file) as f:
        data = json.load(f)
    pages = []
    for item in data:
        if item["type"] == "text":
            pages += make_text(item)
        elif item["type"] == "matrix":
            pages += make_matrix(item)
        elif item["type"] == "photos":
            pages += make_photos(item)
    return json.dumps({
        "pages": pages
    })

def make_text(data):
    if "audio" in data:
        html = f'<audio src=/audio/{data["audio"]} />'
    else:
        html = ''
    html += f'<p>{data["text"]}</p>'
    return [
        {
            "questions": [{
                'type' : 'html',
                'html' : html
            }]
        }
    ]

def make_matrix(data):
    return [
        {
            "questions": [{
                'type' : 'matrix',
                'name' : data["name"],
                'title' : data["text"],
                'isAllRowRequired' : True,
                'columns' : data["columns"],
                'rows' : [{'value': i, 'text' : data} for i, data in enumerate(data["rows"])]
            }]
        }
    ]

_photos = []
with open("photos.json") as f:
    _photos = json.load(f)

def make_photos(data):
    result = []
    perm = list(range(len(_photos)))
    random.shuffle(perm)
    for i in range(data["number"]):
        # print(_photos[perm[i]], file=sys.stderr)
        result.append({
            "questions" : [
                {
                    "type" : "html",
                    "html" : f'<img class="photo" src=/photos/{_photos[perm[i]]["file"]} />'
                },
                {
                    "type" : "radiogroup",
                    'name' : data["prefix"] + str(i),
                    'isRequired' : True,
                    'titleLocation' : 'hidden',
                    "choices" : _photos[perm[i]]["choices"],
                    "rederAs" : "prettycheckbox"
                }
            ]
        })
    return result
        