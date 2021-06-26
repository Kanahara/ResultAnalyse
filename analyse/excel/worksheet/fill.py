

def fill_rows(worksheet, fill, rows):
    for column in range(1, worksheet.max_column + 1):
        for row in rows:
            worksheet.cell(row=row, column=column).fill = fill


def fill_columns(worksheet, fill, columns):
    for row in range(1, worksheet.max_row + 1):
        for column in columns:
            worksheet.cell(row=row, column=column).fill = fill