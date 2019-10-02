#!/usr/local/bin/python3
import cgi
form = cgi.FieldStorage()

if 'company_code' in form:
  company_code = form["company_code"].value
  # coding=utf-8
  # 기업 open_api 이용하기 (https://tariat.tistory.com/31?category=678887)
  
  # step 1
  # urllib, pandas, beautifulsoup, webbrowser를 import합니다.
  from urllib.request import urlopen
  import pandas as pd
  from bs4 import BeautifulSoup
  import webbrowser

  API_KEY="6b0d8da093bdc9a7f62fa77f33dd2838d196c040"

  # step 2
  # dart에서 발급받은 api_key와 기업 종목 코드를 활용하여 데이터를 호출합니다.
  # company_code = "005930" //삼성 코드
  url = "http://dart.fss.or.kr/api/search.xml?auth="+API_KEY+"&crp_cd="+company_code+"&start_dt=19000101&fin_rpt=Y&bsn_tp=A001&page_set=100"
  resultXML = urlopen(url)
  result=resultXML.read()
  # webbrowser.open(url)

  # step 3
  # BeautifulSoup을 이용하여, parsing하면 아래와 같이 회신받은 정보를 확인할 수 있습니다.
  xmlsoup = BeautifulSoup(result,'html.parser')
  # print(xmlsoup)

  # step 4
  # 정보가 list tag 단위로 저장되기 때문에, list단위로 정보를 나누어 저장한 뒤에 for문을 이용해서 한 줄씩 dataframe으로 저장하고, 합쳤습니다.
  data = pd.DataFrame()
  te = xmlsoup.findAll("list")

  for t in te:
    temp = pd.DataFrame(([[t.crp_cls.string,t.crp_nm.string,t.crp_cd.string,t.rpt_nm.string,t.rcp_no.string, t.flr_nm.string, t.rcp_dt.string, t.rmk.string]]),
      columns=["crp_cls","crp_nm","crp_cd","rpt_nm","rcp_no","flr_nm","rcp_dt","rmk"])
    data = pd.concat([data,temp])

  company_name = data[0:1].iloc[0,1]
  # print(data)

  # step 5
  # 현재 공시된 보고서의 list들을 위와 같이 볼 수 있습니다. 여기에 있는 정보를 조합해서 url을 만들면 보고서를 확인할 수 있습니다.
  data = data.reset_index(drop=True)
  url_quarterly_report="http://dart.fss.or.kr/dsaf001/main.do?rcpNo="+data['rcp_no'][0]
  # webbrowser.open(url_quarterly_report)

  # step 6
  # 위의 재무재표 url에서 우리는 dcmNo 를 찾아야 합니다.
  import re
  quarterly_report = urlopen(url_quarterly_report)
  qr_read = quarterly_report.read()
  xmlsoup_quarterly_report = BeautifulSoup(qr_read,'html.parser')
  dcm_no_tag = xmlsoup_quarterly_report.find("body").find("a", href="#download")
  dcm_no = re.search("\'\d{7}\'", str(dcm_no_tag)).group().lstrip('\'').rstrip('\'')
  # print(dcm_no_tag)

  # step 6
  # 위의 분기보고서에서 재무재표 부분만 가져오는 url을 만듭니다.
  url_financial_statement = "http://dart.fss.or.kr/report/viewer.do?rcpNo=" + data['rcp_no'][0] + "&dcmNo=" + dcm_no + "&eleId=13&offset=100000000&length=100000000&dtd=dart3.xsd"
  webbrowser.open(url_financial_statement, new=1)

  # step 7
  # 이제 해당 url에서 우리가 가져오고자 하는 재무제표가 어디에 있는지 확인해야 합니다. 참고로 html에서 표는 <table>이라는 태그로 되어 있기 때문에, 해당 tag를 위주로 확인합니다. 
  # financial_statement = pd.read_html(url_financial_statement)
  # income_statement = financial_statement[4]
  # income_statement.rename(columns = {'Unnamed: 0' : 'index'}, inplace = True)
  # revenue_row = income_statement[income_statement['index'].isin(['수익(매출액)'])].iloc[0:1, 0:2]
  # revenue = int(revenue_row.iloc[0, 1])
  # operating_income_row = income_statement[income_statement['index'].isin(['당기순이익(손실)'])].iloc[0:1, 0:2]
  # operating_income = int(operating_income_row.iloc[0, 1])
  # net_profit_margin = round(operating_income / revenue * 100, 2)
  # print(company_name + '(' + company_code + ')의 가장 최근 년도 당기순이익률은 ' + str(net_profit_margin) + '% 입니다.')


print("Location: fs-search.html")
print()
