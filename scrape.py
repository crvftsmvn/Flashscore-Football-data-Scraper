from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementClickInterceptedException, ElementNotInteractableException, NoSuchElementException, TimeoutException, WebDriverException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import re
import pandas as pd

strike = 0
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
		_a = "https://www.flashscore.com/match/"+_x[4:]+"/#match-summary"
		_lst.append(_a)
	return _lst

# Get name of file we want to save to
def get_file_name(l):
	# Split string using '/' as delimeter
	str_list = l.split('/')
	
	# We will use country name + league name as file name
	# Because some countries share similar league names, so we don't confuse them

	file_name = str_list[-3] + "_"+str_list[-2]+".csv"
	file_name = file_name.replace("-", "_")
	#print(file_name)
	return file_name

# Get all the stats we want
def get_stat(l):
	global strike
	# First we define and initialize all variables
	_homeFHC = 0
	_awayFHC = 0
	_homeSHC = 0
	_awaySHC = 0
	
	homeFS = 0
	awayFS = 0
	homeSS = 0
	awaySS = 0
	
	_homeYCard = 0
	_awayYCard = 0
	_homeRCard = 0
	_awayRCard = 0
	
	_eearly = 0
	_early = 0
	
	# Run headless
	options = Options()
	options.headless=True
	try:
		driver = webdriver.Firefox(options = options)
		driver.get(l)
	except(WebDriverException):
		driver.close()
		get_stat(l)
		return None
	
	# Open the link
	#driver.get(l)
	wait = WebDriverWait(driver, 10)
	# Create a pandas dataframe
	_df = pd.DataFrame()
	
	sleep(2)
	
	# Get matchday
	_z = driver.find_element_by_class_name('fleft')
	_x = _z.find_element_by_xpath(".//*[contains(text(), 'Round')]")
	rnd = _x.text
	_rnd = re.findall('\d+', str(rnd))
	
	# Get HomeTeam
	_ht = driver.find_element_by_class_name('tname-home')
	ht = _ht.find_element_by_tag_name('a')
	_homeName = ht.text
	
	# Get AwayTeam
	_at = driver.find_element_by_class_name('tname-away')
	at = _at.find_element_by_tag_name('a')
	_awayName = at.text
	
	testHName = _homeName.strip()
	testAName = _awayName.strip()
	
	if testHName == "" or testAName == "":
		driver.close()
		get_stat(l)
		return None
	#print( _homeName, " VS ", _awayName)
	# Get scores for first half
	
	try:
		homeFS = driver.find_element_by_class_name('p1_home').text
		awayFS = driver.find_element_by_class_name('p1_away').text
		homeSS = driver.find_element_by_class_name('p2_home').text
		awaySS = driver.find_element_by_class_name('p2_away').text
	except(NoSuchElementException):
		driver.close()
		get_stat(l)
		return None
	
	# Check to see if page loads the statistics
	sleep(2)
	
	# Test to see if game has statistics available
	try:
		_testStats = driver.find_element_by_id('li-match-statistics')
		_testStats.click()
	except(NoSuchElementException):
		strike += 1
		if strike > 3:
			driver.close()
			return None
		else:
			driver.close()
			get_stat(l)
			return None

	# Check for yellow cards and red cards
	# Define variables to hold cards
	
	# Click on first half corner
	try:
		_a = wait.until(EC.presence_of_element_located((By.ID,"statistics-0-statistic")))
		_a.click()
	except(TimeoutException):
		driver.close()
		get_stat(l)
		return None
	sleep(2)
	# Search for yellow cards
	try:
		yCard = driver.find_element_by_xpath("//*[contains(text(), 'Yellow Cards')]")
		_parent = yCard.find_element_by_xpath("..")
		_homeYCard = _parent.find_element_by_class_name('statText--homeValue').text
		_awayYCard = _parent.find_element_by_class_name('statText--awayValue').text
	# Ignore Error if no card found on page
	except(NoSuchElementException):
		pass
	
	# Search for red cards
	try:
		rCard = driver.find_element_by_xpath("//*[contains(text(), 'Red Cards')]")
		_rParent = rCard.find_element_by_xpath("..")	# Go one up
		_homeRCard = _rParent.find_element_by_class_name('statText--homeValue').text
		_awayRCard = _rParent.find_element_by_class_name('statText--awayValue').text
	# Catch exceptions and ignore if no red card
	except(NoSuchElementException):
		pass

	sleep(2)
	# Click on first half corner
	try:
		_b = wait.until(EC.presence_of_element_located((By.ID,"statistics-1-statistic")))
		_b.click()
	except(TimeoutException):
		driver.close()
		get_stat(l)
		return None
	sleep(2)

	
	# Get teams first half corners
	try:
		_corners = driver.find_element_by_id("tab-statistics-1-statistic")
		_hoo = _corners.find_element_by_xpath(".//div[contains(text(), 'Corner Kicks')]")
		_parent = _hoo.find_element_by_xpath('..')
		_homeFHC = _parent.find_element_by_xpath(".//div[contains(@class, 'statText--homeValue')]").text
		_awayFHC = _parent.find_element_by_xpath(".//div[contains(@class, 'statText--awayValue')]").text
	except(NoSuchElementException):
		pass
	
	# Get teams second half corners
	try:
		_c = wait.until(EC.presence_of_element_located((By.ID, "statistics-2-statistic")))
		_c.click()
	except(TimeoutException):
		driver.close()
		get_stat(l)
		return None
		
	sleep(2)
	
	try:
		_c = driver.find_element_by_id("tab-statistics-2-statistic")
		_a = _c.find_element_by_xpath(".//div[contains(text(), 'Corner Kicks')]")
		_p = _a.find_element_by_xpath('..')
		_homeSHC = _p.find_element_by_xpath(".//div[contains(@class, 'statText--homeValue')]").text
		_awaySHC = _p.find_element_by_class_name('statText--awayValue').text
	except(NoSuchElementException):
		pass

	
	# Add data into dataframe
	_df['MD'] = _rnd
	_df['HomeTeam'] = _homeName
	_df['AwayTeam'] = _awayName
	_df['HTFHG'] = homeFS
	_df['AFHG'] = awayFS
	_df['HSHG'] = homeSS
	_df['ASHG'] = awaySS
	_df['HYellow'] = _homeYCard
	_df['AYellow'] = _awayYCard
	_df['HRed'] = _homeRCard
	_df['ARed'] = _awayRCard
	_df['HFHC'] = _homeFHC
	_df['AFHC'] = _awayFHC
	_df['HSHC'] = _homeSHC
	_df['ASHC'] = _awaySHC
	
	driver.close()
	return _df


link1 = "https://www.flashscore.com/football/ireland/premier-division/"
#_test = "https://www.flashscore.com/match/AyTNt38e/#match-summary"
#_test = "https://www.flashscore.com/match/nao50iz7/#match-summary"
#_test = "https://www.flashscore.com/match/ny3I9eDK/#match-summary"
fName = get_file_name(link1)
_IDlist = getLinkID(link1)
_l = BuildLinks(_IDlist)

# Create a DataFrame to save stats
df_ = pd.DataFrame()
for _ in _l:
	_tmp = get_stat(_)
	df_ = df_.append(_tmp, ignore_index=True)

df_.to_csv(fName)

