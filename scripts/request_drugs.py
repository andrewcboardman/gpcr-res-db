import requests
import pandas as pd


def make_request(request):
    # Request data from server
    url_head = 'http://gpcrdb.org/services/'
    return requests.get(url_head + request)


def main():
    # Get list of protein entry names
    input = pd.read_csv('data/gpcrs.csv', usecols=['entry_name'])
    names = input['entry_name']
    # Make request
    for name in names:
        response = make_request('drugs/{}'.format(name))
        data = pd.DataFrame(response.json())
        data['protein'] = name
        # Write data to local file
        if name == names[0]:
            data.to_csv('drugs.csv', mode='w')
        else:
            data.to_csv('drugs.csv', mode='a', header=False)


if __name__ == '__main__':
    main()