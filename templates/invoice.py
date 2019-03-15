
from datetime import datetime

expected_values= [
    "senderName", "senderAddress", "senderCity",
    "senderStateInitials", "senderZipCode",
    "recipientName", "recipientAddress", "recipientCity",
    "recipientStateInitials", "recipientZipCode",
    "invoiceNumber", "taxesPercent", "discountAmount",
    "subtotal", "totalAmount", "feePercentage",
    "issuedDate", "dueDate"
]

additional_values = [
    "taxesAmount", "notes"
]

two_decimal_numbers = [
    "subtotal", "taxesPercent", "taxesAmount", "discountAmount",
    "totalAmount", "feePercentage"
]
dates = [
    "issuedDate", "dueDate"
]

def render(data, to_pdf):
    data['toPdf'] = to_pdf

    if True: # In case we create a pdf everything needs to be there
        # First the data validation
        error = ""
        for key in expected_values:
            if key not in data:
                error += f"The data does not contain {key}.\n"
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

        # Give Invoice number leading zeros
        data["invoiceNumber"] = str(data["invoiceNumber"]).zfill(6)
    else:
        for key in expected_values + two_decimal_numbers + dates:
            data[key] = f"\$details.{key}"

     # Formating the dates and numbers of entries, this is done for both formats
    new_entries = []
    for entry in data['entries']:
        entry['date'] = datetime.strptime(entry['date'], "%Y-%m-%d %H:%M:%S.%f").strftime('%d/%m/%Y')
        entry['rate'] = '%.2f' % entry['rate']
        entry['total'] = '%.2f' % entry['total']
        new_entries.append(entry)
    data['entries'] = new_entries

    return data