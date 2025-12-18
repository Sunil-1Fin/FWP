from fpdf import FPDF
from os.path import join
from PIL import ImageColor
import sys
import os, glob
import json
import datetime as dt
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.ticker as tick
from matplotlib import font_manager as fm
import matplotlib.font_manager as font_manager
import math
import matplotlib.pyplot as plt
from matplotlib.pyplot import gca
import PyPDF2
import math 
import traceback
from PyPDF2 import PdfWriter
import locale 
import io
from utils import create_donut_chart, create_bar_chart_image, read_json_file, draw_gradient
from mf_holding_dashboard import MFHoldingsEvaluationDashboard


FPDF.draw_gradient = draw_gradient


class InvalidUserID(Exception):
    
    def __init__(self, userID, message="Mobile_Number"):
        self.userID = userID
        self.message = message
        super().__init__(self.message)
# API Setup

def api_call(excel_file,save_path):
    f_name,f_ext = os.path.splitext(excel_file)
    if f_ext == '.json':
        with open(sys.argv[1],encoding='utf-8') as f:
            json_data = json.load(f)
    else:
        print('Wrong File')
        return traceback.format_exc()
    # df = pd.DataFrame.from_dict(json_data['meta'])
    final_pdf_name = json_data['meta']['mobile_number']
    try:
        x = money_sign_pdf(json_data,final_pdf_name,save_path)
        if x:
            print('PDF Generated')
        else:
            print('PDF Generation Failed')
        return True
    except Exception as e:
        raise RuntimeError("Error Generating PDF:\n" + traceback.format_exc())
 
#//*---PDF INDEX NUMBER SETUP-----*//
your_top_most_priority = 0
your_fin_prof_idx = 0 
# your_1_view_idx = 0 
your_fin_analysis_idx = 0 
your_fin_analysis_sub_comment = ['Financial Metrics','Net Worth','Liability Analysis']
your_fw_plan_idx = 0 
fin_feat_product_list = 0
best_practices_idx = 0 

#//*-----Index Text of Page--**////
def index_text(pdf,col):
    #//*---Page Index Number----*//
    pdf.set_xy(px2MM(1870), px2MM(1018))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_text_color(*hex2RGB(col))
    pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')


def truncate_float(number, places):
    return round(int(number * (10 ** places)) / 10 ** places,1)
    

#//*----------setting of Pdf Pages---*//
#//*--Setting 0 to 0.0K
def format_cash(amount):
    negative_flag = False
    if amount < 0:
        amount = abs(amount)
        negative_flag = True
    
    if amount < 1e3:
        x = str(truncate_float((amount / 1e3), 2))
        if negative_flag==False:
            return x + "K"
        else:
            return '-'+x + "K"

    if 1e3 <= amount < 1e5:
        x = str(truncate_float((amount / 1e5) * 100, 2))
        if negative_flag==False:
            return x + "K"
        else:
            return '-'+x + "K"

    if 1e5 <= amount < 1e7:
        x = str(truncate_float((amount / 1e7) * 100, 2))
        if negative_flag==False:
            return x + "L"
        else:
            return '-'+x + "L"

    if amount >= 1e7:
        x = str(truncate_float(amount / 1e7, 2))
        if negative_flag==False:
            return x + "Cr"
        else:
            return '-'+x + "Cr"
        
#//*--Setting 0 to 0.0L    
def format_cash2(amount):
    negative_flag = False
    if amount < 0:
        amount = abs(amount)
        negative_flag = True
        
    if amount <= 1e1:
        x = str(truncate_float((amount / 1e5), 2))
        if negative_flag==False:
            return x + "L"
        else:
            return '-'+x + "L"

    if 1e1 < amount <= 1e3:
        x = str(truncate_float((amount / 1e3), 2))
        if negative_flag==False:
            return x + "K"
        else:
            return '-'+x + "K"
        # return amount

    if 1e3 <= amount < 1e5:
        x = str(truncate_float((amount / 1e5) * 100, 2))
        if negative_flag==False:
            return x + "K"
        else:
            return '-'+x + "K"

    if 1e5 <= amount < 1e7:
        x = str(truncate_float((amount / 1e7) * 100, 2))
        if negative_flag==False:
            return x + "L"
        else:
            return '-'+x + "L"

    if amount >= 1e7:
        x = str(truncate_float(amount / 1e7, 2))
        if negative_flag==False:
            return x + "Cr"
        else:
            return '-'+x + "Cr"
  
#//*---If val=300 print 300 (insted of 0.3K)    
def format_cash3(amount):
    negative_flag = False
    if amount < 0:
        amount = abs(amount)
        negative_flag = True


    if amount < 1e3:
        x = str(truncate_float((amount), 2))
        if negative_flag==False:
            return str(int(float(x)))
        else:
            return '-'+str(int(float(x)))
        # return amount

    if 1e3 <= amount < 1e5:
        x = str(truncate_float((amount / 1e5) * 100, 2))
        if negative_flag==False:
            return x + "K"
        else:
            return '-'+x + "K"

    if 1e5 <= amount < 1e7:
        x = str(truncate_float((amount / 1e7) * 100, 2))
        if negative_flag==False:
            return x + "L"
        else:
            return '-'+x + "L"

    if amount >= 1e7:
        x = str(truncate_float(amount / 1e7, 2))
        if negative_flag==False:
            return x + "Cr"
        else:
            return '-'+x + "Cr"
    
# Unit conversionss
def px2MM(val):
  # Sauce: https://www.figma.com/community/plugin/841435609952260079/Unit-Converter
#   return val * (25.4 / 72)
  return val * 0.264583333338

def mm2PX(val):
  # Sauce: https://www.figma.com/community/plugin/841435609952260079/Unit-Converter
  return val * 3.7795275591

def hex2RGB(val):
  return list(ImageColor.getcolor(val, "RGB"))

def px2pts(val):
    return val*0.75

#//*----Get multicell Height----

def multicell_height(pdf,string,width):
    lines = mm2PX(pdf.get_string_width(string))/width
    no_line = math.ceil(lines)
    if no_line == 0:
        return 1
    return no_line

#//*---remove empty strings
def remove_empty_strings(string):
    return string != ""
  
# remove pkl files
for f in glob.glob("*.pkl"):
  os.remove(f)
  
# reportpath=os.getcwd()+'/public/money-sign-reports/'
cwd = script_dir = os.path.abspath( os.path.dirname(__file__) )
logo = join(cwd,'assets','images','logo','1FBlack.png')
logo2 = join(cwd,'assets','images','logo','1FBlackPB.png')
warning_logo = join(cwd,'assets','images','mf_dashboard','Vector.svg')

def money_sign_pdf(json_data,final_pdf_name,save_path):
    pdf  = FPDF('L','mm',(px2MM(1080), px2MM(1920)))
    
    #//*-----File Cleaning----*//
    if os.path.exists("asset_chart.png"):
          os.remove("asset_chart.png")
      
    if os.path.exists("acutal_networth_chart.png"):
          os.remove("acutal_networth_chart.png")
          
    if os.path.exists("liabilities_chart.png"):
          os.remove("liabilities_chart.png")
          
    if os.path.exists("utilisation_of_deduction.png"):
          os.remove("utilisation_of_deduction.png")
    
    LGpkl_file = os.path.join(cwd,'assets','fonts','League_Spartan','static')
    test = os.listdir(LGpkl_file)
    for item in test:
        if item.endswith(".pkl"):
            os.remove(os.path.join(LGpkl_file, item))
    
    test = os.listdir(cwd)
    for item in test:
        if item.endswith(".pkl"):
            os.remove(item)
                        
    Pratapkl_file = os.path.join(cwd,'assets','fonts','Prata')
    test = os.listdir(Pratapkl_file)
    for item in test:
        if item.endswith(".pkl"):
            os.remove(os.path.join(Pratapkl_file, item))
            
    Inter_font = os.path.join(cwd,'assets','fonts','Inter','static')
    test = os.listdir(Inter_font)
    for item in test:
        if item.endswith(".pkl"):
            os.remove(os.path.join(Inter_font, item))
    
                
    pdf.set_auto_page_break(False)            
    pdf.add_font('LeagueSpartan-SemiBold', '', os.path.join(cwd, 'assets', 'fonts', 'League_Spartan','static', 'LeagueSpartan-SemiBold.ttf'))
    pdf.add_font('LeagueSpartan-Bold', '', os.path.join(cwd, 'assets', 'fonts', 'League_Spartan','static', 'LeagueSpartan-Bold.ttf'))
    pdf.add_font('LeagueSpartan-Regular', '', os.path.join(cwd, 'assets', 'fonts', 'League_Spartan','static', 'LeagueSpartan-Regular.ttf'))
    pdf.add_font('LeagueSpartan-Medium', '', os.path.join(cwd, 'assets', 'fonts', 'League_Spartan', 'static', 'LeagueSpartan-Medium.ttf'))
    pdf.add_font('LeagueSpartan-Light', '', os.path.join(cwd, 'assets', 'fonts', 'League_Spartan', 'static', 'LeagueSpartan-Light.ttf'))
    pdf.add_font('Prata', '', os.path.join(cwd, 'assets', 'fonts', 'Prata','Prata-Regular.ttf'))

    
    
    pdf.add_font('Inter-Light', '', os.path.join(cwd, 'assets', 'fonts', 'Inter','static','Inter-Light.ttf'))
    pdf.add_font('Inter-Medium', '', os.path.join(cwd, 'assets', 'fonts', 'Inter','static','Inter-Medium.ttf'))
    pdf.add_font('Inter-Regular', '', os.path.join(cwd, 'assets', 'fonts', 'Inter','static','Inter-Regular.ttf'))
    pdf.add_font('Inter-Bold', '', os.path.join(cwd, 'assets', 'fonts', 'Inter','static','Inter-Bold.ttf'))
    pdf.add_font('Inter-SemiBold', '', os.path.join(cwd, 'assets', 'fonts', 'Inter','static','Inter-SemiBold.ttf'))

    pdf.add_font('Fira_Sans-Light', '', os.path.join(cwd, 'assets', 'fonts', 'Fira_Sans','FiraSans-Light.ttf'))
    pdf.add_font('Fira_Sans-Regular', '', os.path.join(cwd, 'assets', 'fonts', 'Fira_Sans','FiraSans-Regular.ttf'))
    pdf.add_font('Fira_Sans-Bold', '', os.path.join(cwd, 'assets', 'fonts', 'Fira_Sans','FiraSans-Bold.ttf'))
    pdf.add_font('Fira_Sans-SemiBold', '', os.path.join(cwd, 'assets', 'fonts', 'Fira_Sans','FiraSans-SemiBold.ttf'))


    

    #
    pdf.add_font('Roboto-Regular', '', os.path.join(cwd, 'assets', 'fonts', 'Roboto','static', 'Roboto-Regular.ttf'))
    pdf.add_font('Roboto-Medium', '', os.path.join(cwd, 'assets', 'fonts', 'Roboto', 'static', 'Roboto-Medium.ttf'))
    pdf.add_font('Roboto-Light', '', os.path.join(cwd, 'assets', 'fonts', 'Roboto', 'static', 'Roboto-Light.ttf'))


    # c_MoneyS = user_data['moneySign'].split(' ')
    try:
        money_sign = json_data['money_sign']['money_sign']
        c_MoneyS = money_sign.split(' ')
        c_MoneyS = c_MoneyS[-1].strip()
    except Exception as e:
        raise RuntimeError("Error Generating PDF:\n" + traceback.format_exc())


    
    money_signData={
        'Eagle':{
            'Front_P':{
                'Ms_image':'Eagle.png',
                'Vt_line':'#7C5FF2',
                'Date_c':'#C6B9FF'
            },
            'content':['#F3F6F9','#E6E0FF','#C6B9FF','#A792FF','#7C5FF2','#5641AA'],
            'Money_Sign':['#E6E0FF','#7C5FF2','Far-Sighted Eagle'],
            #//*-behav_bias = image,color,x-axis,y-axis,width,height
            'behav_bias':['Eagle_bb.svg','#7C5FF2',837,567,1083,519,'#A792FF'],
            'gen_profile':['#5641AA','#A792FF','#7C5FF2'],
            'fin_profile':['#E6E0FF']
        },
        'Horse':{
            'Front_P':{
                'Ms_image':'Horse.png',
                'Vt_line':'#4DC3A7',
                'Date_c':'#ACE4D7'
            },
            'content':['#F3F6F9','#DEF7F1','#ACE4D7','#82DBC6','#4DC3A7','#229479'],
            'Money_Sign':['#DEF7F1','#4DC3A7','Persistent Horse'],
            'behav_bias':['Horse_bb.svg','#82DBC6',1162,322,688,688,'#82DBC6'],
            'gen_profile':['#229479','#82DBC6','#4DC3A7'],
            'fin_profile':['#DEF7F1']
        },
        'Tiger':{
            'Front_P':{
                'Ms_image':'Tiger.png',
                'Vt_line':'#FFCA41',
                'Date_c':'#FFE6A8'
            },
            'content':['#F3F6F9','#FFF3DB','#FFE6A8','#FFD976','#FFCA41','#D2A530'],
            'Money_Sign':['#FFF3DB','#FFCA41','Tactical Tiger'],
            'behav_bias':['Tiger_bb.svg','#FFCA41',1170,330,680,680,'#FFD976'],
            'gen_profile':['#D2A530','#FFD976','#FFCA41'],
            'fin_profile':['#FFF3DB']
        },
        'Lion':{
            'Front_P':{
                'Ms_image':'Lion.png',
                'Vt_line':'#FFCA41',
                'Date_c':'#FFE6A8'
            },
            'content':['#F3F6F9','#FFF3DB','#FFE6A8','#FFD976','#FFCA41','#D2A530'],
            'Money_Sign':['#FFF3DB','#FFCA41','Opportunistic Lion'],
            'behav_bias':['Lion_bb.svg','#FFCA41',1177,337,673,673,'#FFD976'],
            'gen_profile':['#D2A530','#FFD976','#FFCA41'],
            'fin_profile':['#FFF3DB']
        },
        'Elephant':{
            'Front_P':{
                'Ms_image':'Elephant.png',
                'Vt_line':'#4DC3A7',
                'Date_c':'#ACE4D7'
            },
            'content':['#F3F6F9','#DEF7F1','#ACE4D7','#82DBC6','#4DC3A7','#229479'],
            'Money_Sign':['#DEF7F1','#4DC3A7','Virtuous Elephant'],
            'behav_bias':['Elephant_bb.svg','#4DC3A7',1177,377,673,673,'#82DBC6'],
            'gen_profile':['#229479','#82DBC6','#4DC3A7'],
            'fin_profile':['#DEF7F1']
        },
        'Turtle':{
            'Front_P':{
                'Ms_image':'Turtle.png',
                'Vt_line':'#649DE5',
                'Date_c':'#ADD0FB'
            },
            'content':['#F3F6F9','#DEEDFF','#ADD0FB','#90BEF8','#649DE5','#3D7DD0'],
            'Money_Sign':['#DEEDFF','#649DE5','Vigilant Turtle'],
            'behav_bias':['Turtle_bb.svg','#649DE5',1150,310,700,700,'#90BEF8'],
            'gen_profile':['#3D7DD0','#90BEF8','#649DE5'],
            'fin_profile':['#DEEDFF']
        },
        'Whale':{
            'Front_P':{
                'Ms_image':'Whale.png',
                'Vt_line':'#649DE5',
                'Date_c':'#ADD0FB'
            },
            'content':['#F3F6F9','#DEEDFF','#ADD0FB','#90BEF8','#649DE5','#3D7DD0'],
            'Money_Sign':['#DEEDFF','#649DE5','Enlightened Whale'],
            'behav_bias':['Whale_bb.svg','#649DE5',1177,337,673,673,'#90BEF8'],
            'gen_profile':['#3D7DD0','#90BEF8','#649DE5'],
            'fin_profile':['#DEEDFF']
        },
        'Shark':{
            'Front_P':{
                'Ms_image':'Shark.png',
                'Vt_line':'#7C5FF2',
                'Date_c':'#C6B9FF'
            },
            'content':['#F3F6F9','#E6E0FF','#C6B9FF','#A792FF','#7C5FF2','#5641AA'],
            'Money_Sign':['#E6E0FF','#7C5FF2','Stealthy Shark'],
            'behav_bias':['Shark_bb.svg','#7C5FF2',1170,330,680,680,'#A792FF'],
            'gen_profile':['#5641AA','#A792FF','#7C5FF2'],
            'fin_profile':['#E6E0FF']
        }
       
    }
    
    
    #//*----Pasing pdf_setting,Json Data, MoneySign Name,Money sign wise all Images,Backgrounds to function
    #//*-----Pages Sequence is based on the sequence of function Calling ---*//
    
    x = Banner(pdf,json_data,c_MoneyS,money_signData)
    if x==False:
        return None
    content(pdf,json_data,c_MoneyS,money_signData)
    # top_most_priority(pdf,json_data,c_MoneyS,money_signData)
    cashflow_plan(pdf,json_data,c_MoneyS,money_signData)
    action_plan_summary(pdf,json_data,c_MoneyS,money_signData)
    next_quarter_preview(pdf,json_data)
    fin_profile(pdf, json_data,c_MoneyS,money_signData)
    # fbs(pdf,json_data,c_MoneyS,money_signData)
    your_1_view_detail(pdf,json_data,c_MoneyS,money_signData)
    assets_chart(pdf,json_data,c_MoneyS,money_signData)
    liabilities_chart(pdf,json_data,c_MoneyS,money_signData)
    emergency_planning(pdf,json_data,c_MoneyS,money_signData)
    exp_lib_mang(pdf,json_data,c_MoneyS,money_signData)
    asset_allocation(pdf,json_data,c_MoneyS,money_signData)
    net_worth(pdf,json_data,c_MoneyS,money_signData)
    # net_worth_projection(pdf,json_data,c_MoneyS,money_signData)
    # assumptions(pdf,json_data,c_MoneyS,money_signData)
    bureao_report(pdf,json_data,c_MoneyS,money_signData)
    libility_management_1(pdf,json_data,c_MoneyS,money_signData)
    surrender_impact(pdf,json_data,c_MoneyS,money_signData)
    insurance_policy_eveluation(pdf,json_data,c_MoneyS,money_signData)
    life_insurance_evaluation_summary(pdf,json_data,c_MoneyS,money_signData)
    MFHoldingsEvaluationDashboard(pdf, json_data, c_MoneyS, money_signData,index_text=index_text)
    mf_holding_eveluation(pdf,json_data,c_MoneyS,money_signData)
    tax_liability_potential_planning(pdf,json_data,c_MoneyS,money_signData)
    credit_card_evaluation(pdf,json_data,c_MoneyS,money_signData)
    # term_insurance(pdf,json_data,c_MoneyS,money_signData)
    # health_insurance(pdf,json_data,c_MoneyS,money_signData)
    # equity_mutual_fund(pdf,json_data,c_MoneyS,money_signData)
    # debt_mutual_fund(pdf,json_data,c_MoneyS,money_signData)
    # hybrid_mutual_fund(pdf,json_data,c_MoneyS,money_signData)
    # credit_cards(pdf,json_data,c_MoneyS,money_signData)
    # housing_lenders(pdf,json_data,c_MoneyS,money_signData)
    # building_strong_credit_profile(pdf,json_data,c_MoneyS,money_signData)
    # planning_your_taxes(pdf,json_data,c_MoneyS,money_signData)
    # aval_tax_deduct_1(pdf,json_data,c_MoneyS,money_signData)
    # aval_tax_deduct_2(pdf,json_data,c_MoneyS,money_signData)
    # aval_tax_deduct_3(pdf,json_data,c_MoneyS,money_signData)
    # aval_tax_deduct_4(pdf,json_data,c_MoneyS,money_signData)
    # aval_tax_deduct_5(pdf,json_data,c_MoneyS,money_signData)
    # capital_gains_1(pdf,json_data,c_MoneyS,money_signData)
    # capital_gains_2(pdf,json_data,c_MoneyS,money_signData)
    # capital_gains_3(pdf,json_data,c_MoneyS,money_signData)
    # capital_gains_4(pdf,json_data,c_MoneyS,money_signData)
    # planning_for_inheritance(pdf,json_data,c_MoneyS,money_signData)
    # understanding_inheritance(pdf,json_data,c_MoneyS,money_signData)
    # planning_your_esate_will(pdf,json_data,c_MoneyS,money_signData)
    disclaimer(pdf,json_data,c_MoneyS,money_signData)
    lastpage(pdf,json_data,c_MoneyS,money_signData)
    
    #//*---Calling again Content Page function at last because first need to get all Index number of pages then replace it to second Page(Content Page with no Indexing)
    content(pdf,json_data,c_MoneyS,money_signData)
    

    try:
        #//*---IF Saving path directory does not exist
        pdf.output('temp.pdf')
        
        # input_file = 'temp.pdf'
        pdf_output = PdfWriter()
        
        file = open('temp.pdf', 'rb')
        readpdf = PyPDF2.PdfReader(file)
        totalpages = len(readpdf.pages)
        
        pages_list = [0,-1]
        other_page = list(x for x in range(2,totalpages-1))
        pages_list = pages_list+other_page

        
        for i in pages_list:
            current_page = readpdf.pages[i]
            pdf_output.add_page(current_page)
        dir_name = save_path
        if not os.path.exists(dir_name):
            os.mkdir(dir_name)
        
        output_file = str(final_pdf_name)+'.pdf'
        opfile = join(save_path,output_file)
        pdf_output.write(opfile) 
        file.close()
        
            #//*-----File Cleaning----*//
        if os.path.exists("asset_chart.png"):
            os.remove("asset_chart.png")
        
        if os.path.exists("acutal_networth_chart.png"):
            os.remove("acutal_networth_chart.png")
            
        if os.path.exists("liabilities_chart.png"):
            os.remove("liabilities_chart.png")
        
        if os.path.exists("utilisation_of_deduction.png"):
          os.remove("utilisation_of_deduction.png")
            
        if os.path.exists('temp.pdf'):
            os.remove('temp.pdf')
        return True
    except Exception as e:
        raise RuntimeError("Error Generating PDF:\n" + traceback.format_exc())
    
#//*--------Function to Create a Page with heading and width----*//
def page_build(pdf,heading,width):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #//*----Featured List of Financial Products----*//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(width), px2MM(84),heading,align='L')
    
    #//*---Top Black box
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F')     

    
    
#//*------Banner-----*//
def Banner(pdf,json_data,c_MoneyS,money_signData):
    try:
        # user_name =['name']
        user_name = json_data['meta']["name"]
        if user_name.strip()=="":
            print('No Name in PDF')
            return None
        # user_name = json_data['Name']
    except Exception as e:
        return False
        
    # pdf = FPDF('L','mm','A4')
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0, 0, px2MM(1120), px2MM(1080), 'F')
    
    MoneyS_color = money_signData[c_MoneyS]['Front_P']['Vt_line']
    Date_c = money_signData[c_MoneyS]['Front_P']['Date_c']
    Ms_Image = money_signData[c_MoneyS]['Front_P']['Ms_image']
    
    #/**--For Money sigh right banner

    pdf.set_fill_color(*hex2RGB(MoneyS_color))
    pdf.rect(px2MM(1120), px2MM(0), px2MM(800), px2MM(1080), 'F')
 
    pdf.image(join(cwd,'assets', 'images','money_sign_png',Ms_Image),px2MM(1120), px2MM(0), px2MM(800), px2MM(1080))
 
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0, 0, px2MM(1120), px2MM(1080), 'F')
    
    
    #//*---1F logo--*/
    pdf.image(logo,px2MM(120), px2MM(80), px2MM(98), px2MM(113))
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(120))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(120),px2MM(333))
    pdf.multi_cell(px2MM(796), px2MM(168),'Financial\nWellness Plan')
    # pdf.multi_cell(px2MM(950), px2MM(168),'Financial Analysis')


    
    # Test of User name and Date
    if len(user_name) > 24:
        name_y = 692
    else:
        name_y = 804

    # Test of User name and Date
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(80))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(120),px2MM(name_y))
    pdf.multi_cell(px2MM(924), px2MM(112),user_name.title(),align="L")
    y_after_name = mm2PX(pdf.get_y())


    pdf.set_font('LeagueSpartan-Light', size=px2pts(60))
    pdf.set_text_color(*hex2RGB(Date_c))
    Day=dt.datetime.now().strftime("%d")

    month=dt.datetime.now().strftime("%b")
    year=dt.datetime.now().strftime("%Y")

    if 4 <= int(Day) <= 20 or 24 <= int(Day) <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][int(Day) % 10 - 1]


    pdf.set_fill_color(*hex2RGB('#ffffff'))
    pdf.set_xy(px2MM(120),px2MM(y_after_name))
    pdf.cell(px2MM(60), px2MM(84),str(Day),'LR',align='R')
    
    x_after_day = pdf.get_x()

    pdf.set_font('LeagueSpartan-Light', size=px2pts(36))
    pdf.set_xy(px2MM(mm2PX(x_after_day)-5),px2MM(y_after_name- 10))
    pdf.cell(px2MM(32), px2MM(84),suffix,align='L')


    y_after_suffix = mm2PX(pdf.get_y()) #804
    d_x = pdf.get_x()
    d_x2 = pdf.get_x()
    pdf.set_font('LeagueSpartan-Light', size=px2pts(60))
    pdf.set_xy(px2MM(mm2PX(d_x2)),px2MM(y_after_name))
    pdf.cell(px2MM(100), px2MM(84),' '+str(month)+', '+str(year))
    #//*---Th suffix---*//


    height_of_rect = mm2PX(pdf.get_y())- name_y + 84

    #//*---Left Bottom Vertical Line
    pdf.set_xy(px2MM(0),px2MM(692))
    pdf.set_fill_color(*hex2RGB(MoneyS_color))
    pdf.rect(px2MM(0), px2MM(name_y), px2MM(20), px2MM(height_of_rect), 'F')
    
    
    
# //*----Contents----*//  

def content(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    # pdf.rect()
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080), 'DF')
    
    #//*--Contents banner
    pdf.set_xy(px2MM(120),px2MM(80))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(600), px2MM(84), 'CONTENTS')
    
    #//*----- for vertical dash
    basy_y = 204
    y_gap = 140
    # h_y = 128.83
    fill_color = money_signData[c_MoneyS]['content']
    
    #//*----For Content headings and para
    
    y = 210
    global your_top_most_priority
    global your_fin_analysis_sub_comment
    
    if your_top_most_priority !=0:    
        cont_headings = ['Your Top Most Priority','Your Financial Wellness Plan','Your Financial Profile','Your Financial Analysis']
        if json_data['next_quarter_preview'] == {}: 
            cont_para = ['Stop your losses in Mutual Funds Commissions & Life Insurance Savings Policies','Next 3 Months Action Plan','Financial Behaviour Score, Your 1 view, Assets, Liabilities']  
        else: 
            cont_para = ['Stop your losses in Mutual Funds Commissions & Life Insurance Savings Policies','Next 3 Months Action Plan, Next Consultation Agenda','Financial Behaviour Score, Your 1 view, Assets, Liabilities']  
        index_no = [your_top_most_priority,your_fw_plan_idx,your_fin_prof_idx,your_fin_analysis_idx,fin_feat_product_list,best_practices_idx]
        cont_para.insert(3,", ".join(your_fin_analysis_sub_comment))
    else:
        cont_headings = ['Your Financial Wellness Plan','Your Financial Profile','Your Financial Analysis']
        if json_data['next_quarter_preview'] == {}:
            cont_para = ["Next 3 Months Action Plan","Financial Behaviour Score, Your 1 view, Assets, Liabilities"] 
        else: 
            cont_para = ["Next 3 Months Action Plan, Next Consultation Agenda","Financial Behaviour Score, Your 1 view, Assets, Liabilities"] 
        index_no = [your_fw_plan_idx,your_fin_prof_idx,your_fin_analysis_idx,fin_feat_product_list,best_practices_idx]
        cont_para.insert(2,", ".join(your_fin_analysis_sub_comment))
        
        
        
    # cont_headings = ['Your Financial Profile','Your 1 view','Your Financial Analysis','Your Financial Wellness Plan','Financial Products Featured List','Best Practices']

    # cont_para = ['Financial Behaviour Score, MoneySign  , Generation Profile, Life stage','Snapshot, Detailed Snapshot',"Financial Metrics, Net Worth Projection, Liability Analysis, Insurance Policy Evaluation, MF Holdings Evaluation, Credit Card Evaluation","Key Takeaways, Next 3 Months Action Plan", "Term Insurance Plans, Health Insurance Plans, Equity Mutual Funds, Debt Mutual Funds, Hybrid Mutual Funds, Credit Cards","Building a Strong Credit Profile, Planning Your Income Taxes, Available Tax Deductions, Capital Gains Taxation by Asset Type, Planning For Inheritance, Understanding Inheritance’s Tax Implications, Planning Your Estate and Will"] 
    # index_no = [your_fin_prof_idx,your_1_view_idx,your_fin_analysis_idx,your_fw_plan_idx,fin_feat_product_list,best_practices_idx]
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
    for i in range(len(cont_headings)):
        bar_up=-6
        
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
        if mm2PX(pdf.get_string_width(cont_para[i])) > 1500:
            bar_up = 10
               
        pdf.set_fill_color(*hex2RGB(fill_color[i]))
        pdf.rect(px2MM(120), px2MM(y+bar_up), px2MM(8), px2MM(100), 'F')

        
        

        #//*---Contents for each vertical dash

        pdf.set_draw_color(*hex2RGB('#000000'))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#FFFFFF'))
        pdf.set_line_width(px2MM(2))
        pdf.set_xy(px2MM(168),px2MM(y))
        pdf.cell(px2MM(1500), px2MM(56),cont_headings[i],border='0')


        pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(168),px2MM(y+56))
        pdf.multi_cell(px2MM(1500), px2MM(32),cont_para[i],align='L')
        
        # if mm2PX(pdf.get_string_width(cont_para[i])) > 1500:
        #     new_y = mm2PX(pdf.get_y())+52
        # else:
        new_y = mm2PX(pdf.get_y())+46
        
        #//*---Index Number----*//
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(1675),px2MM(y+25))
        pdf.cell(px2MM(125), px2MM(42),str(index_no[i]),align='R')
        
        y = new_y
        
    
    # #//*--To print superscritp R 
    # pdf.set_font('Inter-Light', size=16)
    # pdf.set_text_color(*hex2RGB('#898B90'))
    # pdf.set_xy(px2MM(550), px2MM(265))
    # pdf.cell(px2MM(16), px2MM(34), '®')
     
    # pdf.set_font('LeagueSpartan-Medium', size=6)
    # pdf.set_text_color(*hex2RGB('#898B90'))
    # pdf.set_xy(px2MM(706), px2MM(273))  
    # pdf.cell(px2MM(16), px2MM(8),'TM') 
    
    # #//*--To print superscritp R 
    # pdf.set_font('LeagueSpartan-Light', size=26)
    # pdf.set_text_color(*hex2RGB('#898B90'))
    # pdf.set_xy(px2MM(707), px2MM(267))
    # pdf.cell(px2MM(16), px2MM(34), '®') 
      

#//*----Financial Behaviour Score----*//  

def fbs(pdf,json_data,c_MoneyS,money_signData):
    try:
        score = json_data['oneview']['fbs']
        score = score if score else 0
    except Exception as e:
        return None

    #//*---Page setup
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080), 'DF')
    
    #//*--Heading vertical line
    vl_color = money_signData[c_MoneyS]['content'][3]
    pdf.set_xy(px2MM(125),px2MM(78))
    pdf.set_fill_color(*hex2RGB(vl_color))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F') 
    
    #//*---heading statement
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(659), px2MM(84),'Financial Behaviour Score') 
    
    #/*--Description--*/
    txt1 = '''Financial Behaviour Score is a numerical representation of your financial well-being, '''
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_xy(px2MM(940),px2MM(325))  
    pdf.multi_cell(px2MM(860), px2MM(56),txt1,align='L') 
    
    pdf.set_font('LeagueSpartan-Light', size=px2pts(36))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_xy(px2MM(1655),px2MM(381))  
    pdf.multi_cell(px2MM(860), px2MM(56),'offering',align='L') 
    
    txt2 = '''an in-depth assessment of how closely your financial choices align with your personality, demography, generation, life constraints, and the macro-economic environment.'''
    pdf.set_xy(px2MM(940),px2MM(437))  
    pdf.multi_cell(px2MM(860), px2MM(56),txt2,align='L') 
    
    #//*----Desclamer---*//
     
    txt = '''Disclaimer: Financial Behaviour Score is part of 1 Finance's patent-pending holistic financial planning framework that is aimed at generating a wellness plan for the customers to help them achieve financial well-being.'''

    pdf.set_xy(px2MM(941),px2MM(702))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#65676D'))
    pdf.multi_cell(px2MM(860), px2MM(32),txt,align='L') 
    
   

    #//*---Scale width is 640(excluding the curve corner) so 1%= 6.4 
    
    if score>=0 and score<=20:
        vl_x = 138+(score*5.75)
    elif score==21:
        vl_x = 272
    elif score>21 and score<=40:
        vl_x = 272+((score-20)*5.75)
    elif score==41:
        vl_x = 406
    elif score>41 and score<=60:
        vl_x = 406+((score-40)*5.75)
    elif score==61:
        vl_x = 540
    elif score>61 and score<=80:
        vl_x = 540+((score-60)*5.75)
    elif score==81:
        vl_x = 674
    elif score>81 and score<=100:
        vl_x = 674+((score-80)*5.75)
    else:
        vl_x=138+(score*6.64)

        
    if score>=0 and score<=21:
        rect_x = 120
        text_x = 165 
    elif score>=82 and score<=100:
        rect_x = 520
        text_x = 565
    else:
        rect_x = (score*6.64)-17
        text_x = 28+ (score*6.64)    
    # vl_x = 138+(score*6.6)
    
     #//*---Score---*//
    if score>=0 and score<=20:
        pdf.image(join(cwd,'assets','images','BehaviourMeter','meter_1_20.png'),px2MM(120), px2MM(627),px2MM(700), px2MM(134))
    elif score>20 and score<=40:
        pdf.image(join(cwd,'assets','images','BehaviourMeter','meter_20_40.png'),px2MM(120), px2MM(627),px2MM(700), px2MM(134))
    elif score>40 and score<=60:
        pdf.image(join(cwd,'assets','images','BehaviourMeter','meter_40_60.png'),px2MM(120), px2MM(627),px2MM(700), px2MM(134))
    elif score>60 and score<=80:
        pdf.image(join(cwd,'assets','images','BehaviourMeter','meter_60_80.png'),px2MM(120), px2MM(627),px2MM(700), px2MM(134))
    else :
        pdf.image(join(cwd,'assets','images','BehaviourMeter','meter_80_100.png'),px2MM(120), px2MM(627),px2MM(700), px2MM(134))
    
      
    #//*---Vertical Line of Score box
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    # pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.rect(px2MM(vl_x), px2MM(532), px2MM(13), px2MM(95), 'F') 
    
    #//*---Score Box
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(rect_x),px2MM(284), px2MM(300), px2MM(248), 'F')
    pdf.set_xy(px2MM(text_x),px2MM(324)) 
    pdf.set_font('Prata', size=px2pts(120))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(209), px2MM(168),str(int(score)),align='C')
    
    # #//*---Scale---*/
    pdf.set_xy(px2MM(120),px2MM(782)) 
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(39))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(600), px2MM(52),'0')
    
    pdf.set_xy(px2MM(761),px2MM(782)) 
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(39))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(59), px2MM(52),'100')

    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
#//*----MoneySign----*//  
  
def money_signtm(pdf,json_data,c_MoneyS,money_signData):
    try:
        # moneySing_desc =['description']
        moneySing_desc = json_data["money_sign"]['money_sign_desc']
    except Exception as e:
        pass
    bg_color = money_signData[c_MoneyS]['Money_Sign'][0]
    vt_line_color = money_signData[c_MoneyS]['Money_Sign'][1]
    ms_name = json_data["money_sign"]['money_sign']
    texture = c_MoneyS+'_text.png'
    #//*---Page setup
    pdf.add_page()
    
    pdf.set_draw_color(*hex2RGB(bg_color))
    pdf.set_fill_color(*hex2RGB(bg_color))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080), 'F') 
    
    #//*----Money Sign Background-****
    pdf.rect(px2MM(0), px2MM(0), px2MM(789.4), px2MM(1080))
    pdf.image(join(cwd,'assets', 'images','MoneySign',texture),px2MM(0), px2MM(0), px2MM(789.4), px2MM(1080))
  
    pdf.rect(px2MM(0), px2MM(0), px2MM(789.4), px2MM(1080))
    pdf.image(join(cwd,'assets', 'images','MoneySign',c_MoneyS+'_overlay.png'),px2MM(0), px2MM(0), px2MM(789.4), px2MM(1080))

    #//*--Purple vertical line
    # pdf.set_xy(px2MM(125),px2MM(78))
    pdf.set_fill_color(*hex2RGB(vt_line_color))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F') 
    
    #//*---heading statement
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(600), px2MM(84),'MoneySign') 
    
    # #//*--To print superscritp TM  of heading
    # pdf.set_xy(px2MM(395), px2MM(83))
    # pdf.set_font('LeagueSpartan-SemiBold', size=26)
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    # pdf.cell(px2MM(30), px2MM(42), 'TM') 
    
    #//*--To print superscritp R 
    pdf.set_font('Inter-Light', size=36)
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(400), px2MM(77))
    pdf.cell(px2MM(90), px2MM(84), '®')  
    
    #//*---Money Sign Logog---*//
    # pdf.rect(0, 0, px2MM(1120), px2MM(1080), 'F')
    pdf.image(join(cwd,'assets', 'images','MoneySign',c_MoneyS+'.png'),px2MM(120), px2MM(224), px2MM(700), px2MM(700))
    
    #//*---Money Sign Name
    pdf.set_xy(px2MM(290),px2MM(924))  
    pdf.set_font('Prata', size=px2pts(42))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(400), px2MM(84),ms_name,align='C') 
    
    #//*----Description---*//

    desc = moneySing_desc.replace('<br><br>','')
    desc = desc.replace('<br>',' ')
    desc = desc.replace('\n','')
    pdf.set_draw_color(*hex2RGB('#E6E0FF'))
    pdf.set_font('LeagueSpartan-Regular',size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#000000'))

    
    if c_MoneyS=='Eagle':
        pdf.set_xy(px2MM(940), px2MM(338))
        
    elif c_MoneyS=='Horse':
        pdf.set_xy(px2MM(940), px2MM(317))
        
    elif c_MoneyS=='Tiger':
        pdf.set_xy(px2MM(940), px2MM(296))
        
    elif c_MoneyS=='Lion':
        pdf.set_xy(px2MM(940), px2MM(275))
        
    elif c_MoneyS=='Elephant':
        pdf.set_xy(px2MM(940), px2MM(317))
        
    elif c_MoneyS=='Turtle':
        pdf.set_xy(px2MM(940), px2MM(233))
        
    elif c_MoneyS=='Whale':
        pdf.set_xy(px2MM(940), px2MM(275))
        
    elif c_MoneyS=='Shark':
        pdf.set_xy(px2MM(940), px2MM(275))
    else:
        pdf.set_xy(px2MM(940), px2MM(275))
   
    pdf.multi_cell(px2MM(860), px2MM(42),desc,align='L')     
    
    #//*----Desclaimer---*//
    desc_y = mm2PX(pdf.get_y())+33
    pdf.set_xy(px2MM(940), px2MM(mm2PX(pdf.get_y())+32))
    pdf.set_font('LeagueSpartan-Regular',size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#4B4C51'))
    pdf.multi_cell(px2MM(860), px2MM(32),"""Disclaimer: MoneySign    is a personality assessment framework based on 1 Finance's""",align='L')
    # pdf.multi_cell(px2MM(860), px2MM(32),"""Disclaimer: MoneySign® is a personality assessment framework based on 1 Finance's""",align='L')
    
    #//*--To print superscritp R 
    pdf.set_xy(px2MM(1160), px2MM(desc_y))
    pdf.set_font('Inter-Light', size=18)
    pdf.set_text_color(*hex2RGB('#4B4C51'))
    pdf.cell(px2MM(16), px2MM(32), '®')  
    
    pdf.set_draw_color(*hex2RGB('#000000'))
    sec_l = pdf.get_y()
    pdf.set_xy(px2MM(940), px2MM(mm2PX(sec_l)+32))
    pdf.set_font('LeagueSpartan-SemiBold',size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#4B4C51'))
    pdf.cell(px2MM(250), px2MM(32),"""patented technology""",align='L')
    
    pdf.set_xy(px2MM(1160), px2MM(mm2PX(sec_l)+32))
    pdf.set_font('LeagueSpartan-Regular',size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#4B4C51'))
    pdf.cell(px2MM(670), px2MM(32),"""that implements one of the most scientifically validated models in""",align='L')
    
    pdf.set_xy(px2MM(940), px2MM(mm2PX(sec_l)+64))
    pdf.set_font('LeagueSpartan-Regular',size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#4B4C51'))
    pdf.cell(px2MM(860), px2MM(32),"""psychology and helps in hyper-personalising the financial suggestions.""",align='L')

    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
#//*----Behavioural Bias----*//
    
def behave_bias(pdf,json_data,c_MoneyS,money_signData):
    
    df=''
    try:
        behav_bias = pd.DataFrame.from_dict(json_data['money_sign']['money_sign_behavioural_bias'])
        if behav_bias.empty:
            return None
            
        behav_bias_keys = list(behav_bias['title'])
    except Exception as e:
        return None
 
    
    page_data = money_signData[c_MoneyS]['behav_bias']
    m_image = page_data[0]
    m_color = page_data[1]
    rect_color = page_data[6]
    img_x = page_data[2]
    img_y = page_data[3]
    img_w = page_data[4]
    img_4 = page_data[5]
    ini = 0
    k = 2
    if len(behav_bias)>1:
        txt2 = """We have also identified some behavioural biases that you’re likely to display while making financial decisions, and should be conscious of:"""
    elif len(behav_bias)<2:
        txt2 = """We have also identified a behavioural bias that you’re likely to display while making financial decisions, and should be conscious of:"""

    for i in range(0,len(behav_bias),2):
        #//*---Page setup
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F') 
        
        #//*---Cloud Images
        pdf.set_draw_color(*hex2RGB('#ffffff'))
        pdf.set_xy(px2MM(750), px2MM(520)) 
        # pdf.image(join(cwd,'assets', 'images','BehaviourBias','bias.png'),px2MM(750), px2MM(520), px2MM(1187.63), px2MM(570.77))
        pdf.image(join(cwd,'assets', 'images','BehaviourBias',m_image),px2MM(img_x), px2MM(img_y), px2MM(img_w), px2MM(img_4))
        
        
        #//*--Purple vertical line
        # pdf.set_xy(px2MM(125),px2MM(78))
        pdf.set_fill_color(*hex2RGB(m_color))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F') 
        
        
        #//*---heading 
        pdf.set_xy(px2MM(120),px2MM(80))  
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(600), px2MM(84),'Behavioural Biases') 
        
        #//*---heading statement
        pdf.set_xy(px2MM(120),px2MM(204))  
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(1300), px2MM(56),txt2) 
        
        
        #//*----Content-----*//
        h_bullet = 414
        h_heading = 396
        h_para = 472
        
        gap_bullet = 284
        gap_heading = 284
        gap_para = 284
        
        for j in range(ini,k):
            
            try:
                if behav_bias_keys[j]:
                    #//* bullet
                    pdf.set_xy(px2MM(120),px2MM(h_bullet))
                    pdf.set_fill_color(*hex2RGB(rect_color))  
                    pdf.rect(px2MM(120),px2MM(h_bullet),px2MM(20),px2MM(20),'F')
                
                #//*--heading
                pdf.set_xy(px2MM(165),px2MM(h_heading))
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
                pdf.set_text_color(*hex2RGB('#000000'))
                pdf.multi_cell(px2MM(1255), px2MM(56),behav_bias_keys[j])
                
                #//*---para
                pdf.set_xy(px2MM(165),px2MM(h_para))
                pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.multi_cell(px2MM(1255), px2MM(42),behav_bias['desc'].iloc[j],align='L')  
                
                h_bullet += gap_bullet
                h_heading += gap_heading
                h_para += gap_para
            except Exception as e:
                pass
        
        ini +=2
        k +=2 
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
   
#//*----Genration Profile----*//    
def gen_profile(pdf,json_data,c_MoneyS,money_signData):
    try:
        # df = pd.DataFrame.from_dict(json_data["Genration"])
        df = json_data["gen_profile"]['gen_profile']
        if df.strip()=="":
            return None
        
    except Exception as e:
        return None

    #//*---Page setup----*//
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F') 
    
    #//*--Purple vertical line
    # pdf.set_xy(px2MM(125),px2MM(78))
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F') 
    
    #//*---heading statement
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(600), px2MM(84),'Generation Profile')
    
    gen_color = money_signData[c_MoneyS]['gen_profile'][0]
    your_profile_color = money_signData[c_MoneyS]['gen_profile'][1]
    bullet_profile_color = money_signData[c_MoneyS]['gen_profile'][2]
    
    if df=='Generation 1':
        pdf.set_fill_color(*hex2RGB(gen_color))
        pdf.rect(px2MM(120), px2MM(204), px2MM(527), px2MM(915), 'F')
        pdf.image(join(cwd,'assets','images','genration profile','shade.png'),px2MM(120), px2MM(204), px2MM(527), px2MM(915))
        
        pdf.set_fill_color(*hex2RGB('#1A1A1D'))
        pdf.rect(px2MM(697), px2MM(204), px2MM(527), px2MM(915), 'F')
        
        pdf.set_fill_color(*hex2RGB('#1A1A1D'))
        pdf.rect(px2MM(1273), px2MM(204), px2MM(527), px2MM(915), 'F')
        sq_bullet_1 = bullet_profile_color
        sq_bullet_2 = '#313236'
        sq_bullet_3 = '#313236'
        
    elif df=='Generation 2':
        pdf.set_fill_color(*hex2RGB('#1A1A1D'))
        pdf.rect(px2MM(120), px2MM(204), px2MM(527), px2MM(915), 'F')
        
        pdf.set_fill_color(*hex2RGB(gen_color))
        pdf.rect(px2MM(697), px2MM(204), px2MM(527), px2MM(915), 'F')
        pdf.image(join(cwd,'assets','images','genration profile','shade.png'),px2MM(697), px2MM(204), px2MM(527), px2MM(915))
        
        pdf.set_fill_color(*hex2RGB('#1A1A1D'))
        pdf.rect(px2MM(1273), px2MM(204), px2MM(527), px2MM(915), 'F')
        sq_bullet = ['#313236',bullet_profile_color,'#313236']
        sq_bullet_1 = '#313236'
        sq_bullet_2 = bullet_profile_color
        sq_bullet_3 = '#313236'
    else:
        pdf.set_fill_color(*hex2RGB('#1A1A1D'))
        pdf.rect(px2MM(120), px2MM(204), px2MM(527), px2MM(915), 'F')
        
        pdf.set_fill_color(*hex2RGB('#1A1A1D'))
        pdf.rect(px2MM(697), px2MM(204), px2MM(527), px2MM(915), 'F')
        
        pdf.set_fill_color(*hex2RGB(gen_color))
        pdf.rect(px2MM(1273), px2MM(204), px2MM(527), px2MM(915), 'F')
        pdf.image(join(cwd,'assets','images','genration profile','shade.png'),px2MM(1273), px2MM(195), px2MM(527), px2MM(915))
        sq_bullet = ['#313236','#313236',bullet_profile_color]
        sq_bullet_1 = '#313236'
        sq_bullet_2 = '#313236'
        sq_bullet_3 = bullet_profile_color

        
    #//*---For base Rectangle---*//
    #//*-------------Card 1-----------*//
    #//*----For Heading (Genrations)---*//
    pdf.set_xy(px2MM(277),px2MM(244))  
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(215), px2MM(56),'Generation 1')

    
    #//*----Personality Traits---*/
    pdf.set_xy(px2MM(160),px2MM(330))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    
    # pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.cell(px2MM(447), px2MM(35),'PERSONALITY TRAITS')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(160), px2MM(372), px2MM(447), px2MM(1))
    
        
    #//*--Point 1---*//
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_1))
    pdf.rect(px2MM(160), px2MM(393), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(190),px2MM(380))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Primary bread-earner in family',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_1))
    pdf.rect(px2MM(160), px2MM(446), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(190),px2MM(419))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Work hard to provide for their loved ones despite limited education',align='L') 

    
    #//*----Financial Behaviour---*/
    pdf.set_xy(px2MM(160),px2MM(523))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(447), px2MM(35),'FINANCIAL BEHAVIOUR')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(160), px2MM(565), px2MM(447), px2MM(1))

    
    #//*--Point 3 to 4---*//
    pdf.set_fill_color(*hex2RGB(sq_bullet_1))
    pdf.rect(px2MM(160), px2MM(586), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(190),px2MM(575))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Earning for basic sustenance',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_1))
    pdf.rect(px2MM(160), px2MM(639), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(190),px2MM(612))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Prioritize stability and security over taking risks with their finances',align='L') 
    
    #//*----ASPIRATIONA---*/
    pdf.set_xy(px2MM(160),px2MM(716))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(447), px2MM(30),'ASPIRATIONS')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(160), px2MM(758), px2MM(447), px2MM(1))
    
    #//*--Point 5 to 3---*//
    pdf.set_fill_color(*hex2RGB(sq_bullet_1))
    pdf.rect(px2MM(160), px2MM(779), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(190),px2MM(768))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Providing social security to family',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_1))
    pdf.rect(px2MM(160), px2MM(816), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(190),px2MM(805))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Giving basic lifestyle to next generation',align='L') 

    #//*----Examples of Priorities---*/
    pdf.set_xy(px2MM(160),px2MM(877))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(457), px2MM(35),'EXAMPLE OF PRIORITIES')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(160), px2MM(919), px2MM(447), px2MM(1))
    
    #//*--Point 5 to 3---*//
    pdf.set_fill_color(*hex2RGB(sq_bullet_1))
    pdf.rect(px2MM(160), px2MM(956), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(190),px2MM(929))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Upgrading existing living facility to one with basic comfort and necessities',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_1))
    pdf.rect(px2MM(160), px2MM(1009), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(190),px2MM(998))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(32),'Living a dignified life in society') 
    
    
     #//*-------------Card 2-----------*//
    #//*----For Heading (Genrations)---*//
    pdf.set_xy(px2MM(850),px2MM(244))  
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(215), px2MM(56),'Generation 2')

    
    #//*----Personality Traits---*/
    pdf.set_xy(px2MM(737),px2MM(330))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    
    # pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.cell(px2MM(447), px2MM(35),'PERSONALITY TRAITS')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(737), px2MM(372), px2MM(447), px2MM(1))
    
        
    #//*--Point 1---*//
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_2))
    pdf.rect(px2MM(737), px2MM(393), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(767),px2MM(380))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Well-educated and skilled professional',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_2))
    pdf.rect(px2MM(737), px2MM(430), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(767),px2MM(419))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Focused on improving current lifestyle',align='L') 

    
    #//*----Financial Behaviour---*/
    pdf.set_xy(px2MM(737),px2MM(481))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(447), px2MM(35),'FINANCIAL BEHAVIOUR')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(737), px2MM(523), px2MM(447), px2MM(1))

    
    #//*--Point 3 to 4---*//
    pdf.set_fill_color(*hex2RGB(sq_bullet_2))
    pdf.rect(px2MM(737), px2MM(544), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(767),px2MM(533))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(425), px2MM(30),'Save mindfully to build a reasonable corpus',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_2))
    pdf.rect(px2MM(737), px2MM(613), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(767),px2MM(570))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Prefer traditional investment options such as bank deposits, mutual funds, insurance plus investment plans etc.',align='L') 
    
    #//*----ASPIRATIONA---*/
    pdf.set_xy(px2MM(737),px2MM(696))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(447), px2MM(30),'ASPIRATIONS')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(737), px2MM(738), px2MM(447), px2MM(1))
    
    #//*--Point 5 to 3---*//
    pdf.set_fill_color(*hex2RGB(sq_bullet_2))
    pdf.rect(px2MM(737), px2MM(775), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(767),px2MM(748))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Providing a good lifestyle and education for future generations',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_2))
    pdf.rect(px2MM(737), px2MM(844), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(767),px2MM(817))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Achieving financial freedom to have more control over time',align='L') 

    #//*----Examples of Priorities---*/
    pdf.set_xy(px2MM(737),px2MM(911)) 
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(457), px2MM(35),'EXAMPLE OF PRIORITIES')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(737), px2MM(953), px2MM(447), px2MM(1))
    
    #//*--Point 5 to 3---*//
    pdf.set_fill_color(*hex2RGB(sq_bullet_2))
    pdf.rect(px2MM(737), px2MM(974), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(767),px2MM(963))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Creating secondary source of income')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_2))
    pdf.rect(px2MM(737), px2MM(1027), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(767),px2MM(1000))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(32),'Buying a quality car and a home with good amenities')
    
    #//*----------Card 3-------*//
    #//*----For Heading (Genrations)---*//
    pdf.set_xy(px2MM(1426),px2MM(244))  
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(215), px2MM(56),'Generation 3')

    
    #//*----Personality Traits---*/
    pdf.set_xy(px2MM(1313),px2MM(330))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    
    # pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.cell(px2MM(447), px2MM(35),'PERSONALITY TRAITS')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(1313), px2MM(372), px2MM(447), px2MM(1))
    
        
    #//*--Point 1---*//
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_3))
    pdf.rect(px2MM(1313), px2MM(409), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(1343),px2MM(380))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Early adopter of new trends and global products',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_3))
    pdf.rect(px2MM(1313), px2MM(478), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(1343),px2MM(451))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Willing to take high risks in pursuit of potential rewards',align='L') 

    
    #//*----Financial Behaviour---*/
    pdf.set_xy(px2MM(1313),px2MM(545))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(447), px2MM(35),'FINANCIAL BEHAVIOUR')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(1313), px2MM(587), px2MM(447), px2MM(1))

    
    #//*--Point 3 to 4---*//
    pdf.set_fill_color(*hex2RGB(sq_bullet_3))
    pdf.rect(px2MM(1313), px2MM(608), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(1343),px2MM(597))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(425), px2MM(30),'Focused on building wealth',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_3))
    pdf.rect(px2MM(1313), px2MM(645), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(1343),px2MM(634))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Like experimenting with risky asset classes',align='L') 
    
    #//*----ASPIRATIONA---*/
    pdf.set_xy(px2MM(1313),px2MM(696))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(447), px2MM(30),'ASPIRATIONS')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(1313), px2MM(738), px2MM(447), px2MM(1))
    
    #//*--Point 5 to 3---*//
    pdf.set_fill_color(*hex2RGB(sq_bullet_3))
    pdf.rect(px2MM(1313), px2MM(759), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(1343),px2MM(748))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Interested in luxury purchases',align='L')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_3))
    pdf.rect(px2MM(1313), px2MM(812), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(1343),px2MM(785))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Driven to start new businesses and pursue hobbies as a profession',align='L') 

    #//*----Examples of Priorities---*/
    pdf.set_xy(px2MM(1313),px2MM(879)) 
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.cell(px2MM(457), px2MM(35),'EXAMPLE OF PRIORITIES')
    pdf.image(join(cwd,'assets','images','genration profile','shade_line.png'),px2MM(1313), px2MM(921), px2MM(447), px2MM(1))
    
    #//*--Point 5 to 3---*//
    pdf.set_fill_color(*hex2RGB(sq_bullet_3))
    pdf.rect(px2MM(1313), px2MM(958), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(1343),px2MM(931))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(30),'Growing investment portfolio by investing in alternative assets')
    
    pdf.set_fill_color(*hex2RGB(sq_bullet_3))
    pdf.rect(px2MM(1313), px2MM(1027), px2MM(10), px2MM(10),'F')
    
    pdf.set_xy(px2MM(1343),px2MM(1000))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#E9EAEE'))
    pdf.set_draw_color(*hex2RGB('#313236'))
    pdf.multi_cell(px2MM(417), px2MM(32),'Staying informed and educated about financial trends and new products')
    
        
    #//**----For Your Profile box---*//
    if df=='Generation 1':
        pdf.set_fill_color(*hex2RGB(your_profile_color))
        pdf.rect(px2MM(120), px2MM(204), px2MM(117), px2MM(35),'F')
        pdf.set_xy(px2MM(132),px2MM(209))  
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(87), px2MM(25.2),'Your Profile') 
    
    elif df=='Generation 2':
        pdf.set_fill_color(*hex2RGB(your_profile_color))
        pdf.rect(px2MM(697), px2MM(204), px2MM(117), px2MM(35),'F')
        pdf.set_xy(px2MM(710),px2MM(209))  
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(87), px2MM(25),'Your Profile')
        
    elif df=='Generation 3':
        pdf.set_fill_color(*hex2RGB(your_profile_color))
        pdf.rect(px2MM(1273), px2MM(204), px2MM(117), px2MM(35),'F')
        pdf.set_xy(px2MM(1288),px2MM(209))  
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(87), px2MM(25.2),'Your Profile')  
    else:
        pass

    #//*-----Index Text of Page--**////
    index_text(pdf,'#FFFFFF')
#//*----Net Worth------*//

def net_worth(pdf,json_data,c_MoneyS,money_signData):
    try:
        df = json_data["networth"]
        # df2 = pd.DataFrame.from_dict(json_data['val_un_adv'])
    except Exception as e:
        return None
    
   
    #//*---Page setup----*//
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F') 
    
    #//*--Purple vertical line
    # pdf.set_xy(px2MM(125),px2MM(78))
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F') 
    
    #//*---heading statement
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(600), px2MM(84),'Net worth')
    
    #//*---What is Net worth
    pdf.set_xy(px2MM(400),px2MM(244))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    text2 = '''Your net worth is simply the difference between'''
    pdf.cell(px2MM(790), px2MM(56),text2,align='C',markdown=True)
    
    pdf.set_xy(px2MM(1190),px2MM(244))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    text2 = '''what you own'''
    pdf.cell(px2MM(250), px2MM(56),text2,align='C',markdown=True)
    
    pdf.set_xy(px2MM(1440),px2MM(244))  
    pdf.set_font('LeagueSpartan-Regular',size=px2pts(40))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    text2 = '''(like'''
    pdf.cell(px2MM(70), px2MM(56),text2,align='C',markdown=True)
    
    pdf.set_xy(px2MM(390),px2MM(300))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    text2 = '''your house, retirement funds, etc) and'''
    pdf.cell(px2MM(640), px2MM(56),text2,align='L',markdown=True)
    
    pdf.set_xy(px2MM(1030),px2MM(300))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    text2 = '''what you owe'''
    pdf.cell(px2MM(240), px2MM(56),text2,align='L',markdown=True)
    
    pdf.set_xy(px2MM(1275),px2MM(300))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    text2 = '''(your liabilities'''
    pdf.cell(px2MM(250), px2MM(56),text2,align='L',markdown=True)
    
    pdf.set_xy(px2MM(390),px2MM(356))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    text2 = '''such as mortgage, credit card debt and so forth).'''
    pdf.cell(px2MM(1130), px2MM(56),text2,align='C',markdown=True)
    
    #//*---Rect---*//
    
    #//*--White rect dynamic x
    white_rect = ('Total Assets','Total Liabilities','Networth')
    white_rect_x = 140
    white_rect_x_gap = 560
    white_rect_text_x = 180
    white_rect_text_x_gap = 560
    
    #//*--Color rect dynamic x
    color_rect = ('#7C5FF2','#FFCA41','#4DC3A7')
    tot_assets = '₹ ' +str(format_cash2(float(df['assets'])))
    tot_liab = '₹ ' +str(format_cash2(float(df['liabilities'])))
    tot_networth = '₹ ' +str(format_cash2(float(df['networth'])))
    
    #//*---Total networth = Total_Assets - Total_Liabilities
    color_rect_val = (tot_assets,tot_liab,tot_networth)
    color_rect_x = 235
    color_rect_x_gap = 560
    color_rect_text_x = 275
    color_rect_text_x_gap = 560
    
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    for i in range(3):
        #//*---White rectangle with text
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(white_rect_x),px2MM(492),px2MM(520),px2MM(173),'FD')
        
        pdf.set_xy(px2MM(white_rect_text_x),px2MM(532))  
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(440), px2MM(56),white_rect[i],border=0,align='C')
        white_rect_x+=white_rect_x_gap
        white_rect_text_x+=white_rect_text_x_gap
        
        #//*---Color Rect with text---*//
        pdf.set_fill_color(*hex2RGB(color_rect[i]))
        pdf.rect(px2MM(color_rect_x),px2MM(618),px2MM(330),px2MM(158),'F')
        
        pdf.set_xy(px2MM(color_rect_text_x),px2MM(658))  
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(56))
        pdf.set_text_color(*hex2RGB('#FFFFFF'))
        pdf.cell(px2MM(250), px2MM(78),color_rect_val[i],border=0,align='C')
        color_rect_x+=color_rect_x_gap
        color_rect_text_x+=color_rect_text_x_gap
      
    #//*---For circle operator symbol 
    
    white_circle1_x = 639                              
    common_gap = 564 
                              
    color_circle_x = 653                                
    
    opt_x = 667.33  
    opt_val = ('-','=')
    opt_height=(3.33,13.33) 
    
                           
    for i in range(2):
        #//*---white outer circle---*//
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.circle(x=px2MM(white_circle1_x),y=px2MM(539),r=px2MM(80),style='F')
        
        #//*---Color Inner circle---*//
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.circle(x=px2MM(color_circle_x),y=px2MM(553),r=px2MM(52),style='F')
        
        #//*---For operator
        pdf.set_xy(px2MM(opt_x),px2MM(572.33))  
        pdf.set_font('LeagueSpartan-Light', size=px2pts(70))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(23.33), px2MM(opt_height[i]),opt_val[i],border=0,align='C')
        
        white_circle1_x+=common_gap
        color_circle_x+=common_gap
        opt_x+=common_gap
        
    #//*----For Value under Adivisoary---*//
    
        pdf.set_xy(px2MM(705),px2MM(892))  
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(374), px2MM(56),'Value Under Advisory:',border=0,align='L')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
        pdf.set_xy(px2MM(1090),px2MM(892)) 
        val_ud_adv = '₹ '+str(format_cash2(float(df['value_under_advisory'])))
        pdf.cell(px2MM(374), px2MM(56),val_ud_adv,border=0,align='L')
        
        pdf.set_xy(px2MM(250),px2MM(968)) 
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
        pdf.cell(px2MM(1419), px2MM(32),'This includes total of your assets and liabilities.',border=0,align='C')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
        
#//*----Expense and Liability Management------*//

def exp_lib_mang(pdf,json_data,c_MoneyS,money_signData):
    try:
        exp_lib_mang = json_data["ratios"]
        if exp_lib_mang=={}:
           return None 
    except Exception as e:
        return None
    
    exp_lib_mang_keys = list(exp_lib_mang.keys())
   
    #//*---Page setup----*//
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F') 
    
    pdf.image(join(cwd,'assets','images','backgrounds','doubleLine.png'),px2MM(1449),px2MM(0),px2MM(471),px2MM(1080))
    
    #//*--Purple vertical line
    # pdf.set_xy(px2MM(125),px2MM(78))
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')
    
    #//*----Purple Rectange of Heading Expense and Liability Management
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(1310), px2MM(81), px2MM(490), px2MM(82),'F')
    
    pdf.set_xy(px2MM(1330),px2MM(101)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.cell(px2MM(450), px2MM(42),'Expense and Liability Management')
     
    #//*---heading statement
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(589), px2MM(84),'Your Financial Analysis')
    

    # all_statements = df['Comments']
    #//*----6 Boxes--*//
    main_box_x =main_box_x1 = 120
    heading_label_x = heading_label_x1 = 160
    x_common_gap = x1_common_gap = 577
    score_box_x = score_box_x1 = 160
    score_x = score_x1 = 170
    ideal_range_x = ideal_range_x1 = 400
    all_stat_x = all_stat_x1 = 160
    
    
    # ideal_min = df["Ideal Range"]
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    for i in range(3):
        
        #//*---vor horizontol Boxes Row 1
        
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.rect(px2MM(main_box_x), px2MM(204), px2MM(527), px2MM(362),'FD')
        
        #//*----Box Headings----*//
        pdf.set_xy(px2MM(heading_label_x),px2MM(244)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#2E3034'))
        pdf.cell(px2MM(447), px2MM(39),exp_lib_mang[exp_lib_mang_keys[i]]['title'],align='L')
        
        #//*----Color Score Box---*//
        
        if exp_lib_mang[exp_lib_mang_keys[i]]['color']=='green':
            pdf.set_fill_color(*hex2RGB('#71EBB8'))
        else:
            pdf.set_fill_color(*hex2RGB('#FF937B'))
            
        pdf.rect(px2MM(score_box_x), px2MM(313), px2MM(102), px2MM(52),'F')
        
        pdf.set_xy(px2MM(score_x),px2MM(318)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(82), px2MM(42),str(round(float(exp_lib_mang[exp_lib_mang_keys[i]]['total'])*100))+'%',align='C')
        
        #//*-----Ideal Ranges
        pdf.set_xy(px2MM(ideal_range_x),px2MM(323)) 
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        if exp_lib_mang[exp_lib_mang_keys[i]]['ideal_range'] =="":
            pdf.cell(px2MM(204), px2MM(32),'',align='R')
        else:
            # val = exp_lib_mang[exp_lib_mang_keys[i]]['ideal_range'].split('-')
            val = exp_lib_mang[exp_lib_mang_keys[i]]['ideal_range']
            # val = " - ".join(list(str(format_cash2(float(x))) for x in val))
            pdf.cell(px2MM(204), px2MM(32),'Ideal: '+val,align='R')
        
        #//*----Statements----*//
        pdf.set_xy(px2MM(all_stat_x),px2MM(395)) 
        pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(447), px2MM(32),exp_lib_mang[exp_lib_mang_keys[i]]['comment'],align='L')
        
        main_box_x+= x_common_gap
        score_box_x+=x_common_gap
        score_x+=x_common_gap
        ideal_range_x+=x_common_gap
        heading_label_x+=x_common_gap
        all_stat_x+=x_common_gap
        
        
    #//*----Lower 3 boxes----*//    
    main_box_x1 = 120
    heading_label_x1 = 160
    x1_common_gap = 577
    score_box_x1 = 160
    score_x1 = 170
    ideal_range_x1 = 400
    all_stat_x1 = 160
    
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))    
    for i in range(3,6):
        
        #//*---vor horizontol Boxes Row 2
        
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.rect(px2MM(main_box_x1), px2MM(616), px2MM(527), px2MM(362),'FD')
        
        #//*----Box Headings----*//
        pdf.set_xy(px2MM(heading_label_x1),px2MM(656)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#2E3034'))
        pdf.cell(px2MM(447), px2MM(39),exp_lib_mang[exp_lib_mang_keys[i]]['title'],align='L')
        
        #//*----Color Score Box---*//
        
        if exp_lib_mang[exp_lib_mang_keys[i]]['color']=='green':
            pdf.set_fill_color(*hex2RGB('#71EBB8'))
        else:
            pdf.set_fill_color(*hex2RGB('#FF937B'))
            
        pdf.rect(px2MM(score_box_x1), px2MM(715), px2MM(102), px2MM(52),'F')
        
        pdf.set_xy(px2MM(score_x1),px2MM(720)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(82), px2MM(42),str(round(float(exp_lib_mang[exp_lib_mang_keys[i]]['total'])*100))+'%',align='C')
        
        #//*-----Ideal Ranges
        pdf.set_xy(px2MM(ideal_range_x1),px2MM(735)) 
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        if exp_lib_mang[exp_lib_mang_keys[i]]['ideal_range'] =="":
            pdf.cell(px2MM(204), px2MM(32),'',align='R')
        else:
            val = exp_lib_mang[exp_lib_mang_keys[i]]['ideal_range']
            # val = exp_lib_mang[exp_lib_mang_keys[i]]['ideal_range'].split('-')
            # val = " - ".join(list(str(format_cash2(float(x))) for x in val))
            pdf.cell(px2MM(204), px2MM(32),'Ideal: '+val,align='R')
        
        #//*----Statements----*//
        pdf.set_xy(px2MM(all_stat_x1),px2MM(807)) 
        pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(447), px2MM(32),exp_lib_mang[exp_lib_mang_keys[i]]['comment'],align='L')
        
        main_box_x1+= x1_common_gap
        score_box_x1+=x1_common_gap
        score_x1+=x1_common_gap
        ideal_range_x1+=x1_common_gap
        heading_label_x1+=x1_common_gap
        all_stat_x1+=x1_common_gap
        
    pdf.set_xy(px2MM(250),px2MM(1019)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    txt = '''Disclaimer: The red shade denotes a value that falls outside of the suggested range for a given metric, while a green shade indicates a value that falls within that suggested range.'''
    pdf.cell(px2MM(1420), px2MM(21.09),txt,align='C')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    global your_fin_analysis_idx
    if your_fin_analysis_idx == 0:
        your_fin_analysis_idx = pdf.page_no()
       
       
#//*----Asset Alocation------*//

def asset_allocation(pdf,json_data,c_MoneyS,money_signData):
    try:
        asset_alloc = json_data['asset_allocation']
        if asset_alloc=={}:
            return None
    except Exception as e:
        return None
    
    asset_alloc_keys = list(asset_alloc.keys())
    
    #//*---Page setup----*//
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F') 
    
    pdf.image(join(cwd,'assets','images','backgrounds','doubleLine.png'),px2MM(1449),px2MM(0),px2MM(471),px2MM(1080))
    
    #//*--Purple vertical line
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')
    
    #//*----Black Rectange of Heading Expense and Liability Management
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(1554), px2MM(81), px2MM(246), px2MM(82),'F')
    
    pdf.set_xy(px2MM(1574),px2MM(101)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.cell(px2MM(206), px2MM(42),'Asset Allocation')
     
    #//*---heading statement
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(589), px2MM(84),'Your Financial Analysis')

    # all_statements = df['Comments']
    #//*----6 Boxes--*//
    main_box_x =main_box_x1 = 120
    heading_label_x = heading_label_x1 = 160
    x_common_gap = x1_common_gap = 577
    score_box_x = score_box_x1 = 160
    score_x = score_x1 = 170
    ideal_range_x = ideal_range_x1 = 400
    all_stat_x = all_stat_x1 = 160

    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    for i in range(3):
        
        #//*---vor horizontol Boxes Row 1
        
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.rect(px2MM(main_box_x), px2MM(204), px2MM(527), px2MM(362),'FD')
        
        #//*----Box Headings----*//
        pdf.set_xy(px2MM(heading_label_x),px2MM(244)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#2E3034'))
        pdf.cell(px2MM(447), px2MM(39),asset_alloc[asset_alloc_keys[i]]['title'],align='L')
        
        #//*----Color Score Box---*//

        if asset_alloc[asset_alloc_keys[i]]['color']=='green':
            pdf.set_fill_color(*hex2RGB('#71EBB8'))
        else:
            pdf.set_fill_color(*hex2RGB('#FF937B'))
            
        pdf.rect(px2MM(score_box_x), px2MM(313), px2MM(102), px2MM(52),'F')
        
        pdf.set_xy(px2MM(score_x),px2MM(318)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(82), px2MM(42),str(round(float(asset_alloc[asset_alloc_keys[i]]['total'])*100))+'%',align='C')
        
        #//*-----Ideal Ranges
        pdf.set_xy(px2MM(ideal_range_x),px2MM(323)) 
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        if asset_alloc[asset_alloc_keys[i]]['ideal_range']=="":
            pdf.cell(px2MM(204), px2MM(32),'',align='R')
        else:
            val = asset_alloc[asset_alloc_keys[i]]['ideal_range']
            pdf.cell(px2MM(204), px2MM(32),'Ideal: '+val,align='R')
        
        #//*----Statements----*//
        pdf.set_xy(px2MM(all_stat_x),px2MM(395)) 
        pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(447), px2MM(32),asset_alloc[asset_alloc_keys[i]]['comment'],align='L')
        
        main_box_x+= x_common_gap
        score_box_x+=x_common_gap
        score_x+=x_common_gap
        ideal_range_x+=x_common_gap
        heading_label_x+=x_common_gap
        all_stat_x+=x_common_gap
        
        
    #//*----Lower 3 boxes----*//    
    main_box_x1 = 120
    heading_label_x1 = 160
    x1_common_gap = 577
    score_box_x1 = 160
    score_x1 = 170
    ideal_range_x1 = 400
    all_stat_x1 = 160
    
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))    
    for i in range(3,5):
        
        #//*---vor horizontol Boxes Row 1
        
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.rect(px2MM(main_box_x1), px2MM(616), px2MM(527), px2MM(362),'FD')
        
        #//*----Box Headings----*//
        pdf.set_xy(px2MM(heading_label_x1),px2MM(656)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#2E3034'))
        pdf.cell(px2MM(447), px2MM(39),asset_alloc[asset_alloc_keys[i]]['title'],align='L')
        
        #//*----Color Score Box---*//
        # if float(df['Actual'][i])>=ideal_mean[i] and float(df['Actual'][i])<=ideal_max[i]:
        #     pdf.set_fill_color(*hex2RGB('#71EBB8'))
        # else:
        #     pdf.set_fill_color(*hex2RGB('#FF937B'))
        
        if asset_alloc[asset_alloc_keys[i]]['color']=='green':
            pdf.set_fill_color(*hex2RGB('#71EBB8'))
        else:
            pdf.set_fill_color(*hex2RGB('#FF937B'))
            
        pdf.rect(px2MM(score_box_x1), px2MM(715), px2MM(102), px2MM(52),'F')
        
        pdf.set_xy(px2MM(score_x1),px2MM(720)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(82), px2MM(42),str(round(float(asset_alloc[asset_alloc_keys[i]]['total'])*100))+'%',align='C')
        
        #//*-----Ideal Ranges
        pdf.set_xy(px2MM(ideal_range_x1),px2MM(735)) 
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        if asset_alloc[asset_alloc_keys[i]]['ideal_range']=="":
            pdf.cell(px2MM(204), px2MM(32),'',align='R')
        else:
            val = asset_alloc[asset_alloc_keys[i]]['ideal_range']
            # val = asset_alloc[asset_alloc_keys[i]]['ideal_range'].split('-')
            # val = " - ".join(list(str(format_cash2(float(x))) for x in val))
            pdf.cell(px2MM(204), px2MM(32),'Ideal: '+val,align='R')
        
        #//*----Statements----*//
        pdf.set_xy(px2MM(all_stat_x1),px2MM(807)) 
        pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(447), px2MM(32),asset_alloc[asset_alloc_keys[i]]['comment'],align='L')
        
        main_box_x1+= x1_common_gap
        score_box_x1+=x1_common_gap
        score_x1+=x1_common_gap
        ideal_range_x1+=x1_common_gap
        heading_label_x1+=x1_common_gap
        all_stat_x1+=x1_common_gap
        
    pdf.set_xy(px2MM(250),px2MM(1019)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    txt = '''Disclaimer: The red shade denotes a value that falls outside of the suggested range for a given metric, while a green shade indicates a value that falls within that suggested range.'''
    pdf.cell(px2MM(1420), px2MM(21.09),txt,align='C')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    global your_fin_analysis_idx
    if your_fin_analysis_idx == 0:
        your_fin_analysis_idx = pdf.page_no()
             
#//*----Emergency Planning------*//

def emergency_planning(pdf,json_data,c_MoneyS,money_signData):
    try:
        emergency = json_data['emergency']
        if emergency=={}:
            return None      
    except Exception as e:
        return None
    
   
    #//*---Page setup----*//
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F') 
    
    pdf.image(join(cwd,'assets','images','backgrounds','doubleLine.png'),px2MM(1449),px2MM(0),px2MM(471),px2MM(1080))
    
    #//*--Purple vertical line
    # pdf.set_xy(px2MM(125),px2MM(78))
    pdf.set_fill_color(*hex2RGB('#000000'))
    
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')
    
    #//*----Black Rectange of Heading Expense and Liability Management
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(1499), px2MM(81), px2MM(301), px2MM(82),'F')
    
    pdf.set_xy(px2MM(1519),px2MM(101)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.cell(px2MM(206), px2MM(42),'Emergency Planning')
     
    #//*---heading statement
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(589), px2MM(84),'Your Financial Analysis')
    
    
    # all_statements = df['Comments']
    #//*----6 Boxes--*//
    main_box_x =main_box_x1 = 120
    heading_label_x = heading_label_x1 = 160
    x_common_gap = x1_common_gap = 577
    score_box_x = score_box_x1 = 160
    score_x = score_x1 = 170
    ideal_range_x = ideal_range_x1 = 400
    all_stat_x = all_stat_x1 = 160
    
    
    # ideal_min = df['Ideal']
    emergency_keys = list(emergency.keys())
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    for i in range(len(emergency)):
        #//*---vor horizontol Boxes Row 1
        
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.rect(px2MM(main_box_x), px2MM(264), px2MM(527), px2MM(362),'FD')
        
        #//*----Box Headings----*//
        pdf.set_xy(px2MM(heading_label_x),px2MM(304)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#2E3034'))
        pdf.cell(px2MM(447), px2MM(39),emergency[emergency_keys[i]]['title'],align='L')
        
        #//*----Color Score Box---*//


        if emergency[emergency_keys[i]]['color'].lower() =='green':
            pdf.set_fill_color(*hex2RGB('#71EBB8'))
        else:
            pdf.set_fill_color(*hex2RGB('#FF937B'))
            
        pdf.rect(px2MM(score_box_x), px2MM(373), px2MM(119), px2MM(52),'F')
        
        pdf.set_xy(px2MM(score_x),px2MM(378)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        # pdf.cell(px2MM(70), px2MM(42),str(int(df["Actual"][i]))+str(df["unit2"][i]),align='C')
        if emergency[emergency_keys[i]]['total'] == "0" or emergency[emergency_keys[i]]['total'] == "0.0":
            pdf.cell(px2MM(90), px2MM(42),'₹ 0.0L',align='C')
        else:
            pdf.cell(px2MM(90), px2MM(42),'₹ '+str(format_cash2(float(emergency[emergency_keys[i]]['total']))),align='C')
        
        #//*-----Ideal Ranges
        pdf.set_xy(px2MM(ideal_range_x),px2MM(383)) 
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        # ideal_range = str(ideal_min[i]).split('-')
        # pdf.cell(px2MM(204), px2MM(32),'Ideal: '+str(ideal_min[i])+str(df['unit1'][i]),align='C')
        if emergency[emergency_keys[i]]['ideal_range']=="":
            pdf.cell(px2MM(204), px2MM(32),'',align='R')
        else:
            val = emergency[emergency_keys[i]]['ideal_range'].split('-')
            val = " - ".join(list('₹ '+str(format_cash2(float(x))) for x in val))
            pdf.cell(px2MM(204), px2MM(32),'Ideal: '+val,align='R')
        
        #//*----Statements----*//
        pdf.set_xy(px2MM(all_stat_x),px2MM(455)) 
        pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(447), px2MM(32),emergency[emergency_keys[i]]['comment'],align='L')
        
        main_box_x+= x_common_gap
        score_box_x+=x_common_gap
        score_x+=x_common_gap
        ideal_range_x+=577
        heading_label_x+=x_common_gap
        all_stat_x+=x_common_gap
        
        
    #//*----Lower 3 boxes----*//    
    main_box_x1 = 120
    heading_label_x1 = 160
    x1_common_gap = 577
    score_box_x1 = 160
    score_x1 = 170
    ideal_range_x1 = 403
    all_stat_x1 = 160
    
    pdf.set_xy(px2MM(250),px2MM(1019)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    txt = '''Disclaimer: The red shade denotes a value that falls outside of the suggested range for a given metric, while a green shade indicates a value that falls within that suggested range.'''
    pdf.cell(px2MM(1420), px2MM(21.09),txt,align='C')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    global your_fin_analysis_idx
    your_fin_analysis_idx = pdf.page_no()
    
#//*-------Assets(pIEcHART)-----*//    
def assets_chart(pdf,json_data,c_MoneyS,money_signData):
    try:
        # df = pd.DataFrame.from_dict(json_data["Snapshot of Holding - Asset"])
        df_table = json_data["assets"]['table']
        df_pie = pd.DataFrame.from_dict(json_data["assets"]['pie'])
    except Exception as e:
        return None
    
    if df_pie.empty:
        return None

    tab_total = json_data["assets"]['total']
    tab_total['asset']='Total'
    tab_total['asset_class']=''
    tab_total['percentage']=''
    
    df_table.append(tab_total)
        
    flag = False
    

    for i in range(len(df_pie['percentage'])):
        if float(df_pie['percentage'].iloc[i]) > 0:
            flag = True
            
    if flag == False:
        return None
    
    start = 0
    stop = 8

    #//*----Donut Pie Chart---*//
    font_path = join(cwd,'assets','fonts','Prata')
    font_files = font_manager.findSystemFonts(fontpaths=font_path)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)

    # set font
    labels = df_pie["particular"]
    sizes = df_pie['percentage']
    
    aut_size = list(str(x) for x in sizes)
    h_size = df_pie['percentage'].tolist()

    free_colors = ['#A792FF','#82DBC6','#90BEF8','#FFC27E','#FFD976']
    w = 1.08
    wed_height = []
    for i in h_size:
        if h_size == 0:
            wed_height.append(1)
        elif w == 1:
            w = 1.08
            wed_height.append(w)
        elif w ==1.08:
            w = 1
            wed_height.append(w)
        else :
            w = 1
            wed_height.append(w)

    colors = free_colors[0:len(df_pie)]
    df_pie['colors'] = colors
    fig, ax0 = plt.subplots(figsize=(6.8, 6.8))
    font = {'family': 'prata','color':  'black','weight': 'normal','size': 24,}
    wedges, plt_labels, junk = ax0.pie(sizes, colors = colors,startangle=90,wedgeprops = {"edgecolor" : "black",'linewidth': 2.5,'antialiased': True,'width':1},autopct=autopct_generator(9),textprops=font)
    # wed_height = [1.08,1,1.08,1,1.08,1,1.08,1]
    plt.rcParams['font.family'] = 'prata'
    
    for i in range(len(wedges)):
        wedges[i].set_radius(wed_height[i])

    centre_circle = plt.Circle((0,0),0.2,color='black')
    fig = plt.gcf()
    fig.patch.set_facecolor('black')
    fig.gca().add_artist(centre_circle)
    
    # plt.show()
    plt.tight_layout()
    plt.savefig('asset_chart.png',dpi=450)
    #//*---------------------------------**----------------------*//
    
    #Page Creation
    def add_asset_page(pdf):
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(0, 0, px2MM(964), px2MM(1080),'F')
        
        #//*---Adding Pie Chart to Page---*//
        pdf.image('asset_chart.png',px2MM(80), px2MM(195), px2MM(600), px2MM(600))
        
        #//*----Legends---*//
        circle_y = 794
        common_gap = 42
        text_y = 788
 
        for i in range(0,len(df_pie)):
                
            pdf.set_fill_color(*hex2RGB(df_pie['colors'].iloc[i]))
            pdf.circle(x=px2MM(227),y=px2MM(circle_y),r=px2MM(20),style='F')
            
            pdf.set_xy(px2MM(267),px2MM(text_y)) 
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#ffffff'))
            pdf.multi_cell(px2MM(250), px2MM(32),str(df_pie["particular"].iloc[i])+':',align='L')
            
            pdf.set_xy(px2MM(517),px2MM(text_y))
            pdf.cell(px2MM(80), px2MM(32),"{:.0f}".format(int(round(float(df_pie['percentage'].iloc[i]))))+'%',align='R')
            
            #//*---Adding double gap to the next value if the current test exceeds the width
            if len(df_pie["particular"].iloc[i])>24:
                circle_y+=common_gap
                text_y+=common_gap
                
            circle_y+=common_gap
            text_y+=common_gap
        
        #//*----Assets----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#ffffff'))
        pdf.multi_cell(px2MM(600), px2MM(84),'Assets',align='L')
        
        #//*---Assets Date----*//

        Day=dt.datetime.now().strftime("%d")
        month=dt.datetime.now().strftime("%b")
        year=dt.datetime.now().strftime("%Y")

        if 4 <= int(Day) <= 20 or 24 <= int(Day) <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][int(Day) % 10 - 1]
            
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#ffffff'))
        pdf.set_xy(px2MM(315),px2MM(110)) 
        pdf.cell(px2MM(400), px2MM(32),f'As on {str(Day)}{suffix} {str(month)} {str(year)}',align='L')

        #//*---Existing Assets ----*//
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(1424), px2MM(81), px2MM(376), px2MM(82),'F')
        
        pdf.set_xy(px2MM(1444),px2MM(101)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#ffffff'))
        ext_value = '₹ '+str(format_cash2(float(json_data['assets']['total']['market_value'])))
        pdf.cell(px2MM(336), px2MM(42),f'Existing Assets: {ext_value}',align='C')
        
        #//*-----Assets Table Heading Column---*//
        #//*----Col1 Assets
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        pdf.rect(px2MM(690), px2MM(317), px2MM(297), px2MM(72),'FD')
        
        pdf.set_xy(px2MM(710),px2MM(337)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(257), px2MM(32),'Asset',align='L')
        
        #//*----Col2 %
    
        pdf.rect(px2MM(987), px2MM(317), px2MM(100), px2MM(72),'FD')
        pdf.set_xy(px2MM(1007),px2MM(337)) 
        pdf.cell(px2MM(60), px2MM(32),'%',align='C')
        
        #//*----Col3 Assets Class
        pdf.rect(px2MM(1087), px2MM(317), px2MM(293), px2MM(72),'FD')
        
        pdf.set_xy(px2MM(1107),px2MM(337)) 
        pdf.cell(px2MM(253), px2MM(32),'Asset Class',align='L')
        
        #//*----Col4 Market Value
        pdf.rect(px2MM(1380), px2MM(317), px2MM(177), px2MM(72),'FD')
        
        pdf.set_xy(px2MM(1400),px2MM(337)) 
        pdf.cell(px2MM(137), px2MM(32),'Market Value',align='R')
        
        #//*----Col5 Monthly Investments
        pdf.rect(px2MM(1557), px2MM(317), px2MM(243), px2MM(72),'FD')
        
        pdf.set_xy(px2MM(1577),px2MM(337)) 
        pdf.cell(px2MM(203), px2MM(32),'Monthly Investment',align='R')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
        
        return 389,'#F3F6F9'
    
    def get_rect_h(pdf,df_table,y):
        state_y = y+15
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(710),px2MM(state_y)) 
        pdf.multi_cell(px2MM(257), px2MM(32),str(df_table['asset']),align='L')
        
        let_y = mm2PX(pdf.get_y())
        
        rect_h = let_y-state_y+30
        state_lh = let_y-state_y
        
        return rect_h,state_lh
        
        
    y,rect_color = add_asset_page(pdf)
    
    for i in range(len(df_table)):
        
        rect_h,state_lh = get_rect_h(pdf,df_table[i],y)
        if 1080-y <= 138+rect_h:
            y,rect_color = add_asset_page(pdf)
        elif i == len(df_table)-2 and 1080-y < 200+rect_h:
            y,rect_color = add_asset_page(pdf)
        
        if i!= len(df_table)-1:
            pdf.set_fill_color(*hex2RGB(rect_color))      
            pdf.set_draw_color(*hex2RGB('#E9EAEE'))
            pdf.rect(px2MM(690), px2MM(y), px2MM(297), px2MM(rect_h),'FD')
            pdf.rect(px2MM(987), px2MM(y), px2MM(100), px2MM(rect_h),'FD')
            pdf.rect(px2MM(1087), px2MM(y), px2MM(293), px2MM(rect_h),'FD')
            pdf.rect(px2MM(1380), px2MM(y), px2MM(177), px2MM(rect_h),'FD')
            pdf.rect(px2MM(1557), px2MM(y), px2MM(243), px2MM(rect_h),'FD')
            state_y = y+15
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
        else:
            pdf.set_fill_color(*hex2RGB('#B9BABE'))      
            pdf.rect(px2MM(690), px2MM(y), px2MM(1110), px2MM(1),'F')
            
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))      
            pdf.rect(px2MM(690), px2MM(y+1), px2MM(1110), px2MM(52),'F')
            state_y = y+11
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            
        
        
        pdf.set_xy(px2MM(710),px2MM(state_y)) 
        pdf.multi_cell(px2MM(257), px2MM(32),str(df_table[i]['asset']),align='L')
        y = mm2PX(pdf.get_y())+15
        #//*----Col2 %
        pdf.set_xy(px2MM(1007),px2MM(state_y)) 
        if df_table[i]['percentage'] != '':
            pdf.cell(px2MM(60), px2MM(state_lh),"{:.0f}".format(float(df_table[i]['percentage']))+'%',align='C')
        
        #//*----Col3 Assets Class
        pdf.set_xy(px2MM(1107),px2MM(state_y)) 
        pdf.cell(px2MM(253), px2MM(state_lh),str((df_table[i]['asset_class'])),align='L')
        
        #//*----Col4 Market Value
        pdf.set_xy(px2MM(1400),px2MM(state_y)) 
        if df_table[i]['market_value'] == '' and i != len(df_table)-1:
            pdf.cell(px2MM(137), px2MM(state_lh),'-',align='R')
        else:
            pdf.cell(px2MM(137), px2MM(state_lh),'₹ '+str(format_cash2(float(df_table[i]['market_value']))),align='R')
            
        #//*----Col5 Monthly Investments
        pdf.set_xy(px2MM(1577),px2MM(state_y))
        if df_table[i]['monthly_investments'] == '' or int(float(df_table[i]['monthly_investments'])) == 0:
            pdf.cell(px2MM(203), px2MM(state_lh),'₹ 0.0K',align='R')
        else:
            pdf.cell(px2MM(203), px2MM(state_lh),'₹ '+str(format_cash2(float(df_table[i]['monthly_investments']))),align='R')
            
        
        if rect_color=='#F3F6F9':
            rect_color='#FFFFFF'
        else:
            rect_color='#F3F6F9'
                  
        
#//**--------------Liability Pie Chart----------------------*/
def liabilities_chart(pdf,json_data,c_MoneyS,money_signData):
    try:
        df_table = json_data["liabilities"]['table']
        df_pie = pd.DataFrame.from_dict(json_data["liabilities"]['pie'])
    except Exception as e:
        return None 
    
    if df_pie.empty:
        return None
    flag = False 
    for i in range(len(df_pie['percentage'])):
        if int(float(df_pie['percentage'].iloc[i])*100) > 0:
            flag = True

                    
    if flag == False:
        return None
    
    emi_list = list(x['emi'] for x in df_table)
        
    tab_total = {}
    tab_total['liability']='Total'
    tab_total['liability_category']=''
    tab_total['outstanding_amount']=json_data["liabilities"]['total']
    tab_total['emi']=sum([eval(i) for i in emi_list])
    tab_total['pending_months']=''
    tab_total['interest_rate']=''
    tab_total['account_age_in_months']=''
    
    df_table.append(tab_total)
    
    #//*----Donut Pie Chart---*//
    font_path = join(cwd,'assets','fonts','Prata')
    font_files = font_manager.findSystemFonts(fontpaths=font_path)
    for font_file in font_files:
        font_manager.fontManager.addfont(font_file)
    # #//*----Donut Pie Chart---*//
    free_colors = ['#FFD976','#ffffff','#A792FF','#82DBC6','#90BEF8','#FFC27E','#FFD976','#3D7DD0']
    colors = free_colors[0:len(df_pie)]
    
    df_pie['colors'] = colors
    df_pie_chart = df_pie

    df_pie_chart = df_pie_chart.replace(0,np.nan, regex=True)
    df_pie_chart = df_pie_chart.dropna()
    
    labels = df_pie_chart['particular']
    sizes = df_pie_chart['percentage']

    fig, ax0 = plt.subplots(figsize=(6.8, 6.8))
    wed_height = [1,0.9,1,1.08,1,1.08,1,1.08,1]
    font = {'family': 'prata','color':  'black','weight': 'normal','size': 24,}
    wedges, plt_labels, junk = ax0.pie(sizes, colors = df_pie_chart['colors'],startangle=90,wedgeprops = {"edgecolor" : "black",'linewidth': 2,'antialiased': True},autopct=autopct_generator(9),textprops=font)
    
    for i in range(len(wedges)):
        wedges[i].set_radius(wed_height[i])
        
    centre_circle = plt.Circle((0,0),0.2,color='black')
    fig = plt.gcf()
    fig.patch.set_facecolor('black')
    fig.gca().add_artist(centre_circle)
    plt.tight_layout()
    plt.savefig('liabilities_chart.png',dpi=650)
    
    #Page Creation
    def add_liability_page(pdf):
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(0, 0, px2MM(964), px2MM(1080),'F')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
        
        #//*----Adding PIE image
        pdf.image('liabilities_chart.png',px2MM(80), px2MM(300), px2MM(600), px2MM(600))
            
        #//*---Description----*//
        pdf.set_xy(px2MM(120),px2MM(184)) 
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#FFFFFF'))
        desc = """Good liabilities generally are productive, with favourable rates and terms, while bad ones are for non-essential expenses, have high rates, or unfavourable terms. Prioritising the repayment of bad liabilities is wise, as they cost more in the long run."""
        pdf.multi_cell(px2MM(812), px2MM(32),desc,align='L')
        
        #//*----Legends---*//
        circle_y = 899
        common_gap = 42
        text_y = 893

        labels = df_pie['particular']
        colors = free_colors[0:len(labels)]
        sizes = df_pie['percentage']
        for i in range(0,len(labels)):
            pdf.set_fill_color(*hex2RGB(df_pie['colors'].iloc[i]))
            pdf.circle(x=px2MM(213),y=px2MM(circle_y),r=px2MM(20),style='F')
            
            pdf.set_xy(px2MM(253),px2MM(text_y)) 
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#ffffff'))
            pdf.cell(px2MM(200), px2MM(32),labels[i]+':',align='L')
            
            pdf.set_xy(px2MM(484),px2MM(text_y))
            pdf.cell(px2MM(56), px2MM(32),str(int(round(sizes[i])))+'%',align='R')
                
            circle_y+=common_gap
            text_y+=common_gap
            
        #//*----Snapshot of Holding - Liability----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#ffffff'))
        pdf.cell(px2MM(224), px2MM(84),'Liabilities',align='L')

        Day=dt.datetime.now().strftime("%d")
        month=dt.datetime.now().strftime("%b")
        year=dt.datetime.now().strftime("%Y")

        if 4 <= int(Day) <= 20 or 24 <= int(Day) <= 30:
            suffix = "th"
        else:
            suffix = ["st", "nd", "rd"][int(Day) % 10 - 1]
            
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#ffffff'))
        pdf.set_xy(px2MM(394),px2MM(110)) 
        # pdf.cell(px2MM(100), px2MM(32),f'As on {str(Day)}',align='R')
        pdf.cell(px2MM(500), px2MM(32),f'As on {str(Day)}{suffix} {str(month)} {str(year)}',align='L')
        
        #//*---Existing Liabilities ----*//
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(1385), px2MM(81), px2MM(415), px2MM(82),'F')
        
        pdf.set_xy(px2MM(1405),px2MM(101)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#ffffff'))
        pdf.cell(px2MM(375), px2MM(42),'Existing Liabilities:'+' ₹ '+str(format_cash2(float(json_data['liabilities']['total']))),align='C')
        
        #//*-----Liability Table---*//
        #//*----Col1 Liabilities
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        pdf.rect(px2MM(690), px2MM(483), px2MM(230), px2MM(104),'F')
        
        pdf.set_xy(px2MM(710),px2MM(503)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(190), px2MM(64),'Liabilities',align='L')
        
        #//*----Col2Category
    
        pdf.rect(px2MM(920), px2MM(483), px2MM(140), px2MM(104),'FD')
        pdf.set_xy(px2MM(940),px2MM(503)) 
        pdf.cell(px2MM(100), px2MM(64),'Category',align='C')
        
        #//*----Col3 Account Age in Months
        pdf.rect(px2MM(1060), px2MM(483), px2MM(170), px2MM(104),'FD')
        pdf.set_xy(px2MM(1070),px2MM(503)) 
        pdf.multi_cell(px2MM(140), px2MM(32),'Account Age in Months',align='R')
        
        #//*----Pending Months
        pdf.rect(px2MM(1230), px2MM(483), px2MM(130), px2MM(104),'FD')
        pdf.set_xy(px2MM(1240),px2MM(503)) 
        pdf.multi_cell(px2MM(100), px2MM(32),'Pending Months',align='R')
        
        #//*----Outstanding Amount
        pdf.rect(px2MM(1360), px2MM(483), px2MM(170), px2MM(104),'FD')
        pdf.set_xy(px2MM(1370),px2MM(503)) 
        pdf.multi_cell(px2MM(140), px2MM(32),'Outstanding Amount',align='R')
        
        #//*----EMI
        pdf.rect(px2MM(1530), px2MM(483), px2MM(140), px2MM(104),'FD')
        pdf.set_xy(px2MM(1550),px2MM(503)) 
        pdf.multi_cell(px2MM(100), px2MM(64),'EMI',align='R')
        
        #//*----Interest Rate
        pdf.rect(px2MM(1670), px2MM(483), px2MM(130), px2MM(104),'FD')
        pdf.set_xy(px2MM(1690),px2MM(503)) 
        pdf.multi_cell(px2MM(90), px2MM(32),'Interest Rate',align='R')
        
        
        return 587,'#F3F6F9'
    
    def get_rect_h(pdf,df_table,y):
        state_y = y
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(710),px2MM(state_y)) 
        pdf.multi_cell(px2MM(190), px2MM(32),str(df_table['liability']),align='L')
        
        let_y = mm2PX(pdf.get_y())
        
        rect_h = let_y-y+30
        state_lh = rect_h
        
        return rect_h,state_lh
        
    y,rect_color = add_liability_page(pdf)
    
    for i in range(len(df_table)):
        rect_h,state_lh = get_rect_h(pdf,df_table[i],y)
        
        if 1080-y <= 138+rect_h:
            y,rect_color = add_liability_page(pdf)
        elif i == len(df_table)-2 and 1080-y < 200+rect_h:
            y,rect_color = add_liability_page(pdf)
        
        if i!= len(df_table)-1:
            pdf.set_fill_color(*hex2RGB(rect_color))      
            pdf.set_draw_color(*hex2RGB('#E9EAEE'))
            pdf.rect(px2MM(690), px2MM(y), px2MM(230), px2MM(rect_h),'FD')
            pdf.rect(px2MM(920), px2MM(y), px2MM(140), px2MM(rect_h),'FD')
            pdf.rect(px2MM(1060), px2MM(y), px2MM(170), px2MM(rect_h),'FD')
            pdf.rect(px2MM(1230), px2MM(y), px2MM(130), px2MM(rect_h),'FD')
            pdf.rect(px2MM(1360), px2MM(y), px2MM(170), px2MM(rect_h),'FD')
            pdf.rect(px2MM(1530), px2MM(y), px2MM(140), px2MM(rect_h),'FD')
            pdf.rect(px2MM(1670), px2MM(y), px2MM(130), px2MM(rect_h),'FD')
            
            state_y = y+15
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
        else:
            pdf.set_fill_color(*hex2RGB('#B9BABE'))      
            pdf.rect(px2MM(690), px2MM(y), px2MM(1110), px2MM(1),'F')
            
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))      
            pdf.rect(px2MM(690), px2MM(y+1), px2MM(1110), px2MM(52),'F')
            state_y = y+11
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            
        #//*----Col1---*//
        pdf.set_xy(px2MM(710),px2MM(state_y)) 
        pdf.multi_cell(px2MM(190), px2MM(32),str(df_table[i]['liability']),align='L')
        # y = mm2PX(pdf.get_y())+15
        
        #//*----Col2---*//
        pdf.set_xy(px2MM(940),px2MM(y)) 
        pdf.cell(px2MM(100), px2MM(state_lh),str(df_table[i]['liability_category']),align='C')
        
        #//*----Col3---*//
        
        pdf.set_xy(px2MM(1080),px2MM(y)) 
        if df_table[i]['account_age_in_months'] =="" or df_table[i]['account_age_in_months'] ==0:
            pdf.cell(px2MM(130), px2MM(state_lh),' ',align='R')
        else:
            pdf.cell(px2MM(130), px2MM(state_lh),str(df_table[i]['account_age_in_months']),align='R')
        
        #//*----Col4---*//
        
        pdf.set_xy(px2MM(1250),px2MM(y)) 
        if df_table[i]['pending_months'] == '' or df_table[i]['pending_months']==0:
            pdf.cell(px2MM(90), px2MM(state_lh),' ',align='R')
        else:
            pdf.cell(px2MM(90), px2MM(state_lh),str(int(df_table[i]['pending_months'])),align='R')
            
        #//*----Col5---*//
        
        pdf.set_xy(px2MM(1380),px2MM(y))

        if int(float(df_table[i]['outstanding_amount'])) == 0 or df_table[i]['outstanding_amount']=='': 
            pdf.cell(px2MM(130), px2MM(state_lh),'₹ 0.0L ',align='R')
        else:
            pdf.cell(px2MM(130),px2MM(state_lh), '₹ '+str(format_cash2(round(float(df_table[i]['outstanding_amount']),1))),align='R')

        
        #//*----Col6---*//
        
        pdf.set_xy(px2MM(1550),px2MM(y)) 
        if df_table[i]['emi'] == 0 or df_table[i]['emi'] =='':
            pdf.cell(px2MM(100), px2MM(state_lh),' ',align='R')
        else:
            pdf.cell(px2MM(100), px2MM(state_lh),'₹ '+str(format_cash2(round(float(df_table[i]['emi']),1))),align='R')
            
        #//*----Col7---*//
        
        pdf.set_xy(px2MM(1690),px2MM(y)) 
        if df_table[i]['interest_rate'] == 0 or df_table[i]['interest_rate'] =='':
            pdf.cell(px2MM(100), px2MM(state_lh),' ',align='R')
        else:
            pdf.cell(px2MM(100), px2MM(state_lh),str(round(df_table[i]['interest_rate'],1))+'%',align='R')    

            
        # y = mm2PX(pdf.get_y())+47
        y +=rect_h
        if rect_color=='#F3F6F9':
            rect_color='#FFFFFF'
        else:
            rect_color='#F3F6F9'
            
#//*---------------------------------------------------------------     
        
def autopct_generator(limit):
    def inner_autopct(pct):
        return ('%.0f' % pct)+'%' if pct > limit else ''
    return inner_autopct  
        
#//*-------Net Worth Projection-----*//    
def net_worth_projection(pdf,json_data,c_MoneyS,money_signData):
    try:
        df = pd.DataFrame.from_dict(json_data["networth"]['networth_projection']['table'])
        if df.empty:
            return None 
    except Exception as e:
        return None   
    ini = 0
    stps = 28
    ini_2 = ini
    last_val = 28
    for tab in range(ini,len(df),stps):
        #//*---Page setup----*//
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')

        pdf.image(join(cwd,'assets','images','backgrounds','doubleLine.png'),px2MM(1449),px2MM(0),px2MM(471),px2MM(1080))
        
        #//*----Net Worth Projection----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(535), px2MM(84),'Net Worth Projection',align='L')
        
        #//*-----Table White rect
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))

        year_rect_x = 886
        year_state_x = 906
        val_rect_y=val_rect_y2 = 289
        val_state_y=val_state_y2 = 299
        
        current_rect_x = 1025
        current_state_x = 1045
        
        project_rect_x = 1164
        project_state_x = 1184

        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        pdf.rect(px2MM(846), px2MM(204), px2MM(954), px2MM(755),'FD')
        #//*-----Table Headings---*//
        
        #//*---Table 1
        #//*--Col 1
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_fill_color(*hex2RGB('#F3F6F9'))
        pdf.set_line_width(px2MM(0.2))
        pdf.rect(px2MM(886), px2MM(244), px2MM(139), px2MM(45),'FD')
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        
        pdf.set_xy(px2MM(906),px2MM(254))
        pdf.cell(px2MM(99), px2MM(25),'Year',align='C')
        
        #//*--Col 2
        pdf.rect(px2MM(1025), px2MM(244), px2MM(139), px2MM(45),'FD')
        pdf.set_xy(px2MM(1045),px2MM(254))
        pdf.cell(px2MM(99), px2MM(25),'CNWT (Cr)',align='C')
        
        #//*--Col 3

        pdf.rect(px2MM(1164), px2MM(244), px2MM(139), px2MM(45),'FD')
        pdf.set_xy(px2MM(1184),px2MM(254))
        pdf.cell(px2MM(99), px2MM(25),'NWTEP (Cr)',align='C')
        
        #//*---Table 2
        if len(df)-ini_2 > 14:
            #//*--Col 1
            pdf.set_fill_color(*hex2RGB('#F3F6F9'))
            pdf.set_line_width(px2MM(0.2))
            pdf.rect(px2MM(1343), px2MM(244), px2MM(139), px2MM(45),'FD')
            pdf.set_font('LeagueSpartan-Medium', size=px2pts(18))
            
            pdf.set_xy(px2MM(1363),px2MM(254))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.cell(px2MM(99), px2MM(25),'Year',align='C')
            
            #//*--Col 2
            pdf.rect(px2MM(1482), px2MM(244), px2MM(139), px2MM(45),'FD')
            pdf.set_xy(px2MM(1502),px2MM(254))
            pdf.cell(px2MM(99), px2MM(25),'CNWT (Cr)',align='C')
            
            #//*--Col 3
            pdf.rect(px2MM(1621), px2MM(244), px2MM(139), px2MM(45),'FD')
            pdf.set_xy(px2MM(1641),px2MM(254))
            pdf.cell(px2MM(99), px2MM(25),'NWTEP (Cr)',align='C')
            
        
        #//**--Table x and y settings---**//
        common_gap = 45
        
        #//*---Table value---*//
        
        for i in range(ini_2,last_val):
            try:
        
            #//*----Col 1
                if i%2==0:
                    pdf.set_fill_color(*hex2RGB('#ffffff'))
                else:
                    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
                pdf.set_draw_color(*hex2RGB('#E9EAEE'))
                pdf.set_line_width(px2MM(0.2))
                pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
                pdf.set_xy(px2MM(year_state_x),px2MM(val_state_y))
                pdf.set_text_color(*hex2RGB('#000000'))
                if (df['year'][i]):
                    pdf.rect(px2MM(year_rect_x), px2MM(val_rect_y), px2MM(139), px2MM(45),'FD') 
                pdf.cell(px2MM(99), px2MM(25),"{0:.0f}".format(df['year'][i]),align='C')
                
                #//*---Col 2
                pdf.rect(px2MM(current_rect_x), px2MM(val_rect_y), px2MM(139), px2MM(45),'FD') 
                pdf.set_xy(px2MM(current_state_x),px2MM(val_state_y))
                pdf.cell(px2MM(99), px2MM(25),"{0:.1f}".format(df['cnwt'][i]),align='C')
                
                #//*---Col 3
                pdf.rect(px2MM(project_rect_x), px2MM(val_rect_y), px2MM(139), px2MM(45),'FD') 
                pdf.set_xy(px2MM(project_state_x),px2MM(val_state_y))
                pdf.cell(px2MM(99), px2MM(25),"{0:.1f}".format(df['nwtet'][i]),align='C')
                
                val_rect_y+=common_gap
                val_state_y+=common_gap
                
                if i==ini_2+27:

                    ini_2 += 28
                    last_val+=28
  
                #//*---Reiniatilizing x and y axis for 2nd side table
                if i == ini_2+13:
                    year_rect_x = 1343
                    year_state_x = 1363
                    current_rect_x = 1482
                    current_state_x = 1502
                    project_rect_x = 1621
                    project_state_x = 1641
                    
                    val_rect_y = val_rect_y2
                    val_state_y= val_state_y2

            except Exception as e:
                pass
                
        if tab ==0:
            #//*------Line Graph---*//
            font_dir = [join(cwd, 'assets','fonts','League_Spartan','static')]
            font_files2 = font_manager.findSystemFonts(fontpaths=font_dir)
            for files in font_files2:
                font_manager.fontManager.addfont(files)

            fig,ax = plt.subplots()
            min_year = df['year'].min()
            max_year = df['year'].max()
            
            a = df['year'].astype(int)
            b = df['nwtet'].astype(float)
            c = df['cnwt'].astype(float)  
 
            #//*----------case 1-------------------*//
            pp = math.ceil(len(df['year'])/8)
            
            color_b = '#FF7051'
            color_a =  '#43D195'
            
            ax = sns.lineplot(x = a,y=b)
            plt.plot(a,b,color=color_a,ms = 3 ,lw = 1)
            plt.plot(a,c,color=color_b,ms = 3 ,lw = 1)
            # plt.plot(min(a),min(b),color='black',ms = 5)
            ax.yaxis.set_major_formatter(tick.FuncFormatter(y_fmt))
    
            plt.xlabel('')
            plt.ylabel('')

            min_year = df['year'].min()
            max_year = df['year'].max()
 
            min_ideal = min(b)
            max_ideal = max(b)
            
            if max(c)>max(b):
                max_ideal = max(c)
            else:
                max_ideal = max(b)
                
            if min(c) <= min(b):
                min_ideal = min(c)
            else:
                min_ideal = min(b)
                
            z = max_ideal/3
            max_ideal = max_ideal +z
                
            plt.xlim(min(a)-1,max(a))
            plt.ylim(int(min_ideal)-1,max_ideal)
            # plt.ylim(min_ideal,max_ideal)
            
  
            #//*----setting Shade of NWTEP as green and CNWT as red statically---*//  
                  
            max_b = max(b)
            red_lp = np.linspace(max_b,min_ideal-1,100)
            for i in red_lp:
                plt.fill_between(a,i,b,color= '#FFD4CB',alpha=0.03) 
            
            NbData = len(a)  
            max_a = max(a)    
            red_MaxBL = [[MaxBL] * NbData for MaxBL in range(max_a)]
            Max = [np.asarray(red_MaxBL[x]) for x in range(max_a)]
            
            for x in range (math.ceil(max(b)),max_a):
                plt.fill_between(a,Max[x],b, facecolor='white', alpha=1) 
                
            # plt.fill_between(a,c,b,color= '#D4FFED',alpha=.9,interpolate=True)
            plt.fill_between(a,c,b,where=b>c,color= '#D4FFED',alpha=.9,interpolate=True)
            plt.fill_between(a,c,b,where=b<c,color= '#FFD4CB',alpha=.6,interpolate=True)
   
                    
                

            # #//*----Color shading case 3
            # if max(c)>max(b):
            #     ln_color_b = '#FFD4CB' #red
            #     ln_color_a =  '#D4FFED' #green

            #     plt.fill_between(a,c,color=ln_color_a,alpha=1) 
            #     plt.fill_between(a,c,b,color=ln_color_b,alpha=0.7) 
            # else:
            #     ln_color_a =  '#D4FFED' #green
            #     ln_color_b = '#FFD4CB' #red
                
            #     plt.fill_between(a,b,color=ln_color_b,alpha=1) 
            #     plt.fill_between(a,b,c,color=ln_color_a,alpha=0.7)
            
            # color_b = '#D4FFED' #green
            # color_a =  '#FFD4CB'  #red
    

            # plt.fill_between(a,b,color=color_b,alpha=1) 
            # plt.fill_between(a,c,color=color_a,alpha=0.7)  
            
            #//*----Circle marker at starting
 
            plt.plot(min(a),min(b), 'o',markerfacecolor='none', ms=10, markeredgecolor='black')  
            plt.plot(min(a),min(b),linewidth=4, marker ='.',color='#000000')   
                  
            # # //*-------Case2 of Ticks------*//

            pp = math.ceil(len(a)/8)
            rem = pp%8
            arg = np.arange(start=df['year'].min(), stop=df['year'].max(), step=pp)
            plt.xticks(np.arange(min(a)+1, max(a),pp))
            
            if len(a)>0 and len(a)<=8:
                plt.xticks(np.arange(min(a), max(a), 1))
            elif len(a)>8 and len(a)<=16:
                plt.xticks(np.arange(min(a), max(a), 2))
            elif len(a)>16 and len(a)<=24:
                plt.xticks(np.arange(min(a), max(a), 3))
            elif len(a)>24 and len(a)<=32:
                plt.xticks(np.arange(min(a), max(a)+1, 4))
            elif len(a)>32 and len(a)<=40:
                plt.xticks(np.arange(min(a), max(a)+1,5))
            else:
                plt.xticks(np.arange(min(a), max(a)+1,math.ceil(len(a)/8)))
                

            #//*---X tick Rotation
            plt.yticks(fontname = "Arial")  
            plt.xticks(fontname = "Arial")  
            ax.tick_params(axis='x', labelrotation = 00)
            ax.tick_params(axis='both',labelsize=10,colors='#65676D')
            ax.tick_params(axis='y',labelsize=10)
            ax.grid(color='#DCDCDC', linestyle='-', linewidth=0.15)
            ax.yaxis.grid(True) 
            ax.xaxis.grid(True)
            ax.spines[['right', 'top','left','bottom']].set_visible(False)
            plt.tick_params(left = False,bottom = False)
        
            plt.savefig('acutal_networth_chart.png',dpi=250)
        
        #//*----Legend and Graph plotting---*//
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        pdf.rect(px2MM(120),px2MM(204),px2MM(686),px2MM(762),'FD')    
        pdf.image('acutal_networth_chart.png',px2MM(160),px2MM(206),px2MM(606),px2MM(400))

        pdf.set_fill_color(*hex2RGB(color_b))
        pdf.rect(px2MM(169),px2MM(629),px2MM(12),px2MM(12),'F')   
        
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
        pdf.set_xy(px2MM(196),px2MM(619))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(559), px2MM(32),'Current Net Worth Trajectory (CNWT)',align='L')
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_xy(px2MM(196),px2MM(656))
        pdf.set_text_color(*hex2RGB('#898B90'))
        # max_curr = "{0:.2f}".format(float(df['cnwt'].max()))
        max_curr = str(format_cash2(float(json_data['networth']['networth_projection']['retirement_cnwt'])))
        # today = datetime.now()
        # mnth = today.strftime("%B")
        mnth = json_data['networth']['networth_projection']['retirement_month_year']
        # data1 = mnth+' '+str(int(max_year))+' | ₹'+max_curr+' Cr'
        data1 = mnth+' | ₹ '+max_curr
        pdf.cell(px2MM(559), px2MM(32),data1,align='L')
        
        
        #//*------
        pdf.set_fill_color(*hex2RGB(color_a))
        pdf.rect(px2MM(169),px2MM(758),px2MM(12),px2MM(12),'F')   
        
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
        pdf.set_xy(px2MM(196),px2MM(718))
        pdf.set_text_color(*hex2RGB('#000000'))
        # pdf.cell(px2MM(295), px2MM(32),str(df['Current net worth Trajectory'].max()),align='C') 
        pdf.cell(px2MM(559), px2MM(32),'Net worth Trajectory With Effective Planning (NWTEP)',align='L')
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_xy(px2MM(196),px2MM(755))
        pdf.set_text_color(*hex2RGB('#898B90'))
        # pdf.cell(px2MM(295), px2MM(32),str(df['Current net worth Trajectory'].max()),align='C')
        max_net_worth = str(format_cash2(float(json_data['networth']['networth_projection']['retirement_nwtet']))) 

        data2 = mnth+' | ₹ '+max_net_worth
        pdf.cell(px2MM(559), px2MM(32),data2,align='L')
        
        if float(json_data['networth']['networth_projection']['retirement_cnwt']) > float(json_data['networth']['networth_projection']['retirement_nwtet']):
            pdf.set_fill_color(*hex2RGB("#B0B3B7"))
            pdf.rect(px2MM(170),px2MM(807),px2MM(586),px2MM(1),'F') 

            pdf.set_font('LeagueSpartan-Bold', size=px2pts(14))
            pdf.set_xy(px2MM(194),px2MM(831))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.cell(px2MM(538), px2MM(14),'Note:',align='L')

            pdf.set_font('LeagueSpartan-Regular', size=px2pts(16))
            pdf.set_xy(px2MM(196),px2MM(857))
            pdf.set_text_color(*hex2RGB('#65676D'))
            pdf.multi_cell(px2MM(559), px2MM(23),'''Higher current net worth projections may result from increased exposure to high-risk high-reward investments. Effective planning prioritizes financial well-being and peace of mind over volatile growth.''',align='L')

        desc_text_1 = '''CNWT: Assumes that you maintain your current financial habits until retirement. NWTEP: Assumes that your finances are aligned with your personality by following the ideal guidance provided on the 'Your Financial Analysis' pages. '''
        pdf.set_xy(px2MM(100), px2MM(978))
        pdf.set_font('LeagueSpartan-Light', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(1700),px2MM(25),desc_text_1,border=0,align="C")

        desc_text_2 = '''Disclaimer: The net worth projections are based on our internal analysis and may change over time.'''
        pdf.set_xy(px2MM(120), px2MM(1028))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(1680),px2MM(32),desc_text_2,border=0,align="C")

        
        
        ini = 29
        stps = 29 
        
def y_fmt(x, y):
    return f'₹ {int(x)}Cr'.format(x)
#//*---Structure for Term and Health Insurance---*// 
def term_health_features(pdf,df,pg_name):
    
    def add_base_page(pdf): 
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

        #//*----Featured List of Financial Products----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(877), px2MM(84),'Financial Products Featured List',align='L')
        
        #//*---Top Black box
        pdf.set_fill_color(*hex2RGB('#313236'))
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#ffffff'))
        
        if pg_name == 'Term Insurance Plans':
        
            pdf.rect(px2MM(126), px2MM(204), px2MM(242), px2MM(42),'F')
            pdf.set_xy(px2MM(141),px2MM(209)) 
            pdf.cell(px2MM(212), px2MM(32),"Term Insurance Plans",align='L')
        elif  pg_name == 'Health Insurance Plans':
            pdf.rect(px2MM(126), px2MM(204), px2MM(259), px2MM(42),'F')
            pdf.set_xy(px2MM(141),px2MM(209)) 
            pdf.cell(px2MM(229), px2MM(32),"Health Insurance Plans",align='L')
        
            
        # //*---Col 1
        
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.rect(px2MM(126), px2MM(246), px2MM(558), px2MM(72),'FD')
        
        pdf.set_xy(px2MM(146),px2MM(266)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(200), px2MM(32),'Plan Details',align='L')
        
        #//*---Col 2
        pdf.rect(px2MM(684), px2MM(246), px2MM(558), px2MM(72),'FD')
        pdf.set_xy(px2MM(704),px2MM(266)) 
        pdf.multi_cell(px2MM(230), px2MM(32),'Strength',align='L')
    
        #//*---Col 3
        pdf.rect(px2MM(1242), px2MM(246), px2MM(558), px2MM(72),'FD')
        pdf.set_xy(px2MM(1262),px2MM(266)) 
        pdf.multi_cell(px2MM(524), px2MM(32),'Weakness',align='L')
    
    #//*---Desclaimer Function---*//
    def add_disclaimer(pdf):
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(px2MM(0), px2MM(1006), px2MM(1920), px2MM(40),'F')
        desclaimer = "Disclaimer: The above featured list is based on 1 Finance's proprietary research."
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_xy(px2MM(120),px2MM(1008))      
        pdf.multi_cell(px2MM(1680), px2MM(32),desclaimer,align='C')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
        global fin_feat_product_list
        
        if fin_feat_product_list == 0:
            fin_feat_product_list = pdf.page_no()
        
    #//*---Function to check height of rectangle
    def get_rect_h(rem,strength,weakness):
        pdf.set_text_color(*hex2RGB('#FCF8ED'))
        pdf.set_text_color(*hex2RGB('#000000'))
        rem_pro = 0
        rem_con = 0
        
        s_text_h = rem
        w_text_h = rem
        
        for j in range(len(strength)):
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_xy(px2MM(744),px2MM(s_text_h)) 
            pdf.multi_cell(px2MM(478), px2MM(32),strength[j],align='L')
            
            s_text_h = mm2PX(pdf.get_y()) 
        
        rem_pro = mm2PX(pdf.get_y())
        
        for j in range(len(weakness)):
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_xy(px2MM(1302),px2MM(w_text_h)) 
            pdf.multi_cell(px2MM(478), px2MM(32),weakness[j],align='L')
            w_text_h = mm2PX(pdf.get_y()) 
        
        rem_con = mm2PX(pdf.get_y())
        
        if rem_pro >=rem_con:
            rect_h = rem_pro-rem+20
        else:
            rect_h = rem_con-rem+20
            
        if rem+rect_h > 975:
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(126), px2MM(rem+1), px2MM(1674), px2MM(rect_h),'F')
            add_disclaimer(pdf)
               
        return rect_h+20
     
    add_base_page(pdf)
    rem = mm2PX(pdf.get_y())+20
    
    #//*---Disclaimer----*//
    add_disclaimer(pdf)
    
    row_color = '#F3F6F9'    
    pdf.set_fill_color(*hex2RGB(row_color))
    for i in range(len(df)):
        
        rect_h = get_rect_h(rem,df['pros'].iloc[i],df['cons'].iloc[i])
        text_y = rem+20
        
        if rem+rect_h > 975:
            add_base_page(pdf)
            rem = mm2PX(pdf.get_y())+20
            
            #//*---Disclaimer----*//
            add_disclaimer(pdf)
            
            row_color = '#F3F6F9'
            pdf.set_fill_color(*hex2RGB(row_color))
            rect_h = get_rect_h(rem,df['pros'].iloc[i],df['cons'].iloc[i])
            text_y = rem+20
            
        # print('rect height : ',rect_h)
        
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        
        #//*---Column 1 Value
        pdf.set_fill_color(*hex2RGB(row_color))
        pdf.rect(px2MM(126), px2MM(rem), px2MM(558), px2MM(rect_h),'FD')
        pdf.set_xy(px2MM(146),px2MM(text_y)) 
        pdf.multi_cell(px2MM(120), px2MM(32),'Insurer - ',align='L')
        
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_xy(px2MM(240),px2MM(text_y)) 
        pdf.multi_cell(px2MM(404), px2MM(32),df['insurer'].iloc[i],align='L')
        
        plan = mm2PX(pdf.get_y())
        
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_xy(px2MM(146),px2MM(plan+12)) 
        pdf.multi_cell(px2MM(100), px2MM(32),'Plan -',align='L')
        
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24)) 
        pdf.set_xy(px2MM(210),px2MM(plan+12)) 
        pdf.multi_cell(px2MM(404), px2MM(32),df['plan'].iloc[i],align='L')
        
        #//*----Column 2 Value
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.rect(px2MM(684), px2MM(rem), px2MM(558), px2MM(rect_h),'FD')
        
        strength = list(filter(remove_empty_strings, df['pros'].iloc[i]))
        for j in range(len(strength)):
            if strength[j]=='':
                continue
            if j==0:
                pdf.set_fill_color(*hex2RGB('#000000'))
                pdf.circle(x=px2MM(724),y=px2MM(text_y+15),r=px2MM(6),style='F')
                
                
                pdf.set_xy(px2MM(744),px2MM(text_y)) 
                pdf.multi_cell(px2MM(478), px2MM(32),strength[j],align='L')
                
            else:
                p_y = mm2PX(pdf.get_y())
                pdf.set_fill_color(*hex2RGB('#000000'))
                pdf.circle(x=px2MM(724),y=px2MM(p_y+15),r=px2MM(6),style='F')
        
                pdf.set_xy(px2MM(744),px2MM(p_y)) 
                pdf.multi_cell(px2MM(478), px2MM(32),strength[j],align='L')
                
        #//*----Column 3 Value
        pdf.set_fill_color(*hex2RGB(row_color))
        pdf.rect(px2MM(1242), px2MM(rem), px2MM(558), px2MM(rect_h),'FD')
        weakness = list(filter(remove_empty_strings, df['cons'].iloc[i]))
        for j in range(0,len(weakness)):

            if weakness[j]=='':
                continue
            if j==0:
                pdf.set_fill_color(*hex2RGB('#000000'))
                pdf.circle(x=px2MM(1282),y=px2MM(text_y+15),r=px2MM(6),style='F')
                
                pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
                pdf.set_xy(px2MM(1302),px2MM(text_y)) 
                pdf.multi_cell(px2MM(478), px2MM(32),weakness[j],align='L')
                
            else:
                p_y = mm2PX(pdf.get_y())
                pdf.set_fill_color(*hex2RGB('#000000'))
                pdf.circle(x=px2MM(1282),y=px2MM(p_y+15),r=px2MM(6),style='F')
                pdf.set_xy(px2MM(1302),px2MM(p_y))      
                pdf.multi_cell(px2MM(478), px2MM(32),weakness[j],align='L')
                
        pdf.set_fill_color(*hex2RGB(row_color))  
        
        if row_color == '#F3F6F9':
            row_color = '#FFFFFF'
        else:
            row_color = '#F3F6F9'
            
        rem = rem+rect_h
            
        # //*----Black VerticaL Line
        pdf.set_fill_color(*hex2RGB('#313236'))
        pdf.rect(px2MM(120), px2MM(204), px2MM(6), px2MM(rem-204),'F')
        
        # pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        # pdf.rect(px2MM(120), px2MM(1006), px2MM(1690), px2MM(40),'FD')
        # desclaimer = "Disclaimer: The above featured list is based on 1 Finance's proprietary research."
        # pdf.set_text_color(*hex2RGB('#000000'))
        # pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
        # pdf.set_xy(px2MM(120),px2MM(1008))      
        # pdf.multi_cell(px2MM(1680), px2MM(32),desclaimer,align='C')
            
  
#//*------Health Term Insurance -----*//        
def term_insurance(pdf,json_data,c_MoneyS,money_signData):
    
    # #//*------For Term Insurance Plans-----*//
    # df = pd.DataFrame.from_dict(json_data["featured_list"]['term_insurance']['table'])
    pg_name = 'Term Insurance Plans'
    # term_health_features(pdf,df,pg_name)
    
    
    #//*------------New Development------//
    term_ins_data = json_data["featured_list"]['term_insurance']['table']
    if term_ins_data == []:
        return None
    def add_feature_page(pdf,pg_name): 
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

        #//*----Featured List of Financial Products----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(877), px2MM(84),pg_name,align='L')
        
        pdf.set_xy(px2MM(1489),px2MM(114)) 
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(330), px2MM(32),'Financial Products Featured List',align='L')
        
        desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
        pdf.set_xy(px2MM(120), px2MM(1028))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        #//*-----Index Text of Page--**////
        pdf.set_xy(px2MM(1870), px2MM(1018))  
        pdf.set_font('LeagueSpartan-Light', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')
        
        global fin_feat_product_list
        if fin_feat_product_list == 0:
            fin_feat_product_list = pdf.page_no()
        
        return 204
        
        # pdf.image('https://imaages-hosting-1fin.s3.ap-south-1.amazonaws.com/assets/fund-logos/Term+insurance+logos/Max.png',px2MM(150), px2MM(254), px2MM(102), px2MM(102))
        
    main_y = add_feature_page(pdf,pg_name) 
    
    def get_all_rect_h(pdf,term_ins_data,main_y):
        
        pro_y = main_y+24
        for i in range(len(term_ins_data['pros'])):
            if term_ins_data['pros'][i] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(pro_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),term_ins_data['pros'][i],border='0',align='L')
                pro_y = mm2PX(pdf.get_y())+16
        pro_end = mm2PX(pdf.get_y())+24
        pro_h = pro_end-main_y
        con_y = pro_end+24
        
        for j in range(len(term_ins_data['cons'])):
            if term_ins_data['cons'][j] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),term_ins_data['cons'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
        con_end = mm2PX(pdf.get_y())+24
        con_h = con_end-pro_end
        card_h = pro_h+con_h
        
        if pro_h+con_h < 162:
            ext_h = 162-(pro_h+con_h)
            pro_h = pro_h+ext_h
        if card_h < 161:
            card_h = 162
            
        if main_y+card_h > 975:
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(126), px2MM(main_y), px2MM(1674), px2MM(card_h),'F')
            
            desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
            pdf.set_xy(px2MM(120), px2MM(1028))
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        return pro_h,con_h,card_h
            
        

        
    for card in range(len(term_ins_data)):
        # if card == 1:
        #     break

        pro_h,con_h,card_h = get_all_rect_h(pdf,term_ins_data[card],main_y)
        if 1080-(main_y+card_h) <= 90:
            main_y = add_feature_page(pdf,pg_name) 
            pro_h,con_h,card_h = get_all_rect_h(pdf,term_ins_data[card],main_y)
            
        # White rectangle
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(120), px2MM(main_y), px2MM(645), px2MM(card_h), 'F')
        
        try:
            pdf.image(term_ins_data[card]['feature_list_logo'],px2MM(150), px2MM(main_y+30), px2MM(102), px2MM(102))
        except Exception as e:
            print('no logo')
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(main_y+40))  
        pdf.multi_cell(px2MM(470), px2MM(42),term_ins_data[card]['insurer'],border='0',align='L')
        plan_y = mm2PX(pdf.get_y())+8
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(plan_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),term_ins_data[card]['plan'],border='0',align='L')
        
        # Card of Pros
        pdf.set_fill_color(*hex2RGB('#DEF7F1'))
        pdf.rect(px2MM(765), px2MM(main_y), px2MM(1035), px2MM(pro_h), 'F')
        
        pro_y = main_y+24
        if pro_y > 0:
            pdf.image(join(cwd,'assets', 'images','feature list','Thumbsup.svg'),px2MM(1744), px2MM(main_y+24), px2MM(32), px2MM(32))

        for i in range(len(term_ins_data[card]['pros'])):
            if term_ins_data[card]['pros'][i] !="":
                pdf.set_fill_color(*hex2RGB('#4B4C51'))
                pdf.rect(px2MM(789), px2MM(pro_y+14), px2MM(8), px2MM(8), 'F')
        
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(pro_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),term_ins_data[card]['pros'][i],border='0',align='L')
                pro_y = mm2PX(pdf.get_y())+16
        pro_end = main_y+pro_h
        con_y = pro_end+24
        
        # Card of Cons
        pdf.set_fill_color(*hex2RGB('#FFF5DA'))
        pdf.rect(px2MM(765), px2MM(pro_end), px2MM(1035), px2MM(con_h), 'F')
        
        if con_h > 0:
            pdf.image(join(cwd,'assets', 'images','feature list','Thumbsdown.svg'),px2MM(1744), px2MM(con_y), px2MM(32), px2MM(32))
        for j in range(len(term_ins_data[card]['cons'])):
            if term_ins_data[card]['cons'][j] !="":
                pdf.set_fill_color(*hex2RGB('#4B4C51'))
                pdf.rect(px2MM(789), px2MM(con_y+14), px2MM(8), px2MM(8), 'F')
                
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),term_ins_data[card]['cons'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
        
        main_y = mm2PX(pdf.get_y())+64
    
#//*------Health Insurance Plans-----*//

def health_insurance(pdf,json_data,c_MoneyS,money_signData):

    # df = pd.DataFrame.from_dict(json_data["featured_list"]['health_insurance']['table'])
    pg_name = 'Health Insurance Plans'
    # term_health_features(pdf,df,pg_name)
    
    #//*------------New Development------//
    health_ins_data = json_data["featured_list"]['health_insurance']['table']
    if health_ins_data == []:
        return None
    def add_feature_page(pdf,pg_name): 
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

        #//*----Featured List of Financial Products----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(877), px2MM(84),pg_name,align='L')
        
        pdf.set_xy(px2MM(1489),px2MM(114)) 
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(330), px2MM(32),'Financial Products Featured List',align='L')
        
        desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
        pdf.set_xy(px2MM(120), px2MM(1028))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        #//*-----Index Text of Page--**////
        pdf.set_xy(px2MM(1870), px2MM(1018))  
        pdf.set_font('LeagueSpartan-Light', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')
        
        global fin_feat_product_list
        if fin_feat_product_list == 0:
            fin_feat_product_list = pdf.page_no()
        
        return 204
        
        # pdf.image('https://imaages-hosting-1fin.s3.ap-south-1.amazonaws.com/assets/fund-logos/Term+insurance+logos/Max.png',px2MM(150), px2MM(254), px2MM(102), px2MM(102))
        
    main_y = add_feature_page(pdf,pg_name) 
    
    def get_all_rect_h(pdf,health_ins_data,main_y):
        
        pro_y = main_y+24
        for i in range(len(health_ins_data['pros'])):
            if health_ins_data['pros'][i] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(pro_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),health_ins_data['pros'][i],border='0',align='L')
                pro_y = mm2PX(pdf.get_y())+16
        pro_end = mm2PX(pdf.get_y())+24
        pro_h = pro_end-main_y
        con_y = pro_end+24
        
        for j in range(len(health_ins_data['cons'])):
            if health_ins_data['cons'][j] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),health_ins_data['cons'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
        con_end = mm2PX(pdf.get_y())+24
        con_h = con_end-pro_end
        card_h = pro_h+con_h
        
        if pro_h+con_h < 162:
            ext_h = 162-(pro_h+con_h)
            pro_h = pro_h+ext_h
        if card_h < 161:
            card_h = 162
            
        if main_y+card_h > 975:
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(126), px2MM(main_y), px2MM(1674), px2MM(card_h),'F')
            
            desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
            pdf.set_xy(px2MM(120), px2MM(1028))
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        return pro_h,con_h,card_h
            
    for card in range(len(health_ins_data)):
        pro_h,con_h,card_h = get_all_rect_h(pdf,health_ins_data[card],main_y)
        if 1080-(main_y+card_h) <= 90:
            main_y = add_feature_page(pdf,pg_name) 
            pro_h,con_h,card_h = get_all_rect_h(pdf,health_ins_data[card],main_y)
            
        # White rectangle
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(120), px2MM(main_y), px2MM(645), px2MM(card_h), 'F')
        
        try:
            pdf.image(health_ins_data[card]['feature_list_logo'],px2MM(150), px2MM(main_y+30), px2MM(102), px2MM(102))
        except Exception as e:
            print('no logo')
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(main_y+40))  
        pdf.multi_cell(px2MM(470), px2MM(42),health_ins_data[card]['insurer'],border='0',align='L')
        plan_y = mm2PX(pdf.get_y())+8
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(plan_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),health_ins_data[card]['plan'],border='0',align='L')
        
        # Card of Pros
        pdf.set_fill_color(*hex2RGB('#DEF7F1'))
        pdf.rect(px2MM(765), px2MM(main_y), px2MM(1035), px2MM(pro_h), 'F')
        
        pro_y = main_y+24
        if pro_y > 0:
            pdf.image(join(cwd,'assets', 'images','feature list','Thumbsup.svg'),px2MM(1744), px2MM(main_y+24), px2MM(32), px2MM(32))

        for i in range(len(health_ins_data[card]['pros'])):
            if health_ins_data[card]['pros'][i] !="":
                pdf.set_fill_color(*hex2RGB('#4B4C51'))
                pdf.rect(px2MM(789), px2MM(pro_y+14), px2MM(8), px2MM(8), 'F')
        
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(pro_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),health_ins_data[card]['pros'][i],border='0',align='L')
                pro_y = mm2PX(pdf.get_y())+16
        pro_end = main_y+pro_h
        con_y = pro_end+24
        
        # Card of Cons
        pdf.set_fill_color(*hex2RGB('#FFF5DA'))
        pdf.rect(px2MM(765), px2MM(pro_end), px2MM(1035), px2MM(con_h), 'F')
        
        if con_h > 0:
            pdf.image(join(cwd,'assets', 'images','feature list','Thumbsdown.svg'),px2MM(1744), px2MM(con_y), px2MM(32), px2MM(32))
        for j in range(len(health_ins_data[card]['cons'])):
            if health_ins_data[card]['cons'][j] !="":
                pdf.set_fill_color(*hex2RGB('#4B4C51'))
                pdf.rect(px2MM(789), px2MM(con_y+14), px2MM(8), px2MM(8), 'F')
                
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),health_ins_data[card]['cons'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
        
        main_y = mm2PX(pdf.get_y())+64
    
#//*----New Mutual Fund-------------*//

def equity_mutual_fund(pdf,json_data,c_MoneyS,money_signData):
    equity = json_data["featured_list"]['equity_mutual_funds']
    if equity == {}:
        return None
    
    def add_equity_page(pdf,key): 
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

        #//*----Equity Mutual Fund Heading----*//
        if key == 'large_cap':
            pg_name = 'Equity Mutual Funds - Large Cap Index' 
        elif key == 'flexi_cap': 
            pg_name = 'Equity Mutual Funds - Flexicap fund'
        else:
                pg_name = ''
            
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(1200), px2MM(84),pg_name,align='L')
        
        pdf.set_xy(px2MM(1489),px2MM(114)) 
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(330), px2MM(32),'Financial Products Featured List',align='L')
        
        desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
        pdf.set_xy(px2MM(120), px2MM(1028))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        #//*-----Index Text of Page--**////
        pdf.set_xy(px2MM(1870), px2MM(1018))  
        pdf.set_font('LeagueSpartan-Light', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')
        
        global fin_feat_product_list
        if fin_feat_product_list == 0:
            fin_feat_product_list = pdf.page_no()
        
        return 204 
    
    #//*---Function to check height of rectangle
    def get_rect_h(pdf,equity_data,main_y):
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(main_y+60))  
        pdf.multi_cell(px2MM(470), px2MM(42),equity_data['fund_scheme'],border='0',align='L')
        head_h = mm2PX(pdf.get_y())+60
        head_h = head_h - main_y
        
        pro_y = main_y+24
        for i in range(len(equity_data['strengths'])):
            if equity_data['strengths'][i] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(pro_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),equity_data['strengths'][i],border='0',align='L')
                pro_y = mm2PX(pdf.get_y())+16
        pro_end = mm2PX(pdf.get_y())+24
        pro_h = pro_end-main_y
        con_y = pro_end+24
        
        for j in range(len(equity_data['weakness'])):
            if equity_data['weakness'][j] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),equity_data['weakness'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
        con_end = mm2PX(pdf.get_y())+24
        con_h = con_end-pro_end
        card_h = pro_h+con_h

        if pro_h+con_h < head_h:
            ext_h = head_h-(pro_h+con_h)
            pro_h = pro_h+ext_h
        if card_h < head_h:
            card_h = head_h
            
        if main_y+card_h > 975:
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(126), px2MM(main_y), px2MM(1674), px2MM(card_h),'F')
            
            desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
            pdf.set_xy(px2MM(120), px2MM(1028))
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        return pro_h,con_h,card_h
    
    for key, items in equity.items():
        equity_data = json_data["featured_list"]['equity_mutual_funds'][key]  
        if equity_data == []:
            pass
        main_y = add_equity_page(pdf,key)

        # Creation of Cards
        for card in range(len(equity_data)):
            # if card ==2:
            #     break
            pro_h,con_h,card_h = get_rect_h(pdf,equity_data[card],main_y)
            
            if 1080-(main_y+card_h) <= 90:
                main_y = add_equity_page(pdf,key) 
                pro_h,con_h,card_h = get_rect_h(pdf,equity_data[card],main_y)
                
            # White rectangle
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.rect(px2MM(120), px2MM(main_y), px2MM(645), px2MM(card_h), 'F')
            
            try:
                pdf.image(equity_data[card]['feature_list_logo'],px2MM(150), px2MM(main_y+30), px2MM(102), px2MM(102))
            except Exception as e:
                print('no logo')
                
            pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.set_xy(px2MM(276), px2MM(main_y+60))  
            pdf.multi_cell(px2MM(470), px2MM(42),equity_data[card]['fund_scheme'],border='0',align='L')
            plan_y = mm2PX(pdf.get_y())+8
            
            # Card of Pros
            pdf.set_fill_color(*hex2RGB('#DEF7F1'))
            pdf.rect(px2MM(765), px2MM(main_y), px2MM(1035), px2MM(pro_h), 'F')
            
            pro_y = main_y+24
            if pro_y > 0:
                pdf.image(join(cwd,'assets', 'images','feature list','Thumbsup.svg'),px2MM(1744), px2MM(main_y+24), px2MM(32), px2MM(32))

            for i in range(len(equity_data[card]['strengths'])):
                if equity_data[card]['strengths'][i] !="":
                    pdf.set_fill_color(*hex2RGB('#4B4C51'))
                    pdf.rect(px2MM(789), px2MM(pro_y+14), px2MM(8), px2MM(8), 'F')
            
                    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#1A1A1D'))
                    pdf.set_xy(px2MM(809), px2MM(pro_y))  
                    pdf.multi_cell(px2MM(900), px2MM(32),equity_data[card]['strengths'][i],border='0',align='L')
                    pro_y = mm2PX(pdf.get_y())+16
            pro_end = main_y+pro_h
            con_y = pro_end+24
                    
            # Card of Cons
            pdf.set_fill_color(*hex2RGB('#FFF5DA'))
            pdf.rect(px2MM(765), px2MM(pro_end), px2MM(1035), px2MM(con_h), 'F')
                    
            if con_h > 0:
                pdf.image(join(cwd,'assets', 'images','feature list','Thumbsdown.svg'),px2MM(1744), px2MM(con_y), px2MM(32), px2MM(32))
            for j in range(len(equity_data[card]['weakness'])):
                if equity_data[card]['weakness'][j] !="":
                    pdf.set_fill_color(*hex2RGB('#4B4C51'))
                    pdf.rect(px2MM(789), px2MM(con_y+14), px2MM(8), px2MM(8), 'F')
                    
                    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#1A1A1D'))
                    pdf.set_xy(px2MM(809), px2MM(con_y))  
                    pdf.multi_cell(px2MM(900), px2MM(32),equity_data[card]['weakness'][j],border='0',align='L')
                    con_y = mm2PX(pdf.get_y())+16
                    
            main_y = main_y+card_h+40
                    
                    

            
            
                               

            
            
#//*-----Bureau Report Summary---*//
def bureao_report(pdf,json_data,c_MoneyS,money_signData):
    try:
        csa = json_data["bureau_report_summary"]['credit_score_analysis']
        cft = pd.DataFrame.from_dict(json_data["bureau_report_summary"]['credit_facilities_taken'])
    except Exception as e:
        return None
    
    if csa['score'].strip()=="":
        return None
    
    if cft.empty:
        return None
    try:
        # cft = cft.update(cft.select_dtypes(include=np.number).applymap('{:,g}'.format))
        type_facility = cft["type_of_facility"].tolist()
        tot_record = cft["total_records"].tolist()
        active_acc = cft["active_accounts"].tolist()
        clsd_acc = cft["closed_accounts"].tolist()
        acc_neg_hist = cft["accounts_with_negative_history"].tolist()
        
        
        total_record = sum(list(filter(lambda i: isinstance(i, (int,float)), tot_record)))
        total_active_account = sum(list(filter(lambda i: isinstance(i, (int,float)), active_acc)))
        total_closed_accounts = sum(list(filter(lambda i: isinstance(i, (int,float)), clsd_acc)))
        total_acc_neg_hist = sum(list(filter(lambda i: isinstance(i, (int,float)), acc_neg_hist)))
    except Exception as e:
        return None

    
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #//*----Featured List of Financial Products----*//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(877), px2MM(84),'Bureau Report Summary',align='L')
    
    #//*---Top Black box
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F')
    
    #//*---Credit Score Analysis
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(126), px2MM(204), px2MM(243), px2MM(42),'F')
    
    
    
    pdf.set_xy(px2MM(141),px2MM(209)) 
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.cell(px2MM(213), px2MM(32),'Credit Score Analysis',align='C')
    
    #//*---Table Header----*//
    pdf.set_fill_color(*hex2RGB('#ffffff'))
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    #//*---Col 1
    pdf.rect(px2MM(126), px2MM(246), px2MM(240), px2MM(72),'FD')
    pdf.set_xy(px2MM(146),px2MM(266)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(200), px2MM(32),'Your Credit Score',align='C')
     #//*---Col 2
    pdf.rect(px2MM(366), px2MM(246), px2MM(320), px2MM(72),'FD')
    pdf.set_xy(px2MM(386),px2MM(266)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.cell(px2MM(600), px2MM(32),'Our Evaluation',align='L')
     #//*---Col 3
    pdf.rect(px2MM(686), px2MM(246), px2MM(1114), px2MM(72),'FD')
    pdf.set_xy(px2MM(706),px2MM(266)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.cell(px2MM(1074), px2MM(32),'Comments',align='L')
    
    
    #//*---Table Value---*//
    if len(csa["commentary"]) > 92:
        rect_h = 104
        text_h = 64
        comm_h = 32
        bl_hight1 = 218
    else:
        comm_h = 32
        rect_h = 72
        text_h = 32
        bl_hight1 = 186
        
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(204), px2MM(6), px2MM(bl_hight1),'F')
    
    
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    #//*---Col 1
    pdf.rect(px2MM(126), px2MM(318), px2MM(240), px2MM(rect_h),'FD')
    pdf.set_xy(px2MM(146),px2MM(338)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(200), px2MM(text_h),str(csa['score']),align='C')
     #//*---Col 2
    pdf.rect(px2MM(366), px2MM(318), px2MM(320), px2MM(rect_h),'FD')
    pdf.set_xy(px2MM(386),px2MM(338)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.multi_cell(px2MM(600), px2MM(text_h),csa['our_evaluation'],align='L')
     #//*---Col 3
    pdf.rect(px2MM(686), px2MM(318), px2MM(1114), px2MM(rect_h),'FD')
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.circle(x=px2MM(726),y=px2MM(351),r=px2MM(5),style='F')
    pdf.set_xy(px2MM(746),px2MM(338)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.multi_cell(px2MM(1034), px2MM(comm_h),csa["commentary"],align='L')
    
    
    
    #//*---Credit Facilities Taken---*//
    
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(126), px2MM(502), px2MM(248), px2MM(42),'F')
    
    pdf.set_xy(px2MM(141),px2MM(507)) 
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.cell(px2MM(218), px2MM(32),'Credit Facilities Taken',align='C')
    
    bl_hight = 114
    
    
    #//*---Table Header----*//
    pdf.set_fill_color(*hex2RGB('#ffffff'))
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    
    #//*---Col 1
    pdf.rect(px2MM(126), px2MM(544), px2MM(290), px2MM(72),'FD')
    pdf.set_xy(px2MM(146),px2MM(564)) 
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(250), px2MM(32),'Type of Facility',align='L')
    #//*---Col 2
    pdf.rect(px2MM(416), px2MM(544), px2MM(290), px2MM(72),'FD')
    pdf.set_xy(px2MM(436),px2MM(564)) 
    pdf.cell(px2MM(250), px2MM(32),'Total Records',align='C')
    #//*---Col 3
    pdf.rect(px2MM(706), px2MM(544), px2MM(290), px2MM(72),'FD')
    pdf.set_xy(px2MM(726),px2MM(564)) 
    pdf.cell(px2MM(250), px2MM(32),'Active Accounts',align='C')
    #//*---Col 4
    pdf.rect(px2MM(996), px2MM(544), px2MM(290), px2MM(72),'FD')
    pdf.set_xy(px2MM(1016),px2MM(564)) 
    pdf.cell(px2MM(250), px2MM(32),'Closed Accounts',align='C')
    #//*---Col 5
    pdf.rect(px2MM(1286), px2MM(544), px2MM(514), px2MM(72),'FD')
    pdf.set_xy(px2MM(1306),px2MM(564)) 
    pdf.cell(px2MM(474), px2MM(32),'Accounts with Negative History',align='C')
    
    for i in range(len(type_facility)):
        #//*---Table Header----*//
        if i%2==0:
            pdf.set_fill_color(*hex2RGB('#F3F6F9'))
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        else:
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_fill_color(*hex2RGB('#ffffff'))
            
        if i==len(type_facility):
            pdf.set_fill_color(*hex2RGB('#ffffff'))
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.5))
        #//*---Col 1
        pdf.rect(px2MM(126), px2MM(616+(i*52)), px2MM(290), px2MM(52),'FD')
        pdf.set_xy(px2MM(146),px2MM(626+(i*52))) 
        
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(250), px2MM(32),str(type_facility[i]),align='L')
        #//*---Col 2
        pdf.rect(px2MM(416), px2MM(616+(i*52)), px2MM(290), px2MM(52),'FD')
        pdf.set_xy(px2MM(436),px2MM(626+(i*52)))
        # if tot_record[i] == 0 or tot_record[i] == '':
        #     pdf.cell(px2MM(250), px2MM(32),'0',align='C')
        # else:
        pdf.cell(px2MM(250), px2MM(32),str(tot_record[i]),align='C')
        #//*---Col 3
        pdf.rect(px2MM(706), px2MM(616+(i*52)), px2MM(290), px2MM(52),'FD')
        pdf.set_xy(px2MM(726),px2MM(626+(i*52))) 
        # if active_acc[i] ==0 or active_acc[i] == '':
        #     pdf.cell(px2MM(250), px2MM(32),'0',align='C')
        # else: 
        pdf.cell(px2MM(250), px2MM(32),str(active_acc[i]),align='C')
        #//*---Col 4
        pdf.rect(px2MM(996), px2MM(616+(i*52)), px2MM(290), px2MM(52),'FD')
        pdf.set_xy(px2MM(1016),px2MM(626+(i*52))) 
        # if clsd_acc[i] ==0:
        #     pdf.cell(px2MM(250), px2MM(32),'0',align='C')
        # else:
        pdf.cell(px2MM(250), px2MM(32),str(clsd_acc[i]),align='C')
        #//*---Col 5
        pdf.rect(px2MM(1286), px2MM(616+(i*52)), px2MM(514), px2MM(52),'FD')
        pdf.set_xy(px2MM(1306),px2MM(626+(i*52))) 
        # if acc_neg_hist[i]==0:
        #     pdf.cell(px2MM(474), px2MM(32),'0',align='C')
        # else:
        pdf.cell(px2MM(474), px2MM(32),str(acc_neg_hist[i]),align='C')
        
    
        bl_hight+=52
    
    #//*---Total----*// 
    tot_height = pdf.get_y()   
    pdf.set_fill_color(*hex2RGB('#B9BABE'))
    pdf.set_draw_color(*hex2RGB('#B9BABE'))
    pdf.set_line_width(px2MM(1))
    pdf.rect(px2MM(126), px2MM(mm2PX(tot_height)+43), px2MM(1674), px2MM(1),'FD') 
    
    
    pdf.set_fill_color(*hex2RGB('#ffffff'))
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.rect(px2MM(126), px2MM(mm2PX(tot_height)+44), px2MM(1674), px2MM(52),'FD') 
    
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    #//*---Col 1

    # pdf.rect(px2MM(126), px2MM(mm2PX(tot_height)+43), px2MM(290), px2MM(52),'F') 
    pdf.set_xy(px2MM(146),px2MM(mm2PX(tot_height)+53)) 
    pdf.cell(px2MM(290), px2MM(32),'Total',align='L')
    #//*---Col 2
    # pdf.rect(px2MM(416), px2MM(mm2PX(tot_height)+43), px2MM(290), px2MM(52),'F')
    pdf.set_xy(px2MM(416),px2MM(mm2PX(tot_height)+53)) 
    pdf.cell(px2MM(290), px2MM(32),str(total_record),align='C')
    #//*---Col 3
    # pdf.rect(px2MM(706), px2MM(mm2PX(tot_height)+43), px2MM(290), px2MM(52),'F')
    pdf.set_xy(px2MM(706),px2MM(mm2PX(tot_height)+53)) 
    pdf.cell(px2MM(290), px2MM(32),str(total_active_account),align='C')
    #//*---Col 4
    # pdf.rect(px2MM(996), px2MM(mm2PX(tot_height)+43), px2MM(290), px2MM(52),'F')
    pdf.set_xy(px2MM(996),px2MM(mm2PX(tot_height)+53)) 
    pdf.cell(px2MM(290), px2MM(32),str(total_closed_accounts),align='C')
    #//*---Col 5
    # pdf.rect(px2MM(1286), px2MM(mm2PX(tot_height)+43), px2MM(514), px2MM(52),'F')
    pdf.set_xy(px2MM(1286),px2MM(mm2PX(tot_height)+53)) 
    pdf.cell(px2MM(514), px2MM(32),str(total_acc_neg_hist),align='C')
    
    bl_hight+=52
    rem = mm2PX(pdf.get_y())+43
    bl_hight = rem-502
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(502), px2MM(6), px2MM(bl_hight),'F')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
            
#//*-----Liability Management 1---*//
def libility_management_1(pdf,json_data,c_MoneyS,money_signData):
    try:
        aff_check = pd.DataFrame.from_dict(json_data["liability_management"]['table'])
        aff_check_total = json_data["liability_management"]['total']
        aff_comment = json_data["liability_management"]['comments']
    except Exception as e:
        return None
    
    if aff_check.empty:
        return None
    
    try:
        lib_type = aff_check["liability_type"].tolist()
        outstanding = aff_check['current_liability_distribution_outstanding_percentage'].tolist()
        out_emi = aff_check['current_liability_distribution_emi_percentage'].tolist()
        balance = aff_check['suggested_loan_size_range'].tolist()
        bal_emi = aff_check['suggested_emi_range'].tolist()
        
    except Exception as e:
        return None
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')

    #//*----Featured List of Financial Products----*//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(877), px2MM(84),'Liability Management',align='L')
    
    #//*---Top Black box
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F')    
    
    
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(126), px2MM(204), px2MM(224), px2MM(42),'F')
    
    pdf.set_xy(px2MM(141),px2MM(209)) 
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.cell(px2MM(194), px2MM(32),'Affordability Check',align='C')
    
    bl_height = 146
    #//*------Affordability Check----*//
    #//*---Col 1
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_fill_color(*hex2RGB('#ffffff'))
    pdf.rect(px2MM(126), px2MM(246), px2MM(290), px2MM(104),'FD')

    pdf.set_xy(px2MM(146),px2MM(280)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(194), px2MM(32),'Liability Type',align='L')

    #//*----Col 1/1-----*//
    pdf.rect(px2MM(416), px2MM(246), px2MM(692), px2MM(52),'FD')
    pdf.set_xy(px2MM(436),px2MM(256)) 
    pdf.cell(px2MM(652), px2MM(32),'Current Liability Distribution',align='C')
    
    #//*----Col 1/1-1-----*//
    pdf.rect(px2MM(416), px2MM(298), px2MM(346), px2MM(52),'FD')
    pdf.set_xy(px2MM(436),px2MM(308)) 
    pdf.cell(px2MM(306), px2MM(32),'Outstanding',align='C')
    
    #//*----Col 1/1-2-----*//
    pdf.rect(px2MM(762), px2MM(298), px2MM(346), px2MM(52),'FD')
    pdf.set_xy(px2MM(782),px2MM(308)) 
    pdf.cell(px2MM(306), px2MM(32),'EMI',align='C')
    
     #//*----Col 2/1-----*//
    pdf.rect(px2MM(1108), px2MM(246), px2MM(692), px2MM(52),'FD')
    pdf.set_xy(px2MM(1128),px2MM(256)) 
    pdf.cell(px2MM(652), px2MM(32),'Suggested Range',align='C')
    
    #//*----Col 2/1-1-----*//
    pdf.rect(px2MM(1108), px2MM(298), px2MM(346), px2MM(52),'FD')
    pdf.set_xy(px2MM(1128),px2MM(308)) 
    pdf.cell(px2MM(306), px2MM(32),'Loan Size',align='C')
    
    #//*----Col 2/1-2-----*//
    pdf.rect(px2MM(1454), px2MM(298), px2MM(346), px2MM(52),'FD')
    pdf.set_xy(px2MM(1474),px2MM(308)) 
    pdf.cell(px2MM(306), px2MM(32),'EMI',align='C')
    
    
    #//*---Table Data---*//
    
    
    rect_y = 350
    text_y = 365
    common_gap = 62
    
    for i in range(len(lib_type)):
        if i%2==0:
            pdf.set_fill_color(*hex2RGB('#F3F6F9'))
        else:
            pdf.set_fill_color(*hex2RGB('#ffffff'))
            
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        pdf.rect(px2MM(126), px2MM(rect_y), px2MM(290), px2MM(62),'FD')

        #//*--Col 1---*/
        pdf.set_xy(px2MM(146),px2MM(text_y)) 
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(194), px2MM(32),str(lib_type[i]),align='L')
        
        #//*---Col 2---*/
        pdf.rect(px2MM(416), px2MM(rect_y), px2MM(346), px2MM(62),'FD')
        pdf.set_xy(px2MM(436),px2MM(text_y)) 
        # pdf.cell(px2MM(306), px2MM(32),outstanding[i]+'%',align='C')
        pdf.cell(px2MM(306), px2MM(32),'₹ '+str(format_cash2(float(outstanding[i]))),align='C')
        
        #//*---Col 3---*/
        pdf.rect(px2MM(762), px2MM(rect_y), px2MM(346), px2MM(62),'FD')
        pdf.set_xy(px2MM(782),px2MM(text_y)) 
        
        if int(float(out_emi[i]))==0:
            pdf.cell(px2MM(306), px2MM(32),'₹ 0.0K',align='C')
        else:
            pdf.cell(px2MM(306), px2MM(32),'₹ '+str(format_cash(float(out_emi[i]))),align='C')
        
        #//*---Col 4---*/
        pdf.rect(px2MM(1108), px2MM(rect_y), px2MM(346), px2MM(62),'FD')
        pdf.set_xy(px2MM(1128),px2MM(text_y)) 
        val =  balance[i].split('to')
        val = " to ".join(list('₹ '+str(format_cash2(float(x))) for x in val))
        # pdf.cell(px2MM(306), px2MM(32),balance[i],align='C')
        pdf.cell(px2MM(306), px2MM(32),val,align='C')
        
        #//*---Col 5---*/
        pdf.rect(px2MM(1454), px2MM(rect_y), px2MM(346), px2MM(62),'FD')
        pdf.set_xy(px2MM(1474),px2MM(text_y)) 
        val =  bal_emi[i].split('to')
        val = " to ".join(list('₹ '+str(format_cash(float(x))) for x in val))
        # pdf.cell(px2MM(306), px2MM(32),bal_emi[i],align='C')
        pdf.cell(px2MM(306), px2MM(32),val,align='C')
        
        rect_y+=common_gap
        text_y+=common_gap
        bl_height+=common_gap

    text_y -= 5    
    #//*---Total-----*//
        
    pdf.set_draw_color(*hex2RGB('#B9BABE'))
    pdf.set_fill_color(*hex2RGB('#B9BABE'))
    pdf.set_line_width(px2MM(1))
    pdf.rect(px2MM(126), px2MM(rect_y), px2MM(1674), px2MM(1),'FD')
    
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(126), px2MM(rect_y+1), px2MM(1674), px2MM(52),'FD')

    #//*--Col 1---*/
    pdf.set_xy(px2MM(146),px2MM(text_y)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(194), px2MM(32),'Total',align='L')
    
    #//*---Col 2---*/

    pdf.set_xy(px2MM(436),px2MM(text_y)) 

    val1 = '₹ '+str(format_cash2(float(aff_check_total['current_liability_distribution_outstanding_percentage'])))
    pdf.cell(px2MM(306), px2MM(32),val1,align='C')
    
    #//*---Col 3---*/
    pdf.set_xy(px2MM(782),px2MM(text_y)) 
    if int(float(aff_check_total['current_liability_distribution_emi_percentage']))==0:
        val2 = '₹ 0.0K'
    else:
        val2 = '₹ '+str(format_cash(float(aff_check_total['current_liability_distribution_emi_percentage'])))
    pdf.cell(px2MM(306), px2MM(32),val2,align='C')
    
    #//*---Col 4---*/
    pdf.set_xy(px2MM(1128),px2MM(text_y))
    val =  aff_check_total['suggested_loan_size_range'].split('to')
    val = " to ".join(list('₹ '+str(format_cash2(float(x))) for x in val))
    pdf.cell(px2MM(306), px2MM(32),val,align='C')
    
    #//*---Col 5---*/
    pdf.set_xy(px2MM(1474),px2MM(text_y)) 
    val =  aff_check_total['suggested_emi_range'].split('to')
    val = " to ".join(list('₹ '+str(format_cash(float(x))) for x in val))
    pdf.cell(px2MM(306), px2MM(32),val,align='C')
    
    
    desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
    pdf.set_xy(px2MM(405), px2MM(1019))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C")
    
    
    try:
        statement = aff_comment 
    except Exception as e:
        return None 
    
    if statement ==[]:
        return None 
    
    flag = 'True'
    
    for i in statement :
        if i == "" or i == None:
            flag = 'False'
        else:
            flag = 'True'
            break
    
    if flag == 'False':
        return None
    
    
    #//*---Long Black vertical line
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(204), px2MM(6), px2MM(bl_height+53),'F')
    
    comment_y = pdf.get_y()
    
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_xy(px2MM(120),px2MM(mm2PX(comment_y)+122)) 
    pdf.cell(px2MM(170), px2MM(56),'Comments',align='L')
    
    for_stat = 682
    
    
    for i in range(len(statement)):    
        if statement[i] == "":
            continue   
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(120), px2MM(for_stat+20), px2MM(10), px2MM(10),'F')
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(150),px2MM(for_stat)) 
        pdf.cell(px2MM(1304), px2MM(42),statement[i],align='L')
        
        for_stat+=52
        
#//*----Financial Product List (Debt Mutual Funds)-----*//
def debt_mutual_fund(pdf,json_data,c_MoneyS,money_signData):
    
    
    debt = json_data["featured_list"]['debt_mutual_fund']
    if debt == {}:
        return None
    
    def add_debt_page(pdf,key): 
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

        #//*----Equity Mutual Fund Heading----*//
        if key == 'liquid_funds':
            pg_name = 'Debt Mutual Funds - Liquid Funds' 
        elif key == 'short_term': 
            pg_name = 'Debt Mutual Funds - Short term'
        elif key == 'dynamic_bond': 
            pg_name = 'Debt Mutual Funds - Dynamic Bond'
        else:
            pg_name = ''
            
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(1200), px2MM(84),pg_name,align='L')
        
        pdf.set_xy(px2MM(1489),px2MM(114)) 
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(330), px2MM(32),'Financial Products Featured List',align='L')
        
        desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
        pdf.set_xy(px2MM(120), px2MM(1028))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        #//*-----Index Text of Page--**////
        pdf.set_xy(px2MM(1870), px2MM(1018))  
        pdf.set_font('LeagueSpartan-Light', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')
        
        global fin_feat_product_list
        if fin_feat_product_list == 0:
            fin_feat_product_list = pdf.page_no()
        
        return 204
    
    #//*---Function to check height of rectangle
    def get_rect_h(pdf,debt_data,main_y):
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(main_y+40))  
        pdf.multi_cell(px2MM(470), px2MM(42),debt_data['name'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+8
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(429), px2MM(h_y))  
        pdf.multi_cell(px2MM(310), px2MM(32),debt_data['investment_horizon'],border='0',align='L')
        
        head_h = mm2PX(pdf.get_y())+40
        head_h = head_h - main_y
        
        pro_y = main_y+24
        for i in range(len(debt_data['strength'])):
            if debt_data['strength'][i] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(pro_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),debt_data['strength'][i],border='0',align='L')
                pro_y = mm2PX(pdf.get_y())+16
        pro_end = mm2PX(pdf.get_y())+24
        pro_h = pro_end-main_y
        con_y = pro_end+24
        
        for j in range(len(debt_data['weakness'])):
            if debt_data['weakness'][j] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),debt_data['weakness'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
        con_end = mm2PX(pdf.get_y())+24
        con_h = con_end-pro_end
        card_h = pro_h+con_h

        if pro_h+con_h < head_h:
            ext_h = head_h-(pro_h+con_h)
            pro_h = pro_h+ext_h
        if card_h < head_h:
            card_h = head_h
            
        if main_y+card_h > 975:
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(126), px2MM(main_y), px2MM(1674), px2MM(card_h),'F')
            
            desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
            pdf.set_xy(px2MM(120), px2MM(1028))
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        return pro_h,con_h,card_h
    
    for key, items in debt.items():

        debt_data = json_data["featured_list"]['debt_mutual_fund'][key]
        if debt_data == []:
            pass
        if len(items) > 0:
            main_y = add_debt_page(pdf,key)

        # Creation of Cards
        for card in range(len(debt_data)):
            # if card ==2:
            #     break
            pro_h,con_h,card_h = get_rect_h(pdf,debt_data[card],main_y)
            
            if 1080-(main_y+card_h) <= 90:
                main_y = add_debt_page(pdf,key) 
                pro_h,con_h,card_h = get_rect_h(pdf,debt_data[card],main_y)
                
            # White rectangle
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.rect(px2MM(120), px2MM(main_y), px2MM(645), px2MM(card_h), 'F')
            
            try:
                pdf.image(debt_data[card]['feature_list_logo'],px2MM(150), px2MM(main_y+30), px2MM(102), px2MM(102))
            except Exception as e:
                print('no logo')
                
            pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.set_xy(px2MM(276), px2MM(main_y+40))  
            pdf.multi_cell(px2MM(470), px2MM(42),debt_data[card]['name'],border='0',align='L')

            h_y = mm2PX(pdf.get_y())+8
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
            pdf.set_text_color(*hex2RGB('#65676D'))
            pdf.set_xy(px2MM(276), px2MM(h_y))  
            pdf.multi_cell(px2MM(150), px2MM(32),'Investment horizon',border='0',align='L')
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
            pdf.set_text_color(*hex2RGB('#212120'))
            pdf.set_xy(px2MM(429), px2MM(h_y))  
            pdf.multi_cell(px2MM(310), px2MM(32),debt_data[card]['investment_horizon'],border='0',align='L')
            
            # Card of Pros
            pdf.set_fill_color(*hex2RGB('#DEF7F1'))
            pdf.rect(px2MM(765), px2MM(main_y), px2MM(1035), px2MM(pro_h), 'F')
            
            pro_y = main_y+24
            if pro_y > 0:
                pdf.image(join(cwd,'assets', 'images','feature list','Thumbsup.svg'),px2MM(1744), px2MM(main_y+24), px2MM(32), px2MM(32))

            for i in range(len(debt_data[card]['strength'])):
                if debt_data[card]['strength'][i] !="":
                    pdf.set_fill_color(*hex2RGB('#4B4C51'))
                    pdf.rect(px2MM(789), px2MM(pro_y+14), px2MM(8), px2MM(8), 'F')
            
                    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#1A1A1D'))
                    pdf.set_xy(px2MM(809), px2MM(pro_y))  
                    pdf.multi_cell(px2MM(900), px2MM(32),debt_data[card]['strength'][i],border='0',align='L')
                    pro_y = mm2PX(pdf.get_y())+16
            pro_end = main_y+pro_h
            con_y = pro_end+24
                    
            # Card of Cons
            pdf.set_fill_color(*hex2RGB('#FFF5DA'))
            pdf.rect(px2MM(765), px2MM(pro_end), px2MM(1035), px2MM(con_h), 'F')
                    
            if con_h > 0:
                pdf.image(join(cwd,'assets', 'images','feature list','Thumbsdown.svg'),px2MM(1744), px2MM(con_y), px2MM(32), px2MM(32))
            for j in range(len(debt_data[card]['weakness'])):
                if debt_data[card]['weakness'][j] !="":
                    pdf.set_fill_color(*hex2RGB('#4B4C51'))
                    pdf.rect(px2MM(789), px2MM(con_y+14), px2MM(8), px2MM(8), 'F')
                    
                    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#1A1A1D'))
                    pdf.set_xy(px2MM(809), px2MM(con_y))  
                    pdf.multi_cell(px2MM(900), px2MM(32),debt_data[card]['weakness'][j],border='0',align='L')
                    con_y = mm2PX(pdf.get_y())+16
                    
            main_y = main_y+card_h+40
            
            
            
            
                
            
#//*----Financial Product List (Hybrid Mutual Funds)-----*//
def hybrid_mutual_fund(pdf,json_data,c_MoneyS,money_signData):
    hybrid = json_data["featured_list"]['hybrid_mutual_fund']
    
    if hybrid == {}:
        return None
    
    def add_hybrid_page(pdf,key): 
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

        #//*----Equity Mutual Fund Heading----*//
        if key == 'balanced_advantage':
            pg_name = 'Hybrid Mutual Funds - Balanced Advantage' 
        elif key == 'aggressive_hybrid': 
            pg_name = 'Hybrid Mutual Funds - Aggressive Hybrid'
        elif key == 'arbitrage_fund':
            pg_name = 'Hybrid Mutual Funds - Arbitrage Hybrid'
        else:
            pg_name = ''
            
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(1200), px2MM(84),pg_name,align='L')
        
        pdf.set_xy(px2MM(1489),px2MM(114)) 
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(330), px2MM(32),'Financial Products Featured List',align='L')
        
        desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
        pdf.set_xy(px2MM(120), px2MM(1028))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        #//*-----Index Text of Page--**////
        pdf.set_xy(px2MM(1870), px2MM(1018))  
        pdf.set_font('LeagueSpartan-Light', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')
        
        global fin_feat_product_list
        if fin_feat_product_list == 0:
            fin_feat_product_list = pdf.page_no()
        
        return 204
    
    #//*---Function to check height of rectangle
    def get_rect_h(pdf,hybrid_data,main_y):
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(main_y+40))  
        pdf.multi_cell(px2MM(470), px2MM(42),hybrid_data['name'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+8
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(429), px2MM(h_y))  
        pdf.multi_cell(px2MM(310), px2MM(32),hybrid_data['investment_horizon'],border='0',align='L')
        
        head_h = mm2PX(pdf.get_y())+40
        head_h = head_h - main_y
        
        pro_y = main_y+24
        for i in range(len(hybrid_data['strength'])):
            if hybrid_data['strength'][i] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(pro_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),hybrid_data['strength'][i],border='0',align='L')
                pro_y = mm2PX(pdf.get_y())+16
        pro_end = mm2PX(pdf.get_y())+24
        pro_h = pro_end-main_y
        con_y = pro_end+24
        
        for j in range(len(hybrid_data['weakness'])):
            if hybrid_data['weakness'][j] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),hybrid_data['weakness'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
        con_end = mm2PX(pdf.get_y())+24
        con_h = con_end-pro_end
        card_h = pro_h+con_h

        if pro_h+con_h < head_h:
            ext_h = head_h-(pro_h+con_h)
            pro_h = pro_h+ext_h
        if card_h < head_h:
            card_h = head_h
            
        if main_y+card_h > 975:
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(126), px2MM(main_y), px2MM(1674), px2MM(card_h),'F')
            
            desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
            pdf.set_xy(px2MM(120), px2MM(1028))
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        return pro_h,con_h,card_h
    
    for key, items in hybrid.items():

        hybrid_data = json_data["featured_list"]['hybrid_mutual_fund'][key]
        if hybrid_data == []:
            continue
        
        main_y = add_hybrid_page(pdf,key)

        # Creation of Cards
        for card in range(len(hybrid_data)):
            # if card ==2:
            #     break
            pro_h,con_h,card_h = get_rect_h(pdf,hybrid_data[card],main_y)
            
            if 1080-(main_y+card_h) <= 90:
                main_y = add_hybrid_page(pdf,key) 
                pro_h,con_h,card_h = get_rect_h(pdf,hybrid_data[card],main_y)
                
            # White rectangle
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.rect(px2MM(120), px2MM(main_y), px2MM(645), px2MM(card_h), 'F')
            
            try:
                pdf.image(hybrid_data[card]['feature_list_logo'],px2MM(150), px2MM(main_y+30), px2MM(102), px2MM(102))
            except Exception as e:
                print('no logo')
                
            pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.set_xy(px2MM(276), px2MM(main_y+40))  
            pdf.multi_cell(px2MM(470), px2MM(42),hybrid_data[card]['name'],border='0',align='L')

            h_y = mm2PX(pdf.get_y())+8
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
            pdf.set_text_color(*hex2RGB('#65676D'))
            pdf.set_xy(px2MM(276), px2MM(h_y))  
            pdf.multi_cell(px2MM(150), px2MM(32),'Investment horizon',border='0',align='L')
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
            pdf.set_text_color(*hex2RGB('#212120'))
            pdf.set_xy(px2MM(429), px2MM(h_y))  
            pdf.multi_cell(px2MM(310), px2MM(32),hybrid_data[card]['investment_horizon'],border='0',align='L')
            
            # Card of Pros
            pdf.set_fill_color(*hex2RGB('#DEF7F1'))
            pdf.rect(px2MM(765), px2MM(main_y), px2MM(1035), px2MM(pro_h), 'F')
            
            pro_y = main_y+24
            if pro_y > 0:
                pdf.image(join(cwd,'assets', 'images','feature list','Thumbsup.svg'),px2MM(1744), px2MM(main_y+24), px2MM(32), px2MM(32))

            for i in range(len(hybrid_data[card]['strength'])):
                if hybrid_data[card]['strength'][i] !="":
                    pdf.set_fill_color(*hex2RGB('#4B4C51'))
                    pdf.rect(px2MM(789), px2MM(pro_y+14), px2MM(8), px2MM(8), 'F')
            
                    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#1A1A1D'))
                    pdf.set_xy(px2MM(809), px2MM(pro_y))  
                    pdf.multi_cell(px2MM(900), px2MM(32),hybrid_data[card]['strength'][i],border='0',align='L')
                    pro_y = mm2PX(pdf.get_y())+16
            pro_end = main_y+pro_h
            con_y = pro_end+24
                    
            # Card of Cons
            pdf.set_fill_color(*hex2RGB('#FFF5DA'))
            pdf.rect(px2MM(765), px2MM(pro_end), px2MM(1035), px2MM(con_h), 'F')
                    
            if con_h > 0:
                pdf.image(join(cwd,'assets', 'images','feature list','Thumbsdown.svg'),px2MM(1744), px2MM(con_y), px2MM(32), px2MM(32))
            for j in range(len(hybrid_data[card]['weakness'])):
                if hybrid_data[card]['weakness'][j] !="":
                    pdf.set_fill_color(*hex2RGB('#4B4C51'))
                    pdf.rect(px2MM(789), px2MM(con_y+14), px2MM(8), px2MM(8), 'F')
                    
                    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#1A1A1D'))
                    pdf.set_xy(px2MM(809), px2MM(con_y))  
                    pdf.multi_cell(px2MM(900), px2MM(32),hybrid_data[card]['weakness'][j],border='0',align='L')
                    con_y = mm2PX(pdf.get_y())+16
                    
            main_y = main_y+card_h+40
            
            
#//*----Financial Product List (Credit Cards)-----*//
def credit_cards(pdf,json_data,c_MoneyS,money_signData):
    
    credit_card = json_data["featured_list"]['credit_card']
    
    def add_credit_card_page(pdf): 
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

            
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(1200), px2MM(84),'Credit Cards',align='L')
        
        pdf.set_xy(px2MM(1489),px2MM(114)) 
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(330), px2MM(32),'Financial Products Featured List',align='L')
        
        desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
        pdf.set_xy(px2MM(120), px2MM(1028))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        #//*-----Index Text of Page--**////
        pdf.set_xy(px2MM(1870), px2MM(1018))  
        pdf.set_font('LeagueSpartan-Light', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')
        
        global fin_feat_product_list
        if fin_feat_product_list == 0:
            fin_feat_product_list = pdf.page_no()
        
        return 204 
        

    
    
    #//*---Function to check height of rectangle
    def get_rect_h(pdf,credit_card,main_y):
        pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(main_y+40))  
        pdf.multi_cell(px2MM(470), px2MM(42),credit_card['card_name'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+8
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card['card_type'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+34
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Annual fee',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card['annual_fee'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2

        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Eligibility',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card['eligibility'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Best suited for',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card['best_suited_for'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Best reward points (RP) conversion rate',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card['best_reward_points_conversion_rate'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        
        head_h = h_y+30
        head_h = head_h - main_y
        
        pro_y = main_y+24
        for i in range(len(credit_card['strength'])):
            if credit_card['strength'][i] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(pro_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),credit_card['strength'][i],border='0',align='L')
                pro_y = mm2PX(pdf.get_y())+16
        pro_end = mm2PX(pdf.get_y())+24
        # print(pro_end)
        pro_h = pro_end-main_y
        con_y = pro_end+24
        
        for j in range(len(credit_card['weakness'])):
            if credit_card['weakness'][j] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),credit_card['weakness'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
        con_end = mm2PX(pdf.get_y())+24
        con_h = con_end-pro_end
        card_h = pro_h+con_h

        if pro_h+con_h < head_h:
            ext_h = head_h-(pro_h+con_h)
            pro_h = pro_h+ext_h
        if card_h < head_h:
            card_h = head_h
            
        if main_y+card_h > 975:
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(126), px2MM(main_y), px2MM(1674), px2MM(card_h),'F')
            
            desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
            pdf.set_xy(px2MM(120), px2MM(1028))
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        return pro_h,con_h,card_h
        
    
    main_y = add_credit_card_page(pdf)
    for card in range(len(credit_card)):
        pro_h,con_h,card_h = get_rect_h(pdf,credit_card[card],main_y)
        
        if 1080-(main_y+card_h) <= 90:
            main_y = add_credit_card_page(pdf) 
            pro_h,con_h,card_h = get_rect_h(pdf,credit_card[card],main_y)
                
        # White rectangle
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(120), px2MM(main_y), px2MM(645), px2MM(card_h), 'F')
        
        try:
            pdf.image(credit_card[card]['feature_list_logo'],px2MM(150), px2MM(main_y+30), px2MM(102), px2MM(102))
        except Exception as e:
            print('no logo')
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(main_y+30))  
        pdf.multi_cell(px2MM(470), px2MM(42),credit_card[card]['card_name'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+8
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card[card]['card_type'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+34
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Annual fee',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card[card]['annual_fee'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2

        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Eligibility',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card[card]['eligibility'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Best suited for',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card[card]['best_suited_for'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Best reward points (RP) conversion rate',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),credit_card[card]['best_reward_points_conversion_rate'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        
        # Card of Pros
        pdf.set_fill_color(*hex2RGB('#DEF7F1'))
        pdf.rect(px2MM(765), px2MM(main_y), px2MM(1035), px2MM(pro_h), 'F')
        
        pro_y = main_y+24
        if pro_y > 0:
            pdf.image(join(cwd,'assets', 'images','feature list','Thumbsup.svg'),px2MM(1744), px2MM(main_y+24), px2MM(32), px2MM(32))
            
        for i in range(len(credit_card[card]['strength'])):
                if credit_card[card]['strength'][i] !="":
                    pdf.set_fill_color(*hex2RGB('#4B4C51'))
                    pdf.rect(px2MM(789), px2MM(pro_y+14), px2MM(8), px2MM(8), 'F')
            
                    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#1A1A1D'))
                    pdf.set_xy(px2MM(809), px2MM(pro_y))  
                    pdf.multi_cell(px2MM(900), px2MM(32),credit_card[card]['strength'][i],border='0',align='L')
                    pro_y = mm2PX(pdf.get_y())+16
        pro_end = pro_h+main_y
        con_y = pro_end+24
                
        # Card of Cons
        pdf.set_fill_color(*hex2RGB('#FFF5DA'))
        pdf.rect(px2MM(765), px2MM(pro_end), px2MM(1035), px2MM(con_h), 'F')
                
        if con_h > 0:
            pdf.image(join(cwd,'assets', 'images','feature list','Thumbsdown.svg'),px2MM(1744), px2MM(con_y), px2MM(32), px2MM(32))
        for j in range(len(credit_card[card]['weakness'])):
            if credit_card[card]['weakness'][j] !="":
                pdf.set_fill_color(*hex2RGB('#4B4C51'))
                pdf.rect(px2MM(789), px2MM(con_y+14), px2MM(8), px2MM(8), 'F')
                
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),credit_card[card]['weakness'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
                    
        main_y = main_y+card_h+40
        
        
#//*----Financial Product List (Housing Lenders)-----*//
def housing_lenders(pdf,json_data,c_MoneyS,money_signData):
    
    housing_lender = json_data["featured_list"]['housing_lenders']
    
    def add_housing_lender_page(pdf): 
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

            
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(1200), px2MM(84),'Housing Lenders',align='L')
        
        pdf.set_xy(px2MM(1489),px2MM(114)) 
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(330), px2MM(32),'Financial Products Featured List',align='L')
        
        desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
        pdf.set_xy(px2MM(120), px2MM(1028))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        #//*-----Index Text of Page--**////
        pdf.set_xy(px2MM(1870), px2MM(1018))  
        pdf.set_font('LeagueSpartan-Light', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')
        
        global fin_feat_product_list
        if fin_feat_product_list == 0:
            fin_feat_product_list = pdf.page_no()
        
        return 204 
        

    #//*---Function to check height of rectangle
    def get_rect_h(pdf,housing_lender,main_y):
        pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(main_y+40))  
        pdf.multi_cell(px2MM(470), px2MM(42),housing_lender['lender_name'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+8
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),housing_lender['best_for'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+34
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Interest Rate',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),housing_lender['interest_rate'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2

        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Processing Fees',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),housing_lender['processing_fees'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Grievance Redressal Process',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),housing_lender['grievance_redressal_process'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        
        head_h = h_y+30
        head_h = head_h - main_y
        
        pro_y = main_y+24
        for i in range(len(housing_lender['strength'])):
            if housing_lender['strength'][i] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(pro_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),housing_lender['strength'][i],border='0',align='L')
                pro_y = mm2PX(pdf.get_y())+16
        pro_end = mm2PX(pdf.get_y())+24
        # print(pro_end)
        pro_h = pro_end-main_y
        con_y = pro_end+24
        
        for j in range(len(housing_lender['weakness'])):
            if housing_lender['weakness'][j] !="":
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),housing_lender['weakness'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
        con_end = mm2PX(pdf.get_y())+24
        con_h = con_end-pro_end
        card_h = pro_h+con_h

        if pro_h+con_h < head_h:
            ext_h = head_h-(pro_h+con_h)
            pro_h = pro_h+ext_h
        if card_h < head_h:
            card_h = head_h
            
        if main_y+card_h > 975:
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(126), px2MM(main_y), px2MM(1674), px2MM(card_h),'F')
            
            desc_text = '''Disclaimer: The above featured list is based on 1 Finance's proprietary research.'''
            pdf.set_xy(px2MM(120), px2MM(1028))
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
        
        return pro_h,con_h,card_h
        
    
    main_y = add_housing_lender_page(pdf)
    for card in range(len(housing_lender)):
        pro_h,con_h,card_h = get_rect_h(pdf,housing_lender[card],main_y)
        
        if 1080-(main_y+card_h) <= 90:
            main_y = add_housing_lender_page(pdf) 
            pro_h,con_h,card_h = get_rect_h(pdf,housing_lender[card],main_y)
                
        # White rectangle
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(120), px2MM(main_y), px2MM(645), px2MM(card_h), 'F')
        
        try:
            pdf.image(housing_lender[card]['feature_list_logo'],px2MM(150), px2MM(main_y+30), px2MM(102), px2MM(102))
        except Exception as e:
            print('no logo')
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(main_y+30))  
        pdf.multi_cell(px2MM(470), px2MM(42),housing_lender[card]['lender_name'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+8
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),housing_lender[card]['best_for'],border='0',align='L')
        
        h_y = mm2PX(pdf.get_y())+34
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Interest Rate',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),housing_lender[card]['interest_rate'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2

        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Processing Fees',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())+12
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),housing_lender[card]['processing_fees'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())+12
        
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(150), px2MM(h_y))  
        pdf.multi_cell(px2MM(124), px2MM(32),'Grievance Redressal Process',border='0',align='L')
        h_y1 = mm2PX(pdf.get_y())
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(276), px2MM(h_y))  
        pdf.multi_cell(px2MM(470), px2MM(32),housing_lender[card]['grievance_redressal_process'],border='0',align='L')
        h_y2 = mm2PX(pdf.get_y())
        
        h_y = h_y1 if h_y1 > h_y2 else h_y2
        
        # Card of Pros
        pdf.set_fill_color(*hex2RGB('#DEF7F1'))
        pdf.rect(px2MM(765), px2MM(main_y), px2MM(1035), px2MM(pro_h), 'F')
        
        pro_y = main_y+24
        if pro_y > 0:
            pdf.image(join(cwd,'assets', 'images','feature list','Thumbsup.svg'),px2MM(1744), px2MM(main_y+24), px2MM(32), px2MM(32))
            
        for i in range(len(housing_lender[card]['strength'])):
                if housing_lender[card]['strength'][i] !="":
                    pdf.set_fill_color(*hex2RGB('#4B4C51'))
                    pdf.rect(px2MM(789), px2MM(pro_y+14), px2MM(8), px2MM(8), 'F')
            
                    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#1A1A1D'))
                    pdf.set_xy(px2MM(809), px2MM(pro_y))  
                    pdf.multi_cell(px2MM(900), px2MM(32),housing_lender[card]['strength'][i],border='0',align='L')
                    pro_y = mm2PX(pdf.get_y())+16
        pro_end = pro_h+main_y
        con_y = pro_end+24
                
        # Card of Cons
        pdf.set_fill_color(*hex2RGB('#FFF5DA'))
        pdf.rect(px2MM(765), px2MM(pro_end), px2MM(1035), px2MM(con_h), 'F')
                
        if con_h > 0:
            pdf.image(join(cwd,'assets', 'images','feature list','Thumbsdown.svg'),px2MM(1744), px2MM(con_y), px2MM(32), px2MM(32))
        for j in range(len(housing_lender[card]['weakness'])):
            if housing_lender[card]['weakness'][j] !="":
                pdf.set_fill_color(*hex2RGB('#4B4C51'))
                pdf.rect(px2MM(789), px2MM(con_y+14), px2MM(8), px2MM(8), 'F')
                
                pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(809), px2MM(con_y))  
                pdf.multi_cell(px2MM(900), px2MM(32),housing_lender[card]['weakness'][j],border='0',align='L')
                con_y = mm2PX(pdf.get_y())+16
                    
        main_y = main_y+card_h+40
            
            
        

def aval_tax_deduct_1(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #//*----Available Tax Deductions----*//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(641), px2MM(84),'Available Tax Deductions',align='L')
    
    pdf.set_xy(px2MM(791),px2MM(106)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(237), px2MM(32),'(as per Old Tax Regime)',align='L')
    
    
    #//*----Content----*//
    bx_height = [72,296,136,200]
    bx_x =[204,276,572,708]
    
    #//*---Table rectangle
    for i in range(4):
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.5))
        if i%2==0:
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        else:
            pdf.set_fill_color(*hex2RGB('#F3F6F9'))
        pdf.rect(px2MM(120), px2MM(bx_x[i]), px2MM(150), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(270), px2MM(bx_x[i]), px2MM(885), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(1155), px2MM(bx_x[i]), px2MM(345), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(1500), px2MM(bx_x[i]), px2MM(300), px2MM(bx_height[i]),'FD')
        
    #//*----Table heading---*//
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    
    pdf.set_xy(px2MM(140),px2MM(224)) 
    pdf.cell(px2MM(110), px2MM(32),'Section',align='L')
    
    pdf.set_xy(px2MM(290),px2MM(224)) 
    pdf.cell(px2MM(845), px2MM(32),'Income Tax Deduction on',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(224)) 
    pdf.cell(px2MM(305), px2MM(32),'Allowed Limit',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(224)) 
    pdf.cell(px2MM(260), px2MM(32),'Applicable For',align='L')
    
    #//*---COL 1 VALUE---*//
    
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    pdf.set_xy(px2MM(140),px2MM(296)) 
    pdf.cell(px2MM(110), px2MM(32),'80C',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(592)) 
    pdf.cell(px2MM(110), px2MM(32),'80CCC',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(728)) 
    pdf.cell(px2MM(110), px2MM(32),'80CCD(1)',align='L')
    
    #//*---COL 2 VALUE---*//

    cir_x = [306,407,439,471,503,535,607,838,870]
    pdf.set_fill_color(*hex2RGB('#000000'))
    for i in range(9):
        pdf.circle(x=px2MM(310), y=px2MM(cir_x[i]), r=px2MM(5), style='F')
        
    pdf.set_xy(px2MM(330),px2MM(296)) 
    pdf.multi_cell(px2MM(815), px2MM(32),'''Investment in PPF, National Saving Certificate (NSC), Sukanya Samriddhi Yojana (SSY), ULIP, ELSS, 5-year tax-saving FD, Senior Citizen Savings Scheme (SCSS), infrastructure bonds''',align='L')
    pdf.set_xy(px2MM(330),px2MM(392)) 
    pdf.multi_cell(px2MM(815), px2MM(32),'''Employee’s share of PF contribution''',align='L')    
    pdf.set_xy(px2MM(330),px2MM(424)) 
    pdf.multi_cell(px2MM(815), px2MM(32),'''Life Insurance premium payment''',align='L')
    pdf.set_xy(px2MM(330),px2MM(456)) 
    pdf.multi_cell(px2MM(815), px2MM(32),'''Children’s Tuition Fee''',align='L')
    pdf.set_xy(px2MM(330),px2MM(488)) 
    pdf.multi_cell(px2MM(815), px2MM(32),'''Principal repayment of home loan''',align='L') 
    pdf.set_xy(px2MM(330),px2MM(520)) 
    pdf.multi_cell(px2MM(815), px2MM(32),'''Stamp duty and registration charges for purchase of property.''',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(592)) 
    pdf.multi_cell(px2MM(815), px2MM(32),'''For LIC or other insurer pension annuity plan deposits from Section 10 funds (23AAB)''',align='L')
    
    pdf.set_xy(px2MM(290),px2MM(728)) 
    pdf.multi_cell(px2MM(845), px2MM(32),'''Employee contribution under section 80CCD(1) towards National Pension Scheme (NPS) account or the Atal Pension Yojana (APY) account. Maximum deduction is the lesser of:''',align='L')
    pdf.set_xy(px2MM(330),px2MM(824)) 
    pdf.multi_cell(px2MM(815), px2MM(32),'''10% of salary (for employees)''',align='L')
    pdf.set_xy(px2MM(330),px2MM(856)) 
    pdf.multi_cell(px2MM(815), px2MM(32),'''20% of gross total income (for self-employed)''',align='L')
   
    
    #//*----Column 3 Value---*//
    
    pdf.set_xy(px2MM(1175),px2MM(296)) 
    pdf.cell(px2MM(305), px2MM(32),'₹ 1.5L ',align='L')
    pdf.set_xy(px2MM(1175),px2MM(296+32)) 
    pdf.multi_cell(px2MM(315), px2MM(32),'(aggregate of sections 80CCD, 80CCC, 80C)',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(592)) 
    pdf.cell(px2MM(305), px2MM(32),'₹ 1.5L',align='L')
    pdf.set_xy(px2MM(1175),px2MM(592+32)) 
    pdf.multi_cell(px2MM(315), px2MM(32),'(aggregate of sections 80CCD, 80CCC, 80C)',align='L')
    
    
    pdf.set_xy(px2MM(1175),px2MM(728)) 
    pdf.cell(px2MM(305), px2MM(32),'₹ 1.5L',align='L')
    pdf.set_xy(px2MM(1175),px2MM(728+32)) 
    pdf.multi_cell(px2MM(315), px2MM(32),'(aggregate of sections 80CCD, 80CCC, 80C)',align='L')
    
    
    #//*---COL 4 VALUE---*//
    
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    pdf.set_xy(px2MM(1520),px2MM(296)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Individuals and HUFs',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(592)) 
    pdf.cell(px2MM(260), px2MM(32),'Individuals',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(728)) 
    pdf.cell(px2MM(260), px2MM(32),'Individuals',align='L')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    

#//*----Available Tax Deductions(Page 2)----*//

def aval_tax_deduct_2(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #//*----Available Tax Deductions----*//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(641), px2MM(84),'Available Tax Deductions',align='L')
    
    pdf.set_xy(px2MM(791),px2MM(106)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(237), px2MM(32),'(as per Old Tax Regime)',align='L')
    
    
    #//*----Content----*//
    # bx_height = [72,72,72,72,104,200,104,72]
    # bx_x =[204,276,348,420,492,596,796,900]
    
    bx_height = [72,232,72,104,168,168]
    bx_x =[204,276,508,580,684,852]
    
    #//*---Table rectangle
    for i in range(6):
        pdf.set_line_width(px2MM(0.5))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        if i%2==0:
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        else:
            pdf.set_fill_color(*hex2RGB('#F3F6F9'))
            
        pdf.rect(px2MM(120), px2MM(bx_x[i]), px2MM(150), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(270), px2MM(bx_x[i]), px2MM(885), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(1155), px2MM(bx_x[i]), px2MM(345), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(1500), px2MM(bx_x[i]), px2MM(300), px2MM(bx_height[i]),'FD')
        
    #//*----Table heading---*//
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    
    pdf.set_xy(px2MM(140),px2MM(224)) 
    pdf.cell(px2MM(110), px2MM(32),'Section',align='L')
    
    pdf.set_xy(px2MM(290),px2MM(224)) 
    pdf.cell(px2MM(845), px2MM(32),'Income Tax Deduction on',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(224)) 
    pdf.cell(px2MM(305), px2MM(32),'Allowed Limit',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(224)) 
    pdf.cell(px2MM(260), px2MM(32),'Applicable For',align='L')  
    
    #//*---COL 1 VALUE---*//
    
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    pdf.set_xy(px2MM(140),px2MM(296)) 
    pdf.cell(px2MM(110), px2MM(32),'80CCD (2)',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(528)) 
    pdf.cell(px2MM(110), px2MM(32),'80CCD(1B)',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(600)) 
    pdf.cell(px2MM(110), px2MM(32),'80CCH',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(704)) 
    pdf.cell(px2MM(110), px2MM(32),'80D',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(872)) 
    pdf.cell(px2MM(110), px2MM(32),'80DD',align='L')
    

    
    
    # #//*---COL 2 VALUE---*//
    
    cir_x = [311,542,614,716,749,950,982]
    pdf.set_fill_color(*hex2RGB('#000000'))
    for i in range(len(cir_x)):
        pdf.circle(x=px2MM(310), y=px2MM(cir_x[i]), r=px2MM(6), style='F')

    pdf.set_xy(px2MM(330),px2MM(296)) 
    pdf.cell(px2MM(805), px2MM(32),'Employer contribution to NPS account',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(528)) 
    pdf.cell(px2MM(805), px2MM(32),'Additional contribution to NPS',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(600)) 
    pdf.cell(px2MM(805), px2MM(32),'Contribution to Agniveer corpus fund (applicable from Nov 2022)',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(704)) 
    pdf.cell(px2MM(805), px2MM(32),'Medical Insurance – self, spouse, children',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(736)) 
    pdf.cell(px2MM(805), px2MM(32),'Medical Insurance – parents',align='L')
    
    pdf.set_xy(px2MM(290),px2MM(872)) 
    pdf.multi_cell(px2MM(845), px2MM(32),'Medical treatment for handicapped dependents or payment to specified scheme for maintenance of handicapped dependent.',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(936)) 
    pdf.cell(px2MM(805), px2MM(32),'Disability is 40% or more but less than 80%',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(968)) 
    pdf.cell(px2MM(805), px2MM(32),'Disability is 80% or more',align='L')
    
    #//*---COL 3 VALUE---*//
    
    cir_x = [342,404,717,749,885,915]
    pdf.set_fill_color(*hex2RGB('#000000'))
    for i in range(len(cir_x)):
        pdf.circle(x=px2MM(1195), y=px2MM(cir_x[i]), r=px2MM(6), style='F')

    pdf.set_xy(px2MM(1175),px2MM(296)) 
    pdf.cell(px2MM(305), px2MM(32),'Maximum up to:',align='L')


    pdf.set_xy(px2MM(1215),px2MM(328))
    pdf.multi_cell(px2MM(300), px2MM(32),'14% of basic salary (for Central Govt. employees)',align='L')

    pdf.set_xy(px2MM(1215),px2MM(392)) 
    pdf.multi_cell(px2MM(265), px2MM(32),'10% of basic salary (for other employees)',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(456)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'(Max ₹ 7.5 lacs per year)',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(532)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'₹ 50K',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(600)) 
    pdf.cell(px2MM(305), px2MM(32),'No limit',align='L')
    
    pdf.set_xy(px2MM(1215),px2MM(704)) 
    pdf.cell(px2MM(265), px2MM(32),'₹ 25K',align='L')
    
    pdf.set_xy(px2MM(1215),px2MM(736)) 
    pdf.multi_cell(px2MM(265), px2MM(32),'₹ 25K (parents <60 years) & ₹ 50K (parents >=60 years)',align='L')
    
    pdf.set_xy(px2MM(1215),px2MM(872)) 
    pdf.multi_cell(px2MM(265), px2MM(32),'₹ 75K',align='L')
    pdf.set_xy(px2MM(1215),px2MM(904)) 
    pdf.cell(px2MM(265), px2MM(32),'₹ 1.25L',align='L')
    
    # #//*---COL 4 VALUE---*//

    pdf.set_xy(px2MM(1520),px2MM(296)) 
    pdf.cell(px2MM(260), px2MM(32),'Individuals',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(528)) 
    pdf.cell(px2MM(260), px2MM(32),'Individuals',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(600)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Individuals enrolled in Agneepath scheme',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(704)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Individuals and HUFs',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(872)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'individuals and HUFs who have a handicapped dependent',align='L')
    
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    
#//*----Available Tax Deductions(Page 3)----*// 
def aval_tax_deduct_3(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #//*----Available Tax Deductions----*//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(641), px2MM(84),'Available Tax Deductions',align='L')
    
    pdf.set_xy(px2MM(791),px2MM(106)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(237), px2MM(32),'(as per Old Tax Regime)',align='L')
    
    
    #//*----Content----*//
    bx_height = [72,168,104,104,136,104,104]
    bx_x =[204,276,444,548,652,788,892]
    
    #//*---Table rectangle
    for i in range(len(bx_x)):
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.5))
        if i%2==0:
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        else:
            pdf.set_fill_color(*hex2RGB('#F3F6F9'))
            
        pdf.rect(px2MM(120), px2MM(bx_x[i]), px2MM(150), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(270), px2MM(bx_x[i]), px2MM(885), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(1155), px2MM(bx_x[i]), px2MM(345), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(1500), px2MM(bx_x[i]), px2MM(300), px2MM(bx_height[i]),'FD')
        
    #//*----Table heading---*//
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    
    pdf.set_xy(px2MM(140),px2MM(224)) 
    pdf.cell(px2MM(110), px2MM(32),'Section',align='L')
    
    pdf.set_xy(px2MM(290),px2MM(224)) 
    pdf.cell(px2MM(845), px2MM(32),'Income Tax Deduction on',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(224)) 
    pdf.cell(px2MM(305), px2MM(32),'Allowed Limit',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(224))
    pdf.cell(px2MM(260), px2MM(32),'Applicable For',align='L')    
    
    #//*---COL 1 VALUE---*//
    
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    pdf.set_xy(px2MM(140),px2MM(296)) 
    pdf.cell(px2MM(110), px2MM(32),'80DDB',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(464)) 
    pdf.cell(px2MM(110), px2MM(32),'80E',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(600)) 
    pdf.cell(px2MM(110), px2MM(32),'80EE',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(672)) 
    pdf.cell(px2MM(110), px2MM(32),'80EEA',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(808)) 
    pdf.cell(px2MM(110), px2MM(32),'80EEB',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(912)) 
    pdf.cell(px2MM(110), px2MM(32),'80G',align='L')
    
    #//*---COL 2 VALUE---*//
    cir_x = (342,374,478,582,686,822,926)
    pdf.set_fill_color(*hex2RGB('#000000'))
    for i in range(len(cir_x)):
        pdf.circle(x=px2MM(310), y=px2MM(cir_x[i]), r=px2MM(6), style='F')
    
    pdf.set_xy(px2MM(290),px2MM(296)) 
    pdf.multi_cell(px2MM(855), px2MM(32),'Medical expenditure on self or dependent relative for diseases specified in rule 11DD:',align='L')
    pdf.set_xy(px2MM(330),px2MM(296+32)) 
    pdf.cell(px2MM(805), px2MM(32),'For less than 60 years old',align='L')
    pdf.set_xy(px2MM(330),px2MM(296+64)) 
    pdf.cell(px2MM(805), px2MM(32),'For more than 60 years old',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(464)) 
    pdf.multi_cell(px2MM(805), px2MM(32),'''Interest on education loan''',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(568)) 
    pdf.multi_cell(px2MM(805), px2MM(32),'''Interest on home loan for first-time homeowners, available for loans sanctioned between 01-Apr-2016 and 31-Mar-2017''',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(672)) 
    pdf.multi_cell(px2MM(805), px2MM(32),'''Interest on home loan (over and above Rs. 2,00,000 deduction under 24B, allowing taxpayers to deduct total of Rs. 3,50,000 for interest on home loan) for loans sanctioned between 01-Apr-2019 and 31-Mar-2022''',align='L')
    
    
    pdf.set_xy(px2MM(330),px2MM(808)) 
    pdf.multi_cell(px2MM(805), px2MM(32),'''Interest on  loan taken between 01-Apr-2019 and 31-Mar-2023 for purchase of electric vehicle''',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(912)) 
    pdf.multi_cell(px2MM(805), px2MM(32),'''Contributions to certain relief funds and charitable institutions''',align='L')
    

    #//*---COL 3 VALUE---*//
    cir_x = (310,374)
    pdf.set_fill_color(*hex2RGB('#000000'))
    for i in range(len(cir_x)):
        pdf.circle(x=px2MM(1195), y=px2MM(cir_x[i]), r=px2MM(6), style='F')
        
    pdf.set_xy(px2MM(1215),px2MM(296)) 
    pdf.multi_cell(px2MM(265), px2MM(32),'Lower of ₹ 40K or amount actually paid',align='L')
    pdf.set_xy(px2MM(1215),px2MM(360)) 
    pdf.multi_cell(px2MM(265), px2MM(32),'Lower of ₹ 1L or amount actually paid',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(464)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'Interest paid for a period of 8 years',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(568)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'₹ 50K',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(672)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'₹ 1.5L',align='L')

    pdf.set_xy(px2MM(1175),px2MM(808)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'₹ 1.5L',align='L')

    pdf.set_xy(px2MM(1175),px2MM(912)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'50% or 100% of the donation amount can be claimed.',align='L')

    
    #//*---COL 4 VALUE---*//
    
    pdf.set_xy(px2MM(1520),px2MM(296)) 
    pdf.cell(px2MM(260), px2MM(32),'Individuals and HUFs',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(464)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Individuals',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(568)) 
    pdf.cell(px2MM(260), px2MM(32),'Individuals',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(672)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Individuals',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(808)) 
    pdf.cell(px2MM(260), px2MM(32),'Individuals',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(912)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Individuals, HUFs, companies',align='L')

    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    
#//*----Available Tax Deductions(Page 4)----*// 
def aval_tax_deduct_4(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #//*----Available Tax Deductions----*//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(641), px2MM(84),'Available Tax Deductions',align='L')
    
    pdf.set_xy(px2MM(791),px2MM(106)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(237), px2MM(32),'(as per Old Tax Regime)',align='L')
    
    
    #//*----Content----*//
    bx_height = [72,200,136,104,104,104,104]
    bx_x =[204,276,476,612,716,820,924]
    
    #//*---Table rectangle
    for i in range(len(bx_x)):
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.5))
        if i%2==0:
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        else:
            pdf.set_fill_color(*hex2RGB('#F3F6F9'))
            
        pdf.rect(px2MM(120), px2MM(bx_x[i]), px2MM(150), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(270), px2MM(bx_x[i]), px2MM(885), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(1155), px2MM(bx_x[i]), px2MM(345), px2MM(bx_height[i]),'FD')
        pdf.rect(px2MM(1500), px2MM(bx_x[i]), px2MM(300), px2MM(bx_height[i]),'FD')
        
    #//*----Table heading---*//
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    
    pdf.set_xy(px2MM(140),px2MM(224)) 
    pdf.cell(px2MM(110), px2MM(32),'Section',align='L')
    
    pdf.set_xy(px2MM(290),px2MM(224)) 
    pdf.cell(px2MM(845), px2MM(32),'Income Tax Deduction on',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(224)) 
    pdf.cell(px2MM(305), px2MM(32),'Allowed Limit',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(224))
    pdf.cell(px2MM(260), px2MM(32),'Applicable For',align='L')    
    
    #//*---COL 1 VALUE---*//
    
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    pdf.set_xy(px2MM(140),px2MM(296)) 
    pdf.cell(px2MM(110), px2MM(32),'80GG',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(528)) 
    pdf.cell(px2MM(110), px2MM(32),'80GGA',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(632)) 
    pdf.cell(px2MM(110), px2MM(32),'80GGC',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(736)) 
    pdf.cell(px2MM(110), px2MM(32),'80RRB',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(840)) 
    pdf.cell(px2MM(110), px2MM(32),'80TTA (1)',align='L')
    
    pdf.set_xy(px2MM(140),px2MM(944)) 
    pdf.cell(px2MM(110), px2MM(32),'80TTB',align='L')
    
    #//*---COL 2 VALUE---*//
    cir_x = (310,510,646,750,854,958)
    pdf.set_fill_color(*hex2RGB('#000000'))
    for i in range(len(cir_x)):
        pdf.circle(x=px2MM(310), y=px2MM(cir_x[i]), r=px2MM(6), style='F')
    
    
    pdf.set_xy(px2MM(330),px2MM(296)) 
    pdf.cell(px2MM(805), px2MM(32),'For rent paid when HRA is not received from an employer',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(496)) 
    pdf.multi_cell(px2MM(805), px2MM(32),"""Donation for scientific, social science,  research, or rural development to specific universities, colleges or research association""",align='L')
    
    pdf.set_xy(px2MM(330),px2MM(632)) 
    pdf.multi_cell(px2MM(805), px2MM(32),'''Contribution by individuals to political parties''',align='L')
    
    pdf.set_xy(px2MM(330),px2MM(736)) 
    pdf.multi_cell(px2MM(805), px2MM(32),'''Royalty on patents''',align='L')

    pdf.set_xy(px2MM(330),px2MM(840)) 
    pdf.multi_cell(px2MM(805), px2MM(32),'''Interest income from savings account''',align='L')

    pdf.set_xy(px2MM(330),px2MM(940)) 
    pdf.multi_cell(px2MM(805), px2MM(32),'''Exemption of interest from banks, post offices, etc.''',align='L')
    
    #//*---COL 3 VALUE---*//
    cir_x = (342,406,438)
    pdf.set_fill_color(*hex2RGB('#000000'))
    for i in range(len(cir_x)):
        pdf.circle(x=px2MM(1195), y=px2MM(cir_x[i]), r=px2MM(6), style='F')
        
    pdf.set_xy(px2MM(1175),px2MM(296)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'Least of:',align='L')    
    pdf.set_xy(px2MM(1215),px2MM(328)) 
    pdf.multi_cell(px2MM(265), px2MM(32),'Rent paid minus 10% of total income',align='L')
    pdf.set_xy(px2MM(1215),px2MM(392)) 
    pdf.multi_cell(px2MM(265), px2MM(32),'₹ 5K per month',align='L')
    pdf.set_xy(px2MM(1215),px2MM(424)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'25% of total income',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(496)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'No limit',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(632)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'Amount contributed (not allowed if paid in cash)',align='L')

    pdf.set_xy(px2MM(1175),px2MM(736)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'₹ 3L',align='L')

    pdf.set_xy(px2MM(1175),px2MM(840)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'₹ 10K',align='L')
    
    pdf.set_xy(px2MM(1175),px2MM(944)) 
    pdf.multi_cell(px2MM(305), px2MM(32),'Maximum up to ₹ 50K',align='L')

    
    #//*---COL 4 VALUE---*//
    
    pdf.set_xy(px2MM(1520),px2MM(296)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Individuals not receiving HRA',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(496)) 
    pdf.multi_cell(px2MM(275), px2MM(32),'All individuals except those having Income from business and profession',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(632)) 
    pdf.cell(px2MM(260), px2MM(32),'Individuals',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(736)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Resident individual who is a patentee',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(840)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Individuals and HUFs (except senior citizens)',align='L')
    
    pdf.set_xy(px2MM(1520),px2MM(944)) 
    pdf.multi_cell(px2MM(260), px2MM(32),'Senior citizens (above 60 years)',align='L')

    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    
def aval_tax_deduct_5(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    pdf.set_xy(px2MM(791),px2MM(106)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(237), px2MM(32),'(as per Old Tax Regime)',align='L')

    pdf.set_draw_color(*hex2RGB('#E9EAEE'))

    #//----Availablel Tax Deductions 1st Page----//
    #//----Headings----//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(641), px2MM(84),'Available Tax Deductions',align='L')

    # Section
    
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.rect(px2MM(120), px2MM(204), px2MM(150), px2MM(72),'FD')
    pdf.set_xy(px2MM(140),px2MM(224))
    pdf.cell(px2MM(110), px2MM(32),"Section",align='L')

    # Section Col Values
    vals = ['80U','24B','10(13A)','10(5)']
    rect_top = [276,412,484,716]
    rect_height = [136,72,232,264]
    set_xy_top = [296,432,504,736]


    for i in range(len(vals)):
        fill_color = "#FFFFFF" if i % 2 != 0 else '#F3F6F9'
        pdf.set_fill_color(*hex2RGB(fill_color))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.rect(px2MM(120), px2MM(rect_top[i]), px2MM(150), px2MM(rect_height[i]),'FD')
        pdf.set_xy(px2MM(140),px2MM(set_xy_top[i]))
        pdf.cell(px2MM(150), px2MM(32),vals[i],align='L')
    pdf.set_fill_color(*hex2RGB('#FFFFFF')) # Set Fill Color Back To White
    

    # Income Tax Deduction on
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.rect(px2MM(270), px2MM(204), px2MM(885), px2MM(72),'FD')
    pdf.set_xy(px2MM(290),px2MM(224))
    pdf.cell(px2MM(845), px2MM(32),"Income Tax Deduction on",align='L')


    vals = ["Individual suffering from physical disability (including blindness) or mental retardation",
            "Individual suffering from severe disability"]
    for i in range(4):
        fill_color = "#FFFFFF" if i % 2 != 0 else '#F3F6F9'
        pdf.set_fill_color(*hex2RGB(fill_color))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.rect(px2MM(270), px2MM(rect_top[i]), px2MM(885), px2MM(rect_height[i]),'FD')
    pdf.set_fill_color(*hex2RGB('#FFFFFF')) # Set Fill Color Back To White

    pdf.set_fill_color(*hex2RGB('#000000'))
    # Kaala Timba
    pdf.circle(x=px2MM(290+5), y=px2MM(296 + 20), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(290 + 20),px2MM(296+5))
    pdf.multi_cell(px2MM(810), px2MM(32),vals[0],align='L')

    pdf.circle(x=px2MM(290+5), y=px2MM(296 + 64 + 20), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(290 + 20),px2MM(296 + 64 + 5))
    pdf.multi_cell(px2MM(810), px2MM(32),vals[1],align='L')

    
    # Tab 2
    val = ["Tax exemption on interest paid on home loan"]
    pdf.circle(x=px2MM(290+5), y=px2MM(432 + 20), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(290 + 20),px2MM(432 + 5)) 
    pdf.multi_cell(px2MM(810), px2MM(32),val[0],align='L')
    
    val = ["House Rent Allowance (HRA)"]
    pdf.circle(x=px2MM(290+5), y=px2MM(504 + 20), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(290 + 20),px2MM(504 + 5)) 
    pdf.multi_cell(px2MM(810), px2MM(32),val[0],align='L')


    # Tab 3
    # Val 1
    val = "Leave Travel Allowance (LTA)"
    pdf.circle(x=px2MM(290+5), y=px2MM(736 + 20), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(290 + 20),px2MM(736+5))    
    pdf.multi_cell(px2MM(810), px2MM(32),val,align='L')

    pdf.set_fill_color(*hex2RGB('#FFFFFF')) # Set Fill Color Back To White


    # Allowed Limit
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.rect(px2MM(1155), px2MM(204), px2MM(345), px2MM(72),'FD')
    pdf.set_xy(px2MM(1175),px2MM(224))
    pdf.cell(px2MM(260), px2MM(32),"Allowed Limit",align='L')

    # Allowed Limit Vals 
    for i in range(4):
        fill_color = "#FFFFFF" if i % 2 != 0 else '#F3F6F9'
        pdf.set_fill_color(*hex2RGB(fill_color))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.rect(px2MM(1155), px2MM(rect_top[i]), px2MM(345), px2MM(rect_height[i]),'FD')
        # pdf.set_xy(px2MM(1175),px2MM(set_xy_top[i]))
        # pdf.multi_cell(px2MM(305), px2MM(32),vals[i],align='L')
    pdf.set_fill_color(*hex2RGB('#FFFFFF')) # Set Fill Color Back To White
    pdf.set_fill_color(*hex2RGB('#000000'))


    vals = ["₹ 75K","₹ 1.25L"]
    # Kaala Timba
    # pdf.circle(x=px2MM(1175+5), y=px2MM(296 + 20), r=px2MM(5), style='F')
    pdf.circle(x=px2MM(1175+10), y=px2MM(296 + 20), r=px2MM(5), style='F')
    # pdf.set_xy(px2MM(1175 + 20),px2MM(296+5))
    pdf.set_xy(px2MM(1175 + 25),px2MM(296+5))
    pdf.multi_cell(px2MM(810), px2MM(32),vals[0],align='L')
    
    pdf.circle(x=px2MM(1175 + 10), y=px2MM(296 + 32 +20), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(1175 + 25),px2MM(296+ 32 +5))
    pdf.multi_cell(px2MM(810), px2MM(32),vals[1],align='L')
    
    # Tab 3
    # pdf.set_xy(px2MM(1175 + 20),px2MM(432))
    pdf.set_xy(px2MM(1175 + 5),px2MM(432))
    pdf.multi_cell(px2MM(810), px2MM(32),"₹ 2L",align='L')


    # Tab 3
    pdf.set_xy(px2MM(1175 + 5),px2MM(504))
    pdf.multi_cell(px2MM(810), px2MM(32),"Least of:",align='L')

    # Point 2
    pdf.circle(x=px2MM(1175+10), y=px2MM(504 + 32 +20), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(1175 + 25),px2MM(504 + 32 + 5))
    pdf.multi_cell(px2MM(810), px2MM(32),"Actual HRA received",align='L')
    
    # Point 3
    pdf.circle(x=px2MM(1175+10), y=px2MM(504 + 32 + 32 + 20), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(1175 + 25),px2MM(504 + 32 +32 + 5))
    pdf.multi_cell(px2MM(305), px2MM(32),"40%/50% of Basic+DA for non-metro/ metro city",align='L')
    
    
    # Point 4
    pdf.circle(x=px2MM(1175+10), y=px2MM(504 + 32 + 32 + 64 + 20), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(1175 + 25),px2MM(504 + 32 + 32 + 64 + 5))
    pdf.multi_cell(px2MM(305), px2MM(32),"Actual rent paid minus 10% \nof Basic+DA",align='L')


    # Tab 4
    # Point 1
    val = "Only for self/family's domestic travel by train \n(max upto 1st class AC \nFare by shortest route) or flight (max upto economy class fare)"
    val2 = "Allowed 2 times in 4 years"

    pdf.circle(x=px2MM(1175+10), y=px2MM(736 + 20 - 5), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(1175 + 25),px2MM(736 + 5 - 5))
    pdf.multi_cell(px2MM(305), px2MM(32),val,align='L')
    
    # Point 2
    pdf.circle(x=px2MM(1175+10), y=px2MM(736 + 216 - 5), r=px2MM(5), style='F')
    pdf.set_xy(px2MM(1175 + 25),px2MM(736 + 198 + 5 - 5))
    pdf.multi_cell(px2MM(305), px2MM(32),val2,align='L')


    
    pdf.set_fill_color(*hex2RGB('#FFFFFF')) # Set Fill Color Back To White
    # Applicable For
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.rect(px2MM(1500), px2MM(204), px2MM(300), px2MM(72),'FD')
    pdf.set_xy(px2MM(1520),px2MM(224))
    pdf.cell(px2MM(269), px2MM(32),"Allowed Limit",align='L')

    # Applicable For Values
    # vals = ['Individuals and HUFs','Individuals','Individuals']
    for i in range(4):
        fill_color = "#FFFFFF" if i % 2 != 0 else '#F3F6F9'
        pdf.set_fill_color(*hex2RGB(fill_color))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.rect(px2MM(1500), px2MM(rect_top[i]), px2MM(300), px2MM(rect_height[i]),'FD')
        # pdf.set_xy(px2MM(1520),px2MM(set_xy_top[i]))
        # pdf.cell(px2MM(260), px2MM(32),"Hello World",align='L')
    pdf.set_fill_color(*hex2RGB('#FFFFFF')) # Set Fill Color Back To White

    # Tab 1

    set_xy_top = [296,432,504,736]

    pdf.set_xy(px2MM(1520 + 5),px2MM(296))
    pdf.multi_cell(px2MM(260), px2MM(32),"Individuals with disabilities",align='L')
    
    pdf.set_xy(px2MM(1520 + 5),px2MM(432))
    pdf.multi_cell(px2MM(260), px2MM(32),"Individuals",align='L')

    pdf.set_xy(px2MM(1520 + 5),px2MM(504))
    pdf.multi_cell(px2MM(260), px2MM(32),"Individual receiving HRA from employer",align='L')
    
    pdf.set_xy(px2MM(1520 + 5),px2MM(736))
    pdf.multi_cell(px2MM(260), px2MM(32),"Individual receiving LTA from employer",align='L')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
 
 
 
 
#//*----Capital Gains Taxation by Asset Type (Page 1)-----*//   
 
def capital_gains_1(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
    
    # black rectangle
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

    #//*----Headings----//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(960), px2MM(84),'Capital Gains Taxation by Asset Type',align='L')
    
    #//*---Black vertical line--*-//
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(204), px2MM(6), px2MM(414),'F')
    
    pdf.rect(px2MM(126), px2MM(204), px2MM(100), px2MM(42),'F')
    pdf.set_xy(px2MM(141),px2MM(209)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(80), px2MM(32),'Equity',align='L')
    
    
    #//*----Equity Table-----------------*//
    #//*---Columns---*//
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(126), px2MM(246), px2MM(457), px2MM(104),'FD')
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(146),px2MM(266)) 
    pdf.cell(px2MM(80), px2MM(64),'Asset Type',align='L')
    
    pdf.rect(px2MM(583), px2MM(246), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(256)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Long-term Capital Gains (LTCG)',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(246), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(256)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Short-term Capital Gains (STCG)',align='C')
    
    pdf.rect(px2MM(583), px2MM(298), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(308)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(772), px2MM(298), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(792),px2MM(308)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(298), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(308)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(298), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(308)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    #//*----Row 1(1/1)----*//
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.rect(px2MM(126), px2MM(350), px2MM(240), px2MM(144),'FD')
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_xy(px2MM(146),px2MM(406)) 
    pdf.cell(px2MM(210), px2MM(32),'Domestic shares',align='L')
    
    pdf.rect(px2MM(366), px2MM(350), px2MM(217), px2MM(72),'FD')
    pdf.set_xy(px2MM(386),px2MM(370)) 
    pdf.cell(px2MM(177), px2MM(32),'Listed',align='L')
    
    pdf.rect(px2MM(583), px2MM(350), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(603),px2MM(370)) 
    pdf.cell(px2MM(155), px2MM(32),'> 1 year',align='C')
    
    pdf.rect(px2MM(772), px2MM(350), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(792),px2MM(370)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5% on LTCG > ₹ 1.25 lakh/year',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(350), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(370)) 
    pdf.cell(px2MM(155), px2MM(32),'< 1 year',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(350), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(370)) 
    pdf.cell(px2MM(379.5), px2MM(32),'20%',align='C')
    
    #//*--row (1/2)---*//
    pdf.rect(px2MM(366), px2MM(422), px2MM(217), px2MM(72),'FD')
    pdf.set_xy(px2MM(386),px2MM(442)) 
    pdf.cell(px2MM(177), px2MM(32),'Unlisted',align='L')
    
    pdf.rect(px2MM(583), px2MM(422), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(603),px2MM(442)) 
    pdf.cell(px2MM(155), px2MM(32),'> 2 years',align='C')
    
    pdf.rect(px2MM(772), px2MM(422), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(792),px2MM(442)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5%',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(422), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(442)) 
    pdf.cell(px2MM(155), px2MM(32),'< 2 years',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(422), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(442)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    #//*--row (2)---*//
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(126), px2MM(494), px2MM(457), px2MM(62),'FD')
    pdf.set_xy(px2MM(146),px2MM(509)) 
    pdf.cell(px2MM(366), px2MM(32),'Equity mutual funds',align='L')
    
    pdf.rect(px2MM(583), px2MM(494), px2MM(189), px2MM(62),'FD')
    pdf.set_xy(px2MM(603),px2MM(509)) 
    pdf.cell(px2MM(155), px2MM(32),'> 1 year',align='C')
    
    pdf.rect(px2MM(772), px2MM(494), px2MM(419.5), px2MM(62),'FD')
    pdf.set_xy(px2MM(792),px2MM(509)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5% on LTCG > ₹ 1.25 lakh/year',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(494), px2MM(189), px2MM(62),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(509)) 
    pdf.cell(px2MM(155), px2MM(32),'< 1 year',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(494), px2MM(419.5), px2MM(62),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(509)) 
    pdf.cell(px2MM(379.5), px2MM(32),'20%',align='C')
    
    #//*--row (3)---*//
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.rect(px2MM(126), px2MM(556), px2MM(457), px2MM(62),'FD')
    pdf.set_xy(px2MM(146),px2MM(571)) 
    pdf.cell(px2MM(366), px2MM(32),'Foreign shares',align='L')
    
    pdf.rect(px2MM(583), px2MM(556), px2MM(189), px2MM(62),'FD')
    pdf.set_xy(px2MM(603),px2MM(571)) 
    pdf.cell(px2MM(155), px2MM(32),'> 2 years',align='C')
    
    pdf.rect(px2MM(772), px2MM(556), px2MM(419.5), px2MM(62),'FD')
    pdf.set_xy(px2MM(792),px2MM(571)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5%',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(556), px2MM(189), px2MM(62),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(571)) 
    pdf.cell(px2MM(155), px2MM(32),'< 2 years',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(556), px2MM(419.5), px2MM(62),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(571)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    
    #//*----Real Estate Table-----------------*//
    #//*---Black vertical line--*-//
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(658), px2MM(6), px2MM(208),'F')
    
    pdf.rect(px2MM(126), px2MM(658), px2MM(147), px2MM(42),'F')
    pdf.set_xy(px2MM(141),px2MM(663)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(120), px2MM(32),'Real Estate',align='L')
    
    
    #//*---Columns---*//
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(126), px2MM(700), px2MM(457), px2MM(104),'FD')
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(146),px2MM(720)) 
    pdf.cell(px2MM(80), px2MM(64),'Asset Type',align='L')
    
    pdf.rect(px2MM(583), px2MM(700), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(710)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Long-term Capital Gains (LTCG)',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(700), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(710)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Short-term Capital Gains (STCG)',align='C')
    
    pdf.rect(px2MM(583), px2MM(752), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(762)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(772), px2MM(752), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(792),px2MM(762)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(752), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(762)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(752), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(762)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    #//*--row (1)---*//
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    pdf.rect(px2MM(126), px2MM(804), px2MM(457), px2MM(62),'FD')
    pdf.set_xy(px2MM(146),px2MM(819)) 
    pdf.cell(px2MM(366), px2MM(32),'Residential/commercial',align='L')
    
    pdf.rect(px2MM(583), px2MM(804), px2MM(189), px2MM(62),'FD')
    pdf.set_xy(px2MM(603),px2MM(819)) 
    pdf.cell(px2MM(155), px2MM(32),'> 2 years',align='C')
    
    pdf.rect(px2MM(772), px2MM(804), px2MM(419.5), px2MM(62),'FD')
    pdf.set_xy(px2MM(792),px2MM(819)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5%',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(804), px2MM(189), px2MM(62),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(819)) 
    pdf.cell(px2MM(155), px2MM(32),'< 2 years',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(804), px2MM(419.5), px2MM(62),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(819)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    desc_list = ["Capital gains tax exemptions under the Income Tax Act:","1. Section 112A (Grandfather provision): Exempts LTCG tax on equity shares/units bought before 31st January 2018, adjusting the cost to the values as of 1st February 2018.","2. Section 54: Allows tax exemption on LTCG from the sale of a house, provided capital gains are reinvested in a new residential property.","3. Section 54EC: Offers tax exemption on gains when proceeds from housing property sales are reinvested in specific bonds issued by NHAI or REC.","4. Section 54F: Grants tax exemption on gains from the sale of long-term capital assets other than house property, when sales proceeds are reinvested in a new residential property."]
    
    for i in range(len(desc_list)):
        pdf.set_font('LeagueSpartan-Light', size=px2pts(18))
        pdf.set_xy(px2MM(120),px2MM(906+(i*25))) 
        pdf.cell(px2MM(1680), px2MM(25),desc_list[i],align='L')
        
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
          
    
#//*----Capital Gains Taxation by Asset Type (Page 2)-----*//  
 
def capital_gains_2(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
    
    # black rectangle
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

    #//*----Headings----//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(960), px2MM(84),'Capital Gains Taxation by Asset Type',align='L')
    
    #//*---Black vertical line--*-//
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(204), px2MM(6), px2MM(362),'F')
    
    pdf.rect(px2MM(126), px2MM(204), px2MM(80), px2MM(42),'F')
    pdf.set_xy(px2MM(141),px2MM(209)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(70), px2MM(32),'Debt',align='L')
    
    
    #//*----Debt Table-----------------*//
    #//*---Columns---*//
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(126), px2MM(246), px2MM(457), px2MM(104),'FD')
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(146),px2MM(266)) 
    pdf.cell(px2MM(80), px2MM(64),'Asset Type',align='L')
    
    pdf.rect(px2MM(583), px2MM(246), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(256)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Long-term Capital Gains (LTCG)',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(246), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(256)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Short-term Capital Gains (STCG)',align='C')
    
    pdf.rect(px2MM(583), px2MM(298), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(308)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(772), px2MM(298), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(792),px2MM(308)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(298), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(308)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(298), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(308)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    
    #//*--row (1)---*//
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    pdf.rect(px2MM(126), px2MM(350), px2MM(457), px2MM(72),'FD')
    pdf.set_xy(px2MM(146),px2MM(370)) 
    pdf.cell(px2MM(417), px2MM(32),'Debt mutual funds',align='L')
    
    pdf.rect(px2MM(583), px2MM(350), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(603),px2MM(370)) 
    pdf.cell(px2MM(155), px2MM(32),'Any',align='C')
    
    pdf.rect(px2MM(772), px2MM(350), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(792),px2MM(370)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(350), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(370)) 
    pdf.cell(px2MM(155), px2MM(32),'Any',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(350), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(370)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    #//*--row (2)---*//
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    pdf.rect(px2MM(126), px2MM(422), px2MM(457), px2MM(72),'FD')
    pdf.set_xy(px2MM(146),px2MM(442)) 
    pdf.cell(px2MM(417), px2MM(32),'Listed/Zero coupon bonds',align='L')
    
    pdf.rect(px2MM(583), px2MM(422), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(603),px2MM(442)) 
    pdf.cell(px2MM(155), px2MM(32),'> 1 year',align='C')
    
    pdf.rect(px2MM(772), px2MM(422), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(792),px2MM(442)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5%',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(422), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(442)) 
    pdf.cell(px2MM(155), px2MM(32),'< 1 year',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(422), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(442)) 
    pdf.cell(px2MM(379.5), px2MM(32),'20%',align='C')
    
    #//*--row (3)---*//
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    
    pdf.rect(px2MM(126), px2MM(494), px2MM(457), px2MM(72),'FD')
    pdf.set_xy(px2MM(146),px2MM(514)) 
    pdf.cell(px2MM(417), px2MM(32),'Unlisted bonds',align='L')
    
    pdf.rect(px2MM(583), px2MM(494), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(603),px2MM(514)) 
    pdf.cell(px2MM(155), px2MM(32),'> 2 years',align='C')
    
    pdf.rect(px2MM(772), px2MM(494), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(792),px2MM(514)) 
    pdf.multi_cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(494), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(514)) 
    pdf.cell(px2MM(155), px2MM(32),'< 2 years',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(494), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(514)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    
    #//*---Black vertical line--*-//
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(204), px2MM(6), px2MM(362),'F')
    
    pdf.rect(px2MM(126), px2MM(204), px2MM(80), px2MM(42),'F')
    pdf.set_xy(px2MM(141),px2MM(209)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(70), px2MM(32),'Debt',align='L')
    
    
    #//*----Passive Income Assets Table-----------------*//
    #//*---Black vertical line--*-//
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(638), px2MM(6), px2MM(218),'F')
    
    pdf.rect(px2MM(126), px2MM(638), px2MM(257), px2MM(42),'F')
    pdf.set_xy(px2MM(141),px2MM(643)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(250), px2MM(32),'Passive Income Assets',align='L')
    
    #//*---Columns---*//
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(126), px2MM(680), px2MM(457), px2MM(104),'FD')
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(146),px2MM(700)) 
    pdf.cell(px2MM(80), px2MM(64),'Asset Type',align='L')
    
    pdf.rect(px2MM(583), px2MM(680), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(690)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Long-term Capital Gains (LTCG)',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(680), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(690)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Short-term Capital Gains (STCG)',align='C')
    
    pdf.rect(px2MM(583), px2MM(732), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(742)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(772), px2MM(732), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(792),px2MM(742)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(732), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(742)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(732), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(742)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    
    #//*--row (1)---*//
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    pdf.rect(px2MM(126), px2MM(784), px2MM(457), px2MM(72),'FD')
    pdf.set_xy(px2MM(146),px2MM(804)) 
    pdf.cell(px2MM(417), px2MM(32),'REITs/InvITs',align='L')
    
    pdf.rect(px2MM(583), px2MM(784), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(603),px2MM(804)) 
    pdf.cell(px2MM(155), px2MM(32),'> 1 year',align='C')
    
    pdf.rect(px2MM(772), px2MM(784), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(792),px2MM(804)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5% on LTCG > ₹ 1.25 lakh/year',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(784), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(804)) 
    pdf.cell(px2MM(155), px2MM(32),'< 1 year',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(784), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(804)) 
    pdf.cell(px2MM(379.5), px2MM(32),'20%',align='C')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    
    
#//*----Capital Gains Taxation by Asset Type (Page 3)-----*//      
def capital_gains_3(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
    
    # black rectangle
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

    #//*----Headings----//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(960), px2MM(84),'Capital Gains Taxation by Asset Type',align='L')
    
    #//*---Black vertical line--*-//
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(204), px2MM(6), px2MM(572),'F')
    
    pdf.rect(px2MM(126), px2MM(204), px2MM(100), px2MM(42),'F')
    pdf.set_xy(px2MM(141),px2MM(209)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(80), px2MM(32),'Others',align='L')
    
    
    #//*----Equity Table-----------------*//
    #//*---Columns---*//
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(126), px2MM(246), px2MM(457), px2MM(104),'FD')
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(146),px2MM(266)) 
    pdf.cell(px2MM(80), px2MM(64),'Asset Type',align='L')
    
    pdf.rect(px2MM(583), px2MM(246), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(256)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Long-term Capital Gains (LTCG)',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(246), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(256)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Short-term Capital Gains (STCG)',align='C')
    
    pdf.rect(px2MM(583), px2MM(298), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(308)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(772), px2MM(298), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(792),px2MM(308)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(298), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(308)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(298), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(308)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    #//*----Row 1(1/1)----*//
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.rect(px2MM(126), px2MM(350), px2MM(240), px2MM(240),'FD')
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_xy(px2MM(146),px2MM(406)) 
    pdf.multi_cell(px2MM(200), px2MM(32),'Hybrid mutual funds (<35% equity)/Market- Linked Debentures',align='L')
    
    pdf.rect(px2MM(366), px2MM(350), px2MM(217), px2MM(104),'FD')
    pdf.set_xy(px2MM(386),px2MM(370)) 
    pdf.multi_cell(px2MM(200), px2MM(32),'Purchased before 1st April,  2023',align='L')
    
    pdf.rect(px2MM(583), px2MM(350), px2MM(189), px2MM(104),'FD')
    pdf.set_xy(px2MM(603),px2MM(386)) 
    pdf.cell(px2MM(155), px2MM(32),'> 2 years',align='C')
    
    pdf.rect(px2MM(772), px2MM(350), px2MM(419.5), px2MM(104),'FD')
    pdf.set_xy(px2MM(792),px2MM(386)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5% without indexation',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(350), px2MM(189), px2MM(104),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(386)) 
    pdf.cell(px2MM(155), px2MM(32),'< 2 years',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(350), px2MM(419.5), px2MM(104),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(386)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    #//*--row (1/2)---*//
    pdf.rect(px2MM(366), px2MM(454), px2MM(217), px2MM(136),'FD')
    pdf.set_xy(px2MM(386),px2MM(474)) 
    pdf.multi_cell(px2MM(177), px2MM(32),'Purchased on or after 1st April, 2023',align='L')
    
    pdf.rect(px2MM(583), px2MM(454), px2MM(189), px2MM(136),'FD')
    pdf.set_xy(px2MM(603),px2MM(506)) 
    pdf.cell(px2MM(155), px2MM(32),'Any',align='C')
    
    pdf.rect(px2MM(772), px2MM(454), px2MM(419.5), px2MM(136),'FD')
    pdf.set_xy(px2MM(792),px2MM(506)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(454), px2MM(189), px2MM(136),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(506)) 
    pdf.cell(px2MM(155), px2MM(32),'Any',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(454), px2MM(419.5), px2MM(136),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(506)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    #//*--row (2)-row(4)---*//
    asset_type= ['Hybrid mutual funds (35% - 65% equity)','Collectibles/Antiques','Cryptos/NFTs']
    long_hold = ['> 2 years','> 2 years','Any']
    long_tax = ['12.5% without indexation','12.5% without indexation','30% for all holding periods']
    short_hold = ['< 2 years','< 2 years','Any']
    short_tax = ['As per income tax slab','As per income tax slab','30% for all holding periods']
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    
    col = '#FFFFFF'
    
    for i in range(len(asset_type)):
        pdf.set_fill_color(*hex2RGB(col))
        pdf.rect(px2MM(126), px2MM(590+(i*62)), px2MM(457), px2MM(62),'FD')
        pdf.set_xy(px2MM(146),px2MM(605+(i*62))) 
        pdf.cell(px2MM(366), px2MM(32),asset_type[i],align='L')
        
        pdf.rect(px2MM(583), px2MM(590+(i*62)), px2MM(189), px2MM(62),'FD')
        pdf.set_xy(px2MM(603),px2MM(605+(i*62))) 
        pdf.cell(px2MM(155), px2MM(32),long_hold[i],align='C')
        
        pdf.rect(px2MM(772), px2MM(590+(i*62)), px2MM(419.5), px2MM(62),'FD')
        pdf.set_xy(px2MM(792),px2MM(605+(i*62))) 
        pdf.cell(px2MM(379.5), px2MM(32),long_tax[i],align='C')
        
        pdf.rect(px2MM(1191.5), px2MM(590+(i*62)), px2MM(189), px2MM(62),'FD')
        pdf.set_xy(px2MM(1211.5),px2MM(605+(i*62))) 
        pdf.cell(px2MM(155), px2MM(32),short_hold[i],align='C')
        
        pdf.rect(px2MM(1380.5), px2MM(590+(i*62)), px2MM(419.5), px2MM(62),'FD')
        pdf.set_xy(px2MM(1400.5),px2MM(605+(i*62))) 
        pdf.cell(px2MM(379.5), px2MM(32),short_tax[i],align='C')
        
        if col == '#F3F6F9':
            col = '#FFFFFF'
        else:
            col = '#F3F6F9'
        
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    
#//*----Capital Gains Taxation by Asset Type (Page 4)-----*//      
def capital_gains_4(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
    
    # black rectangle
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

    #//*----Headings----//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(960), px2MM(84),'Capital Gains Taxation by Asset Type',align='L')
    
    #//*---Black vertical line--*-//
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(120), px2MM(204), px2MM(6), px2MM(466),'F')
    
    pdf.rect(px2MM(126), px2MM(204), px2MM(100), px2MM(42),'F')
    pdf.set_xy(px2MM(141),px2MM(209)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(80), px2MM(32),'Others',align='L')
    
    
    #//*----Equity Table-----------------*//
    #//*---Columns---*//
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(126), px2MM(246), px2MM(457), px2MM(104),'FD')
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(146),px2MM(266)) 
    pdf.cell(px2MM(80), px2MM(64),'Asset Type',align='L')
    
    pdf.rect(px2MM(583), px2MM(246), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(256)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Long-term Capital Gains (LTCG)',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(246), px2MM(608.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(256)) 
    pdf.cell(px2MM(568.5), px2MM(32),'Short-term Capital Gains (STCG)',align='C')
    
    pdf.rect(px2MM(583), px2MM(298), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(603),px2MM(308)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(772), px2MM(298), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(792),px2MM(308)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(298), px2MM(189), px2MM(52),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(308)) 
    pdf.cell(px2MM(155), px2MM(32),'Holding Period',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(298), px2MM(419.5), px2MM(52),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(308)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Tax Rate',align='C')
    
    #//*----Row 1(1/1)----*//
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.rect(px2MM(126), px2MM(350), px2MM(240), px2MM(176),'FD')
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_xy(px2MM(146),px2MM(406)) 
    pdf.multi_cell(px2MM(210), px2MM(32),'Sovereign Gold Bonds',align='L')
    
    pdf.rect(px2MM(366), px2MM(350), px2MM(217), px2MM(72),'FD')
    pdf.set_xy(px2MM(386),px2MM(370)) 
    pdf.multi_cell(px2MM(200), px2MM(32),'Held till Maturity',align='L')
    
    pdf.rect(px2MM(583), px2MM(350), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(603),px2MM(370)) 
    pdf.cell(px2MM(155), px2MM(32),'Any',align='C')
    
    pdf.rect(px2MM(772), px2MM(350), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(792),px2MM(370)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Exempt',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(350), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(370)) 
    pdf.cell(px2MM(155), px2MM(32),'Any',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(350), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(370)) 
    pdf.cell(px2MM(379.5), px2MM(32),'Exempt',align='C')
    
    #//*--row (1/2)---*//
    pdf.rect(px2MM(366), px2MM(422), px2MM(217), px2MM(104),'FD')
    pdf.set_xy(px2MM(386),px2MM(442)) 
    pdf.multi_cell(px2MM(200), px2MM(32),'Sold in secondary market',align='L')
    
    pdf.rect(px2MM(583), px2MM(422), px2MM(189), px2MM(104),'FD')
    pdf.set_xy(px2MM(603),px2MM(458)) 
    pdf.cell(px2MM(155), px2MM(32),'> 1 year',align='C')
    
    pdf.rect(px2MM(772), px2MM(422), px2MM(419.5), px2MM(104),'FD')
    pdf.set_xy(px2MM(792),px2MM(458)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5% without indexation',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(422), px2MM(189), px2MM(104),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(458)) 
    pdf.cell(px2MM(155), px2MM(32),'< 1 year',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(422), px2MM(419.5), px2MM(104),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(458)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    
    #//*----Row 2(2/1)----*//
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.rect(px2MM(126), px2MM(526), px2MM(240), px2MM(144),'FD')
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_xy(px2MM(146),px2MM(566)) 
    pdf.multi_cell(px2MM(210), px2MM(32),'Non-Convertible Debentures',align='L')
    
    pdf.rect(px2MM(366), px2MM(526), px2MM(217), px2MM(72),'FD')
    pdf.set_xy(px2MM(386),px2MM(546)) 
    pdf.multi_cell(px2MM(200), px2MM(32),'Listed',align='L')
    
    pdf.rect(px2MM(583), px2MM(526), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(603),px2MM(546)) 
    pdf.cell(px2MM(155), px2MM(32),'> 1 year',align='C')
    
    pdf.rect(px2MM(772), px2MM(526), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(792),px2MM(546)) 
    pdf.cell(px2MM(379.5), px2MM(32),'12.5% without indexation',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(526), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(546)) 
    pdf.cell(px2MM(155), px2MM(32),'< 1 year',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(526), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(546)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    #//*--row (2/2)---*//
    pdf.rect(px2MM(366), px2MM(598), px2MM(217), px2MM(72),'FD')
    pdf.set_xy(px2MM(386),px2MM(618)) 
    pdf.multi_cell(px2MM(200), px2MM(32),'Unlisted',align='L')
    
    pdf.rect(px2MM(583), px2MM(598), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(603),px2MM(618)) 
    pdf.cell(px2MM(155), px2MM(32),'Any',align='C')
    
    pdf.rect(px2MM(772), px2MM(598), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(792),px2MM(618)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    pdf.rect(px2MM(1191.5), px2MM(598 ), px2MM(189), px2MM(72),'FD')
    pdf.set_xy(px2MM(1211.5),px2MM(618)) 
    pdf.cell(px2MM(155), px2MM(32),'Any',align='C')
    
    pdf.rect(px2MM(1380.5), px2MM(598 ), px2MM(419.5), px2MM(72),'FD')
    pdf.set_xy(px2MM(1400.5),px2MM(618)) 
    pdf.cell(px2MM(379.5), px2MM(32),'As per income tax slab',align='C')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
              
#//*---------------------Planning For Inheritance------------------*//

def planning_for_inheritance(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #//*----Headings----//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(614), px2MM(84),'Planning For Inheritance',align='L')
    
    #//*---Black vertical line--*-//
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F')
    
    header_text = "Inheritance planning is your proactive roadmap, preparing you today for the sensitive journey of inheriting wealth in the future. It's about equipping yourself from now itself with the knowledge to manage future responsibilities wisely, fostering financial stability and peace of mind, all while maintaining family harmony and strengthening ties. Here's what to keep in mind:"
    
    pdf.set_xy(px2MM(120),px2MM(224)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.multi_cell(px2MM(1680), px2MM(42),header_text,align='L')
    
    y_rect = [408,470,532,594,656]
    y_text = [390,452,514,576,638]
    
    stat_text = ["In India, wealth can be inherited in four primary ways: via a will, succession laws, gifting, or through a trust.","While a will and succession laws come into play after the owner's death, gifts can be given during their lifetime.","Trusts involve a legal entity managing wealth for beneficiaries, often requiring specialized legal advice.","Always retain documents and records of the assets purchased by the previous generation.","For real estate purchased before 1st April 2001, obtain a valuation certificate from a registered property valuer for fair market value as of 1st April 2001."]
    
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_fill_color(*hex2RGB('#000000'))
    for i in range(len(stat_text)):
        pdf.rect(px2MM(120), px2MM(y_rect[i]), px2MM(10), px2MM(10),'F')
        pdf.set_xy(px2MM(150),px2MM(y_text[i])) 
        pdf.multi_cell(px2MM(1650), px2MM(42),stat_text[i],align='L')
        
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    
    
#//*---------------------Understanding Inheritance’s Tax Implications------------------*//

def understanding_inheritance(pdf,json_data,c_MoneyS,money_signData)        :
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #//*----Headings----//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(1200), px2MM(84),'Understanding Inheritance’s Tax Implications',align='L')
    
    #//*---Black vertical line--*-//
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F')
    
    header_text = "Although inheritance may not have any immediate tax consequences in India, it is critical to understand the scenarios that can trigger tax liabilities. Here are some essential details:"
    
    pdf.set_xy(px2MM(120),px2MM(224)) 
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.multi_cell(px2MM(1680), px2MM(42),header_text,align='L')
    
    
    y_rect = [366,428,532,594]
    y_text = [348,514,576]
    
    stat_text = ["There’s no inheritance tax in India. However, capital gains tax is applicable when selling inherited assets.","If filing ITR 3, disclosing the inherited assets is advisable.","If the deceased earned during any part of the financial year in which they passed away, their ITR should be filed."]
    
    
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_fill_color(*hex2RGB('#000000'))
    for i in range(len(y_rect)):
        pdf.rect(px2MM(120), px2MM(y_rect[i]), px2MM(10), px2MM(10),'F')
        
    for i in range(len(stat_text)):
        pdf.set_xy(px2MM(150),px2MM(y_text[i])) 
        pdf.multi_cell(px2MM(1650), px2MM(42),stat_text[i],align='L')
        
        
    #//*---For 2nd Cooment----*//
    pdf.set_xy(px2MM(150),px2MM(410)) 
    pdf.cell(px2MM(1478), px2MM(42),"While calculating capital gains, cost will be the price paid by the previous owner at the time of purchase. Refer to the",border='0',align='L')    
    rem_x = mm2PX(pdf.get_x())
        
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(rem_x),px2MM(410)) 
    pdf.cell(px2MM(150), px2MM(42),"‘Capital Gains",align='L')  
    pdf.set_xy(px2MM(150),px2MM(452)) 
    pdf.multi_cell(px2MM(400), px2MM(42),"Taxation by Asset Type’",align='L')   
    
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(470),px2MM(452)) 
    pdf.multi_cell(px2MM(600), px2MM(42),"table for more details.",align='L')  
        
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    
        
#//*--------------------------MF Holdings Evaluation (new)------------------------------------------------//

def mf_holding_eveluation(pdf,json_data,c_MoneyS,money_signData):
    try:
        tab_val1 = json_data["mf_holding_evaluation"]['table']
        if tab_val1==[]:
            return None

        tab_total = json_data["mf_holding_evaluation"]['total']
        tab_total['scheme_name']='Total'
        tab_total['plan']=''
        tab_total['category']=''
        tab_total['scheme_type']=''
        tab_total['fund_evaluation_quality']=''
        tab_val1.append(tab_total)
        mf_hold = pd.DataFrame.from_dict(tab_val1)

        # mf_hold_total = json_data["mf_holding_evaluation"]['total']
        mf_comment1 = json_data["mf_holding_evaluation"]['comments1']
        mf_comment2 = json_data["mf_holding_evaluation"]['comments2']
    except Exception as e:
        return None
    
    #//*---LOOP FOR TABLE---*//
    if mf_hold.empty:
        return None   
    
    global your_fin_analysis_sub_comment
    your_fin_analysis_sub_comment.append('Mutual Fund Holdings Evaluation')
    
    def desclaimer_text(pdf):
        desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
        pdf.set_xy(px2MM(405), px2MM(1039))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(1110),px2MM(21),desc_text,border=0,align="C")
        
    def mf_page_create(pdf):
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

        #//*----Featured List of Financial Products----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(800), px2MM(84),'Mutual Fund Holdings Evaluation',align='L')
                
        #//*---Top Black box
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F') 
        
        desclaimer_text(pdf)
        index_text(pdf,'#1A1A1D')
        
        
        #//*---Table Column Name--*//
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        
        #//*--Col 1
        pdf.rect(px2MM(120), px2MM(204), px2MM(396), px2MM(104),'FD')
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(140),px2MM(224)) 
        pdf.cell(px2MM(356), px2MM(64),'Scheme Name',align='L')
        
        #//*--Col 2
        pdf.rect(px2MM(516), px2MM(204), px2MM(160), px2MM(104),'FD')
        pdf.set_xy(px2MM(536),px2MM(224)) 
        pdf.cell(px2MM(120), px2MM(64),'Plan',align='L')
        
        #//*--Col 3
        pdf.rect(px2MM(676), px2MM(204), px2MM(160), px2MM(104),'FD')
        pdf.set_xy(px2MM(696),px2MM(224)) 
        pdf.cell(px2MM(120), px2MM(64),'Category',align='L')
        
        #//*--Col 4
        pdf.rect(px2MM(836), px2MM(204), px2MM(230), px2MM(104),'FD')
        pdf.set_xy(px2MM(856),px2MM(224)) 
        pdf.cell(px2MM(190), px2MM(64),'Scheme Type',align='L')
        
        #//*--Col 5
        pdf.rect(px2MM(1066), px2MM(204), px2MM(212), px2MM(104),'FD')
        pdf.set_xy(px2MM(1086),px2MM(224)) 
        pdf.cell(px2MM(172), px2MM(64),'Current Value',align='R')
        
        #//*--Col 6
        pdf.rect(px2MM(1278), px2MM(204), px2MM(320), px2MM(52),'FD')
        pdf.set_xy(px2MM(1298),px2MM(214)) 
        pdf.cell(px2MM(280), px2MM(32),'Fund Evaluation',align='C')
        
        pdf.rect(px2MM(1278), px2MM(256), px2MM(160), px2MM(52),'FD')
        pdf.set_xy(px2MM(1298),px2MM(266)) 
        pdf.cell(px2MM(120), px2MM(32),'Score*',align='C')
        
        pdf.rect(px2MM(1438), px2MM(256), px2MM(160), px2MM(52),'FD')
        pdf.set_xy(px2MM(1458),px2MM(266)) 
        pdf.cell(px2MM(120), px2MM(32),'Quality',align='C')
        
        #//*--Col 7
        pdf.rect(px2MM(1598), px2MM(204), px2MM(202), px2MM(104),'FD')
        pdf.set_xy(px2MM(1618),px2MM(224)) 
        pdf.multi_cell(px2MM(162), px2MM(32),'Excess Annual Commission**',align='R')
        
        
    def get_rect_h(pdf,mf_hold,y):
        text_y = y+15
        
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(140),px2MM(text_y)) 
        pdf.multi_cell(px2MM(355), px2MM(32),mf_hold["scheme_name"].iloc[i],border='0',align='L')
        y1 = mm2PX(pdf.get_y())
        
        
        pdf.set_xy(px2MM(536),px2MM(text_y)) 
        pdf.multi_cell(px2MM(120), px2MM(32),mf_hold["plan"].iloc[i],align='L')
        y2 = mm2PX(pdf.get_y())

        
        pdf.set_xy(px2MM(856),px2MM(text_y)) 
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(190), px2MM(32),mf_hold["scheme_type"].iloc[i],align='L')
        y3 = mm2PX(pdf.get_y())
        
        max_line_list = [int((y1-text_y)/32),int((y2-text_y)/32),int((y3-text_y)/32)]
        
        if max(max_line_list) >= 1:
            h_rect = max(max_line_list)*32+30
            h_text = max(max_line_list)*32
            h_text = w1 = w2 = w3 = max(max_line_list)*32
        
        
        w1 =  y+(h_rect-(max_line_list[0]*32))/2
        w2 =  y+(h_rect-(max_line_list[2]*32))/2
        w3 =  y+(h_rect-(max_line_list[1]*32))/2
        # if  max_line_list[0] > 1:
        #     w1 = 32
        # if max_line_list[2] > 1:
        #     w2 = 32
            
        # if max_line_list[1] > 1:
        #     w3 = 32 
        if 1080-y < 94+h_rect and i != len(mf_hold)-2 :
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(0), px2MM(y+1), px2MM(1278), px2MM(1080-y),'F')
            desclaimer_text(pdf)
              
        elif 1080-rect_y < 255+h_rect and i == len(mf_hold)-2 :
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(0), px2MM(y+1), px2MM(1278), px2MM(h_rect),'F')\
                
        return h_rect,h_text,w1,w2,w3
        
    mf_page_create(pdf)    
    rect_y = mm2PX(pdf.get_y())+20
    text_y = rect_y+15
    col = '#F3F6F9'
    
    for i in range(len(mf_hold)):
        h_rect,h_text,w1,w2,w3 = get_rect_h(pdf,mf_hold,rect_y)

        if 1080-rect_y < 94+h_rect and i != len(mf_hold)-2 :
            mf_page_create(pdf) 
            rect_y = mm2PX(pdf.get_y())+20
            h_rect,h_text,w1,w2,w3 = get_rect_h(pdf,mf_hold,rect_y)
            text_y = rect_y+15
            col = '#F3F6F9'
            
        elif 1080-rect_y < 255+h_rect and i == len(mf_hold)-2 :
            mf_page_create(pdf) 
            rect_y = mm2PX(pdf.get_y())+20
            h_rect,h_text,w1,w2,w3 = get_rect_h(pdf,mf_hold,rect_y)
            text_y = rect_y+15
            col = '#F3F6F9'
            
        # h_rect = 62
        # h_text = w1 = w2= w3 = 32
        # gp = 15
        
        # pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        # pdf.set_text_color(*hex2RGB('#1A1A1D'))
        
        # ##//* New logic to get string height
        
        # pdf.set_xy(px2MM(140),px2MM(text_y)) 
        # pdf.multi_cell(px2MM(355), px2MM(w1),mf_hold["scheme_name"].iloc[i],border='R',align='L')
        # y1 = mm2PX(pdf.get_y())
        
        # pdf.set_xy(px2MM(536),px2MM(text_y)) 
        # pdf.multi_cell(px2MM(120), px2MM(w3),mf_hold["plan"].iloc[i],align='L')
        # y2 = mm2PX(pdf.get_y())
        
        # pdf.set_xy(px2MM(856),px2MM(text_y)) 
        # pdf.multi_cell(px2MM(190), px2MM(w2),mf_hold["scheme_type"].iloc[i],align='L')
        # y3 = mm2PX(pdf.get_y())
        
        # max_line_list = [int((y1-text_y)/32),int((y2-text_y)/32),int((y3-text_y)/32)]
        
        # if max(max_line_list) > 1:
        #     h_rect = 94
        #     h_text = 64
        #     h_text = w1 = w2 = w3 = 64
            
        # if  max_line_list[0] > 1:
        #     w1 = 32
        # if max_line_list[2] > 1:
        #     w2 = 32
            
        # if max_line_list[1] > 1:
        #     w3 = 32 

        ##//* Old logic to get string height
        # if mm2PX(pdf.get_string_width(mf_hold["scheme_name"].iloc[i])) > 350 or mm2PX(pdf.get_string_width(mf_hold["scheme_type"].iloc[i])) > 190 or mm2PX(pdf.get_string_width(mf_hold["plan"].iloc[i])) > 120 :
        #     h_rect = 94
        #     h_text = 64
        #     h_text = w1 = w2 = w3 = 64
            
        # if mm2PX(pdf.get_string_width(mf_hold["scheme_name"].iloc[i])) > 350:
        #     w1 = 32
        # if mm2PX(pdf.get_string_width(mf_hold["scheme_type"].iloc[i])) > 190:
        #     w2 = 32
            
        # if mm2PX(pdf.get_string_width(mf_hold["plan"].iloc[i])) > 120:
        #     w3 = 32 
            
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        if i == (len(mf_hold)-1):
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            pdf.set_fill_color(*hex2RGB('#B9BABE'))
            pdf.rect(px2MM(120), px2MM(rect_y), px2MM(1680), px2MM(1),'FD')
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.set_draw_color(*hex2RGB('#E9EAEE'))
            pdf.set_line_width(px2MM(0.2))
            pdf.rect(px2MM(120), px2MM(rect_y+1), px2MM(1680), px2MM(h_rect),'FD')
            if mf_hold["excess_annual_expense"].iloc[i] not in ["0.0","00.00","0.00","0",""]:

                pdf.set_fill_color(*hex2RGB('#EF4444'))
                pdf.set_draw_color(*hex2RGB('#E9EAEE'))
                pdf.set_line_width(px2MM(0.2))
                pdf.rect(px2MM(1598), px2MM(rect_y+1), px2MM(202), px2MM(h_rect),'FD')
        else: 
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.set_fill_color(*hex2RGB(col))
            pdf.rect(px2MM(120), px2MM(rect_y), px2MM(396), px2MM(h_rect),'FD')
            pdf.rect(px2MM(516), px2MM(rect_y), px2MM(160), px2MM(h_rect),'FD')
            pdf.rect(px2MM(676), px2MM(rect_y), px2MM(160), px2MM(h_rect),'FD')
            pdf.rect(px2MM(836), px2MM(rect_y), px2MM(230), px2MM(h_rect),'FD')
            pdf.rect(px2MM(1066), px2MM(rect_y), px2MM(212), px2MM(h_rect),'FD')
            pdf.rect(px2MM(1278), px2MM(rect_y), px2MM(160), px2MM(h_rect),'FD')
            pdf.rect(px2MM(1438), px2MM(rect_y), px2MM(160), px2MM(h_rect),'FD')
            pdf.rect(px2MM(1598), px2MM(rect_y), px2MM(202), px2MM(h_rect),'FD')
        
        #//*--Col 1
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(140),px2MM(w1)) 
        pdf.multi_cell(px2MM(355), px2MM(32),mf_hold["scheme_name"].iloc[i],align='L')
        
        #//*--Col 2

        # Define color based on plan type
        dynamic_color = {"Regular": "#EF4444", "Direct": "#22C55D"}.get(mf_hold["plan"].iloc[i], "#1A1A1D")
        
        pdf.set_text_color(*hex2RGB(dynamic_color))
        pdf.set_xy(px2MM(536),px2MM(w3)) 
        pdf.multi_cell(px2MM(120), px2MM(32),mf_hold["plan"].iloc[i],align='L')
        
        #//*--Col 3
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(696),px2MM(text_y)) 
        pdf.multi_cell(px2MM(135), px2MM(h_text),mf_hold["category"].iloc[i],align='L')
        
        #//*--Col 4
        pdf.set_xy(px2MM(856),px2MM(w2)) 
        pdf.multi_cell(px2MM(190), px2MM(32),mf_hold["scheme_type"].iloc[i],align='L')
        
        #//*--Col 5
 
        pdf.set_xy(px2MM(1086),px2MM(text_y)) 
        if mf_hold["current_value"].iloc[i] == '-':
            pdf.multi_cell(px2MM(172), px2MM(h_text),'',align='R')
        else:   

            val1 = '₹ '+str(format_cash2(float(mf_hold["current_value"].iloc[i])))
            # val1 = locale.currency(mf_hold["current_value"].iloc[i], grouping=True)
            pdf.multi_cell(px2MM(172), px2MM(h_text),val1,align='R')
        
        #//*--Col 6    
        pdf.set_xy(px2MM(1298),px2MM(text_y)) 
        if mf_hold["fund_evaluation_score"].iloc[i] == 0 and  i == (len(mf_hold)-1):
            pdf.multi_cell(px2MM(120), px2MM(h_text),' ',align='C')
        elif mf_hold["fund_evaluation_score"].iloc[i] == 0 and i != (len(mf_hold)-1):
            pdf.multi_cell(px2MM(120), px2MM(h_text),"-",align='C')
        else:
            pdf.multi_cell(px2MM(120), px2MM(h_text),str(int(mf_hold["fund_evaluation_score"].iloc[i])),align='C')
        #//*--Col 7
        pdf.set_xy(px2MM(1458),px2MM(text_y)) 
        if mf_hold["fund_evaluation_quality"].iloc[i]=="" and i == (len(mf_hold)-1):
            pdf.multi_cell(px2MM(120), px2MM(h_text)," ",align='C')
            
        elif mf_hold["fund_evaluation_quality"].iloc[i]=="" and not i == (len(mf_hold)-1):
            pdf.multi_cell(px2MM(120), px2MM(h_text),"-",align='C')
            
        else:
            conditional_color = (
            "#22C55D" if mf_hold["fund_evaluation_quality"].iloc[i] == "High" 
            else "#EF4444" if mf_hold["fund_evaluation_quality"].iloc[i] == "Low" 
            else "#F5B40B")
            pdf.set_text_color(*hex2RGB(conditional_color))
            pdf.multi_cell(px2MM(120), px2MM(h_text),mf_hold["fund_evaluation_quality"].iloc[i] ,align='C')
        
        #//*--Col 8
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(1598),px2MM(text_y)) 
        if int(float(mf_hold["excess_annual_expense"].iloc[i])) == 0 or mf_hold["excess_annual_expense"].iloc[i]== "":
            pdf.multi_cell(px2MM(190), px2MM(h_text),'₹ 0.0K',align='R')
            
        else:
            if i == (len(mf_hold)-1):
                pdf.set_text_color(*hex2RGB('#FFFFFF'))
                val = 'Approx ₹ '+str(format_cash3(float(mf_hold["excess_annual_expense"].iloc[i])))
            else:
                val = '₹ '+str(format_cash3(float(mf_hold["excess_annual_expense"].iloc[i])))
            pdf.multi_cell(px2MM(190), px2MM(h_text),val,align='R')
            
        if col == '#F3F6F9':
            col = '#FFFFFF'
        else:
            col = '#F3F6F9'
            
        rect_y=mm2PX(pdf.get_y())+15
        text_y=rect_y+15
        
        
        #//*-----Index Text of Page--**////
        rem = mm2PX(pdf.get_y())+25
    
        # pdf.set_xy(px2MM(1870), px2MM(1018))  
        # pdf.set_font('LeagueSpartan-Light', size=px2pts(30))
        # pdf.set_text_color(*hex2RGB('#1A1A1D'))
        # pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')

    #//*---1st Comment----*//
    if (1080-rem) > 120:  
        for i in range (len(mf_comment1)):
            pdf.set_font('LeagueSpartan-Light', size=px2pts(18))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.set_xy(px2MM(120),px2MM(rem+40+(i*35))) 
            pdf.cell(px2MM(1680), px2MM(25),mf_comment1[i],align='L')
    else:
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        #//*----Featured List of Financial Products----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(800), px2MM(84),'Mutual Fund Holdings Evaluation',align='L')
        
        #//*---Top Black box
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F') 
        
        #//*-----Index Text of Page--**////
        rem = mm2PX(pdf.get_y())+140
        index_text(pdf,'#1A1A1D') 
        for i in range (len(mf_comment1)):
            pdf.set_font('LeagueSpartan-Light', size=px2pts(18))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.set_xy(px2MM(140),px2MM(rem+(i*35))) 
            pdf.cell(px2MM(1680), px2MM(25),mf_comment1[i],align='L')
     
            
    rem1 = mm2PX(pdf.get_y())        
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    cnt = multicell_height(pdf,mf_comment2[0],1650)+multicell_height(pdf,mf_comment2[1],1650)+1

    #//*----Second Comment--------*//
    
    # //*--check if space is avaliable or not to print comment
    if 1080-rem1 >  (156+(cnt*42)):
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(120),px2MM(rem1+60)) 
        pdf.cell(px2MM(170), px2MM(56),'Comments',align='L')

        cm_cnt = 0
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#000000'))
        rem1+=146
        

        #//*---Point1------*//
        start_point = mf_comment2[0].split('Mutual Fund Commission Analyser')
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(120),px2MM(rem1+18),px2MM(10),px2MM(10),'F')
        
        #//*---Check if link variable exist or not
        if "Mutual Fund Commission Analyser" in mf_comment2[0]:
            pdf.set_xy(px2MM(150),px2MM(rem1))
            # pdf.multi_cell(px2MM(1650), px2MM(42),"""70% of your MF investments (by value) are in Regular plans. As a result, you might pay 0.62% of your investment value in excess commissions every year. By switching to direct plans you can enhance your returns by that much. Explore our""",align='L')
            pdf.multi_cell(px2MM(1650), px2MM(42),start_point[0],align='L')
            
            str_w = mm2PX(pdf.get_string_width(start_point[0]))
            if str_w > 3100: 
                pdf.set_xy(px2MM(142),px2MM(rem1+84))
                pdf.cell(px2MM(265), px2MM(42),""" Mutual Fund Commission Analyser""",align='L',link='https://1finance.co.in/calculator/mutual-funds')
            else:
                
                pdf.set_text_color(*hex2RGB('#3366CC'))
                pdf.set_font('LeagueSpartan-Regular','U',size=px2pts(30))
                
                # pdf.set_xy(px2MM(str_w-1485),px2MM(rem1+2))
                # pdf.cell(px2MM(300), px2MM(42),"""Mutual Fund""",align='L',link='https://1finance.co.in/calculator/mutual-funds')
                
                pdf.set_xy(px2MM(300),px2MM(rem1+84))
                pdf.cell(px2MM(425), px2MM(42),"""Mutual Fund Commission Analyser""",align='L',link='https://1finance.co.in/calculator/mutual-funds')
                x = mm2PX(pdf.get_x())
                pdf.set_text_color(*hex2RGB('#000000'))
                pdf.set_font('LeagueSpartan-Regular',size=px2pts(30))
                pdf.set_xy(px2MM(x),px2MM(rem1+84))
                pdf.cell(px2MM(1650), px2MM(42),""" to estimate excess commissions paid by you till date.""",align='L')
            
            rem2 = mm2PX(pdf.get_y())+42
        else:
            pdf.set_xy(px2MM(150),px2MM(rem1))
            pdf.multi_cell(px2MM(1650), px2MM(42),str(mf_comment2[0]),align='L')
        
            rem2 = mm2PX(pdf.get_y())
        
        #//*---Point 2
        start_point2 = mf_comment2[1].split('Mutual Fund Scoring and Ranking page')
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(120),px2MM(rem2+28),px2MM(10),px2MM(10),'F')
        pdf.set_xy(px2MM(150),px2MM(rem2+10))
        # pdf.multi_cell(px2MM(1650), px2MM(42),"""54% of your equity MFs (by value) are high quality. Consider removing low/medium quality funds from your portfolio. Our equity MF featured list is available at the end of this report, and an evaluation of all equity MFs is available on our""",align='L')
        pdf.multi_cell(px2MM(1650), px2MM(42),start_point2[0],align='L')
        pdf.set_text_color(*hex2RGB('#3366CC'))
        pdf.set_font('LeagueSpartan-Regular','U',size=px2pts(30))
        # pdf.set_xy(px2MM(1630),px2MM(rem2+54))
        # pdf.cell(px2MM(350), px2MM(42),"""Mutual Fund""",align='L',link='https://1finance.co.in/product-scoring/mutual-funds?type=equity')
        
        pdf.set_xy(px2MM(150),px2MM(rem2+94))
        pdf.cell(px2MM(350), px2MM(42),"""Scoring and Ranking.""",align='L',link='https://1finance.co.in/product-scoring/mutual-funds?type=equity')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
    else:
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

        #//*----Featured List of Financial Products----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(602), px2MM(84),'Mutual Fund Holdings Evaluation',align='L')
        
        #//*---Top Black box
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F') 
        
        rem1 = mm2PX(pdf.get_y())+60
        
        desclaimer_text(pdf)
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(120),px2MM(rem1+60)) 
        pdf.cell(px2MM(170), px2MM(56),'Comments',align='L')

        rem1 = mm2PX(pdf.get_y())+60
        
        start_point = mf_comment2[0].split('Mutual Fund Commission Analyser')
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(120),px2MM(rem1+18),px2MM(10),px2MM(10),'F')
        
        if "Mutual Fund Commission Analyser" in mf_comment2[0]:
            pdf.set_xy(px2MM(150),px2MM(rem1))
            pdf.multi_cell(px2MM(1650), px2MM(42),start_point[0],align='L')
            pdf.set_text_color(*hex2RGB('#3366CC'))
            pdf.set_font('LeagueSpartan-Regular','U',size=px2pts(30))
            str_w = mm2PX(pdf.get_string_width(start_point[0]))
            if str_w >  3100:
                pdf.set_xy(px2MM(142),px2MM(rem1+84))
                pdf.cell(px2MM(265), px2MM(42),""" Mutual Fund Commission Analyser""",align='L',link='https://1finance.co.in/calculator/mutual-funds')
            else: 
                # pdf.set_xy(px2MM(1590),px2MM(rem1+42))
                # pdf.set_xy(px2MM(str_w-1485),px2MM(rem1+42))
                # pdf.cell(px2MM(300), px2MM(42),"""Mutual Fund """,align='L',link='https://1finance.co.in/calculator/mutual-funds')
                
                pdf.set_xy(px2MM(300),px2MM(rem1+84))
                pdf.cell(px2MM(425), px2MM(42),"""Mutual Fund Commission Analyser""",align='L',link='https://1finance.co.in/calculator/mutual-funds')
                x = mm2PX(pdf.get_x())
                pdf.set_text_color(*hex2RGB('#000000'))
                pdf.set_font('LeagueSpartan-Regular',size=px2pts(30))
                pdf.set_xy(px2MM(x),px2MM(rem1+84))
                pdf.cell(px2MM(1650), px2MM(42),""" to estimate excess commissions paid by you till date.""",align='L')
            
            rem2 = mm2PX(pdf.get_y())+42
        else:
            pdf.set_xy(px2MM(150),px2MM(rem1))
            pdf.multi_cell(px2MM(1650), px2MM(42),str(mf_comment2[0]),align='L')
        
            rem2 = mm2PX(pdf.get_y())
        
        #//*---Point 2
        start_point2 = mf_comment2[1].split('Mutual Fund Scoring and Ranking page')
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(120),px2MM(rem2+28),px2MM(10),px2MM(10),'F')
        pdf.set_xy(px2MM(150),px2MM(rem2+10))
        # pdf.multi_cell(px2MM(1650), px2MM(42),"""54% of your equity MFs (by value) are high quality. Consider removing low/medium quality funds from your portfolio. Our equity MF featured list is available at the end of this report, and an evaluation of all equity MFs is available on our""",align='L')
        pdf.multi_cell(px2MM(1650), px2MM(42),start_point2[0],align='L')
        
        pdf.set_text_color(*hex2RGB('#3366CC'))
        pdf.set_font('LeagueSpartan-Regular','U',size=px2pts(30))
        # pdf.set_xy(px2MM(1630),px2MM(rem2+54))
        # pdf.cell(px2MM(350), px2MM(42),"""Mutual Fund""",align='L',link='https://1finance.co.in/product-scoring/mutual-funds?type=equity')
        
        pdf.set_xy(px2MM(150),px2MM(rem2+94))
        pdf.cell(px2MM(350), px2MM(42),"""Mutual Fund Scoring and Ranking page.""",align='L',link='https://1finance.co.in/product-scoring/mutual-funds?type=equity')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D') 
        

#//*----------------------------------**------------------------------------------------//

#//*--------------Surrender Impact-------------*//
def surrender_impact(pdf,json_data,c_MoneyS,money_signData):
    try:
        surrender_impact = json_data['surrender_impact']
        tab_val1 = json_data["surrender_impact"]['table']
        if tab_val1==[]:
            return None
        # global your_fin_analysis_sub_comment
        # your_fin_analysis_sub_comment.append('Surrender Impact')

        tab_total = json_data["surrender_impact"]['total']
        tab_total['sr_no']='Total'
        tab_total['policy_name']=''
        tab_total['insurance_type']=''
        tab_total['action_taken']=''
        tab_total['surrender_received']=tab_total['surrender_received']
        tab_total['annual_premium_saved']=tab_total['annual_premium_saved']
        tab_total['commission_saved']=tab_total['commission_saved']
        
        tab_val1.append(tab_total)
        si_df = pd.DataFrame.from_dict(tab_val1)
    except Exception as e:
        print(e)
        return None
    
    def desclaimer_text(pdf):
        desc_text = '''Disclaimer: Commission is considered at flat 20%'''
        pdf.set_xy(px2MM(405), px2MM(1039))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(1110),px2MM(21),desc_text,border=0,align="C")
        
    def surrender_impact_create(pdf,surrender_impact):
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

        #//*----Featured List of Financial Products----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(800), px2MM(84),'Surrender Impact',align='L')
                
        #//*---Top Black box
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F') 
        
        desclaimer_text(pdf)
        index_text(pdf,'#1A1A1D')
        
        
        pdf.rect(px2MM(120), px2MM(432), px2MM(105), px2MM(104),'FD')
        
        #//*---REct Property--*//
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        
        pdf.rect(px2MM(120), px2MM(204), px2MM(1680), px2MM(186),'FD')
        
        #Verticall Lining
        pdf.set_fill_color(*hex2RGB('#D4D4D4'))
        pdf.rect(px2MM(541), px2MM(244), px2MM(1), px2MM(106),'F')
        pdf.rect(px2MM(960), px2MM(244), px2MM(1), px2MM(106),'F')
        pdf.rect(px2MM(1379), px2MM(244), px2MM(1), px2MM(106),'F')
        
        # Images 
        pdf.image(join(cwd,'assets', 'images','surrender impact','total_surrender_value_received.svg'),px2MM(160), px2MM(245), px2MM(36), px2MM(36))
        pdf.image(join(cwd,'assets', 'images','surrender impact','number_of_policy.svg'),px2MM(579), px2MM(245), px2MM(36), px2MM(36))
        pdf.image(join(cwd,'assets', 'images','surrender impact','annual_premium_saved.svg'),px2MM(998), px2MM(245), px2MM(36), px2MM(36))
        pdf.image(join(cwd,'assets', 'images','surrender impact','overall_commission_saved.svg'),px2MM(1417), px2MM(245), px2MM(36), px2MM(36))
        
        pdf.set_font('Inter-Medium', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#425466'))
        pdf.set_xy(px2MM(211),px2MM(251)) 
        pdf.cell(px2MM(310), px2MM(24.2),'Total Surrender value received',align='L')
        
        pdf.set_xy(px2MM(630),px2MM(251)) 
        pdf.cell(px2MM(310), px2MM(24.2),'Number of Policies (NOP)',align='L')
        
        pdf.set_xy(px2MM(1049),px2MM(251)) 
        pdf.cell(px2MM(310), px2MM(24.2),'Annual Premium saved',align='L')
        
        pdf.set_xy(px2MM(1468),px2MM(251)) 
        pdf.cell(px2MM(310), px2MM(24.2),'Overall Commission Saved',align='L')
        
        
        locale.setlocale(locale.LC_MONETARY, 'en_IN')
        pdf.set_font('Inter-Medium', size=px2pts(36))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(160),px2MM(305)) 
        if surrender_impact["total_surrender_value_recived"] == '-':
            pdf.multi_cell(px2MM(343), px2MM(44),'',align='L')
        else:   
            tsvr = str(locale.currency(float(surrender_impact["total_surrender_value_recived"]), grouping=True))
            tsvr = tsvr.split('.')[0].replace('₹','₹ ')
            pdf.multi_cell(px2MM(343), px2MM(44),tsvr,align='L')
            
        pdf.set_xy(px2MM(579),px2MM(305)) 
        pdf.multi_cell(px2MM(343), px2MM(44),surrender_impact["number_of_policies_nop"],align='L')
            
        pdf.set_xy(px2MM(998),px2MM(305)) 
        if surrender_impact["annual_premium_saved"] == '-':
            pdf.multi_cell(px2MM(343), px2MM(44),'',align='L')
        else:   
            aps = str(locale.currency(float(surrender_impact["annual_premium_saved"]), grouping=True))
            aps = aps.split('.')[0].replace('₹','₹ ')
            pdf.multi_cell(px2MM(343), px2MM(44),aps,align='l')
            
        pdf.set_xy(px2MM(1417),px2MM(305)) 
        if surrender_impact["overall_commission_saved"] == '-':
            pdf.multi_cell(px2MM(343), px2MM(44),'',align='L')
        else:   
            ocs = str(locale.currency(float(surrender_impact["overall_commission_saved"]), grouping=True))
            ocs = ocs.split('.')[0].replace('₹','₹ ')
            pdf.multi_cell(px2MM(343), px2MM(44),ocs,align='L')
            
        
            
        # Table Columns
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
         #//*--Col 1
        pdf.rect(px2MM(120), px2MM(432), px2MM(105), px2MM(104),'FD')
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(140),px2MM(453)) 
        pdf.cell(px2MM(65), px2MM(64),'Sr No.',align='C')
        
        #//*--Col 2
        pdf.rect(px2MM(225), px2MM(432), px2MM(550), px2MM(104),'FD')
        pdf.set_xy(px2MM(245),px2MM(452)) 
        pdf.cell(px2MM(510), px2MM(64),'Policy Name',align='L')
        
        #//*--Col 3
        pdf.rect(px2MM(775), px2MM(432), px2MM(160), px2MM(104),'FD')
        pdf.set_xy(px2MM(795),px2MM(452)) 
        pdf.multi_cell(px2MM(120), px2MM(32),'Insurance Type',align='L')
        
        #//*--Col 4
        pdf.rect(px2MM(935), px2MM(432), px2MM(230), px2MM(104),'FD')
        pdf.set_xy(px2MM(955),px2MM(452)) 
        pdf.cell(px2MM(190), px2MM(64),'Action Taken',align='L')
        
        #//*--Col 5
        pdf.rect(px2MM(1165), px2MM(432), px2MM(220), px2MM(104),'FD')
        pdf.set_xy(px2MM(1185),px2MM(452)) 
        pdf.multi_cell(px2MM(180), px2MM(32),'Surrender Received',align='R')
        
        #//*--Col 6
        pdf.rect(px2MM(1385), px2MM(432), px2MM(213), px2MM(104),'FD')
        pdf.set_xy(px2MM(1400),px2MM(452)) 
        pdf.multi_cell(px2MM(178), px2MM(32),'Annual Premium Saved',align='L')
        
        #//*--Col 7
        pdf.rect(px2MM(1598), px2MM(432), px2MM(202), px2MM(104),'FD')
        pdf.set_xy(px2MM(1618),px2MM(452)) 
        pdf.multi_cell(px2MM(162), px2MM(32),'Commission Saved',align='R')
        
    def get_rect_h(pdf,si_df,y):
        text_y = y+15
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))

        #//*--Col 2
        pdf.set_xy(px2MM(245),px2MM(text_y)) 
        pdf.multi_cell(px2MM(500), px2MM(32),si_df["policy_name"].iloc[i],align='L')
        y1 = mm2PX(pdf.get_y())
        
        #//*--Col 3
        pdf.set_xy(px2MM(790),px2MM(text_y)) 
        pdf.multi_cell(px2MM(140), px2MM(32),si_df["insurance_type"].iloc[i],align='L')
        y2 = mm2PX(pdf.get_y())
        
        #//*--Col 4
        pdf.set_xy(px2MM(950),px2MM(text_y)) 
        pdf.multi_cell(px2MM(200), px2MM(32),si_df["action_taken"].iloc[i],align='L')
        y3 = mm2PX(pdf.get_y())

        
        max_line_list = [int((y1-text_y)/32),int((y2-text_y)/32),int((y3-text_y)/32)]
    
        if max(max_line_list) >= 1:
            h_rect = max(max_line_list)*32+30
            h_text = max(max_line_list)*32
            h_text = w1 = w2 = w3 = max(max_line_list)*32
        
        
        w1 =  y+(h_rect-(max_line_list[0]*32))/2
        w2 =  y+(h_rect-(max_line_list[1]*32))/2
        w3 =  y+(h_rect-(max_line_list[2]*32))/2
        
        if 1080-y < 94+h_rect and i != len(si_df)-2 :
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(0), px2MM(y+1), px2MM(1278), px2MM(1080-y),'F')
            desclaimer_text(pdf)
              
        elif 1080-rect_y < 255+h_rect and i == len(si_df)-2 :
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(0), px2MM(y+1), px2MM(1278), px2MM(h_rect),'F')\
               
        return h_rect,h_text,w1,w2,w3
    
    surrender_impact_create(pdf,surrender_impact)    
    rect_y = mm2PX(pdf.get_y())+20
    text_y = rect_y+15
    col = '#F3F6F9'
    
    for i in range(len(si_df)):
        h_rect,h_text,w1,w2,w3 = get_rect_h(pdf,si_df,rect_y)

        if 1080-rect_y < 94+h_rect and i != len(si_df)-2 :
            surrender_impact_create(pdf,surrender_impact) 
            rect_y = mm2PX(pdf.get_y())+20
            h_rect,h_text,w1,w2,w3 = get_rect_h(pdf,si_df,rect_y)
            text_y = rect_y+15
            col = '#F3F6F9'
            
        elif 1080-rect_y < 255+h_rect and i == len(si_df)-2 :
            surrender_impact_create(pdf,surrender_impact) 
            rect_y = mm2PX(pdf.get_y())+20
            h_rect,h_text,w1,w2,w3 = get_rect_h(pdf,si_df,rect_y)
            text_y = rect_y+15
            col = '#F3F6F9'
            
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        if i == (len(si_df)-1):
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            pdf.set_fill_color(*hex2RGB('#B9BABE'))
            pdf.rect(px2MM(120), px2MM(rect_y), px2MM(1680), px2MM(1),'FD')
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.set_draw_color(*hex2RGB('#E9EAEE'))
            pdf.set_line_width(px2MM(0.2))
            pdf.rect(px2MM(120), px2MM(rect_y+1), px2MM(1680), px2MM(h_rect),'FD')
        else: 
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.set_fill_color(*hex2RGB(col))
            pdf.rect(px2MM(120), px2MM(rect_y), px2MM(105), px2MM(h_rect),'FD')
            pdf.rect(px2MM(225), px2MM(rect_y), px2MM(550), px2MM(h_rect),'FD')
            pdf.rect(px2MM(775), px2MM(rect_y), px2MM(160), px2MM(h_rect),'FD')
            pdf.rect(px2MM(935), px2MM(rect_y), px2MM(230), px2MM(h_rect),'FD')
            pdf.rect(px2MM(1165), px2MM(rect_y), px2MM(220), px2MM(h_rect),'FD')
            pdf.rect(px2MM(1385), px2MM(rect_y), px2MM(213), px2MM(h_rect),'FD')
            pdf.rect(px2MM(1598), px2MM(rect_y), px2MM(202), px2MM(h_rect),'FD')
            
         #//*--Col 1
        pdf.set_xy(px2MM(140),px2MM(text_y)) 
        pdf.multi_cell(px2MM(65), px2MM(h_text),si_df["sr_no"].iloc[i],align='C')
        
        #//*--Col 2
        pdf.set_xy(px2MM(245),px2MM(w1)) 
        pdf.multi_cell(px2MM(500), px2MM(32),si_df["policy_name"].iloc[i],align='L')
        
        #//*--Col 3
        pdf.set_xy(px2MM(790),px2MM(w2)) 
        pdf.multi_cell(px2MM(140), px2MM(32),si_df["insurance_type"].iloc[i],align='L')
        
        #//*--Col 4
        pdf.set_xy(px2MM(950),px2MM(w3)) 
        pdf.multi_cell(px2MM(200), px2MM(32),si_df["action_taken"].iloc[i],align='L')
        
        #//*--Col 5
        pdf.set_xy(px2MM(1180),px2MM(text_y)) 
        if si_df["surrender_received"].iloc[i] == '-' or si_df["surrender_received"].iloc[i] == '0':
            pdf.multi_cell(px2MM(190), px2MM(h_text),'-',align='R')
        else:   
            sr = str(locale.currency(float(si_df["surrender_received"].iloc[i]), grouping=True))
            sr = sr.split('.')[0].replace('₹','₹ ')
            pdf.multi_cell(px2MM(190), px2MM(h_text),sr,align='R')
        
        #//*--Col 6
        pdf.set_xy(px2MM(1400),px2MM(text_y)) 
        if si_df["annual_premium_saved"].iloc[i] == '-' or si_df["annual_premium_saved"].iloc[i] == '0':
            pdf.multi_cell(px2MM(180), px2MM(h_text),'-',align='R')
        else:   
            aps = str(locale.currency(float(si_df["annual_premium_saved"].iloc[i]), grouping=True))
            aps = aps.split('.')[0].replace('₹','₹ ')
            pdf.multi_cell(px2MM(180), px2MM(h_text),aps,align='R')
        
        #//*--Col 7
        pdf.set_xy(px2MM(1608),px2MM(text_y)) 
        if si_df["commission_saved"].iloc[i] == '-' or si_df["commission_saved"].iloc[i] == '0':
            pdf.multi_cell(px2MM(172), px2MM(h_text),'-',align='R')
        else:   
            cs = str(locale.currency(float(si_df["commission_saved"].iloc[i]), grouping=True))
            cs = cs.split('.')[0].replace('₹','₹ ')
            pdf.multi_cell(px2MM(172), px2MM(h_text),cs,align='R')
        
        if col == '#F3F6F9':
            col = '#FFFFFF'
        else:
            col = '#F3F6F9'
            
        rect_y=mm2PX(pdf.get_y())+15
        text_y=rect_y+15

# #//*-----Insurance Policy Evaluation----*//
def insurance_policy_eveluation(pdf,json_data,c_MoneyS,money_signData):
    try:
        tab_val1 = json_data["insurance_policy_evaluation"]['table']
        if tab_val1==[]:
            return None
        global your_fin_analysis_sub_comment
        your_fin_analysis_sub_comment.append('Insurance Policy Evaluation')

        tab_total = json_data["insurance_policy_evaluation"]['total']
        tab_total['policy_name']='Total'
        tab_total['plan_type']=''
        tab_total['start_date']=''
        tab_total['policy_tenure']=''
        tab_total['suggested_action']=''
        check_column_df = pd.DataFrame.from_dict(tab_val1) 
        tab_val1.append(tab_total)
        insurance_policy = pd.DataFrame.from_dict(tab_val1)
        
        accured_bonus_column = check_column_df['accured_bonus'].tolist()
        surrender_column = check_column_df['surrender_value'].tolist()
        
        accured_flag = True
        surrender_flag = True
        
        if list(set(accured_bonus_column))[0] =='' and len(list(set(accured_bonus_column)))==1:
            accured_flag = False
            
        if list(set(surrender_column))[0] =='' and len(list(set(surrender_column)))==1:
            surrender_flag = False

    except Exception as e:
        print(e)
        return None
    
    #//*---LOOP FOR TABLE---*//
    if insurance_policy.empty:
        return None   
    
    if accured_flag == True and surrender_flag == True:
        policy_detail_rect_w = 970
        policy_detail_text_w = 930
        
        policy_eval_rect_x = 1090
        policy_eval_rect_w = 710
        policy_eval_text_x = 1110
        policy_eval_text_w = 670
        
        policy_name_rect_w = 210
        policy_name_text_w = 170
        
        plan_type_x = 330

        start_date_x = 500
        policy_tenure_x = 630
        annual_premium_x = 740
        life_cover_x = 870
        accured_bonus_x = 980
        premium_td_x = 1090
        premium_payb_x = 1239
        suggested_action_rect_x = 1389
        suggested_action_rect_w = 206
        suggested_action_text_x = 1409
        suggested_action_text_w = 166
        surrender_value_x = 1595
        
    elif accured_flag == False and surrender_flag == True: 
        policy_detail_rect_w = 970
        policy_detail_text_w = 930
        
        policy_eval_rect_x = 1090
        policy_eval_rect_w = 710
        policy_eval_text_x = 1110
        policy_eval_text_w = 670
        
        policy_name_rect_w = 320
        policy_name_text_w = 280
        
        plan_type_x = 440
        start_date_x = 610
        policy_tenure_x = 740
        annual_premium_x = 850
        life_cover_x = 980
        accured_bonus_x = 0
        premium_td_x = 1090
        premium_payb_x = 1239
        suggested_action_rect_x = 1389
        suggested_action_rect_w = 206
        suggested_action_text_x = 1409
        suggested_action_text_w = 166
        surrender_value_x = 1595
 
    elif accured_flag == True and surrender_flag == False: 
        policy_detail_rect_w = 1070
        policy_detail_text_w = 1030
        
        policy_eval_rect_x = 1190
        policy_eval_rect_w = 610
        policy_eval_text_x = 1210
        policy_eval_text_w = 570

        policy_name_rect_w = 310
        policy_name_text_w = 270
        plan_type_x = 430
        start_date_x = 600
        policy_tenure_x = 730
        annual_premium_x = 840
        life_cover_x = 970
        accured_bonus_x = 1080
        premium_td_x = 1190
        premium_payb_x = 1339
        suggested_action_rect_x = 1489
        suggested_action_rect_w = 311
        suggested_action_text_x = 1509
        suggested_action_text_w = 271
        surrender_value_x = 0

    elif accured_flag == False and surrender_flag == False: 
        policy_detail_rect_w = 970
        policy_detail_text_w = 930
        
        policy_eval_rect_x = 1090
        policy_eval_rect_w = 710
        policy_eval_text_x = 1110
        policy_eval_text_w = 670
        
        policy_name_rect_w = 320
        policy_name_text_w = 280
        
        plan_type_x = 440
        start_date_x = 610
        policy_tenure_x = 740
        annual_premium_x = 850
        life_cover_x = 980
        accured_bonus_x = 0
        premium_td_x = 1090
        premium_payb_x = 1239
        suggested_action_rect_x = 1389
        suggested_action_rect_w = 411
        suggested_action_text_x = 1409
        suggested_action_text_w = 371
        surrender_value_x = 0
    else: 
        policy_detail_rect_w = 970
        policy_detail_text_w = 930
        policy_eval_rect_x = 1090
        policy_eval_rect_w = 710
        policy_eval_text_x = 1110
        policy_eval_text_w = 670
        policy_name_rect_w = 320
        policy_name_text_w = 280
        plan_type_x = 440
        start_date_x = 500
        policy_tenure_x = 630
        annual_premium_x = 740
        life_cover_x = 870
        accured_bonus_x = 980
        premium_td_x = 1090
        premium_payb_x = 1239
        suggested_action_rect_x = 1389
        suggested_action_rect_w = 206
        suggested_action_text_x = 1409
        suggested_action_text_w = 166
        surrender_value_x = 1595

    
    def insur_page_create(pdf,accured_flag,surrender_flag):
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

        #//*----Life Insurance Policy Evaluation----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(820), px2MM(84),'Life Insurance Policy Evaluation',align='L')
        
        pdf.set_xy(px2MM(943),px2MM(94)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(470), px2MM(56),'(Excluding Term Insurance)',align='L')
        
        desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
        pdf.set_xy(px2MM(405), px2MM(1039))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(1110),px2MM(21),desc_text,border=0,align="C")
        
        #//*---Top Black box
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F') 
        
        
        #//*---Table Column Name--*//
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        
        #//*--Heading Col 
        pdf.rect(px2MM(120), px2MM(204), px2MM(policy_detail_rect_w), px2MM(52),'FD')
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(140),px2MM(216)) 
        pdf.cell(px2MM(policy_detail_text_w), px2MM(28),'Policy Details',align='C')
        
        pdf.rect(px2MM(policy_eval_rect_x), px2MM(204), px2MM(policy_eval_rect_w), px2MM(52),'FD')
        pdf.set_xy(px2MM(policy_eval_text_x),px2MM(216)) 
        pdf.cell(px2MM(policy_eval_text_w), px2MM(28),'Policy Evaluation',align='C')
        
        #//*--Col 1
        pdf.rect(px2MM(120), px2MM(256), px2MM(policy_name_rect_w), px2MM(124),'FD')
        pdf.set_xy(px2MM(140),px2MM(304)) 
        pdf.cell(px2MM(policy_name_text_w), px2MM(28),'Policy Name',align='L')
        
        #//*--Col 2
        pdf.rect(px2MM(plan_type_x), px2MM(256), px2MM(170), px2MM(124),'FD')
        pdf.set_xy(px2MM(plan_type_x+20),px2MM(304)) 
        pdf.cell(px2MM(130), px2MM(28),'Plan Type',align='L')
        
        #//*--Col 3
        pdf.rect(px2MM(start_date_x), px2MM(256), px2MM(130), px2MM(124),'FD')
        pdf.set_xy(px2MM(start_date_x+10),px2MM(304)) 
        pdf.cell(px2MM(100), px2MM(28),'Start Date',align='C')
        
        #//*--Col 4
        pdf.rect(px2MM(policy_tenure_x), px2MM(256), px2MM(110), px2MM(124),'FD')
        pdf.set_xy(px2MM(policy_tenure_x+20),px2MM(290)) 
        pdf.multi_cell(px2MM(70), px2MM(28),'Policy Tenure',align='R')
        
        #//*--Col 5
        pdf.rect(px2MM(annual_premium_x), px2MM(256), px2MM(130), px2MM(124),'FD')
        pdf.set_xy(px2MM(annual_premium_x+20),px2MM(290)) 
        pdf.multi_cell(px2MM(95), px2MM(28),'Annual Premium* ',align='R')
        
        #//*--Col 6
        pdf.rect(px2MM(life_cover_x), px2MM(256), px2MM(110), px2MM(124),'FD')
        pdf.set_xy(px2MM(life_cover_x+20),px2MM(290)) 
        pdf.multi_cell(px2MM(75), px2MM(28),'Life Cover',align='R')
        
        #//*--Col 6
        if accured_flag == True:
            pdf.rect(px2MM(accured_bonus_x), px2MM(256), px2MM(110), px2MM(124),'FD')
            pdf.set_xy(px2MM(accured_bonus_x+20),px2MM(290)) 
            pdf.multi_cell(px2MM(80), px2MM(28),'Accrued Bonus ',align='R')
            
        #//*--Col 7
        pdf.rect(px2MM(premium_td_x), px2MM(256), px2MM(149), px2MM(124),'FD')
        pdf.set_xy(px2MM(premium_td_x+10),px2MM(276)) 
        pdf.multi_cell(px2MM(120), px2MM(28),'Premium paid till date amount',align='R')
        
        #//*--Col 8
        pdf.rect(px2MM(premium_payb_x), px2MM(256), px2MM(150), px2MM(124),'FD')
        pdf.set_xy(px2MM(premium_payb_x+20),px2MM(290)) 
        pdf.multi_cell(px2MM(110), px2MM(28),'Premium Payable',align='R')
        
        #//*--Col 9
        pdf.rect(px2MM(suggested_action_rect_x), px2MM(256), px2MM(suggested_action_rect_w), px2MM(124),'FD')
        pdf.set_xy(px2MM(suggested_action_text_x),px2MM(304)) 
        pdf.cell(px2MM(suggested_action_text_w), px2MM(28),'Suggested Action',align='L')

        #//*--Col 10
        if surrender_flag == True:
            pdf.rect(px2MM(surrender_value_x), px2MM(256), px2MM(205), px2MM(124),'FD')
            pdf.set_xy(px2MM(surrender_value_x+20),px2MM(304)) 
            pdf.cell(px2MM(165), px2MM(28),'Surrender Value**',align='R')

        
        
    insur_page_create(pdf,accured_flag,surrender_flag)    
    rect_y = mm2PX(pdf.get_y())+63
    text_y = rect_y+15
    col = '#F3F6F9'
    
    for i in range(len(insurance_policy)):

        if 1080-rect_y < 182 and i != len(insurance_policy)-2:
            insur_page_create(pdf,accured_flag,surrender_flag)  
            rect_y = mm2PX(pdf.get_y())+63
            text_y = rect_y+15
            col = '#F3F6F9'
            
        elif 1080-rect_y < 252 and i == len(insurance_policy)-2:
            insur_page_create(pdf,accured_flag,surrender_flag)  
            rect_y = mm2PX(pdf.get_y())+63
            text_y = rect_y+15
            col = '#F3F6F9'
            
        h_rect = 58
        h_text = w1 = w2 = 28
        gp = 15
        suggested_action_y_gap = 0
        
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(20))

        line_tupple = (multicell_height(pdf,insurance_policy["policy_name"].iloc[i],policy_name_text_w),multicell_height(pdf,insurance_policy["suggested_action"].iloc[i],suggested_action_text_w))
        max_line = max(line_tupple)
        
        h_rect = 28*max_line+30
        h_text = 28*max_line
        w1 = 28*max_line/multicell_height(pdf,insurance_policy["policy_name"].iloc[i],policy_name_text_w-6)
        if line_tupple[1]==1:
            w2 = h_text
        else:
            w2 = 28
            
        if line_tupple[0]==3 and line_tupple[1]==2:
            suggested_action_y_gap=20


        if i == (len(insurance_policy)-1):
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(20))
            pdf.set_fill_color(*hex2RGB('#B9BABE'))
            pdf.set_draw_color(*hex2RGB('#B9BABE'))
            pdf.set_line_width(px2MM(1))
            pdf.rect(px2MM(120), px2MM(rect_y), px2MM(1680), px2MM(1),'FD')
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.set_draw_color(*hex2RGB('#E9EAEE'))
            pdf.set_line_width(px2MM(0.2))
            pdf.rect(px2MM(120), px2MM(rect_y+1), px2MM(1680), px2MM(h_rect),'FD')
        else: 
            pdf.set_fill_color(*hex2RGB(col))
            pdf.rect(px2MM(120), px2MM(rect_y), px2MM(policy_name_rect_w), px2MM(h_rect),'FD')
            pdf.rect(px2MM(plan_type_x), px2MM(rect_y), px2MM(170), px2MM(h_rect),'FD')
            pdf.rect(px2MM(start_date_x), px2MM(rect_y), px2MM(130), px2MM(h_rect),'FD')
            pdf.rect(px2MM(policy_tenure_x), px2MM(rect_y), px2MM(110), px2MM(h_rect),'FD')
            pdf.rect(px2MM(annual_premium_x), px2MM(rect_y), px2MM(130), px2MM(h_rect),'FD')
            pdf.rect(px2MM(life_cover_x), px2MM(rect_y), px2MM(110), px2MM(h_rect),'FD')
            if accured_flag == True:
                pdf.rect(px2MM(accured_bonus_x), px2MM(rect_y), px2MM(110), px2MM(h_rect),'FD')

            pdf.rect(px2MM(premium_td_x), px2MM(rect_y), px2MM(149), px2MM(h_rect),'FD')
            pdf.rect(px2MM(premium_payb_x), px2MM(rect_y), px2MM(150), px2MM(h_rect),'FD')
            pdf.rect(px2MM(suggested_action_rect_x), px2MM(rect_y), px2MM(suggested_action_rect_w), px2MM(h_rect),'FD')
            if surrender_flag == True:
                pdf.rect(px2MM(surrender_value_x), px2MM(rect_y), px2MM(205), px2MM(h_rect),'FD')
        
        #//*--Col 1
        pdf.set_xy(px2MM(140),px2MM(text_y)) 
        pdf.multi_cell(px2MM(policy_name_text_w), px2MM(w1),insurance_policy["policy_name"].iloc[i],align='L')
        
        #//*--Col 2
        pdf.set_xy(px2MM(plan_type_x+20),px2MM(text_y)) 
        pdf.multi_cell(px2MM(150), px2MM(h_text),insurance_policy["plan_type"].iloc[i],align='L')
        
        #//*--Col 3
        pdf.set_xy(px2MM(start_date_x+10),px2MM(text_y)) 
        pdf.multi_cell(px2MM(120), px2MM(h_text),insurance_policy["start_date"].iloc[i],align='C')
        
        #//*--Col 4
        pdf.set_xy(px2MM(policy_tenure_x+20),px2MM(text_y)) 
        pdf.multi_cell(px2MM(80), px2MM(h_text),insurance_policy["policy_tenure"].iloc[i],border='0',align='R')
        
        #//*--Col 5
        pdf.set_xy(px2MM(annual_premium_x+20),px2MM(text_y)) 
        if insurance_policy["annual_premium"].iloc[i] == "":
            pdf.multi_cell(px2MM(90), px2MM(h_text),'-',align='R')
        else:   
            val1 = '₹ '+str(format_cash2(float(insurance_policy["annual_premium"].iloc[i])))
            pdf.multi_cell(px2MM(90), px2MM(h_text),val1,align='R')
        
        #//*--Col 6    
        pdf.set_xy(px2MM(life_cover_x+10),px2MM(text_y)) 
        if insurance_policy["life_cover"].iloc[i] == "":
            pdf.multi_cell(px2MM(80), px2MM(h_text),'-',align='R')
        else:
            val1 = '₹ '+str(format_cash2(float(insurance_policy["life_cover"].iloc[i])))
            pdf.multi_cell(px2MM(80), px2MM(h_text),val1,align='R')
            
        #//*--Col 6   
        if accured_flag == True: 
            pdf.set_xy(px2MM(accured_bonus_x+20),px2MM(text_y)) 
            if insurance_policy["accured_bonus"].iloc[i] == "":
                pdf.multi_cell(px2MM(80), px2MM(h_text),'-',align='R')
            else:
                val1 = '₹ '+str(format_cash2(float(insurance_policy["accured_bonus"].iloc[i])))
                pdf.multi_cell(px2MM(80), px2MM(h_text),val1,align='R')
                
        #//*--Col 7
        pdf.set_xy(px2MM(premium_td_x+20),px2MM(text_y)) 
        if insurance_policy["premium_paid_till_date"].iloc[i]=="":
            pdf.multi_cell(px2MM(114), px2MM(h_text),"-",align='R')
        else:
            val1 = '₹ '+str(format_cash2(float(insurance_policy["premium_paid_till_date"].iloc[i])))
            pdf.multi_cell(px2MM(114), px2MM(h_text),val1,align='R')
                   
        #//*--Col 8
        pdf.set_xy(px2MM(premium_payb_x+20),px2MM(text_y)) 
        if insurance_policy["premium_payable"].iloc[i]=="":
            pdf.multi_cell(px2MM(110), px2MM(h_text),"-",align='R')
        else:
            val = '₹ '+str(format_cash3(float(insurance_policy["premium_payable"].iloc[i])))
            pdf.multi_cell(px2MM(110), px2MM(h_text),val,align='R')
            
            
        #//*--Col 9
        pdf.set_xy(px2MM(suggested_action_text_x),px2MM(text_y+suggested_action_y_gap)) 
        pdf.multi_cell(px2MM(suggested_action_text_w), px2MM(w2),insurance_policy["suggested_action"].iloc[i],align='L')
        
        #//*--Col 10
        if surrender_flag == True:
            pdf.set_xy(px2MM(surrender_value_x+10),px2MM(text_y)) 
            if insurance_policy["surrender_value"].iloc[i]== "":
                pdf.multi_cell(px2MM(170), px2MM(h_text),'-',align='R')    
            elif insurance_policy["surrender_value"].iloc[i].isdigit() or (insurance_policy["surrender_value"].iloc[i].count('.') == 1 and insurance_policy["surrender_value"].iloc[i].replace('.', '').isdigit()):
                if i == (len(insurance_policy)-1):
                    val = '~ ₹ '+str(format_cash3(float(insurance_policy["surrender_value"].iloc[i])))
                    pdf.multi_cell(px2MM(170), px2MM(h_text),val,align='R')
                else:
                    val = '₹ '+str(format_cash3(float(insurance_policy["surrender_value"].iloc[i])))
                    pdf.multi_cell(px2MM(170), px2MM(h_text),val,align='R')  
            else:
                pdf.multi_cell(px2MM(170), px2MM(h_text),insurance_policy["surrender_value"].iloc[i],align='R')
                


        if col == '#F3F6F9':
            col = '#FFFFFF'
        else:
            col = '#F3F6F9'
            
        rect_y=mm2PX(pdf.get_y())+gp
        text_y=rect_y+15
        
        
        #//*-----Index Text of Page--**////
        
        # desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
        # pdf.set_xy(px2MM(405), px2MM(1039))
        # pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
        # pdf.set_text_color(*hex2RGB('#000000'))
        # pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C")
        
        rem_y = mm2PX(pdf.get_y())+57
    
        pdf.set_xy(px2MM(1870), px2MM(1018))  
        pdf.set_font('LeagueSpartan-Light', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(20), px2MM(42),str(pdf.page_no()),align='R')
        
        
        
    #//*----Add page for comments----*//
        
    def ins_page_add(pdf):
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

        #//*----Life Insurance Policy Evaluation----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(820), px2MM(84),'Life Insurance Policy Evaluation',align='L')
        
        pdf.set_xy(px2MM(943),px2MM(94)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(470), px2MM(56),'(Excluding Term Insurance)',align='L')
        
        #//*---Top Black box
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F') 
        
        #//*-----Index Text of Page--**////
        rem_y = mm2PX(pdf.get_y())+120
        index_text(pdf,'#1A1A1D') 
        return rem_y

    # suggested_action = list(set(insurance_policy["suggested_action"].tolist()))
    # suggested_action = [x.lower() for x in suggested_action]
    pt_no = 1
 

    #//*---1st Comment----*//
    tab_comments = ['* All premium amounts are converted to annual figures based on the frequency of premium payments (quarterly, semi-annual, etc.)','** Surrender value is an estimate derived from the general surrender value factor applied to insurance policies in case of surrender. The total surrender value excludes ULIPs and Annuities.']
    if not (1080-rem_y) > 100 :
        rem_y = ins_page_add(pdf)
        
    for i in range(2):
        pdf.set_font('LeagueSpartan-Light', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(120),px2MM(rem_y)) 
        pdf.cell(px2MM(1680), px2MM(25),tab_comments[i],align='L')
        rem_y = mm2PX(pdf.get_y())+35
        
    #//*-------------Main Comments------------------*///
    
    if not (1080-rem_y) > 400:
            rem_y = ins_page_add(pdf)
    else:
        rem_y = mm2PX(pdf.get_y())+75
        
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_xy(px2MM(120),px2MM(rem_y)) 
    pdf.cell(px2MM(170), px2MM(56),'Comments',align='L')
    
    comments = json_data["insurance_policy_evaluation"]['comment']
    rem_y = mm2PX(pdf.get_y())+86
    
    for i in range(len(comments)):
        
        # if i == 1:
        #     break
        
        if not (1080-rem_y) > 295:
            rem_y = ins_page_add(pdf)

        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(120),px2MM(rem_y)) 
        pdf.cell(px2MM(20), px2MM(42),str(pt_no)+'.',align='L')
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_xy(px2MM(150),px2MM(rem_y)) 
        pdf.cell(px2MM(200), px2MM(42),'For policies where,',align='L')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_xy(px2MM(385),px2MM(rem_y)) 
        str_w = mm2PX(pdf.get_string_width(comments[i]['suggested_action']))
        pdf.cell(px2MM(str_w+30), px2MM(42),'"'+comments[i]['suggested_action']+'"',align='L')
        
        rem_x = mm2PX(pdf.get_x())
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_xy(px2MM(rem_x),px2MM(rem_y)) 
        pdf.cell(px2MM(250), px2MM(42),"is suggested:",align='L')
        
        rem_y = mm2PX(pdf.get_y())+72
        
        for j in range(len(comments[i]['points'])):
            
            if not (1080-rem_y) > 220:
                rem_y = ins_page_add(pdf)

                
            pdf.set_fill_color(*hex2RGB('#000000'))
            pdf.rect(px2MM(150), px2MM(rem_y+20), px2MM(10), px2MM(10),'F')
            
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.set_xy(px2MM(180),px2MM(rem_y)) 
            pdf.cell(px2MM(160), px2MM(42),comments[i]['points'][j]['plan_type']+':',align='L')
            
            rem_y = mm2PX(pdf.get_y())+52
            
            for k in range(len(comments[i]['points'][j]['description'])):
                pdf.circle(x=px2MM(180), y=px2MM(rem_y+14), r=px2MM(7), style='F')
                pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
                pdf.set_xy(px2MM(200),px2MM(rem_y)) 
                pdf.multi_cell(px2MM(1590), px2MM(42),comments[i]['points'][j]['description'][k],align='L')
                
                rem_y = mm2PX(pdf.get_y())
                
            rem_y = mm2PX(pdf.get_y())+16
            
        rem_y = mm2PX(pdf.get_y())+30
        pt_no+=1
        
                    
    
    # #//*------Recommendation Summary Page------------*//    
    # try:
    #     tab_val2 = json_data["insurance_policy_evaluation"]['recommendation_table']
    #     if tab_val2==[]:
    #         return None
    # except Exception as e:
    #     return None 
    
    # insurance_policy_recommendation = pd.DataFrame.from_dict(tab_val2)
    # if insurance_policy_recommendation.empty:
    #     return None
    
    # plan = insurance_policy_recommendation['plan'].tolist()
    # cover = insurance_policy_recommendation['cover'].tolist()
    # annual_premium = insurance_policy_recommendation['annual_premium'].tolist()
    
    
    # rem_y = mm2PX(pdf.get_y())+40

    
    # if not 1080-rem_y > 635:
        
    #     pdf.add_page()
    #     pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    #     pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #     #//*----Life Insurance Policy Evaluation----*//
    #     pdf.set_xy(px2MM(120),px2MM(80)) 
    #     pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    #     pdf.set_text_color(*hex2RGB('#1A1A1D'))
    #     pdf.cell(px2MM(820), px2MM(84),'Life Insurance Policy Evaluation',align='L')
        
    #     pdf.set_xy(px2MM(943),px2MM(94)) 
    #     pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
    #     pdf.set_text_color(*hex2RGB('#1A1A1D'))
    #     pdf.cell(px2MM(470), px2MM(56),'(Excluding Term Insurance)',align='L')
        
    #     #//*---Top Black box
    #     pdf.set_fill_color(*hex2RGB('#000000'))
    #     pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F') 
        
    #     rem_y = 0
    # else:
    #     rem_y = mm2PX(pdf.get_y())-154
        
        
    
    # #//*----Heading Statements----*//
    # statement1 = "By separating your insurance and investment needs, you can increase your life coverage significantly (with term insurance) and earn better returns on your investments (with instruments like mutual funds)."
    # statement2 = "Refer to our “Financial Products Featured List” section for high-quality term insurance and mutual fund options."
    
    # pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    # pdf.set_text_color(*hex2RGB('#000000'))
    # pdf.set_xy(px2MM(120),px2MM(204+rem_y)) 
    # pdf.multi_cell(px2MM(1680), px2MM(42),statement1,align='L')
    
    # pdf.set_xy(px2MM(120),px2MM(308+rem_y)) 
    # pdf.multi_cell(px2MM(1680), px2MM(42),statement2,align='L')
    
    # pdf.set_fill_color(*hex2RGB('#313236'))
    # pdf.rect(px2MM(120), px2MM(410+rem_y), px2MM(315), px2MM(42),'F') 
    # pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    # pdf.set_text_color(*hex2RGB('#FFFFFF'))
    # pdf.set_xy(px2MM(135),px2MM(415+rem_y)) 
    # pdf.multi_cell(px2MM(300), px2MM(32),'Recommendation Summary',align='L')
    
    # pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    # pdf.set_line_width(px2MM(0.02))
    
    # #//*---Table Rectangles---*//
    # for i in range(3):
    #     if i == 1:
    #         pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    #     else:
    #         pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    #     pdf.rect(px2MM(120), px2MM(452+(i*52)+rem_y), px2MM(646), px2MM(52),'FD') 
    #     pdf.rect(px2MM(766), px2MM(452+(i*52)+rem_y), px2MM(517), px2MM(52),'FD') 
    #     pdf.rect(px2MM(1283), px2MM(452+(i*52)+rem_y), px2MM(517), px2MM(52),'FD')
        
    # #//*---For last Row (Full White)    
    # pdf.set_fill_color(*hex2RGB('#B9BABE'))
    # pdf.set_draw_color(*hex2RGB('#B9BABE'))
    # pdf.set_line_width(px2MM(1))
    # # pdf.rect(px2MM(126), px2MM(mm2PX(tot_height)+43), px2MM(1674), px2MM(1),'F') 
    # # pdf.set_fill_color(*hex2RGB('#E9EAEE'))    
    # pdf.rect(px2MM(120), px2MM(608+rem_y), px2MM(1680), px2MM(1),'FD')
    # pdf.set_fill_color(*hex2RGB('#FFFFFF'))   
    # pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    # pdf.set_line_width(px2MM(0.2)) 
    # pdf.rect(px2MM(120), px2MM(609+rem_y), px2MM(1680), px2MM(52),'FD')
        
    # #//*---Column Names---------*//
    # #//*---Col 1
    # pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    # pdf.set_xy(px2MM(140),px2MM(462+rem_y)) 
    # pdf.multi_cell(px2MM(350), px2MM(32),'',align='L')
    
    # #//*---Col 2
    # pdf.set_xy(px2MM(786),px2MM(462+rem_y)) 
    # pdf.multi_cell(px2MM(477), px2MM(32),'Cover',align='C')
    
    # #//*--col 3
    # pdf.set_xy(px2MM(1303),px2MM(462+rem_y)) 
    # pdf.multi_cell(px2MM(477), px2MM(32),'Annual Premium',align='C')
    

    # for i in range(3):
    #     #//*---Field Values---------*//
    #     #//*---Col 1
    #     pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    #     pdf.set_text_color(*hex2RGB('#1A1A1D'))
    #     pdf.set_xy(px2MM(140),px2MM(514+(i*52)+rem_y)) 
    #     pdf.multi_cell(px2MM(350), px2MM(32),plan[i],align='L')
        
    #     #//*---Col 2
    #     pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))  
    #     pdf.set_xy(px2MM(786),px2MM(514+(i*52)+rem_y)) 
    #     if cover[i]== "" and i!= 2:
    #         pdf.multi_cell(px2MM(477), px2MM(32),"-",align='C')
            
    #     elif cover[i]== "" and i== 2:
    #         pdf.multi_cell(px2MM(477), px2MM(32),"",align='C')
    #     else:
    #         val1 = "₹ "+str(format_cash2(float(cover[i])))
    #         pdf.multi_cell(px2MM(477), px2MM(32),val1,border='0',align='C')
            
    #         if i == 1:
    #             deg_one = mm2PX(pdf.get_x())+3
    #             deg_one = 1024+(mm2PX(pdf.get_string_width(str(val1)))/2)
    #             pdf.set_font('LeagueSpartan-Regular', size=px2pts(9))
    #             pdf.set_xy(px2MM(deg_one),px2MM(514+(i*52)+4+rem_y)) 
    #             pdf.multi_cell(px2MM(15), px2MM(12),"1",border='0',align='L')
        
    #     #//*--col 3
    #     pdf.set_xy(px2MM(1303),px2MM(514+(i*52)+rem_y)) 
    #     if i == 2:
    #         pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    #         pdf.set_xy(px2MM(1303),px2MM(514+(i*52)+1+rem_y)) 
    #     else:
    #         pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    #     if annual_premium[i] == "" :   
    #         pdf.multi_cell(px2MM(477), px2MM(32),'-',align='C')
    #     else:
    #         if i != 0:
    #             val2 = "~ ₹ "+str(format_cash2(float(annual_premium[i])))
    #             pdf.multi_cell(px2MM(477), px2MM(32),val2,align='C')
    #         else:
    #             val2 = "₹ "+str(format_cash2(float(annual_premium[i])))
    #             pdf.multi_cell(px2MM(477), px2MM(32),val2,align='C')
            
    #         deg_two = 1541+(mm2PX(pdf.get_string_width(str(val2)))/2)    
    #         pdf.set_font('LeagueSpartan-Regular', size=px2pts(9))
    #         if i == 1:
    #             pdf.set_xy(px2MM(deg_two),px2MM(514+(i*52)+4+rem_y)) 
    #             pdf.multi_cell(px2MM(15), px2MM(12),"2",border='0',align='L')
    #         elif i ==2:
    #             pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(9))
    #             pdf.set_xy(px2MM(deg_two),px2MM(514+(i*52)+4+rem_y)) 
    #             pdf.multi_cell(px2MM(15), px2MM(12),"3",border='0',align='L')
            
    # #//*---Comments----*//
    # comments = ["Estimated based on your need-based analysis, considering the identified mortality protection gap.","Estimated using your age, gender, the above cover, and coverage until the age of 65 years, for an affordable policy. The exact premium may vary depending on other factors like policy tenure, cover amount, life insurer, etc.","Net savings in premiums can be reinvested in high-quality instruments."]
    # comm_num = [1,2,3]
    # for i in range(3) :
    #     pdf.set_font('LeagueSpartan-Light', size=px2pts(8))
    #     pdf.set_xy(px2MM(120),px2MM(697+(i*25)+10+rem_y)) 
    #     pdf.multi_cell(px2MM(15), px2MM(25),str(comm_num[i]),align='L')
        
    #     pdf.set_font('LeagueSpartan-Light', size=px2pts(18))
    #     pdf.set_xy(px2MM(127),px2MM(700+(i*25)+10+rem_y)) 
    #     pdf.multi_cell(px2MM(1680), px2MM(25),comments[i],align='L')
        
    # #//*-----Index Text of Page--**////
    # index_text(pdf,'#1A1A1D')
        
#//*--------------Surrender Impact-------------*//
def life_insurance_evaluation_summary(pdf,json_data,c_MoneyS,money_signData):
    try:
        life_insurance_evaluation_summary = json_data['life_insurance_evaluation_summary']
        tab_val1 = life_insurance_evaluation_summary['traditional_life_insurace_table']
        tab_val2 = life_insurance_evaluation_summary['term_insurance_table']
        
        if life_insurance_evaluation_summary=={}:
            return None
        
        
    except Exception as e:
        print(e)
        return None 
    
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    #//*----Featured List of Financial Products----*//
    pdf.set_xy(px2MM(120),px2MM(80)) 
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(800), px2MM(84),'Life Insurance Evaluation Summary',align='L')
            
    #//*---Top Black box
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F') 
    
    index_text(pdf,'#1A1A1D')
    
    pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_xy(px2MM(120), px2MM(204))
    pdf.multi_cell(px2MM(1680),px2MM(32),'By separating your insurance and investment needs, you can increase your life coverage significantly (with term insurance) and earn better returns on your investments (with instruments like mutual funds).',border=0,align="L")
        
    pdf.set_xy(px2MM(120), px2MM(278))
    pdf.multi_cell(px2MM(1680),px2MM(32),'Refer to the "References" file in DocuLocker for high-quality Term Insurance and Mutual Fund options.',border=0,align="L")
    
    if life_insurance_evaluation_summary.get('your_coverage_status'):
        pdf.set_text_color(*hex2RGB('#FFFFFF'))
        pdf.set_font('Inter-Medium', size=px2pts(24))
        ycs_x = 1155
        if life_insurance_evaluation_summary['your_coverage_status']:
            if life_insurance_evaluation_summary['your_coverage_status'].lower() == 'sufficiently insured':
                pdf.set_fill_color(*hex2RGB('#166533'))
                pdf.rect(px2MM(1515), px2MM(370), px2MM(285), px2MM(44),'F')
                pdf.set_xy(px2MM(1515), px2MM(371))
                pdf.cell(px2MM(285),px2MM(44),life_insurance_evaluation_summary['your_coverage_status'],align="C")
                impact_premium_rect = '#F0FDF5'
                impact_premium_border = '#DDEAE3'
                impact_premium_text = '#16A349'
                ycs_x = 1155
            elif life_insurance_evaluation_summary['your_coverage_status'].lower() == 'under insured':
                pdf.set_fill_color(*hex2RGB('#991B1B'))
                pdf.rect(px2MM(1583), px2MM(370), px2MM(217), px2MM(44),'F')
                pdf.set_xy(px2MM(1583), px2MM(371))
                pdf.cell(px2MM(217),px2MM(44),life_insurance_evaluation_summary['your_coverage_status'],align="C")
                impact_premium_rect = '#F0FDF5'
                impact_premium_border = '#DDEAE3'
                impact_premium_text = '#16A349'
                ycs_x = 1223
            elif life_insurance_evaluation_summary['your_coverage_status'].lower() == 'over insured':
                pdf.set_fill_color(*hex2RGB('#991B1B'))
                pdf.rect(px2MM(1583), px2MM(370), px2MM(217), px2MM(44),'F')
                pdf.set_xy(px2MM(1583), px2MM(371))
                pdf.cell(px2MM(217),px2MM(44),life_insurance_evaluation_summary['your_coverage_status'],align="C")
                impact_premium_rect = '#FEF2F2'
                impact_premium_border = '#FEE2E2'
                impact_premium_text = '#DC2626'
                ycs_x = 1223
                
        pdf.set_xy(px2MM(ycs_x), px2MM(374))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(310),px2MM(36),'Your Coverage Status',border=0,align="L")
    
    tab_x = 0
    if tab_val1 :
        pdf.set_draw_color(*hex2RGB('#E5EBF2'))
        pdf.set_line_width(px2MM(0.2))   
        pdf.set_fill_color(*hex2RGB('#F5F5F5'))
        pdf.rect(px2MM(120), px2MM(444), px2MM(825), px2MM(52),'FD')
        
        # table 1 rectangle
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(120), px2MM(496), px2MM(825), px2MM(72),'FD')
        pdf.rect(px2MM(120), px2MM(568), px2MM(825), px2MM(72),'FD')
        pdf.rect(px2MM(120), px2MM(640), px2MM(825), px2MM(72),'FD')
        
        # table headers
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    
        pdf.set_xy(px2MM(140), px2MM(454))
        pdf.cell(px2MM(420),px2MM(32),'Traditional Life Insurance',align="L")
        
        pdf.set_xy(px2MM(604), px2MM(454))
        pdf.cell(px2MM(140),px2MM(32),'Sum Assured',align="C")
         
        pdf.set_xy(px2MM(800), px2MM(454))
        pdf.cell(px2MM(100),px2MM(32),'Premium',align="C")
        
        
        # table 1 values
        y = 516
        for i in range(3):
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            if i==2:
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            else:
                pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            
            pdf.set_xy(px2MM(140), px2MM(y))
            pdf.cell(px2MM(420),px2MM(32),tab_val1[i]['traditional_life_insurace'],align="L")
            
            pdf.set_xy(px2MM(590), px2MM(y))
            locale.setlocale(locale.LC_ALL, 'en_IN.UTF-8')
            if tab_val1[i]['sum_assured'] == '-' or tab_val1[i]['sum_assured'] == '0':
                pdf.cell(px2MM(172),px2MM(32),'-',align="C")
            else:   
                sa = str(locale.currency(float(tab_val1[i]['sum_assured']), grouping=True))
                sa = sa.split('.')[0].replace('₹','₹ ')
                pdf.cell(px2MM(172),px2MM(32),sa,align="C")
            
            pdf.set_xy(px2MM(772), px2MM(y))
            if tab_val1[i]['premium'] == '-' or tab_val1[i]['premium'] == '0':
                pdf.cell(px2MM(172),px2MM(32),'-',align="C")
            else:   
                prem = str(locale.currency(float(tab_val1[i]['premium']), grouping=True))
                prem = prem.split('.')[0].replace('₹','₹ ')
                pdf.cell(px2MM(172),px2MM(32),prem,align="C")
                
            y+=72
        tab_x=855
                        
            
    if tab_val2 :
        pdf.set_draw_color(*hex2RGB('#E5EBF2'))
        pdf.set_line_width(px2MM(0.2))   
        pdf.set_fill_color(*hex2RGB('#F5F5F5'))
        pdf.rect(px2MM(120+tab_x), px2MM(444), px2MM(825), px2MM(52),'FD')
        
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        # table 2 rectangle
        pdf.rect(px2MM(120+tab_x), px2MM(496), px2MM(825), px2MM(72),'FD')
        pdf.rect(px2MM(120+tab_x), px2MM(568), px2MM(825), px2MM(72),'FD')
        pdf.rect(px2MM(120+tab_x), px2MM(640), px2MM(825), px2MM(72),'FD')
        
        # table headers
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            
        pdf.set_xy(px2MM(140+tab_x), px2MM(454))
        pdf.cell(px2MM(420),px2MM(32),'Term Insurance',align="L")
        
        
        pdf.set_xy(px2MM(604+tab_x), px2MM(454))
        pdf.cell(px2MM(140),px2MM(32),'Sum Assured',align="C")  
        
        pdf.set_xy(px2MM(800+tab_x), px2MM(454))
        pdf.cell(px2MM(100),px2MM(32),'Premium',align="C")
            
        
        y = 516
        for i in range(3):
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            if i==2:
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            else:
                pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            
            pdf.set_xy(px2MM(140+tab_x), px2MM(y))
            pdf.cell(px2MM(420),px2MM(32),tab_val2[i]['term_insurance'],align="L")
            
            pdf.set_xy(px2MM(590+tab_x), px2MM(y))
            if tab_val2[i]['sum_assured'] == '-' or tab_val2[i]['sum_assured'] == '0':
                pdf.cell(px2MM(172),px2MM(32),'-',align="C")
            else:   
                sa = str(locale.currency(float(tab_val2[i]['sum_assured']), grouping=True))
                sa = sa.split('.')[0].replace('₹','₹ ')
                pdf.cell(px2MM(172),px2MM(32),sa,align="C")
            
            pdf.set_xy(px2MM(772+tab_x), px2MM(y))
            if tab_val2[i]['premium'] == '-' or tab_val2[i]['premium'] == '0':
                pdf.cell(px2MM(172),px2MM(32),'-',align="C")
            else:   
                if tab_val2[i]['premium'][0] == '-':
                    pdf.cell(px2MM(172),px2MM(32),tab_val2[i]['premium'],align="C")
                else:
                    prem = str(locale.currency(float(tab_val2[i]['premium']), grouping=True))
                    prem = prem.split('.')[0].replace('₹','₹ ')
                    pdf.cell(px2MM(172),px2MM(32),prem,align="C")
            y+=72
            

    
    # impact premium rectangle
    if life_insurance_evaluation_summary.get('impact_premium'):
        if (float(life_insurance_evaluation_summary['impact_premium']) < 0): 
            impact_premium_rect = '#FEF2F2'
            impact_premium_border = '#F5D0D0'
            impact_premium_text = '#DC2626'
        pdf.set_fill_color(*hex2RGB(impact_premium_rect))
        pdf.set_draw_color(*hex2RGB(impact_premium_border))
        pdf.rect(px2MM(120), px2MM(742), px2MM(1680), px2MM(80),'FD')
        
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
        pdf.set_xy(px2MM(140), px2MM(766))
        pdf.cell(px2MM(260),px2MM(36),'Impact in Premium',align="L")
        
        pdf.set_text_color(*hex2RGB('#737373'))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(16))
        pdf.set_xy(px2MM(405), px2MM(775))
        pdf.cell(px2MM(720),px2MM(19),'(Traditional Policies to be surrendered / stopped)  - (Additional Term Insurance recommended)',align="L")
        
        pdf.set_text_color(*hex2RGB(impact_premium_text))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(36))
        pdf.set_xy(px2MM(1111), px2MM(762))

        if life_insurance_evaluation_summary['impact_premium'] == '-' or life_insurance_evaluation_summary['impact_premium'] == '0':
            pdf.cell(px2MM(670),px2MM(40),'-',align="R")
            
        else:  
            if life_insurance_evaluation_summary['impact_premium'][0] == '-':
               ip = str(locale.currency(float(life_insurance_evaluation_summary['impact_premium'][1:]), grouping=True)) 
               prefix = ''
            else:
                ip = str(locale.currency(float(life_insurance_evaluation_summary['impact_premium']), grouping=True))
                prefix=''
            ip = ip.split('.')[0].replace('₹','₹ ')
            pdf.cell(px2MM(670),px2MM(40),prefix+ip,align="R")
        
    btm_text = ["Estimated based on your need-based analysis, considering the identified mortality protection gap.",
                "Estimated using your age, gender, the above cover, and coverage until the age of 65 years, for an affordable policy. The exact premium may vary depending on other factors like policy tenure, cover amount, life insurer, etc.",
                "Net savings in premiums can be reinvested in high-quality instruments."]
    
    para_y = 852
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    for i in range(len(btm_text)):
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(9))
        pdf.set_xy(px2MM(120), px2MM(para_y))
        pdf.cell(px2MM(3),px2MM(15),str(i+1),align="L")
        
        pdf.set_font('LeagueSpartan-Light', size=px2pts(18))
        pdf.set_xy(px2MM(127), px2MM(para_y))
        pdf.cell(px2MM(1680),px2MM(25),btm_text[i],align="L")
        
        para_y+=35
        
    
    

#//*-----CreditCard Evaluation----*//
def credit_card_evaluation(pdf,json_data,c_MoneyS,money_signData):
    try:
        tab_val1 = json_data["creditcard_evaluation"]
        if tab_val1==[]:
            return None
        global your_fin_analysis_sub_comment
        your_fin_analysis_sub_comment.append('Credit Card Evaluation')
    except Exception as e:
        return None 
    
    for data in tab_val1:
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

        #//*----'Credit Card Evaluation'----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(602), px2MM(84),'Credit Card Evaluation',align='L')
        
        #//*---Top Black box
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F')
        
        #//*----Main Big rect---*//
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(px2MM(120), px2MM(203.7), px2MM(1680.3), px2MM(732.5),'FD')
        
        #//*----Dark Grey Rectangular Box (TOP Left BOX 1)----*///
        
        pdf.set_fill_color(*hex2RGB('#313236'))
        pdf.rect(px2MM(120), px2MM(204), px2MM(600), px2MM(454),'F')
        
        #//*--Card Name----*//
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#FFFFFF'))
        pdf.set_xy(px2MM(150),px2MM(234)) 
        pdf.multi_cell(px2MM(540), px2MM(42),data['name'],align='L')
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(150),px2MM(320)) 
        pdf.cell(px2MM(540), px2MM(32),"Annual fee",align='L')
        
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#FFFFFF'))
        pdf.set_xy(px2MM(150),px2MM(360)) 
        pdf.multi_cell(px2MM(540), px2MM(32),data['annual_fee'],align='L')
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(150),px2MM(416)) 
        pdf.cell(px2MM(540), px2MM(32),"Best suited for",align='L')
        
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#FFFFFF'))
        pdf.set_xy(px2MM(150),px2MM(456)) 
        pdf.multi_cell(px2MM(540), px2MM(32),data['best_suited_for'],align='L')
        
        rem = mm2PX(pdf.get_y())+24
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(150),px2MM(rem)) 
        pdf.cell(px2MM(540), px2MM(32),"Rewards convertibility",align='L')
        
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#FFFFFF'))
        pdf.set_xy(px2MM(150),px2MM(rem+40)) 
        pdf.multi_cell(px2MM(540), px2MM(32),data['reward_convertibility'],align='L')
        
        
        #//*----Light Grey Rectangular Box (Bottom Left BOX 2)----*///
        pdf.set_fill_color(*hex2RGB('#B9BABE'))
        pdf.rect(px2MM(120), px2MM(662), px2MM(600), px2MM(274),'F')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(150),px2MM(692)) 
        pdf.cell(px2MM(540), px2MM(32),"Rewards Points Redemption",align='L')
        
        line_x = 150
        line_y = (780,829.35,780,829.35)
        
        for i in range(4):
            pdf.set_fill_color(*hex2RGB('#898B90'))
            pdf.rect(px2MM(line_x), px2MM(line_y[i]), px2MM(258), px2MM(1),'F')
            if i == 1:
               line_x = 432 
        
        type_x = 145  
        val_x = 334  
        type_y = (743,793,842,743,793,842)       
        val_y = (740,789.5,839,740,789.5,839)       
        type_name = ("Flights","Vouchers","Product Purchase / Shopping","Cashback","Air Miles","Hotels") 
        type_val = ("flights","vouchers","product_purchases","cashback","air_miles","hotels")
              
        for i in range(6):
            
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(20))
            pdf.set_text_color(*hex2RGB('#4B4C51'))
            pdf.set_xy(px2MM(type_x),px2MM(type_y[i])) 
            pdf.multi_cell(px2MM(180), px2MM(28),type_name[i],align='L')
                        
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.set_xy(px2MM(val_x),px2MM(val_y[i])) 
            if type_name[i] == "Air Miles": 
                pdf.multi_cell(px2MM(80), px2MM(32),data['reward_point_redemption'][type_val[i]],align='R')
            else:
                pdf.multi_cell(px2MM(80), px2MM(32),'₹ '+data['reward_point_redemption'][type_val[i]],align='R')
            
            if i == 2:
               type_x = 428
               val_x = 616
               
        
        #//*----White Rectangular Box (Right BOX 3)----*///
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(720), px2MM(204), px2MM(1080), px2MM(732),'F') 
        
        #//*---Category--//
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(750),px2MM(234)) 
        pdf.multi_cell(px2MM(1080), px2MM(42),'Category',align='L')
        
        text_y = mm2PX(pdf.get_y())+16
        
        for i in range(len(data['category'])):
            
            #//**---Description---(first printed desc to get the desc height)
            pdf.set_font('LeagueSpartan-Light', size=px2pts(20))
            pdf.set_text_color(*hex2RGB('#313236'))
            pdf.set_xy(px2MM(1002),px2MM(text_y)) 
            pdf.multi_cell(px2MM(768), px2MM(28),data['category'][i]['description'],align='L')
            
            rem = mm2PX(pdf.get_y())
            
            #//*----Name---*//
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#313236'))
            pdf.set_xy(px2MM(750),px2MM(text_y)) 
            pdf.multi_cell(px2MM(180), px2MM(rem-text_y),str(data['category'][i]['name']),align='L')
            
            #//*----God or Bad---*//
            if data['category'][i]['type'].lower() == 'good':
                pdf.image(join(cwd,'assets', 'images','credit_card','Thumbsup.png'),px2MM(954), px2MM(text_y+((rem-text_y)/2)-12), px2MM(24), px2MM(24))
            elif data['category'][i]['type'].lower() == 'bad':
                pdf.image(join(cwd,'assets', 'images','credit_card','Thumbsdown.png'),px2MM(954), px2MM(text_y+((rem-text_y)/2)-12), px2MM(24), px2MM(24))
            else:
                pdf.set_xy(px2MM(954), px2MM(text_y)) 
                pdf.multi_cell(px2MM(24), px2MM(24),'-',align='L')
            
            text_y = rem+16
            
        #//*---Complimentary Airport Lounge Access --//
        
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(750),px2MM(text_y+44)) 
        pdf.multi_cell(px2MM(490), px2MM(42),'Complimentary Airport Lounge Access',align='L')
        sub_com_x = mm2PX(pdf.get_x())-5
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(1235),px2MM(text_y+53)) 
        pdf.multi_cell(px2MM(472), px2MM(28),'(Per year at participating lounges)',align='L')
        
        text_y = mm2PX(pdf.get_y())+21
        
        for i in range(len(data['complimentary_airport_lounge_acess'])):
            pdf.set_font('LeagueSpartan-Light', size=px2pts(20))
            pdf.set_text_color(*hex2RGB('#313236'))
            pdf.set_xy(px2MM(1002),px2MM(text_y)) 
            pdf.multi_cell(px2MM(768), px2MM(28),data['complimentary_airport_lounge_acess'][i]['description'],align='L')
            
            rem = mm2PX(pdf.get_y())
            
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#313236'))
            pdf.set_xy(px2MM(750),px2MM(text_y)) 
            pdf.multi_cell(px2MM(180), px2MM(rem-text_y),str(data['complimentary_airport_lounge_acess'][i]['name']),align='L')
            
            #//*----God or Bad---*//
            if data['complimentary_airport_lounge_acess'][i]['type'].lower() == 'good':
                pdf.image(join(cwd,'assets', 'images','credit_card','Thumbsup.png'),px2MM(954), px2MM(text_y+((rem-text_y)/2)-12), px2MM(24), px2MM(24))
            elif data['complimentary_airport_lounge_acess'][i]['type'].lower() == 'bad':
                pdf.image(join(cwd,'assets', 'images','credit_card','Thumbsdown.png'),px2MM(954), px2MM(text_y+((rem-text_y)/2)-12), px2MM(24), px2MM(24))
            else:
                pdf.set_xy(px2MM(954), px2MM(text_y)) 
                pdf.multi_cell(px2MM(24), px2MM(24),'-',align='L')
            
            text_y = rem+16


        #  desclaimer = "Disclaimer: All the above schemes are Growth-Direct plans. The above featured list is based on 1 Finance's proprietary research. "
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_xy(px2MM(120),px2MM(1008))  
        desclaimer = "Disclaimer: Evaluation for each category is done by comparing card features with other cards in similar annual fees range."    
        pdf.multi_cell(px2MM(1680), px2MM(32),desclaimer,align='C')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
        





#//*-----Planning Your Estate and Will
def planning_your_esate_will(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.cell(px2MM(8018),px2MM(84),"Planning Your Estate and Will")

    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F')


    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(120), px2MM(224))
    pdf.multi_cell(px2MM(1500), px2MM(42), "Creating a will is essential for individuals who wish to distribute their assets as per their preference after their demise. In India, legal heirs differ based on religious identity, and it is crucial to understand the legalities involved in estate and will planning. Here are some key points to keep in mind:")

    pdf.set_fill_color(*hex2RGB('#000000'))

    # Rectangle Bullets in PDF.
    pdf.rect(px2MM(120),px2MM(408),px2MM(10), px2MM(10), 'F')
    pdf.rect(px2MM(120),px2MM(470),px2MM(10), px2MM(10), 'F')
    pdf.rect(px2MM(120),px2MM(574),px2MM(10), px2MM(10), 'F')
    pdf.rect(px2MM(120),px2MM(636),px2MM(10), px2MM(10), 'F')
    pdf.rect(px2MM(120),px2MM(740),px2MM(10), px2MM(10), 'F')
    
    
    
    pdf.set_xy(px2MM(150), px2MM(390))
    pdf.multi_cell(px2MM(1470),px2MM(42),"Any adult over the age of 18 with sound mind can create a will that outlines the distribution of assets.",align = "L")

    pdf.set_xy(px2MM(150), px2MM(452))
    pdf.multi_cell(px2MM(1470),px2MM(42), "Legal heirs differ based on religious identity, with Hindus following the Hindu Succession Act of 1956, Muslims following the Muslim Personal Law, and other Indians following the Indian Succession Act of 1925.",align = "L")
    
    pdf.set_xy(px2MM(150) , px2MM(556))
    pdf.multi_cell(px2MM(1470), px2MM(42), "Nominees are caretakers and not owners of the assets, and the assets will later be distributed to legal heirs.",align = "L")

    pdf.set_xy(px2MM(150), px2MM(618))
    pdf.multi_cell(px2MM(1480),px2MM(42), "Joint accounts are considered as equal ownership between individuals, so the survivor does not become the owner. Half the wealth is distributed to legal heirs or according to the will.",align = "L")

    pdf.set_xy(px2MM(150), px2MM(722))
    pdf.multi_cell(px2MM(1470),px2MM(42),"It is not mandatory for a will to be stamped, typed, or registered, and it only requires the individual's signature along with two other witnesses.",align = "L")
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')


#//*-----Building a Strong Credit Profile
def building_strong_credit_profile(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.cell(px2MM(8018),px2MM(84),"Building a Strong Credit Profile")

    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F')

    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(120), px2MM(224))
    pdf.multi_cell(px2MM(1500), px2MM(42), "A strong credit profile is critical for financial stability and securing credit. Cultivating good financial habits can help you achieve a healthy credit profile. Here are some valuable tips to consider:")

    pdf.set_fill_color(*hex2RGB('#000000'))

    # Rectangle Bullets in PDF.
    for i in range(6):
        pdf.rect(px2MM(120),px2MM(366 + (i * 104)),px2MM(10), px2MM(10), 'F')


    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(348))
    pdf.multi_cell(px2MM(500),px2MM(42), "Make timely payments - ",align = "L")

    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(475), px2MM(348))
    pdf.cell(px2MM(1470 -200),px2MM(42), "Consistently paying your bills on time demonstrates your creditworthiness and protects you")

    pdf.set_xy(px2MM(150), px2MM(348+42))
    pdf.multi_cell(px2MM(1470),px2MM(42), "from unnecessary fees.")

    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(452))
    pdf.multi_cell(px2MM(1470),px2MM(42), "Keep a credit card in use - ",align = "L")

    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(498), px2MM(452))
    pdf.multi_cell(px2MM(1470),px2MM(42), "Using a credit card responsibly can positively impact your credit score, but it is important to")

    pdf.set_xy(px2MM(150), px2MM(452+42))
    pdf.multi_cell(px2MM(1470),px2MM(42), "pay off the entire balance on time to avoid accruing debt.")
    
# _____________________________________________________________________________________________________________________________________________________

    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(556))
    pdf.multi_cell(px2MM(1470),px2MM(42), "Apply for credit mindfully - ",align = "L")

    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(512), px2MM(556))
    pdf.multi_cell(px2MM(1470),px2MM(42), "While having a healthy mix of credit lines can boost your creditworthiness, avoid applying")

    pdf.set_xy(px2MM(150), px2MM(556+42))
    pdf.multi_cell(px2MM(1470),px2MM(42), "for credit unnecessarily or having multiple rejections, which can negatively impact your credit profile.")

# ____________________________________________________________________________________________________________________________________________________

# ____________________________________________________________________________________________________________________________________________________

    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150) , px2MM(660))
    pdf.multi_cell(px2MM(1470), px2MM(42), "Always close accounts - ",align = "L")

    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(465), px2MM(660))
    pdf.multi_cell(px2MM(1470),px2MM(42), "Make timely repayments, request the return of any hypothecated documents, and verify that ")

    pdf.set_xy(px2MM(150), px2MM(660 + 42))
    pdf.multi_cell(px2MM(1470),px2MM(42), "closure letters are updated with credit bureaus.")
# ____________________________________________________________________________________________________________________________________________________

# ____________________________________________________________________________________________________________________________________________________

    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(660 + 104))
    pdf.multi_cell(px2MM(1470),px2MM(42), "Maintain aged accounts - ",align = "L")

    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(490), px2MM(660 + 104))
    pdf.multi_cell(px2MM(1470),px2MM(42), "Keep your oldest accounts open, as they can help build a longer credit history and improve")
    
    pdf.set_xy(px2MM(150), px2MM(660 + 104 + 42))
    pdf.multi_cell(px2MM(1470),px2MM(42), "your credit profile. Use your available credit lines wisely and pay them off in a timely manner.")
# ____________________________________________________________________________________________________________________________________________________

# ____________________________________________________________________________________________________________________________________________________

    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(764 + 104))
    pdf.multi_cell(px2MM(1470),px2MM(42),"Communicate with your lender - ",align = "L")

    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(578), px2MM(764 + 104))
    pdf.multi_cell(px2MM(1470),px2MM(42), "If you face any financial difficulties, be open and honest with your lender, and seek")

    pdf.set_xy(px2MM(150), px2MM(764 + 104 + 42))
    pdf.multi_cell(px2MM(1470),px2MM(42), "help when needed. Most lenders are willing to listen and provide assistance if you can demonstrate the legitimacy of your situation.")
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    global best_practices_idx
    best_practices_idx = pdf.page_no()
# ____________________________________________________________________________________________________________________________________________________

def planning_your_taxes(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.cell(px2MM(740),px2MM(84),"Planning Your Income Taxes",align='L')

    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F')


    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(120), px2MM(224))
    pdf.multi_cell(px2MM(1500), px2MM(42), "Tax planning is a crucial aspect of personal finance that cannot be overlooked. It can help you maximize your returns and minimize your tax liability. Here are some best practices that you should consider:")

    pdf.set_fill_color(*hex2RGB('#000000'))

    # Rectangle Bullets in PDF.
       # Rectangle Bullets in PDF.
    pdf.rect(px2MM(120),px2MM(366),px2MM(10), px2MM(10), 'F')
    pdf.rect(px2MM(120),px2MM(428),px2MM(10), px2MM(10), 'F')
    pdf.rect(px2MM(120),px2MM(532),px2MM(10), px2MM(10), 'F')
    pdf.rect(px2MM(120),px2MM(636),px2MM(10), px2MM(10), 'F')
    pdf.rect(px2MM(120),px2MM(740),px2MM(10), px2MM(10), 'F')

    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(348))
    pdf.cell(px2MM(340),px2MM(42), "Start tax planning early - ",align = "L")
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(490), px2MM(348))
    pdf.multi_cell(px2MM(1130),px2MM(42), "Start at the beginning of the financial year instead of waiting till the last minute.",align = "L")

    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(410))
    pdf.cell(px2MM(420),px2MM(42), "Utilize tax-saving investments - ",align = "L")
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(570), px2MM(410))
    pdf.cell(px2MM(1050),px2MM(42), "Invest in tax-saving instruments to reduce your tax liability. Refer to the 'Available ",align = "L")
    pdf.set_xy(px2MM(150), px2MM(452))
    pdf.multi_cell(px2MM(1470),px2MM(42), "Tax Deductions' table on the following pages.",align = "L")
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(514))
    pdf.cell(px2MM(470),px2MM(42), "Claim all available tax deductions - ",align = "L")
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(620), px2MM(514))
    pdf.cell(px2MM(1000),px2MM(42), "Make sure to claim all possible deductions under different sections of the Income ",align = "L")
    pdf.set_xy(px2MM(150), px2MM(556))
    pdf.multi_cell(px2MM(1470),px2MM(42), "Tax Act to reduce your tax liability. Refer to the 'Available Tax Deductions' table on the following pages.",align = "L")

    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(618))
    pdf.cell(px2MM(400),px2MM(42), "Review your salary structure -",align = "L")
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(550), px2MM(618))
    pdf.cell(px2MM(1070),px2MM(42), "Optimize your salary structure to reduce your tax liability by including components such",align = "L")
    pdf.set_xy(px2MM(150), px2MM(660))
    pdf.multi_cell(px2MM(1470),px2MM(42), "as House Rent Allowance (HRA), Leave Travel Allowance (LTA), and medical reimbursements.",align = "L")
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_xy(px2MM(150), px2MM(722))
    pdf.cell(px2MM(320),px2MM(42), "File your taxes on time -",align = "L")
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
    pdf.set_xy(px2MM(470), px2MM(722))
    pdf.cell(px2MM(1150),px2MM(42), "Ensure that you file your tax returns on time to avoid penalties and interest charges.",align = "L")
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
          
#//*----Page Written By Gurutirth 

#//*----Your Financial Profile---*//  
def fin_profile(pdf, json_data,c_MoneyS,money_signData):
     # //*---User Values---*//

    money_sign_desc = {
        "Eagle":"Far-Sighted Eagle", "Horse":"Persistent Horse",
        "Tiger":"Tactical Tiger", "Lion":"Opportunistic Lion",
        "Elephant":"Virtuous Elephant", "Turtle":"Vigilant Turtle",
        "Whale":"Enlightened Whale", "Shark":"Stealthy Shark"
    }
    

    #  generation
    try:
        # df = pd.DataFrame.from_dict(json_data["Generation Profile"])
        fin_score=json_data['oneview']['fbs']
        if fin_score==None:
            fin_score = 0
    except Exception as e:
        return None
    gen_profile = json_data['gen_profile']["gen_profile"] 

        
    # card 4 data
    age_range = json_data['gen_profile']['life_stage_age_range']
    phase = json_data['gen_profile']['life_stage']
    generation = json_data['gen_profile']['gen_profile']
    generation_desc = json_data['gen_profile']['gen_profile_desc']

    
    life_stage_pts =  json_data['gen_profile']['life_stage_desc']   
    age_range_color = money_signData[c_MoneyS]['fin_profile'][0] 
    meter_stick_xpos_dict = {20:(0, 63), 40:(70, 137), 60:(144, 211), 80:(218, 285), 100:(292, 359)}
    meter_img_dict = {20:'meter_1_20.png', 40:'meter_20_40.png', 
    60:'meter_40_60.png', 80:'meter_60_80.png', 100:'meter_80_100.png'}
    for val in meter_img_dict:
        if fin_score <= val:
            meter_img = meter_img_dict[val]
            meter_stick_xpos = (meter_stick_xpos_dict[val][1] - meter_stick_xpos_dict[val][0])/20*(fin_score - (val-20))
            meter_stick_xpos = (201 + meter_stick_xpos_dict[val][0] + meter_stick_xpos)
            if fin_score <= 20:
                score_box_xpos = 190
            elif fin_score >=81:
                score_box_xpos = 416
            else:
                score_box_xpos = meter_stick_xpos - 74
            break
    
    your_money_sign = c_MoneyS.capitalize()

   
   
    #//*---Page setup----*//
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

    vl_color = money_signData[c_MoneyS]['content'][3]
    # purple rectangle
    pdf.set_fill_color(*hex2RGB(vl_color))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')
    

    # cards
    ms_tm = 'MoneySign<sup>TM</sup>'
    card_titles = ['Financial Behaviour Score', 'MoneySign', 'Generation Profile']
    for card_num in range(3):
        # card background
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        if card_num == 2:
            card_height = 309
        else:
            card_height = 786
        pdf.rect(px2MM(120+(card_num*577)), px2MM(214), px2MM(527), px2MM(card_height), 'F')

        if card_num == 1:
        # card 2 background
            pdf.image(join(cwd,'assets','images','MoneySign',f'{your_money_sign}_text.png'),px2MM(697), px2MM(216), px2MM(527), px2MM(784))
            pdf.image(join(cwd,'assets','images','MoneySign','cream_bg_mask.png'),px2MM(697), px2MM(216), px2MM(527), px2MM(784))
            pdf.image(join(cwd,'assets','images','MoneySign',f'{your_money_sign}.png'),px2MM(810), px2MM(422), px2MM(300), px2MM(300))
            # black boxes to hide your_money_sign_bg.png vertical overflow
            pdf.set_fill_color(*hex2RGB('#000000'))
            pdf.rect(px2MM(697), px2MM(0), px2MM(527), px2MM(216), 'F')
            pdf.rect(px2MM(647), px2MM(0), px2MM(50), px2MM(1080), 'F')
            pdf.rect(px2MM(697), px2MM(1000), px2MM(527), px2MM(80), 'F')

        # card titles
        pdf.set_xy(px2MM(168+(card_num*577)), px2MM(254))  
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#000000'))


        pdf.cell(px2MM(431), px2MM(56), card_titles[card_num], align='C')
        
        # pdf.set_xy(px2MM(1048), px2MM((266)))
        # pdf.set_font('LeagueSpartan-Medium', size=16)
        # pdf.set_text_color(*hex2RGB('#000000'))
        # pdf.cell(px2MM(16), px2MM(8), 'TM')
        
        #//*--To print superscritp R 
        pdf.set_xy(px2MM(1046), px2MM(252))
        pdf.set_font('Inter-Light', size=26)
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(16), px2MM(56), '®') 

    # ------------- meter ----------------
    
    # fin score stick
    pdf.set_fill_color(*hex2RGB("#FFFFFF"))
    pdf.rect(px2MM(meter_stick_xpos), px2MM(542), px2MM(6), px2MM(95), 'F')
    # fin score box
    pdf.rect(px2MM(score_box_xpos), px2MM(430), px2MM(160), px2MM(148), 'F')

    # fin score 
    pdf.set_xy(px2MM(score_box_xpos), px2MM(464))  
    pdf.set_font('Prata', size=px2pts(64))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(160), px2MM(87), str(fin_score), align='C')

    # Actual meter image
    pdf.image(join(cwd,'assets','images','BehaviourMeter', meter_img),px2MM(190), px2MM(635), px2MM(386), px2MM(74))

    # -------------meter labels------------

    # 0 label
    pdf.set_xy(px2MM(190), px2MM(729))  
    pdf.set_font('LeagueSpartan-semiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.multi_cell(px2MM(40), px2MM(32), '0', align='L')

    # 100 label
    pdf.set_xy(px2MM(540), px2MM(729))  
    pdf.set_font('LeagueSpartan-semiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.multi_cell(px2MM(50), px2MM(32), '100', align='L')

    # # card 1 footer
    # # card footer range
    # pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    # pdf.set_xy(px2MM(160), px2MM(761))
    # pdf.cell(px2MM(63), px2MM(32), '0-50 : ', align='L')
    # pdf.set_xy(px2MM(160), px2MM(808))
    # pdf.cell(px2MM(74), px2MM(32), '50-75 : ', align='L')
    # pdf.set_xy(px2MM(160), px2MM(855))
    # pdf.cell(px2MM(83), px2MM(32), '75-100 : ', align='L')
    # # card footer range descriptions
    # pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    # pdf.set_text_color(*hex2RGB('#1A1A1D'))
    # pdf.set_xy(px2MM(233), px2MM(761))
    # pdf.cell(px2MM(213), px2MM(32), 'Financially vulnerable', align='L')
    # pdf.set_xy(px2MM(244), px2MM(808))
    # pdf.cell(px2MM(175), px2MM(32), 'Financially coping', align='L')
    # pdf.set_xy(px2MM(253), px2MM(855))
    # pdf.cell(px2MM(131), px2MM(32), 'Financially fit', align='L')

    # card 2 footer
    pdf.set_xy(px2MM(766), px2MM(782))
    pdf.set_font('Prata', size=px2pts(42))
    pdf.set_text_color(*hex2RGB('#000000'))
    # pdf.cell(px2MM(400), px2MM(66),['moneySign'], align='C')
    pdf.cell(px2MM(400), px2MM(66), json_data['money_sign']['money_sign'], align='C')

    # Money Sign Risk Category
    pdf.set_xy(px2MM(766), px2MM(870))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(16))
    pdf.set_text_color(*hex2RGB('#000000'))
    # pdf.cell(px2MM(400), px2MM(66),['moneySign'], align='C')
    pdf.cell(px2MM(400), px2MM(66), 'Your Risk Category :', align='C')

    pdf.set_xy(px2MM(766), px2MM(892))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(20))
    pdf.set_text_color(*hex2RGB('#000000'))
    # pdf.cell(px2MM(400), px2MM(66),['moneySign'], align='C')
    pdf.cell(px2MM(400), px2MM(66), json_data['money_sign']['money_sign_risk_category'], align='C')

    # card 3 content
    # --Titles
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    # generation 
    pdf.set_xy(px2MM(1313), px2MM(330))
    pdf.cell(px2MM(447), px2MM(42), generation)

    # content
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#313236'))
    pdf.set_xy(px2MM(1313), px2MM(387))
    pdf.multi_cell(px2MM(447), px2MM(32),generation_desc, align='L')

    # -----card 4
    # background
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(px2MM(1273), px2MM(563), px2MM(527), px2MM(437), 'F')

    # title
    pdf.set_xy(px2MM(1454), px2MM(603))  
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(164), px2MM(56), 'Life stage', align='C')

    # subtitle
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#1A1A1D')) 
    pdf.set_xy(px2MM(1313), px2MM(679))
    pdf.cell(px2MM(250), px2MM(42), phase, align='L')

    # label
    pdf.set_fill_color(*hex2RGB(age_range_color))
    pdf.rect(px2MM(1605), px2MM(682.5), px2MM(166), px2MM(35), 'F')
    # label text
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
    pdf.set_text_color(*hex2RGB('#000000')) 
    pdf.set_xy(px2MM(1610), px2MM(687.5))
    pdf.cell(px2MM(154), px2MM(25), f'Age Range: {age_range}', align='C')

    y_h = pdf.get_y()+13
    # bullet points
    for idx, point in enumerate(life_stage_pts):
        pdf.set_fill_color(*hex2RGB('#313236'))
        # pdf.rect(px2MM(1295), px2MM(mm2PX(y_h)+15), px2MM(5), px2MM(5), 'F')
        pdf.circle(x=px2MM(1333), y=px2MM(mm2PX(y_h)+14), r=px2MM(5), style='F')
        # text
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236')) 
        pdf.set_xy(px2MM(1353), px2MM(mm2PX(y_h)))
        pdf.multi_cell(px2MM(427), px2MM(32), point,align='L')
        y_h = pdf.get_y()
        # pdf.cell(px2MM(1334), px2MM(pdf.get_y()+32), point, align='L')

    # page tile 
    pdf.set_xy(px2MM(120), px2MM(80))  
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(792), px2MM(84), 'Your Financial Profile')
 
    #//*-----Index Text of Page--**////
    index_text(pdf,'#FFFFFF')
    global your_fin_prof_idx
    your_fin_prof_idx = pdf.page_no()

#//*----Our Assumptions------*//
def assumptions(pdf,json_data,c_MoneyS,money_signData):
    try:
        df = pd.DataFrame.from_dict(json_data["our_assumption"]['assets'])
        df2 = pd.DataFrame.from_dict(json_data["our_assumption"]['yoy_growth_to_income'])
        df3 = pd.DataFrame.from_dict(json_data["our_assumption"]['liabilities_interest_ratio'])
        
    except Exception as e:
        return None
   
    #//*---Page setup----*//
    pdf.add_page()

    # pg background color
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080), 'F')
    pdf.image(join(cwd,'assets','images','backgrounds','doubleLine.png'),px2MM(1449),px2MM(0),px2MM(471),px2MM(1080))
    # black rectangle besides title
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(80), 'F')

    # Page title
    pdf.set_xy(px2MM(120), px2MM(80))  
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.multi_cell(px2MM(441), px2MM(84), 'Our Assumptions', align='L')

    # ------cards--------------
    pdf.set_fill_color(*hex2RGB('#FFFFFF'))
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    # card 1: Asset class risk level table  card
    pdf.rect(px2MM(120), px2MM(184), px2MM(820), px2MM(752), 'FD')
    # card 2: income/expense table card
    pdf.rect(px2MM(980), px2MM(184), px2MM(820), px2MM(462), 'FD')
    

    # card 2 title
    pdf.set_xy(px2MM(1020), px2MM(224))  
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.multi_cell(px2MM(400), px2MM(32), 'Income/Expense YoY Growth', align='L')


    # ---------tables-------------------------
    # --card 1 table--
    # asset class table title row
    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    pdf.set_line_width(px2MM(0.2))
    pdf.rect(px2MM(160), px2MM(276), px2MM(177), px2MM(45), 'DF')
    pdf.rect(px2MM(337), px2MM(276), px2MM(248), px2MM(45), 'DF')
    pdf.rect(px2MM(585), px2MM(276), px2MM(119), px2MM(45), 'DF')
    pdf.rect(px2MM(704), px2MM(276), px2MM(196), px2MM(45), 'DF')  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(18))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_xy(px2MM(180),px2MM(286))
    pdf.cell(px2MM(137), px2MM(25),'Asset Classes',border=0,align='L')
    pdf.set_xy(px2MM(357),px2MM(286))
    pdf.cell(px2MM(208), px2MM(25),'Examples',border=0,align='L')
    pdf.set_xy(px2MM(605),px2MM(286))
    pdf.cell(px2MM(79), px2MM(25),'Returns %',border=0,align='L')
    pdf.set_xy(px2MM(724),px2MM(286))
    pdf.cell(px2MM(156), px2MM(25),'Risk Level',border=0,align='C')

    instrument = []
    risk_images = []
    
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
    pdf.set_xy(px2MM(160),px2MM(224))
    pdf.cell(px2MM(357), px2MM(32),'Risk/Return Profile of Asset Classes',border=0,align='L')
    
    for i in range(len(df)):
        # txt = df["Instrument 1"][i]+'\n'+df["Instrument 2"][i]+'\n'+df["Instrument 3"][i]
        txt = "\n".join(df['examples'].iloc[i])
        instrument.append(txt)
        
        if df["risk_level"][i]=="Moderate to High":
            risk_images.append('Riskmeter_m2h.png')
        elif df["risk_level"][i]=="Low to High":
            risk_images.append('Riskmeter_l2h.png')
        elif df["risk_level"][i]=="Very Low to Moderate":
            risk_images.append('Riskmeter_vl2m.png')
        elif df["risk_level"][i]=="Low to Very High":
            risk_images.append('Riskmeter_l2vh.png')
              
    table1_col_vals = [list(df['asset_class']),instrument,list(df["return_percentage"]),list(df['risk_level'])]
    risk_images = ['Riskmeter_m2h.png', 'Riskmeter_l2h.png', 'Riskmeter_l2h.png', 'Riskmeter_vl2m.png', 'Riskmeter_l2vh.png']

    pdf.set_fill_color(*hex2RGB('#F3F6F9'))
    pdf.set_draw_color(*hex2RGB('#E9EAEE'))
    col_x_pos = (160, 337, 585, 704)
    col_text_y_pos = (366, 341, 366, 391)
    col_widths = (177, 248, 119, 196)
    col_text_widths = (137, 218, 100, 166)
    for row in range(len(df)):
        for column in range(len(table1_col_vals)):
            # backgrounds
            pdf.set_draw_color(*hex2RGB('#E9EAEE'))
            if row%2 == 0:
                pdf.set_fill_color(*hex2RGB('#ffffff')) 
                pdf.rect(px2MM(col_x_pos[column]), px2MM(321+(row*115)), px2MM(col_widths[column]), px2MM(115), 'DF')
            else:
                pdf.set_fill_color(*hex2RGB('#F3F6F9'))
                pdf.rect(px2MM(col_x_pos[column]), px2MM(321+(row*115)), px2MM(col_widths[column]), px2MM(115), 'DF')
            
            # text weigth
            if column == 0 or column == 2:
                pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
            else:
                pdf.set_font('LeagueSpartan-Light', size=px2pts(18))

            # text color
            pdf.set_text_color(*hex2RGB('#000000'))

            # text positions
            if row == 2 and column == 0 or row == 4 and column == 0:
                pdf.set_xy(px2MM((col_x_pos[column])+20),px2MM(col_text_y_pos[column]+row*115-12))
            else:
                pdf.set_xy(px2MM((col_x_pos[column])+20),px2MM(col_text_y_pos[column]+row*115))
            
            # text cells
            if column == 3:
                pdf.multi_cell(px2MM(col_text_widths[column]), px2MM(25),table1_col_vals[column][row],border=0,align='C')
            else:
                pdf.multi_cell(px2MM(col_text_widths[column]), px2MM(25),table1_col_vals[column][row],border=0,align='L')
            # Risk Images
            pdf.image(join(cwd,'assets','images','RiskMeters',risk_images[row]), px2MM(763), px2MM(341+row*115), px2MM(78), px2MM(40))
                
    # --card2 table--
    
    col_x_pos = (1020, 1175, 1299)
    col_widths = (155, 124, 156)
    col_text_widths = (115, 84, 116)
    col_align = ('L', 'C', 'R')

    l1 = ['Lifestage']+list(df2["life_stage"])
    l2 = ['Age Range']+list(df2["age_range"])
    # l3 = ['Income Growth']+list(str(x*100)+'%' for x in df2["Percentage"])
    l3 = ['Income Growth']+list(df2["income_growth"])


    
    for i in range(len(l1)):
        if i%2==0:
            pdf.set_fill_color(*hex2RGB('#F3F6F9'))
        else:
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        if i==0:
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(18))
        else:
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
            
 
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_line_width(px2MM(0.2))
        pdf.rect(px2MM(1020),px2MM(276+(i*45)),px2MM(290),px2MM(45),'FD')
        pdf.set_xy(px2MM(1040),px2MM(286+(i*45)))
        pdf.cell(px2MM(250),px2MM(25),l1[i],align='L')
        
        pdf.rect(px2MM(1310),px2MM(276+(i*45)),px2MM(258),px2MM(45),'FD')
        pdf.set_xy(px2MM(1330),px2MM(286+(i*45)))
        pdf.cell(px2MM(218),px2MM(25),str(l2[i]),align='C')
        
        pdf.rect(px2MM(1568),px2MM(276+(i*45)),px2MM(192),px2MM(45),'FD')
        pdf.set_xy(px2MM(1588),px2MM(286+(i*45)))
        pdf.cell(px2MM(152),px2MM(25),str(l3[i]),align='R')
        
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))  
    pdf.set_xy(px2MM(1310),px2MM(511))
    pdf.cell(px2MM(170),px2MM(25),'Expense Growth: '+ json_data["our_assumption"]['yoy_growth_expense'],align='L')  
    
    pdf.set_font('LeagueSpartan-Light', size=px2pts(18))  
    pdf.set_xy(px2MM(1020),px2MM(556))
    pdf.multi_cell(px2MM(740),px2MM(25),'The timing of life stages varies based on profession, industry trends, career goals, and other factors, making it unique to each individual.',align='L') 
    
    desc_text = '''Disclaimer: The returns and rates mentioned in this report are based on historical data and are subject to change in the future.'''
    pdf.set_xy(px2MM(120), px2MM(1028))
    pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.multi_cell(px2MM(1680),px2MM(32),desc_text,border=0,align="C")
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')

#//*----Your Financial wellness plan------*//

def fin_wellness_plan(pdf,json_data,c_MoneyS,money_signData):
    try:
        fwp = pd.DataFrame.from_dict(json_data['fwp'])
        if fwp.empty:
            return None
        
        
        df_exp_lib_manage = fwp['desc'].iloc[0]
        df_asset = fwp['desc'].iloc[1]
        df_expense = fwp['desc'].iloc[2]
        
        if df_exp_lib_manage==[] and df_asset==[] and df_expense==[]:
            return None
    
    except Exception as e:
        return None
    
    #//*---Page setup----*//
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F') 

    # black background of page
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0, 0, 1920, 1080, 'F')

    # white rectangular backgrount at bottom
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(px2MM(0), px2MM(736), px2MM(1920), px2MM(344), 'F')
    
    #//*--Purple vertical line
    # pdf.set_xy(px2MM(125),px2MM(78))
    pdf.set_fill_color(*hex2RGB('#ffffff'))
    pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F') 
    
    #//*---heading statement
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.cell(px2MM(724), px2MM(84),'Your Financial Wellness Plan')
        
    # subtitle
    pdf.set_xy(px2MM(120), px2MM(244))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.cell(px2MM(234), px2MM(56), 'Key Takeaways')
    # Cards

    card_title_list = fwp['title'].tolist()
    image_list = []
    for i in card_title_list:
        if i.lower() == "emergency planning":
           image_list.append('Shield.png') 
        elif i.lower() == "expense and liability management":
            image_list.append('Expense.png') 
        elif i.lower() == "asset allocation":
            image_list.append('Assets.png') 
        else:
            image_list.append('Assets.png') 
            
    #//*---Image name: (Shield = Emergency Planning)
    # image_list = ['Shield.png','Expense.png', 'Assets.png']
   
    
    len_p = []
    for card_num in range(len(card_title_list)):
        # Card Boxes
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        
        pdf.rect(px2MM(120+(card_num*577)), px2MM(340), px2MM(527), px2MM(654), 'FD')
            
        # logo 
        logo = join(cwd,'assets','images','icons', image_list[card_num])
        pdf.image(logo, px2MM(160+(card_num*577)), px2MM(382), px2MM(80), px2MM(80))

        # Card titles  
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#000000'))
        if len(card_title_list[card_num]) >= 20:
            pdf.set_xy(px2MM(260+(card_num*579)), px2MM(380))
        else:
            pdf.set_xy(px2MM(260+(card_num*579)), px2MM(399))
        pdf.multi_cell(px2MM(347), px2MM(42), card_title_list[card_num], align="L")
        
        pi_gap_rect=522
        pi_gap_text = 504  
        for i in range(len(fwp['desc'].iloc[card_num])):
            if fwp['desc'].iloc[card_num][i] == "":
                continue
            pdf.set_fill_color(*hex2RGB('#000000'))
            pdf.rect(px2MM(160+(card_num*576)), px2MM(pi_gap_rect+(i*48)), px2MM(10), px2MM(10), 'F')

            pdf.set_xy(px2MM(195+(card_num*577)), px2MM(pi_gap_text+(i*30)))  
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(30))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.multi_cell(px2MM(417), px2MM(42), fwp['desc'].iloc[card_num][i], align='L')
            
            pi_gap_rect=pi_gap_text = mm2PX(pdf.get_y())

    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    global your_fw_plan_idx
    your_fw_plan_idx = pdf.page_no()
    
    
#//*------cashflow_plan
def cashflow_plan(pdf,json_data,c_MoneyS,money_signData):
    cashflow_plan_customer_type = json_data.get('next_three_months_action_plan',{}).get('is_new_action_step',None)
    if cashflow_plan_customer_type == True:
        cashflow_plan_new_customer(pdf,json_data,c_MoneyS,money_signData)
    elif cashflow_plan_customer_type == False:
        cashflow_plan_old_customer(pdf,json_data,c_MoneyS,money_signData)


def cashflow_plan_new_customer(pdf,json_data,c_MoneyS,money_signData):
    try:
        df_cash_flow = pd.DataFrame.from_dict(json_data['next_three_months_action_plan']["table"])
    except Exception as e:
        return None
    
    lcol_val_list = ["Next 3 Months Cashflows"]+list(df_cash_flow["particular"])

    rcol_val_list = ["Amount"]+list("₹ "+str(format_cash2(float(x))) for x in df_cash_flow["amount"])
    
    #//* function Page setup (adding page with cashflow table) if multiple page gets created due to large comments
    def cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list,table_req=False):
        #//*---Page setup----*//
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
        global your_fw_plan_idx
        if your_fw_plan_idx == 0:
            your_fw_plan_idx = pdf.page_no()

        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

        # page tile 
        pdf.set_xy(px2MM(120), px2MM(80))  
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(792), px2MM(84), "Next 3 Months Action Plan")

        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.05))
        # pdf.set_draw_color(*hex2RGB('#D3D3D3'))
        # pdf.rect(px2MM(120), px2MM(224), px2MM(516), px2MM(432), 'D')

        desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
        pdf.set_xy(px2MM(405), px2MM(1039))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C")

        if not table_req:
            return 204
        
        pdf.set_fill_color(*hex2RGB('#DEEDFF'))
        pdf.rect(px2MM(119), px2MM(204), px2MM(1683), px2MM(116), 'F')
        pdf.image(join(cwd,'assets','images','Action Plan','Personality.svg'),px2MM(159),px2MM(221),px2MM(84),px2MM(84))
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(273), px2MM(220))
        pdf.multi_cell(px2MM(200),px2MM(42),'Consult your',border=0,align="L")

        
        pdf.set_xy(px2MM(426), px2MM(220))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.multi_cell(px2MM(500),px2MM(42),'Financial Advisor',border=0,align="L")
        
        pdf.set_xy(px2MM(640), px2MM(220))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.multi_cell(px2MM(1390),px2MM(42),'before executing any transactions involving existing financial products for long-term and',border=0,align="L")
        
        pdf.set_xy(px2MM(273), px2MM(262))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.multi_cell(px2MM(1690),px2MM(42),'short-term tax implications',border=0,align="L")

        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        for row in range(len(lcol_val_list)):
            if row%2 == 0:
                col = '#ffffff'
            else:
                col = '#F3F6F9'
            pdf.set_fill_color(*hex2RGB(col))
                
            if row == 0 or row==len(lcol_val_list)-1: 
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            else:
                pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
                
                
            pdf.set_line_width(px2MM(0.5))
            pdf.rect(px2MM(574), px2MM(360+(row*65)), px2MM(500), px2MM(65), 'FD')
            pdf.rect(px2MM(1074), px2MM(360+(row*65)), px2MM(250), px2MM(65), 'FD')
            if row ==len(lcol_val_list)-1:
                pdf.set_draw_color(*hex2RGB('#B9BABE'))
                pdf.set_fill_color(*hex2RGB('#B9BABE'))
                pdf.rect(px2MM(574), px2MM(360+(row*65)), px2MM(750), px2MM(1), 'FD') 
                pdf.set_fill_color(*hex2RGB(col))
                pdf.set_draw_color(*hex2RGB('#E9EAEE'))
                pdf.set_line_width(px2MM(0.2))
                pdf.rect(px2MM(574), px2MM(361+(row*65)), px2MM(750), px2MM(65), 'FD') 
                
                
            # col1 text
            pdf.set_xy(px2MM(594), px2MM(380+(row*65)))  
            pdf.cell(px2MM(450), px2MM(32), lcol_val_list[row], align='L')
            # col2 text
            pdf.set_xy(px2MM(1094), px2MM(382+(row*65)))
            if rcol_val_list[row]=='₹0.0' or rcol_val_list[row]=='₹0':
                pdf.cell(px2MM(210), px2MM(32),' ', align='R')
            else:
                pdf.cell(px2MM(210), px2MM(32), rcol_val_list[row], align='R')
                
        return 360
                
    y = cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list,table_req=True)    
    # featured_list = json_data['next_three_months_action_plan']['cashflow_comments_new']
    # if featured_list == []:
    #     return None
    
    # sep = 0
    
    # # Get the height of first title comments (logic 2)
    # def get_first_comment_height(pdf,featured_list,y):
    #     if sep != 0:
    #         y=mm2PX(pdf.get_y())+64

    #     pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
    #     pdf.set_text_color(*hex2RGB('#1A1A1D'))
    #     pdf.set_xy(px2MM(696), px2MM(y))
    #     pdf.multi_cell(px2MM(1110),px2MM(42),featured_list['name'],border=0,align="L")
    #     title_y = mm2PX(pdf.get_y())+20
        
    #     pdf.set_font('LeagueSpartan-medium', size=px2pts(30))
    #     pdf.set_text_color(*hex2RGB('#1A1A1D'))
    #     pdf.set_xy(px2MM(726), px2MM(title_y))
    #     pdf.multi_cell(px2MM(1080),px2MM(42),featured_list['comments'][0]['title'],border=0,align="L")
        
    #     if featured_list['comments'][0]['suggestion'] != "":
    #         sugg = mm2PX(pdf.get_y())+8
    #         pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    #         pdf.set_text_color(*hex2RGB('#4B4C51'))
    #         pdf.set_xy(px2MM(726), px2MM(sugg))
    #         pdf.multi_cell(px2MM(1080),px2MM(32),featured_list['comments'][0]['suggestion'],border=0,align="L")
        
    #     title_y = mm2PX(pdf.get_y())+92
    #     pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    #     pdf.rect(px2MM(695), px2MM(y), px2MM(1110), px2MM(title_y-y),'F')
    #     if 1080-y < title_y-y:
    #         # pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    #         pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    #         pdf.rect(px2MM(695), px2MM(y), px2MM(1110), px2MM(title_y-y),'F')
    #         desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
    #         pdf.set_xy(px2MM(405), px2MM(1039))
    #         pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
    #         pdf.set_text_color(*hex2RGB('#000000'))
    #         pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C")
        
    #     return title_y-y

    # x = 695
    # w = 1080
    # def get_comment_height(pdf,comment,y,x,w):

    #     pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    #     pdf.set_text_color(*hex2RGB('#4B4C51'))
    #     pdf.set_xy(px2MM(x+10), px2MM(y+10))
    #     pdf.multi_cell(px2MM(20),px2MM(10),"\u2022",border=0,align="L")

    #     pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    #     pdf.set_xy(px2MM(x+30), px2MM(y))
    #     pdf.multi_cell(px2MM(w),px2MM(32),comment,border=0,align="L")
    #     next_y = mm2PX(pdf.get_y())+10
    #     comment_h = next_y-y

    #     if next_y > 1020 :
    #         pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    #         pdf.rect(px2MM(695), px2MM(y), px2MM(1110), px2MM(comment_h),'F')
    #         desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
    #         pdf.set_xy(px2MM(405), px2MM(1039))
    #         pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
    #         pdf.set_text_color(*hex2RGB('#000000'))
    #         pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C") 
    #     return comment_h ,next_y

    # for i in range(len(featured_list)):  
    #     # if i ==2:
    #     #     break

    #     if 1080-y < 240:
    #         x,w = 119,1650
    #         table_req = False
    #         y = cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list,table_req)

    #     pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
    #     pdf.set_text_color(*hex2RGB('#1A1A1D'))
    #     pdf.set_xy(px2MM(x), px2MM(y))
    #     pdf.multi_cell(px2MM(1110),px2MM(42),featured_list[i]['name'],border=0,align="L")  
    #     y = mm2PX(pdf.get_y())+10

    #     for j in range(len(featured_list[i].get("comments",[]))):
    #         commen_h,new_y = get_comment_height(pdf,featured_list[i]['comments'][j],y,x,w)
    #         if y+commen_h > 1020:
    #             x,w = 119,1650
    #             table_req = False
    #             y = cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list,table_req)
    #             commen_h,new_y = get_comment_height(pdf,featured_list[i]['comments'][j],y,x,w)
    #         y = new_y
        
    #     y += 32




# def cashflow_plan_new_customer(pdf,json_data,c_MoneyS,money_signData):
#     try:
#         df_cash_flow = pd.DataFrame.from_dict(json_data['next_three_months_action_plan']["table"])
#     except Exception as e:
#         return None
    
#     lcol_val_list = ["Next 3 Months Cashflows"]+list(df_cash_flow["particular"])

#     rcol_val_list = ["Amount"]+list("₹ "+str(format_cash2(float(x))) for x in df_cash_flow["amount"])
    
#     #//* function Page setup (adding page with cashflow table) if multiple page gets created due to large comments
#     def cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list,table_req=False):
#         #//*---Page setup----*//
#         pdf.add_page()
#         pdf.set_fill_color(*hex2RGB('#FCF8ED'))
#         pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
#         #//*-----Index Text of Page--**////
#         index_text(pdf,'#1A1A1D')
#         global your_fw_plan_idx
#         if your_fw_plan_idx == 0:
#             your_fw_plan_idx = pdf.page_no()

#         # black rectangle
#         pdf.set_fill_color(*hex2RGB('#000000'))
#         pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

#         # page tile 
#         pdf.set_xy(px2MM(120), px2MM(80))  
#         pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
#         pdf.set_text_color(*hex2RGB('#1A1A1D'))
#         pdf.cell(px2MM(792), px2MM(84), "Next 3 Months Action Plan")

#         pdf.set_draw_color(*hex2RGB('#E9EAEE'))
#         pdf.set_line_width(px2MM(0.05))
#         # pdf.set_draw_color(*hex2RGB('#D3D3D3'))
#         # pdf.rect(px2MM(120), px2MM(224), px2MM(516), px2MM(432), 'D')

#         desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
#         pdf.set_xy(px2MM(405), px2MM(1039))
#         pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
#         pdf.set_text_color(*hex2RGB('#000000'))
#         pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C")

#         if not table_req:
#             return 204
        
#         pdf.set_fill_color(*hex2RGB('#DEEDFF'))
#         pdf.rect(px2MM(119), px2MM(204), px2MM(1683), px2MM(116), 'F')
#         pdf.image(join(cwd,'assets','images','Action Plan','Personality.svg'),px2MM(159),px2MM(221),px2MM(84),px2MM(84))
        
#         pdf.set_font('LeagueSpartan-regular', size=px2pts(28))
#         pdf.set_text_color(*hex2RGB('#1A1A1D'))
#         pdf.set_xy(px2MM(273), px2MM(220))
#         pdf.multi_cell(px2MM(200),px2MM(42),'Consult your',border=0,align="L")

        
#         pdf.set_xy(px2MM(426), px2MM(220))
#         pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(28))
#         pdf.set_text_color(*hex2RGB('#313236'))
#         pdf.multi_cell(px2MM(500),px2MM(42),'Financial Advisor',border=0,align="L")
        
#         pdf.set_xy(px2MM(640), px2MM(220))
#         pdf.set_font('LeagueSpartan-regular', size=px2pts(28))
#         pdf.set_text_color(*hex2RGB('#313236'))
#         pdf.multi_cell(px2MM(1390),px2MM(42),'before executing any transactions involving existing financial products for long-term and',border=0,align="L")
        
#         pdf.set_xy(px2MM(273), px2MM(262))
#         pdf.set_font('LeagueSpartan-regular', size=px2pts(28))
#         pdf.set_text_color(*hex2RGB('#313236'))
#         pdf.multi_cell(px2MM(1690),px2MM(42),'short-term tax implications',border=0,align="L")

#         pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
#         pdf.set_text_color(*hex2RGB('#000000'))
#         for row in range(len(lcol_val_list)):
#             if row%2 == 0:
#                 col = '#ffffff'
#             else:
#                 col = '#F3F6F9'
#             pdf.set_fill_color(*hex2RGB(col))
                
#             if row == 0 or row==len(lcol_val_list)-1: 
#                 pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
#             else:
#                 pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
                
                

#             pdf.rect(px2MM(120), px2MM(360+(row*65)), px2MM(360), px2MM(65), 'FD')
#             pdf.rect(px2MM(480), px2MM(360+(row*65)), px2MM(156), px2MM(65), 'FD')
#             if row ==len(lcol_val_list)-1:
#                 pdf.set_draw_color(*hex2RGB('#B9BABE'))
#                 pdf.set_fill_color(*hex2RGB('#B9BABE'))
#                 pdf.rect(px2MM(120), px2MM(360+(row*65)), px2MM(516), px2MM(1), 'FD') 
#                 pdf.set_fill_color(*hex2RGB(col))
#                 pdf.set_draw_color(*hex2RGB('#E9EAEE'))
#                 pdf.set_line_width(px2MM(0.2))
#                 pdf.rect(px2MM(120), px2MM(361+(row*65)), px2MM(516), px2MM(65), 'FD') 
                
                
#             # col1 text
#             pdf.set_xy(px2MM(140), px2MM(380+(row*65)))  
#             pdf.cell(px2MM(320), px2MM(32), lcol_val_list[row], align='L')
#             # col2 text
#             pdf.set_xy(px2MM(500), px2MM(382+(row*65)))
#             if rcol_val_list[row]=='₹0.0' or rcol_val_list[row]=='₹0':
#                 pdf.cell(px2MM(116), px2MM(32),' ', align='R')
#             else:
#                 pdf.cell(px2MM(116), px2MM(32), rcol_val_list[row], align='R')
                
#         return 360
                
#     y = cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list,table_req=True)    
#     featured_list = json_data['next_three_months_action_plan']['cashflow_comments_new']
#     if featured_list == []:
#         return None
    
#     sep = 0
    
#     # Get the height of first title comments (logic 2)
#     def get_first_comment_height(pdf,featured_list,y):
#         if sep != 0:
#             y=mm2PX(pdf.get_y())+64

#         pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
#         pdf.set_text_color(*hex2RGB('#1A1A1D'))
#         pdf.set_xy(px2MM(696), px2MM(y))
#         pdf.multi_cell(px2MM(1110),px2MM(42),featured_list['name'],border=0,align="L")
#         title_y = mm2PX(pdf.get_y())+20
        
#         pdf.set_font('LeagueSpartan-medium', size=px2pts(30))
#         pdf.set_text_color(*hex2RGB('#1A1A1D'))
#         pdf.set_xy(px2MM(726), px2MM(title_y))
#         pdf.multi_cell(px2MM(1080),px2MM(42),featured_list['comments'][0]['title'],border=0,align="L")
        
#         if featured_list['comments'][0]['suggestion'] != "":
#             sugg = mm2PX(pdf.get_y())+8
#             pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
#             pdf.set_text_color(*hex2RGB('#4B4C51'))
#             pdf.set_xy(px2MM(726), px2MM(sugg))
#             pdf.multi_cell(px2MM(1080),px2MM(32),featured_list['comments'][0]['suggestion'],border=0,align="L")
        
#         title_y = mm2PX(pdf.get_y())+92
#         pdf.set_fill_color(*hex2RGB('#FCF8ED'))
#         pdf.rect(px2MM(695), px2MM(y), px2MM(1110), px2MM(title_y-y),'F')
#         if 1080-y < title_y-y:
#             # pdf.set_fill_color(*hex2RGB('#FCF8ED'))
#             pdf.set_fill_color(*hex2RGB('#FCF8ED'))
#             pdf.rect(px2MM(695), px2MM(y), px2MM(1110), px2MM(title_y-y),'F')
#             desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
#             pdf.set_xy(px2MM(405), px2MM(1039))
#             pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
#             pdf.set_text_color(*hex2RGB('#000000'))
#             pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C")
        
#         return title_y-y

#     x = 695
#     w = 1080
#     def get_comment_height(pdf,comment,y,x,w):

#         pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
#         pdf.set_text_color(*hex2RGB('#4B4C51'))
#         pdf.set_xy(px2MM(x+10), px2MM(y+10))
#         pdf.multi_cell(px2MM(20),px2MM(10),"\u2022",border=0,align="L")

#         pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
#         pdf.set_xy(px2MM(x+30), px2MM(y))
#         pdf.multi_cell(px2MM(w),px2MM(32),comment,border=0,align="L")
#         next_y = mm2PX(pdf.get_y())+10
#         comment_h = next_y-y

#         if next_y > 1020 :
#             pdf.set_fill_color(*hex2RGB('#FCF8ED'))
#             pdf.rect(px2MM(695), px2MM(y), px2MM(1110), px2MM(comment_h),'F')
#             desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
#             pdf.set_xy(px2MM(405), px2MM(1039))
#             pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
#             pdf.set_text_color(*hex2RGB('#000000'))
#             pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C") 
#         return comment_h ,next_y

#     for i in range(len(featured_list)):  
#         # if i ==2:
#         #     break

#         if 1080-y < 240:
#             x,w = 119,1650
#             table_req = False
#             y = cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list,table_req)

#         pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
#         pdf.set_text_color(*hex2RGB('#1A1A1D'))
#         pdf.set_xy(px2MM(x), px2MM(y))
#         pdf.multi_cell(px2MM(1110),px2MM(42),featured_list[i]['name'],border=0,align="L")  
#         y = mm2PX(pdf.get_y())+10

#         for j in range(len(featured_list[i].get("comments",[]))):
#             commen_h,new_y = get_comment_height(pdf,featured_list[i]['comments'][j],y,x,w)
#             if y+commen_h > 1020:
#                 x,w = 119,1650
#                 table_req = False
#                 y = cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list,table_req)
#                 commen_h,new_y = get_comment_height(pdf,featured_list[i]['comments'][j],y,x,w)
#             y = new_y
        
#         y += 32

#//*------cashflow function for old customer------//
def cashflow_plan_old_customer(pdf,json_data,c_MoneyS,money_signData):
    try:
        df_cash_flow = pd.DataFrame.from_dict(json_data['next_three_months_action_plan']["table"])
    except:
        return None
    
    lcol_val_list = ["Next 3 Months Cashflows"]+list(df_cash_flow["particular"])

    rcol_val_list = ["Amount"]+list("₹ "+str(format_cash2(float(x))) for x in df_cash_flow["amount"])
    
    #//* function Page setup (adding page with cashflow table) if multiple page gets created due to large comments
    def cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list):
        #//*---Page setup----*//
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
        global your_fw_plan_idx
        if your_fw_plan_idx == 0:
            your_fw_plan_idx = pdf.page_no()

        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

        # page tile 
        pdf.set_xy(px2MM(120), px2MM(80))  
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(792), px2MM(84), "Next 3 Months Action Plan")

        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.05))
        # pdf.set_draw_color(*hex2RGB('#D3D3D3'))
        # pdf.rect(px2MM(120), px2MM(224), px2MM(516), px2MM(432), 'D')

        desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
        pdf.set_xy(px2MM(405), px2MM(1039))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C")
        
        pdf.set_fill_color(*hex2RGB('#DEEDFF'))
        pdf.rect(px2MM(119), px2MM(204), px2MM(1683), px2MM(116), 'F')
        pdf.image(join(cwd,'assets','images','Action Plan','Personality.svg'),px2MM(159),px2MM(221),px2MM(84),px2MM(84))
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(273), px2MM(220))
        pdf.multi_cell(px2MM(200),px2MM(42),'Consult your',border=0,align="L")

        
        pdf.set_xy(px2MM(426), px2MM(220))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.multi_cell(px2MM(500),px2MM(42),'Financial Advisor',border=0,align="L")
        
        pdf.set_xy(px2MM(640), px2MM(220))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.multi_cell(px2MM(1390),px2MM(42),'before executing any transactions involving existing financial products for long-term and',border=0,align="L")
        
        pdf.set_xy(px2MM(273), px2MM(262))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(28))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.multi_cell(px2MM(1690),px2MM(42),'short-term tax implications',border=0,align="L")

        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        for row in range(len(lcol_val_list)):
            if row%2 == 0:
                col = '#ffffff'
            else:
                col = '#F3F6F9'
            pdf.set_fill_color(*hex2RGB(col))
                
            if row == 0 or row==len(lcol_val_list)-1: 
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            else:
                pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
                
                

            pdf.rect(px2MM(120), px2MM(360+(row*65)), px2MM(360), px2MM(65), 'FD')
            pdf.rect(px2MM(480), px2MM(360+(row*65)), px2MM(156), px2MM(65), 'FD')
            if row ==len(lcol_val_list)-1:
                pdf.set_draw_color(*hex2RGB('#B9BABE'))
                pdf.set_fill_color(*hex2RGB('#B9BABE'))
                pdf.rect(px2MM(120), px2MM(360+(row*65)), px2MM(516), px2MM(1), 'FD') 
                pdf.set_fill_color(*hex2RGB(col))
                pdf.set_draw_color(*hex2RGB('#E9EAEE'))
                pdf.set_line_width(px2MM(0.2))
                pdf.rect(px2MM(120), px2MM(361+(row*65)), px2MM(516), px2MM(65), 'FD') 
                
                
            # col1 text
            pdf.set_xy(px2MM(140), px2MM(380+(row*65)))  
            pdf.cell(px2MM(320), px2MM(32), lcol_val_list[row], align='L')
            # col2 text
            pdf.set_xy(px2MM(500), px2MM(382+(row*65)))
            if rcol_val_list[row]=='₹0.0' or rcol_val_list[row]=='₹0':
                pdf.cell(px2MM(116), px2MM(32),' ', align='R')
            else:
                pdf.cell(px2MM(116), px2MM(32), rcol_val_list[row], align='R')
                
        return 360
                
    y = cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list)    
    featured_list = json_data['next_three_months_action_plan']['cashflow_comments_old']
    if featured_list == []:
        return None
    
    sep = 0
    
    # Get the height of first title comments (logic 2)
    def get_first_comment_height(pdf,featured_list,y):
        if sep != 0:
            y=mm2PX(pdf.get_y())+64

        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(696), px2MM(y))
        pdf.multi_cell(px2MM(1110),px2MM(42),featured_list['name'],border=0,align="L")
        title_y = mm2PX(pdf.get_y())+20
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(726), px2MM(title_y))
        pdf.multi_cell(px2MM(1080),px2MM(42),featured_list['comments'][0]['title'],border=0,align="L")
        
        if featured_list['comments'][0]['suggestion'] != "":
            sugg = mm2PX(pdf.get_y())+8
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#4B4C51'))
            pdf.set_xy(px2MM(726), px2MM(sugg))
            pdf.multi_cell(px2MM(1080),px2MM(32),featured_list['comments'][0]['suggestion'],border=0,align="L")
        
        title_y = mm2PX(pdf.get_y())+92
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(px2MM(695), px2MM(y), px2MM(1110), px2MM(title_y-y),'F')
        if 1080-y < title_y-y:
            # pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(px2MM(695), px2MM(y), px2MM(1110), px2MM(title_y-y),'F')
            desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
            pdf.set_xy(px2MM(405), px2MM(1039))
            pdf.set_font('LeagueSpartan-Regular', size=px2pts(18))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.multi_cell(px2MM(1110),px2MM(22),desc_text,border=0,align="C")
        
        return title_y-y
        
    for i in range(len(featured_list)):        

        if featured_list[i]['comments'] == []:
            sep = 0
            continue

        # # Get the height of first title comments (logic 1)
        # pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
        # no_l_title = multicell_height(pdf,featured_list[i]['comments'][0]['title'],1080)
        # pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        # no_l_comment = multicell_height(pdf,featured_list[i]['comments'][0]['suggestion'],1080)
        # f1_y = 234+(no_l_comment*32)+(no_l_title*42) 
        
        # Get the height of first title comments (logic 2)
        f1_y = get_first_comment_height(pdf,featured_list[i],y)      
          
        if 1080-y < f1_y:
            y = cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list) 
            sep = 0 
     
        if sep != 0:
            pdf.set_fill_color(*hex2RGB('#B9BABE')) 
            pdf.rect(px2MM(696), px2MM(y), px2MM(1107), px2MM(1), 'F') 
            # y=mm2PX(pdf.get_y())+64
            y+=32   
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(696), px2MM(y))
        pdf.multi_cell(px2MM(1110),px2MM(42),featured_list[i]['name'],border=0,align="L")
        
        title_y = mm2PX(pdf.get_y())+20
        for j in range(len(featured_list[i]['comments'])):
            
            pdf.set_font('LeagueSpartan-medium', size=px2pts(30))
            no_l = multicell_height(pdf,featured_list[i]['comments'][j]['suggestion'],1080)
            if 1080-title_y < 140+(no_l*32):
                y = cashflow_pageSetUp_withTable(pdf,lcol_val_list,rcol_val_list) 
                sep = 0
            
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(696), px2MM(y))
                pdf.multi_cell(px2MM(1110),px2MM(42),featured_list[i]['name'],border=0,align="L")
                
                title_y = mm2PX(pdf.get_y())+20
                
            pdf.set_fill_color(*hex2RGB('#1A1A1D')) 
            pdf.rect(px2MM(696), px2MM(title_y+18), px2MM(10), px2MM(10), 'F')
            
            pdf.set_font('LeagueSpartan-medium', size=px2pts(30))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.set_xy(px2MM(726), px2MM(title_y))
            pdf.multi_cell(px2MM(1080),px2MM(42),featured_list[i]['comments'][j]['title'],border=0,align="L")
            
            if featured_list[i]['comments'][j]['suggestion'] != "":
                sugg = mm2PX(pdf.get_y())+8
                      
                pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#4B4C51'))
                pdf.set_xy(px2MM(726), px2MM(sugg))
                pdf.multi_cell(px2MM(1080),px2MM(32),featured_list[i]['comments'][j]['suggestion'],border=0,align="L")
            
            title_y = mm2PX(pdf.get_y())+10

        sep = i+1
        y = mm2PX(pdf.get_y())+32


#//*-----Action Plan Summary---*//
def action_plan_summary(pdf,json_data,c_MoneyS,money_signData):
    try:
        action_plan_summary = json_data.get("action_plan_summary",{})
        action_plan_total = action_plan_summary.get("total",{})
        action_plan_summary_table = action_plan_summary.get("table",[])

    except Exception as e:
        return None
    
    if not action_plan_summary_table:
        return None
    locale.setlocale(locale.LC_MONETARY, 'en_IN')
    bl_hight = 0

    def create_page(pdf,action_plan_summary,bl_hight):
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

        #//*----Featured List of Financial Products----*//
        pdf.set_xy(px2MM(120),px2MM(80)) 
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(877), px2MM(84),'Action Plan Summary',align='L')
        
        #//*---Top Black box
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F')
    
        #//*---Credit Facilities Taken---*//
        
        pdf.set_fill_color(*hex2RGB('#313236'))
        pdf.rect(px2MM(109), px2MM(217), px2MM(252), px2MM(42),'F')
        
        pdf.set_xy(px2MM(109),px2MM(222)) 
        pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#ffffff'))
        pdf.cell(px2MM(252), px2MM(32),f'Number of Actions - {action_plan_summary.get("number_of_actions","0")}',align='C')
    
        #//*---Table Header----*//
        pdf.set_fill_color(*hex2RGB('#ffffff'))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.2))
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        
        #//*---Col 1
        pdf.rect(px2MM(115), px2MM(259), px2MM(290), px2MM(72),'FD')
        pdf.set_xy(px2MM(135),px2MM(279)) 
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(250), px2MM(32),'Particulars',align='L')
        #//*---Col 2
        pdf.rect(px2MM(405), px2MM(259), px2MM(200), px2MM(72),'FD')
        pdf.set_xy(px2MM(425),px2MM(279)) 
        pdf.cell(px2MM(120), px2MM(32),'Timeline',align='L')
        #//*---Col 3
        pdf.rect(px2MM(605), px2MM(259), px2MM(750), px2MM(72),'FD')
        pdf.set_xy(px2MM(625),px2MM(279)) 
        pdf.cell(px2MM(300), px2MM(32),'Action Plan points',align='L')
        #//*---Col 4
        pdf.rect(px2MM(1355), px2MM(259), px2MM(235), px2MM(72),'FD')
        pdf.set_xy(px2MM(1375),px2MM(279)) 
        pdf.cell(px2MM(200), px2MM(32),'Suggested Amount',align='C')
        #//*---Col 5
        pdf.rect(px2MM(1590), px2MM(259), px2MM(220), px2MM(72),'FD')
        pdf.set_xy(px2MM(1622),px2MM(279)) 
        pdf.cell(px2MM(170), px2MM(32),'Financial Impact',align='R')

        bl_hight+=72
        add_desclaimer(pdf)
        return 331,bl_hight
    
    def add_desclaimer(pdf):
        txt = '''Disclaimer: Numbers may not add up due to rounding.'''
        pdf.set_xy(px2MM(740),px2MM(1039))  
        pdf.set_font('Roboto-Regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.multi_cell(px2MM(450), px2MM(21),txt,align='C') 
    
    y,bl_hight = create_page(pdf,action_plan_summary,bl_hight)

    def get_rect_hight(row,y):
        str_y = y+10
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_xy(px2MM(135),px2MM(str_y)) 
        pdf.multi_cell(px2MM(250), px2MM(32),str(row.get("particular","")),align='L')
        y1 = mm2PX(pdf.get_y())+10

        pdf.set_xy(px2MM(425),px2MM(str_y)) 
        pdf.multi_cell(px2MM(170), px2MM(32),str(row.get("timeline","")),align='L')
        y2 = mm2PX(pdf.get_y())+10

        act_y = str_y
        for j,item in enumerate(row.get("action_points",[])):
            sub_gap = 6 if j!=0 else 0
            pdf.set_xy(px2MM(625),px2MM(act_y+sub_gap)) 
            pdf.multi_cell(px2MM(710), px2MM(32),str(item.get("points","")),align='L')
            act_y = mm2PX(pdf.get_y())+10
        y3 = mm2PX(pdf.get_y())+10

        pdf.set_xy(px2MM(1600),px2MM(str_y)) 
        pdf.multi_cell(px2MM(180), px2MM(32),str(row.get("financial_impact","")),align='L')
        y4 = mm2PX(pdf.get_y())+10

        max_y = max(y1,y2,y3,y4)
        rect_h = max_y-y

        if max_y > 859:
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.rect(px2MM(0), px2MM(y), px2MM(1920), px2MM(rect_h),'F')
            if max_y > 1039:
                add_desclaimer(pdf)

        return rect_h

    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    for i, row in enumerate(action_plan_summary_table):

        rect_h = get_rect_hight(row,y)
        if 1080-y<221 or (i == len(action_plan_summary_table)-1 and 1080-y<350 ):
            pdf.set_fill_color(*hex2RGB('#313236'))
            pdf.rect(px2MM(118), px2MM(259), px2MM(6), px2MM(bl_hight),'F')
            bl_hight = 0
            y,bl_hight = create_page(pdf,action_plan_summary,bl_hight)
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            #//*-----Index Text of Page--**////
            index_text(pdf,'#1A1A1D')
        
        if i%2==0:
            pdf.set_fill_color(*hex2RGB('#F3F6F9'))
        else:
            pdf.set_fill_color(*hex2RGB('#ffffff'))

        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_line_width(px2MM(0.5))
        #Col 1
        pdf.rect(px2MM(115), px2MM(y), px2MM(290), px2MM(rect_h),'FD')
        pdf.set_xy(px2MM(135),px2MM(y+10)) 
        pdf.multi_cell(px2MM(250), px2MM(32),str(row.get("particular","")),align='L')

        #Col 2
        pdf.rect(px2MM(405), px2MM(y), px2MM(200), px2MM(rect_h),'FD')
        pdf.set_xy(px2MM(425),px2MM(y+10)) 
        pdf.multi_cell(px2MM(170), px2MM(32),str(row.get("timeline","")),align='L')

        #Col 3
        act_y = y+10
        pdf.rect(px2MM(605), px2MM(y), px2MM(750), px2MM(rect_h),'FD')
        pdf.rect(px2MM(1355), px2MM(y), px2MM(235), px2MM(rect_h),'FD')
        for j,item in enumerate(row.get("action_points",[])):
            sub_gap = 6 if j!=0 else 0
            pdf.set_xy(px2MM(625),px2MM(act_y+sub_gap)) 
            pdf.multi_cell(px2MM(710), px2MM(32),str(item.get("points","")),align='L')
            act_y1 = mm2PX(pdf.get_y())+10
            try :
                pdf.set_xy(px2MM(1375),px2MM(act_y+sub_gap)) 
                # pdf.multi_cell(px2MM(195), px2MM(32),str(row.get("suggested_amount",[])[j]),align='R')  

                if str(item.get("value","0")) in ('-','0',''):
                    pdf.multi_cell(px2MM(180), px2MM(32),'₹ 0.0K',align='R')
                else:
                    # val1 = str(locale.currency(float(str(item.get("value",""))), grouping=True))
                    # val1 = val1.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                    val2 = format_cash2(float(str(item.get("value",""))))
                    pdf.multi_cell(px2MM(195), px2MM(32),f"₹ {val2}",align='R') 
            except Exception as e:
                pass
            act_y2 = mm2PX(pdf.get_y())+10
            act_y = max(act_y1,act_y2)



        #Col 4
        pdf.rect(px2MM(1590), px2MM(y), px2MM(220), px2MM(rect_h),'FD')
        pdf.set_xy(px2MM(1600),px2MM(y+10)) 

        if str(row.get("financial_impact","-")) in ('-','0',''):
            pdf.multi_cell(px2MM(180), px2MM(32),'₹ 0.0K',align='R')
        else:
            # val1 = str(locale.currency(float(str(row.get("financial_impact",""))), grouping=True))
            # val1 = val1.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
            val1 = format_cash2(float(str(row.get("financial_impact","0.0"))))
            pdf.multi_cell(px2MM(180), px2MM(32),f"₹ {val1}",align='R')

        y+=rect_h
        bl_hight+=rect_h

    #//*---Total----*// 
    pdf.set_fill_color(*hex2RGB('#B9BABE'))
    pdf.set_draw_color(*hex2RGB('#B9BABE'))
    pdf.set_line_width(px2MM(1))
    pdf.rect(px2MM(115), px2MM(y), px2MM(1701), px2MM(1),'FD') 
    y+=1
    pdf.set_fill_color(*hex2RGB('#E2E1F3'))
    pdf.rect(px2MM(115), px2MM(y), px2MM(1701), px2MM(72),'F') 

    #col1
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_xy(px2MM(135),px2MM(y+20)) 
    pdf.cell(px2MM(250), px2MM(32),str(action_plan_total.get("particular","Total Financial Impact")),align='L')

    #col2
    pdf.set_xy(px2MM(1600),px2MM(y+20)) 

    if str(action_plan_total.get("financial_impact","-")) in ('-','0',''):
        pdf.multi_cell(px2MM(180), px2MM(32),'₹ 0',align='R')
    else:
        # val1 = str(locale.currency(float(str(action_plan_total.get("financial_impact","0"))), grouping=True))
        # val1 = val1.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
        val3 = format_cash2(float(str(action_plan_total.get("financial_impact","0"))))
        pdf.multi_cell(px2MM(180), px2MM(32),f"₹ {val3}",align='R')

    bl_hight+=72
    pdf.set_fill_color(*hex2RGB('#313236'))
    pdf.rect(px2MM(109), px2MM(259), px2MM(6), px2MM(bl_hight),'F')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')


# #//*-----Action Plan Summary---*//
# def action_plan_summary(pdf,json_data,c_MoneyS,money_signData):
#     try:
#         action_plan_summary = json_data.get("action_plan_summary",{})
#         action_plan_total = action_plan_summary.get("total",{})
#         action_plan_summary_table = action_plan_summary.get("table",[])

#     except Exception as e:
#         return None
    
#     if not action_plan_summary_table:
#         return None
#     locale.setlocale(locale.LC_MONETARY, 'en_IN')
#     bl_hight = 0

#     def create_page(pdf,action_plan_summary,bl_hight):
#         pdf.add_page()
#         pdf.set_fill_color(*hex2RGB('#FCF8ED'))
#         pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')

#         #//*----Featured List of Financial Products----*//
#         pdf.set_xy(px2MM(120),px2MM(80)) 
#         pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
#         pdf.set_text_color(*hex2RGB('#1A1A1D'))
#         pdf.cell(px2MM(877), px2MM(84),'Action Plan Summary',align='L')
        
#         #//*---Top Black box
#         pdf.set_fill_color(*hex2RGB('#000000'))
#         pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84),'F')
    
#         #//*---Credit Facilities Taken---*//
        
#         pdf.set_fill_color(*hex2RGB('#313236'))
#         pdf.rect(px2MM(118), px2MM(217), px2MM(252), px2MM(42),'F')
        
#         pdf.set_xy(px2MM(118),px2MM(222)) 
#         pdf.set_font('LeagueSpartan-Medium', size=px2pts(24))
#         pdf.set_text_color(*hex2RGB('#ffffff'))
#         pdf.cell(px2MM(252), px2MM(32),f'Number of Actions - {action_plan_summary.get("number_of_actions","0")}',align='C')
    
#         #//*---Table Header----*//
#         pdf.set_fill_color(*hex2RGB('#ffffff'))
#         pdf.set_draw_color(*hex2RGB('#E9EAEE'))
#         pdf.set_line_width(px2MM(0.2))
#         pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        
#         #//*---Col 1
#         pdf.rect(px2MM(124), px2MM(259), px2MM(308), px2MM(72),'FD')
#         pdf.set_xy(px2MM(144),px2MM(279)) 
#         pdf.set_text_color(*hex2RGB('#1A1A1D'))
#         pdf.cell(px2MM(250), px2MM(32),'Particulars',align='L')
#         #//*---Col 2
#         pdf.rect(px2MM(432), px2MM(259), px2MM(298), px2MM(72),'FD')
#         pdf.set_xy(px2MM(452),px2MM(279)) 
#         pdf.cell(px2MM(250), px2MM(32),'Timeline',align='L')
#         #//*---Col 3
#         pdf.rect(px2MM(730), px2MM(259), px2MM(852), px2MM(72),'FD')
#         pdf.set_xy(px2MM(750),px2MM(279)) 
#         pdf.cell(px2MM(300), px2MM(32),'Action Plan points',align='L')
#         #//*---Col 4
#         pdf.rect(px2MM(1582), px2MM(259), px2MM(220), px2MM(72),'FD')
#         pdf.set_xy(px2MM(1614),px2MM(279)) 
#         pdf.cell(px2MM(170), px2MM(32),'Financial Impact',align='R')

#         bl_hight+=72
#         add_desclaimer(pdf)
#         return 331,bl_hight
    
#     def add_desclaimer(pdf):
#         txt = '''Disclaimer: Numbers may not add up due to rounding.'''
#         pdf.set_xy(px2MM(740),px2MM(1039))  
#         pdf.set_font('Roboto-Regular', size=px2pts(18))
#         pdf.set_text_color(*hex2RGB('#1A1A1D'))
#         pdf.multi_cell(px2MM(450), px2MM(21),txt,align='C') 
    
#     y,bl_hight = create_page(pdf,action_plan_summary,bl_hight)

#     def get_rect_hight(row,y):
#         str_y = y+10
#         pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
#         pdf.set_xy(px2MM(144),px2MM(str_y)) 
#         pdf.multi_cell(px2MM(280), px2MM(32),str(row.get("particular","")),align='L')
#         y1 = mm2PX(pdf.get_y())+10

#         pdf.set_xy(px2MM(452),px2MM(str_y)) 
#         pdf.multi_cell(px2MM(260), px2MM(32),str(row.get("timeline","")),align='L')
#         y2 = mm2PX(pdf.get_y())+10

#         act_y = str_y
#         for j,item in enumerate(row.get("action_points",[])):
#             sub_gap = 6 if j!=0 else 0
#             pdf.set_xy(px2MM(750),px2MM(act_y+sub_gap)) 
#             pdf.multi_cell(px2MM(812), px2MM(32),str(item),align='L')
#             act_y = mm2PX(pdf.get_y())+10
#         y3 = mm2PX(pdf.get_y())+10

#         pdf.set_xy(px2MM(1600),px2MM(str_y)) 
#         pdf.multi_cell(px2MM(180), px2MM(32),str(row.get("financial_impact","")),align='L')
#         y4 = mm2PX(pdf.get_y())+10

#         max_y = max(y1,y2,y3,y4)
#         rect_h = max_y-y

#         if max_y > 859:
#             pdf.set_fill_color(*hex2RGB('#FCF8ED'))
#             pdf.set_text_color(*hex2RGB('#1A1A1D'))
#             pdf.rect(px2MM(0), px2MM(y), px2MM(1920), px2MM(rect_h),'F')
#             if max_y > 1039:
#                 add_desclaimer(pdf)

#         return rect_h

#     pdf.set_text_color(*hex2RGB('#1A1A1D'))
#     for i, row in enumerate(action_plan_summary_table):

#         rect_h = get_rect_hight(row,y)
#         if 1080-y<221 or (i == len(action_plan_summary_table)-1 and 1080-y<350 ):
#             pdf.set_fill_color(*hex2RGB('#313236'))
#             pdf.rect(px2MM(118), px2MM(259), px2MM(6), px2MM(bl_hight),'F')
#             bl_hight = 0
#             y,bl_hight = create_page(pdf,action_plan_summary,bl_hight)
#             pdf.set_text_color(*hex2RGB('#1A1A1D'))
#             #//*-----Index Text of Page--**////
#             index_text(pdf,'#1A1A1D')
        
#         if i%2==0:
#             pdf.set_fill_color(*hex2RGB('#F3F6F9'))
#         else:
#             pdf.set_fill_color(*hex2RGB('#ffffff'))

#         pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
#         pdf.set_draw_color(*hex2RGB('#E9EAEE'))
#         pdf.set_line_width(px2MM(0.5))
#         #Col 1
#         pdf.rect(px2MM(124), px2MM(y), px2MM(308), px2MM(rect_h),'FD')
#         pdf.set_xy(px2MM(144),px2MM(y+10)) 
#         pdf.multi_cell(px2MM(280), px2MM(32),str(row.get("particular","")),align='L')

#         #Col 2
#         pdf.rect(px2MM(432), px2MM(y), px2MM(298), px2MM(rect_h),'FD')
#         pdf.set_xy(px2MM(452),px2MM(y+10)) 
#         pdf.multi_cell(px2MM(260), px2MM(32),str(row.get("timeline","")),align='L')

#         #Col 3
#         act_y = y+10
#         pdf.rect(px2MM(730), px2MM(y), px2MM(852), px2MM(rect_h),'FD')
#         for j,item in enumerate(row.get("action_points",[])):
#             sub_gap = 6 if j!=0 else 0
#             pdf.set_xy(px2MM(750),px2MM(act_y+sub_gap)) 
#             pdf.multi_cell(px2MM(812), px2MM(32),str(item),align='L')
#             act_y = mm2PX(pdf.get_y())+10

#         #Col 4
#         pdf.rect(px2MM(1582), px2MM(y), px2MM(220), px2MM(rect_h),'FD')
#         pdf.set_xy(px2MM(1600),px2MM(y+10)) 

#         if str(row.get("financial_impact","-")) in ('-','0',''):
#             pdf.multi_cell(px2MM(180), px2MM(32),'₹ 0',align='R')
#         else:
#             val1 = str(locale.currency(float(str(row.get("financial_impact",""))), grouping=True))
#             val1 = val1.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
#             pdf.multi_cell(px2MM(180), px2MM(32),val1,align='R')

#         y+=rect_h
#         bl_hight+=rect_h

#     #//*---Total----*// 
#     pdf.set_fill_color(*hex2RGB('#B9BABE'))
#     pdf.set_draw_color(*hex2RGB('#B9BABE'))
#     pdf.set_line_width(px2MM(1))
#     pdf.rect(px2MM(124), px2MM(y), px2MM(1682), px2MM(1),'FD') 
#     y+=1
#     pdf.set_fill_color(*hex2RGB('#E2E1F3'))
#     pdf.rect(px2MM(124), px2MM(y), px2MM(1682), px2MM(72),'F') 

#     #col1
#     pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
#     pdf.set_xy(px2MM(144),px2MM(y+20)) 
#     pdf.cell(px2MM(250), px2MM(32),str(action_plan_total.get("particular","Total Financial Impact")),align='L')

#     #col2
#     pdf.set_xy(px2MM(1600),px2MM(y+20)) 

#     if str(action_plan_total.get("financial_impact","-")) in ('-','0',''):
#         pdf.multi_cell(px2MM(180), px2MM(32),'₹ 0',align='R')
#     else:
#         val1 = str(locale.currency(float(str(action_plan_total.get("financial_impact","0"))), grouping=True))
#         val1 = val1.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
#         pdf.multi_cell(px2MM(180), px2MM(32),val1,align='R')

#     bl_hight+=72
#     pdf.set_fill_color(*hex2RGB('#313236'))
#     pdf.rect(px2MM(118), px2MM(259), px2MM(6), px2MM(bl_hight),'F')
    
#     #//*-----Index Text of Page--**////
#     index_text(pdf,'#1A1A1D')




def next_quarter_preview(pdf, json_data):
    if json_data['next_quarter_preview'] == {}:
        return
    def next_quarter_preview_pg_setup(pdf, date):  
        #//*---Page setup----*//
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0, 0, px2MM(1920), px2MM(1080),'F')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#1A1A1D')
        global your_fw_plan_idx
        if your_fw_plan_idx == 0:
            your_fw_plan_idx = pdf.page_no()

        # black rectangle
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(0), px2MM(80), px2MM(15), px2MM(84), 'F')

        # page tile 
        pdf.set_xy(px2MM(120), px2MM(80))  
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.cell(px2MM(792), px2MM(84), "Next Consultation Agenda")

        # White box for the background
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))  # White fill
        pdf.set_xy(px2MM(119), px2MM(204))  # Position of the box
        pdf.rect(px2MM(119), px2MM(204), px2MM(1683), px2MM(160), 'F')   

        # Icon
        pdf.image(join(cwd,'assets','images','Next Quarter Preview','EMICalculator.svg'),px2MM(159),px2MM(244),px2MM(80),px2MM(80))
            
        # Date title
        pdf.set_xy(px2MM(279), px2MM(256))  
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.cell(px2MM(420), px2MM(60), "Next Consultation meeting date")

        # Generation Date
        pdf.set_xy(px2MM(1420), px2MM(254))  
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(56))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.cell(px2MM(420), px2MM(60), date)

        # White box for the background
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))  # White fill
        pdf.set_xy(px2MM(120), px2MM(448))  # Position of the box
        pdf.rect(px2MM(120), px2MM(448), px2MM(1683), px2MM(500), 'F')
    
    next_quarter_preview_pg_setup(pdf, date = json_data['next_quarter_preview']['date'])      

    actions = json_data['next_quarter_preview']['actions']
    title_y = mm2PX(pdf.get_y())+40
    for j in range(len(actions)):
        # print(title_y, actions[j]['title'])
        no_l = multicell_height(pdf,actions[j]['description'],1080)
        if 1080-title_y < 140+(no_l*32): 
            next_quarter_preview_pg_setup(pdf, date = json_data['next_quarter_preview']['date'])
            title_y = mm2PX(pdf.get_y())+40  # Reset title_y after adding a new page

        pdf.set_fill_color(*hex2RGB('#1A1A1D')) 
        pdf.rect(px2MM(160), px2MM(title_y+18), px2MM(10), px2MM(10), 'F')
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(190), px2MM(title_y))
        pdf.multi_cell(px2MM(1572),px2MM(42),actions[j]['title'],border=0,align="L")

        if actions[j]['description'] != "":
            sugg = mm2PX(pdf.get_y())+8
                    
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#4B4C51'))
            pdf.set_xy(px2MM(190), px2MM(sugg))
            pdf.multi_cell(px2MM(1572),px2MM(32),actions[j]['description'],border=0,align="L")

        title_y = mm2PX(pdf.get_y())+30


#//*-----disclaimer----*//
def disclaimer(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0,0,px2MM(1920),px2MM(1080),'F')

    pdf.set_xy(px2MM(140),px2MM(78))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(263), px2MM(84),"Disclaimer",border=0)
    
    
    pdf.set_xy(px2MM(140),px2MM(202))  
    pdf.set_font('LeagueSpartan-Medium', size=px2pts(36))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.cell(px2MM(1143), px2MM(45),"The Disclaimer page should be read in conjunction with this report.",border=0)
    
    pdf.set_xy(px2MM(140),px2MM(287))  
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(1760), px2MM(32),"This report is based on the data and presumptions supplied by you (client/ user/ member).",border=0)
    
    pdf.set_xy(px2MM(140),px2MM(343))  
    pdf.multi_cell(px2MM(1660), px2MM(32),"This report is designed to assess your present financial condition and recommend planning ideas and concepts that may be beneficial. This report aims to demonstrate how well-established financial planning principles can enhance your existing financial situation. This report does not imply a recommendation of any specific method, but rather offers broad, general advice on the benefits of a few financial planning principles.",border=0,align='L')

    pdf.set_xy(px2MM(140),px2MM(463))  
    text1="""The reports give estimates based on multiple hypotheses; thus they are purely speculative and do not represent assurances of investment returns. Before making any financial decisions or adopting any transactions or plans, you should speak with your tax and/or legal counsel and solely decide on the execution and implementation."""
    pdf.multi_cell(px2MM(1646), px2MM(32),text1,border=0,align="L")
    
    
    pdf.set_xy(px2MM(140),px2MM(527))  
    txt1 = """1 Finance Private Limited or any of its representatives will not be liable or responsible for any losses or damages incurred by the client/user/member as a result of this report."""
    pdf.multi_cell(px2MM(1640), px2MM(32),txt1,border=0,align="L")
    
    pdf.set_xy(px2MM(140),px2MM(615))  
    txt3 = """Prices mentioned in this report may have come from sources we believe to be dependable, but they are not guaranteed. It’s crucial to understand that past performance does not guarantee future outcomes and that actual results may vary from the forecasts in this report."""
    pdf.multi_cell(px2MM(1640), px2MM(32),txt3,border=0,align="L")
    
    pdf.set_xy(px2MM(140),px2MM(703))  
    txt4 = """Unless changes to your financial or personal situation necessitate a more frequent review, we advise that you evaluate your plan once a quarter. Please be aware that some discrepancies could occur due to different calculation methods."""
    pdf.multi_cell(px2MM(1650), px2MM(32),txt4,border=0,align="L")
    
    pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_xy(px2MM(140),px2MM(791))  
    txt5 = """Investment in securities market are subject to market risks. Read all the related documents carefully before investing. Registration granted by SEBI, enlistment of IA with Exchange and certification from NISM in no way guarantee performance of the intermediary or provide any assurance of returns to investors."""
    pdf.multi_cell(px2MM(1650), px2MM(32),txt5,border=0,align="L")
    
    
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_font('LeagueSpartan-light', size=px2pts(24))
    pdf.set_xy(px2MM(130),px2MM(966))  
    pdf.multi_cell(px2MM(350), px2MM(32),'SEBI RIA Registration No :',border=0,align="L")
    
    pdf.set_xy(px2MM(130),px2MM(1008))  
    pdf.multi_cell(px2MM(350), px2MM(32),'BSE Enlistment No :',border=0,align="L")
    
    pdf.set_xy(px2MM(1237),px2MM(966))  
    pdf.multi_cell(px2MM(350), px2MM(32),'Validity of Registration :',border=0,align="L")
    
    pdf.set_xy(px2MM(1416),px2MM(1008))  
    pdf.multi_cell(px2MM(350), px2MM(32),'Type of Registration :',border=0,align="L")
    
    
    pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.set_xy(px2MM(390),px2MM(966))  
    pdf.multi_cell(px2MM(1650), px2MM(32),'INA000017523',border=0,align="L")
    
    pdf.set_xy(px2MM(330),px2MM(1008))  
    pdf.multi_cell(px2MM(1650), px2MM(32),'1936',border=0,align="L")

    pdf.set_xy(px2MM(1479),px2MM(966))  
    pdf.multi_cell(px2MM(1650), px2MM(32),'December 22, 2022-Perpetual',border=0,align="L")

    pdf.set_xy(px2MM(1632),px2MM(1008))  
    pdf.multi_cell(px2MM(1650), px2MM(32),'Non-Individual',border=0,align="L")

    
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#1A1A1D')
    
    
#//*-----Def last Page
def lastpage(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0,0,px2MM(1920),px2MM(1080),'F')

    pdf.image(logo,px2MM(910),px2MM(162),px2MM(104),px2MM(119.88))
    pdf.set_xy(px2MM(712),px2MM(308))  
    pdf.set_font('LeagueSpartan-medium', size=px2pts(48))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(510),px2MM(67),"1 Finance Private Limited",border=0,align="L")
    
    pdf.set_xy(px2MM(860),px2MM(415))  
    pdf.set_font('LeagueSpartan-medium', size=px2pts(32))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.cell(px2MM(200),px2MM(45),"Office Address",border=0,align="L")

    pdf.set_font('LeagueSpartan-Light', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(505),px2MM(460))  
    text3="""Unit No. 1101 & 1102, 11th Floor, B - Wing, \nLotus Corporate Park, Goregaon (E), Mumbai-400063,"""
    pdf.multi_cell(px2MM(910),px2MM(56),text3,border=0,align="C")

    pdf.image(join(cwd,'assets','images','icons','gmail.svg'),px2MM(676),px2MM(602),px2MM(32),px2MM(32))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(25.33))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(724),px2MM(602))  
    pdf.cell(px2MM(241),px2MM(32),"care@1finance.co.in",border=0,align="L")

    pdf.image(join(cwd,'assets','images','icons','globe.svg'),px2MM(970),px2MM(602),px2MM(32),px2MM(32))
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(1014),px2MM(602))  
    pdf.cell(px2MM(243),px2MM(32),"https://1finance.co.in",border=0,align="L")


    # pdf.image(join(cwd,'assets','images','icons','call.svg'),px2MM(110),px2MM(948),px2MM(32),px2MM(32))
    # pdf.set_xy(px2MM(158),px2MM(948))  
    # pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(25.33))
    # pdf.set_text_color(*hex2RGB('#FFFFFF'))
    # pdf.cell(px2MM(158),px2MM(32),"022 - 6912 0000",border=0,align="L")
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(320),px2MM(674))  
    pdf.cell(px2MM(1287),px2MM(32),"Corresponding SEBI Local Office Address",border=0,align="C")
    
    pdf.set_font('LeagueSpartan-Light', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(330),px2MM(708))  
    pdf.cell(px2MM(1296),px2MM(32),"Securities and Exchange Board of India, SEBI Bhavan II, Plot No: C7, “G” Block, Bandra Kurla Complex, Bandra (East), Mumbai-400051",border=0,align="C")

    # pdf.line(110,791,1700,0)
    pdf.image(join(cwd,'assets','images','icons','Line 3.png'),px2MM(110),px2MM(791),px2MM(1700),px2MM(0.02))
    
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(108),px2MM(852))  
    pdf.cell(px2MM(310),px2MM(32),"Principal Officer",border=0,align="C")
    
    pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(108),px2MM(886))  
    pdf.multi_cell(px2MM(320),px2MM(32),"Mr. Akhil Rathi\nEmail id : po@1finance.co.in\nContact No : +91 22 69120000",border=0,align="C")
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(780),px2MM(852))  
    pdf.cell(px2MM(370),px2MM(32),"Compliance and Grievance Officer",border=0,align="C")
    
    pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#FFFFFF'))
    pdf.set_xy(px2MM(780),px2MM(886))  
    pdf.multi_cell(px2MM(370),px2MM(32),"Mr. Pradhumna Didwania \nEmail id : compliance@1finance.co.in\nContact No : +91 22 69121150",border=0,align="C")
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#FFFFFF') 

#//*-----Def Your 1 view
def your_1_view_detail(pdf,json_data,c_MoneyS,money_signData):
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0,0,px2MM(1920),px2MM(1080),'F')
    
    # df_asset = pd.DataFrame.from_dict(json_data['Asset'])

    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(px2MM(0),px2MM(80),px2MM(15),px2MM(84),'F')

    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.set_font('LeagueSpartan-Bold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.cell(px2MM(293),px2MM(84),"Your 1 View",border=0,align="L")

    # card 1
    pdf.set_fill_color(*hex2RGB('#E6E0FF'))
    pdf.rect(px2MM(120),px2MM(204),px2MM(527),px2MM(520),'F')
    # pdf.image(join(cwd,'assets','images','1_view_table','table_bg1.png'),px2MM(120),px2MM(204),px2MM(527),px2MM(592))

    pdf.image(join(cwd,'assets','images','icons','Assets.png'),px2MM(160),px2MM(244),px2MM(60),px2MM(60))
    pdf.set_xy(px2MM(240),px2MM(246))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(105),px2MM(56),"Assets",border=0,align="L")

    asset_table = pd.DataFrame(json_data['oneview']['assets'])
    assets = list(asset_table['title'])
    
    pdf.set_xy(px2MM(500),px2MM(253))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(105),px2MM(42),'₹ '+ format_cash2(float(json_data['oneview']['total']['assets'])),border=0,align="L")
    
    pdf.set_text_color(*hex2RGB('#000000'))
    for rows in range(len(assets)):
        pdf.set_line_width(px2MM(0.1))
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(160), px2MM(324+(rows*72)), px2MM(290), px2MM(72), 'DF')
        pdf.rect(px2MM(450), px2MM(324+(rows*72)), px2MM(157), px2MM(72), 'DF')
        
        pdf.set_xy(px2MM(180), px2MM(344+(rows*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.cell(px2MM(250),px2MM(32),assets[rows],border=0,align="L")

            #cal2 text
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_xy(px2MM(470), px2MM(344+(rows*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        if asset_table['value'].iloc[rows] ==' ' or asset_table['value'].iloc[rows] =='':
            pdf.cell(px2MM(117),px2MM(25),'-',border=0,align="R")
        elif asset_table['value'].iloc[rows] ==' ' or asset_table['value'].iloc[rows] =='':
            pdf.cell(px2MM(117),px2MM(25),'-',border=0,align="R")
        else:
            val = format_cash2(float(asset_table['value'].iloc[rows]))
            # pdf.cell(px2MM(117),px2MM(25),f"₹ {asset_table['value'].iloc[rows]}",border=0,align="R")
            pdf.cell(px2MM(117),px2MM(25),f"₹ {val}",border=0,align="R")
  
     # card 2
    pdf.set_fill_color(*hex2RGB('#DEEDFF'))
    pdf.rect(px2MM(697),px2MM(558),px2MM(527),px2MM(304),'F')

    pdf.image(join(cwd,'assets','images','icons','Income.png'),px2MM(737),px2MM(598),px2MM(60),px2MM(60))
    pdf.set_xy(px2MM(817),px2MM(600))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(116),px2MM(56),"Income",border=0,align="L")
    
    income_table = pd.DataFrame(json_data['oneview']['income'])
    income = list(income_table['title'])

    
    pdf.set_xy(px2MM(1050),px2MM(607))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(130),px2MM(42),'₹ '+format_cash2(float(json_data['oneview']['total']['income'])),border=0,align="R")
    
    pdf.set_text_color(*hex2RGB('#000000'))
    for rows in range(len(income_table)):
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(737), px2MM(678+(rows*72)), px2MM(447), px2MM(72), 'DF')
        pdf.rect(px2MM(1027), px2MM(678+(rows*72)), px2MM(157), px2MM(72), 'DF')

        # col1 text
        pdf.set_xy(px2MM(757), px2MM(698+(rows*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.cell(px2MM(250),px2MM(32),income[rows],border=0,align="L")

            #cal2 text
        pdf.set_xy(px2MM(1047), px2MM(698+(rows*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        if income_table['value'].iloc[rows] == '':
            pdf.cell(px2MM(117),px2MM(32),'-',border=0,align="R")
        else:
            val = format_cash2(float(income_table['value'].iloc[rows]))
            pdf.cell(px2MM(117),px2MM(32),f"₹ {val}",border=0,align="R")

    pdf.set_fill_color(*hex2RGB('#FFDDDA'))
    pdf.rect(px2MM(1273),px2MM(558),px2MM(527),px2MM(448),'F')

    pdf.image(join(cwd,'assets','images','icons','Expense.png'),px2MM(1313),px2MM(598),px2MM(60),px2MM(60))
    pdf.set_xy(px2MM(1393),px2MM(600))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(154),px2MM(56),"Expenses",border=0,align="L")

    
    expense_table = pd.DataFrame(json_data['oneview']['expense'])
    expense_keys = list(expense_table['title'])

    
    pdf.set_xy(px2MM(1630),px2MM(607))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(130),px2MM(42),'₹ '+format_cash2(float(json_data['oneview']['total']['expense'])),border=0,align="R")
    
    pdf.set_text_color(*hex2RGB('#000000'))
    for rows in range(len(expense_keys)):
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(1313), px2MM(678+(rows*72)), px2MM(290), px2MM(72), 'DF')
        pdf.rect(px2MM(1603), px2MM(678+(rows*72)), px2MM(157), px2MM(72), 'DF')
        
        pdf.set_xy(px2MM(1333), px2MM(698+(rows*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.cell(px2MM(250),px2MM(32),expense_keys[rows],border=0,align="L")

            #cal2 text
        pdf.set_xy(px2MM(1623), px2MM(698+(rows*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        if expense_table['value'].iloc[rows] == '':
            pdf.cell(px2MM(117),px2MM(32),"-",border=0,align="R")
        else:
            val = format_cash2(float(expense_table['value'].iloc[rows]))
            pdf.cell(px2MM(117),px2MM(32),f"₹ {val}",border=0,align="R")
    
    Insurance_table = pd.DataFrame(json_data['oneview']['insurance'])
    Insurance_keys = list(Insurance_table['title'])

    
    pdf.set_fill_color(*hex2RGB('#FFE7CC'))
    pdf.rect(px2MM(1273),px2MM(204),px2MM(527),px2MM(304),'F')

    pdf.image(join(cwd,'assets','images','icons','Insurance.png'),px2MM(1313),px2MM(244),px2MM(60),px2MM(60))
    pdf.set_xy(px2MM(1393),px2MM(246))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(158),px2MM(56),"Insurance",border=0,align="L")
    
    
    pdf.set_text_color(*hex2RGB('#000000'))
    for row in range(len(Insurance_table)):
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(1313), px2MM(324+(row*72)), px2MM(290), px2MM(72), 'DF')
        pdf.rect(px2MM(1603), px2MM(324+(row*72)), px2MM(157), px2MM(72), 'DF')
        
        # col1 text
        pdf.set_xy(px2MM(1333), px2MM(344+(row*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.cell(px2MM(250),px2MM(32),Insurance_keys[row],border=0,align="L")

            #cal2 text
        pdf.set_xy(px2MM(1623), px2MM(344+(row*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        if Insurance_table['value'].iloc[row]== '':  
            pdf.cell(px2MM(117),px2MM(32),'-',border=0,align="R")
        else:   
            pdf.cell(px2MM(117),px2MM(32),f"₹ {format_cash2(float(Insurance_table['value'].iloc[row]))}",border=0,align="R")


    #  # card 5
    
    try:
        val = json_data['oneview']['total']['liabilities']
    except Exception as e:
        val = 'N/A'
    pdf.set_fill_color(*hex2RGB('#FFF3DB'))
    pdf.rect(px2MM(696),px2MM(204),px2MM(527),px2MM(304),'F')

    pdf.image(join(cwd,'assets','images','icons','Liabilities.png'),px2MM(736),px2MM(244),px2MM(60),px2MM(60))
    pdf.set_xy(px2MM(816),px2MM(246))  
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(40))
    pdf.set_text_color(*hex2RGB('#000000'))
    pdf.cell(px2MM(155),px2MM(56),"Liabilities",border=0,align="L")
    
    pdf.set_xy(px2MM(1050),px2MM(253))  
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(30))
    pdf.set_text_color(*hex2RGB('#000000'))
    if val == 'N/A':
        pdf.cell(px2MM(130),px2MM(42),'0',border=0,align="R")
    else:
        
        pdf.cell(px2MM(130),px2MM(42),'₹ '+str(format_cash2(float(val))),border=0,align="R")
    
    
    
    liabilities_table = pd.DataFrame(json_data['oneview']['liabilities'])
    liabilities_keys = list(liabilities_table['title'])
    # liabilities_keys = list(liabilities.keys())
    
    pdf.set_text_color(*hex2RGB('#000000'))
    for row in range(len(liabilities_keys)):
        pdf.set_draw_color(*hex2RGB('#E9EAEE'))
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(736), px2MM(324+(row*72)), px2MM(290), px2MM(72), 'DF')
        pdf.rect(px2MM(1026), px2MM(324+(row*72)), px2MM(157), px2MM(72), 'DF')

        #     # col1 text
        pdf.set_xy(px2MM(756), px2MM(344+(row*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        pdf.cell(px2MM(250),px2MM(32),liabilities_keys[row],border=0,align="L")

            #cal2 text
        pdf.set_xy(px2MM(1046), px2MM(344+(row*72)))
        pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
        if liabilities_table['value'].iloc[row] =='':
            pdf.cell(px2MM(117),px2MM(25),'-',border=0,align="R")
        else:
            pdf.cell(px2MM(117),px2MM(25),f'₹ {format_cash2(float(liabilities_table["value"].iloc[row]))}',border=0,align="R")

    desc_text = '''Disclaimer: Numbers may not add up due to rounding.'''
    pdf.set_xy(px2MM(405), px2MM(1008))
    pdf.set_font('LeagueSpartan-Regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#ffffff'))
    pdf.multi_cell(px2MM(1110),px2MM(32),desc_text,border=0,align="C")
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#FFFFFF')  
    # global your_1_view_idx
    # your_1_view_idx = pdf.page_no()
 
 
# //* Your Top Most Priority----//
     
def top_most_priority(pdf,json_data,c_MoneyS,money_signData):
    
    
    tab_val1 = json_data["insurance_policy_evaluation"]['table']
    surrender_column_val = False
    if tab_val1 !=[]:
        check_column_df = pd.DataFrame.from_dict(tab_val1) 
        suggested_action_column = check_column_df['suggested_action'].tolist()

        if "Surrender" in suggested_action_column:
            surrender_column_val = True
        
    mf_value = json_data['mf_holding_evaluation']['total']['excess_annual_expense']
    surrender_value = json_data['insurance_policy_evaluation']['total']['top_most_priority_surrender_value']
    recommended_table = json_data['insurance_policy_evaluation']['recommendation_table']
    if recommended_table != []:
        recommended_life_cover = json_data['insurance_policy_evaluation']['recommendation_table'][1]['cover']
        existing_plan_cover = json_data['insurance_policy_evaluation']['recommendation_table'][0]['cover']
        saving_premium = json_data['insurance_policy_evaluation']['recommendation_table'][2]['annual_premium']
    
    if mf_value == "":
        mf_value = "0"
    else:
        mf_value_check = float(mf_value)
        if mf_value_check < 1000:
            mf_value = "0"
        
    if mf_value == "0" and surrender_column_val == False:
        return None
    
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.cell(px2MM(740),px2MM(84),"Your Top Most Priority",align='L')

    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F') 
    
    
    card2_space = 980
    # Card1
    card_x = 120     
    card_y = 240
    
    
    if mf_value != "0":
        mf_value = '~ ₹ '+str(format_cash3(float(mf_value)))
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(120),px2MM(204), px2MM(820),px2MM(751),'F')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(160),px2MM(224))  
        pdf.cell(px2MM(564),px2MM(48),"Mutual Funds",align='L')
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(160),px2MM(324))  
        pdf.cell(px2MM(564),px2MM(32),"Lost in Commissions",align='L')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#CC563C'))
        pdf.set_xy(px2MM(160),px2MM(364))  
        pdf.cell(px2MM(564),px2MM(48),mf_value,align='L')
        
        mf_value_x = mm2PX(pdf.get_x())
        mf_w = mm2PX(pdf.get_string_width(mf_value))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.set_xy(px2MM(170+mf_w),px2MM(368))  
        pdf.cell(px2MM(100),px2MM(48),"/ year",align='L')
        
        pdf.image(join(cwd,'assets', 'images','top_most_priorty','MFScore.svg'),px2MM(732), px2MM(244), px2MM(168), px2MM(162))
        
        
        # Comment box Card 1
        pdf.set_fill_color(*hex2RGB('#F3F6F9'))
        pdf.rect(px2MM(160),px2MM(555), px2MM(740),px2MM(360),'F')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.set_xy(px2MM(192),px2MM(587))  
        pdf.cell(px2MM(140),px2MM(32),"Action Steps",align='L')
        
        pdf.set_fill_color(*hex2RGB('#313236'))
        pdf.rect(px2MM(192),px2MM(651), px2MM(10),px2MM(10),'F')
        pdf.rect(px2MM(192),px2MM(701), px2MM(10),px2MM(10),'F')
        pdf.rect(px2MM(192),px2MM(786), px2MM(10),px2MM(10),'F')
        
        pdf.set_xy(px2MM(216),px2MM(635))  
        pdf.cell(px2MM(100),px2MM(42),"Stop",align='L')

        pdf.set_xy(px2MM(216),px2MM(685))  
        pdf.cell(px2MM(100),px2MM(42),"Choose",align='L')
        
        pdf.set_xy(px2MM(216),px2MM(770))  
        pdf.cell(px2MM(100),px2MM(42),"Shift",align='L')
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        
        pdf.set_xy(px2MM(270),px2MM(635))  
        pdf.cell(px2MM(600),px2MM(42),"your current investments and SIPs in Regular Mutual Funds",align='L')
        
        pdf.set_xy(px2MM(300),px2MM(685))  
        pdf.cell(px2MM(600),px2MM(42),"the high quality Direct Mutual Funds recommended by",align='L')
        pdf.set_xy(px2MM(216),px2MM(685+38))  
        pdf.cell(px2MM(600),px2MM(42),"your Advisor for new investments",align='L')
        
        pdf.set_xy(px2MM(270),px2MM(770))  
        pdf.cell(px2MM(600),px2MM(42),"your investments from Regular Mutual Funds to high quality",align='L')
        pdf.set_xy(px2MM(216),px2MM(770+38))  
        pdf.multi_cell(px2MM(652),px2MM(42),"Direct Mutual Funds in a tax efficient way as guided by your Advisor",align='L')
    else:
        card2_space = 120
        
    if surrender_column_val == True:
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(card2_space),px2MM(204), px2MM(820),px2MM(751),'F')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(card2_space+40),px2MM(224))  
        pdf.cell(px2MM(564),px2MM(48),"Life Insurance",align='L')
        
        pdf.image(join(cwd,'assets', 'images','top_most_priorty','life_insurance.svg'),px2MM(card2_space+618), px2MM(260), px2MM(168), px2MM(162))
        
        surrender_x = card2_space+40
        surrender_y = 324
        recommended_comment_check = recommended_life_cover
        
        if recommended_table != []:
            if recommended_life_cover == "":
                recommended_life_cover = "0"
            if float(recommended_life_cover) > 0:
                pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#65676D'))
                pdf.set_xy(px2MM(card2_space+40),px2MM(324))  
                pdf.cell(px2MM(564),px2MM(32),"Recommended Life Cover",align='L')
                
                
                val_for_trend = (float(recommended_life_cover)/float(existing_plan_cover))
                recommended_life_cover = '₹ '+str(format_cash3(float(recommended_life_cover)))
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
                pdf.set_text_color(*hex2RGB('#313236'))
                pdf.set_xy(px2MM(card2_space+40),px2MM(364))  
                pdf.cell(px2MM(564),px2MM(48),recommended_life_cover,align='L')
                
                inc_val = str(round(val_for_trend,1))+'x'
                rl_w1 = mm2PX(pdf.get_string_width(recommended_life_cover))
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#26A670'))
                pdf.set_xy(px2MM(card2_space+50+rl_w1),px2MM(368))  
                pdf.cell(px2MM(70),px2MM(48),inc_val,align='L')
                
                rl_w2 = mm2PX(pdf.get_string_width(inc_val))+rl_w1+56
                pdf.image(join(cwd,'assets', 'images','top_most_priorty','trend_arrow.svg'),px2MM(card2_space+rl_w2), px2MM(380), px2MM(24), px2MM(24))
                
                surrender_y = 426
            

                if saving_premium == "":
                    saving_premium = "0"
                    
                if float(saving_premium) > 0:
                    pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#65676D'))
                    pdf.set_xy(px2MM(card2_space+40),px2MM(426))  
                    pdf.cell(px2MM(564),px2MM(32),"Savings in Premium",align='L')
                    
                    saving_premium = '~ ₹ '+str(format_cash3(float(saving_premium)))
                    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
                    pdf.set_text_color(*hex2RGB('#313236'))
                    pdf.set_xy(px2MM(card2_space+40),px2MM(466))  
                    pdf.cell(px2MM(564),px2MM(48),saving_premium,align='L')
                    

                    sp_w = mm2PX(pdf.get_string_width(saving_premium))
                    pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
                    pdf.set_text_color(*hex2RGB('#313236'))
                    pdf.set_xy(px2MM(card2_space+50+sp_w),px2MM(472))  
                    pdf.cell(px2MM(70),px2MM(48),"/ year",align='L')
                    
                    surrender_x = mm2PX(pdf.get_x())+50
                    if surrender_x < card2_space+293:
                        surrender_x = card2_space+293 
        if surrender_value.isdigit() or (surrender_value.count('.') == 1 and surrender_value.replace('.', '').isdigit()) or surrender_value == 'Check market value':
            if surrender_value != 'Check market value':
                surrender_value = '~ ₹ '+str(format_cash3(float(surrender_value)))  
              
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#65676D'))
            pdf.set_xy(px2MM(surrender_x),px2MM(surrender_y))  
            pdf.cell(px2MM(564),px2MM(32),"Surrender Value",align='L')
            
            # surrender_value = '₹ '+str(format_cash3(float(surrender_value)))
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40))
            pdf.set_text_color(*hex2RGB('#313236'))
            pdf.set_xy(px2MM(surrender_x),px2MM(surrender_y+40))  
            pdf.cell(px2MM(564),px2MM(48),surrender_value,align='L')
        

        # Comment box Card 2
        pdf.set_fill_color(*hex2RGB('#F3F6F9'))
        pdf.rect(px2MM(card2_space+40),px2MM(555), px2MM(740),px2MM(360),'F')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.set_xy(px2MM(card2_space+72),px2MM(587))  
        pdf.cell(px2MM(140),px2MM(32),"Action Steps",align='L')
        
        y = mm2PX(pdf.get_y())
        pdf.set_fill_color(*hex2RGB('#313236'))
        pdf.rect(px2MM(card2_space+72),px2MM(y+64), px2MM(10),px2MM(10),'F')
        pdf.set_xy(px2MM(card2_space+96),px2MM(y+48))  
        pdf.cell(px2MM(150),px2MM(42),"Surrender",align='L')
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#313236'))
        pdf.set_xy(px2MM(card2_space+210),px2MM(y+48))  
        pdf.cell(px2MM(600),px2MM(42),"the mentioned policies to keep your insurances and",align='L')
        pdf.set_xy(px2MM(card2_space+96),px2MM(y+86))  
        pdf.cell(px2MM(652),px2MM(42),"investments separate",align='L')
        y = mm2PX(pdf.get_y())
        
        if recommended_comment_check == "":
            recommended_comment_check = "0"
        if float(recommended_comment_check) > 0:
            pdf.set_fill_color(*hex2RGB('#313236'))
            pdf.rect(px2MM(card2_space+72),px2MM(y+66), px2MM(10),px2MM(10),'F')
            
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24)) 
            pdf.set_xy(px2MM(card2_space+96),px2MM(721))  
            pdf.cell(px2MM(100),px2MM(42),"Purchase",align='L')
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_xy(px2MM(card2_space+200),px2MM(721))  
            pdf.cell(px2MM(600),px2MM(42),"Term Insurance to get more life cover at a lesser",align='L')
            pdf.set_xy(px2MM(card2_space+96),px2MM(758))  
            pdf.cell(px2MM(652),px2MM(42),"premium",align='L')
            
            pdf.rect(px2MM(card2_space+72),px2MM(822), px2MM(10),px2MM(10),'F')
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24)) 
            pdf.set_xy(px2MM(card2_space+96),px2MM(806))  
            pdf.cell(px2MM(100),px2MM(42),"Invest",align='L')
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_xy(px2MM(card2_space+160),px2MM(806))  
            pdf.cell(px2MM(600),px2MM(42)," the surrender proceeds and net savings as guided by the",align='L')
            pdf.set_xy(px2MM(card2_space+96),px2MM(842))  
            pdf.cell(px2MM(652),px2MM(42),"Advisor",align='L')
            
    #//*-----Index Text of Page--**////
    index_text(pdf,'#000000')  
    global your_top_most_priority
    your_top_most_priority = pdf.page_no()
    
    
    
#//*----Tax Liability & Potential Savings----*//
def tax_liability_potential_planning(pdf,json_data,c_MoneyS,money_signData):
    if json_data["tax_planning"]=={}:
        return None
    locale.setlocale(locale.LC_MONETARY, 'en_IN')
    
    
    pdf.add_page()
    pdf.set_fill_color(*hex2RGB('#FCF8ED'))
    pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(120),px2MM(80))  
    pdf.cell(px2MM(840),px2MM(84),"Tax Liability & Potential Savings",align='L')

    pdf.set_fill_color(*hex2RGB('#000000'))
    pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F') 
    
    
    financial_year = json_data["tax_planning"].get('financial_year')
    if financial_year == None:
        financial_year = "Financial Year April 2024- March 2025"
    pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#1A1A1D'))
    pdf.set_xy(px2MM(1400),px2MM(114))  
    pdf.cell(px2MM(400),px2MM(32),financial_year,align='L')
    
    #//*-----Index Text of Page--**////
    index_text(pdf,'#000000')  
    
    global your_fin_analysis_sub_comment
    your_fin_analysis_sub_comment.append('Tax Evaluation')
    
    regime_type = json_data['tax_planning']['tax_liability_potential_saving'].get('regime_type')
    if regime_type!=None:
        regime_type = regime_type.lower()
        regime_type_list = regime_type.split(" ")
            
    no_breakup_table = json_data['tax_planning']['tax_liability_potential_saving'].get('no_break_up')
    if no_breakup_table is None:
        no_breakup_table = []
        
    if no_breakup_table != []:
        pdf.set_fill_color(*hex2RGB('#FAFBFD'))
        pdf.rect(px2MM(120),px2MM(240), px2MM(956),px2MM(121),'F')
        pdf.rect(px2MM(120),px2MM(361), px2MM(311),px2MM(450),'F')
        
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(431),px2MM(361), px2MM(645),px2MM(450),'F')
        
        pdf.set_fill_color(*hex2RGB('#E9EAEE'))
        pdf.rect(px2MM(120),px2MM(361), px2MM(956),px2MM(0.5),'F')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(145),px2MM(284.5))  
        pdf.cell(px2MM(200),px2MM(32),"Tax Comparison",align='L')
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(145),px2MM(420))  
        pdf.cell(px2MM(200),px2MM(32),"Deductions",align='L')
        
        pdf.set_xy(px2MM(145),px2MM(570))  
        pdf.cell(px2MM(200),px2MM(32),"Taxable Income",align='L')
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#65676D'))
        pdf.set_xy(px2MM(145),px2MM(720.5))  
        pdf.cell(px2MM(200),px2MM(32),"Total Tax Payable",align='L')
        
        # Table Values
        
        # Tax Planning
        x = (431,753.5)
        y = (279.5,420,570,720)
        len_no_breakup_table = len(no_breakup_table)

        for i in range(len_no_breakup_table):
            x_axis = x[i]
            pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
            pdf.set_text_color(*hex2RGB('#000000'))
            tax_comp_w = x_axis+85
            len_tax_comp = mm2PX(pdf.get_string_width(no_breakup_table[i]['tax_comparison']))+55
            if no_breakup_table[i]['opted'] == True:
                pdf.set_font('LeagueSpartan-regular', size=px2pts(24))        
                pdf.set_text_color(*hex2RGB('#898B90'))
                pdf.set_xy(px2MM(x_axis+len_tax_comp),px2MM(y[0]+6))  
                pdf.cell(px2MM(300),px2MM(32),"(Opted)",align='L')
                
                tax_comp_w = x_axis+47
                
            if no_breakup_table[i]['recommended'] == True:
                pdf.set_fill_color(*hex2RGB('#DEF7F1'))
                pdf.rect(px2MM(x_axis),px2MM(361), px2MM(324),px2MM(450),'F')
                pdf.set_fill_color(*hex2RGB('#ACE4D7'))
                pdf.rect(px2MM(x_axis),px2MM(361), px2MM(324),px2MM(36),'F')
                pdf.set_char_spacing(px2MM(7))
                pdf.set_font('LeagueSpartan-Bold', size=px2pts(18))        
                pdf.set_text_color(*hex2RGB('#000000'))
                pdf.set_xy(px2MM(x_axis),px2MM(361))  
                pdf.cell(px2MM(324),px2MM(36),"RECOMMENDED",align='C')
                pdf.set_char_spacing(px2MM(0.7))
                
            pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.set_xy(px2MM(tax_comp_w),px2MM(y[0]))  
            pdf.cell(px2MM(150),px2MM(42),no_breakup_table[i]['tax_comparison'].title(),align='L')
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.set_xy(px2MM(x_axis),px2MM(y[1]))
            if no_breakup_table[i]['deductions'].isdigit() or (no_breakup_table[i]['deductions'].count('.') == 1 and no_breakup_table[i]['deductions'].replace('.', '').isdigit()):  
                deduction = str(locale.currency(float(no_breakup_table[i]['deductions']), grouping=True))
                deduction = deduction.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                pdf.cell(px2MM(322.5),px2MM(32),deduction,align='C')
                
            pdf.set_xy(px2MM(x_axis),px2MM(y[2]))
            if no_breakup_table[i]['taxable_income'].isdigit() or (no_breakup_table[i]['taxable_income'].count('.') == 1 and no_breakup_table[i]['taxable_income'].replace('.', '').isdigit()):  
                taxable_income = str(locale.currency(float(no_breakup_table[i]['taxable_income']), grouping=True))
                taxable_income = taxable_income.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                pdf.cell(px2MM(322.5),px2MM(32),taxable_income,align='C')
            
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))    
            pdf.set_xy(px2MM(x_axis),px2MM(y[3]))
            if no_breakup_table[i]['total_tax_payable'].isdigit() or (no_breakup_table[i]['total_tax_payable'].count('.') == 1 and no_breakup_table[i]['total_tax_payable'].replace('.', '').isdigit()):  
                total_tax_payable = str(locale.currency(float(no_breakup_table[i]['total_tax_payable']), grouping=True))
                total_tax_payable = total_tax_payable.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                pdf.cell(px2MM(322.5),px2MM(32),total_tax_payable,align='C')
        
        # Green vertivle line
        pdf.set_fill_color(*hex2RGB('#229479'))
        pdf.rect(px2MM(753.5),px2MM(240), px2MM(0.5),px2MM(571),'F')
                
        # bottom rectangular box comment
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(140),px2MM(900), px2MM(1640),px2MM(80),'F')
        pdf.set_font('LeagueSpartan-medium', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(180),px2MM(924))  
        pdf.cell(px2MM(1560),px2MM(32),'You may share the exemptions & deduction details with your Advisor. This will help us plan your tax strategy and maximize your savings.',align='C')
        
        # Action of this year
        act_of_this_year = json_data['tax_planning']['action_of_this_year']
    
        if act_of_this_year ==[]:
            return None
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(1136),px2MM(240))  
        pdf.cell(px2MM(664),px2MM(42),'Actions for this year',align='L')
        
        def act_page_create(pdf):
            pdf.add_page()
            pdf.set_fill_color(*hex2RGB('#FCF8ED'))
            pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            pdf.set_xy(px2MM(120),px2MM(80))  
            pdf.cell(px2MM(900),px2MM(84),"Tax Liability & Potential Savings",align='L')

            pdf.set_fill_color(*hex2RGB('#000000'))
            pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F')
            
            #//*-----Index Text of Page--**////
            index_text(pdf,'#000000') 
            
            
        rem_y = 302
        comm_x_axis = 1136
        comm_width = 634
        
        for i in range(len(act_of_this_year)):
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
            comment = act_of_this_year[i].rstrip('\n')
            if 1080-rem_y < (220+(42*(multicell_height(pdf,comment,comm_width)))):
                act_page_create(pdf)
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
                pdf.set_text_color(*hex2RGB('#1A1A1D'))
                pdf.set_xy(px2MM(120),px2MM(204))
                pdf.cell(px2MM(1435),px2MM(42),'Actions for this year',align='L')
                rem_y = 266
                comm_width = 1435
                comm_x_axis = 120
                
            pdf.set_fill_color(*hex2RGB('#000000'))
            pdf.rect(px2MM(comm_x_axis),px2MM(rem_y+18), px2MM(10),px2MM(10),'F')
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
            pdf.set_text_color(*hex2RGB('#1A1A1D'))
            comment = act_of_this_year[i].rstrip('\n')
            pdf.set_xy(px2MM(comm_x_axis+30),px2MM(rem_y))  
            pdf.multi_cell(px2MM(comm_width),px2MM(42),comment,align='L')
            
            rem_y = mm2PX(pdf.get_y())+16
        

        
    else:
        liab_comp_table = json_data['tax_planning']['tax_liability_potential_saving'].get('tax_liability_comparison_table')
        if liab_comp_table is not None:
            table_current = json_data['tax_planning']['tax_liability_potential_saving']['tax_liability_comparison_table']['current']
            table_after_planning = json_data['tax_planning']['tax_liability_potential_saving']['tax_liability_comparison_table']['after_planning']
            # Table Rectangle boxes
            pdf.set_fill_color(*hex2RGB('#FAFBFD'))
            pdf.rect(px2MM(120),px2MM(204), px2MM(403),px2MM(571),'F')
            pdf.rect(px2MM(523),px2MM(204), px2MM(1277),px2MM(121),'F')
            
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.rect(px2MM(523),px2MM(325), px2MM(1277),px2MM(450),'F')
            
            pdf.set_fill_color(*hex2RGB('#F3F6F966'))
            pdf.rect(px2MM(842),px2MM(325), px2MM(0.4),px2MM(450),'F')
            

            # table headings
            
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.set_xy(px2MM(148),px2MM(248.5))  
            pdf.cell(px2MM(200),px2MM(32),"Tax Comparison",align='L')
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.set_xy(px2MM(535),px2MM(243.5))  
            pdf.cell(px2MM(614),px2MM(42),"Current",align='C')
            
            pdf.set_xy(px2MM(1267),px2MM(243.5))  
            pdf.cell(px2MM(427),px2MM(42),"After Planning",align='C')
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
            pdf.set_text_color(*hex2RGB('#898B90'))
            pdf.set_xy(px2MM(145),px2MM(365.5))  
            pdf.cell(px2MM(200),px2MM(32),"Tax Regime",align='L')
            
            pdf.set_xy(px2MM(145),px2MM(477.5))  
            pdf.cell(px2MM(200),px2MM(32),"Deductions",align='L')
            
            pdf.set_xy(px2MM(145),px2MM(590.5))  
            pdf.cell(px2MM(200),px2MM(32),"Taxable Income",align='L')
            
            pdf.set_text_color(*hex2RGB('#65676D'))
            pdf.set_xy(px2MM(145),px2MM(702.5))  
            pdf.cell(px2MM(200),px2MM(32),"Total Tax Payable",align='L')
            
            # CURRENT
            x = (535,854)
            y = (385.5,477,590,702)
            len_current = len(table_current)

            for i in range(len_current):
                x_axis = x[i]
                
                if table_current[i]['opted'] == True:
                    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(18))        
                    pdf.set_text_color(*hex2RGB('#4B4C51'))
                    pdf.set_fill_color(*hex2RGB('#E9EAEE'))
                    pdf.rect(px2MM(x_axis-12),px2MM(325), px2MM(319),px2MM(36),'F')
                    pdf.set_xy(px2MM(x_axis-12),px2MM(325))  
                    pdf.cell(px2MM(319),px2MM(36),"O P T E D",align='C')
                    
                pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
                pdf.set_text_color(*hex2RGB('#898B90'))
                pdf.set_xy(px2MM(x_axis),px2MM(y[0]))  
                pdf.cell(px2MM(295),px2MM(42),table_current[i]['tax_regime'].title(),align='C')
                
                pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#000000'))
                pdf.set_xy(px2MM(x_axis),px2MM(y[1]))
                if table_current[i]['deductions'].isdigit() or (table_current[i]['deductions'].count('.') == 1 and table_current[i]['deductions'].replace('.', '').isdigit()):  
                    deduction = str(locale.currency(float(table_current[i]['deductions']), grouping=True))
                    deduction = deduction.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                    pdf.cell(px2MM(295),px2MM(32),deduction,align='C')
                    
                pdf.set_xy(px2MM(x_axis),px2MM(y[2]))
                if table_current[i]['taxable_income'].isdigit() or (table_current[i]['taxable_income'].count('.') == 1 and table_current[i]['taxable_income'].replace('.', '').isdigit()):  
                    taxable_income = str(locale.currency(float(table_current[i]['taxable_income']), grouping=True))
                    taxable_income = taxable_income.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                    pdf.cell(px2MM(295),px2MM(32),taxable_income,align='C')
                
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))    
                pdf.set_xy(px2MM(x_axis),px2MM(y[3]))
                if table_current[i]['total_tax_payable'].isdigit() or (table_current[i]['total_tax_payable'].count('.') == 1 and table_current[i]['total_tax_payable'].replace('.', '').isdigit()):  
                    total_tax_payable = str(locale.currency(float(table_current[i]['total_tax_payable']), grouping=True))
                    total_tax_payable = total_tax_payable.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                    pdf.cell(px2MM(295),px2MM(32),total_tax_payable,align='C')
            
            # Tax Planning
            x = (1173,1492)
            y = (385.5,477,590,702)
            len_after_planning = len(table_after_planning)

            for i in range(len_after_planning):
                x_axis = x[i]
                
                if table_after_planning[i]['recommended'] == True:
                    pdf.set_fill_color(*hex2RGB('#DEF7F1'))
                    pdf.rect(px2MM(x_axis-11),px2MM(325), px2MM(319),px2MM(450),'F')
                    pdf.set_fill_color(*hex2RGB('#ACE4D7'))
                    pdf.rect(px2MM(x_axis-11),px2MM(325), px2MM(319),px2MM(36),'F')
                    pdf.set_char_spacing(px2MM(7))
                    pdf.set_font('LeagueSpartan-Bold', size=px2pts(18))        
                    pdf.set_text_color(*hex2RGB('#000000'))
                    pdf.set_xy(px2MM(x_axis-11),px2MM(325))  
                    pdf.cell(px2MM(319),px2MM(36),"RECOMMENDED",align='C')
                    pdf.set_char_spacing(px2MM(0.7))
                    
                pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
                pdf.set_text_color(*hex2RGB('#898B90'))
                pdf.set_xy(px2MM(x_axis),px2MM(y[0]))  
                pdf.cell(px2MM(295),px2MM(42),table_after_planning[i]['tax_regime'].title(),align='C')
                
                pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
                pdf.set_text_color(*hex2RGB('#000000'))
                pdf.set_xy(px2MM(x_axis),px2MM(y[1]))
                if table_after_planning[i]['deductions'].isdigit() or (table_after_planning[i]['deductions'].count('.') == 1 and table_after_planning[i]['deductions'].replace('.', '').isdigit()):  
                    deduction = str(locale.currency(float(table_after_planning[i]['deductions']), grouping=True))
                    deduction = deduction.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                    pdf.cell(px2MM(295),px2MM(32),deduction,align='C')
                    
                pdf.set_xy(px2MM(x_axis),px2MM(y[2]))
                if table_after_planning[i]['taxable_income'].isdigit() or (table_after_planning[i]['taxable_income'].count('.') == 1 and table_after_planning[i]['taxable_income'].replace('.', '').isdigit()):  
                    taxable_income = str(locale.currency(float(table_after_planning[i]['taxable_income']), grouping=True))
                    taxable_income = taxable_income.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                    pdf.cell(px2MM(295),px2MM(32),taxable_income,align='C')
                
                pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))    
                pdf.set_xy(px2MM(x_axis),px2MM(y[3]))
                if table_after_planning[i]['total_tax_payable'].isdigit() or (table_after_planning[i]['total_tax_payable'].count('.') == 1 and table_after_planning[i]['total_tax_payable'].replace('.', '').isdigit()):  
                    total_tax_payable = str(locale.currency(float(table_after_planning[i]['total_tax_payable']), grouping=True))
                    total_tax_payable = total_tax_payable.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                    pdf.cell(px2MM(295),px2MM(32),total_tax_payable,align='C')
            
            # Green vertivle line
            pdf.set_fill_color(*hex2RGB('#229479'))
            pdf.rect(px2MM(1161),px2MM(204), px2MM(0.5),px2MM(571),'F')
            
            # Bottom White Box
            pdf.set_fill_color(*hex2RGB('#FFFFFF'))
            pdf.rect(px2MM(370),px2MM(816), px2MM(1180),px2MM(164),'F')
            
            # Headings
            pdf.set_font('LeagueSpartan-regular', size=px2pts(24)) 
            pdf.set_text_color(*hex2RGB('#898B90'))
            pdf.set_xy(px2MM(410),px2MM(853))  
            pdf.cell(px2MM(250),px2MM(32),"Current Payable Tax",align='L')
            
            pdf.set_xy(px2MM(730),px2MM(853))  
            pdf.cell(px2MM(300),px2MM(32),"Recommended Payable Tax",align='L')
            
            pdf.set_font('LeagueSpartan-regular', size=px2pts(40)) 
            pdf.set_text_color(*hex2RGB('#65676D'))
            pdf.set_xy(px2MM(1150),px2MM(836))  
            pdf.cell(px2MM(250),px2MM(56),"Potential Tax",align='L')
            
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(40)) 
            pdf.set_text_color(*hex2RGB('#229479'))
            pdf.set_xy(px2MM(1380),px2MM(836))  
            pdf.cell(px2MM(250),px2MM(56),"Savings",align='L')
            
            # Symbols
            
            pdf.set_fill_color(*hex2RGB('#FFDB80'))
            pdf.rect(px2MM(650),px2MM(878), px2MM(40),px2MM(40),'F')
            
            pdf.set_fill_color(*hex2RGB('#82DBC6'))
            pdf.rect(px2MM(1063),px2MM(878), px2MM(40),px2MM(40),'F')
            
            pdf.image(join(cwd,'assets', 'images','tax_planning','minus.svg'),px2MM(650),px2MM(878), px2MM(40),px2MM(40))
            pdf.image(join(cwd,'assets', 'images','tax_planning','equal.svg'),px2MM(1071),px2MM(892), px2MM(23),px2MM(13))

            # Values
            current_payable_tax = json_data['tax_planning']['tax_liability_potential_saving']['current_payable_tax']
            pdf.set_font('LeagueSpartan-medium', size=px2pts(35)) 
            pdf.set_text_color(*hex2RGB('#000000'))
            pdf.set_xy(px2MM(410),px2MM(900)) 
            if current_payable_tax.isdigit() or (current_payable_tax.count('.') == 1 and current_payable_tax.replace('.', '').isdigit()):  
                current_payable_tax = str(locale.currency(float(current_payable_tax), grouping=True))
                current_payable_tax = current_payable_tax.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                pdf.cell(px2MM(220),px2MM(42),current_payable_tax,align='C',border='0')
                
            recommended_payable_tax = json_data['tax_planning']['tax_liability_potential_saving']['recommended_payable_tax']
            pdf.set_xy(px2MM(730),px2MM(900)) 
            if recommended_payable_tax.isdigit() or (recommended_payable_tax.count('.') == 1 and recommended_payable_tax.replace('.', '').isdigit()):  
                recommended_payable_tax = str(locale.currency(float(recommended_payable_tax), grouping=True))
                recommended_payable_tax = recommended_payable_tax.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                pdf.cell(px2MM(268),px2MM(42),recommended_payable_tax,align='C')
                
            potential_tax_saving = json_data['tax_planning']['tax_liability_potential_saving']['potential_tax_saving']
            pdf.set_font('LeagueSpartan-medium', size=px2pts(56)) 
            pdf.set_xy(px2MM(1160),px2MM(900)) 
            if int(potential_tax_saving.count('.') == 1 and potential_tax_saving.replace('.', '').isdigit()) or int(potential_tax_saving):  
                potential_tax_saving_fm = str(locale.currency(float(potential_tax_saving), grouping=True))
                if float(potential_tax_saving) < 0:
                    potential_tax_saving_fm = potential_tax_saving_fm.split('.')[0].replace('₹ ', '₹-').replace('₹-', '₹ -')
                else:
                    potential_tax_saving_fm = potential_tax_saving_fm.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                x = mm2PX(pdf.get_string_width(potential_tax_saving_fm))+10
                pdf.cell(px2MM(x),px2MM(32),potential_tax_saving_fm,align='L')
            
            if regime_type != "":
                regime_type_list = regime_type.split(" ")
                if regime_type_list[0].lower() == "old":
                    old_regime(pdf,json_data,regime_type)
                elif regime_type_list[0].lower() == "new":
                    new_regime(pdf,json_data,regime_type)  
            

#//*----Tax Liability & Potential Savings (Old Regime)----*//
def old_regime(pdf,json_data,regime_type):
    
    tdet = json_data['tax_planning']['tax_deduction_exemption_table']
    if tdet ==[]:
        return None
    
    star_val = False
    for i in range(len(tdet)):
        if tdet[i]['suggested_utilisation_additional_val'] !="":
          star_val = True
          break  
    
    def add_page_with_column(pdf,json_data,regime_type):
        locale.setlocale(locale.LC_MONETARY, 'en_IN')
    
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(120),px2MM(80))  
        pdf.cell(px2MM(780),px2MM(84),"Tax Deductions & Exemptions",align='L')

        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#000000') 
        
        pdf.set_font('LeagueSpartan-light', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(120),px2MM(1035)) 
        if star_val == True:
            pdf.cell(px2MM(110),px2MM(25),"* Includes only the increase in investment",align='L')
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(1686),px2MM(114)) 
        regime_type_list = regime_type.split(" ")
        if regime_type_list[0].lower() == "old":
            pdf.cell(px2MM(120),px2MM(32),"Old Regime",align='L')
            

        
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(120),px2MM(204), px2MM(1319),px2MM(725),'F')
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(160),px2MM(244))  
        pdf.cell(px2MM(623),px2MM(32),"Deductions & Exemptions",align='L')
        
        pdf.set_xy(px2MM(800),px2MM(244))  
        pdf.cell(px2MM(160),px2MM(32),"Max. Deduction",align='L')
        
        pdf.set_xy(px2MM(985),px2MM(244))  
        pdf.cell(px2MM(185),px2MM(32),"Current Utilisation",align='R')
        
        pdf.set_xy(px2MM(1190),px2MM(244))  
        pdf.cell(px2MM(215),px2MM(32),"Suggested Utilisation",align='R')
        
        pdf.set_fill_color(*hex2RGB('#E9EAEE'))
        pdf.rect(px2MM(160),px2MM(292), px2MM(1239),px2MM(1),'FD')
        
        return 308
              
    new_y = add_page_with_column(pdf,json_data,regime_type)
    
    h_rect = 65
    
    # Function to find height of rect
    def get_rect_h(pdf,tdet,new_y):
        pdf.set_font('LeagueSpartan-medium', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#000000'))
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(160),px2MM(new_y))  
        pdf.multi_cell(px2MM(630),px2MM(32),tdet[i]['tax_class'],border='0',align='L')
        
        tc_sub_y  =  mm2PX(pdf.get_y())
        
        if tdet[i]['tax_class_sub_val'] != "":
            pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
            pdf.set_text_color(*hex2RGB('#898B90'))
            pdf.set_xy(px2MM(160),px2MM(tc_sub_y+8))  
            pdf.multi_cell(px2MM(640),px2MM(25),tdet[i]['tax_class_sub_val'],align='L')
        
        tc_sub_new_y  =  mm2PX(pdf.get_y())
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#000000'))
            
        pdf.set_xy(px2MM(1190),px2MM(new_y))      
        if tdet[i]['suggested_utilisation'] == "" or tdet[i]['suggested_utilisation'] == "-":
            pdf.multi_cell(px2MM(210),px2MM(32),'-',border='0',align='R')
        elif tdet[i]['suggested_utilisation'].isdigit() or (tdet[i]['suggested_utilisation'].count('.') == 1 and tdet[i]['suggested_utilisation'].replace('.', '').isdigit()):
            su = str(locale.currency(float(tdet[i]['suggested_utilisation']), grouping=True))
            # su = str(format_currency(float(tdet[i]['suggested_utilisation']), 'INR', locale='en_IN', format=u'₹ #,##0'))
            su = su.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
            pdf.multi_cell(px2MM(210),px2MM(32),su,border='0',align='R')
        else:
            pdf.multi_cell(px2MM(210),px2MM(32),tdet[i]['suggested_utilisation'],border='0',align='R')
            
        su_sub_y  =  mm2PX(pdf.get_y())
        
        if tdet[i]['suggested_utilisation_additional_val'] != "":
            pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
            pdf.set_text_color(*hex2RGB('#898B90'))
            su_ad_val = str(locale.currency(float(tdet[i]['suggested_utilisation_additional_val']), grouping=True))
            # su_ad_val = str(format_currency(float(tdet[i]['suggested_utilisation_additional_val']), 'INR', locale='en_IN', format=u'₹ #,##0'))
            su_ad_val = su_ad_val.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
            pdf.set_xy(px2MM(1190),px2MM(su_sub_y+8))  
            pdf.multi_cell(px2MM(210),px2MM(25),'Additional '+su_ad_val+'*',align='R')
        
        su_sub_new_y = mm2PX(pdf.get_y())
            
        c1_h = tc_sub_new_y-new_y
        c2_h = su_sub_new_y-new_y
        
        if c1_h >= c2_h:
            return c1_h+32,tc_sub_new_y+24
        elif c2_h > c1_h:
            return c2_h+32,su_sub_new_y+24
    # function for bargraph    
    def bar_plot(pdf,tdet):
        img_name = 'utilisation_of_deduction.png' 
        
        font_path = join(cwd,'assets','fonts','Prata','League_Spartan','static')
        font_files = font_manager.findSystemFonts(fontpaths=font_path)
        for font_file in font_files:
            font_manager.fontManager.addfont(font_file)
        colors = ['#E9EAEE','#90BEF8']
        labels = ['Current','Recommended']
        # font = {'family': 'league spartan','color':  'black','weight': 'normal','size': 24,}
        sizes = [float(tdet[-1]['current_utilisation']),float(tdet[-1]['suggested_utilisation'])]
        
        dict_val = {"name":labels,"value":sizes,"color":colors}
        dict_val2 = [{"Current":float(tdet[-1]['current_utilisation']),"Recommended":float(tdet[-1]['suggested_utilisation'])}]
        pd_data = pd.DataFrame(dict_val)
        pd_data1 = pd.DataFrame(dict_val2)
        
        fig,ax0 = plt.subplots(figsize=(1.8, 5))
        # fig,ax0 = plt.subplots(figsize=(0.1,0.3))
        cols = ['#E9EAEE' if x == 'Current'  else '#90BEF8' for x in pd_data.name ]
        ax=sns.barplot(x='name',y='value',data=pd_data,palette=cols,width=1)
        for g in ax.patches:
            ax.annotate('₹ '+format_cash2(g.get_height()),
                        
                        (g.get_x() + g.get_width() / 2., g.get_height()),
                        ha = 'center', va = 'center',
                        xytext = (0,10),font='Arial',
                        textcoords = 'offset points')
        plt.xlabel(None)
        plt.ylabel(None)
        plt.tick_params(axis='x',labelsize=0)
        plt.tick_params(axis='y',labelsize=0)
        plt.grid(False)
        sns.despine(fig=None, ax=None, top=True, right=True, left=True, bottom=True, offset=None, trim=False)
        plt.tick_params(left = False,bottom = False,label1On=False)
        plt.savefig('utilisation_of_deduction.png',dpi=250)
        
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(1479),px2MM(204), px2MM(321),px2MM(725),'F')
        # pdf.image('utilisation_of_deduction.png',px2MM(120),px2MM(234), px2MM(321),px2MM(680))
        pdf.image('utilisation_of_deduction.png',px2MM(1549),px2MM(264), px2MM(180),px2MM(620))
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(1519),px2MM(244))  
        pdf.cell(px2MM(241),px2MM(32),'Utilisation of',align='C')
        pdf.set_xy(px2MM(1519),px2MM(276))  
        pdf.cell(px2MM(241),px2MM(32),'Deductions/Exemptions',align='C')
        
        pdf.set_fill_color(*hex2RGB('#E9EAEE'))
        pdf.rect(px2MM(1519),px2MM(870), px2MM(12),px2MM(12),'F')
        pdf.set_font('LeagueSpartan-medium', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(1539),px2MM(864))  
        pdf.cell(px2MM(65),px2MM(25),'Current',align='L')
        
        pdf.set_fill_color(*hex2RGB('#90BEF8'))
        pdf.rect(px2MM(1630),px2MM(870), px2MM(12),px2MM(12),'F')
        pdf.set_xy(px2MM(1650),px2MM(864))  
        pdf.cell(px2MM(120),px2MM(25),'Recommended',align='L')
        
    bar_plot(pdf,tdet)
    
    # pdf.image('utilisation_of_deduction.png',px2MM(160),px2MM(292),px2MM(200),px2MM(516))
    for i in range(len(tdet)):
        if 1080-new_y < 207:
            new_y = add_page_with_column(pdf,json_data,regime_type) 
            bar_plot(pdf,tdet)
            h_rect,next_new_y = get_rect_h(pdf,tdet,new_y)
        # elif i==len(tdet)-2 and 1080-new_y < 350:
        elif i==len(tdet)-2 and 1080-new_y < 350:
            new_y = add_page_with_column(pdf,json_data,regime_type) 
            bar_plot(pdf,tdet)
            h_rect,next_new_y = get_rect_h(pdf,tdet,new_y)
        else:
            h_rect,next_new_y = get_rect_h(pdf,tdet,new_y)
        # if i == 1:
        #     break        
            
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(120),px2MM(new_y), px2MM(1319),px2MM(h_rect),'F')
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(20))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(160),px2MM(new_y))  
        pdf.multi_cell(px2MM(630),px2MM(32),tdet[i]['tax_class'],border='0',align='L')
        
        tc_sub_y  =  mm2PX(pdf.get_y())+8
        pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(160),px2MM(tc_sub_y))  
        pdf.cell(px2MM(640),px2MM(25),tdet[i]['tax_class_sub_val'],align='L')
        
        if i == len(tdet)-1:
            su_val_color = '#649DE5'
            new_y = new_y-2
            pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
            pdf.set_fill_color(*hex2RGB('#E9EAEE'))
            pdf.rect(px2MM(160),px2MM(new_y-14), px2MM(1239),px2MM(1),'F')
        else:
            su_val_color = '#000000'
            pdf.set_font('LeagueSpartan-medium', size=px2pts(20))
            
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(820),px2MM(new_y))  
        if tdet[i]['max_deduction'] == "-" :  
            pdf.multi_cell(px2MM(154),px2MM(32),'-',border='0',align='R')
        elif tdet[i]['max_deduction'] == "":  
            pdf.multi_cell(px2MM(154),px2MM(32),'',border='0',align='R')
        elif tdet[i]['max_deduction'].isdigit() or (tdet[i]['max_deduction'].count('.') == 1 and tdet[i]['max_deduction'].replace('.', '').isdigit()):
            md = str(locale.currency(float(tdet[i]['max_deduction']), grouping=True))
            # md = str(format_currency(float(tdet[i]['max_deduction']), 'INR', locale='en_IN', format=u'₹ #,##0'))
            md = md.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
            pdf.multi_cell(px2MM(154),px2MM(32),md,border='0',align='R')
        else:
            pdf.multi_cell(px2MM(154),px2MM(32),tdet[i]['max_deduction'],border='0',align='R')
            
            
        pdf.set_xy(px2MM(993),px2MM(new_y))  
        if tdet[i]['current_utilisation'] == "":
            cu = str(locale.currency(float(tdet[i]['current_utilisation']), grouping=True))
            cu = cu.split('.')[0]
            pdf.multi_cell(px2MM(181),px2MM(32),cu,border='0',align='R')
        elif tdet[i]['current_utilisation'].isdigit() or (tdet[i]['current_utilisation'].count('.') == 1 and tdet[i]['current_utilisation'].replace('.', '').isdigit()):
            cu = str(locale.currency(float(tdet[i]['current_utilisation']), grouping=True))
            # cu = str(format_currency(float(tdet[i]['current_utilisation']), 'INR', locale='en_IN', format=u'₹ #,##0'))
            cu = cu.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
            pdf.multi_cell(px2MM(181),px2MM(32),cu,border='0',align='R')
        else:
            pdf.multi_cell(px2MM(181),px2MM(32),tdet[i]['current_utilisation'],border='0',align='R')
            
            
        pdf.set_text_color(*hex2RGB(su_val_color))
        pdf.set_xy(px2MM(1190),px2MM(new_y))      
        if tdet[i]['suggested_utilisation'] == "" or tdet[i]['suggested_utilisation'] == "-":
            pdf.multi_cell(px2MM(210),px2MM(32),'-',border='0',align='R')
        elif tdet[i]['suggested_utilisation'].isdigit() or (tdet[i]['suggested_utilisation'].count('.') == 1 and tdet[i]['suggested_utilisation'].replace('.', '').isdigit()):
            su = str(locale.currency(float(tdet[i]['suggested_utilisation']), grouping=True))
            # su = str(format_currency(float(tdet[i]['suggested_utilisation']), 'INR', locale='en_IN', format=u'₹ #,##0'))
            su = su.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
            pdf.multi_cell(px2MM(210),px2MM(32),su,border='0',align='R')
        else:
            pdf.multi_cell(px2MM(210),px2MM(32),tdet[i]['suggested_utilisation'],border='0',align='R')
            
            
        su_sub_y  =  mm2PX(pdf.get_y())+8
        
        if tdet[i]['suggested_utilisation_additional_val'] != "":
            pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
            pdf.set_text_color(*hex2RGB('#649DE5'))
            pdf.set_xy(px2MM(1190),px2MM(su_sub_y))  
            if tdet[i]['suggested_utilisation_additional_val'].isdigit() or (tdet[i]['suggested_utilisation_additional_val'].count('.') == 1 and tdet[i]['suggested_utilisation_additional_val'].replace('.', '').isdigit()):
                su_ad_val = str(locale.currency(float(tdet[i]['suggested_utilisation_additional_val']), grouping=True))
                # su_ad_val = str(format_currency(float(tdet[i]['suggested_utilisation_additional_val']), 'INR', locale='en_IN', format=u'₹ #,##0'))
                su_ad_val = su_ad_val.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                pdf.multi_cell(px2MM(210),px2MM(25),'Additional '+su_ad_val+'*',align='R')
            else:
                pdf.multi_cell(px2MM(210),px2MM(25),tdet[i]['suggested_utilisation_additional_val'],align='R')
                
            
        new_y  =  next_new_y
    
    
    
    pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.set_xy(px2MM(393),px2MM(860))  
    pdf.cell(px2MM(100),px2MM(25),'You can save',align='L')  
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#229479'))
    x_axis = 493
    x = 0  
    pdf.set_xy(px2MM(500),px2MM(857))  
    potential_tax_saving = json_data['tax_planning']['tax_liability_potential_saving']['potential_tax_saving'] 
    if int(potential_tax_saving.count('.') == 1 and potential_tax_saving.replace('.', '').isdigit()) or int(potential_tax_saving):  
        potential_tax_saving_fm = str(locale.currency(float(potential_tax_saving), grouping=True))
        if float(potential_tax_saving) < 0:
            potential_tax_saving_fm = potential_tax_saving_fm.split('.')[0].replace('₹ ', '₹-').replace('₹-', '₹ -')
        else:
            potential_tax_saving_fm = potential_tax_saving_fm.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
        x = mm2PX(pdf.get_string_width(potential_tax_saving_fm))+10
        pdf.cell(px2MM(x),px2MM(32),potential_tax_saving_fm,align='L')
    x_axis = 497+ x
    pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
    pdf.set_text_color(*hex2RGB('#898B90'))
    pdf.set_xy(px2MM(x_axis),px2MM(860))  
    pdf.cell(px2MM(395),px2MM(25),'in taxes with an additional investment/insurance of',align='L')  
    x_axis = x_axis+400
    
    
    pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(24))
    pdf.set_text_color(*hex2RGB('#229479'))
    pdf.set_xy(px2MM(x_axis),px2MM(857))  
    additional_investment = json_data['tax_planning']['tax_liability_potential_saving']['additional_investment'] 
    if additional_investment.isdigit() or (additional_investment.count('.') == 1 and additional_investment.replace('.', '').isdigit()):  
        additional_investment = str(locale.currency(float(additional_investment), grouping=True))
        additional_investment = additional_investment.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
        x = mm2PX(pdf.get_string_width(additional_investment))+10
        pdf.cell(px2MM(x),px2MM(32),additional_investment,align='L')
    
      
    act_of_this_year = json_data['tax_planning']['action_of_this_year']
    
    if act_of_this_year ==[]:
        return None
    
    def act_page_create(pdf):
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(120),px2MM(80))  
        pdf.cell(px2MM(800),px2MM(84),"Recommended Tax Planning",align='L')

        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#000000') 
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(120),px2MM(204))  
        pdf.cell(px2MM(800),px2MM(42),"Actions for this year",align='L')
        
        
    act_page_create(pdf)
    
    y = 266
    for i in range(len(act_of_this_year)):
        pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
        comment = act_of_this_year[i].rstrip('\n')
        if 1080-y < (60+(42*(multicell_height(pdf,comment,1650)))):
            y = act_page_create(pdf)
            y = 266
        
        # if 1080-y < 140:
        #     act_page_create(pdf)
        #     y = 266
        
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(120),px2MM(y+18), px2MM(10),px2MM(10),'F')
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        comment = act_of_this_year[i].rstrip('\n')
        pdf.set_xy(px2MM(150),px2MM(y))  
        pdf.multi_cell(px2MM(1660),px2MM(42),comment,align='L')
        
        y = mm2PX(pdf.get_y())+16
        

#//*----Tax Liability & Potential Savings (New Regime)----*//
def new_regime(pdf,json_data,regime_type):
    
    # action of this year page create if more comments  and no table
    def act_page_create(pdf):
        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(120),px2MM(80))  
        pdf.cell(px2MM(800),px2MM(84),"Recommended Tax Planning",align='L')

        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#000000') 
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(120),px2MM(204))  
        pdf.cell(px2MM(800),px2MM(42),"Actions for this year",align='L')
        
        return 266
    
    
    tdet = json_data['tax_planning']['tax_deduction_exemption_table']
    if tdet !=[]:
        locale.setlocale(locale.LC_MONETARY, 'en_IN')

        pdf.add_page()
        pdf.set_fill_color(*hex2RGB('#FCF8ED'))
        pdf.rect(0,0, px2MM(1920),px2MM(1080),'F')
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(60))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(120),px2MM(80))  
        pdf.cell(px2MM(780),px2MM(84),"Recommended Tax Planning",align='L')

        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(0,px2MM(80), px2MM(15),px2MM(84),'F')
        
        #//*-----Index Text of Page--**////
        index_text(pdf,'#000000') 
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(1686),px2MM(114)) 
        regime_type_list = regime_type.split(" ")
        if regime_type_list[0].lower() == "new":
            pdf.cell(px2MM(120),px2MM(32),"New Regime",align='L')
            
        pdf.set_fill_color(*hex2RGB('#FFFFFF'))
        pdf.rect(px2MM(120),px2MM(204), px2MM(1683),px2MM(244),'F')
                
        pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(160),px2MM(244))  
        pdf.cell(px2MM(450),px2MM(32),"Deductions & Exemptions",align='L')
        
        pdf.set_xy(px2MM(690),px2MM(244))  
        pdf.cell(px2MM(306),px2MM(32),"Max. Deduction",align='R')
        
        pdf.set_xy(px2MM(1075),px2MM(244))  
        pdf.cell(px2MM(306),px2MM(32),"Current Utilisation",align='R')
        
        pdf.set_xy(px2MM(1458),px2MM(244))  
        pdf.cell(px2MM(306),px2MM(32),"Suggested Utilisation",align='R')
        
        pdf.set_fill_color(*hex2RGB('#E9EAEE'))
        pdf.rect(px2MM(160),px2MM(296), px2MM(1603),px2MM(0.5),'F')
        pdf.rect(px2MM(650),px2MM(234), px2MM(0.5),px2MM(184),'F')
        pdf.rect(px2MM(1034.3),px2MM(234), px2MM(0.5),px2MM(184),'F')
        pdf.rect(px2MM(1418.6),px2MM(234), px2MM(0.5),px2MM(184),'F')
        
        # Table Values
        
        pdf.set_font('LeagueSpartan-medium', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(160),px2MM(326))  
        pdf.multi_cell(px2MM(470),px2MM(42),tdet[0]['tax_class'],border='0',align='L')
        
        tc_sub_y  =  mm2PX(pdf.get_y())+8
        pdf.set_font('LeagueSpartan-regular', size=px2pts(24))
        pdf.set_text_color(*hex2RGB('#898B90'))
        pdf.set_xy(px2MM(160),px2MM(tc_sub_y))  
        pdf.cell(px2MM(455),px2MM(32),tdet[0]['tax_class_sub_val'],align='L')
        

        pdf.set_font('LeagueSpartan-medium', size=px2pts(30))
            
        pdf.set_text_color(*hex2RGB('#000000'))
        pdf.set_xy(px2MM(690),px2MM(326))
        if tdet[0]['max_deduction'] == "-":
            pdf.multi_cell(px2MM(306),px2MM(42),'-',border='0',align='R')
        elif tdet[0]['max_deduction'].isdigit() or (tdet[0]['max_deduction'].count('.') == 1 and tdet[0]['max_deduction'].replace('.', '').isdigit()):
            md = str(locale.currency(float(tdet[0]['max_deduction']), grouping=True))
            # md = str(format_currency(float(tdet[0]['max_deduction']), 'INR', locale='en_IN', format=u'₹ #,##0'))
            md = md.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
            pdf.multi_cell(px2MM(306),px2MM(42),md,border='0',align='R')
        else:
            pdf.multi_cell(px2MM(306),px2MM(42),tdet[0]['max_deduction'],border='0',align='R')
            
        pdf.set_xy(px2MM(1074),px2MM(326))  
        if tdet[0]['current_utilisation'] == "":
            pdf.multi_cell(px2MM(305),px2MM(42),"",border='0',align='R')
        elif tdet[0]['current_utilisation'].isdigit() or (tdet[0]['current_utilisation'].count('.') == 1 and tdet[0]['current_utilisation'].replace('.', '').isdigit()):
            cu = str(locale.currency(float(tdet[0]['current_utilisation']), grouping=True))
            # cu = str(format_currency(float(tdet[0]['current_utilisation']), 'INR', locale='en_IN', format=u'₹ #,##0'))
            cu = cu.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
            pdf.multi_cell(px2MM(305),px2MM(42),cu,border='0',align='R')
        else:
            pdf.multi_cell(px2MM(305),px2MM(42),tdet[0]['current_utilisation'],border='0',align='R')
            
        
        
        pdf.set_xy(px2MM(1458.5),px2MM(326))    
        if tdet[0]['suggested_utilisation'] == "-":
            pdf.multi_cell(px2MM(305),px2MM(42),'-',border='0',align='R')
        elif tdet[0]['suggested_utilisation'].isdigit() or (tdet[0]['suggested_utilisation'].count('.') == 1 and tdet[0]['suggested_utilisation'].replace('.', '').isdigit()):
            su = str(locale.currency(float(tdet[0]['suggested_utilisation']), grouping=True))
            # su = str(format_currency(float(tdet[0]['suggested_utilisation']), 'INR', locale='en_IN', format=u'₹ #,##0'))
            su = su.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')  
            pdf.multi_cell(px2MM(305),px2MM(42),su,border='0',align='R')
        else:
            pdf.multi_cell(px2MM(305),px2MM(42),tdet[0]['suggested_utilisation'],border='0',align='R')
        
            
        su_sub_y  =  mm2PX(pdf.get_y())+8
        
        if tdet[0]['suggested_utilisation_additional_val'] != "":
            pdf.set_font('LeagueSpartan-regular', size=px2pts(18))
            pdf.set_text_color(*hex2RGB('#649DE5'))
            pdf.set_xy(px2MM(1458),px2MM(su_sub_y))  
            if tdet[0]['suggested_utilisation_additional_val'].isdigit() or (tdet[0]['suggested_utilisation_additional_val'].count('.') == 1 and tdet[0]['suggested_utilisation_additional_val'].replace('.', '').isdigit()):
                su_ad_val = str(locale.currency(float(tdet[0]['suggested_utilisation_additional_val']), grouping=True))
                # su_ad_val = str(format_currency(float(tdet[0]['suggested_utilisation_additional_val']), 'INR', locale='en_IN', format=u'₹ #,##0'))
                su_ad_val = su_ad_val.split('.')[0].replace('₹ ','₹').replace('₹','₹ ')
                pdf.multi_cell(px2MM(305),px2MM(25),'Additional '+su_ad_val+'*',align='R')
            else:
                pdf.multi_cell(px2MM(305),px2MM(25),tdet[0]['suggested_utilisation_additional_val'],align='R')
                
        act_of_this_year = json_data['tax_planning']['action_of_this_year']
        
        if act_of_this_year ==[]:
            return None    
        
        pdf.set_font('LeagueSpartan-SemiBold', size=px2pts(32))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(120),px2MM(488))  
        pdf.cell(px2MM(800),px2MM(42),"Actions for this year",align='L')
        
        y = 550
    else:
        act_of_this_year = json_data['tax_planning']['action_of_this_year']
        
        if act_of_this_year == []:
            return None 
        y = act_page_create(pdf)
            

    # Comments Printing
    for i in range(len(act_of_this_year)):
        pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
        comment = act_of_this_year[i].rstrip('\n')
        if 1080-y < (60+(42*(multicell_height(pdf,comment,1650)))):
            y = act_page_create(pdf)
            y = 266
        
        pdf.set_fill_color(*hex2RGB('#000000'))
        pdf.rect(px2MM(120),px2MM(y+18), px2MM(10),px2MM(10),'F')
        
        pdf.set_font('LeagueSpartan-regular', size=px2pts(30))
        pdf.set_text_color(*hex2RGB('#1A1A1D'))
        pdf.set_xy(px2MM(150),px2MM(y))  
        pdf.multi_cell(px2MM(1660),px2MM(42),comment,align='L')
        
        y = mm2PX(pdf.get_y())+16
    
#//*----Calling of main functiong by taking sys.argv----*//
excel_file,save_path = sys.argv[1],sys.argv[2]
api_call(excel_file,save_path)
