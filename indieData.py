#! python3

from indiefunctions import *
import ezsheets
import pyperclip
import sys
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import time

ss = ezsheets.Spreadsheet('1EAhyX8g8YeCwqKwgCWJk5n70CC3mqH8C-i8ocy9gVRc')
Clipboard = pyperclip.paste()
refined = ss[0]
unrefined = ss[1]
newGamesSheet = ss[4]
currentGames = unrefined.getColumn(1)


print(''' Hello Ben, what would you like to accomplish today? \n
- Add games: Type 'ADD'
- Handle unrefined list: Type 'UNREFINED'
- Update refined list: Type 'REFINED' ''')

tree = input('> ')

if tree == 'ADD':
    print(''' Would you like to 'manual' add, 'download', or 'scrape'?''')
    select = input('> ')
    if select == 'manual':
        newGamesList = manualAdd
        listUpdate(unrefined, refined, newGamesList)
    elif select == 'download':
        unrefinedList = unrefined.getColumn(1)
        refinedList = refined.getColumn(1)
        newGamesList = newGamesSheet.getColumn(1)
        newGameslist = listUpdate(unrefinedList, refinedList, newGamesList, unrefined) 
        newGamesSheet.updateColumn(1, newGameslist)
    elif select == 'scrape':
        skip = input('how many should we skip?')
        ss.refresh()
        rows = unrefined.getRows() 
        browser = webdriver.Chrome()
        delay = 2
        newGames = igdbScrape(browser, delay, ss, skip)
elif tree == 'UNREFINED':
    print(''' Would you like to 'fill' in info, 'update' info, or 'refine'?''')
    select = input('> ')
    if select == 'fill':
        print("Okay, let's fill out the initial information")
        print('...')
        ss.refresh()
        rows = unrefined.getRows() 
        browser = webdriver.Chrome()
        delay = 1
        for row in rows[1:]:
            if row[1] == '':
                row[1] = updateGenre(row[0], browser, delay)
            if row[9] == '':
                row[9] = updateSystems(browser)
            sheetrow = rows.index(row)
            sheetrow += 1
            unrefined.updateRow(sheetrow, row)
    elif select == 'update':
        print("Okay, let's update the genre and systems")
        print('...')
        ss.refresh()
        rows = unrefined.getRows() 
        browser = webdriver.Chrome()
        delay = .5
        skip = int(input('how many rows should we skip? > '))
        for row in rows[skip:]:
            row[1] = updateGenre(row[0], browser, delay)
            row[9] = updateSystems(browser)
            sheetrow = rows.index(row)
            sheetrow += 1
            unrefined.updateRow(sheetrow, row)
    elif select == 'refine':
        refine(unrefined, refined)
elif tree == 'REFINED':
    print(''' Would you like to 'fill' in info, 'update' info, or 'tally'? ''')
    select = input('> ')
    if select == 'fill':
        print(''' What would you like to fill?
        - 'twitch'
        - 'playtime'
        - 'views'
        - 'reddit'
        - 'price'
        - 'trailer'
        ''')
        selectTwo = input('> ')
        if selectTwo == 'twitch':
            answer = 'reFillTwtich'
            ss.refresh()
            rows = refined.getRows()
            browser = webdriver.Chrome()
            delay = 2
            for row in rows[1:]:
                if row[8] == '':
                    print(' grabbing ' + row[0] + "'s twitch followers.")
                    row[8] = updateTwitch( row[0], browser, delay)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
        if selectTwo == 'playtime':
            print("Okay, let's get those playtimes.")
            print('...')
            ss.refresh()
            rows = refined.getRows() 
            browser = webdriver.Chrome()
            delay = 3
            for row in rows [1:]:
                if row[3] == '':
                    row[3] = updatePlaytime(row[0], browser, delay)
                    print(row)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
        if selectTwo == 'views':
            ss.refresh()
            rows = refined.getRows()
            browser = webdriver.Chrome()
            delay = 10
            for row in rows[1:]:
                if row[6] == '' or row[6] == '-':
                    print(' grabbing ' + row[0] + "'s youtube stats.")
                    row[6] = updateTubeStats( row[0], browser, delay)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
        if selectTwo == 'reddit':
            ss.refresh()
            rows = refined.getRows()
            browser = webdriver.Chrome()
            delay = 2
            for row in rows[1:]:
                if row[5] == '':
                    print('Updating ' + row[0] + "'s reddit stats.")
                    row[5], row[4] = updateRedditStats(row[0], row[4], browser, delay)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
        if selectTwo == 'price':
            ss.refresh()
            rows = refined.getRows()
            browser = webdriver.Chrome()
            delay = 6
            for row in rows[1:]:
                if row[7] == '' or row[7] == 'unknown':
                    print(' grabbing ' + row[0] + "'s price.")
                    row[7] = updatePrice( row[0], browser, delay)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
        if selectTwo == 'trailer':
            print("Okay, let's find a trailer")
            print('...')
            ss.refresh()
            rows = refined.getRows() 
            browser = webdriver.Chrome()
            delay = 2
            for row in rows[1:]:
                if row[2] == '':
                    row[2] = updateTrailer(row[0], browser, delay)
                    print(row)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
    elif select == 'update':
        print(''' What would you like to update?
        - 'twitch'
        - 'playtime'
        - 'views'
        - 'reddit'
        - 'price'
        - 'trailer'
        ''')
        selectTwo = input('> ')
        if selectTwo == 'twitch':
            ss.refresh()
            rows = refined.getRows()
            browser = webdriver.Chrome()
            delay = 2
            for row in rows[1:]:
                print(' grabbing ' + row[0] + "'s twitch followers.")
                row[8] = updateTwitch( row[0], browser, delay)
                sheetrow = rows.index(row)
                sheetrow += 1
                refined.updateRow(sheetrow, row)
        if selectTwo == 'playtime':
            print("Okay, let's get those playtimes.")
            print('...')
            ss.refresh()
            rows = refined.getRows() 
            browser = webdriver.Chrome()
            delay = 3
            for row in rows[1:]:
                    row[3] = updatePlaytime(row[0], browser, delay)
                    print(row)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
        if selectTwo == 'views':
            ss.refresh()
            rows = refined.getRows()
            browser = webdriver.Chrome()
            delay = 2
            for row in rows[1:]:
                    print(' grabbing ' + row[0] + "'s youtube stats.")
                    row[6] = updateTubeStats( row[0], browser, delay)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
        if selectTwo == 'reddit':
            ss.refresh()
            rows = refined.getRows()
            browser = webdriver.Chrome()
            delay = 2
            for row in rows[1:]:
                print('Updating ' + row[0] + "'s reddit stats.")
                row[5], row[4] = updateRedditStats(row[0], row[4], browser, delay)
                sheetrow = rows.index(row)
                sheetrow += 1
                refined.updateRow(sheetrow, row)
        if selectTwo == 'price':
            ss.refresh()
            rows = refined.getRows()
            browser = webdriver.Chrome()
            delay = 6
            for row in rows[1:]:
                if row[7] == '' or row[7] == 'unknown':
                    print(' grabbing ' + row[0] + "'s price.")
                    row[7] = updatePrice( row[0], browser, delay)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
        if selectTwo == 'trailer':
            print("Okay, let's find a trailer")
            print('...')
            ss.refresh()
            rows = refined.getRows() 
            browser = webdriver.Chrome()
            delay = 2
            for row in rows[1:]:
                    row[2] = updateTrailer(row[0], browser, delay)
                    print(row)
                    sheetrow = rows.index(row)
                    sheetrow += 1
                    refined.updateRow(sheetrow, row)
    elif select == 'tally':
        ss.refresh()
        finalScore(refined)