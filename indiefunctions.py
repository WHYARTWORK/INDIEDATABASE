#! python3

# Get current list of indie games, append new list if not in list

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
import ezsheets
import pyperclip
import sys
import time
import requests
import bs4
import lxml
import re
import urllib

def updateTwitch(gameTitle, browser, delay):
    gameTitlere = urllib.parse.quote(gameTitle)
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException)
    browser.get('https://twitch.tv/directory/game/' + gameTitlere)
    try:
        followers = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.XPATH, '''//*[@id="root"]
                        /div/div[2]/div/main/div[1]/div[3]/div/div/div/div[1]/div[2]/div/div
                        [2]/div[2]/div[3]/p/strong'''))).text
        if 'K' in followers:
            followers = re.sub(r'[^0-9.]+', '', followers)
            followers = float(followers)*1000
            return(followers)
        elif 'M' in followers:
            followers = re.sub(r'[^0-9.]+', '', followers)
            followers = float(followers)*1000000
        else:
            return(float(followers))
    except TimeoutException:
        try:
            followers = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                            .until(EC.presence_of_element_located((By.XPATH, '''//*[@id="root"]/div/
                            div[2]/div/main/div[1]/div[3]/div/div/div/div[1]/div[2]/div/div[2]/div[2]
                            /div[1]/p/strong'''))).text
            if 'K' in followers:
                followers = re.sub(r'[^0-9.]+', '', followers)
                followers = float(followers)*1000
                return(followers)
            else:
                return(float(followers))
        except TimeoutException:
            return('-')

def refine(unrefined, refined):
    rowsOne = unrefined.getRows()
    rowsTwo = refined.getRows()
    for row in rowsOne:
        if 'Nintendo Switch' in row[9]:
            rowsTwo.append(row)
            rowsOne.remove(row)
        elif 'PlayStation 4' in row[9]:
            rowsTwo.append(row)
            rowsOne.remove(row)
        elif 'PlayStation Network' in row[9]:
            rowsTwo.append(row)
            rowsOne.remove(row)
    unrefined.updateRows(rowsOne)
    refined.updateRows(rowsTwo)
            
def manualAdd():
    newGameList = []
    print('''Okay, let's add some games. Type the name of the game and press 'enter' or type 'q' to
    quit''')
    while True:
        game = input(''> '')
        if game == 'q':
            break
        else:
            newGameList.append(game)
    return(newGameList)


def igdbPage(browser, delay):
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException,)
    pageTitles = []
    for i in range(10):
        try:
            xpath = '//*[@id="content-page"]/div/div/div/div/div['+ str(i+2) +']/div[2]/a'
            title = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                            .until(EC.presence_of_element_located((By.XPATH, '''xpath'''))).text
            pageTitles.append(title)                
        except StaleElementReferenceException:
            title = 'e'
            pageTitles.append(title)
        except TimeoutException:
            title = 'e'
            pageTitles.append(title)
    return(pageTitles)

def igdbScrape(browser, delay, ss, skip):
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException )
    browser.get('https://igdb.com/genres/indie')
    pgSkip = int(skip) / 10
    for i in range(int(pgSkip)):
        next = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.CLASS_NAME, 'next ')))
        browser.execute_script("arguments[0].click();", next)
        time.sleep(.5)
    titles = []
    ss.refresh()
    unrefined = ss[0]
    currentGames = unrefined.getColumn(1)
    while True:
        newtitles = igdbPage(browser, delay)
        listUpdate(currentGames, newtitles, unrefined)
        try:
            next = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.CLASS_NAME, 'next ')))
            browser.execute_script("arguments[0].click();", next)
        except TimeoutException:
            break
    return(titles)

def updatePrice(gameTitle, browser, delay):
    try:
        article, wordmatch, *nomatch = gameTitle.split(' ')
    except ValueError:
        wordmatch, *nomatch = gameTitle.split()
    price = '-'
    gameTitlere = urllib.parse.quote(gameTitle)
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException)
    browser.get('https://store.playstation.com/en-us/grid/search-game/1?query=' + gameTitlere)
    try:
        priceRaw = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.CLASS_NAME, 'price-display__price'))).text
        print(priceRaw)
        price = re.sub(r'[^0-9.]+', '', priceRaw)
        print(price)
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass
    browser.get('https://nintendo.com/search/#category=all&page=1&query=' + gameTitlere)
    try:
        title = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                                .until(EC.presence_of_element_located((By.CLASS_NAME,'title')))
        browser.execute_script("arguments[0].click();", title)
        url = browser.current_url
        if wordmatch.lower() not in url.lower():
            pass
        else:
            WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                .until(EC.text_to_be_present_in_element((By.XPATH,'//*[@id="purchase-options"]/div[1]/span[1]'), '$'))
            nintendoPrice = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                .until(EC.presence_of_element_located((By.XPATH,'//*[@id="purchase-options"]/div[1]/span[1]'))).text
            nintendoPrice = re.sub(r'[^0-9.]+', '', nintendoPrice)
            if price == 'unknown' or nintendoPrice < price:
                price = nintendoPrice
                return(price)
    except TimeoutException:
        try:
            WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                .until(EC.text_to_be_present_in_element((By.XPATH,'//*[@id="purchase-options"]/div[1]/span[1]'), '$'))
            nintendoPrice = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                .until(EC.presence_of_element_located((By.XPATH,'//*[@id="purchase-options"]/div[1]/span[1]'))).text
            nintendoPrice = re.sub(r'[^0-9.]+', '', nintendoPrice)
            if price == 'unknown' or nintendoPrice < price:
                price = nintendoPrice
                return(price)
        except TimeoutException:
            pass
    return(price)

def listUpdate(unrefinedlist, refinedlist, newGameslist, unrefined):
    for i in newGameslist:
        if i not in unrefinedlist and i not in refinedlist:
            unrefinedlist.append(i)
            newGameslist.remove(i)
    unrefined.updateColumn(1, unrefinedlist)
    return(newGameslist)


def updateGenre(gameTitle, browser, delay):
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException,)
    gameTitle = re.sub(r'[^A-Za-z0-9 ]+', '', gameTitle)
    gameTitle = gameTitle.replace(' ','-').lower()
    browser.get('https://igdb.com/games/' + gameTitle)
    finalgenre = ''
    for i in range(10):
        try:
            xpath = '//*[@id="content-page"]/div[1]/div/div[2]/div[2]/div[2]/div[2]/p[1]/a[' + str(i) + ']'
            genre = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                            .until(EC.presence_of_element_located((By.XPATH, xpath))).text
            finalgenre += ' '
            finalgenre += genre
            print(finalgenre)
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
        except TimeoutException:
            pass
    return(finalgenre)

def updateSystems(browser):
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException,)
    finalSystems = ''
    for i in range(10):
        try:
            xpath = '//*[@id="content-page"]/div[1]/div/div[2]/div[2]/div[2]/div[2]/p[2]/a[' + str(i) + ']'
            system = browser.find_element_by_xpath(xpath).text
            finalSystems += ' ' + system
            print(finalSystems)
        except NoSuchElementException:
            pass
        except StaleElementReferenceException:
            pass
    print(finalSystems)
    return(finalSystems)

def updateTrailer(gameTitle, browser, delay):
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException)
    gameTitle = re.sub(r'[^A-Za-z0-9 ]+', '', gameTitle)
    gameTitle = gameTitle.replace(' ','-').lower()
    browser.get('https://youtube.com/results?search_query=' + gameTitle + '+trailer')
    title = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.XPATH, '''//*[@id="video-title"]
                        /yt-formatted-string''')))
    title.click()
    time.sleep(.5)
    return(browser.current_url)

def updatePlaytime(gameTitle, browser, delay):
    ignored_exceptions = (NoSuchElementException, StaleElementReferenceException)
    browser.get('https://www.howlongtobeat.com')
    elem = browser.find_element_by_name('global_search_box')
    elem.click()
    elem.send_keys(gameTitle)
    try:
        WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                    .until(EC.text_to_be_present_in_element((By.XPATH, '''//*[@id="global_search_content"]/h3'''), gameTitle))
        elem2 = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                            .until(EC.presence_of_element_located((By.XPATH, '''/html/body/div[1]/form
                            /div[5]/div/div/div[6]/div/ul/li/div[2]/h3/a''')))
        elem2.click() 
        elem3 = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                            .until(EC.presence_of_element_located((By.XPATH, '''//*[@id="global_site"]
                            /div[2]/div/div[2]/div[1]/ul/li[2]/div'''))).text
        if '-' in elem3:
            elem3 = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                            .until(EC.presence_of_element_located((By.XPATH, '''//*[@id="global_site"]/div[2]
                            /div/div[2]/div[1]/ul/li[1]/div'''))).text
        play = re.sub(r'[^0-9½]+', '', elem3)
        play = play.replace('½','.5')
    except TimeoutException:
        return('-')
    except StaleElementReferenceException:
        return('-')
    return(play)

def updateTubeStats(gameTitle, browser, delay):
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException,)
    gameTitle = re.sub(r'[^A-Za-z0-9 ]+', '', gameTitle)
    gameTitle = gameTitle.replace(' ','-').lower()
    browser.get("https://youtube.com/results?search_query=Let%27s+Play+" + gameTitle)
    try:
        title = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                            .until(EC.presence_of_element_located((By.XPATH, '''/html/body/ytd-app/div/
                            ytd-page-manager/ytd-search/div[1]/ytd-two-column-search-results-renderer/
                            div/ytd-section-list-renderer/div[2]/ytd-item-section-renderer/div[3]/
                            ytd-video-renderer[11]/div[1]/div/div[1]/div/h3/a''')))
    except TimeoutException:
        return('-')
    title = title.get_attribute('aria-label')
    try:
        views = title.split('second', 1)[1]
    except IndexError:
        try:
            views = title.split('minute', 1)[1]
        except IndexError:
            views = title.split('hour', 1)[1]
    if 'K' in views:
        viewsNumber = re.sub(r'[^0-9]+', '', views)
        viewsNumber = float(viewsNumber) * 1000
    else:
        viewsNumber = re.sub(r'[^0-9]+', '', views)
    return(viewsNumber)



def updateRedditStats(gameTitle, redditTitle, browser, delay):
    try:
        article, wordmatch, *nomatch = gameTitle.split(' ')
    except ValueError:
        wordmatch, *nomatch = gameTitle.split()
    googleSub = '-'
    ignored_exceptions = (NoSuchElementException,StaleElementReferenceException,)
    gameTitlere = re.sub(r'[^A-Za-z0-9 ]+', '', gameTitle)
    gameTitlere = gameTitle.replace(' ','').lower()
    browser.get('https://subredditstats.com/r/' + gameTitlere)
    try:
        sub = WebDriverWait(browser, delay ,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.XPATH, '''/html/body/pre'''))).text
        if 'requests' in sub:
            sys.exit('timed out subredditstats')
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass
    try:
        sub = WebDriverWait(browser, delay ,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.XPATH, '''/html/body/div[3]/
                        div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[1]'''))).text
    except TimeoutException:
        browser.get('https://google.com/search?q=' + gameTitle + '+reddit')
        try:
            googleSub = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.XPATH, '''//*[@id="rso"]/div[1]/div/div[1]/a/div/cite'''))).text
            googleSub = googleSub.split(' › ',2)[1]
            if wordmatch not in googleSub:
                return('-', "right sub?  -" + googleSub)
            browser.get('https://subredditstats.com/r/' + googleSub)
            try:
                sub = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.XPATH, '''/html/body/div[3]
                        /div[2]/div[1]/div/div[1]/table/tbody/tr[2]/td[1]'''))).text
            except TimeoutException:
                return( "-", "right sub?  -" + googleSub)
        except TimeoutException:
            return('-', "right sub?  -" + googleSub)
    try:
        comment = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.XPATH, '''/html/body/div[3]
                        /div[2]/div[1]/div/div[2]/table/tbody/tr[2]/td[1]'''))).text
    except TimeoutException:
        comment = 0
        pass
    try:
        post = WebDriverWait(browser, delay,ignored_exceptions=ignored_exceptions)\
                        .until(EC.presence_of_element_located((By.XPATH, '''/html/body/div[3]
                        /div[2]/div[1]/div/div[3]/table/tbody/tr[2]/td[1]'''))).text
    except TimeoutException:
        post = 0
        pass
    if sub != 0:
        sub = float(sub.replace(',',''))
    if comment != 0:
        comment = float(comment.replace(',',''))
    if post != 0:
        post = float(post.replace(',',''))
    if post != 0 and comment !=0:
        finalScore = ((comment/post)*sub)
    else:
        finalScore = 0
    print(finalScore, googleSub)
    return(finalScore, googleSub)

def finalScore(refined):
    finalScore = 0
    rows = refined.getRows()
    for row in rows[1:]:
        if row[0] != '':
        # Playtime Score
            if row[3] == '-' or row[3] == '':
                finalScore = 0
            elif float(row[3]) >= 8 and  float(row[3]) <= 20:
                finalScore = 35
            elif float(row[3]) > 20 and float(row[3]) <= 25:
                finalScore = 20
            elif float(row[3]) > 25 and float(row[3]) <= 30:
                finalScore = 10
            elif float(row[3]) > 30 and float(row[3]) <= 40:
                finalScore = 5
            elif float(row[3]) > 40:
                finalScore = 0
            elif float(row[3]) >= 4 and float(row[3]) < 8:
                finalScore = 20
            elif float(row[3]) < 4:
                finalScore = 15
            # Price Score
            if row[7] == '-' or row[7] == '':
                finalScore += 0
            elif float(row[7]) < 10:
                finalScore += 10
            # Price/Hr Score
            if row[7] == '-' or row[7] == '':
                finalScore += 0
            elif row[3] == '-' or row [3] == '':
                finalScore += 0
            else:
                hourPrice = float(row[7])/float(row[3])
                if hourPrice <= .50:
                    finalScore += 20
                elif hourPrice > .50 and hourPrice <= .75:
                    finalScore += 15
                elif hourPrice > .75 and hourPrice <= 1.00:
                    finalScore += 10
                elif hourPrice > 1.00 and hourPrice <= 1.25:
                    finalScore += 5
                elif hourPrice > 1.25:
                    finalScore += 0
            # twitchScore
            if row[8] == 'unknown' or row[8] == '-' or row[8] == '':
                finalScore += 0
            elif float(row[8]) <= 500:
                finalScore += 3
            elif float(row[8]) > 500 and float(row[8]) <= 1000:
                finalScore += 6
            elif float(row[8]) > 1000 and float(row[8]) <= 10000:
                finalScore += 9
            elif float(row[8]) > 10000 and float(row[8]) <= 20000:
                finalScore += 12
            elif float(row[8]) > 20000:
                finalScore += 15
            #redditstats
            if row[5] == '-' or row[5] == '':
                finalScore += 0
            elif float(row[5]) <= 100:
                finalScore += 2
            elif float(row[5]) > 100 and float(row[5]) <= 500:
                finalScore += 4
            elif float(row[5]) > 500 and float(row[5]) <= 1000:
                finalScore += 6
            elif float(row[5]) > 1000 and float(row[5]) <= 5000:
                finalScore += 8
            elif float(row[5]) > 5000:
                finalScore += 10
            #tubestats
            if row[6] == '-' or row [6] == '':
                finalScore += 0
            elif float(row[6]) <=100:
                finalScore += 16
            elif float(row[6]) > 100 and float(row[6]) <= 500:
                finalScore += 20
            elif float(row[6]) > 500 and float(row[6]) <= 1000:
                finalScore += 12
            elif float(row[6]) > 1000 and float(row[6]) <= 5000:
                finalScore += 8
            elif float(row[6]) > 5000:
                finalScore += 4
        row[10] = finalScore
        print(finalScore)
    refined.updateRows(rows)


    