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

    def test_get_list(self):
        for type in self.buy_type:
            for pref in self.pref_cd:
                print( self.base_url.format(type,pref,'l') )
                self.driver.get( self.base_url.format(type,pref,'l') )
#                with open("./csvfiles/type-{}_pref-{}.csv".format(type,pref), newline='') as csvfile:
#                reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
#                time.sleep(3)
#
                #with open("./csvfiles/type-{}_pref-{}.csv".format(type,pref), newline='') as csvfile:
                with open("./csvfiles/type-{}_pref-{}.csv".format(type,pref), 'r') as csvfile: # open city list
                    reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
                    header = next(reader)
                    cnt=1
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
                            time.sleep(3)
                            # open page: thing list
                            self.change_list_num(self.select_list_title, self.select_num)
                            self.get_thing_link(type,pref) # correct thing
                            # reset
                            self.driver.get( self.base_url.format(type,pref,'l') )
                        cnt = cnt +1

    def get_thing_link(self, type, pref):
        try:
            with open("./csvfiles/detail-{}_pref-{}.csv".format(type,pref), 'w') as csvfile:
                writer = csv.writer(csvfile, lineterminator='\n')
                while True:
                    elem = WebDriverWait(self.driver, 15).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.bottom-button.width-s > a'))) # wait for clickable search_btn
                    soup = BeautifulSoup(self.driver.page_source, "lxml")
                    for tag in soup.find_all(re.compile("h5")):
                        print('{},{}'.format(tag.a.text,tag.a.get("href")))
                        writer.writerow('{},{}'.format(tag.a.text,tag.a.get("href")))
                    self.go_next_page()
                    time.sleep(1)
        except OSError as err:
            driver.save_screenshot('screenshots/paginate_err.png')
            print("OS error: {0}".format(err))
            csvfile.close()
            pass

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

