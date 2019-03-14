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

from bs4 import BeautifulSoup
from importlib import reload

render_module = None

def lambda_handler(event, context):

    # retrieve parameters
    name = event['name']
    to_pdf = event['to_pdf']
    data = event['data']
    images = event.get('images',{})

    # prepare  /tmp/templates
    shutil.rmtree("/tmp/templates", ignore_errors=True)
    os.mkdir("/tmp/templates")

    # Prepare /tmp/latex
    shutil.rmtree("/tmp/latex", ignore_errors=True)
    os.mkdir("/tmp/latex")
    os.mkdir("/tmp/latex/pics")

    # Prepare /tmp/texmf
    # os.makedirs("/tmp/texmf", exist_ok=True)

    # connect to s3
    s3 = boto3.resource('s3')

    # Prepare config file for htlatex: If we create an html file we need to load the cfg file
    if not to_pdf:
        with open("/tmp/latex/config.cfg", "w+") as f:
            f.write(s3.Object('ds-temp-stg',f"latex_template_test/config.cfg").get()['Body'].read().decode('utf-8'))

    # download template.tex and template.py to /tmp/templates
    tex_template =  s3.Object('ds-temp-stg',f"latex_template_test/{name}.tex").get()['Body'].read().decode('utf-8')
    py_template =  s3.Object('ds-temp-stg',f"latex_template_test/{name}.py").get()['Body'].read().decode('utf-8')
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
        # prepare images
        data = prepare_images(data,images,to_pdf)
        data = render_module.render(data, to_pdf)
        rendered_tex = render(data)
        res =  compiler(rendered_tex, to_pdf)
        res['data'] = data
        return res
    except Exception as e:
        return {"stackTrace": traceback.format_exc(), "errorMessage": repr(e)}


def prepare_images(json_data, images, to_pdf):
    """
    This function either downloads the images into the temporary folder to create a pdf
    or else sets the coresponding variable to the public url
    """
    if to_pdf:
        for image in images:
            r = requests.get(images[image], stream=True)
            with open(f"/tmp/latex/pics/{image}","wb+") as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
    else:
        for image in images:
            json_data[image.split('.')[0]] = images[image]

    return json_data


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


def compiler(tex, to_pdf):

    with open("/tmp/latex/document.tex", "w+") as f:
        f.write(tex)

    os.environ['PATH'] += ":/var/task/texlive/2017/bin/x86_64-linux/"
    os.environ['HOME'] = "/tmp/latex/"
    os.environ['PERL5LIB'] = "/var/task/texlive/2017/tlpkg/TeXLive/"

    os.chdir("/tmp/latex/")

    if to_pdf:
        # Run pdflatex...
        r = subprocess.run(["latexmk",
                            "-verbose",
                            "-interaction=batchmode",
                            "-pdf",
                            "-output-directory=/tmp/latex",
                            "document.tex"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
        r = subprocess.run(["latexmk",
                            "-verbose",
                            "-interaction=batchmode",
                            "-pdf",
                            "-output-directory=/tmp/latex",
                            "document.tex"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)

    else:
        r = subprocess.run(["htlatex",
                            "document.tex",
                            '"config,css-in"'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
    res = {"stdout": r.stdout.decode('utf_8'),"tex": tex}

    if to_pdf:
        try:
            # Read "document.pdf"...
            with open("document.pdf", "rb") as pdf_file:
                res['pdf'] = base64.b64encode(pdf_file.read()).decode('ascii')
        except FileNotFoundError:
            pass

    else:
    # Read "document.html"...
        try:
            with open("document.html", "rb") as html_file:
                soup = BeautifulSoup(html_file.read(), 'html.parser')
                res['html'] = str(soup.find('body'))
        except FileNotFoundError:
            pass
    # Read "document.css"...
    try:
        with open("document.css", "rb") as css_file:
            res['css'] = base64.b64encode(css_file.read()).decode('ascii')
    except:
        pass

    # Read "document.log"...
    try:
        with open("document.log", "rb") as log_file:
            res['log'] = base64.b64encode(log_file.read()).decode('ascii')
    except:
        pass

    # Return base64 encoded pdf and stdout log from pdflaxex...
    return res
