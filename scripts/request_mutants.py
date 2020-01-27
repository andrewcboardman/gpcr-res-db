import requests
import pandas as pd


def make_request(request):
    # Request data from server
    url_head = 'http://gpcrdb.org/services/'
    return requests.get(url_head + request)


def main():
    # Get list of protein entry names
    input = pd.read_csv('gpcrs.csv', usecols=['entry_name'])
    names = input['entry_name']
    # Make request
    for i, name in enumerate(names):
        response = make_request('mutants/{}'.format(name))
        data = pd.DataFrame(response.json())
        # Write data to local file
        if i == 0:
            data.to_csv('mutants.csv', mode='w')
        else:
            data.to_csv('mutants.csv', mode='a', header=False)


if __name__ == '__main__':
    main()