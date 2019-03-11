# Templates

The payload for the lambda is structured like in the following example

``` python
payload = json.dumps({
    "name": "nda",
    "data": {
            "ownerName": "Yannick:Owner",
            "recipientName": "tispr:Recipient"
        },
    "to_pdf": True
    })
```

Each template expects different key value pairs in `data`. We distinguish between parameters which change the structure of the document and variables which are simply copied into the document at various places. Variables are made editable in the web version of the document this is why in the html version (`"to_pdf": False`) they are replaced  with placeholders. The placeholders are constituted of a `$` sign followed by `details.` then the name of the variable. As an example the variable `ownerName` will be `$details.ownerName`.

As a consequence when generating the html version an empty data object can be sent and only the set parameters will have any influence on the outcome. If parameters are not sent they will be set to their default value. For the pdf version all parameters are expected, depending on the parameters the values are then expected or not.

## NDA

### Parameters

| name | default value for  html version |
|---|---|
| isDisclosurePerpetual | False |
| isEffectiveDateSpecific |  False |
| isOwnerCompany |  True |
| isRecipientCompany | False|


### Values

|name| type | condition for necessity|
|---|---|---|
|ownerName| string  | always |
|recipientName| string  | always |
|contractDated | string  (we could make it a date but then I need to format it)| when  isEffectiveDateSpecific is True|
|contractEndWithinDays | integer (represent days) | always |
| disclosureExpireInYears| integer | if isDisclosurePerpetual is False |
| lawState | string | always|
| ownerAddress| string | always |
| ownerCity | string  | always |
| ownerState  | string  | always |
|ownerZipCode | string (can be int) | always |
| recipientAddress | string  | always |
| ownerCity | string  | always |
| recipientState | string  | always |
| recipientZipCode | string (can be int) | always |
| ownerRepresentantName | string  | never |
| ownerRepresentantTitle | string  | never |
| recipientRepresentantName | string | never |
| recipientRepresentantTitle | string | never |

The last four variables are only used in the signature fields when the according party is a company, if they don't appear lines will be placed instead.