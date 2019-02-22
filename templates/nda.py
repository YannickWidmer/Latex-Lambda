
from num2words import num2words

expected_values = ['ownerName', 'recipientName', 'contractDated', 'contractEndWithinDays',\
     'isDisclosurePerpetual', 'lawState','isOwnerCompany', 'isRecipientCompany', 'ownerRole',\
         'ownerAddress', 'ownerState', 'ownerZipCode', 'recipientAddress', 'recipientState', 'recipientZipCode']
additional = ['disclosureExpireInYears','ownerRepresentantName', 'ownerRepresentantTitle', 'recipientRepresentantName', 'recipientRepresentantTitle']

expected_output = ['ownerDescription', 'recipientDescription','isCompany', 'contractEndWithinDaysWord', 'ownerSignDate', 'signatureOwner', 'recipientSignDate', 'signatureRecipient']
def render(data, to_pdf):

    # First the data validation
    error = ""
    for key in expected_values:
        if key not in data:
            error += f"The data does not contain {key}.\n"
    if len(error) >0 :
        raise ValueError(error)

    for key in ['isOwnerCompany','isRecipientCompany','isDisclosurePerpetual']:
        if key in data and not type(data[key])  is bool:
            error += f"{key} has to be a boolean.\n"

    if type(data['isDisclosurePerpetual']) is bool and data['isDisclosurePerpetual']:
        if 'disclosureExpireInYears' not in data:
            error += "isDiclosurePerpetual is false but no disclosureExpireInYears is given.\n"
        if not type(data['disclosureExpireInYears']) is int:
            error += "disclosureExpireInYears is not an integer.\n"

    if data['isOwnerCompany'] and ('ownerRepresentantName' not in data or 'ownerRepresentantTitle' not in data):
        error += "Since isOwnerCompany is true, the values ownerRepresentantName and ownerRepresentantTitle are mandatory.\n"

    if data['isRecipientCompany'] and ('recipientRepresentantName' not in data or 'recipientRepresentantTitle' not in data):
        error += "Since isRecipientCompany is true, the values recipientRepresentantName and recipientRepresentantTitle are mandatory.\n"

    if not data['ownerRole'] in ['Client','Consultant']:
        error += "ownerRole has to be one of 'Client', 'Consultant'.\n"

    if len(error) >0 :
        raise ValueError(error)

    # Computing some fields

    data['contractEndWithinDaysWord'] = num2words(data['contractEndWithinDays'])

    if data['ownerRole'] == 'Client':
        data['isCompany'] = ('Yes' if data['isRecipientCompany'] else 'No') + ('Yes' if data['isOwnerCompany'] else 'No')
    else:
        data['isCompany'] = ('Yes' if data['isOwnerCompany'] else 'No') + ('Yes' if data['isRecipientCompany'] else 'No')

    for key in ['ownerSignDate', 'signatureOwner', 'recipientSignDate','signatureRecipient']:
        data[key] = 'tbd'

    if data['isOwnerCompany']:
        inner = f"a {data['ownerState']} corporation with offices at"
    else:
        inner = "an individual residing at"
    data['ownerDescription'] = f"{data['ownerName']}, " + inner + f" {data['ownerAddress']}, {data['ownerState']}, {data['ownerZipCode']}" + ' (the "{\\bf '\
        + data['ownerRole'] +'}")'

    if data['isRecipientCompany']:
        inner = f"a {data['recipientState']} corporation with offices at"
    else:
        inner = "an individual residing at"
    data['recipientDescription'] = f"{data['recipientName']}, " + inner + f" {data['recipientAddress']}, {data['recipientState']}, {data['recipientZipCode']}"\
        + ' (the "{\\bf '+ ('Client' if data['ownerRole'] == 'Consultant' else 'Consultant') +'}")'

    data['toPdf'] = to_pdf

    return data