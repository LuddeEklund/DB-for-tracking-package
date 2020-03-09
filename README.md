# DB-for-tracking-package

Database with a command line interface 

Maybe you have ordered a product from the internet and followed its journey to your home door.  This program builds and deploys a database, that could work as the back-end system. 

The program is written in Python and runs from commando prompt, preferable from Anaconda. 

Overview

There is places, customers, packages and events. 

A place is somewhere on the journey where the package is scanned. Every place has a different name.

A customer order the package, every customer have a different name. 

Every package has a tracking number, by which the package can be referred to. Every package has a different tracking number and every package belongs to a specific customer. 

When the package is scanned, an event occurs. An event refers to a specific package and place. Furthermore, a description and added time, date and clock time, is added to the event.  

There are functions and functionality in the program. I recommend that you will start exploring with the stress test, option (i). This will give you a database with 1000 packages and 1 million events. Option (i) should take less than 50 seconds. 
