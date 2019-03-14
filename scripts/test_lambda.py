import base64
import json
import boto3
import os
import ast

def test_template(name,data, to_pdf, images = {}):

    print("##########################################################")
    print("##########################################################")
    print(f"############# testing for template: {name} ##############")
    print("##########################################################")
    print("##########################################################")
    payload = json.dumps({
        "name": name,
        "data": data,
        "to_pdf": to_pdf,
        "images" : images
        })

    print(payload)

    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName="latex_compiler",
        InvocationType='RequestResponse',
        Payload=payload,
    )

    res = json.loads(response['Payload'].read().decode())

    print("############# RES ###############")

    print([key for key in res])

    out_dir = './test_output/'

    for ending in ['pdf','css','log']:
        if ending in res:
            print(f"############# write document.{ending} ###############")
            with open(os.path.join(out_dir, f'document.{ending}'), 'wb+') as outfile:
                outfile.write(base64.b64decode(res[ending]))

    for ending in ['html','tex']:
        if ending in res:
            print(f"############# write document.{ending} ###############")
            with open(os.path.join(out_dir, f'document.{ending}'), 'w+') as outfile:
                outfile.write(res[ending])

    for out in ['stdout','stderr']:
        if out in res:
            print(f"############# write {out} to {out}.txt ###############")
            with open(os.path.join(out_dir, f'{out}.txt'), 'w+') as outfile:
                outfile.write(res[out])


    for tx in ['errorMessage','stackTrace','data','images']:
        if tx in res:
            print(f"\n############# PRINT {tx} ###############\n")
            print(res[tx])


if input("Test nda y/N") == 'y':
    test_template("nda",{
                    "isEffectiveDateSpecific": True,
                    "isDisclosurePerpetual": False,
                    "isOwnerCompany": False,
                    "isRecipientCompany": True,
                    "ownerName": "Yannick",
                    "recipientName": "tispr",
                    "contractDated": "1/1/2019",
                    "contractEndWithinDays": 7,
                    "lawState": "California",
                    #"recipientRepresentantName": "Jonathan",
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
                },True)
    test_template("nda",{},False)

if input("Test invoice y/N") == 'y':
    test_template("invoice",{
                    "ownerName": "Yannick",
                    "recipientName": "tispr",
                    "ownerAddress": "8123 McConnell",
                    "ownerState": "California",
                    "ownerZipCode": "90045",
                    "recipientAddress": "8123 McConnell",
                    "recipientState": "California",
                    "recipientZipCode": "90045"
    },True,
    images = {
        "logo.png" : "https://s3-us-west-2.amazonaws.com/ds-temp-stg/latex_template_test/files/logo.png"
        })
    test_template("invoice",{},False,
    images = {
        "logo.png" : "https://s3-us-west-2.amazonaws.com/ds-temp-stg/latex_template_test/files/logo.png"
        })

