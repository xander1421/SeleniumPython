#query data from DB
import pyodbc
import pprint
import sys, os
import collections
import pandas as pd
import calendar
from datetime import datetime
from string import ascii_letters, punctuation, whitespace
from NavigateAndSet import GoToSubscriberPage



class ExtractFromSQL(object):
################################## Brings the full table from SQL
    def make_sql_connection(self):
        connection = pyodbc.connect("DRIVER={SQL Server};"
                        "Server=SERVER_NAME;"
                        "Trusted_Connection=no;"
                        "UID=USERNAME;"
                        "PWD=PASSWORD")
    ############                      
        qry = """THE_QUERY"""
    ############
        if connection:
            print("Huston, we have a connection")
            self.data = pd.read_sql(qry,connection) #get all data in a table
            pprint.pprint(self.data) #prints all the data

            return self.data
############################ Brings the full table from SQL



class Calculations(object):

    def __init__(self, row):
        self.row = row # Choses a row from the table we got in CLASS: ExtractFromSQL
        
##################
    def make_sql_connection(self):
        connection = pyodbc.connect("DRIVER={SQL Server};"
                        "Server=SERVER_NAME;"
                        "Trusted_Connection=no;"
                        "UID=USERNAME;"
                        "PWD=PASSWORD")
    ############                      
        qry = """THE_QUERY"""
    ############
        if connection:
            print("Huston, we have a connection")
            self.data = pd.read_sql(qry,connection) #get all data in a table
            # pprint.pprint(self.data) #prints all the data
############################ Brings the full table from SQL
        return self.data 

    
    #used to chose the row before execution    
    @classmethod
    def from_input(cls):
        return cls(
            int(input('CHOSE THE ROW: ')),
        )

    def get_data_from_qry(self):
        ############################ get country name
        country_of_visit_obj = self.data.at[self.row, 'countryName']
        self.country_of_visit = str(country_of_visit_obj)
        ##################
        if self.country_of_visit == 'United States': # comes from TAS like this but you cant find the country in Partner 
            self.country_of_visit = 'usa' # in this format it's recognizable
        elif self.country_of_visit == 'Cameroon': # NO PACKAGES FOR THIS COUNTRY
            print(self.country_of_visit + 'doesnt have DATA packages available for purchase')
            exit()
        elif self.country_of_visit == 'Russian Federation':
            self.country_of_visit = 'Russia'

        else:
            print('No need to modify the country name')
            
        
############################ get country name
        return self.country_of_visit


    def get_phone_nr(self):
        phone_number = self.data.at[self.row, 'cellNumber']
        # phone_number_clean = int(phone_number)
        clean_phone_number = ''.join(x for x in phone_number if x.isdigit()) # => phone number is made of 9 digits
  
        self.clean_phone_number = clean_phone_number[-9:] # get the last 9 digit of the phone_number
        
        #print phone number
        print("\nThe phone number is", self.clean_phone_number)        
        return self.clean_phone_number


    
    def get_dates(self):
############################ get departure dates
        dep_date = self.data.at[self.row, 'departureDate']     #gets the row info || departureDate
        
        print(type(dep_date))

        self.dep_date_string = str(dep_date)

        self.dep_date = self.dep_date_string[8:10]
        self.dep_month = self.dep_date_string[5:7]
        ############################ get departure date and month
        print("Departure Date is= " + self.dep_date)   #prints departure date
        print("Departure month= " + self.dep_month) #prints departure month 
    ###########################
        ret_date = self.data.at[self.row, 'returnDate']  #gets the row info || returnDate
        self.ret_date_string = str(ret_date)
        self.ret_date = self.ret_date_string[8:10]
        self.ret_month = self.ret_date_string[5:7]
        ############################ get return date and month
        print("Return Date is=  " + self.ret_date)
        print("Return Month is= " + self.ret_month)
    ############################
        self.today_date = datetime.now()
        self.today_month = self.today_date.month
        print("Todays month is: ", self.today_month)
        # day_obj  = self.dep_date_string
        print("todays full date is ", self.today_date)
############################
        return self.dep_date


    def check_type_of_Package_To_Set(self):       
        #calculate the difference between departure day and return day
            print("package is for future date")
            
            
            now = datetime.now()
            how_many_days_the_month_has = calendar.monthrange(now.year, now.month)[1]  #gets how many days the current month has
            
            dm = self.dep_month
            dd = self.dep_date.lstrip("0") # removes the 0 from the front of dates between 1 to 9
            
            rm = self.ret_month
            rd = self.ret_date 

            if int(rm) == int(dm): # if the departure and return month are the same
                
                self.days_away = (int(rd) - int(dd))
                print("days away:", self.days_away)
                if self.days_away > 7:
                    print("more then 7 days")
                    self.type_of_package = None
                    self.type_of_package = 3 #SETS 3GB DATA PACKAGE
                else:
                    print("less then 7 days")
                    self.type_of_package = None
                    self.type_of_package = 1 #SETS 1GB DATA PACKAGE
                return self.type_of_package
            else:  # if the departure and return month are different
                self.days_away = (how_many_days_the_month_has - (int(dd)-int(rd)))
                print("days away:", self.days_away)
                if self.days_away > 7:
                    print("more then 7 days, next month")
                    self.type_of_package = None
                    self.type_of_package = 3 #SETS 3GB DATA PACKAGE
                else:
                    print("less then 7 days, next month")
                    self.type_of_package = None
                    self.type_of_package = 1 #SETS 1GB DATA PACKAGE
                return self.type_of_package, self.days_away


    def check_if_for_today_or_future(self):
        self.for_today_or_future = None
        self.dep_date = self.dep_date.lstrip("0")

        if (int(self.dep_month)) == self.today_month:

            if int(self.today_date.day) == int(self.dep_date):
                self.for_today_or_future = 1
                print("HAS TO START TODAY")

            elif int(self.today_date.day) < int(self.dep_date):
                self.for_today_or_future = 2
                print("HAS TO START AT A FUTURE DATE 1")    
            else:
                print("CANT SET THE PACKGE, the user departure date has already passed")
                exit()

        elif (int(self.dep_month)) > self.today_month:
            self.for_today_or_future = 2
            print("HAS TO START AT A FUTURE DATE because the Departure month is Numbers Bigger")
            
        elif (int(self.dep_month)) < self.today_month:
            print("CANT SET THE PACKGE, the user departure date has already passed")
            exit()
        
        
        return self.for_today_or_future


    def gather_info_from_class(self): # gathers the information in a list to use with the class below
        self.info = [list(self.clean_phone_number), str(self.country_of_visit), self.type_of_package, self.for_today_or_future, self.dep_date, self.dep_month, self.days_away]    
        print(self.info)
                
        return self.info

    
    def configure_packages(self):
        foo = GoToSubscriberPage(self.info[0],self.info[1],self.info[2],self.info[3],self.info[4], self.info[5], self.info[6])
    ###############################
        foo.setUp()
        foo.go_to_subscriber_page()
        foo.input_number()
        foo.check_for_future()
        
        # foo.nopackages()
        # foo.check_active1()
        # foo.check_active2()
        foo.active_ones() 
        
        foo.chose_country()
        # foo.chose_type_3GB()
        foo.chose_package_to_set()
        foo.for_future_date()



# if __name__ == "__main__":
    
        


#         to_print = ExtractFromSQL()
#         to_print.make_sql_connection()
        
#         funct = Calculations.from_input() #which row to chose from 8 not in system
#         funct.make_sql_connection()
#         funct.get_phone_nr()
#         funct.get_dates()
#         funct.check_type_of_Package_To_Set()
#         funct.get_data_from_qry()
#         funct.check_if_for_today_or_future()
#         funct.gather_info_from_class()
#         funct.configure_packages()






# run_from_TAS()





    






