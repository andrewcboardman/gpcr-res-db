import requests
import pandas as pd


def make_request(request):
    # Request data from server
    url_head = 'http://gpcrdb.org/services/'
    return requests.get(url_head + request)


def main():
    # Make request
    family_ids = ['100']
    data = []
    for i, fid in enumerate(family_ids):
        response = make_request('proteinfamily/proteins/{}'.format(fid))
        data.append(pd.DataFrame(response.json()))
    all_data = pd.concat(data)
    # Write data to local file
    all_data.to_csv('data/g_proteins.csv')


if __name__ == '__main__':
    main()