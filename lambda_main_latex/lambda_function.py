import os
import io
import shutil
import subprocess
import base64
import zipfile
import boto3
import json
import jinja2
import requests
import traceback
import sys


from importlib import reload


render_module = None

def lambda_handler(event, context):
    # retrieve the lambda parameters
    bucket = os.environ['bucket']
    key_prefix = os.environ['key_prefix']

    # retrieve the call parameters
    name = event['name']
    to_pdf = event['to_pdf']
    data = event['data']
    files = event.get('files',{})

    # prepare  /tmp/templates
    shutil.rmtree("/tmp/templates", ignore_errors=True)
    os.mkdir("/tmp/templates")

    # connect to s3
    s3 = boto3.resource('s3')

    # download template.tex and template.py to /tmp/templates
    tex_template =  s3.Object(bucket,f"{key_prefix}{name}.tex").get()['Body'].read().decode('utf-8')
    py_template =  s3.Object(bucket,f"{key_prefix}{name}.py").get()['Body'].read().decode('utf-8')
    with open("/tmp/templates/template.tex", "w+") as f:
        f.write(tex_template)
    with open("/tmp/templates/template.py", "w+") as f:
        f.write(py_template)
    with open("/tmp/templates/__init__.py", "w+") as f:
        f.write("")

    # Loading the template.py so we can use it to perform the data transformation.
    # To do so we need to add /tmp/templates to the PATH and then load the module.
    # However lambda keeps an instance of the lambda if calls are made fast after each other.
    # In that case we need to make sure that we have the python module for the according template
    # and that it is the latest version, if we would simply import the class and it had done it in a
    # previous run it would ignore the import assuming it has the right module. Like this changes
    # to the file would be ignored (only problematic during development I guess) then if it was another
    # template it would load the module for the other class instead of this one.
    global render_module
    sys.path.insert(0, '/tmp/templates/')
    if render_module is None:
        render_module = __import__('template')
    else:
        reload(render_module)

    try:
        # add files to data
        for filename in files:
            data_key = filename.split('.')[0] # remove the filetype
            if data_key in data:
                raise ValueError(f"{data_key} has been specified in files and data")
            data[data_key] = files[filename] # add the key value pair (ending striped filename, file url)


        data = render_module.render(data, to_pdf) # use the template specific python module to prepare and check the data
        rendered_tex = render(data) # use jinja to apply tempates rule according to data
        res =  compiler(rendered_tex, files, to_pdf) # compile the tex file to pdf or html using the second lambda (lambda inception)
        res['data'] = data # adding data to res for debugging reasons
        return res
    except Exception as e:
        return {"stackTrace": traceback.format_exc(), "errorMessage": repr(e)}


def render(json_data):

    latex_jinja_env = jinja2.Environment(
        block_start_string='\BLOCK{',
        block_end_string='}',
        variable_start_string='\VAR{',
        variable_end_string='}',
        comment_start_string='\#{',
        comment_end_string='}',
        line_statement_prefix='%[',
        line_comment_prefix='%#',
        trim_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(os.path.join('/tmp', 'templates')))
    # retrieve the jinja template
    template = latex_jinja_env.get_template('template.tex')
    # import the according class for this template
    return template.render(**json_data)


def compiler(tex, files, to_pdf):

    payload = json.dumps({
        "tex": tex,
        "to_pdf": to_pdf,
        "files" : files
        })

    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName="latex_compiler",
        InvocationType='RequestResponse',
        Payload=payload,
    )

    res = json.loads(response['Payload'].read().decode())

    # Return base64 encoded pdf and stdout log from pdflaxex...
    return res
