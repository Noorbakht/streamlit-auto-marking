from fpdf import FPDF
import random

random_id = f'Tender No. : TO{str(random.randint(2000000, 9999999))}'
# font = 'Arial' 
# fontsize = 11
font = 'Times'
fontsize = 12

class FPDF(FPDF):
    def header(self):
        # Set font
        self.set_font(font, '', 12)
        # Calculate the width of the page to center the title
        page_width = self.w - 2 * self.l_margin  # Total width minus margins
        # Title (Centered)
        self.cell(page_width, 10, 'Official (Closed), Non-Sensitive', 0, 1, 'C')  # 'C' for center alignment
        # Line break
        self.ln(2)

    def footer(self):
        # Set the position for the footer
        self.set_y(-15)

        # Draw a black line (from left margin to right margin)
        self.set_draw_color(0, 0, 0)  # Set color to black
        self.line(25, self.get_y(), self.w - 25, self.get_y())  # Draw line from left to right
        
        # Set the font
        self.set_font(font, '', 10)
        
        # Title on the bottom left
        self.cell(0, 10, 'Singapore Polytechnic', 0, 0, 'L')  # 'L' aligns text to the left
        
        # Page number on the bottom right
        self.cell(0, 10, 'Page ' + str(self.page_no()), 0, 0, 'R')  # 'R' aligns text to the right


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
    
    pdf.set_margins(left=25, top=5, right=25)
    pdf.add_page()
    pdf.set_font(font, '', fontsize)

    for d in range(len(TABLE_DATA)):
        row = TABLE_DATA[d]
        
        if len(row[0]) == 1:
            pdf.ln(10)  # Add space above the section title
            pdf.set_font(font, '', fontsize)
            for i in range(len(row)):
                if i == len(row)-1:
                    pdf.multi_cell(0, 0, f'{row[i]}', 0)
                else:
                    pdf.cell(1, 0, '', 0)
            pdf.ln(line_height)  # Add space above the section title

        # Check if row is divider
        elif row[0][0] == '-':
            pass

        else:
            pdf.set_font(font, '', fontsize)
            for i in range(len(row)):
                if i == len(row)-1:
                    pdf.multi_cell(0, line_height + cell_padding, f'{row[i]}', 0)
                else:
                    pdf.ln(2)
                    pdf.cell(10 + cell_padding, line_height + cell_padding, f'{row[i]}', 0)

    return pdf.output(dest="S").encode("latin-1")