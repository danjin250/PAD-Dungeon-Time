# PAD-Dungeon-Time
Get the daily PAD Dungeon Times sent to your email

Written in Python

App stores a list of emails that you can add or remove when you run the program.
Add your email and your PAD ID and when you run it, you get an email telling you your dungeon times (in EST)
Works by scraping the PADX site with Selenium

This is specifically for the limited time dungeons that depend on your group number each day, 
such as Metal Dragons, daily Descends, Starry Vault, Tamadra Retreats etc etc.


If you leave the program running (like on a raspberryPi for example), it'll wait until 7AM the next day to sent out 
an email again.

