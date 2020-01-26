import json
import random
import sys

class Survey:
    def __init__(self, filename):
        self.columns = []
        data = []
        with open(filename) as f:
            data = json.load(f)
        makers = {
            'text' : self.make_text,
            'matrix' : self.make_matrix,
            'photo' : self.make_photo
        }
        self.pages = []
        for item in data:
            makers[item['type']](item)

    def generate(self, filename):
        with open(filename, "w") as f:
            f.write(json.dumps({ "pages": self.pages }))
    
    def make_text(self, data):
        if "audio" in data:
            html = f"""<audio controls autoplay>
                    <source src="/audio/{data["audio"]}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>"""
        else:
            html = ''
        html += f'<p>{data["text"]}</p>'
        self.pages.append({
            "questions": [{
                'type' : 'html',
                'html' : html
            }]
        })
    
    def make_matrix(self, data):
        self.columns += [data["name"] + "_" + col for col in data["columns"]]
        self.pages.append({
            "questions": [{
                'type' : 'matrix',
                'name' : data["name"],
                'title' : data["text"],
                'isAllRowRequired' : True,
                'columns' : data["columns"],
                'rows' : [{'value': i, 'text' : data} for i, data in enumerate(data["rows"])]
            }]
        })

    def make_photo(self, data):
        self.columns.append(data['name'])
        self.pages.append({
            "questions" : [
                {
                    "type" : "html",
                    "html" : f'<img class="photo" src=/photos/{data["file"]} />'
                },
                {
                    "type" : "radiogroup",
                    'name' : data["name"],
                    'isRequired' : True,
                    'titleLocation' : 'hidden',
                    "choices" : data["choices"],
                    "colCount" : len(data["choices"])
                    # "rederAs" : "prettycheckbox"
                }
            ]
        })
