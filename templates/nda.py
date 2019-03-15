
from num2words import num2words

expected_values = ['ownerName', 'recipientName', 'contractEndWithinDays', 'isEffectiveDateSpecific', 'isDisclosurePerpetual', 'lawState','isOwnerCompany', 'isRecipientCompany',
 'ownerAddress', 'ownerCity', 'ownerState', 'ownerZipCode', 'recipientAddress', 'recipientCity','recipientState', 'recipientZipCode', 'agreementExpireInYears']
additional = ['contractDated','disclosureExpireInYears','ownerRepresentantName', 'ownerRepresentantTitle', 'recipientRepresentantName', 'recipientRepresentantTitle']

html_parameters = { # Parameters that can be set with their standard value
    'isDisclosurePerpetual': False,
    'isOwnerCompany': True,
    'isRecipientCompany': False,
    'isEffectiveDateSpecific' : False
}
html_values = ['ownerName', 'recipientName', 'contractDated', 'contractEndWithinDays', 'lawState', 'ownerAddress', 'ownerCity', 'ownerState', 'ownerZipCode', 'recipientAddress', 'recipientCity','recipientState', 'recipientZipCode', 'ownerRepresentantName', 'ownerRepresentantTitle', 'recipientRepresentantName', 'recipientRepresentantTitle', 'disclosureExpireInYears']

# TO get state initials
us_state_abbrev = {
    'Alabama': 'AL',
    'Alaska': 'AK',
    'Arizona': 'AZ',
    'Arkansas': 'AR',
    'California': 'CA',
    'Colorado': 'CO',
    'Connecticut': 'CT',
    'Delaware': 'DE',
    'Florida': 'FL',
    'Georgia': 'GA',
    'Hawaii': 'HI',
    'Idaho': 'ID',
    'Illinois': 'IL',
    'Indiana': 'IN',
    'Iowa': 'IA',
    'Kansas': 'KS',
    'Kentucky': 'KY',
    'Louisiana': 'LA',
    'Maine': 'ME',
    'Maryland': 'MD',
    'Massachusetts': 'MA',
    'Michigan': 'MI',
    'Minnesota': 'MN',
    'Mississippi': 'MS',
    'Missouri': 'MO',
    'Montana': 'MT',
    'Nebraska': 'NE',
    'Nevada': 'NV',
    'New Hampshire': 'NH',
    'New Jersey': 'NJ',
    'New Mexico': 'NM',
    'New York': 'NY',
    'North Carolina': 'NC',
    'North Dakota': 'ND',
    'Ohio': 'OH',
    'Oklahoma': 'OK',
    'Oregon': 'OR',
    'Pennsylvania': 'PA',
    'Rhode Island': 'RI',
    'South Carolina': 'SC',
    'South Dakota': 'SD',
    'Tennessee': 'TN',
    'Texas': 'TX',
    'Utah': 'UT',
    'Vermont': 'VT',
    'Virginia': 'VA',
    'Washington': 'WA',
    'West Virginia': 'WV',
    'Wisconsin': 'WI',
    'Wyoming': 'WY',
}


def render(data, to_pdf):

    if to_pdf: # In case we create a pdf everything needs to be there
        # First the data validation
        error = ""
        for key in expected_values:
            if key not in data:
                error += f"The data does not contain {key}.\n"
        if len(error) >0 :
            raise ValueError(error)

        for key in ['isOwnerCompany','isRecipientCompany','isDisclosurePerpetual','isEffectiveDateSpecific']:
            if key in data and not type(data[key])  is bool:
                error += f"{key} has to be a boolean.\n"

        if type(data['isDisclosurePerpetual']) is bool and data['isDisclosurePerpetual']:
            if 'disclosureExpireInYears' not in data:
                error += "isDisclosurePerpetual is false but no disclosureExpireInYears is given.\n"
            if not type(data['disclosureExpireInYears']) is int:
                error += "disclosureExpireInYears is not an integer.\n"

        if type(data['isEffectiveDateSpecific']) is bool and data['isEffectiveDateSpecific']:
            if 'contractDated' not in data:
                error += "isEffectiveDateSpecific is true but no contractDated is given.\n"

        if len(error) >0 :
            raise ValueError(error)

            # Setting State initials
        for state in ['ownerState', 'recipientState']:
            data[state+'Initials'] = us_state_abbrev[data[state]]

        # Creating word version of contractEndWithinDays
        data['contractEndWithinDaysWord'] = num2words(data['contractEndWithinDays'])

    else:
        for key in html_parameters:
            if key not in data:
                data[key] = html_parameters[key] # if not existant set to default value

        for key in html_values:
            # in html frontend replaces those so we don't pass values
            # instead we send placeholders $details.{name}
            data[key] = f"\$details.{key}"

    # Computing isCompany
    data['isCompany'] =  ('Yes' if data['isOwnerCompany'] else 'No') + ('Yes' if data['isRecipientCompany'] else 'No')


    # Passing a copy of to_pdf to the Jinja
    data['toPdf'] = to_pdf

    return data

