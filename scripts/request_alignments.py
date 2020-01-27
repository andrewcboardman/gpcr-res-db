import requests
import pandas as pd
import itertools as it
from functools import reduce


def make_request_alignment(request, output_file):
    # Request data from server
    url_head = 'http://gpcrdb.org/services/'
    response = requests.get(url_head + request)
    data = pd.DataFrame.from_dict(response.json(),
                                  orient='index', columns=['aligned_sequence'])
    return data


def merge_alignments(df1, df2):
    df1.merge(df2, left_index=True, right_index=True)


def main():
    # Get list of GPCR families
    family_ids = [('00' + str(x)) for x in range(1, 1)]
    # List of segment names
    segments = [('TM' + str(x)) for x in range(1, 8)] + \
        [('ICL' + str(x)) for x in range(1, 4)] + \
        [('ECL' + str(x))for x in range(1, 4)] #+ \
        #['N-term', 'C-term']

    # Combine these and append to list
    human_alignments = []
    full_alignments = []
    for fid in family_ids:
        for seg in segments:
            # Include non-human
            request = 'alignment/family/' + fid + '/' + seg
            outfile = 'alignment_' + fid + '_' + seg
            full_alignment = make_request_alignment(request, outfile + '.csv')
            full_alignment.columns = [seg]
            full_alignments.append(full_alignment)

            # Exclude non-human
            request_human = request + '/Homo sapiens'
            outfile_human = outfile + '_human'
            human_alignment = make_request_alignment(request_human, outfile_human + '.csv')
            human_alignment.columns = [seg]
            human_alignments.append(human_alignment)

        full_alignments_df = reduce(merge_alignments, full_alignments)
        human_alignments_df = reduce(merge_alignments, human_alignments)

        full_alignments_df.to_csv(fid + '_alignment_full.csv')
        human_alignments_df.to_csv(fid + '_alignment_human.csv')


if __name__ == '__main__':
    main()