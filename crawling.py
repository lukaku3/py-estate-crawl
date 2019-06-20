import csv,os,re,sys,time,unittest
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

    def setUp(self):
        #self.driver = webdriver.Chrome()
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"))
#        self.driver.set_window_size(1024, 1024)
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
                with open("./csvfiles/type-{}_pref-{}.csv".format(type,pref), 'r') as csvfile:
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
#                            self.driver.find_element_by_css_selector('div.bottom-button.width-s > a').click() # click search_btn
                            element0 = WebDriverWait(self.driver, 15).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.bottom-button.width-s > a'))) # click search_btn
                            element0.click()
                            # open thing list
                            #element1 = WebDriverWait(self.driver, 10).until(
                            #    EC.element_to_be_clickable((By.CSS_SELECTOR, 'th[colspan="4"] > h5 > a'))) # click thing title
                            #element1.click()
                            #print(self.driver.title)
                            #self.driver.send_keys(Keys.PAGE_DOWN)
                            #self.driver.execute_script("window.scrollTo(0, 630)")
                            #self.scroll_to_target_element('#cont > table:nth-child(12) > tbody > tr:nth-child(2) > td > table > tbody > tr:nth-child(1) > th > p > span')
                            #self.select_100()
                            element1 = WebDriverWait(self.driver, 15).until(
                                EC.element_to_be_clickable((By.CSS_SELECTOR, 'div.bottom-button.width-s > a'))) # till clickable search_btn
                            soup = BeautifulSoup(self.driver.page_source, "lxml")
                            css_soup = soup.select('#cont > table > tbody > tr:nth-child(1) > th > h5 > a')
                            print(css_soup)
                            sys.exit() 
                            time.sleep(10)
                        if ( cnt == 6 ):
                            sys.exit() 
                        cnt = cnt +1

    def scroll_to_target_element(self, css_selector):
        print(css_selector)
        element = self.driver.find_element_by_css_selector(css_selector)
        print(element.location_once_scrolled_into_view['y'])
        #self.driver.execute_script("window.scrollTo(0, {})".format(element.location_once_scrolled_into_view['y']))
        self.driver.execute_script("window.scrollTo(0, 630)")
        #self.scrollByY(element.location_once_scrolled_into_view['y'])

    def scrollByY(self, height):
        self.driver.execute_script("window.scrollTo(0, " + str(height) + ");")

    def select_100(self):
        Select(self.driver.find_element_by_css_selector(self.next_css_select)).select_by_value('100')

    def test_main(self):
        self.driver.get("https://www.google.co.jp")


        self.driver.close()

if __name__ == '__main__':
    unittest.main()

