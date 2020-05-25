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
currentGames = unrefined.getColumn(1)

print('''Hello Ben, what would you like to accomplish today? \n
- Refine List: Type 'refine'
- Manual Add: Type 'add'
- IGDB Scrape: Type 'igdb'
- Update Genre + System Elements: Type 'static'
- Update Playtime : Type 'play'
- Update Youtube Trailer: Type 'tube'
- Update Reddit Stats: Type 'reddit'
- Update Dynamic Elements: Type 'dynamic''')

answer = input('> ')

if answer == 'refine':
    refine(unrefined, refined)



#if answer == 'add':

if answer == 'twitch':
    ss.refresh()
    rows = refined.getRows()
    browser = webdriver.Chrome()
    delay = 2
    for row in rows:
        if row[8] == '':
            print(' grabbing ' + row[0] + "'s twitch followers.")
            row[8] = updateTwitch( row[0], browser, delay)
            sheetrow = rows.index(row)
            sheetrow += 1
            refined.updateRow(sheetrow, row)


if answer == 'igdb':
    skip = input('how many should we skip?')
    ss.refresh()
    rows = unrefined.getRows() 
    browser = webdriver.Chrome()
    delay = 20
    newGames = igdbScrape(browser, delay, ss, skip)

if answer == 'static':
    print("Okay, let's fill out the initial information")
    print('...')
    ss.refresh()
    rows = un.getRows() 
    browser = webdriver.Chrome()
    delay = 20
    for row in rows[1:]:
        if row[1] == '':
            row[1] = updateGenre(row[0], browser, delay)
            row[9] = updateSystems(browser)
            print(row)
            sheetrow = rows.index(row)
            sheet.updateRow(sheetrow, row)

if answer == 'tube':
    print("Okay, let's find a trailer")
    print('...')
    ss.refresh()
    rows = refined.getRows() 
    browser = webdriver.Chrome()
    delay = 20
    for row in rows:
        if row[2] == '':
            row[2] = updateTrailer(row[0], browser, delay)
            print(row)
            sheetrow = rows.index(row)
            sheetrow += 1
            refined.updateRow(sheetrow, row)
            
if answer == 'play':
    print("Okay, let's get those playtimes.")
    print('...')
    ss.refresh()
    rows = refined.getRows() 
    browser = webdriver.Chrome()
    delay = 3
    for row in rows:
        if row[3] == '' or row[3] == '-':
            row[3] = updatePlaytime(row[0], browser, delay)
            print(row)
            sheetrow = rows.index(row)
            sheetrow += 1
            refined.updateRow(sheetrow, row)
            

if answer == 'reddit':
    ss.refresh()
    rows = refined.getRows()
    browser = webdriver.Chrome()
    delay = 2
    for row in rows:
        if row[5] == '':
            print('Updating ' + row[0] + "'s reddit stats.")
            row[5], row[4] = updateRedditStats(row[0], row[4], browser, delay)
            sheetrow = rows.index(row)
            sheetrow += 1
            refined.updateRow(sheetrow, row)

if answer == 'tubestats':
    ss.refresh()
    rows = refined.getRows()
    browser = webdriver.Chrome()
    delay = 2
    for row in rows:
        if row[6] == '':
            print(' grabbing ' + row[0] + "'s youtube stats.")
            row[6] = updateTubeStats( row[0], browser, delay)
            sheetrow = rows.index(row)
            sheetrow += 1
            refined.updateRow(sheetrow, row)

if answer == 'price':
    ss.refresh()
    rows = refined.getRows()
    browser = webdriver.Chrome()
    delay = 6
    for row in rows:
        if row[7] == '' or row[7] == 'unknown':
            print(' grabbing ' + row[0] + "'s price.")
            row[7] = updatePrice( row[0], browser, delay)
            sheetrow = rows.index(row)
            sheetrow += 1
            refined.updateRow(sheetrow, row)

if answer == 'finalscore':
    ss.refresh()
    finalScore(refined)

    

    
    #TODO updatPrice

    #TODO updateKeywords 

