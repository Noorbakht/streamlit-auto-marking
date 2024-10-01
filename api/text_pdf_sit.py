from fpdf import FPDF
import random

random_id = f'Tender No. : TO{str(random.randint(2000000, 9999999))}'
font = 'Arial' 
fontsize = 11
# font = font
# fontsize = 12

class FPDF(FPDF):
    def header(self):
        # Logo
        self.image('sit_logo.png', 5, 5, 40)
        # Times bold 15
        self.set_font(font, '', 10)
        # Move to the right
        self.cell(160)
        # Title
        self.cell(30, 10, random_id, 0, 0, 'C')
        # Line break
        self.ln(25)

    # Page footer
    def footer(self):
        # Position at 1.5 cm from bottom
        self.set_y(-15)
        # Times italic 8
        self.set_font(font, '', 7)
        # Page number
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'C')

def gen_pdf(html_text, line_height=5, cell_padding=1):

    print(html_text)

    TABLE_DATA = [
    ]

    # Data preparation for PDF output
    rows = html_text.split("\n")
    
    for row in rows[0:-1]:
        cells = row.split("|")
        number = cells[1].strip()
        spec = cells[2].strip()
        TABLE_DATA.append((number, spec))
    
    print(TABLE_DATA)

    # Create the PDF and config format
    pdf = FPDF()
    
    pdf.set_margins(left=15, top=5, right=15)
    pdf.set_font(font, '', fontsize)

    for d in range(len(TABLE_DATA)):
        row = TABLE_DATA[d]
        print(row)
        if len(row[0]) == 1:
            pdf.add_page()
            pdf.ln(line_height)  # Add space above the section title
            pdf.set_font(font, 'B', fontsize)
            for i in range(len(row)):
                if i == len(row)-1:
                    pdf.multi_cell(0, 0, f'{row[i]}', 0)
                else:
                    pdf.cell(1, 0, '', 0)

        # Check if row is divider
        elif row[0][0] == '-':
            pass

        else:
            pdf.set_font(font, '', fontsize)
            for i in range(len(row)):
                if i == len(row)-1:
                    pdf.multi_cell(0, line_height + cell_padding, f'{row[i]}', 0)
                else:
                    pdf.ln(line_height)
                    pdf.cell(10 + cell_padding, line_height + cell_padding, f'{row[i]}', 0)

    return pdf.output(dest="S").encode("latin-1")