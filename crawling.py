import csv,os,re,sys,time,unittest,urllib
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options

class Crawling(unittest.TestCase):
    
    root_url = 'http://www.fudousan.or.jp/system/{}'
    base_url = "http://www.fudousan.or.jp/system/?act=f&type={}&pref={}&stype={}"
    pref_cd = {'13':'東京','11':'埼玉','12':'千葉','14':'神奈川','27':'大阪'}
    buy_type = {'31':"マンション","32":"一戸建て、その他","33":"事業用物件"}
    next_css_select = "#cont > table:nth-child(12) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td:nth-child(1) > p > select"
    title_link_selector = 'table.result_all_part > tbody > tr > th > h5 > a'
    select_list_title = '#cont > table:nth-child(12) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(2) > td:nth-child(1) > p > span'
    select_list = 'select[name="select"]'
    select_num = '100'
    search_result_title = '#cont > table:nth-child(12) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > th > p > span'
    nx = '#cont > table:nth-child(12) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > td > p > a:nth-child({})'
    fieldnames = ['title','address','map_url','bno','bno_sub','price','access','subcommission','sikikin','release_notice','hoshokin','built_type','madori','madori_detail','floor_area','built_ym','structure','floors','direction','balcony_area','parking','facility','summary','status','entry','contract_period','fixed_term_lease_contract','insurance','recontract_fee','Amortization','etc_fee','zatsu','memo1','memo2','caution_memo','transaction_form','registed_date','next_update_date','detail_url','estate_url','qr_code','information_provider','information_provider_url','information_provider_id','information_provider_detail']

    def setUp(self):
        self.driver = webdriver.Chrome()
        #self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"))
        #self.driver.set_window_size(1024, 768)
        self.driver.set_window_size(1024, 900)
        self.driver.implicitly_wait(10)

    def test_get_city(self):
        for type in self.buy_type:
            for pref in self.pref_cd:
                print( self.base_url.format(type,pref,'l') )
                self.driver.get( self.base_url.format(type,pref,'l') )
                with open("./csvfiles/type-{}_pref-{}.csv".format(type,pref), 'w', newline='') as csvfile:
                    soup = BeautifulSoup(self.driver.page_source, "lxml")
                    css_soup = soup.select('table.area li')
                    handle = csv.DictWriter(csvfile, ['id','title','count'])
                    handle.writeheader()
                    for li in css_soup:
                        row = {}
                        m=None
                        row['id'] = li.input['id']
                        if li.a == None:
                            row['title'] = li.span.string.split('(')[0]
                            m = re.search(r'[0-9]+', li.span.string.split('(')[1])
                            row['count'] = m.group(0)
                        else:
                            row['title'] = li.a.string.split('(')[0]
                            m = re.search(r'[0-9]+', li.a.string.split('(')[1])
                            row['count'] = m.group(0)
#                        print(row)
                        handle.writerow(row)
        self.driver.close()

    def test_abc(self):
        for type in self.buy_type:
            for pref in self.pref_cd:
                print( self.base_url.format(type,pref,'l') )
                self.driver.get( self.base_url.format(type,pref,'l') )
                time.sleep(1)
                self.scroll_to_target_element('h4.title_area')
                time.sleep(13)

    def test_get_list(self):
        for type in self.buy_type:
            for pref in self.pref_cd:
                print( self.base_url.format(type,pref,'l') )
                self.driver.get( self.base_url.format(type,pref,'l') )

                with open("./csvfiles/type-{}_pref-{}.csv".format(type,pref), 'r') as csvfile: # open city list
                    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                    header = next(reader)
                    cnt=1
                    try:
                        for row in reader: # read csv
                            print(cnt)
                            list=row[0].split(',')
                            print(list[0])
                            if ( int(list[2]) > 0):
                                self.driver.find_element_by_id(list[0]).click() # click city
                            if (cnt > 1 and (cnt % 5) == 0):
                                element0 = WebDriverWait(self.driver, 15).until(
                                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.bottom-button.width-s > a'))) # click search_btn
                                element0.click()
                                time.sleep(1)
                                # open page: thing list
                                self.change_list_num(self.select_list_title, self.select_num)
                                try:
                                    self.get_thing_link(type,pref) # correct thing
                                except:
                                    # reset
                                    self.driver.get( self.base_url.format(type,pref,'l') )
                                    self.scroll_to_target_element('h4.title_area')
                            cnt = cnt +1
                    except csv.Error as e:
                        print( self.base_url.format(type,pref,'l') )
                        print(e)
                        pass
                    except OSError as err:
                        print("OS error: {0}".format(err))                        

    def test_get_detail(self):
        import re
        for type in self.buy_type:
            for pref in self.pref_cd:
                with open("./csvfiles/detail-{}_pref-{}.csv".format(type,pref), 'r') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                    next(reader)
                    with open("./csvfiles/detail_data-{}_pref-{}.csv".format(type,pref), 'a') as f:
                        writer = csv.DictWriter(f, fieldnames=self.fieldnames, delimiter=",", quotechar='"')
                        writer.writeheader()
                        for row in reader:
                            #print(row[1])
                            detail = {}
                            detail = self.collect_detail(row)
                            print(detail)
                            writer.writerow(detail)
                            time.sleep(3)

    def collect_detail(self, row):
        detail = {}
        head_title=''
        self.driver.get( self.root_url.format(row[1]) )
        try:
            elem = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a.function-button'))) # wait for clickable link
        except:
            return detail['closed'] = row[0]
        soup = BeautifulSoup(self.driver.page_source, "lxml")
        elem = self.driver.find_element_by_css_selector( "div.content-title-text")
        detail['title'] = elem.text.split('／')[0]
        detail['address'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(2) > td > p > span").text
        detail['map_url'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(2) > td > p > a").get_attribute("href")
        detail['bno'] = self.driver.find_element_by_css_selector("td.midashi.bid-text p").text.split('／')[0].split(':')[1]
        detail['bno_sub'] = self.driver.find_element_by_css_selector("td.midashi.bid-text p").text.split('／')[1].split(':')[1]
        detail['price'] = self.driver.find_element_by_css_selector("span.syousai_price").text.split(' ')[2]
        detail['access'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(3) > td > p").text
        detail['subcommission'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(4) > td:nth-child(2) > p").text
        detail['sikikin'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(4) > td:nth-child(4) > p").text
        detail['release_notice'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(5) > td:nth-child(2) > p").text
        detail['hoshokin'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(5) > td:nth-child(4) > p").text
        detail['built_type'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(6) > td:nth-child(2) > p").text
        detail['madori'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(7) > td:nth-child(2) > p").text
        detail['madori_detail'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(8) > td:nth-child(2) > p").text
        detail['floor_area'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(9) > td:nth-child(2) > p").text
        detail['built_ym'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(9) > td:nth-child(4) > p").text
        detail['structure'] = self.driver.find_element_by_css_selector("#info-table-1 > tbody > tr:nth-child(9) > td:nth-child(2) > p").text
        detail['floors'] = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(2) > td:nth-child(2) > p").text
        detail['direction'] = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(2) > td:nth-child(2) > p").text
        detail['balcony_area'] = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(2) > td:nth-child(2) > p").text
        detail['parking']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(2) > td:nth-child(2) > p").text
        detail['facility']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(4) > td > p").text
        detail['summary']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(5) > td > p").text
        detail['status']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(6) > td > p").text
        detail['entry']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(6) > td:nth-child(4) > p").text
        detail['contract_period']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(7) > td > p").text
        detail['fixed_term_lease_contract']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(7) > td:nth-child(4) > p").text
        detail['insurance']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(8) > td > p").text
        detail['recontract_fee']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(8) > td > p").text
        detail['Amortization']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(9) > td:nth-child(4) > p").text
        detail['etc_fee']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(10) > td:nth-child(2) > p").text
        detail['zatsu']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(11) > td:nth-child(2) > p").text
        detail['memo1']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(12) > td:nth-child(2) > p").text
        detail['memo2']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(13) > td:nth-child(2) > p").text
        detail['caution_memo']  = self.driver.find_element_by_css_selector("#info-table-2 > tbody > tr:nth-child(14) > td:nth-child(2) > p").text
        detail['transaction_form']  = self.driver.find_element_by_css_selector("#info-table-5 > tbody > tr:nth-child(1) > td.qrctd > p").text
        detail['registed_date']  = self.driver.find_element_by_css_selector("#info-table-5 > tbody > tr:nth-child(2) > td > p").text
        detail['next_update_date']  = self.driver.find_element_by_css_selector("#info-table-5 > tbody > tr:nth-child(3) > td > p").text
        detail['detail_url']  = self.driver.find_element_by_css_selector("#info-table-5 > tbody > tr:nth-child(3) > td > p").text
        detail['estate_url']  = self.driver.find_element_by_css_selector("#info-table-5 > tbody > tr:nth-child(4) > td > p").text
        detail['qr_code']  = self.driver.find_element_by_css_selector("#propertyQrcode > img").get_attribute("src")
        detail['information_provider']  = self.driver.find_element_by_css_selector("#companyinfo > div > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > b > a").text
        detail['information_provider_url']  = self.driver.find_element_by_css_selector("#companyinfo > div > div > table > tbody > tr:nth-child(1) > td:nth-child(2) > b > a").get_attribute("href")
        detail['information_provider_id']  = self.driver.find_element_by_css_selector("#companyinfo > div > div > table > tbody > tr:nth-child(1) > td:nth-child(3)").text
        detail['information_provider_detail']  = self.driver.find_element_by_css_selector("#companyinfo > div > div > table > tbody > tr:nth-child(2) > td:nth-child(1)").text
        return detail

    def get_thing_link(self, type, pref):
        with open("./csvfiles/detail-{}_pref-{}.csv".format(type,pref), 'a') as csvfile:
            #writer = csv.writer(csvfile, lineterminator='\n')
            handle = csv.DictWriter(csvfile, ['title','url'])
            handle.writeheader()
            while True:
                elem = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.bottom-button.width-s > a'))) # wait for clickable search_btn
                soup = BeautifulSoup(self.driver.page_source, "lxml")
                for tag in soup.find_all(re.compile("h5")):
                    row = {}
                    row['title'] = tag.a.text
                    row['url']   = tag.a.get('href')
                    print('{},{}'.format(tag.a.text,tag.a.get("href")))
                    handle.writerow(row)
                self.go_next_page()
                time.sleep(1)

    def change_list_num(self, css_selector, num):
        self.scroll_to_target_element(css_selector)
        css_selector = 'select[name="select"]'
        Select(self.driver.find_element_by_css_selector(css_selector)).select_by_value(self.select_num)

    def scroll_to_target_element(self, css_selector):
        print(css_selector)
        element = self.driver.find_element_by_css_selector(css_selector)
        print(element.location_once_scrolled_into_view)
        self.driver.execute_script("window.scrollTo(0, {})".format(element.location_once_scrolled_into_view['y']))
#        self.driver.execute_script("window.scrollTo(0, {})".format(600))

#    def scrollByY(self, height):
#        self.driver.execute_script("window.scrollTo(0, " + str(height) + ");")

    def go_next_page(self):
        self.scroll_to_target_element('h4.title_home_all')
        pg = self.get_curr_pg_num()
        print('page:{}'.format(pg))
        self.driver.find_element_by_link_text('次へ＞').click()

    def chk_curr_pg(self):
        curr_pg = self.get_curr_pg_num() if self.get_curr_pg_num() != None else 0
        print('curr_pg:{}'.format(curr_pg))

    def get_curr_pg_num(self):
        curr = self.driver.current_url
        for p in curr.split('&'):
            m = re.search(r'^p=[0-9]+$', p)
            if m == None:
                pass
            else:
                return int(re.search(r'[0-9]+', m.group(0)).group(0))
        return 1

    def test_main(self):
        self.driver.get("https://www.google.co.jp")

        self.driver.close()

if __name__ == '__main__':
    unittest.main()

