import json

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
        pages: pages
    })

def make_text(data):
    if "audio" in data:
        html = f'<audio src={data["file"]} />'
    else:
        html = ''
    html += f'<p>{data["text"]}</p>'
    return [
        {
            "questions": [{
                'type' : 'html',
                'name' : name,
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
                'columns' : data["columns"],
                'rows' : data["rows"]
            }]
        }
    ]

def make_photos(photos, data):
    result = []
    perm = random.shuffle(range(len(photos)))
    for i in range(data["number"]):
        result.append({
            "questions" : [
                {
                    "type" : "html"
                    "html" : f'<img src={photos[perm[i]]["file"]} />'
                },
                {
                    "type" : "radiogroup",
                    "choices" : photos[perm[i]]["choices"]
                }
        })
        