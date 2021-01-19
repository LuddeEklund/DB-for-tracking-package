#!/usr/bin/env python3
# Copyright (c) 2008-11 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version. It is provided for educational
# purposes and is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.

#Modification Ludvig Eklund, March 2020
#Source: http://www.qtrac.eu/py3book.html


import datetime
import os
import sqlite3
import sys

from datetime import datetime as dt
from time import process_time
from random import randint


def main():
    functions = dict(a=stress_test, b=add_place, c=add_customer, d=add_package, e=add_event, f=list_event, 
                     g=list_package, h=list_place, q=quit)  #refer to corresponding functions
    filename = os.path.join(os.path.dirname(__file__), "events.sdb")   
    db = None
    try:
        db = connect(filename)
        action = ""
        while True:
            place_counter = place_count(db)
            print('\nPackages ({0})'.format(os.path.basename(filename)))
            print()
            menu = ( " Menu, choose option(b-h) or quit (q): \n"
                     "(b) Add a new place to the database and give the place a (new) name\n"
                     "(c) Add a new customer to the database and give the customer a name\n"
                     "(d) Add a new package to the database and give the tracking number and customer name. The customer name has to already exist in the database. \n "
                     "(e) Add a new event to the database and give the tracking number, place and description. The customer name and tracking number have to already exist in the database. \n "
                     "(f) List all events of the package when tracking number is given\n"
                     "(g) List all of the customer's packages and the corresponding number of events\n"
                     "(h) List the number of events on a given date for a place\n"
                     "(q) quit \n"
                     #Why not numbers? https://stackoverflow.com/questions/10390606/python-syntaxerror-with-dict1-but-1-works

                    if place_counter else "Choose option (a) or (q): \n (a) Perform a database stress test,\n "
                                            "(q) quit \n")  
                    
            valid = frozenset("bcdefghiq" if place_counter else "aq")   #A set object is an unordered collection of immutable values. 
            action = get_menu_choice(menu, valid, "Your choice" if place_counter else "Choose a/q", True)  
            functions[action](db)
    finally:
        if db is not None:
            db.close()


def connect(filename):
    create = not os.path.exists(filename)
    db = sqlite3.connect(filename)
    if create:
        cursor = db.cursor()
        cursor.execute("CREATE TABLE Place ("
            "name VARCHAR(20) PRIMARY KEY UNIQUE NOT NULL) ")
        cursor.execute("CREATE TABLE Customer ("
            "name VARCHAR(20) PRIMARY KEY UNIQUE NOT NULL) ")
        cursor.execute("CREATE TABLE Package ("
             "tracking_number VARCHAR(20) PRIMARY KEY UNIQUE NOT NULL, "
             "customer_name VARCHAR(20) NOT NULL, "
             "FOREIGN KEY (customer_name) REFERENCES Customer)")
        cursor.execute("CREATE TABLE Event ("
            "id INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE NOT NULL, "
            "description VARCHAR(20) NOT NULL, "
            "time DATETIME, "
            "place_name VARCHAR(20) NOT NULL, "
            "package_tracking_number VARCHAR(20) NOT NULL, "
            "FOREIGN KEY (place_name) REFERENCES Place, "
            "FOREIGN KEY (package_tracking_number) REFERENCES Package) ")
        createSecondaryIndex = ("CREATE INDEX idx_tr_number ON Event (package_tracking_number)")  
        cursor.execute(createSecondaryIndex)                                                    
        db.commit()
    return db



def stress_test(db):

    customer_list = []  #empty list, "global" parameter within stress_test
    place_list = []
    tr_number_list = []
    
    #Adding a thousand places with the name P1, P2, P3
    def add_place_test(db):
        data_list = []
        for i in range(1, 1001):
            places = (str("P")+str(i))
            place_list.append(places)
            data = [places]
            data_list.append(data)
            
        cur = db.cursor()
        cur.executemany("INSERT INTO Place (name) VALUES (?)", data_list)
        db.commit()

    #Adding a thousand customers with the name C1, C2, C3
    def add_customer_test(db):
        data_list = []
        for i in range(1, 1001):
            customer = (str("C")+str(i))
            customer_list.append(customer)
            data = [customer]
            data_list.append(data)
            
        cur = db.cursor()
        cur.executemany("INSERT INTO Customer (name) VALUES (?)", data_list)
        db.commit()

    # We add a thousand packages to the database by drawing a random customer to every package
    def add_package_test (db):
        data_list = []
        for i in range(1, 1001):
            tr_number = (str("T")+str(i))
            tr_number_list.append(tr_number)
            customer_name = customer_list[randint(0,999)]  #draw random customer from customer_list, the index starts from zero  
            data = [tr_number, customer_name]
            data_list.append(data)
            
        cursor = db.cursor()
        cursor.executemany("INSERT INTO Package (tracking_number, customer_name) VALUES (?, ?)", data_list)
        db.commit()    

    #A million events are added, each is given a tracking number. 
    def add_event_test(db):
        descr_list = []
        data_list = []
        for i in range (1,51):   #we have 50 different descriptions
            descr = (str("D")+str(i))
            descr_list.append(descr)
            
        for i in range (1,1000000): 
            descr = descr_list[randint(0,49)]
            pl_name = place_list[randint(0,999)]
            tr_number = tr_number_list[randint(0,999)]
            created_at = get_time()
            data = [descr, created_at, tr_number, pl_name]  
            data_list.append(data)
            
        cursor = db.cursor()
        cursor.executemany("INSERT INTO Event (description, time, package_tracking_number, place_name) VALUES (?, ?, ?, ?)", data_list)
        db.commit()

    #We perform a thousand questions where we search the number of packages for a random customer
    def count_number_of_packages_test(db):
        #result_list = []
        for i in range (1000):
            customer = customer_list[randint(0,999)]  #get a random customer
            cursor = db.cursor()
            cursor.execute( "SELECT COUNT(tracking_number) FROM Package WHERE customer_name = (?)" , [customer]) 
            count = cursor.fetchall()
            #result = ( customer, count)
            #result_list.append(result)
        
        #print(result_list)
        
    #We perform a thousand questions where we search the number of events for a random package
    def count_number_of_events_test(db):
        #result_list = []
        for i in range (1000):
            tr_number = tr_number_list[randint(0,999)]
            cursor = db.cursor()
            cursor.execute( "SELECT COUNT(id) FROM Event WHERE package_tracking_number = (?)" , [tr_number]) 
            count = cursor.fetchall()
            #result = (tr_number, count)
            #result_list.append(result)
        
        #print(result_list)
    
    t_start = process_time() #start timer
    add_place_test(db) 
    t_place_test = process_time()
    print("Elapsed time (in seconds), add_place:", t_place_test- t_start)  
    
    add_customer_test(db)
    t_customer_test = process_time()
    print("Elapsed time, add_customer:", t_customer_test- t_place_test)  
    
    add_package_test(db)
    t_package_test = process_time()
    print("Elapsed time, add_package:", t_package_test - t_customer_test)
    
    add_event_test(db)
    t_event_test = process_time()
    print("Elapsed time, add_event:", t_event_test - t_package_test)
    print("Total elapsed time, add processes:", t_event_test- t_start)

    count_number_of_packages_test(db)
    t_count_number_of_packages_test = process_time()
    print("Elapsed time, count_number_of_packages_test",  t_count_number_of_packages_test - t_event_test)
    
    count_number_of_events_test(db)
    t_count_number_of_events_test = process_time()
    print("Elapsed time, count_number_of_events_test", t_count_number_of_events_test - t_count_number_of_packages_test)
    
#Add a new place to the database, when the name of the place is given 
def add_place(db):
    name = get_string("Place", "place")
    if not name:
        return
    check_place = find_place(db, name)
    if check_place:
        print("Error, not a new place")
        return
    cursor = db.cursor()
    cursor.execute("INSERT INTO Place "
                   "(name) "
                   "VALUES (?)",
                   [name])
    db.commit()
    
    
#Add a new customer to the database, when the name of the customer is given 
def add_customer(db):
    name = get_string("Customer", "customer")
    if not name:
        return
    check_customer = find_customer_name(db, name)
    if check_customer:
       print("Error, not a new customer")
       return
    cursor = db.cursor()
    cursor.execute("INSERT INTO Customer"
                   "(name) "
                   "VALUES (?)",
                   [name])
    db.commit()
 
#Add a new package to the database, when the tracking_number and customer is given. Customer should already be in the database
def add_package(db):
    tracking_number = get_string("Tracking_number", "tracking_number")
    if not tracking_number:
        return
    check_package = find_package(db, tracking_number)
    if check_package:   #has to be a new package
        print("Error, not a new tracking_number")
        return
    customer_name = get_string("Customer_name", "customer_name") 
    check_customer = find_customer_name(db, customer_name)
    if not check_customer:   #has to be an existing customer
        print("Unknown customer, failed to add package")
        return
    cursor = db.cursor()
    cursor.execute("INSERT INTO Package "
                   "(tracking_number, customer_name) "
                   "VALUES (?, ?)",
                   [tracking_number, customer_name])
    db.commit()

#Add a new event to the database, when tracking_number, customer and description is given. 
#Package and place should already be in the database
def add_event(db):
    descr = get_string("Description", "description")
    if not descr:
        return
    place = get_string("Name of place", "name of place")
    check_place = find_place(db, place)
    if not check_place:
         print("Unknown place, failed to add event")
         return
    tracking_number = get_string("Tracking_number", "tracking_number")
    check_package = find_package(db, tracking_number)
    if not check_package:
        print("Unknown tracking_number, failed to add event")
        return    
    created_at = get_time()
    cursor = db.cursor()
    cursor.execute("INSERT INTO Event "
                   "(description, time, package_tracking_number, place_name) "
                   "VALUES (?, ?, ?, ?)",
                   [descr, created_at, tracking_number, place])
    db.commit()


def find_customer_name (db, customer):
    cursor = db.cursor()
    cursor.execute("SELECT name FROM Customer WHERE name=(?)", [customer])
    records = cursor.fetchall()
    if len(records) == 0:
        return False
    else:
        return True
    
def find_place (db, p):
    cursor = db.cursor()
    cursor.execute("SELECT name FROM Place WHERE name=(?)", [p])
    records = cursor.fetchall()
    if len(records) == 0:
       return False
    else:
       return True
 
def find_package (db, tr_number):
    cursor = db.cursor()
    cursor.execute("SELECT tracking_number FROM Package WHERE tracking_number=(?)", [tr_number])
    records = cursor.fetchall()
    if len(records) == 0:
        return False
    else:
        return True

def find_date (db, date):
    cursor = db.cursor()
    cursor.execute("SELECT time FROM Event WHERE strftime('%Y-%m-%d', time)=(?)", [date])  
    records = cursor.fetchall()
    if len(records) == 0:
       return False
    else:
       return True

#Get the amount of events on a specific place and day
def list_place(db):
    p = get_string("Place", "place")  
    check_place = find_place (db, p)
    if not check_place:
        print("Unknown place, listing of events failed")
        return
    date = get_string("Date in the shape YYYY-MM-DD", "date in the shape YYYY-MM-DD")  
    check_time = find_date (db, date)
    if not check_time:
        print("No event ", date)
        return
    
    cursor = db.cursor()
    cursor.execute("CREATE TEMPORARY TABLE Temp_table AS SELECT id, time, place_name FROM Event WHERE place_name=(?)", [p])
    cursor.execute("SELECT COUNT(id) FROM Temp_table WHERE strftime('%Y-%m-%d', time)=(?)", [date])
    count = cursor.fetchall()
    count = str(count)
    count = count.replace("[(", "")  
    count = count.replace(",)]", "")
    print("Place: ", p, "Number of events: ",count, "on date: ", date)
    cursor.execute("DROP TABLE IF EXISTS Temp_table")

#Get all the packages for a specific customer, and the number of events
def list_package(db):
    customer = get_string("Customer", "customer")  #ask customer
    check_customer = find_customer_name (db, customer)
    if not check_customer:
        print("Unknown customer, listing of events failed")
        return
    cursor = db.cursor()
    cursor.execute( "SELECT tracking_number FROM Package WHERE customer_name = (?)" , [customer])         
    tr_number = cursor.fetchall() 
    tr_number = str(tr_number)
    
    numbers = re.findall("(\d+)", tr_number)   #The regex pattern \d+ matches 1 or more numerical characters in sequence.
            # By putting it in brackets ( ) it captures each occurrence of that pattern
            # as a group. And the re.findall method returns those groups in a list. 
            # Note that they are still strings, not numbers.
    
    for i in range(len(numbers)):
        tr_nr = ("T" + numbers[i])
        sql = ("SELECT COUNT(id) FROM Event "        
           "WHERE package_tracking_number = (?)")
        cursor.execute(sql, [tr_nr]) 
        count = cursor.fetchall()
        count = str(count)
        count = count.replace("[(", "")  
        count = count.replace(",)]", "")
        print("Customer: ", customer, "package tracking_number: ", tr_nr, "number of events: ", count)  
        
#Get all the events for a package with a given tracking_number 
def list_event(db):
    tr_number = get_string("Tracking_number", "tracking_number")
    check_package = find_package(db, tr_number)
    if not check_package:
       print("Unknown tracking_number, listing of events failed")
       return    
    cursor = db.cursor()
    sql = ("SELECT * FROM Event "
           "WHERE package_tracking_number = (?)")
    cursor.execute(sql, [tr_number])
    records = cursor.fetchall()
    print("List_event: ", records)

def get_menu_choice(message, valid, default=None, force_lower=False):
    message += ": " if default is None else " [{0}]: ".format(default)
    while True:
        line = input(message)
        if not line and default is not None:
            return default
        if line not in valid:
            print("ERROR only {0} are valid choices".format(
                  ", ".join(["'{0}'".format(x)
                  for x in sorted(valid)])))
        else:
            return line if not force_lower else line.lower()

def get_time():
    return dt.now().strftime('%Y-%m-%d %H:%M:%S')
  
def package_count(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM Package")
    return cursor.fetchone()[0]

def place_count(db):
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM Place")
    return cursor.fetchone()[0]
        
def get_string(message, name="string", default=None,
               minimum_length=0, maximum_length=80,
               force_lower=False):
    message += ": " if default is None else " [{0}]: ".format(default)
    while True:
        try:
            line = input(message)
            if not line:
                if default is not None:
                    return default
                if minimum_length == 0:
                    return ""
                else:
                    raise ValueError("{0} may not be empty".format(
                                     name))
            if not (minimum_length <= len(line) <= maximum_length):
                raise ValueError("{0} must have at least {1} and "
                        "at most {2} characters".format(
                        name, minimum_length, maximum_length))
            return line if not force_lower else line.lower()
        except ValueError as err:
            print("ERROR", err)


def quit(db):
    if db is not None:
        count = package_count(db)
        db.commit()
        db.close()
        print("There are {0} package(s) ".format(count),"in the database.")
    sys.exit()

main()
