import base64
import json
import boto3
import os
import ast
from bs4 import BeautifulSoup

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


def get_html(data):
    payload = json.dumps(data)
    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName="latex_compiler",
        InvocationType='RequestResponse',
        Payload=payload,)
    res = ast.literal_eval(response['Payload'].read().decode())
    soup = BeautifulSoup(base64.b64decode(res['html']), 'html.parser')
    body = soup.find('body')
    the_contents_of_body_without_body_tags = body
    return render_template('edit_pane.html',content=the_contents_of_body_without_body_tags)

def get_pdf(data):
    payload = json.dumps(data)
    client = boto3.client('lambda')
    response = client.invoke(
        FunctionName="latex_compiler",
        InvocationType='RequestResponse',
        Payload=payload,)

    res = ast.literal_eval(response['Payload'].read().decode())
    outdir = os.path.join(os.getcwd(),'/tmp')
    with open(os.path.join(outdir, 'document.pdf'), 'wb+') as outfile:
            outfile.write(base64.b64decode(res['pdf']))
    return send_file(os.path.join(outdir, 'document.pdf'), attachment_filename='contract.pdf')

@app.route('/')
def main_page():
    return get_html( {
    "name": "nda",
    "data": {
            "ownerName": "Yannick:Owner",
            "recipientName": "tispr:Recipient",
            "contractDated": "1/1/2019",
            "contractEndWithinDays": 7,
            "isDisclosurePerpetual": False,
            "lawState": "California:lawState",
            "isOwnerCompany": False,
            "isRecipientCompany": True,
            "recipientRepresentantName": "Jonathan:Recipient",
            "recipientRepresentantTitle": "Boss:recipient",
            "ownerRole": "Client",
            "ownerAddress": "8123 McConnell:OwnerAddress",
            "ownerState": "California:OwnerState",
            "ownerZipCode": "90045:OwnerZip",
            "recipientAddress": "8123 McConnell:RecipientAddress",
            "recipientState": "California:Recipient",
            "recipientZipCode": "90045:recipient"
        },
    "to_pdf": False
    })

@app.route('/submit', methods=['POST','GET'])
def submit():
    ownerName = request.form['name']
    recipientName = request.form['familyName']

    if request.form['action'] == 'Submit':
        res = get_html({
        "name": "nda",
        "data": {
                "ownerName": ownerName,
                "recipientName": recipientName,
                "contractDated": "1/1/2019",
                "contractEndWithinDays": 7,
                "isDisclosurePerpetual": False,
                "lawState": "California:lawState",
                "isOwnerCompany": False,
                "isRecipientCompany": True,
                "recipientRepresentantName": "Jonathan:Recipient",
                "recipientRepresentantTitle": "Boss:recipient",
                "ownerRole": "Client",
                "ownerAddress": "8123 McConnell:OwnerAddress",
                "ownerState": "California:OwnerState",
                "ownerZipCode": "90045:OwnerZip",
                "recipientAddress": "8123 McConnell:RecipientAddress",
                "recipientState": "California:Recipient",
                "recipientZipCode": "90045:recipient"
            },
        "to_pdf": False
        })
        return res
    else:
        return get_pdf({
        "name": "nda",
        "data": {
                "ownerName": ownerName,
                "recipientName": recipientName,
                "contractDated": "1/1/2019",
                "contractEndWithinDays": 7,
                "isDisclosurePerpetual": False,
                "lawState": "California:lawState",
                "isOwnerCompany": False,
                "isRecipientCompany": True,
                "recipientRepresentantName": "Jonathan:Recipient",
                "recipientRepresentantTitle": "Boss:recipient",
                "ownerRole": "Client",
                "ownerAddress": "8123 McConnell:OwnerAddress",
                "ownerState": "California:OwnerState",
                "ownerZipCode": "90045:OwnerZip",
                "recipientAddress": "8123 McConnell:RecipientAddress",
                "recipientState": "California:Recipient",
                "recipientZipCode": "90045:recipient"
            },
        "to_pdf": True
        })

if __name__ == '__main__':
    app.debug = True
    app.run()