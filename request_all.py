import requests
import pandas as pd
import os

def make_request(request):
    # Request data from server
    url_head = 'http://gpcrdb.org/services/'
    return requests.get(url_head + request)


def request_gpcr_families():
    if os.path.exists('data/gpcr_families.csv'):
        print('Families already exist. Skipping...')
    else:
        response = make_request('proteinfamily/children/000')
        data = pd.DataFrame(response.json()).drop('parent',axis=1)
        data[data['slug'] != '100'].to_csv('data/gpcr_families.csv')
        print('Families downloaded')

def request_gpcr_metadata():
    if os.path.exists('data/gpcr_metadata.csv') and os.path.exists('data/gpcr_sequences.csv'):
        print( 'Metadata and sequences already exist. Skipping...')
    else:
        # Make request
        family_ids = pd.read_csv('data/gpcr_families.csv',dtype='str')['slug']
        data = []
        for i, fid in enumerate(family_ids):
            response = make_request('proteinfamily/proteins/{}'.format(fid))
            family_metadata = pd.DataFrame(response.json())
            family_metadata['family_id'] = fid
            data.append(family_metadata)
        all_data = pd.concat(data)
        # Write metadata to file
        all_data.drop('sequence',axis=1).to_csv('data/gpcr_metadata.csv')
        # Write sequences to file
        all_data[['entry_name','sequence']].to_csv('data/gpcr_sequences.csv')
        print('Metadata and sequences downloaded.')

def request_residue_labels():
    if os.path.exists('data/gpcr_reslabels'):
        print('Residue labels already exist. Skipping...')
    else:
        protein_entry_names = pd.read_csv('data/gpcr_metadata.csv',dtype='str')['entry_name']
        output = ',sequence_number, amino_acid, protein_segment, display_generic_number, protein\n'
        with open('data/gpcr_reslabels.csv','w') as fid:
            fid.write(output)

        for i, name in enumerate(protein_entry_names):
            response = make_request('residues/' + name)
            labels_df = pd.DataFrame(response.json())
            labels_df['protein'] = name
            labels_df.to_csv('data/gpcr_reslabels.csv',mode='a',header=False)
            print('Residue labels for {} / {} proteins downloaded'.format(i+1,len(protein_entry_names)))

        print('Residue labels downloaded.')

def request_alignments():
    if os.path.exists('data/gpcrdb_align.csv'):
        print('Alignment file already exists. Skipping...')
    else:
        family_ids = pd.read_csv('data/gpcr_families.csv',dtype='str')['slug'].drop('00')
        segments = ['N-term','TM1','ICL1',
                    'TM2','ECL1','TM3',
                    'ICL2','TM4','ECL2',
                    'TM5','ICL3','TM6',
                    'ECL3','TM7','C-term']
        data = []
        for family, segment in zip(family_ids,segments):
            response = make_request('alignment/family/' +family + '/' + segment)
            align_df = pd.DataFrame(dict(
                name = list(response.json().keys()),
                align = list(response.json().values())))
            align_df = align_df[~align_df['name'].isin(['false','CONSENSUS'])]
            align_df['family'] = family
            align_df['segment'] = segment
            align_df = (align_df.set_index('name')
                                .apply(lambda x: x.apply(list).apply(pd.Series).stack())
                                .reset_index()
                                .rename(columns={'level_1':'n_align_seg'}))
            data.append(align_df)
        all_data = pd.concat(data)
        all_data['n_align'] = all_data.groupby('name').cumcount()
        all_data = all_data.rename(columns={'align':'res'})
        all_data = all_data[all_data['res'] != '-']
        all_data['n_res'] = all_data.groupby('name').cumcount()
        all_data.to_csv('data/gpcr_alignments.csv')
def merge_alignments():
    if os.path.exists('data/merged_alignments_labels.csv'):
        print('Alignment and labels already merged. Skipping...')

def request_structures_list():
    if os.path.exists('data/structures_list.csv'):
        print('Structures list already exists. Skipping...')
    else:
        # Make request
        response = make_request('structure')
        output = pd.DataFrame(response.json())
        # Write data to local file
        output.to_csv('data/structures_list.csv')
        print('Structures list downloaded.')


def main():
    request_gpcr_families()
    # Get basic data on all GPCR entries in GPCRdb
    request_gpcr_metadata()

    request_residue_labels()

    #request_alignments()
    #request_structures_list()


    
	
if __name__ == '__main__':
    main()
