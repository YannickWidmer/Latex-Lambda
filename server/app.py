import base64
import json
import boto3
import os
import ast

#!flask/bin/python
from flask import Flask, render_template, url_for, redirect, request, send_file

app = Flask(__name__)
app.config.from_object(__name__) # load config from this file , app.py

# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='dsflhsad;fklh ;ewhf',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('LATEXLAMBDA_SETTINGS', silent=True)


def get_html(data, container_name):
    data['to_pdf'] = False
    payload = json.dumps(data)
    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName="latex_compiler",
        InvocationType='RequestResponse',
        Payload=payload,)

    res = json.loads(response['Payload'].read().decode())
    if 'html' not in res:
        raise ValueError(res)
    return render_template(container_name,content=res['html'])

def get_pdf(data):
    data['to_pdf'] = True
    payload = json.dumps(data)
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName="latex_compiler",
        InvocationType='RequestResponse',
        Payload=payload,)
    res = json.loads(response['Payload'].read().decode())
    if 'pdf' not in res:
        raise ValueError(res)
    outdir = os.path.join(os.getcwd(),'/tmp')
    with open(os.path.join(outdir, 'document.pdf'), 'wb+') as outfile:
            outfile.write(base64.b64decode(res['pdf']))
    return send_file(os.path.join(outdir, 'document.pdf'), attachment_filename='contract.pdf')

@app.route('/')
def main_page():
    return get_html( {
    "name": "nda",
    "data": { }
    },'edit_nda.html')

@app.route('/submit', methods=['POST','GET'])
def submit():
    ownerName = request.form['name']
    recipientName = request.form['familyName']

    if request.form['action'] == 'Submit':
        return get_html({
        "name": "nda",
        "data": {
                "ownerName": ownerName,
                "recipientName": recipientName
            }
        },'edit_nda.html')

    elif request.form['action'] == 'Download_contract':
        return get_pdf({
        "name": "nda",
        "data": {
                "ownerName": ownerName,
                "recipientName": recipientName,
                "isEffectiveDateSpecific": True,
                "contractDated": "1/1/2019",
                "contractEndWithinDays": 7,
                "isDisclosurePerpetual": False,
                "lawState": "California",
                "isOwnerCompany": False,
                "isRecipientCompany": True,
                "recipientRepresentantName": "Jonathan",
                "recipientRepresentantTitle": "Boss",
                "ownerRole": "Client",
                "ownerAddress": "8123 McConnell",
                "ownerCity": "Westchester",
                "ownerState": "California:OwnerState",
                "ownerZipCode": "90045:OwnerZip",
                "recipientAddress": "8123 McConnell",
                "recipientCity": "Santa Monica",
                "recipientState": "California",
                "recipientZipCode": "90045"
                }
        })
    elif request.form['action'] == 'Submit_invoice':
        return get_html({
        "name": "invoice",
        "data": {
                "ownerName": ownerName,
                "recipientName": recipientName
            }
        },'edit_invoice.html')

    elif request.form['action'] == 'Download_invoice':
        return get_pdf({
        "name": "invoice",
        "data": {
                "ownerName": ownerName,
                "recipientName": recipientName
            }
        })

@app.route('/invoice')
def invoice_page():
    return get_html( {
    "name": "invoice",
    "data": {
        "ownerName": "Yannick"
    },
    "images": {"logo.png" : "https://s3-us-west-2.amazonaws.com/ds-temp-stg/latex_template_test/files/logo.png"},
    "to_pdf": False
    },'edit_invoice.html')


if __name__ == '__main__':
    app.debug = True
    app.run()