import requests
import pandas as pd
import

def make_request(request):
    # Request data from server
    url_head = 'http://gpcrdb.org/services/'
    return requests.get(url_head + request)


def main():
    # Make request
    response = make_request('structure')
    output = pd.DataFrame(response.json())

    output
    # Write data to local file
    output.to_csv('structures.csv')


if __name__ == '__main__':
    main()