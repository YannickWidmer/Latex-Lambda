import base64
import json
import boto3
import os
import ast
from datetime import datetime

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
                "isDisclosurePerpetual": False,
                "isOwnerCompany": False,
                "isRecipientCompany": True,
                "contractDated": "1/1/2019",
                "contractEndWithinDays": 7,
                "disclosureExpireInYears": 3,
                "agreementExpireInYears": 2,
                "lawState": "California",
                "recipientRepresentantName": "Jonathan",
                "recipientRepresentantTitle": "Boss",
                "ownerRole": "Client",
                "ownerAddress": "8123 McConnell",
                "ownerCity": "Westchester",
                "ownerState": "California",
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
            "entries":[
                {
                    'date': datetime(2019,5,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    'title': 'Logo',
                    'description': 'Logo variants' ,
                    'units': '02 units',
                    'rate': 80,
                    'total': 160
                },
                {
                    'date': datetime(2019,5,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    'title': 'Squad core team',
                    'description': 'Meeting with Alex, Dima, Andrei, Maxim' ,
                    'units': '01:21 hrs',
                    'rate': 75,
                    'total': 101.35
                }
            ],
        },
        "images": {"logo.png" : "https://s3-us-west-2.amazonaws.com/ds-temp-stg/latex_template_test/files/logo.png"}
        },'edit_invoice.html')

    elif request.form['action'] == 'Download_invoice':
        return get_pdf({
        "name": "invoice",
        "data": {
            "senderName": "Tina Smith",
            "senderAddress": "8123 McConnell Ave",
            "senderCity": "Los Angeles",
            "senderStateInitials": "CA",
            "senderZipCode": "90045",
            "recipientName": "Andre McGuire",
            "recipientAddress": "1635 16th St",
            "recipientCity": "Santa Monica",
            "recipientStateInitials": "CA",
            "recipientZipCode": "90404",
            "invoiceNumber": 1,
            "issuedDate": datetime(2018,12,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "dueDate": datetime(2019,1,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "taxesPercent": 0,
            "discountAmount": 0,
            "totalAmount": 456.30,
            "subtotal": 456.35,
            "feePercentage":10.0,
            "entries":[
                {
                    'date': datetime(2019,5,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    'title': 'Logo',
                    'description': 'Logo variants' ,
                    'units': '02 units',
                    'rate': 80,
                    'total': 160
                },
                {
                    'date': datetime(2019,5,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    'title': 'Squad core team',
                    'description': 'Meeting with Alex, Dima, Andrei, Maxim' ,
                    'units': '01:21 hrs',
                    'rate': 75,
                    'total': 101.35
                }
            ]
        },
        "images": {"logo.png" : "https://s3-us-west-2.amazonaws.com/ds-temp-stg/latex_template_test/files/logo.png"}
        })

@app.route('/invoice')
def invoice_page():
    return get_html( {
    "name": "invoice",
    "data": {
            "senderName": "Tina Smith",
            "senderAddress": "8123 McConnell Ave",
            "senderCity": "Los Angeles",
            "senderStateInitials": "CA",
            "senderZipCode": "90045",
            "recipientName": "Andre McGuire",
            "recipientAddress": "1635 16th St",
            "recipientCity": "Santa Monica",
            "recipientStateInitials": "CA",
            "recipientZipCode": "90404",
            "invoiceNumber": 1,
            "issuedDate": datetime(2018,12,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "dueDate": datetime(2019,1,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
            "taxesPercent": 0,
            "discountAmount": 0,
            "totalAmount": 456.30,
            "subtotal": 456.35,
            "feePercentage":10.0,
            "entries":[
                {
                    'date': datetime(2019,5,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    'title': 'Logo',
                    'description': 'Logo variants' ,
                    'units': '02 units',
                    'rate': 80,
                    'total': 160
                },
                {
                    'date': datetime(2019,5,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
                    'title': 'Squad core team',
                    'description': 'Meeting with Alex, Dima, Andrei, Maxim' ,
                    'units': '01:21 hrs',
                    'rate': 75,
                    'total': 101.35
                }
            ]
        },
        "images": {"logo.png" : "https://s3-us-west-2.amazonaws.com/ds-temp-stg/latex_template_test/files/logo.png"}
    },
    'edit_invoice.html')


if __name__ == '__main__':
    app.debug = True
    app.run()