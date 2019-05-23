import os
import io
import shutil
import subprocess
import base64
import zipfile
import boto3
import json
import requests
import traceback
import sys
from bs4 import BeautifulSoup

from importlib import reload


def lambda_handler(event, context):

    # retrieve the lambda parameters
    bucket = os.environ['bucket']
    key_prefix = os.environ['key_prefix']

    # retrieve the call parameters
    to_pdf = event['to_pdf']
    tex = event['tex']
    files = event.get('files',{})

    # Prepare /tmp/latex
    shutil.rmtree("/tmp/latex", ignore_errors=True)
    os.mkdir("/tmp/latex")
    os.mkdir("/tmp/latex/files")

    # connect to s3
    s3 = boto3.resource('s3')

    # Prepare config file for htlatex: If we create an html file we need to load the cfg file
    if not to_pdf:
        with open("/tmp/latex/config.cfg", "w+") as f:
            f.write(s3.Object(bucket,f"{key_prefix}config.cfg").get()['Body'].read().decode('utf-8'))



    try:
        if to_pdf:
            # download files
            for filename in files:
                r = requests.get(files[filename], stream=True)
                with open(f"/tmp/latex/files/{filename}","wb+") as f:
                    r.raw.decode_content = True
                    shutil.copyfileobj(r.raw, f)
        # compile using latex
        res =  compiler(tex, to_pdf)
        return res
    except Exception as e:
        return {"stackTrace": traceback.format_exc(), "errorMessage": repr(e)}




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
