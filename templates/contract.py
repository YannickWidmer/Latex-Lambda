
from num2words import num2words
from datetime import datetime

expected_values = ['clientName', 'consultantName', 'clientAddress', 'clientCity', 'clientState', 'clientZipCode','consultantAddress', 'consultantCity',
 'consultantState', 'consultantZipCode', 'isClientOwner', 'isEffectiveDateSpecific', 'contractEnd', 'lawState','isClientCompany', 'isConsultantCompany', 'paymentRate',
 'invoiceFrequency' ,'invoicePaymentDays','paymentPrice','invoiceFee','isConsultantPayingExpenses','hasExpenseAdditionalCriteria','isExpenseNeedPreApproval',
 'contractEndWithinDays','workscope','canConsultantUseWork','isClientNeedToCredit','hasOwnershipAdditionalCriteria']
additional = ['hasExpensePreApprovalPrice','expensePreApprovalPrice','estimatedWorkHoursADay', 'contractDated', 'ownershipAdditionalCriteria',
'clientRepresentantName','clientRepresentantTitle','consultantRepresentantName','consultantRepresentantTitle']

html_parameters = { # Parameters that can be set with their standard value
    'isEffectiveDateSpecific': False,
    'isClientOwner': True,
    'isClientCompany': True,
    'isConsultantCompany': False,
    'paymentRate' : 'flatFee',
    'invoiceFrequency':'weekly',
    'isConsultantPayingExpenses': True,
    'hasExpenseAdditionalCriteria':False,
    'isExpenseNeedPreApproval': False,
    'canConsultantUseWork': True,
    'isClientNeedToCredit':True,
    'hasOwnershipAdditionalCriteria': False,
    'hasExpensePreApprovalPrice': False
}

integers = ['invoicePaymentDays','contractEndWithinDays','estimatedWorkHoursADay']

two_decimal_numbers = [
    "paymentPrice", 'invoiceFee', 'expensePreApprovalPrice'
]
dates = [
    "contractDated", "contractEnd"
]

html_values = []
for key in expected_values + additional:
    if key not in html_parameters:
        html_values.append(key)

# To get state initials
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

        for key in html_parameters:
            if key in data and not type(data[key])  is type(html_parameters[key]):
                error += f"{key} has to be a {type(html_parameters[key])}.\n"
        if len(error) >0 :
            raise ValueError(error)

        if not data['isExpenseNeedPreApproval']:
            if 'hasExpensePreApprovalPrice' not in data:
                error += f"hasExpensePreApprovalPrice is not set while isExpenseNeedPreApproval is false.\n"
            elif data['hasExpensePreApprovalPrice']:
                if 'expensePreApprovalPrice' not in data:
                    error += f"expensePreApprovalPrice is not set but hasExpensePreApprovalPrice is true.\n"

        if data['paymentRate'] not in ['flatFee','hour','day','month']:
            error += f"paymentRate is not in [flatFee,hour,day,month].\n"
        if data['invoiceFrequency'] not in ['weekly','biWeekly','monthly','endOfProject']:
            error += f"invoiceFrequency is not in [weekly,biWeekly,monthly,endOfProject].\n"

        if type(data['isEffectiveDateSpecific']) is bool and data['isEffectiveDateSpecific']:
            if 'contractDated' not in data:
                error += "isEffectiveDateSpecific is true but no contractDated is given.\n"

        if len(error) >0:
            raise ValueError(error)

        # Ensuring that decimal numbers have exactly two decimals
        for key in two_decimal_numbers:
            if key in data:
                data[key] = '%.2f' % data[key]

        # Formating the dates
        for key in dates:
            if key in data:
                data[key] = datetime.strptime(data[key], "%Y-%m-%d %H:%M:%S.%f").strftime('%b %d, %Y')

        # Setting State initials
        for state in ['clientState', 'consultantState']:
            data[state+'Initials'] = us_state_abbrev[data[state]]

        # Creating word version of contractEndWithinDays
        for key in integers:
            if key in data:
                data[key + 'Word'] = num2words(data[key])

    else:
        for key in html_parameters:
            if key not in data:
                data[key] = html_parameters[key] # if not existant set to default value

        for key in html_values:
            # in html frontend replaces those so we don't pass values
            # instead we send placeholders $details.{name}
            data[key] = f"\$details.{key}"

    # defining consultantWithWithoutEmployees
    data['consultantWithWithoutEmployees'] = 'Consultant and its Employees' if data['isConsultantCompany'] else 'Consultant'

    # Passing a copy of to_pdf to the Jinja
    data['toPdf'] = to_pdf

    return data

