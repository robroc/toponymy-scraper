#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import unicodecsv

browser = webdriver.Chrome()
f = open('toponymy_data.csv', 'wb+')
writer = unicodecsv.writer(f)
writer.writerow(["feature_name", "entry_date", "feature_type", "history", "changed_name", "old_name"])

def main():

    browser.get('http://www.toponymie.gouv.qc.ca/ct/ToposWeb/recherche.aspx?avancer=oui')
    time.sleep(3)
    browser.find_element_by_xpath("//*[@id='ctl00_ConteneurToposWeb_lstRegAdm']/option[@value='06']").click()
    time.sleep(1)
    browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_btnSoumettreAvancer"]').click()
    time.sleep(12)
    table = browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_quadResultats"]/tbody')
    scrape_rows(table)

    for i in range (1,2):
        print "Scraping page %s" % i
        browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_paginHaut"]/a[' + str(i) + ']').click()
        table = browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_quadResultats"]/tbody')
        scrape_rows(table)
        time.sleep(6)
           
    #for i in range (2, 7):
    #    print "Scraping page %s" % i+11
    #    scrape_rows()
    #    browser.find_element_by_xpath('//*[@id="ctl00_ConteneurToposWeb_paginHaut"]/a[' + str(i) + ']').click()
    #    time.sleep(6)   
    
    f.close()
    browser.close()
    

def scrape_rows(table):
    trs = table.find_elements_by_tag_name('tr')
    for tr in trs[1:]:
        link = tr.get_attribute('onclick')
        if link is not None:
            id_start = link.find("=")+1
            id_end = link.find("');")
            page_id = str(link[id_start:id_end])
            get_details(page_id)


def get_details(page_id):
    changed_name = False
    old_name = "None"
    r = requests.get("http://www.toponymie.gouv.qc.ca/ct/ToposWeb/fiche.aspx?no_seq=" + page_id)
    soup = BeautifulSoup(r.text)
    entry_date = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq17'}).text
    feature_name = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq19'}).text    
    feature_type = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq23'}).text
    history = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueFiche_etq9'}).text
    old_name_div = soup.find('div', attrs={'id':'ctl00_ConteneurToposWeb_pTitreVariantes'})  
    if old_name_div is not None:
        changed_name = True
        old_name = soup.find('span', attrs={'id':'ctl00_ConteneurToposWeb_vueVariantes_ctl01_lbltopvar'}).text
    print "Getting info for feature {0} {1}".format(feature_type, feature_name)
    writer.writerow([feature_name, entry_date, feature_type, history, changed_name, old_name])
    
if __name__ == '__main__':
    main()