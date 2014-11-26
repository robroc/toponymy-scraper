import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import unicodecsv

f = open('toponymy_data.csv', 'wb+')
writer = unicodecsv.writer(f)
writer.writerow(["feature_name", "entry_date", "feature_type", "history"])

browser = webdriver.Firefox()
browser.get('http://www.toponymie.gouv.qc.ca/ct/ToposWeb/recherche.aspx?avancer=oui')
time.sleep(3)
browser.find_element_by_xpath("//*[@id='ctl00_ConteneurToposWeb_lstRegAdm']/option[@value='06']").click()
time.sleep(3)
browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_btnSoumettreAvancer"]').click()
time.sleep(15)

for i in range (1,11):
    browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_paginHaut"]/a[' + str(i) + ']').click()
    time.sleep(6)
    scrape_rows()
    
for i in range (2, 7):
    browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_paginHaut"]/a[' + str(i) + ']').click()
    time.sleep(6)
    scrape_rows() 

def scrape_rows():
    table = browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_quadResultats"]')
    trs = table.find_elements_by_tag_name('tr')
    for tr in trs[1:]:
        try:
            link = tr.get_attribute('onclick')
            page_id = link[len("javascript:OuvrirLien('fiche.aspx?no_seq="):-len("');")]
            get_details(page_id)
        except TypeError:
            continue
        
def get_details(page_id):
    details_page = webdriver.Firefox()
    details_page.get("http://www.toponymie.gouv.qc.ca/ct/ToposWeb/fiche.aspx?no_seq=" + page_id)
    entry_date = details_page.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_vueFiche_etq17"]').text
    feature_name = details_page.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_vueFiche_etq19"]').text
    feature_type = details_page.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_vueFiche_etq23"]').text
    history = details_page.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_vueFiche_etq9"]').text
    writer.writerow([feature_name, entry_date, feature_type, history])
    details_page.close()
