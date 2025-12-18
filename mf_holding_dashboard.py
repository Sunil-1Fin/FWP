from utils import px2MM, px2pts, hex2RGB, create_bar_chart_image, create_donut_chart
import os
from os.path import join
from utils import format_amount, print_gradient_on_pdf_page,container6_v2, container_fourth_method, mutual_fund_type_method, bottom_containers, container1, container2, container3, container4
# # Add text inside the rectangle
# pdf.set_xy(x, y)
# pdf.set_font("Arial", size=12)
# pdf.set_text_color(0, 0, 0)  # Black text
# pdf.cell(width, height, "Excellent! You have no funds in the Regular plan", border=0, ln=1, align='C')

# # Output the PDF
# pdf.output("gradient_rectangle_no_gaps.pdf")


cwd = script_dir = os.path.abspath( os.path.dirname(__file__) )
warning_logo = join(cwd,'assets','images','mf_dashboard','Vector.svg')
stars_logo = join(cwd,'assets','images','mf_dashboard','star.png')







#//*-----MF Holdings Evaluation Dashboard-----*//#
def MFHoldingsEvaluationDashboard(pdf,json_data,c_MoneyS,money_signData,index_text):
    try:
        tab_val1 = json_data["mf_holding_evaluation"]['table']
        if tab_val1==[]:
            return None
    except:
        return None

    dashboard_data=json_data["mf_holding_evaluation"]["mf_holding_dashboard"]
    
    if not dashboard_data:
        return None
    
    Mutual_fund_portfolio_allocation = dashboard_data["mf_allocation"]

    # 1st Container Vars...
    NoOfMutualFundsValue = int(dashboard_data["no_of_funds"]["value"])

    # 2nd Container Vars...
    avg_portfolio_score = dashboard_data["mf_score"]
    avg_portfolio_score_value = avg_portfolio_score["value"]
    avg_portfolio_score_status = avg_portfolio_score["status"].upper()

  
    # 3rd Container Vars...
    equity_amount =  Mutual_fund_portfolio_allocation["equity_amount"] if Mutual_fund_portfolio_allocation else ""
    debt_amount = Mutual_fund_portfolio_allocation["debt_amount"] if Mutual_fund_portfolio_allocation else ""
    other_amount = Mutual_fund_portfolio_allocation["other_amount"] if Mutual_fund_portfolio_allocation else ""
    equity_percentage =  Mutual_fund_portfolio_allocation["equity_percentage"] if equity_amount else "0%"
    debt_percentage = Mutual_fund_portfolio_allocation["debt_percentage"] if debt_amount else "0%"
    other_percentage = Mutual_fund_portfolio_allocation["other_percentage"] if other_amount else "0%"
    

    # 4th Container Vars...
    EquityMarketCapDistribution= dashboard_data["mf_equity_allocation"]
    

    large_cap_amount = EquityMarketCapDistribution["large_cap_amount"]
    mid_cap_amount = EquityMarketCapDistribution["mid_cap_amount"]
    small_cap_amount = EquityMarketCapDistribution["small_cap_amount"]

    large_cap_percentage = EquityMarketCapDistribution["large_cap_percentage"] if large_cap_amount else "0%"
    mid_cap_percentage = EquityMarketCapDistribution["mid_cap_percentage"] if mid_cap_amount else "0%"
    small_cap_percentage = EquityMarketCapDistribution["small_cap_percentage"] if small_cap_amount else "0%"

    # 6th Container Vars...
    mutual_func_type = dashboard_data["mf_type"]

    direct_fund = mutual_func_type["direct"]
    direct_fund_percentage = direct_fund["percentage"] 
    direct_fund_value = direct_fund["value"]

    regular_fund = mutual_func_type["regular"]
    regular_fund_percentage = regular_fund["percentage"]
    regular_fund_value = regular_fund["value"]


    # 7th Container Vars...
    commissionLoss  = dashboard_data["mf_commission_projection"]
    commissionLossAnnual = commissionLoss["annual"]
    commissionLossProjection = commissionLoss["projections"]
    commissionLossProjectionFiveYears =  commissionLossProjection["five_years"]
    commissionLossProjectionTenYears = commissionLossProjection["ten_years"]
    commissionLossProjectionFifteenYears = commissionLossProjection["fifteen_years"]


    # Bottom Container Vars...
    portfololio_overlap_list = dashboard_data["mf_overlap"]


    conditional_text = "Attention! All your funds are in Regular Plan" if not direct_fund_value and regular_fund_value else "No Data Available" if (not regular_fund_value and not direct_fund_value) else "Regular funds found in your portfolio"


    # if not direct_fund_value and regular_fund_value:
    mutual_func_type = dashboard_data["mf_type"]

    direct_fund = mutual_func_type["direct"]
    direct_fund_value = direct_fund["value"]
    direct_fund_percentage = direct_fund["percentage"]

    regular_fund = mutual_func_type["regular"]
    regular_fund_value = regular_fund["value"]
    regular_fund_percentage = regular_fund["percentage"]


    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))

    # Black Strap Near Title
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0,px2MM(80), px2MM(15),px2MM(85),'F')

    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.cell(px2MM(8018),px2MM(84),"Mutual Fund Holdings Evaluation")

    # If Mutual Fund Portfolio Is Available Condition Starts Here!
    if Mutual_fund_portfolio_allocation:
        if mutual_func_type and (not regular_fund_value and direct_fund_value):
            y = 245
            container1(pdf, NoOfMutualFundsValue=NoOfMutualFundsValue, y=y)
            set_text_color = "#EF4444" if avg_portfolio_score_status == "LOW" else "#F5B40B" if avg_portfolio_score_status == "MEDIUM" else "#16A349"
            conditioal_fill_color = "#FEF2F2" if avg_portfolio_score_status == "LOW" else "#fcefcf" if avg_portfolio_score_status == "MEDIUM" else "#F0FDF5"
            container2(pdf, set_text_color=set_text_color, conditioal_fill_color=conditioal_fill_color, avg_portfolio_score_status=avg_portfolio_score_status, avg_portfolio_score_value=avg_portfolio_score_value, y=y )

            # Container 3
            if equity_percentage != '0%' or debt_percentage != '0%' or other_percentage != '0%':
                container3(pdf, equity_percentage=equity_percentage, equity_amount=equity_amount, debt_percentage=debt_percentage, other_percentage=other_percentage,  debt_amount=debt_amount, other_amount=other_amount, y=y)


            # (pdf, large_cap_percentage, large_cap_amount , mid_cap_percentage ,mid_cap_amount, small_cap_percentage, small_cap_amount, y):
            # container 4
            if equity_percentage != '0%':
                container4(pdf, large_cap_percentage=large_cap_percentage, large_cap_amount=large_cap_amount, mid_cap_percentage=mid_cap_percentage, mid_cap_amount=mid_cap_amount, small_cap_percentage=small_cap_percentage, small_cap_amount=small_cap_amount, y=y )

            # Print Gradiant
            # print_gradient_on_pdf_page(pdf=pdf, image=stars_logo, y_pos=471.35)

            if portfololio_overlap_list:
                # Initialize positions for bottom containers
                y = 615
                x = 0
                container_width = 569.76  # Constant width for each container
                max_per_row = 3  # Maximum containers per row

                # Draw bottom containers dynamically
                for index, item in enumerate(portfololio_overlap_list):
                    percentage = item.get("overlap")
                    fund1 = item.get("fund1")
                    fund2 = item.get("fund2")

                    # Move to the next row after max_per_row containers
                    if index > 0 and index % max_per_row == 0:
                        x = 0
                        y += 170

                    bottom_containers(pdf, val=percentage, fund1=fund1, fund2=fund2, x=x, y=y, iter=index)
                    x += container_width  # Increment x for the next container
                # Add "Portfolio Overlap (Top 5)" title
                pdf.set_text_color(*hex2RGB("#1A1A1D"))
                pdf.set_font('Inter-Regular', size=px2pts(21))
                pdf.set_xy(px2MM(120), px2MM(553))
                pdf.cell(px2MM(172), px2MM(29), "Portfolio Overlap (Top 5)", align="L")
        else:
            y = 188
            # <__________________________________________________________________________________>
            container1(pdf, NoOfMutualFundsValue=NoOfMutualFundsValue, y=y)
            set_text_color = "#EF4444" if avg_portfolio_score_status == "LOW" else "#F5B40B" if avg_portfolio_score_status == "MEDIUM" else "#16A349"
            conditioal_fill_color = "#FEF2F2" if avg_portfolio_score_status == "LOW" else "#fcefcf" if avg_portfolio_score_status == "MEDIUM" else "#F0FDF5"

            container2(pdf, set_text_color=set_text_color, conditioal_fill_color=conditioal_fill_color, avg_portfolio_score_status=avg_portfolio_score_status, avg_portfolio_score_value=avg_portfolio_score_value, y=y )
            
            if equity_percentage != '0%' or debt_percentage != '0%' or other_percentage != '0%':
                container3(pdf, equity_percentage=equity_percentage, equity_amount=equity_amount, debt_percentage=debt_percentage,debt_amount=debt_amount , other_amount=other_amount, other_percentage=other_percentage, y=y)
            
            if equity_percentage != '0%':
                container4(pdf=pdf,large_cap_percentage=large_cap_percentage, large_cap_amount=large_cap_amount, mid_cap_percentage=mid_cap_percentage,mid_cap_amount=mid_cap_amount, small_cap_percentage=small_cap_percentage,small_cap_amount=small_cap_amount, y=y)
        
            # <__________________________________________________________________________________>
            # 5th Container
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.rect(px2MM(120),px2MM(417.65), px2MM(539.25),px2MM(197.65),'F')
            pdf.set_xy(px2MM(149), px2MM(442))
            pdf.set_text_color(*hex2RGB("#425466"))
            pdf.set_font('Inter-Regular', size=px2pts(14.641))
            pdf.cell(px2MM(145),px2MM(29), "Mutual Fund Type",align = "L")
            pdf.set_font('Inter-Regular', size=px2pts(14.27))
            pdf.set_text_color(*hex2RGB("#425466"))
            pdf.set_xy(px2MM(167), px2MM(494.51))
            pdf.cell(px2MM(52.461),px2MM(15), "Direct",align = "L")
            pdf.set_xy(px2MM(167), px2MM(529.03))
            pdf.cell(px2MM(52.461),px2MM(15), "Regular",align = "L")
            pdf.set_fill_color(*hex2RGB('#7FCDA4'))
            pdf.rect(px2MM(149),px2MM(498), px2MM(8),px2MM(8),'F')
            pdf.set_fill_color(*hex2RGB('#FF8B81'))
            pdf.rect(px2MM(149),px2MM(531.47), px2MM(8),px2MM(8),'F')

            # Input Should Be Dynamic From The Json File Provided By Backend.
            direct_fund_clean_percentage = direct_fund_percentage.replace("%","")
            regular_fund_clean_percentage = regular_fund_percentage.replace("%","")

            values = [direct_fund_clean_percentage if direct_fund_clean_percentage else '0', regular_fund_clean_percentage]
            # Direct, Regular
            colors = ['#7FCDA4', '#FF8B81']
            conditional_colors = ['#FF8B81', '#FF8B81']

            buf = create_donut_chart(values=values, colors=conditional_colors if not direct_fund_value and regular_fund_value else colors)
            pdf.image(buf, px2MM(503), px2MM(456.69), w=px2MM(118), h=px2MM(118))
            pdf.set_font('Inter-Regular', size=px2pts(14.27))
            pdf.set_text_color(*hex2RGB("#425466"))
            pdf.set_xy(px2MM(258.7), px2MM(494.51))
            pdf.cell(px2MM(40),px2MM(15), direct_fund_percentage if direct_fund_percentage else "0%",align = "L")
            pdf.set_xy(px2MM(258.9), px2MM(529.03))
            pdf.cell(px2MM(40),px2MM(15), regular_fund_percentage if regular_fund_percentage else "0%",align = "L")
            pdf.set_text_color(*hex2RGB("#718096"))
            pdf.set_xy(px2MM(338), px2MM(494.51))
            pdf.cell(px2MM(58.56),px2MM(15), format_amount(direct_fund_value),align = "L")
            pdf.set_xy(px2MM(338), px2MM(529.03))
            pdf.cell(px2MM(56.56),px2MM(15),  format_amount(regular_fund_value),align = "L")
            pdf.image(warning_logo,x=px2MM(150.5), y=px2MM(569.59), w=px2MM(18.3),h=px2MM(15.8) )
            pdf.set_font('Inter-Regular', size=px2pts(17.081))
            pdf.set_text_color(*hex2RGB("#DC2626"))
            pdf.set_xy(px2MM(178.5), px2MM(566.47))
            pdf.cell(px2MM(295.25),px2MM(22),conditional_text, align="L")
            # <_________________________________________________________________________________>

            # <__________________________________________________________________________________>
            # 6th Box
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.rect(px2MM(688.54),px2MM(417.65), px2MM(1110.23),px2MM(197.65),'F')
            pdf.set_font('Inter-Regular', size=px2pts(14.641))
            pdf.set_text_color(*hex2RGB("#898B90"))
            pdf.set_xy(px2MM(734), px2MM(442))
            pdf.multi_cell(px2MM(213),px2MM(28.061), "Your Losses in \nCommission (Annual)",align = "L")
            pdf.set_xy(px2MM(1020), px2MM(442 + 40))
            pdf.multi_cell(px2MM(213),px2MM(28.061),"Commission\nLoss Projection",align = "L")
            pdf.set_font('Inter-Bold', size=px2pts(39.041))
            pdf.set_text_color(*hex2RGB("#F87171"))
            pdf.set_xy(px2MM(734.9), px2MM(534.77))
            pdf.cell(px2MM(120),px2MM(47),format_amount(commissionLossAnnual), align="L")
            pdf.set_font('Inter-Bold', size=px2pts(24.401))
            pdf.set_xy(px2MM(1197.3), px2MM(548.19))
            pdf.cell(px2MM(89),px2MM(31),format_amount(commissionLossProjectionFiveYears), align="L")
            pdf.set_xy(px2MM(1401.46), px2MM(548.19))
            pdf.cell(px2MM(112),px2MM(31),format_amount(commissionLossProjectionTenYears), align="L")
            pdf.set_xy(px2MM(1598.69), px2MM(548.19))
            pdf.cell(px2MM(148),px2MM(31),format_amount(commissionLossProjectionFifteenYears), align="L")
            pdf.set_font('Inter-Regular', size=px2pts(17.081))
            pdf.set_text_color(*hex2RGB("#A3A3A3"))
            dynamic_x_padding_for_annual_income = 861.78 if len(commissionLossAnnual) <=4 else 883
            pdf.set_xy(px2MM(dynamic_x_padding_for_annual_income), px2MM(554.29))
            pdf.cell(px2MM(64),px2MM(23),"Approx", align="L")
            # Big Horizontal Line.
            pdf.set_fill_color(*hex2RGB('#DFE5EB'))
            pdf.rect(px2MM(1242.43),px2MM(516.79), px2MM(428),px2MM(2),'F')
            # Small Vertical Line.
            pdf.rect(px2MM(1242.43),px2MM(506), px2MM(2),px2MM(20),'F')
            # Small Vertical Line
            pdf.rect(px2MM(1457.16),px2MM(506), px2MM(2),px2MM(20),'F')
            # Small Vertical Line.
            pdf.rect(px2MM(1670.86),px2MM(506), px2MM(2),px2MM(20),'F')
            pdf.set_font('Inter-Regular', size=px2pts(17.081))
            pdf.set_text_color(*hex2RGB("#898B90"))
            pdf.set_xy(px2MM(1211.94), px2MM(456.69))
            pdf.cell(px2MM(60),px2MM(29), "5 years",align = "C")
            pdf.set_xy(px2MM(1423), px2MM(456.69))
            pdf.cell(px2MM(68),px2MM(29), "10 years",align = "C")
            pdf.set_xy(px2MM(1638.95), px2MM(456.69))
            pdf.cell(px2MM(68),px2MM(29), "15 years",align = "C")
            # Big Vertical Seperation Line.
            pdf.set_fill_color(*hex2RGB('#DFE5EB'))
            pdf.rect(px2MM(971.49),px2MM(462.79), px2MM(2),px2MM(108),'F')            
            # <__________________________________________________________________________________>


            # <__________________________________________________________________________________
            if portfololio_overlap_list:
                y = 696.21
                x = 0        
                # Drawing bottom containers dynamically.
                for index, item in enumerate(portfololio_overlap_list):
                    percentage = item.get("overlap")
                    fund1 = item.get("fund1")
                    fund2 = item.get("fund2")
                    if index ==3:
                        x=0
                        y+=170
                    bottom_containers(pdf, val=percentage, fund1=fund1,fund2=fund2, x=x, y=y, iter=index)
                    x+=569.76

                pdf.set_font('Inter-Regular', size=px2pts(21))
                pdf.set_text_color(*hex2RGB("#1A1A1D"))
                pdf.set_xy(px2MM(120), px2MM(647.29))
                pdf.cell(px2MM(172),px2MM(29), "Portfolio Overlap (Top 5)",align = "L")
            # <__________________________________________________________________________________>

    # If Mutual Fund Portfolio Is Not Available Condition Starts Here!
    if not Mutual_fund_portfolio_allocation:    
        if mutual_func_type and (not regular_fund_value and direct_fund_value):
            y = 245
            container1(pdf=pdf, NoOfMutualFundsValue=NoOfMutualFundsValue, y=y)

            # Determine text and fill colors based on portfolio score status.
            color_mapping = {
            "LOW": {"text_color": "#EF4444", "fill_color": "#FEF2F2"},
            "MEDIUM": {"text_color": "#F5B40B", "fill_color": "#FFF9EB"},
            "HIGH": {"text_color": "#16A349", "fill_color": "#F0FDF5"}
            }
            status_colors = color_mapping.get(avg_portfolio_score_status, {})
            set_text_color = status_colors.get("text_color", "#000000")  # Default to black if status unknown
            conditioal_fill_color = status_colors.get("fill_color", "#FFFFFF")  # Default to white if status unknown

            # container2 with dynamic colors
            container2(
            pdf,
            conditioal_fill_color=conditioal_fill_color,
            set_text_color=set_text_color,
            avg_portfolio_score_status=avg_portfolio_score_status,
            avg_portfolio_score_value=avg_portfolio_score_value,
            y=y
            )
             # Add gradient image
            # print_gradient_on_pdf_page(pdf, y_pos=471.35, image=stars_logo)

           
            if portfololio_overlap_list:
                # Initialize positions for bottom containers
                y = 615
                x = 0
                container_width = 569.76  # Constant width for each container
                max_per_row = 3  # Maximum containers per row

                # Draw bottom containers dynamically
                for index, item in enumerate(portfololio_overlap_list):
                    percentage = item.get("overlap")
                    fund1 = item.get("fund1")
                    fund2 = item.get("fund2")

                    # Move to the next row after max_per_row containers
                    if index > 0 and index % max_per_row == 0:
                        x = 0
                        y += 170

                    bottom_containers(pdf, val=percentage, fund1=fund1, fund2=fund2, x=x, y=y, iter=index)
                    x += container_width  # Increment x for the next container
                # Portfolio Overlap title
                pdf.set_text_color(*hex2RGB("#1A1A1D"))
                pdf.set_font('Inter-Regular', size=px2pts(21))
                pdf.set_xy(px2MM(120), px2MM(553))
                pdf.cell(px2MM(172), px2MM(29), "Portfolio Overlap (Top 5)", align="L")
       
        else:
            y = 298
            container1(pdf=pdf, NoOfMutualFundsValue=NoOfMutualFundsValue, y=y)
            # Determine text and fill colors based on portfolio score status
            color_mapping = {
            "LOW": {"text_color": "#EF4444", "fill_color": "#FEF2F2"},
            "MEDIUM": {"text_color": "#F5B40B", "fill_color": "#FFF9EB"},
            "HIGH": {"text_color": "#16A349", "fill_color": "#F0FDF5"}
            }

            status_colors = color_mapping.get(avg_portfolio_score_status, {})
            set_text_color = status_colors.get("text_color", "#000000")  # Default to black if status unknown
            conditioal_fill_color = status_colors.get("fill_color", "#FFFFFF")  # Default to white if status unknown

            # Render container with dynamic colors
            container2(
            pdf,
            conditioal_fill_color=conditioal_fill_color,
            set_text_color=set_text_color,
            avg_portfolio_score_status=avg_portfolio_score_status,
            avg_portfolio_score_value=avg_portfolio_score_value,
            y=y
            )
            mutual_fund_type_method(pdf, warning_logo, direct_fund_percentage, regular_fund_percentage, direct_fund_value, regular_fund_value, conditional_text, y=y)

            # 6th Containers Compact Version...
            container6_v2(pdf,amount=commissionLossAnnual,y=y)


            # <_________________________________________________________________
            if portfololio_overlap_list:
                # Initialize positions for bottom containers
                y = 615
                x = 0
                container_width = 569.76  # Constant width for each container
                max_per_row = 3  # Maximum containers per row


                # Drawing bottom containers dynamically
                for index, item in enumerate(portfololio_overlap_list):
                    percentage = item.get("overlap")
                    fund1 = item.get("fund1")
                    fund2 = item.get("fund2")
                    # Move to the next row after max_per_row containers
                    if index > 0 and index % max_per_row == 0:
                        x = 0
                        y += 170
                    bottom_containers(pdf, val=percentage, fund1=fund1, fund2=fund2, x=x, y=y, iter=index)
                    x += container_width  # Increment x for the next container

                # Portfolio Overlap title
                pdf.set_text_color(*hex2RGB("#1A1A1D"))
                pdf.set_font('Inter-Regular', size=px2pts(21))
                pdf.set_xy(px2MM(120), px2MM(553))
                pdf.cell(px2MM(172), px2MM(29), "Portfolio Overlap (Top 5)", align="L")

            # <__________________________________________________________________________________>
            
    
    pdf.set_xy(px2MM(745), px2MM(1039))
    pdf.set_font('Roboto-Regular', size=px2pts(18))
    pdf.set_text_color(*hex2RGB("#000000"))
    pdf.cell(px2MM(420),px2MM(21), "Disclaimer: Numbers may not add up due to rounding.",align = "C")

    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')














# Green Gradient Rectangle. #F0FDF5 #00BC44
# pdf.draw_gradient(px2MM(120), px2MM(431.35), px2MM(1680), px2MM(50), hex2RGB("#00BC44"), hex2RGB("#F0FDF5"))
# pdf.image(stars_logo,px2MM(135), px2MM(442.14),px2MM(30.00), px2MM(27.5))
# pdf.set_font('Inter-SemiBold', size=px2pts(14))
# pdf.set_text_color(*hex2RGB("#FFFFFF"))
# pdf.set_xy(px2MM(182), px2MM(447.42))
# pdf.cell(px2MM(328),px2MM(23), "Excellent! You have no funds in the Regular plan",align = "L")
