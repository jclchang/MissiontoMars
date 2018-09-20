
# Dependencies
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
from bs4 import BeautifulSoup
import requests
import time
import pandas as pd


def scrape():

	# Include Chrome Web Driver path 
	executable_path = {'executable_path': 'chromedriver.exe'}
	browser = Browser('chrome', **executable_path, headless=False)

	#############################################
	### Scrape NASA Mars News

	newsurl = 'https://mars.nasa.gov/news/'
	browser.visit(newsurl)

	# HTML object
	html = browser.html

	# Parse HTML with Beautiful Soup
	soup = BeautifulSoup(html, 'html.parser')

	# Retrieve the first <li> which contain the latest news
	MarsArticles = soup.find_all('li', {"class":"slide"})[0]

	# title is in the <div class="content_title"> tag
	news_title = MarsArticles.find('div', class_='content_title').text
	# news paragraph is in <div class="article_teaser_body"> tag
	news_p = MarsArticles.find('div', class_='article_teaser_body').text

	#print (news_title)
	#print (news_p)

	#############################################
	### Scrape JPL Mars Space Images

	image_url = "https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars"
	browser.visit(image_url)

	# click on "FULL IMAGE" button - this take you to a page with just the medium size jpg
	browser.click_link_by_partial_text('FULL IMAGE')

	# doesn't work without sleep in between
	time.sleep(20)

	# Click on the "more info" button to get to a page with large jpg
	browser.click_link_by_partial_text('more info')

	# HTML object
	image_html = browser.html
	# Parse HTML with Beautiful Soup
	soup = BeautifulSoup(image_html, 'html.parser')

	# image path is in <figure class="lede">
	# <a href="/spaceimages/images/largesize/PIA11777_hires.jpg"><img alt="This impact crater, as seen by NASA's Mars Reconnaissance Orbiter, appears relatively recent as it has a sharp rim and well-preserved ejecta." title="This impact crater, as seen by NASA's Mars Reconnaissance Orbiter, appears relatively recent as it has a sharp rim and well-preserved ejecta." class="main_image" src="/spaceimages/images/largesize/PIA11777_hires.jpg"></a>
	# </figure>
	image_path = soup.find('figure', class_='lede').a['href']
	featured_image_url = "https://www.jpl.nasa.gov/" + image_path

	#print (featured_image_url)

	#############################################
	###  Scrape Twitter for Mars Weather 

	weather_url = "https://twitter.com/marswxreport?lang=en"
	browser.visit(weather_url)

	# HTML object
	weather_html = browser.html
	# Parse HTML with Beautiful Soup
	soup = BeautifulSoup(weather_html, 'html.parser')

	# the latest weather is in 
	#   <p class="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text" lang="en" data-aria-label-part="0">
	#       Sol 2171 (2018-09-14), high -12C/10F, low -65C/-84F, pressure at 8.79 hPa, daylight 05:43-17:59</p>

	mars_weather = soup.find_all('p', {"class":"TweetTextSize"})[0].text

	#print (mars_weather)

	#############################################
	### Scrape Mars Facts 

	fact_url = "http://space-facts.com/mars/"

	# read table into a list
	fact_list = pd.read_html(fact_url)
	#fact_list
	#type(fact_list)

	# convert list to a DataFrame
	fact_df = fact_list[0]
	#type(fact_df)
	#fact_df

	fact_df.columns = ["Description", "Value"]
	#fact_df

	# Set the index to the State column
	fact_df.set_index('Description', inplace=True)
	#fact_df

	# Convert DataFrame to a html table
	fact_html_table = fact_df.to_html()
	#fact_html_table


	#############################################
	##  Scrape USGS for Mars Hemispheres images

	usgs_url = "https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars"
	browser.visit(usgs_url)
	usgs_html = browser.html
	soup = BeautifulSoup(usgs_html, "html.parser")

	# the link to each picture is in 
	# <a href="/search/map/Mars/Viking/cerberus_enhanced" class="itemLink product-item"><h3>Cerberus Hemisphere Enhanced</h3></a>
	# and there are 4 links on the page
	# this does not work - sgsImgLinks = soup.find_all('a', class_="itemLink") - because there are two sets of these for each image
	usgsImgLinks = soup.find_all('div', class_="description")

	hemisphere_image_urls = []

	for usgsImgLink in usgsImgLinks:
		title = usgsImgLink.h3.text
		img_url = "https://astrogeology.usgs.gov" + usgsImgLink.a['href']
		#print (title)
		#print (img_url)
		
		####  new
		browser.visit(img_url)
		fullUsgs_html = browser.html
		Imgsoup = BeautifulSoup(fullUsgs_html, "html.parser") 
    
		#full image link is in <img class="wide-image" src="/cache/images/cfa62af2557222a02478f1fcd781d445_cerberus_enhanced.tif_full.jpg">
		fullImgLink = "https://astrogeology.usgs.gov" +  Imgsoup.find('img',class_ ="wide-image" )['src']
		#print (fullImgLink)
    
		#### end new
		
		# add title and image url to a dictionary, then add the dictionary to the list
		image_dict = {}
		image_dict['title'] = title
		image_dict['img_url'] = fullImgLink
			
		hemisphere_image_urls.append(image_dict)
			
	#hemisphere_image_urls

	#############################################
	# put all results into a dictionary
	marsInfo_dict = {
			"news_title": news_title,
			"news_p": news_p,
			"featured_image_url": featured_image_url,
			"mars_weather": mars_weather,
			"fact_table": fact_html_table,
			"hemisphere_image_urls": hemisphere_image_urls
		}

	print(marsInfo_dict)
	
	return marsInfo_dict
	
