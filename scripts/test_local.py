from shutil import copyfile, rmtree
import os
import json
import sys
import os
sys.path.insert(0, os.getcwd() +'/latexlambda' )
sys.path.insert(0, os.getcwd() +'/latexlambda/render_modules' )
import lambda_function as lambdalatex

json_data = {
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
    }

name = "nda"

json_data = __import__(name).render(json_data)

rmtree("/tmp/templates")
os.mkdir("/tmp/templates")
copyfile(f"./templates/{name}.tex", f"/tmp/templates/template.tex")

out_dir = './output_test/'


rendered_tex = lambdalatex.render(json_data)
with open(os.path.join(out_dir, 'document.tex'), 'w+') as outfile:
    outfile.write(rendered_tex)



