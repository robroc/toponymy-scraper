#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from bs4 import BeautifulSoup
import unicodecsv

# Initialize Selenium webdriver and CSV writer as globals
browser = webdriver.Chrome()
f = open('toponymy_data_new.csv', 'ab+')
writer = unicodecsv.writer(f)
writer.writerow(["id","feature_name", "entry_date", "feature_type", "city", "borough", "history", "changed_name", "old_name","coords"])

def main():
    browser.get('http://www.toponymie.gouv.qc.ca/ct/ToposWeb/recherche.aspx?avancer=oui')
    time.sleep(3)
    
    # Select Montreal only
    browser.find_element_by_xpath("//*[@id='ctl00_ConteneurToposWeb_lstRegAdm']/option[@value='06']").click()
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_btnSoumettreAvancer"]').click()
    time.sleep(10)
    
    # Start scraping the first page of results
    table = browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_quadResultats"]/tbody')
    print ""
    print "SCRAPING PAGE 1"
    print ""
    scrape_rows(table)
     
    # Scrape following pages. When get to page 11, pagination index resets to 2  
    for i in range (1,11):
        paginate(i)
       
    for i in range (2, 7):
        paginate(i)
   
    f.close()
    browser.close() 
     
def paginate(page):
    print ""
    print "SCRAPING PAGE %s" % str(page+1)
    print ""
    page_link =  WebDriverWait(browser, 12).until(EC.presence_of_element_located((By.ID,'ctl00_ConteneurToposWeb_paginHaut')))
    browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_paginHaut"]/a[' + str(page) + ']').click()
    time.sleep(10)
    table = WebDriverWait(browser, 12).until(EC.presence_of_element_located((By.ID, 'ctl00_ConteneurToposWeb_quadResultats')))           
    table = browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_quadResultats"]/tbody')
    scrape_rows(table)

def scrape_rows(table):
    row = 0
    try:
        trs = table.find_elements_by_tag_name('tr')
    except StaleElementReferenceException:
        time.sleep(10)
        trs = table.find_elements_by_tag_name('tr')  
    for tr in trs[1:]:
        if tr.text != '':
            if tr.text[0].isdigit():
                continue
            link = tr.get_attribute('onclick')
            if link is not None:
                id_start = link.find("=")+1
                id_end = link.find("');")
                page_id = str(link[id_start:id_end])
                row = row + 1  
                get_details(page_id, row)
        time.sleep(3)      

def get_details(page_id, row):
    changed_name = False
    old_name = "None"
    coords = ""
    headers = {'user-agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5); Roberto Rocha/robroc1@gmail.com'}
    r = requests.get("http://www.toponymie.gouv.qc.ca/ct/ToposWeb/fiche.aspx?no_seq=" + page_id, headers=headers)
    if r.status_code == 200:
        soup = BeautifulSoup(r.text)
        entry_date = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq17'}).text
        feature_name = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq19'}).text    
        feature_type = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq23'}).text
        city = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etqMunicipalite'}).text.replace(' (Ville)','')
        borough = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etqFusion'}).text.replace('(','').replace(')','')
        history = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq9'}).text
        old_name_div = soup.find('div', attrs={'id':'ctl00_ConteneurToposWeb_pTitreVariantes'})
        coords_span = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_Label3'})
        if old_name_div is not None:
            changed_name = True
            old_name = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueVariantes_ctl01_lbltopvar'}).text
        if coords_span is not None:
            coords = coords_span.text
        print "{0}. Fetching: {1} {2}".format(row, feature_type, feature_name)
        writer.writerow([page_id,feature_name, entry_date, feature_type, city, borough, history, changed_name, old_name, coords])
    else:
        print "Detail page not found"
    
if __name__ == '__main__':
    main()
