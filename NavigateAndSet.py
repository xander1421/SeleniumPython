import time, re, sys
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException, NoAlertPresentException, ElementNotInteractableException

import json

#for sendding emails
from mail_sender import email_usage
#fancy stuff
import functools

####################################################################################################################################
delay = 25
####################################################################################################################################
class GoToSubscriberPage(object):

    def __init__(self, phone_number, country_of_visit, type_of_package, for_today_or_future, day, month, days_away):
        self.phone_number = phone_number
        self.country_of_visit = country_of_visit
        self.type_of_package = type_of_package
        self.for_today_or_future = for_today_or_future
        self.day = day
        self.month = month
        self.days_away = days_away
        
#USED####INITIAL WEBDRIVER SETUP
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.driver.maximize_window()

        self.verificationErrors = []
        self.accept_next_alert = True

#USED#### Login

    def go_to_subscriber_page(self): # login without cookies
        driver = self.driver
        with open('creds.json') as f:
            data = json.load(f)
        driver.get(('WEBSITE_URL'))

        try:
            driver.find_element_by_xpath('//*[@id="USER"]').send_keys(data['userName'])
            # Fil the password
            driver.find_element_by_xpath('//*[@id="PASSWORD"]').click()
            driver.find_element_by_xpath('//*[@id="PASSWORD"]').send_keys(data['password'])
            # Click loginBTN
            driver.find_element_by_id('LoginBtn').click() # wait for elements to load
            #driver.get(('https://biz.partner.co.il/he-il/biz/international/Going-abroad/')) #Goto package page

            print("We are logged in")
        except NoSuchElementException:
            driver.refresh()
            print('refreshed')
            GoToSubscriberPage.go_to_subscriber_page(self)
    

        
#USED#####Input users Number from: list1                       
    #//DONE   
    def input_number(self):
        driver = self.driver
        
        # Located the field where you input the Users phone number
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.ID, 'ContentBody_FindContractCtrl1_Input')))
        if TimeoutException:
            print("were out of time, could not fing the number input field")
            
        else:
            ("were good")
        WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.ID, 'ContentBody_FindContractCtrl1_Input'))).click()
        driver.find_element_by_id("ContentBody_FindContractCtrl1_Input").clear()
        
        i = 0
        phone_number = list(self.phone_number)
        while i < 9:
            driver.find_element_by_id("ContentBody_FindContractCtrl1_Input").send_keys(phone_number[i])
            driver.find_element_by_id("ContentBody_FindContractCtrl1_Input").click()
            
            i += 1
        WebDriverWait(driver, 4)

        try:
            users_number = driver.find_element_by_class_name('number')
            
            
            if users_number.is_enabled():
                WebDriverWait(driver, 2)
                print('i used this')
                users_number.click()
            else:
                print("THE USER DOESNT HAVE A PARTNER NUMBER")
                exit()         
        except TimeoutException:
            print("THIS TOOK TO MUCH TIME, RESTART THE SCRIPT")
        except ElementNotInteractableException:
            print("THE USER DOESNT HAVE A PARTNER NUMBER 3")
            print("Need to send him email to get a package by himself, below class can do that")
            
            cell_nr = self.phone_number
            str1 = ''.join(str(e) for e in cell_nr)
            #sending test email to helpdesk

            email_body = '''Unfortunately, we can't activate the data package for your trip because your number isn't covered by the Partner.
 For this trip you will need to manage the package by yourself (talk with a cellular company and arrange a package) – and you will get a refund for up to 350 NIS maximum..'''
            email = email_usage('helpdesk@EMAIL.COM', 'Number: ' + str1 + ' not in partner', email_body)    
            #email.send_email()
              
            exit()

#USED##### Checks if a package has been set for a recent date
    #//DONE
    def check_for_future(self):
        
        driver = self.driver
        try:
            elem = driver.find_element_by_xpath('/html/body/form[1]/div[2]/div[2]/div[2]/section/section/div[3]/table/tbody/tr[2]/td[3]/a')
            if elem.is_enabled():
                elem.click()
                # this will click the element if it is there
                print("FOUND a package set for future activation: the details are below")
                self.type_set_for_future = driver.find_element_by_css_selector('.internationalPackagesFUview > td:nth-child(1)').get_attribute('innerHTML') #get type of package
                self.date_set = driver.find_element_by_css_selector('.internationalPackagesFUview > td:nth-child(2)').get_attribute('innerHTML') #get date of package
                print("The type of package that was set is: " + self.type_set_for_future)
                print("The date that the package will start is: " + self.date_set)


                if str(self.type_of_package) in self.type_set_for_future:
                    print("No need to activate a new package for the user, it has already been set for future activation")

                    listToStr = ' '.join([str(elem) for elem in self.phone_number]).replace(' ', '')

                    send_email_if_package_already_activated = email_usage('helpdesk@EMAIL.COM', 'No need to activate a new 3GB data package', 'There is no need to activate a new package for the user: ' + listToStr + '. It has already been set to activation and it will start on ' + self.day + '/' + self.month)
                    #send_email_if_package_already_activated.send_email()
                    exit()
                               
        except NoSuchElementException:
                print("This user has no  package set for future activation")

#USED##### in some rare cases users didnt have pakcages for a long time so we do a check
    #//DONE
    def nopackages(self):
        
        driver = self.driver
        try:
            clean = ("lnkOpenDetails")
            elem_clean = driver.find_element_by_id(clean)
            if elem_clean.is_enabled():
                WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.ID, clean))).click() #tries to click the show more package details
            WebDriverWait(driver, delay)
            clean_elem = driver.find_element_by_css_selector("#tblEnetitlements > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(3) > a:nth-child(1)")
            if clean_elem.is_enabled():                 
                print("its clean")     
            else:
                WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#lnkOpenDetails"))).click() #tries to click the show more package details
        except NoSuchElementException:
                print("had before")

#####################################################

#USED#####checks if the user has a running package1 and brings back all of its details 
    def check_active1(self):
        
        driver = self.driver
        try:
            WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#lnkOpenDetails"))).click()
            ####
            package1_date_start = driver.find_element_by_css_selector('.date-row')
            package1_date_end = driver.find_element_by_css_selector('.rDetails > div:nth-child(2)')
            print(package1_date_end)
            if package1_date_start.is_enabled():
                elem_type_set = driver.find_element_by_css_selector('.rDetails > div:nth-child(1) > span:nth-child(2)') #chacks is the element is in the page
                self.type_set = elem_type_set.get_attribute('innerHTML') # Gets text if 1 or 3 GB is set
                procentage_usage_elem = driver.find_element_by_class_name('percentConNum')                    
            
                procentage_usage = procentage_usage_elem.get_attribute('innerHTML') # gets how many % of the package have been used
                procentage_usageConvesion = ''.join(x for x in procentage_usage if x.isdigit())
                self.procentage_usage_int1 = procentage_usageConvesion[:-2]

                date_start = package1_date_start.get_attribute('innerHTML') # Gets the text of when the package started 
                full_date_end = package1_date_end.get_attribute('innerHTML')[-25:-15] #FORMAT(dd/mm/yyyy) #Gets the text of when the package will end 
                               
                self.day_date_end1 = full_date_end[:-8] # GET THE DATE STRING
                self.month_date_end1 = full_date_end[-7:-5] # GET THE MONTH STRING
                print(full_date_end + "why") 
                print("were in check_active1")
                print("Package1 type: " + self.type_set)
                print(self.procentage_usage_int1 + "% were used from the current package")
                print("Package1 started at : " + date_start)
                print("Package1 will end: " + full_date_end)

                self.whats_active1 = str(self.type_of_package) + "GB" # generates the string to compare with the new package
                GoToSubscriberPage.see_if_needed1(self)
        except NoSuchElementException:
            print("This user has no 1st active package")               


    def see_if_needed1(self):
        
        if int(self.month_date_end1) >= int(self.month): # checks if the month of departure is the same as the month that the package ends
            package_has_days_available1 = int(self.day_date_end1) - int(self.day) # How many days are left for the package
            package_has_days_available = abs(package_has_days_available1)
            if int(package_has_days_available) >= int(self.days_away): #checks if the days the package has left are more or equal to how many days the user will be away
                if self.whats_active1 in self.type_set: #checks if the active package is the same type that its trying to activate
                    print("User has an active data package that is the same as the one that needs to be activated") 
                    if int(self.procentage_usage_int1) <= 75: # checks if the package has less than 75% usage
                        print("The user only has " + self.procentage_usage_int1 + "%" + " used from the 1ST DATA package" + " no need to activate another one")
                        exit()
                    elif int(self.procentage_usage_int1) > 75:
                        print("Need to activate another current package usage is big1")
                    else:
                        print("Need to activate another current package usage is big1.1")
                else:
                    print("Different type of packages  active =/= package it wants to activate #1ST")
                    pass
            else:
                print("The 1ST DATA package needs to have more days")
                pass                  
        else:
            print("this is ok but month is not here")
            pass

#USED#####checks if the user has a running package2 and brings back all of its details

    def check_active2(self): 
        
        driver = self.driver
        try:

            package2_date_start = driver.find_element_by_xpath('(//td[@class="date-row"])[2]')

            package2_date_end = driver.find_element_by_xpath('//*[@id="Div21"]/div[4]/div[1]/div[2]')

            if package2_date_start.is_enabled():
                elem_type_set2 = driver.find_element_by_css_selector('div.openInnerContent:nth-child(4) > div:nth-child(1) > div:nth-child(1) > span:nth-child(2)') #chacks is the element is in the page
                self.type_set2 = elem_type_set2.get_attribute('innerHTML') # Gets text if 1 or 3 GB is set
                #procentage_usage_elem2 = driver.find_element_by_xpath('(//span[@class="percentConNum")[2]') 
                procentage_usage_elem2 = driver.find_element_by_xpath('/html/body/form[1]/div[2]/div[2]/div[2]/section/section/div[3]/table/tbody/tr[4]/td/li[2]/div/table/tbody/tr/td/div[2]/div[3]/div/table/tbody/tr[1]/td[3]/div/span')                   
            
                procentage_usage2 = procentage_usage_elem2.get_attribute('innerHTML') # gets how many % of the package have been used
                procentage_usageConvesion = ''.join(x for x in procentage_usage2 if x.isdigit())
                self.procentage_usage_int2 = procentage_usageConvesion[:-2]

                date_start2 = package2_date_start.get_attribute('innerHTML') # Gets the text of when the package started 
                
                full_date_end2 = package2_date_end.get_attribute('innerHTML')[-25:-15] #FORMAT(dd/mm/yyyy) #Gets the text of when the package will end 
                self.day_date_end2 = full_date_end2[:-8] # GET THE DATE STRING
                self.month_date_end2 = full_date_end2[-7:-5] # GET THE MONTH STRING
                print("were in check_active2")
                print("Package2 type: " + self.type_set2)
                print(self.procentage_usage_int2 + "% were used from the 2nd package")
                print("Package2 started at : " + date_start2)
                print("Package2 will end: " + full_date_end2)

                self.whats_active2 = str(self.type_of_package) + "GB" # generates the string to

                GoToSubscriberPage.see_if_needed2(self)      #performs the checkage to see if the dates are available       
            
        
        except NoSuchElementException:
                print("This user has no 2nd active package")

#################################################################################################
    def see_if_needed2(self):

        try:
            if int(self.month_date_end2) >= int(self.month): # checks if the month of departure is the same as the month that the package ends
                package_has_days_available2 = int(self.day_date_end2) - int(self.day) # How many days are left for the package
                package_has_days_available = abs(package_has_days_available2)
            if int(package_has_days_available) >= int(self.days_away): #checks if the days the package has left are more or equal to how many days the user will be away
                if self.whats_active2 in self.type_set2: #checks if the active package is the same type that its trying to activate
                    print("User has an active data package that is the same as the one that needs to be activated") 
                    if int(self.procentage_usage_int2) <= 75: # checks if the package has less than 75% usage
                        print("The user only has " + self.procentage_usage_int2 + "%" + " used from the 2ND DATA package" + " no need to activate another one")
                        exit()
                    elif int(self.procentage_usage_int2) > 75:
                        print("Need to activate another current package usage is big2")
                    else:
                        print("Need to activate another current package usage is big2.1")
                else:
                    print("Different type of packages  active =/= package it wants to activate #2PACKAGE")
                    pass
            else:
                print("The 2ND DATA package needs to have more days")
                pass                  
        except AttributeError:
            print('NO 2ND PACKAGE TO CALCULATE')
            pass
# #########
    def active_ones(self): #checks many things
        driver = self.driver
        message_active_text = driver.find_element_by_xpath('/html/body/form[1]/div[2]/div[2]/div[2]/section/section/div[3]/table/tbody/tr[3]/td[2]/span[1]').get_attribute('innerHTML')
        
        text_package_for_future = driver.find_element_by_xpath('(//span[@class="statusDiv1"])[1]').get_attribute('innerHTML')
        # print(text_package_for_future)
        if str(text_package_for_future) == 'אין חבילות פעילות':
            GoToSubscriberPage.nopackages(self)
            print('There are no active packages in active_ones')
        else:
            GoToSubscriberPage.nopackages(self)
            ('text_package_for_future with ELSE')
        
        
        if str(message_active_text) == 'קיימות חבילות פעילות':
            print('May have active packages, will now gather their details')
            
            GoToSubscriberPage.check_active1(self)
            # GoToSubscriberPage.see_if_needed1(self)
            try:
                package2_date_start = driver.find_element_by_xpath('(//td[@class="date-row"])[2]')

                if package2_date_start.is_displayed():
                    GoToSubscriberPage.check_active2(self)
                    # GoToSubscriberPage.see_if_needed2(self)
            except NoSuchElementException:
                print('No need to calculate the second package, its not activated')

        elif str(message_active_text) == 'אין חבילות פעילות':
            print('Doesnt have active packages')



##########################################################################################################
#NOT USED#####Chose the country
#//DONE / tested / works
    def chose_country(self):
        driver = self.driver
        
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="txtCountries"]')))
        WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.ID, 'txtCountries'))).click()
        driver.find_element_by_id('txtCountries').clear()
        driver.find_element_by_id('txtCountries').send_keys(self.country_of_visit)
        
        driver.find_element_by_id('txtCountries').send_keys(Keys.DOWN)
        WebDriverWait(driver, delay)
        driver.find_element_by_id('txtCountries').send_keys(Keys.ENTER)
        WebDriverWait(driver, delay)
        print('country set: '+ self.country_of_visit) 
        #clicks the show more packages button
        try:
            time.sleep(5) #wait for 5 seconds
            elem_more = driver.find_element_by_xpath('(//*[@class="more-lnk"])[2]')
            elem_more.click()
        except NoSuchElementException:
            print("THIS COUNTRY DOESNT HAVE DATA PACKAGES")
                #sending test email helpdesk
            email = email_usage('helpdesk@EMAIL.COM', 'This country: ' + self.country_of_visit + ' doesnt have data packages, inform the user', '_test_NO_DATA_PACKAGE_FOR_THIS_COUNTRY')    
            #email.send_email()
            exit()

#Choses which package to activate 3 or 3.1 GB

    def chose_type_3GB(self): 
        driver = self.driver
        try:
            package3_1 = driver.find_element_by_xpath("/html/body/form[1]/div[2]/div[2]/div[2]/section/section/div[4]/section/section/table[2]/tbody/tr[6]/td[4]/div/a")
            if package3_1.is_enabled():
                
                package3_1.click()
                print("SET 3GB")
                
        except NoSuchElementException:
                WebDriverWait(driver, delay)
                driver.save_screenshot("NO_PACKAGE_AVAILABLE.png")
                print("CANT SET ANY MORE PACKAGES")
                print("Need to send him email to get a package by himself")
                
                #sending test email to helpdesk
                email = email_usage('helpdesk@EMAIL.COM', 'Cant set any more 3GB packages, send email to partner for them ' + self.phone_number + ' to set it manually', '_test_')    
                #email.send_email()

                exit()
    def chose_package_to_set(self):
        driver = self.driver

        if self.type_of_package == 1:
            try:
                package1GB = driver.find_element_by_xpath('/html/body/form[1]/div[2]/div[2]/div[2]/section/section/div[4]/section/section/table[2]/tbody/tr[1]/td[4]/div/a')
                
                if package1GB.is_enabled():

                    package1GB.click()
                    print("SET 1GB")

            except NoSuchElementException:
                print("cannot set the 1GB package, elem not in page")
        elif self.type_of_package == 3:
            try:
                package3GB = driver.find_element_by_xpath('/html/body/form[1]/div[2]/div[2]/div[2]/section/section/div[4]/section/section/table[2]/tbody/tr[6]/td[4]/div/a')
                
                if package3GB.is_enabled():
                    
                    package3GB.click()
                    print("SET 3GB")
            except NoSuchElementException:
                print("cannot set the 3GB package, elem not in page")

#####################################################################################################################################
    #//Work in progress
    # Chose a package for future date     
    def for_future_date(self):
        driver = self.driver
        #tick the approve box
        time.sleep(3)
        WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.NAME, 'approve_checkbox'))).click()
        #driver.find_element_by_name('approve_checkbox').click()
        if self.for_today_or_future == 1:
            WebDriverWait(driver, delay)
            print("Confirm for today")
            exit()
        elif self.for_today_or_future == 2:  #package starting not today
            todays_date = datetime.now()
            WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, '//*[@id="SHOW_CALNDER"]')))
            WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="SHOW_CALNDER"]'))).click()
       
            print("opened date picked")
            driver.find_element_by_class_name('ui-datepicker-trigger').click()          
            WebDriverWait(driver, delay)
            WebDriverWait(driver, delay)
            WebDriverWait(driver, delay)

            if int(self.month) > int(todays_date.month): #package starting not today and for next month
                WebDriverWait(driver, delay)
                driver.find_element_by_xpath("/html/body/div[7]/div/a[1]").click() #pressed the next month button
                
                #the element with the passed date
                date_xpath = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, "//table[@class='ui-datepicker-calendar']//a[.='" + self.day + "']")))
                #costum action to move to the element and click it
                ActionChains(driver).move_to_element(date_xpath).click(date_xpath).perform()
                print("Confirm for a future month and date")

            else: #self.month == todays_date.month: #package starting not today but this month
                # select  the date that is being passed with: self.day
                WebDriverWait(driver, delay)
                #driver.find_element_by_xpath("//table[@class='ui-datepicker-calendar']//a[.='" + self.day + "']").send_keys(Keys.END)
                
                
                date_xpath = WebDriverWait(driver, delay).until(EC.element_to_be_clickable((By.XPATH, "//table[@class='ui-datepicker-calendar']//a[.='" + self.day + "']")))
                #costum action to move to the element and click it
                ActionChains(driver).move_to_element(date_xpath).click(date_xpath).perform() 

                print("Confirm for future date")


# if __name__ == "__main__":

#           phoneNUmber(123456789), country(name), typeofpackage(1or3), forWhen(1or2), date(number), month(number), days_away(number)
#     foo = GoToSubscriberPage('phoneNumber','country', 3, 1 ,'31','12', 26)                                                                                                  #549222280   USER WITH 2 active packages

#     ###############################
#     foo.setUp()
#     foo.go_to_subscriber_page()
#     foo.input_number()
#     foo.check_for_future()
#     foo.nopackages()
    
#     # foo.check_active1()
#     # foo.check_active2()
#     foo.active_ones()

#     foo.chose_country()
#     # foo.chose_type_3GB()
#     foo.chose_package_to_set()
#     foo.for_future_date()
# # ################################## 
