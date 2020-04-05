from chatterbot.logic import LogicAdapter
from chatterbot.conversation import Statement
import requests


#Utility Functions

def get_master_data():
    """
    Get the master data
    """
    data = RAW_RESPONSE.json()
    STATES = set()
    CITIES = set()
    DISTRICTS = set()
    for each in data["raw_data"]:

        if each["detectedstate"]!='':
            STATES.add(each["detectedstate"].lower().strip().replace(" ",""))
        if each["detecteddistrict"]!='':
            DISTRICTS.add(each["detecteddistrict"].lower().strip().replace(" ",""))
        if each["detectedcity"]!='':
            CITIES.add(each["detectedcity"].lower().strip().replace(" ",""))
    STATES = list(filter(None, STATES))
    DISTRICTS = list(filter(None, DISTRICTS))
    CITIES = list(filter(None, CITIES))

    return STATES, DISTRICTS, CITIES


def get_case_history(search_text):
    """
    Try to get case history from raw data
    """

    data = RAW_RESPONSE.json()
    count = 0
    metadata = "History of Cases in {}: \n".format(search_text)
    add_text = ""
    for city in data["raw_data"]:
        if city["detectedcity"].lower().strip().replace(" ","") == search_text:
            count+=1
            add_text+= "Case {}:\n".format(count) + "As on date: {}\n".format(city["statuschangedate"]) + \
            "Current status of the patient is {}.\n".format(city["currentstatus"]) + \
            "Age of the patient {}\n".format(city["agebracket"]) + \
            "Gender of the patient {}\n".format(city["gender"]) + \
            "Nationality: {}\n".format(city["nationality"]) + \
            "Location: {}\n".format(city["detectedcity"]) + \
            "Type Of Transmission: {}\n".format(city["typeoftransmission"]) + \
            "Case announced on {}\n".format(city["dateannounced"]) + \
            "Notes: {}\n".format(city["notes"]) + \
            "Sources: {}".format(city["source1"], city["source2"], city["source3"])

            add_text += '\n\n'
    
    if add_text=="":
        add_text="Case history not found at the moment. Try being more specific."
            
    return metadata+add_text


def get_district_cases(search_text):
    """
    Find district cases
    """
    data = DISTRICT_RESPONSE.json()
    for state in data:
        for district in state["districtData"]:

            if district["district"].lower().strip().replace(" ","") == search_text:
                date = "As of today: {}.\n".format(district["lastupdatedtime"])
                active = "Total number of cases: {}\n".format(district["confirmed"])
                today_cases= "New cases reported today:{}\n".format(district["delta"]["confirmed"])
                text = active + today_cases
                break
    return text

def get_state_cases(search_text):
    """
    Find state cases
    """
    data = STATE_RESPONSE.json()
    for state in data['statewise']:
        
        if state["state"].lower().strip().replace(" ","") == search_text:
            date = "As of {}.\n".format(state["lastupdatedtime"])
            active = "Active Cases: {}\n".format(state["active"])
            deaths = "Total Deaths: {}\n".format(state["deaths"])
            recovery = "Total Recovered: {}\n".format(state["recovered"])
            confirmed_now1 = "Cases confirmed today: {}\n".format(state["deltaconfirmed"])
            confirmed_now2 = "Deaths confirmated today: {}\n".format(state["deltadeaths"])
            confirmed_now3 = "Recovered Today: {}\n".format(state["deltarecovered"])

            text = date + active + deaths + recovery + confirmed_now1 + confirmed_now2 + confirmed_now3
            break
    
    return text

# Get all DISTRICTS, STATES and City
RAW_RESPONSE = requests.get('https://api.covid19india.org/raw_data.json')
STATE_RESPONSE = requests.get('https://api.covid19india.org/data.json')
DISTRICT_RESPONSE = requests.get('https://api.covid19india.org/v2/state_district_wise.json')
STATES, DISTRICTS, CITIES = get_master_data()


class InfoAdapter(LogicAdapter):
    
    def __init__(self, chatbot, **kwargs):
        super().__init__(chatbot, **kwargs)

    def can_process(self, statement):

        search_text = statement.text.lower().strip().replace(" ","")
        if search_text in STATES or search_text in DISTRICTS or search_text in CITIES:
            return True
        elif 'show' in statement.text.lower().strip().replace(" ",""):
            return True
        else:
            return False


    def process(self, input_statement, additional_response_selection_parameters):
        """
        Process chatbot responses
        """
        
        search_text = input_statement.text.lower().strip().replace(" ","")
        text = ""

        # Let's base the confidence value on if the request was successful
        if RAW_RESPONSE.status_code == 200:
            confidence = 1
        else:
            confidence = 0

        if search_text == "show STATES":
            
            text = 'List of affected STATES:\n' + ','.join(STATES)
            selected_statement = Statement(text=text)
            selected_statement.confidence = confidence
        
        elif search_text == "show DISTRICTS":

            text = 'List of affected DISTRICTS:\n' + ','.join(DISTRICTS)
            selected_statement = Statement(text=text)
            selected_statement.confidence = confidence
        
        elif search_text == "show cities":
        
            text = 'List of affected cities:\n' + ','.join(CITIES)
            selected_statement = Statement(text=text)
            selected_statement.confidence = confidence

        elif search_text in STATES:

            text = get_state_cases(search_text)
        
        elif search_text in DISTRICTS:
            
            text = get_district_cases(search_text)

            text += get_case_history(search_text)
        
        elif search_text in CITIES:
            text = get_case_history(search_text)
        
        else:
            text="No reported cases found for {}. Note: This could be because the name doesn't match"\
                    "our database. Type show STATES or show DISTRICTS or show cities".format(search_text)
            selected_statement.confidence = confidence
        
        selected_statement = Statement(text=text)
        selected_statement.confidence = confidence

        return selected_statement