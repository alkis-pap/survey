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
                    <source src="/files/{data["audio"]}" type="audio/wav">
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
        self.columns += [data["name"] + "_" + str(i + 1) for i in range(len(data["rows"]))]
        self.make_text(data)
        self.pages[-1]["questions"].append({
                'type' : 'matrix',
                'name' : data["name"],
                # 'title' : '',#data["text"],
                'titleLocation' : 'hidden',
                'isAllRowRequired' : True,
                'columns' : [{'value': i + 1, 'text': col} for i, col in enumerate(data["columns"])],
                'rows' : [{'value': i + 1, 'text' : row} for i, row in enumerate(data["rows"])]
        })

    def make_photo(self, data):
        self.columns.append(data['name'])
        self.pages.append({
            "questions" : [
                {
                    "type" : "html",
                    "html" : f'<img class="photo" src=/files/{data["file"]} />'
                },
                {
                    "type" : "radiogroup",
                    'name' : data["name"],
                    'isRequired' : True,
                    'titleLocation' : 'hidden',
                    "choices" : [{'value': i + 1, 'text': col} for i, col in enumerate(data["choices"])],
                    "colCount" : len(data["choices"])
                    # "rederAs" : "prettycheckbox"
                }
            ]
        })
