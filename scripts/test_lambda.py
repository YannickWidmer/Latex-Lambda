import base64
import json
import boto3
import os
import ast
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, meta

def test_template(name,data, to_pdf, images = {}):

    print("##########################################################")
    print("##########################################################")
    print(f"############# testing for template: {name} ##############")
    print(f"#############  {'PDF ' if to_pdf else 'HTML'}                         ##############")
    print("##########################################################")
    print("##########################################################")
    payload = json.dumps({
        "name": name,
        "data": data,
        "to_pdf": to_pdf,
        "images" : images
        })

    print()
    print("##################  Payload  #############################")
    print(payload)

    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName="latex_compiler",
        InvocationType='RequestResponse',
        Payload=payload,
    )

    res = json.loads(response['Payload'].read().decode())

    print()
    print("####################  RES  ##############################")

    print([key for key in res])

    out_dir = './test_output/'

    for ending in ['pdf','css','log']:
        if ending in res:
            print(f"############# write document.{ending}         ###############")
            with open(os.path.join(out_dir, f'document.{ending}'), 'wb+') as outfile:
                outfile.write(base64.b64decode(res[ending]))

    for ending in ['html','tex']:
        if ending in res:
            print(f"############# write document.{ending}         ###############")
            with open(os.path.join(out_dir, f'document.{ending}'), 'w+') as outfile:
                outfile.write(res[ending])

    for out in ['stdout','stderr']:
        if out in res:
            print(f"############# write {out} to {out}.txt ###############")
            with open(os.path.join(out_dir, f'{out}.txt'), 'w+') as outfile:
                outfile.write(res[out])


    for tx in ['stackTrace','data','images']:
        if tx in res:
            print(f"\n############# PRINT {tx}      #########################")
            print(res[tx])
            print()


if input("Test Consulting Agreement y/N") == 'y':
    test_template("contract",{
                'clientName':'Yannick',
                'consultantName': 'Jonathan',
                'clientAddress': 'clientAddress',
                'clientCity': 'clientCity',
                'clientState': 'California',
                'clientZipCode': 12345,
                'consultantAddress': 'address of consultant',
                'consultantCity': 'City of Angels',
                'consultantState': 'Texas',
                'consultantZipCode': '234234523',
                'isClientOwner': True,
                'isEffectiveDateSpecific': False,
                'contractEnd':datetime(2018,12,12).strftime("%Y-%m-%d %H:%M:%S.%f"),
                'lawState': 'California',
                'isClientCompany': True,
                'isConsultantCompany': True,
                'paymentRate':'day',
                'invoiceFrequency':'biWeekly',
                'invoicePaymentDays': 30,
                'paymentPrice': 10.2,
                'invoiceFee': 4.5,
                'isConsultantPayingExpenses': False,
                'hasExpenseAdditionalCriteria' : False,
                'isExpenseNeedPreApproval': False,
                'hasExpensePreApprovalPrice': False,
                'contractEndWithinDays': 2,
                'workscope':' The workscope, meaning what there is to do.',
                'canConsultantUseWork': True,
                'isClientNeedToCredit': True,
                'hasOwnershipAdditionalCriteria': False
                },True)
    test_template("contract",{'paymentRate':'day'},False)

if input("Test nda y/N") == 'y':
    test_template("nda",{
                    "isEffectiveDateSpecific": True,
                    "isDisclosurePerpetual": False,
                    "isOwnerCompany": True,
                    "isRecipientCompany": False,
                    "ownerName": "Yannick",
                    "recipientName": "tispr",
                    "contractDated": "1/1/2019",
                    "contractEndWithinDays": 0,
                    "disclosureExpireInYears": 1,
                    "agreementExpireInYears": 1,
                    "lawState": "California",
                    #"recipientRepresentantName": "Jonathan",
                    "recipientRepresentantTitle": "Boss",
                    "ownerRole": "Client",
                    "ownerAddress": "8123 McConnell",
                    "ownerCity": "Westchester",
                    "ownerState": "California",
                    "ownerZipCode": "90045",
                    "recipientAddress": "8123 McConnell",
                    "recipientCity": "Santa Monica",
                    "recipientState": "California",
                    "recipientZipCode": "90045"
                },True)
    test_template("nda",{},False)

if input("Test invoice y/N") == 'y':
    test_template(
        "invoice",
        {
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
            "subtotal": 456.35,
            "totalAmount": 456.35,
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
        True,
        images = {
            "logo.png" : "https://s3-us-west-2.amazonaws.com/ds-temp-stg/latex_template_test/files/logo.png"
            })
    test_template("invoice",
        {
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
        },False,
    images = {
        "logo.png" : "https://s3-us-west-2.amazonaws.com/ds-temp-stg/latex_template_test/files/logo.png"
        })


for temp in ['contract','nda','invoice']:
    if input(f"Check all variables in {temp} y/N") =='y':
        latex_jinja_env = Environment(
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
            loader=FileSystemLoader(os.path.join('./', 'templates')))
        template_source = latex_jinja_env.loader.get_source(latex_jinja_env,  f'{temp}.tex')[0]
        parsed_content = latex_jinja_env.parse(template_source)
        print(meta.find_undeclared_variables(parsed_content))