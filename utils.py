import matplotlib.pyplot as plt
import io, os
from matplotlib.patches import PathPatch
from matplotlib.path import Path
import numpy as np
import json
from matplotlib.patches import FancyBboxPatch
from PIL import ImageColor


def read_json_file(file_path):
    """
    Reads a JSON file and returns its contents as a Python dictionary.

    Args:
        file_path: The path to the JSON file.

    Returns:
        A Python dictionary containing the data from the JSON file.
    """
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"Error: File '{file_path}' not found.")
        return None

    # Check if the file has a .json extension
    if not file_path.lower().endswith(".json"):
        print(f"Error: '{file_path}' is not a JSON file.")
        return None
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in file '{file_path}': {e}")
        return None



def all_elements_empty(lst):
    return all(x == "" for x in lst)



def create_donut_chart(values, colors):
    """
    Creates a donut-shaped pie chart and returns the image buffer.

    Parameters:
    values (list): Proportions for the pie chart sections.
    colors (list): Colors for the pie chart sections.

    Returns:
    io.BytesIO: Buffer containing the image data.
    """
    # explode = [0.02, 0.02, 0.02]  # One value for each wedge
    # Plotting the donut-shaped pie chart

    # if all_elements_empty(values):
        # values = [0, 50]
        # colors = ["#000000","#000000"]

    wedgeprops = {
    'edgecolor': 'white',  # Set edge color
    'width': 0.55,
    'linewidth': 3,  # Set edge width
    # 'linestyle': '-',      # Solid line
    # 'capstyle':'round',   # Add rounded cap (requires customization)   
    }  
    print(values)

    plt.figure(figsize=(4, 4))
    plt.pie(values, colors=colors, startangle=90, wedgeprops=wedgeprops, explode=None)

    # fig, ax = plt.subplots(figsize=(4, 4))
    # wedges, _ = ax.pie(values, colors=colors, startangle=90, wedgeprops={'edgecolor': 'white','linewidth': 3, 'width': 0.48})

    # Saving the pie chart to a buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', pad_inches=0, transparent=True)
    plt.close()
    buf.seek(0)

    return buf



def create_bar_chart_image(val, iter):

    save_path = f"temp_files/horizontal_bar_chart_{iter}.png"

    if isinstance(val, str) and '%' in val:
        val = float(val.replace('%', ''))

    # Create the directory if it does not exist
    directory = os.path.dirname(save_path)
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)  # Ensures all intermediate directories are created

    # The values for left, middle, and right parts of the chart
    left_right = (100 - val) / 2  # Left and right parts are equal
    values = [left_right, val, left_right]  # Total sum will always be 100%
    
    # Define colors for each part
    colors = ['#C8BFF4', '#9E91D2', '#8A81B8']
    # Normalize values
    total = sum(values)
    normalized_values = [value / total for value in values]

    # Create the bar chart
    fig, ax = plt.subplots(figsize=(8, 2))
    left_offset = 0

    for value, color in zip(normalized_values, colors):
        ax.barh(0, value, left=left_offset, color=color) 
        left_offset += value
    ax.set_xlim(0, 1)
    ax.axis('off')

    # Save the chart as an image
    plt.tight_layout()
    plt.savefig(save_path, dpi=300, pad_inches=0, transparent=True)
    plt.close()
    return save_path


def draw_gradient(self, x, y, width, height, start_color, end_color):
        """Draw a horizontal gradient using overlapping thin rectangles."""
        steps = 200  # Increase steps for smoother gradient
        r1, g1, b1 = start_color
        r2, g2, b2 = end_color

        step_width = width / steps  # Width of each gradient step

        for i in range(steps):
            # Calculate the interpolated color
            r = r1 + (r2 - r1) * i / steps
            g = g1 + (g2 - g1) * i / steps
            b = b1 + (b2 - b1) * i / steps

            # Set the fill color
            self.set_fill_color(int(r), int(g), int(b))

            # Draw a slightly overlapping rectangle
            self.rect(x + i * step_width, y, step_width + 0.5, height, 'F')  # Add slight overlap

def format_amount(val):
    # Handle None or empty strings
    if val is None or val == "":
        return "₹ 0.00"
    return f"₹ {val}"

        # # Convert string to float if needed
        # numeric_value = float(amount)

        # # Format with two decimal places
        # if numeric_value >= 1_00_000:  # Values in lakhs or more
        #     formatted_value = f"{numeric_value / 1_00_000:.2f}L"
        # elif numeric_value >= 1_000:  # Values in thousands or more
        #     formatted_value = f"{numeric_value / 1_000:.2f}K"
        # else:
        #     formatted_value = f"{numeric_value:.2f}"  # No suffix for smaller values

        # # Add the rupee symbol and return
        # return f"₹ {formatted_value}"

# Green Gradient Rectangle. #F0FDF5 #00BC44
def print_gradient_on_pdf_page(pdf, y_pos, image):
    pdf.draw_gradient(px2MM(120), px2MM(y_pos), px2MM(1680), px2MM(50), hex2RGB("#00BC44"), hex2RGB("#F0FDF5"))
    pdf.image(image, px2MM(135), px2MM(y_pos + 10.79), px2MM(30.00), px2MM(27.5))
    pdf.set_font('Inter-SemiBold', size=px2pts(14))
    pdf.set_text_color(*hex2RGB("#FFFFFF"))
    pdf.set_xy(px2MM(182), px2MM(y_pos + 13.79))
    # pdf.cell(px2MM(328), px2MM(23), "Excellent! You have no funds in the Regular plan", align="L")


# Unit conversionss
def px2MM(val):
    # Sauce: https://www.figma.com/community/plugin/841435609952260079/Unit-Converter
    #   return val * (25.4 / 72)
    return val * 0.264583333338


def px2pts(val):
    return val * 0.75


def hex2RGB(val):
    return list(ImageColor.getcolor(val, "RGB"))


# //*-----Index Text of Page--**////
def index_text(pdf, col):
    # //*---Page Index Number----*//
    pdf.set_xy(px2MM(1870), px2MM(1018))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_text_color(*hex2RGB(col))
    pdf.cell(px2MM(20), px2MM(42), str(pdf.page_no()), align='R')


def mutual_fund_type_method(pdf, warning_logo , direct_fund_percentage, regular_fund_percentage, direct_fund_value, regular_fund_value, conditional_text, y):
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(689), px2MM(y), px2MM(540.48), px2MM(197.65), 'F')

    pdf.set_xy(px2MM(719.05), px2MM(y + 24.4))
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_font('Inter-Regular', size=px2pts(14.641))
    pdf.cell(px2MM(145), px2MM(29), "Mutual Fund Type", align="L")
    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_xy(px2MM(737.96), px2MM(y + 76.86))
    pdf.cell(px2MM(52.461), px2MM(15), "Direct", align="L")
    pdf.set_xy(px2MM(737.96), px2MM(y + 111.38))
    pdf.cell(px2MM(52.461), px2MM(15), "Regular", align="L")
    pdf.set_fill_color(*hex2RGB('#7FCDA4'))
    pdf.rect(px2MM(721.05), px2MM(y + 81.27), px2MM(8), px2MM(8), 'F')
    pdf.set_fill_color(*hex2RGB('#FF8B81'))
    pdf.rect(px2MM(721.05), px2MM(y + 113.82), px2MM(8), px2MM(8), 'F')

    # Input Should Be Dynamic From The Json File Provided By Backend.
    direct_fund_clean_percentage = direct_fund_percentage.replace("%", "")
    regular_fund_clean_percentage = regular_fund_percentage.replace("%", "")

    values = [direct_fund_clean_percentage, regular_fund_clean_percentage]
    # Direct, Regular
    colors = ['#7FCDA4', '#FF8B81']
    conditional_colors = ['#FF8B81', '#FF8B81']
    buf = create_donut_chart(values=values, colors=conditional_colors if not direct_fund_value and regular_fund_value else colors)
    pdf.image(buf, px2MM(1060.66), px2MM(y + 39.04), w=px2MM(118), h=px2MM(118))
    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_xy(px2MM(824.6), px2MM(y + 76.86))
    pdf.cell(px2MM(40), px2MM(15), direct_fund_percentage if direct_fund_percentage else "0%", align="L")
    pdf.set_xy(px2MM(824.6), px2MM(y + 113.86))
    pdf.cell(px2MM(40), px2MM(15), regular_fund_percentage if direct_fund_percentage else "0%", align="L")
    pdf.set_text_color(*hex2RGB("#718096"))
    pdf.set_xy(px2MM(900.45), px2MM(y + 76.86))
    pdf.cell(px2MM(58.56), px2MM(15), format_amount(direct_fund_value), align="L")
    pdf.set_xy(px2MM(900.45), px2MM(y + 113.86))
    pdf.cell(px2MM(56.56), px2MM(15), format_amount(regular_fund_value), align="L")
    pdf.image(warning_logo, x=px2MM(721.05), y=px2MM(y + 151.94), w=px2MM(18.3), h=px2MM(15.8))
    pdf.set_font('Inter-Regular', size=px2pts(17.081))
    pdf.set_text_color(*hex2RGB("#DC2626"))
    pdf.set_xy(px2MM(737.96 + 8.45), px2MM(y + 149.63))
    pdf.cell(px2MM(295.25), px2MM(22), conditional_text, align="L")


def container6_v2(pdf, amount, y):
    amount = format_amount(amount)
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(1259.52), px2MM(y), px2MM(540.48), px2MM(197.65), "F")

    pdf.set_font('Inter-Regular', size=px2pts(14))
    pdf.set_text_color(*hex2RGB("#898B90"))
    pdf.set_xy(px2MM(1289), px2MM(y + 76.18))
    pdf.multi_cell(px2MM(175), px2MM(23), "Your Losses in \nCommission (Annual)", align="L")

    pdf.set_font('Inter-Bold', size=px2pts(32))
    pdf.set_text_color(*hex2RGB("#F87171"))
    pdf.set_xy(px2MM(1589), px2MM(y + 88.18))
    # pdf.cell(px2MM(175),px2MM(23), "₹ 8.3K",align = "L")
    pdf.cell(px2MM(175), px2MM(23), amount, align="L")

    pdf.set_font('Inter-Light', size=px2pts(14))
    pdf.set_text_color(*hex2RGB("#898B90"))
    dynamic_x_padding_for_annual_income = 1693 if len(amount) <=6 else 1708
    # pdf.set_xy(px2MM(1693), px2MM(y + 95.18))
    pdf.set_xy(px2MM(dynamic_x_padding_for_annual_income), px2MM(y + 95.18))
    pdf.cell(px2MM(47), px2MM(19), "Approx", align="L")


def container_fourth_method(pdf, warning_logo, direct_fund_value , direct_fund_percentage, regular_fund_value, regular_fund_percentage, conditional_text):
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(120), px2MM(417.65), px2MM(539.25), px2MM(197.65), 'F')
    pdf.set_xy(px2MM(149), px2MM(442))
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_font('Inter-Regular', size=px2pts(14.641))
    pdf.cell(px2MM(145), px2MM(29), "Mutual Fund Type", align="L")
    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_xy(px2MM(167), px2MM(494.51))
    pdf.cell(px2MM(52.461), px2MM(15), "Direct", align="L")
    pdf.set_xy(px2MM(167), px2MM(529.03))
    pdf.cell(px2MM(52.461), px2MM(15), "Regular", align="L")
    pdf.set_fill_color(*hex2RGB('#7FCDA4'))
    pdf.rect(px2MM(149), px2MM(498), px2MM(8), px2MM(8), 'F')
    pdf.set_fill_color(*hex2RGB('#FF8B81'))
    pdf.rect(px2MM(149), px2MM(531.47), px2MM(8), px2MM(8), 'F')
  
    # Input Should Be Dynamic From The Json File Provided By Backend.
    direct_fund_clean_percentage = direct_fund_percentage.replace("%", "") 
    regular_fund_clean_percentage = regular_fund_percentage.replace("%", "")
    values = [direct_fund_clean_percentage, regular_fund_clean_percentage]
    # Direct, Regular
    colors = ['#7FCDA4', '#FF8B81']
    conditional_colors = ['#FF8B81', '#FF8B81']
    buf = create_donut_chart(values=values, colors=conditional_colors if not direct_fund_value and regular_fund_value else colors)
    pdf.image(buf, px2MM(503), px2MM(456.69), w=px2MM(118), h=px2MM(118))
    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_xy(px2MM(258.7), px2MM(494.51))
    pdf.cell(px2MM(40), px2MM(15), direct_fund_percentage, align="L")
    pdf.set_xy(px2MM(258.9), px2MM(529.03))
    pdf.cell(px2MM(40), px2MM(15), regular_fund_percentage, align="L")
    pdf.set_text_color(*hex2RGB("#718096"))
    pdf.set_xy(px2MM(338), px2MM(494.51))
    pdf.cell(px2MM(58.56), px2MM(15), direct_fund_value, align="L")
    pdf.set_xy(px2MM(338), px2MM(529.03))
    pdf.cell(px2MM(56.56), px2MM(15), regular_fund_value, align="L")
    pdf.image(warning_logo, x=px2MM(150.5), y=px2MM(569.59), w=px2MM(18.3), h=px2MM(15.8))
    pdf.set_font('Inter-Regular', size=px2pts(17.081))
    pdf.set_text_color(*hex2RGB("#DC2626"))
    pdf.set_xy(px2MM(178.5), px2MM(566.47))
    # conditional_text = "Attention! All your funds are in Regular Plan" if not direct_fund_value and regular_fund_value else "Regular funds found in your portfolio"
    # pdf.cell(px2MM(295.25),px2MM(22),"Regular funds found in your portfolio", align="L")
    pdf.cell(px2MM(295.25), px2MM(22), conditional_text, align="L")


def container1(pdf , NoOfMutualFundsValue, y):
    # <__________________________________________________________________________________>
    # 1st Box
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(120),px2MM(y), px2MM(247),px2MM(197),'F')

    pdf.set_font('Inter-Regular', size=px2pts(17.08))
    pdf.set_text_color(*hex2RGB("#898B90"))
    pdf.set_xy(px2MM(144.4), px2MM(y + 24.4))
    pdf.cell(px2MM(163), px2MM(29), "No. of Mutual Funds", align="L")

    if NoOfMutualFundsValue <= 6:
        pdf.set_font('Inter-Bold', size=px2pts(39.041))
        pdf.set_text_color(*hex2RGB("#0B9826"))
        pdf.set_xy(px2MM(144.4), px2MM(y + 69.54))
        pdf.cell(px2MM(165.9), px2MM(47), str(NoOfMutualFundsValue), align="L")
    
        pdf.set_font('Inter-Light', size=px2pts(17.081))
        pdf.set_text_color(*hex2RGB("#898B90"))
        pdf.set_xy(px2MM(144.4), px2MM(y + 128.74))
        pdf.multi_cell(w=px2MM(200), h=px2MM(23.5), txt="Excellent! You have an optimum portfolio", align="L")

    elif NoOfMutualFundsValue >= 7 and NoOfMutualFundsValue <= 10:
        pdf.set_font('Inter-Bold', size=px2pts(39.041))
        pdf.set_text_color(*hex2RGB("#F97C16"))
        pdf.set_xy(px2MM(144.4),  px2MM(y + 69.54))
        pdf.cell(px2MM(165.9), px2MM(47), str(NoOfMutualFundsValue), align="L")

        pdf.set_font('Inter-Light', size=px2pts(17.081))
        pdf.set_text_color(*hex2RGB("#898B90"))
        pdf.set_xy(px2MM(144.4), px2MM(y + 128.74))
        pdf.cell(w=px2MM(200), h=px2MM(23.5), txt="It is best to keep the", align="L")
        pdf.set_xy(px2MM(144.4), px2MM(y + 128.74 + 23.7))
        pdf.cell(w=px2MM(200), h=px2MM(23.5), txt="count to", align="L")
        
        pdf.set_font('Inter-SemiBold', size=px2pts(17.081))
        pdf.set_xy(px2MM(144.4 + 71), px2MM(y + 128.74 + 23.7))
        pdf.cell(w=px2MM(200), h=px2MM(23.5), txt="6 or less", align="L")
        
    elif NoOfMutualFundsValue >= 10:
        pdf.set_font('Inter-Bold', size=px2pts(39.041))
        pdf.set_text_color(*hex2RGB("#F50018"))
        pdf.set_xy(px2MM(144.4), px2MM(y + 69.54))
        pdf.cell(px2MM(165.9), px2MM(47), str(NoOfMutualFundsValue), align="L")
        pdf.set_font('Inter-Light', size=px2pts(17.081))
        pdf.set_text_color(*hex2RGB("#898B90"))
        pdf.set_xy(px2MM(144.4),  px2MM(y + 120.74))
        pdf.multi_cell(w=px2MM(200), h=px2MM(23.5), txt="Attention! You must consolidate your portfolio on priority", align="L")

def container2(pdf,conditioal_fill_color,set_text_color, avg_portfolio_score_status, avg_portfolio_score_value,y):
    status = ["HIGH","MEDIUM","LOW"]
    pdf.set_fill_color(*hex2RGB(conditioal_fill_color))
    pdf.rect(px2MM(396),px2MM(y), px2MM(263.53),px2MM(197.65),'F')

    # <__________________________________________________________________________________>
        
    pdf.set_font('Inter-Regular', size=px2pts(17.08))
    pdf.set_xy(px2MM(426.23), px2MM(y + 24.4))
    # pdf.set_text_color(*hex2RGB("#16A349"))
    pdf.set_text_color(*hex2RGB(set_text_color))
    pdf.cell(px2MM(192),px2MM(29), "Avg Portfolio Score",align = "L")

    pdf.set_font('Inter-Bold', size=px2pts(39.041))
    # pdf.set_text_color(*hex2RGB("#16A349")) 
    pdf.set_text_color(*hex2RGB(set_text_color))
    pdf.set_xy(px2MM(426.43), px2MM(y + 70.48))
    # pdf.cell(px2MM(165.9),px2MM(47),"72", align="L")
    pdf.cell(px2MM(165.9),px2MM(47.58),str(avg_portfolio_score_value), align="L")

    pdf.set_font('Inter-Bold', size=px2pts(12.2))
    # pdf.set_text_color(*hex2RGB("#16A349"))
    pdf.set_text_color(*hex2RGB(set_text_color))

    x_padding = 460.6 if len(avg_portfolio_score_value) == 1 else 483 if len(avg_portfolio_score_value) == 2 else 505
    # pdf.set_xy(px2MM(472.6), px2MM(276.78))
    pdf.set_xy(px2MM(x_padding), px2MM(y + 88.78))
    pdf.cell(px2MM(55),px2MM(29),avg_portfolio_score_status, align="L")

    pdf.set_font('Inter-Regular', size=px2pts(17.08))
    # pdf.set_text_color(*hex2RGB("#70AB87"))
    pdf.set_text_color(*hex2RGB(set_text_color))
    pdf.set_xy(px2MM(426.23), px2MM(y + 130.26))
    pdf.multi_cell(w=px2MM(234.24),h=px2MM(22),txt="Based on the 1 Finance proprietary research", align="L")
    # <__________________________________________________________________________________>

def container3(pdf, equity_percentage , equity_amount ,debt_percentage, debt_amount, other_percentage, other_amount, y):

    # Format amounts with the rupee symbol
    equity_amount = format_amount(equity_amount)
    debt_amount = format_amount(debt_amount)
    other_amount = format_amount(other_amount)

    # 3rd Container
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(689),px2MM(y), px2MM(540.48),px2MM(197.65),'F')

    pdf.set_font('Inter-Regular', size=px2pts(17.08))
    pdf.set_text_color(*hex2RGB("#898B90"))
    pdf.set_xy(px2MM(719.05), px2MM(y + 20))
    pdf.cell(px2MM(254),px2MM(29), "Mutual fund Portfolio Allocation",align = "L")

    pdf.set_fill_color(*hex2RGB('#B4A4FF'))
    pdf.rect(px2MM(719),px2MM(y + 65.97), px2MM(8),px2MM(8),'F')

    pdf.set_fill_color(*hex2RGB('#FFDB80'))
    pdf.rect(px2MM(719),px2MM(y + 93.66), px2MM(8),px2MM(8),'F')

    pdf.set_fill_color(*hex2RGB('#82DBC6'))
    pdf.rect(px2MM(719),px2MM(y + 121.34), px2MM(8),px2MM(8),'F')

    pdf.set_font('Inter-Regular', size=px2pts(14.641))
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_xy(px2MM(736.96), px2MM(y + 63))
    pdf.cell(px2MM(43),px2MM(15), "Equity",align = "L")

    pdf.set_xy(px2MM(736.96), px2MM(y + 91))
    pdf.cell(px2MM(43),px2MM(15), "Debt",align = "L")

    pdf.set_xy(px2MM(736.96), px2MM(y + 119))
    pdf.cell(px2MM(43),px2MM(15), "Other",align = "L")


    pdf.set_font('Inter-SemiBold', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466")) 
    pdf.set_xy(px2MM(824.8), px2MM(y + 63))
    # pdf.cell(w=px2MM(31.72),h=px2MM(15),txt="54%", align="R")
    pdf.cell(w=px2MM(31.72),h=px2MM(15),txt=equity_percentage if equity_percentage else "0%", align="R")


    pdf.set_font('Inter-SemiBold', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466")) 
    pdf.set_xy(px2MM(824.8), px2MM(y + 91))
    # pdf.cell(w=px2MM(31.72),h=px2MM(15),txt="40%", align="R")
    pdf.cell(w=px2MM(31.72),h=px2MM(15),txt=debt_percentage if debt_percentage else "0%", align="R")


    pdf.set_font('Inter-SemiBold', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466")) 
    pdf.set_xy(px2MM(825.8), px2MM(y + 119))
    # pdf.cell(w=px2MM(31.72),h=px2MM(15),txt="6%", align="R")
    pdf.cell(w=px2MM(31.72),h=px2MM(15),txt=other_percentage if other_percentage else "0%", align="R")


        

    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#718096")) 
    pdf.set_xy(px2MM(900.45), px2MM(y + 63))
    # pdf.cell(w=px2MM(70.76),h=px2MM(15),txt="₹ 12.46L", align="R")
    pdf.cell(w=px2MM(70.76),h=px2MM(15),txt=equity_amount, align="R")



    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#718096")) 
    pdf.set_xy(px2MM(900.45), px2MM(y + 91))
    # pdf.cell(w=px2MM(70.76),h=px2MM(15),txt="₹ 6.08L", align="R")
    pdf.cell(w=px2MM(70.76),h=px2MM(15),txt=debt_amount, align="R")


    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#718096")) 
    pdf.set_xy(px2MM(900.45), px2MM(y + 119))
    # pdf.cell(w=px2MM(70.76),h=px2MM(15),txt="₹ 98K", align="R")
    pdf.cell(w=px2MM(70.76),h=px2MM(15),txt=other_amount, align="R")

    other_percentage_clean = other_percentage.replace("%","")
    debt_percentage_clean = debt_percentage.replace("%","")
    equity_percentage_clean = equity_percentage.replace("%","")

    values = [other_percentage_clean, debt_percentage_clean, equity_percentage_clean]

    other_color = "#82DBC6"
    dept_color = "#FFD66F"
    equity_color =  "#AB99FF"


    # Other, Dept , Equity
    colors = [other_color, dept_color , equity_color]

    dotnut_pie = create_donut_chart(values, colors)
    pdf.image(dotnut_pie, x=px2MM(1060), y=px2MM(y + 32), w=px2MM(118.34), h=px2MM(118.34))

def container4(pdf, large_cap_percentage, large_cap_amount , mid_cap_percentage ,mid_cap_amount, small_cap_percentage, small_cap_amount, y):

    if large_cap_percentage == '0%' or mid_cap_percentage == '0%' or small_cap_percentage == '0%':
        return
    # Format amounts with the rupee symbol
    large_cap_amount = format_amount(large_cap_amount)
    mid_cap_amount = format_amount(mid_cap_amount)
    small_cap_amount = format_amount(small_cap_amount)


    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(1259.52),px2MM(y), px2MM(540.48),px2MM(197.65),"F")

    pdf.set_font('Inter-Regular', size=px2pts(14.641))
    pdf.set_text_color(*hex2RGB("#898B90"))
    pdf.set_xy(px2MM(1288.05), px2MM(y + 20))
    pdf.cell(px2MM(279),px2MM(23), "Equity Market Cap Distribution (Domestic)",align = "L")

    pdf.set_fill_color(*hex2RGB('#7C5FF2'))
    pdf.rect(px2MM(1288.8),px2MM(y + 65.97), px2MM(8),px2MM(8),'F')

    pdf.set_fill_color(*hex2RGB('#A792FF'))
    pdf.rect(px2MM(1288.8),px2MM(y + 93.63), px2MM(8),px2MM(8),'F')
            
    pdf.set_fill_color(*hex2RGB('#C6B9FF'))
    pdf.rect(px2MM(1288.8),px2MM(y + 121.64), px2MM(8),px2MM(8),'F')

            
    pdf.set_font('Inter-Regular', size=px2pts(14.641))
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_xy(px2MM(1306.72), px2MM(y + 63))
    pdf.cell(px2MM(40),px2MM(15), "Large",align = "L")

    pdf.set_xy(px2MM(1306.72), px2MM(y + 91))
    pdf.cell(px2MM(26),px2MM(15), "Mid",align = "L")

    pdf.set_xy(px2MM(1306.72), px2MM(y + 119))
    pdf.cell(px2MM(38),px2MM(15), "Small",align = "L")


    pdf.set_font('Inter-SemiBold', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466")) 
    pdf.set_xy(px2MM(1390.64), px2MM(y + 63))
    # pdf.cell(w=px2MM(31.72),h=px2MM(15),txt="54%", align="R")
    pdf.cell(w=px2MM(31.72),h=px2MM(15),txt=large_cap_percentage if large_cap_percentage else "0%", align="R")



    pdf.set_font('Inter-SemiBold', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466")) 
    pdf.set_xy(px2MM(1390.64), px2MM(y + 91))
    # pdf.cell(w=px2MM(31.72),h=px2MM(15),txt="40%", align="R")
    pdf.cell(w=px2MM(31.72),h=px2MM(15),txt=mid_cap_percentage if mid_cap_percentage else "0%", align="R")



    pdf.set_font('Inter-SemiBold', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#425466")) 
    pdf.set_xy(px2MM(1390.64), px2MM(y + 119))
    # pdf.cell(w=px2MM(31.72),h=px2MM(15),txt="6%", align="R")
    pdf.cell(w=px2MM(31.72),h=px2MM(15),txt=small_cap_percentage if small_cap_percentage else "0%", align="R")




    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#718096")) 
    pdf.set_xy(px2MM(1466.29), px2MM(y + 63))
    # pdf.cell(w=px2MM(70.76),h=px2MM(15),txt="₹ 12.46L", align="R")
    pdf.cell(w=px2MM(70.76),h=px2MM(15),txt=large_cap_amount, align="R")



    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#718096")) 
    pdf.set_xy(px2MM(1466.2), px2MM(y + 91))
    # pdf.cell(w=px2MM(70.76),h=px2MM(15),txt="₹ 6.08L", align="R")
    pdf.cell(w=px2MM(70.76),h=px2MM(15),txt=mid_cap_amount, align="R")


    pdf.set_font('Inter-Regular', size=px2pts(14.27))
    pdf.set_text_color(*hex2RGB("#718096")) 
    pdf.set_xy(px2MM(1466.2), px2MM(y + 119))
    # pdf.cell(w=px2MM(70.76),h=px2MM(15),txt="₹ 98K", align="R")
    pdf.cell(w=px2MM(70.76),h=px2MM(15),txt=small_cap_amount, align="R")

    large_col = "#7C5FF2"
    mid_col = "#A792FF"
    small_col = "#C6B9FF"

    # values = [80 , 80 , 200]
    values = [large_cap_percentage.replace("%", "") , mid_cap_percentage.replace("%","") , small_cap_percentage.replace("%","")]
    # Other, Dept , Equity
    colors = [large_col, mid_col, small_col]
    dotnut_pie = create_donut_chart(values, colors)
    pdf.image(dotnut_pie, x=px2MM(1630.42), y=px2MM(y + 32), w=px2MM(118.34), h=px2MM(118.34))
    #<__________________________________________________________________________________>

def bottom_containers(pdf, val, fund1, fund2,  y, x, iter):
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(120 + x), px2MM(y), px2MM(540), px2MM(148), 'F')
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_font('Fira_Sans-Regular', size=px2pts(19.521))
    pdf.set_xy(px2MM(149.28 + x), px2MM(y + 29.28))
    # pdf.multi_cell(px2MM(205.8), px2MM(29), "HDFC Mid-Cap Opportunities", align="L")
    pdf.multi_cell(px2MM(205.8), px2MM(29), fund1, align="L")
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_font('Fira_Sans-Regular', size=px2pts(19.521))
    pdf.set_xy(px2MM(425.38 + x), px2MM(y + 29.28))
    pdf.multi_cell(px2MM(205.8), px2MM(29), fund2, align="R")
    # # Horizontal Bars 
    bar = create_bar_chart_image(val= int(val), iter=iter)
    pdf.image(bar, px2MM(145.50 + x), px2MM(y + 94.38), px2MM(490.8), px2MM(24))
    pdf.set_text_color(*hex2RGB("#425466"))
    pdf.set_font('Fira_Sans-Bold', size=px2pts(21.961))
    pdf.set_xy(px2MM(369.74 + x), px2MM(y + 56.28))
    pdf.cell(px2MM(41), px2MM(32), val+'%', align="C",)
    save_path = f"temp_files/horizontal_bar_chart_{iter}.png"
    # Delete the file after saving it
    if os.path.exists(save_path):
        os.remove(save_path)
