import json
import random
import sys
from jsonschema import validate, ValidationError

class SurveyError(Exception):
    pass

class Survey:
    # page_schemas = {
    #     'text' : {
    #         'type' : 'object',
    #         'properties' : {
    #             # 'type' : {'type' : 'string', 'enum' : ['text']},
    #             'text' : {'type' : 'string'},
    #             'audio' : {'type' : 'string'}
    #         },
    #         'required' : ['text']
    #     },
    #     'matrix' : {
    #         'type' : 'object',
    #         'properties' : {
    #             # 'type' : {'type' : 'string', 'enum' : ['matrix']},
    #             'name' : {'type' : 'string'},
    #             'text' : {'type' : 'string'},
    #             'audio' : {'type' : 'string'},
    #             'rows' : {
    #                 'type' : 'array',
    #                 'items' : { 'type' : 'string' }    
    #             },
    #             'columns' : {
    #                 'type' : 'array',
    #                 'items' : { 'type' : 'string' }    
    #             }
    #         },
    #         'required' : ['name', 'columns']
    #     },
    #     'photo' : {
    #         'type' : 'object',
    #         'properties' : {
    #             # 'type' : {'type' : 'string', 'enum' : ['photo']},
    #             'name' : {'type' : 'string'},
    #             'file' : {'type' : 'string'},
    #             'choices' : {
    #                 'type' : 'array',
    #                 'items' : { 'type' : 'string' }    
    #             }
    #         },
    #         'required' : ['name', 'file', 'choices']
    #     }
    # }
    
    # schema = {
    #     'type' : 'array',
    #     'items' : {
    #         'oneOf' : list(page_schemas.values())
    #     }
    # }

    def __init__(self, filename):
        self.columns = []
        data = []
        with open(filename) as f:
            data = json.load(f)
        
        try:
            # validate(instance=data, schema=Survey.schema)
            
                # makers = {
                #     'text' : self.make_text,
                #     'matrix' : self.make_matrix,
                #     'photo' : self.make_photo
                # }
                # print(makers)
            self.pages = []
            for item in data:
                item_type = item['type']
                print(item_type)
                if item_type == 'text':
                    print('make_text')
                    self.make_text(item)
                elif item_type == 'matrix':
                    print('make_matrix')
                    self.make_matrix(item)
                elif item_type == 'photo':
                    print('make_photo')
                    self.make_photo(item)
                else:
                    raise SurveyError(f"invalid question type: '{item_type}'")

        except ValidationError as e:
            raise SurveyError(e)


    def generate(self, filename):
        with open(filename, "w") as f:
            f.write(json.dumps({ "pages": self.pages }))
    
    def make_text(self, data):
        validate(instance=data, schema={
            'type' : 'object',
            'properties' : {
                # 'type' : {'type' : 'string', 'enum' : ['text']},
                'text' : {'type' : 'string'},
                'audio' : {'type' : 'string'}
            },
            'required' : ['text']
        })

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
        validate(instance=data, schema={
            'type' : 'object',
            'properties' : {
                # 'type' : {'type' : 'string', 'enum' : ['matrix']},
                'name' : {'type' : 'string'},
                'text' : {'type' : 'string'},
                'audio' : {'type' : 'string'},
                'rows' : {
                    'type' : 'array',
                    'items' : { 'type' : 'string' }    
                },
                'columns' : {
                    'type' : 'array',
                    'items' : { 'type' : 'string' }    
                }
            },
            'required' : ['name', 'columns', 'text']
        })

        self.columns += [data["name"] + "_" + str(i + 1) for i in range(len(data["rows"]))]
        self.make_text(data)
        self.pages[-1]["questions"].append({
                'type' : 'matrix',
                'name' : data["name"],
                'title' : data["text"],
                # 'titleLocation' : 'hidden',
                'isAllRowRequired' : True,
                'columns' : [{'value': i + 1, 'text': col} for i, col in enumerate(data["columns"])],
                'rows' : [{'value': i + 1, 'text' : row} for i, row in enumerate(data["rows"])]
        })

    def make_photo(self, data):
        validate(instance=data, schema={
            'type' : 'object',
            'properties' : {
                # 'type' : {'type' : 'string', 'enum' : ['photo']},
                'name' : {'type' : 'string'},
                'file' : {'type' : 'string'},
                'choices' : {
                    'type' : 'array',
                    'items' : { 'type' : 'string' }    
                }
            },
            'required' : ['name', 'file', 'choices']
        })

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
