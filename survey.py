import json
import random
import sys
from jsonschema import validate, ValidationError

class SurveyError(Exception):
    pass

class Survey:

    def __init__(self, filename):
        self.columns = []
        data = []
        with open(filename) as f:
            data = json.load(f)
        
        try:
            self.pages = []
            for questions_array in data:
                questions = []
                for question in questions_array:
                    question_type = question['type']
                    # print(question_type)
                    if 'text' in question:
                        question['text'] = question['text'].replace('\n', '<br>')
                    if question_type == 'text':
                        questions += self.make_text(question)
                    elif question_type == 'question':
                        questions += self.make_question(question)
                    elif question_type == 'matrix':
                        questions += self.make_matrix(question)
                    elif question_type == 'photo':
                        questions += self.make_photo(question)
                    else:
                        raise SurveyError(f"invalid question type: '{question_type}'")
                self.pages.append({
                    'questions' : questions
                })

        except ValidationError as e:
            raise SurveyError(e)


    def generate(self, filename):
        with open(filename, "w") as f:
            f.write(json.dumps({ "pages": self.pages }))

    def make_text(self, data):
        validate(instance=data, schema={
            'type' : 'object',
            'properties' : {
                'text' : {'type' : 'string'},
                'audio' : {'type' : 'string'}
            },
            'required' : ['text']
        })
        
        if "audio" in data:
            return[{
                'type' : 'html',
                'html' : f"""<audio controls autoplay>
                    <source src="/files/{data["audio"]}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                <p class="survey-text">{data["text"]}</p>"""
            }]
        elif "audio_m" in data and "audio_w" in data:
            return [{
                'type' : 'html',
                'html' : f"""<audio controls autoplay>
                    <source src="/files/{data["audio_w"]}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                <p class="survey-text">{data["text"]}</p>""",
                'visibleIf' : "{gender} = 1"
            },
            {
                'type' : 'html',
                'html' : f"""<audio controls autoplay>
                    <source src="/files/{data["audio_m"]}" type="audio/wav">
                    Your browser does not support the audio element.
                </audio>
                <p class="survey-text">{data["text"]}</p>""",
                'visibleIf' : "{gender} = 2"
            }]
        else:
            return [{
                'type' : 'html',
                'html' : f'<p class="survey-text">{data["text"]}</p>'
            }]

    def make_question(self, data):
        validate(instance=data, schema={
            'type' : 'object',
            'properties' : {
                'name' : {'type' : 'string'},
                'text' : {'type' : 'string'},
                'choices' : {
                    'type' : 'array',
                    'items' : { 'type' : 'string' }    
                }
            },
            'required' : ['name', 'choices', 'text']
        })

        self.columns.append(data['name'])
        
        return [
            {
                "type" : "dropdown",
                'name' : data["name"],
                'isRequired' : True,
                'title' : data["text"],
                'titleLocation' : 'left',
                "choices" : [{'value': i + 1, 'text': col} for i, col in enumerate(data["choices"])],
                "colCount" : len(data["choices"])
                # "rederAs" : "prettycheckbox"
            }
        ]

    def make_matrix(self, data):
        validate(instance=data, schema={
            'type' : 'object',
            'properties' : {
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

        return self.make_text(data) + [{
            'type' : 'matrix',
            'name' : data["name"],
            'title' : data["text"],
            'titleLocation' : 'hidden',
            'isAllRowRequired' : True,
            'columns' : [{'value': i + 1, 'text': col} for i, col in enumerate(data["columns"])],
            'rows' : [{'value': i + 1, 'text' : row} for i, row in enumerate(data["rows"])]
        }]

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

        title = data.get('title', '')

        return [
            {
                "type" : "html",
                "html" : f'<p>{title}</p><img class="photo" src=/files/{data["file"]} />'
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
