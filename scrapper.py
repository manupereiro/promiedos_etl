import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import numpy as np

def get_tournament_name(tournament):
    """
    Obtain the name of the tournament from the tournament div.
    param tournament: BeautifulSoup object
    return: str
    """
    return tournament.find("a", class_="event-header_left__q8kgh").text

def get_local_team(tournament):
    """
    Obtain the local team from the tournament div.
    param tournament: BeautifulSoup object
    return: list of str
    """
    return [team.find("span").text for team in tournament.find_all("div", class_="team_block__BYWWw team_left__S_a4n")]

def get_visitor_team(tournament):
    """
    Obtain the visitor team from the tournament div.
    param tournament: BeautifulSoup object
    return: list of str
    """
    return [team.find("span").text for team in tournament.find_all("div", class_="team_block__BYWWw team_right__ePX7C")]

def penalties_check(div_check):
    """
    Check if the match went to penalties.
    param div_check: BeautifulSoup object
    return: bool
    """
    return div_check.find("span", class_="penalties_score__rF_Gk") is not None

def get_local_score(tournament):
    """
    Obtain the local score from the tournament div.
    param tournament: BeautifulSoup object
    return: list of str
    """
    scores = tournament.find_all("span", class_="scores_scoreseventresult__X_Y_1")
    if not scores:
        return []
    if penalties_check(tournament.find("div", class_="result_block__8wTEO")):
        penalties = tournament.find_all("span", class_="penalties_score__rF_Gk")
        return [f"{scores[i].text} {penalties[0].text}" for i in range(len(scores)) if i % 2 == 0]
    else:
        return [scores[i].text for i in range(len(scores)) if i % 2 == 0]

def get_visitor_score(tournament):
    """
    Obtain the visitor score from the tournament div.
    param tournament: BeautifulSoup object
    return list of str
    """
    scores = tournament.find_all("span", class_="scores_scoreseventresult__X_Y_1")
    if not scores:
        return []
    if penalties_check(tournament.find("div", class_="result_block__8wTEO")):
        penalties = tournament.find_all("span", class_="penalties_score__rF_Gk")
        return [f"{scores[i].text} {penalties[1].text}" for i in range(len(scores)) if i % 2 != 0]
    else:
        return [scores[i].text for i in range(len(scores)) if i % 2 != 0] 

def get_local_scorers(tournament):
    """
    Obtain the local scorers from the tournament div.
    param tournament: BeautifulSoup object
    return: list of list of str
    """
    left_scorers = tournament.find_all("div", class_="gols_itemLeft__qNNDP")
    # If there are no elements, return an empty list for the 0-0 match
    if not left_scorers:
        return []
    
    scorers = []
    for scorer in left_scorers:
        scorers_aux = scorer.find_all("span", class_="gols_block__uW5yg")
        list_aux = []
        for span in scorers_aux:
            if span.p:
                list_aux.append(span.p.text.replace(";", ""))
        scorers.append(list_aux)
    
    # If all elements are empty lists, an empty list is returned instead of a list of empty lists.
    # This is done to avoid having a list of empty lists when there are no scorers.
    if all(len(s) == 0 for s in scorers):
        return []
    
    return scorers

def get_visitor_scorers(tournament):
    """
    Obtain the visitor scorers from the tournament div.
    param tournament: BeautifulSoup object
    return: list of list of str
    """
    right_scorers = tournament.find_all("div", class_="gols_itemRight__VSB2J")
    if not right_scorers:
        return []
    
    scorers = []
    for scorer in right_scorers:
        list_aux = []
        scorers_aux = scorer.find_all("span", class_="gols_block__uW5yg")
        for span in scorers_aux:
            list_aux.append(span.p.text.replace(";",""))
        scorers.append(list_aux)
    
    if all(len(s) == 0 for s in scorers):
        return []
    return scorers

def get_local_scorers_minutes(tournament):
    """
    Obtain the minutes of the local scorers from the tournament div.
    param tournament: BeautifulSoup object
    return: list of list of str
    """
    left_scorers_minutes = tournament.find_all("div", class_="gols_itemLeft__qNNDP")
    scorers_minutes = []
    # If there are no elements, return an empty list for the 0-0 match
    if not left_scorers_minutes:
        return [[]]
    
    for scorer in left_scorers_minutes:
        list_aux = []
        scorers_aux = scorer.find_all("span", class_="gols_block__uW5yg")
        for span in scorers_aux:
            minute_span = span.find("span", class_="green")
            if minute_span is not None and minute_span.text:
                list_aux.append(minute_span.text.replace("'", ""))
        scorers_minutes.append(list_aux)
    
    # If all elements are empty lists, an empty list is returned instead of a list of empty lists.
    # This is done to avoid having a list of empty lists when there are no scorers.
    if all(len(lst) == 0 for lst in scorers_minutes):
        return [[]]
    
    return scorers_minutes

def get_visitor_scorers_minutes(tournament):
    """
    Obtain the minutes of the visitor scorers from the tournament div.
    param tournament: BeautifulSoup object
    return: list of list of str
    """
    right_scorers_minutes = tournament.find_all("div", class_="gols_itemRight__VSB2J")
    scorers_minutes = []
    if not right_scorers_minutes:
        return [[]]
    for scorer in right_scorers_minutes:
        list_aux = []
        scorers_aux = scorer.find_all("span", class_="gols_block__uW5yg")
        for span in scorers_aux:
            list_aux.append(span.find("span", class_="green").text.replace("'",""))
        scorers_minutes.append(list_aux)
    
    if all(len(lst) == 0 for lst in scorers_minutes):
        return [[]]
    
    return scorers_minutes

def get_local_red_cards(tournament):
    """
    Obtain the number of red cards of the local team from the tournament div.
    param tournament: BeautifulSoup object
    return: list of int
    """
    left_red_cards = tournament.find_all("div", class_="red_gol__kGbip mr-75")
    return [len(red_card.find_all("span", class_="red_ball__NEoJ3 red_visible__8MS3_")) for red_card in left_red_cards]
    
def get_visitor_red_cards(tournament):
    """
    Obtain the number of red cards of the visitor team from the tournament div.
    param tournament: BeautifulSoup object
    return: list of int
    """
    right_red_cards = tournament.find_all("div", class_="red_gol__kGbip ml-75")
    return [len(red_card.find_all("span", class_="red_ball__NEoJ3 red_visible__8MS3_")) for red_card in right_red_cards]

def get_end_match(tournament):
    """
    Obtain the status of the match from the tournament div.
    param tournament: BeautifulSoup object
    return: list of str
    """
    end_match = tournament.find_all("div", class_="time_status___8fRm")
    return [status.text for status in end_match]


def make_dicctionary(tournament_name, 
                     local_team, 
                     visitor_team, 
                     local_score, 
                     visitor_score,
                     local_scorers,
                     visitor_scorers,
                     local_scorers_minutes,
                     visitor_scorers_minutes,
                     local_red_cards, 
                     visitor_red_cards, 
                     end_match, 
                     day):
    """
    Create a dictionary with the information obtained from the tournament div.
    param tournament_name: list of str
    param local_team: list of str
    param visitor_team: list of str
    param local_score: list of str
    param visitor_score: list of str
    param local_scorers: list of list of str
    param visitor_scorers: list of list of str
    param local_scorers_minutes: list of list of str
    param visitor_scorers_minutes: list of list of str
    param local_red_cards: list of int
    param visitor_red_cards: list of int
    param end_match: list of str
    param day: str
    return: dict
    """
    dictionary = {}
    
    # Initialize dictionary with basic match information
    for i in range(len(local_team)):
        tournament = tournament_name  # Use the tournament name directly
        if tournament not in dictionary:
            dictionary[tournament] = {
                'local_team': [],
                'visitor_team': [],
                'local_score': [],
                'visitor_score': [],
                'local_scorers': [],
                'visitor_scorers': [],
                'local_scorers_minutes': [],
                'visitor_scorers_minutes': [],
                'local_red_cards': [],
                'visitor_red_cards': [],
                'end_match': [],
                'day': day
            }
        
        # Add teams and match status
        dictionary[tournament]['local_team'].append(local_team[i])
        dictionary[tournament]['visitor_team'].append(visitor_team[i])
        dictionary[tournament]['end_match'].append(end_match[i])
        
        # Add scores or nan if empty
        dictionary[tournament]['local_score'].append(local_score[i] if i < len(local_score) else np.nan)
        dictionary[tournament]['visitor_score'].append(visitor_score[i] if i < len(visitor_score) else np.nan)
        
        # Add scorers or empty list if no scorers
        dictionary[tournament]['local_scorers'].append(local_scorers[i] if i < len(local_scorers) else [])
        dictionary[tournament]['visitor_scorers'].append(visitor_scorers[i] if i < len(visitor_scorers) else [])
        
        # Add scorers minutes or empty list if no minutes
        dictionary[tournament]['local_scorers_minutes'].append(local_scorers_minutes[i] if i < len(local_scorers_minutes) else [])
        dictionary[tournament]['visitor_scorers_minutes'].append(visitor_scorers_minutes[i] if i < len(visitor_scorers_minutes) else [])
        
        # Add red cards or 0 if no red cards
        dictionary[tournament]['local_red_cards'].append(local_red_cards[i] if i < len(local_red_cards) else 0)
        dictionary[tournament]['visitor_red_cards'].append(visitor_red_cards[i] if i < len(visitor_red_cards) else 0)

    return dictionary

def get_dataframe(dictionary):
    """
    Create a DataFrame from the dictionary with continuous indexing.
    param dictionary: dict
    return: pd.DataFrame
    """
    # Create an empty list to store all rows
    all_rows = []
    
    # Iterate through each tournament in the dictionary
    for tournament, data in dictionary.items():
        # Iterate through each match in the tournament
        for i in range(len(data['local_team'])):
            row = {
                'tournament': tournament,
                'local_team': data['local_team'][i],
                'visitor_team': data['visitor_team'][i],
                'local_score': data['local_score'][i],
                'visitor_score': data['visitor_score'][i],
                'local_scorers': data['local_scorers'][i],
                'visitor_scorers': data['visitor_scorers'][i],
                'local_scorers_minutes': data['local_scorers_minutes'][i],
                'visitor_scorers_minutes': data['visitor_scorers_minutes'][i],
                'local_red_cards': data['local_red_cards'][i],
                'visitor_red_cards': data['visitor_red_cards'][i],
                'end_match': data['end_match'][i],
                'day': data['day']
            }
            all_rows.append(row)
    
    # Create DataFrame from the list of rows
    df = pd.DataFrame(all_rows)
    
    # Reset index to ensure continuous indexing
    #df.index = range(len(df))
    df.reset_index(drop=True, inplace=True)
    
    return df

def main():
    # Set up headless browser
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    # Get the page
    path_url = "https://www.promiedos.com.ar/ayer"
    driver.get(path_url)
    
    # Wait for the elements to load
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "team_block__BYWWw"))
        )
    except Exception as e:
        print("Los elementos no se cargaron a tiempo:", e)
        driver.quit()
        return
    
    # Get page source after JavaScript execution
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "html.parser")
    
    # Find tournaments and matches
    tournaments = soup.find_all("div", class_="match-info_itemevent__jJv13")
    
    all_data = []
    
    for tournament in tournaments:
        try:
            tournament_name = get_tournament_name(tournament)
            local_team = get_local_team(tournament)
            visitor_team = get_visitor_team(tournament)
            local_score = get_local_score(tournament)
            visitor_score = get_visitor_score(tournament)
            local_scorers = get_local_scorers(tournament)
            visitor_scorers = get_visitor_scorers(tournament)
            local_scorers_minutes = get_local_scorers_minutes(tournament)
            visitor_scorers_minutes = get_visitor_scorers_minutes(tournament)
            local_red_cards = get_local_red_cards(tournament)
            visitor_red_cards = get_visitor_red_cards(tournament)
            end_match = get_end_match(tournament)
            day = (pd.Timestamp.today() - pd.Timedelta(days=1)).strftime('%d-%m-%Y')

            dicctionary = make_dicctionary(tournament_name,
                                             local_team,
                                             visitor_team,
                                             local_score,
                                             visitor_score,
                                             local_scorers,
                                             visitor_scorers,
                                             local_scorers_minutes,
                                             visitor_scorers_minutes,
                                             local_red_cards,
                                             visitor_red_cards,
                                             end_match,
                                             day
                                             )
            all_data.append(dicctionary)

        except Exception as e:
            print("Error:", e)
    
    # Combine all dictionaries into a single DataFrame
    combined_df = pd.concat([get_dataframe(d) for d in all_data], ignore_index=True)
    print(combined_df)
    
    driver.quit()
    
    driver.quit()

if __name__ == "__main__":
    main()
