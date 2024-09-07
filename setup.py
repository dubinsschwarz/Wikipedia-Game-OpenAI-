model_name = 'gpt-4o-mini'

#The code below sets up everything. Run the game by calling game().

import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By

import re

import os
import openai

#I use Microsoft Edge.
driver = webdriver.Edge()
driver.get('https://en.wikipedia.org/wiki/Main_Page')

def start():
    button = driver.find_element(By.XPATH, '//*[@id="vector-main-menu-dropdown-checkbox"]')
    button.click()
    link = driver.find_element(By.XPATH, '//*[@id="n-randompage"]/a/span')
    link.click()

def clean(string):
    return string.translate({ord(c): None for c in '()[];,.\n-"\'!@#$'})

from openai import OpenAI
client = OpenAI(api_key = os.getenv("OPENAI_API_KEY"))

def game():
    start()
    score = 0
    while driver.current_url != 'https://en.wikipedia.org/wiki/Jesus' and score < 50:
        
        raw_links = driver.find_elements(By.CSS_SELECTOR,"a[href ^= '/wiki/']")
        #the ^= doesn't seem to work with XPATH

        links = [link for link in raw_links if link.text not in ['Search', 'Article', 'Talk', 'Read', 'About Wikipedia', 'Disclaimers', '']]

        dict = {clean(link.text):link for link in links}

        title = driver.find_element(By.CSS_SELECTOR, "h1").text
        print(f'{model_name} is on the page: {title}')
        
        outstring = 'The current page is: ' + title + '\nThe available links are:\n' + '\n'.join(map(clean,list(dict.keys())))
        
        completion = client.chat.completions.create(
            model = model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi there, we're in the middle of a round of the Wikipedia game of 5 Clicks to Jesus."},
                {"role": "assistant", "content": "Am I the one playing?"},
                {"role": "user", "content": "Yes, exactly. I'll give you the name of the page we're currently on,\
                as well as a list of the available links. Think carefully about which one is likely to be the best to get to Jesus,\
                then give me the name of the link you think is the best."},
                {"role": "assistant", "content": "Got it! Do you need me to format my answer in any particular way?"},
                {"role": "user", "content": "Yes, please. Could you preface the name you pick with double dollars ('$$')\
                and not add any characters afterwards please? And feel free to think out loud. Thanks!"},
                {"role": "assistant", "content": "Okay, no problem. I'll make sure to do that. I'm ready."},
                {"role": "user", "content": "Glad to hear it! Here's the information. Good luck!" + outstring}
        
            ]
        )

        response = completion.choices[0].message.content
        print(response + '\n')
        
        key = re.findall(r'\$\$(.+)', response)[0]
        dict[key].click()
        
        score = score + 1
        
    print(f'{model_name} scored: ' + str(score))
