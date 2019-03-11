import os
import io
import shutil
import subprocess
import base64
import zipfile
import boto3
import json
import jinja2
import sys
from bs4 import BeautifulSoup
from importlib import reload

render_module = None

def lambda_handler(event, context):
    # Put template into /tmp/template/template.tex
    shutil.rmtree("/tmp/templates", ignore_errors=True)
    os.mkdir("/tmp/templates")

    name = event['name']
    # connect to s3
    s3 = boto3.resource('s3')

    tex_template =  s3.Object('ds-temp-stg',f"latex_template_test/{name}.tex").get()['Body'].read().decode('utf-8')
    py_template =  s3.Object('ds-temp-stg',f"latex_template_test/{name}.py").get()['Body'].read().decode('utf-8')

    with open("/tmp/templates/template.tex", "w+") as f:
        f.write(tex_template)
    with open("/tmp/templates/template.py", "w+") as f:
        f.write(py_template)
    with open("/tmp/templates/__init__.py", "w+") as f:
        f.write("")

    data = event['data']
    if not type(data) is dict:
        raise ValueError('The entry in data is not a dict.')

    sys.path.insert(0, '/tmp/templates/')

    # lambda keep an instance of the lambda if calls are made fast after each other.
    # in that case we need to make sure that we have the python module for the according template
    # and that it is the latest version
    global render_module
    if render_module is None:
        render_module = __import__('template')
    else:
        reload(render_module)

    json_data = render_module.render(data, event['to_pdf'])

    rendered_tex = render(json_data)
    return compiler(rendered_tex, event['to_pdf'])


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

    # Extract input ZIP file to /tmp/latex...
    shutil.rmtree("/tmp/latex", ignore_errors=True)
    os.mkdir("/tmp/latex")

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
                            '"html,css-in"'],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.STDOUT)
    res = {"stdout": r.stdout.decode('utf_8'),"tex": tex, 'path': os.environ['PATH']}

    if to_pdf:
    # Read "document.pdf"...
        with open("document.pdf", "rb") as html_file:
            res['pdf'] = base64.b64encode(html_file.read()).decode('ascii')
    else:
    # Read "document.html"...
        with open("document.html", "rb") as html_file:
            soup = BeautifulSoup(html_file.read(), 'html.parser')
            res['html'] = str(soup.find('body'))

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
