

def number_format_rows(worksheet, number_format, rows):
    for column in range(1, worksheet.max_column + 1):
        for row in rows:
            worksheet.cell(row=row, column=column).number_format = number_format


def number_format_columns(worksheet, number_format, columns):
    for row in range(1, worksheet.max_row + 1):
        for column in columns:
            worksheet.cell(row=row, column=column).number_format = number_format
