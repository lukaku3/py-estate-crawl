import csv,os,re,unittest
from selenium import webdriver
from bs4 import BeautifulSoup

class Crawling(unittest.TestCase):
    
    base_url = "http://www.fudousan.or.jp/system/?act=f&type={}&pref={}&stype={}"
    pref_cd = {'13':'東京','11':'埼玉','12':'千葉','14':'神奈川','27':'大阪'}
    buy_type = {'31':"マンション","32":"一戸建て、その他","33":"事業用物件"}

    def setUp(self):
        #self.driver = webdriver.Chrome()
        self.driver = webdriver.Chrome(executable_path=os.path.abspath("chromedriver"))

    def test_get_city(self):

        for type in self.buy_type:
            for pref in self.pref_cd:
                print( self.base_url.format(type,pref,'l') )
                self.driver.get( self.base_url.format(type,pref,'l') )
                with open("./csvfiles/type-{}_pref-{}.csv".format(type,pref), 'w', newline='') as csvfile:
                    soup = BeautifulSoup(self.driver.page_source, "lxml")
                    css_soup = soup.select('table.area li')
#                    handle = csv.writer(csvfile, delimiter=',',
#                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
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


#                print(css_soup)
#        self.driver.close()

    def test_main(self):
        self.driver.get("https://www.google.co.jp")


        self.driver.close()

if __name__ == '__main__':
    unittest.main()

