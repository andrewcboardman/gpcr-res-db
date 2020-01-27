import requests
import argparse
import pandas as pd


def make_request(request, output_file):
    # Request data from server
    url_head = 'http://gpcrdb.org/services/'
    response = requests.get(url_head + request)
    data = pd.DataFrame(response.json())
    # Write data to local file
    data.to_csv(output_file)


def make_request_alignment(request, output_file):
    # Request data from server
    url_head = 'http://gpcrdb.org/services/'
    response = requests.get(url_head + request)
    data = pd.DataFrame.from_dict(response.json(),
                                  orient='index', columns=['aligned_sequence'])
    # Write data to local file
    data.to_csv(output_file)

def main():
    # Get command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--request', help='Call to RESTful API')
    parser.add_argument('-o', '--outfile', help='File to output results to')
    parser.add_argument('--alignment', action='store_true', help='Call is for alignment')
    args = parser.parse_args()

    # Make request
    if args.alignment:
        make_request_alignment(args.request, args.outfile)
    else:
        make_request(args.request, args.outfile)


if __name__ == '__main__':
    main()