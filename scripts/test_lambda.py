import base64
import json
import boto3
import os
import ast

def test_template(name,data, to_pdf):

    print(f"testing for template: {name}")
    payload = json.dumps({
        "name": name,
        "data": data,
        "to_pdf": to_pdf
        })

    print(payload)




    client = boto3.client('lambda')

    response = client.invoke(
        FunctionName="latex_compiler",
        InvocationType='RequestResponse',
        Payload=payload,
    )

    res = ast.literal_eval(response['Payload'].read().decode())

    print("############# RES ###############")

    print([key for key in res])

    if 'errorMessage' in res:
        print("\n############# ERROR MESSAGE ###############\n")
        print(res['errorMessage'])
        print("\n############# STACK TRACE   ###############\n")
        for trace in res['stackTrace']:
            print(": ".join([str(t) for t in trace]))

    else:
        print("############# write output ###############")
        print(res['path'])
        out_dir = './test_output/'
        if to_pdf:
            with open(os.path.join(out_dir, 'document.pdf'), 'wb+') as outfile:
                outfile.write(base64.b64decode(res['pdf']))
        else:
            try:
                with open(os.path.join(out_dir, 'document.html'), 'wb+') as outfile:
                    outfile.write(base64.b64decode(res['html']))
                with open(os.path.join(out_dir, 'document.css'), 'wb+') as outfile:
                    outfile.write(base64.b64decode(res['css']))
            except:
                print(res['stdout'])

        try:
            with open(os.path.join(out_dir, 'document.log'), 'wb+') as outfile:
                outfile.write(base64.b64decode(res['log']))

            with open(os.path.join(out_dir, 'document.tex'), 'w+') as outfile:
                outfile.write(res['tex'])

            with open(os.path.join(out_dir, 'log.txt'), 'w+') as outfile:
                outfile.write(res['stdout'])
        except:
            pass


if input("Test nda y/N") == 'y':
    test_template("nda",{
                    "ownerName": "Yannick",
                    "recipientName": "tispr",
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
                },False)

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
                },True)