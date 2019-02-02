from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import re
import pandas as pd

# Get the ID for different games 
# We will use these id's to build up link to the page with game stats
def getLinkID(l):
	
  # We will create a Firefox driver and run it headless
  # If you want to see the browser window, remove the options in Firefox()
	options = Options()
	options.headless = True
	driver = webdriver.Firefox(options = options)
	
	# Open the link
	driver.get(l)
	
	# Use visible text on screen to load all games 
	_flag = True
	while _flag:
		try:
			driver.find_element_by_xpath("//*[contains(text(), 'Show more matches')]").click()
			sleep(5)
			_flag = True
		except(ElementClickInterceptedException, ElementNotInteractableException):
			_flag = False
	sleep(5)
	
	# At this point all games on page re fully loaded
	# Next we get the id for each game 
	# We'll use this id's to build up the links to their respective stats pages
	wrap_ = driver.find_element_by_class_name("soccer")
	id_ = wrap_.find_elements(By.TAG_NAME, 'tr')
	# Create empty list to store id's
	_lst = list()
	# Loop through and print all id's 
	for _ in id_:
		__ = _.get_attribute("id")
		if len(__) > 5:
			_lst.append(__)
	
	driver.close()
	return _lst

# Next we will use the id's that we extracted to build up links 
def BuildLinks(_list):
  # The link we are trying to build is structured like this
  "https://www.flashscore.com/match/AyTNt38e/#match-summary"
  # Where the AyTNt38e is out id
  # And our extracted id looks something like 'g_1_lE6tbhNS'
  
  _lst = list()
  
  for _x in _list:
    _a = "https://www.flashscore.com/match/"+_x[4:]+"/match-summary"
    _lst.append(_a)
  return _lst


link1 = "https://www.flashscore.com/football/england/premier-league/"
_IDlist = getLinkID(link1)
for _ in _IDlist:
  print(_)
