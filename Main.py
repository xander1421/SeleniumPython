from queryData import *  


class Type_to_set(object):
    def __init__(self, private_or_business):
        self.private_or_business = private_or_business

    @classmethod
    def from_inputs(cls):
        return cls(
            int(input('Type 0 for Private or 1 for Business: ')),
        )
    def run_from_TAS_or_manual_input(self): #uses TAS to extract data and to create the package
###############################        
        if self.private_or_business == 1:
            to_print = ExtractFromSQL()
            to_print.make_sql_connection()
            
            funct = Calculations.from_input() #which row to chose from
            funct.make_sql_connection()
            funct.get_phone_nr()
            funct.get_dates()
            funct.check_type_of_Package_To_Set()
            funct.get_data_from_qry()
            funct.check_if_for_today_or_future()
            funct.gather_info_from_class()
            funct.configure_packages()
###############################
        elif self.private_or_business == 0:
            phone_number = input("Type the phone number EX: 123456789 : ")
            country_name = input("Type the country name: ")
            GB1_or_GB3 = int(input("Type 1 for 1GB package and 3 for 3Gb package: "))
            today1_future2 = int(input("Type 1 for the package to start now or 2 to make it start at a future date: "))
            date_of_dep = input("Type the date if the package has to start at a future date else press ENTER: ")
            month_of_dep = input("Type the month number for future departure else press ENTER: ")
            days_away = input("Type the number of days the user will be away else press ENTER: ")
###############################
            if today1_future2 == 1:
                foo = GoToSubscriberPage(phone_number, country_name, GB1_or_GB3, today1_future2, date_of_dep, month_of_dep, days_away)
                ###############################
                foo.setUp()
                foo.go_to_subscriber_page()
                foo.input_number()
                foo.check_for_future()
                #foo.nopackages()

                #foo.check_active1()
                #foo.check_active2()
                #foo.active_ones()
                foo.chose_country()
                #foo.chose_type_3GB()
                foo.chose_package_to_set()
                foo.for_future_date()
###############################                
            elif today1_future2 == 2:
                foo = GoToSubscriberPage(phone_number, country_name, GB1_or_GB3, today1_future2, date_of_dep, month_of_dep, days_away)
                ###############################
                foo.setUp()
                foo.go_to_subscriber_page()
                foo.input_number()
                foo.check_for_future()

                foo.active_ones()
                
                foo.chose_country()
                # foo.chose_type_3GB()
                foo.chose_package_to_set()
                foo.for_future_date()

###############################                
                
if __name__ == "__main__":


    chosing = Type_to_set.from_inputs()

    chosing.run_from_TAS_or_manual_input()





