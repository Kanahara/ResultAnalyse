

def alignment_rows(worksheet, alignment, rows):
    for column in range(1, worksheet.max_column + 1):
        for row in rows:
            worksheet.cell(row=row, column=column).alignment = alignment


def alignment_columns(worksheet, alignment, columns):
    for row in range(1, worksheet.max_row + 1):
        for column in columns:
            worksheet.cell(row=row, column=column).alignment = alignment
