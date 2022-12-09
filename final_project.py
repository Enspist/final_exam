# Importing the necessary modules for this script. 
import requests,pathlib,csv,math,time,pickle

# This is the base API URL for NYTimes Article Search and the API Key being used to pull the data.
BASE_URL = 'https://api.nytimes.com/svc/search/v2/articlesearch.json'
API_KEY = 'ooOlpNdFnuANOfT5dW73iONfg4V2O5ez'

# Here are the base parameters, what is being searched for and the API key to allow for searches.
gun_control_parameters = {'q' : 'Gun Control', 'api-key' : API_KEY}
gun_control_parameters['fq'] = 'document_type:("article") AND section_name:("U.S.")'
gun_control_parameters['begin_date']='20220401'
gun_control_parameters['page'] = 0  # type: ignore

def data_pull(parameters):
    """This function calls on the NYTimes API to search for articles based on parameters

    Args:
        parameters (list): This is the list of parameters that the API is going to use to search for articles.
        It is based off of the documentation for the API.

    Returns:
        json: this is a json file with all of the results of the API search
    """
    response = requests.get(BASE_URL, params=parameters)
    results = response.json()
    return results

def create_csv(article_results, location):
    """This is going to create a CSV file with the results of the search in a specified location

    Args:
        article_results (dict): this is the dictionary that the specified results get put into 
        after being refined by the data_dictionary function.
        
        location (str): This is the folder that the final CSV will be placed into.
    """
    # pulling the current directory .
    curr_dir = pathlib.Path.cwd()

    # creating a folder object in the directory called nytimes_results.
    location = curr_dir/f"{location}"

    # Creating the folder with the mkdir command.
    location.mkdir(exist_ok=True)

    # Creating the object for the CSV file.
    articles_extract = location/"articles_extract.csv"

    # Creating the CSV using the open function and csv commands. 
    with articles_extract.open(mode='w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['headline' , 'pub_date', 'web_url'])
        writer.writeheader()
        writer.writerows(article_results)

def data_dump(location, page_count, parameters):
    """This is going to call upon the API for each page of data and download it as a .pkl file into a specified location

    Args:
        location (str): This is where the folder where the .pkl files are going to be downloaded to.
        
        page_count (int): This is the total number of pages that need to be searched.
        It is based on the total number of hits that API call gets. 
        
        parameters (list): This is the list of parameters for the API to search for.
    """
    if page_count > 200:
        page_count = 200
    
    for i in range(page_count):
        parameters['page']=i  # type: ignore
        extract_data = data_pull(parameters)
        data_file_name = f"extract_data_{parameters['page']}.pkl"
        data_file_name_path = location/data_file_name
        with data_file_name_path.open(mode='wb') as file:
            pickle.dump(extract_data, file)
        print(f"file {i + 1} downloaded")
        time.sleep(6)
    print(f"set downloaded")

def data_dictionary(dictionary, location):
    """This is going to search the downloaded .pkl files and refine the searches further.
    This data will be placed into a dictionary to then be pulled into a CSV.

    Args:
        dictionary (dict): This is the dictionary where the refined searched are going to go.
        
        location (str): This is the location where the .pkl files are stored. 
    """
    count = 0
    for file in location.glob('*.pkl'):
        with file.open(mode= 'rb') as f:
            data = pickle.load(f)
            articles = data['response']['docs']
            for article in articles:
                headline = article['headline']['main']
                pub_date = article['pub_date']
                dictionary.append({'headline':headline, 'pub_date':pub_date})
    
def create_data_location(location):
    """This is the location for the .pkl files to be stored. 

    Args:
        location (str): The name of the location where the .pkl files will be stored.

    Returns:
        str: The name of the location where the .pkl files will be stored.
    """
    curr_dir = pathlib.Path.cwd()

    #  creating a folder object in the directory called nytimes_results.
    location = curr_dir/f"{location}"

    # Creating the folder with the mkdir command.
    location.mkdir(exist_ok=True)
    
    return location

def pages(parameters):
    """This is getting the hit count and the page count of the API search

    Args:
        parameters (list): This is the list of parameters that the API has to use to search. 

    Returns:
        int, int: Returns the hit count and page count of the search.
    """
    
    extract_data = data_pull(parameters)

    hit_count = extract_data['response']['meta']['hits']

    page_count = math.ceil(hit_count / 10)
    
    return hit_count, page_count

# This is the Dict where the results are going to be compiled.
article_results = []

# Getting the hit count and page count of the search
page_count = pages(gun_control_parameters)

# printing out the number of hits and pages the API needs to search
print(f"hits: {page_count[0]} \npages: {page_count[1]}")

# The location where the .pkl files will be stored.
api_data_extracts = create_data_location("api_data_extracts")

# Running the data dump function
data_dump(api_data_extracts, page_count[1], gun_control_parameters)
    
# Running the data_dict function
data_dictionary(article_results, api_data_extracts)

# Creating the final csv in the specified location
create_csv(article_results, "NYTimes_Data")