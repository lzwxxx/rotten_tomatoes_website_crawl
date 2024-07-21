import pandas as pd
import time

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from selenium.webdriver.common.by import By

#INITIALISE DATAFRAMES
df_reviews = pd.DataFrame(columns=['movie_title','critic_name','top_critic','publisher_name','review_type','review_score', 'review_date','review_content'])

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

#NAVIGATE TO TOP 100 MOVIES TAB
driver.get("https://www.rottentomatoes.com/browse/movies_at_home/sort:popular")

time.sleep(2)  

#retrieves movie name
movie_name = driver.find_elements(By.XPATH, '//a[@slot = "caption"]//span[@class = "p--small"]')
noOfMovies = len(movie_name)

NO_OF_MOVIES_INPUT = 30
NO_OF_COMMENTS_TO_BE_EXTRACTED = 5

NO_OF_MOVIES_INPUT = NO_OF_MOVIES_INPUT - 1
l = 0
numOfClicksForNextButton = 0

while (l < NO_OF_MOVIES_INPUT):
    
    track = l
    
    for l in range(track,noOfMovies):
        movie_title = movie_name[l].text
        
        #NAVIGATE TO DESCRIPTION OF A MOVIE
        selected_movie = driver.find_elements(By.XPATH, '//tile-dynamic[@isvideo = "true"]//a[@slot = "caption"]')
        driver.get(selected_movie[l].get_attribute("href"))

        #NAVIGATE TO ALL CRITICS REVIEW SECTION
        all_critics_link = driver.find_elements(By.XPATH, '//div[@class="links-wrap"]//a')
        driver.get(all_critics_link[0].get_attribute("href"))

        
        count = 0
        while count < NO_OF_COMMENTS_TO_BE_EXTRACTED:

            review_rows = driver.find_elements(By.XPATH, '//div[@class = "review-row"]')
            display_name_elements = driver.find_elements(By.XPATH, '//a[@class = "display-name"]')
            publication_elements = driver.find_elements(By.XPATH, '//a[@class = "publication"]')
            review_type_elements = driver.find_elements(By.XPATH, '//div[@class = "review-data"]//score-icon-critic')

            review_elements = driver.find_elements(By.XPATH, '//div[@class = "review-text-container"]//p[@class = "review-text"]')
            score_elements = driver.find_elements(By.XPATH, '//div[@class = "review-text-container"]//p[@class = "original-score-and-url"]')
            
            for r in range(0,len(review_rows)):
            # for r in range(0,count):
                display_name = "" 
                publication = "" 
                review_type = "" 
                review = ""
                date = ""
                score = "" 
                isCritic = ""

                count = count + 1
                display_name = display_name_elements[r].text
                publication = publication_elements[r].text
                review_type = review_type_elements[r].get_attribute("state")
                review = review_elements[r].text
                if("Original" in score_elements[r].text.split('|')[1]):
                    date = score_elements[r].text.split('|')[2].strip()
                    score = score_elements[r].text.split('|')[1].split(':')[1]
                    
                else:
                    date = score_elements[r].text.split('|')[1].strip()
                    score = ""

                isCritic = driver.find_elements(By.XPATH, '//div[@class = "reviewer-name-and-publication"]//rt-icon-top-critic[@class = "small"]//div[@class = "wrap"]//span')
                if(len(isCritic)==0):
                    isCritic = "False"
                else:
                    isCritic = "True"

                row = pd.Series([movie_title,display_name,isCritic,publication,review_type,score,date,review], index=df_reviews.columns)
                df_reviews = df_reviews.append(row,ignore_index=True)

                if (count == NO_OF_COMMENTS_TO_BE_EXTRACTED):
                    break
                
            try: 
                time.sleep(3)
                next_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//rt-button[@data-qa="next-btn"]')))
                # next_button = driver.find_element(By.XPATH, '//nav[@class = "prev-next-paging__wrapper"]//rt-button[@data-direction = "next"]')
                next_button.click()
                time.sleep(3)  
            except NoSuchElementException:
                break
            except TimeoutException:
                break
        

        driver.get("https://www.rottentomatoes.com/browse/movies_at_home/sort:popular")
        time.sleep(10)

        if(l == NO_OF_MOVIES_INPUT):
            break

        if numOfClicksForNextButton > 0:

            for i in range(0,numOfClicksForNextButton):
                try:
                    load_more_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="discovery__actions"]//button')))
                    load_more_btn.click()

                    time.sleep(3)
                    movie_name = driver.find_elements(By.XPATH, '//a[@slot = "caption"]//span[@class = "p--small"]')
                    noOfMovies = len(movie_name)
                    # print("New len")
                    # print(noOfMovies)

                except NoSuchElementException:
                    noOfMovies = 0
                except TimeoutException:
                    break

        if numOfClicksForNextButton == 0: 
            movie_name = driver.find_elements(By.XPATH, '//a[@slot = "caption"]//span[@class = "p--small"]')
            noOfMovies = len(movie_name)

    numOfClicksForNextButton =numOfClicksForNextButton  + 1
    if numOfClicksForNextButton > 0:

        for i in range(0,numOfClicksForNextButton):
            try:
                load_more_btn = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//div[@class="discovery__actions"]//button')))
                load_more_btn.click()

                time.sleep(3)
                movie_name = driver.find_elements(By.XPATH, '//a[@slot = "caption"]//span[@class = "p--small"]')
                noOfMovies = len(movie_name)
                print("New len")
                print(noOfMovies)

            except NoSuchElementException:
                noOfMovies = 0
            except TimeoutException:
                break
        
    
df_reviews = df_reviews.drop_duplicates()
df_reviews.to_csv('movie_reviews.csv',index=False)
