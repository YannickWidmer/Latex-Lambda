import base64
import json
import boto3
import os
import ast


name = "nda"
to_pdf = True

payload = json.dumps({
    "name": name,
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
    "to_pdf": to_pdf
    })


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
    print("############# ERROR MESSAGE ###############\n\n")
    print(res['errorMessage'])
    print(res['stackTrace'])

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






