from django.conf.urls import patterns, include, url
from django.contrib import admin
from selenium import webdriver
from requests import session
from bs4 import BeautifulSoup
import re
import csv


urlpatterns = patterns('', url(r'^admin/', include(admin.site.urls)))

USERNAME = 'emailaccount@email.com'
PASSWORD = 'password1234'

##################################################################################################################
#######################################  FUNCTION DECLARATIONS AND DEFINITIONS  ##################################
##################################################################################################################

def setWebDriver():
    global wd
    wd = webdriver.Chrome('C:\Dev\Chromium\chromedriver.exe')
def setEachGlobalArray():
    fin = open("C:\Users\Public\Documents\neighborhood-report.csv", "rb")
    reader = csv.DictReader(fin)
    global city
    global firstName
    global lastName
    global street
    global phone
    global number
    city = []
    firstName = []
    lastName = []
    street = []
    phone = []
    number = 0
    for row in reader:
        city[number] = row[4]
        firstName[number] = row[11]
        lastName[number] = row[12]
        street[number] = row[13]
        phone[number] = "NoNumber"
        number += 1
    fin.close()

#######################################################################################################################
#######################################  START MAIN  ##################################################################
#######################################################################################################################

payload = {'action': 'login', 'username': USERNAME, 'password': PASSWORD}
with session() as c:#This session allows us to share cookies and parameters throughout
    setWebDriver()
    setEachGlobalArray()

    ###########################  LOGIN  #########################################################################

    wd.get('https://www.spokeo.com/login?url=http%3A%2F%2Fwww.spokeo.com%2F')
    wd.find_element_by_name("email_address").send_keys(USERNAME)
    wd.find_element_by_name("password").send_keys(PASSWORD)
    wd.find_element_by_xpath('//*[@id="login_button"]').click()
    wd.implicitly_wait(5000)

    ###############################  SEARCH THE FIRST NAME  #####################################################

    wd.find_element_by_xpath('//*[@id="hero_search_input"]').send_keys(firstName[0], ' ', lastName[0], ', ', city[0], ', CA')
    wd.find_element_by_xpath('//*[@id="hero_search_submit"]').click()

    ######################  STORE NUMBER IF STRAIGHT TO PROFILE ##################################################
    with open("C:\Users\Public\Documents\compiledList.csv", "wb") as fileOut:
        fileWriter = csv.writer(fileOut)
        fileWriter.writerows("First Name", "Last Name", "Street", "City", "Phone Number")

        isElementPresent = wd.find_elements_by_xpath('//*[@id="profile_bookmark_button"])').size()
        if isElementPresent is True:
            htmlCode = wd.page_source
            soup = BeautifulSoup(htmlCode)
            for tag in soup.find_all(text = re.compile("\\(\\d\{3\}\\)\\s\\d\{3\}-\\d\{4\}")):
                phone[0] = tag.text
            fileWriter.writerows(firstName[0], lastName[0], street[0], city[0], phone[0])
        #execute code if you've gone straight to profile page

    ##########################  OR MATCH ADDRESS IF MULTIPLE OPTIONS  ###########################################

        else:
            streetNum = street[0]
        #htmlCode = wd.page_source
        #soup = BeautifulSoup(htmlCode)
        #Maybe theres a way i can use the beuatiful soup trick here too

            profile1 = wd.find_element_by_xpath('//*[@id="2832"]/div[2]').getattr("maxLength = 30")
            profile2 = wd.find_element_by_xpath('//*[@id="2828"]/div[2]').getattr("maxLength = 30")
            profile3 = wd.find_element_by_xpath('//*[@id="2831"]/div[2]').getattr("maxLength = 30")
            profile4 = wd.find_element_by_xpath('//*[@id="2826"]/div[2]').getattr("maxLength = 30")
            profile5 = wd.find_element_by_xpath('//*[@id="2827"]/div[2]').getattr("maxLength = 30")
            if streetNum is profile1:
                wd.find_element_by_xpath('//*[@id="2832"]').click()
                wd.implicitly_wait(5000)
            if streetNum is profile2:
                wd.find_element_by_xpath('//*[@id="2828"]').click()
                wd.implicitly_wait(5000)
            if streetNum is profile3:
                wd.find_element_by_xpath('//*[@id="2831"]').click()
                wd.implicitly_wait(5000)
            if streetNum is profile4:
                wd.find_element_by_xpath('//*[@id="2826"]').click()
                wd.implicitly_wait(5000)
            if streetNum is profile5:
                wd.find_element_by_xpath('//*[@id="2827"]').click()
                wd.implicitly_wait(5000)

        ###########################  GET NUMBER FROM CORRECT PAGE  ##################################################

            htmlCode = wd.page_source
            soup = BeautifulSoup(htmlCode)
            for tag in soup.find_all(text = re.compile("\\(\\d\{3\}\\)\\s\\d\{3\}-\\d\{4\}")):
                phone[0] = tag.text
            fileWriter.writerows(firstName[0], lastName[0], street[0], city[0], phone[0])
####################################################################################################################
#########################################################  START LOOPING  ##########################################
####################################################################################################################

        for counter in (1,number+1):
            wd.find_element_by_xpath('//*[@id="header_logo"]/i[1]').click()#click the spokeo logo in the top left to get to the clean search bar screen
            wd.implicitly_wait(5000)#then wait some seconds so we dont inundate the server

        #################################  ENTER NEXT NAME AND CITY  ##############################################

            wd.find_element_by_xpath('//*[@id="hero_search_input"]').send_keys(firstName[counter], ' ', lastName[counter], ', ',
                                                                       city[counter], ', CA')#type in the information first & last name, city, CA, use the counter to access the correct piece of the array
            wd.find_element_by_xpath('//*[@id="hero_search_submit"]').click()#click the submit button

        ######################  STORE NEXT NUMBER IF STRAIGHT TO PROFILE ################################################

            isElementPresent = wd.find_element_by_xpath('//*[@id="profile_bookmark_button"])').size()#I want to make sure that a certain element does not exist by checking the "size" of some object containing my element this way, it doesnt wait forever looking for the object or waiting for it.
            if isElementPresent is True:#if the element is present then you're on the profile page already and you can stop and check the address and get the number
                streetNum = street[counter]
                htmlCode = wd.page_source
                soup = BeautifulSoup(htmlCode)
                for tag in soup.find_all(text = re.compile("\\(\\d\{3\}\\)\\s\\d\{3\}-\\d\{4\}")):
                    phone[counter] = tag.text
                    #save the number and other info to csv
                fileWriter.writerows(firstName[counter], lastName[counter], street[counter], city[counter], phone[counter])

        ##########################  OR MATCH NEXT ADDRESS IF MULTIPLE OPTIONS  ##########################################

            else:#otherwise we have to select the correct profile from the list of addresses
                streetNum = street[counter]
            #i feel like maybe I cant really do this... is xpath going to save the "text"? i need to be able to match it to
            #the array information.. this attribute thing might work
                profile1 = wd.find_element_by_xpath('//*[@id="2832"]/div[2]').getattr("maxLength = 30")
                profile2 = wd.find_element_by_xpath('//*[@id="2828"]/div[2]').getattr("maxLength = 30")
                profile3 = wd.find_element_by_xpath('//*[@id="2831"]/div[2]').getattr("maxLength = 30")
                profile4 = wd.find_element_by_xpath('//*[@id="2826"]/div[2]').getattr("maxLength = 30")
                profile5 = wd.find_element_by_xpath('//*[@id="2827"]/div[2]').getattr("maxLength = 30")

                if streetNum == profile1:
                    wd.find_element_by_xpath('//*[@id="2832"]').click()
                    wd.implicitly_wait(5000)
                if streetNum == profile2:
                    wd.find_element_by_xpath('//*[@id="2828"]').click()
                    wd.implicitly_wait(5000)
                if streetNum == profile3:
                    wd.find_element_by_xpath('//*[@id="2831"]').click()
                    wd.implicitly_wait(5000)
                if streetNum == profile4:
                    wd.find_element_by_xpath('//*[@id="2826"]').click()
                    wd.implicitly_wait(5000)
                if streetNum == profile5:
                    wd.find_element_by_xpath('//*[@id="2827"]').click()
                    wd.implicitly_wait(5000)
            ######################  GET NUMBER FROM CORRECT PAGE  ##################################################
                htmlCode = wd.page_source
                soup = BeautifulSoup(htmlCode)
                for tag in soup.find_all(text = re.compile("\\(\\d\{3\}\\)\\s\\d\{3\}-\\d\{4\}")):
                    phone[0] = tag.text

                fileWriter.writerows(firstName[counter], lastName[counter], street[counter], city[counter], phone[counter])
#with open("C:\Users\Public\Documents\compiledList.csv", "wb") as fileOut:
 #   fileWriter = csv.writer(fileOut)
  #  filewriter.writerow()