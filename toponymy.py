import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import unicodecsv

def main():

    f = open('toponymy_data.csv', 'wb+')
    writer = unicodecsv.writer(f)
    writer.writerow(["feature_name", "entry_date", "feature_type", "history"])

    browser = webdriver.Chrome()
    browser.get('http://www.toponymie.gouv.qc.ca/ct/ToposWeb/recherche.aspx?avancer=oui')
    time.sleep(3)
    browser.find_element_by_xpath("//*[@id='ctl00_ConteneurToposWeb_lstRegAdm']/option[@value='06']").click()
    time.sleep(3)
    browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_btnSoumettreAvancer"]').click()
    time.sleep(30)
    scrape_rows(browser)

    for i in range (1,2):
        print "Scraping page %s" % i
        browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_paginHaut"]/a[' + str(i) + ']').click()
        time.sleep(6)
        scrape_rows(browser)
    
    #for i in range (2, 7):
    #    browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_paginHaut"]/a[' + str(i) + ']').click()
    #    time.sleep(6)
    #    scrape_rows() 
    
    f.close()

def scrape_rows(browser):
    table = browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_quadResultats"]')
    trs = table.find_elements_by_tag_name('tr')
    for tr in trs[1:]:
        try:
            link = tr.get_attribute('onclick')
            id_start = link.find("=")+1
            id_end = link.find("');")
            page_id = link[id_start:id_end]
            get_details(page_id)
        except TypeError:
            continue
        
def get_details(page_id):
    changed_name = False
    r = requests.get("http://www.toponymie.gouv.qc.ca/ct/ToposWeb/fiche.aspx?no_seq=" + page_id)
    soup = BeautifulSoup(r.text)
    entry_date = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq17'}).string
    feature_name = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq19'}).string    
    feature_type = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq20'}).string
    history = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq9'}).string
    old_name_div = soup.find('div', attrs={'id':'ctl00_ConteneurToposWeb_pTitreVariantes'})  
    if old_name_div is not None:
        changed_name = True
        old_name = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueVariantes_ctl01_lbltopvar'}).string       
    print "Getting info for feature %s %s" % feature_type, feature_name
    writer.writerow([feature_name, entry_date, feature_type, history, changed_name, old_name])
    
if __name__ == '__main__':
    main()