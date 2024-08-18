import urllib.request
import json

class Api:
    """
    A class for making API calls.

    Attributes:
        url (str): The API endpoint URL.
        headers (dict): Headers for the API request.
    """

    def __init__(self, config_file='config.json') -> None:
        """
        Initialize the Api class.

        Parameters:
            config_file (str): The path to the configuration file.
        """
        with open(config_file) as file:
            config = json.load(file)

        prefix = config['url']
        suffix = '_search'
        self.url = f"{prefix}labfumehood/{suffix}"
        self.headers = {
            config['Authorization-Header']: config['labfumehood/'],
            'Cache-Control': 'no-cache'
        }

    def call(self, TLInstance, start_day = None, end_day = None, size=1):
        """
        Make an API call.

        Parameters:
            TLInstance (str): The TLInstance parameter.
            start_day (str): The start date for the query.
            end_day (str): The end date for the query.
            size (int): The size parameter for the query.

        Returns:
            list: A list of hits from the API response.
        """
        try:
            size_param = f'?size={size}'
            sort_param = '&sort=@timestamp:desc'
            if start_day and end_day:
            
                query_param = f'&q=TLInstance:{TLInstance} AND @timestamp:{{{start_day} TO {end_day}}}'
            else:
                query_param = f'&q=TLInstance:{TLInstance}'
            query_param = query_param.replace(" ", "%20")

            full_url = f"{self.url}{size_param}{sort_param}{query_param}"
            
            request = urllib.request.Request(full_url, headers=self.headers)
            request.get_method = lambda: 'GET'

            with urllib.request.urlopen(request) as response:
                return json.loads(response.read())['hits']['hits']

        except Exception as e:
            print(e)
            pass

def main():
    api_instance = Api()

    # Example API call
    try:
        
        results = api_instance.call(
            TLInstance='1337',
            #start_day='2024-01-01',
            #end_day='2024-01-07',
            size=50
        )
        print(results)
        # Print the results
        print("API Results:")
        for result in results:
            print(result)

    except Exception as e:
        print(f"Error during API call: {e}")

if __name__ == "__main__":
    main()
    
