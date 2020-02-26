import requests
import pandas as pd
import os
import itertools as it


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
    if os.path.exists('data/gpcr_reslabels.csv'):
        print('Residue labels already exist. Skipping...')
    else:
        protein_entry_names = pd.read_csv('data/gpcr_metadata.csv',dtype='str')['entry_name']
        output = 'sequence_number,amino_acid,protein_segment,display_generic_number,protein\n'
        with open('data/gpcr_reslabels.csv','w') as fid:
            fid.write(output)

        for i, name in enumerate(protein_entry_names):
            if i < len(protein_entry_names) - 3751:
                response = make_request('residues/' + name)
                labels_df = pd.DataFrame(response.json())
                labels_df['protein'] = name
                labels_df.to_csv('data/gpcr_reslabels.csv',mode='a',header=False,index=False)
                print('Residue labels for {} / {} proteins downloaded'.format(i+1,len(protein_entry_names)))

        print('Residue labels downloaded.')

def get_alignment_df(family,segment):
    response = make_request('alignment/family/' +family + '/' + segment)
    align_df = pd.DataFrame(dict(
        name = list(response.json().keys()),
        align = list(response.json().values())))
    align_df = align_df[~align_df['name'].isin(['false','CONSENSUS'])]

    align_df = (align_df.set_index('name')
                        .apply(lambda x: x.apply(list).apply(pd.Series).stack())
                        .reset_index()
                        .rename(columns={'level_1':'n_align_seg'}))

    align_df['family'] = family
    align_df['segment'] = segment
    return align_df
  


def request_alignments():
    if os.path.exists('data/gpcr_alignments.csv'):
        print('Alignment file already exists. Skipping...')
    else:
        family_ids = pd.read_csv('data/gpcr_families.csv',dtype='str')['slug']
        segments = ['N-term','TM1','ICL1',
                    'TM2','ECL1','TM3',
                    'ICL2','TM4','ECL2',
                    'TM5','ICL3','TM6',
                    'ECL3','TM7','ICL4',
                    'H8','C-term']
        data = []
        for family, segment in it.product(family_ids,segments):
            try:
                align_df = get_alignment_df(family, segment)
                data.append(align_df)
            except IndexError:
                continue
        
        all_data = pd.concat(data)
        all_data['n_align_seg'] =  all_data['n_align_seg'] + 1
        all_data['n_align'] = all_data.groupby('name').cumcount() + 1
        all_data = all_data.rename(columns={'align':'res'})
        all_data = all_data[~all_data['res'].isin(['-','_'])]
        all_data['n_res'] = all_data.groupby('name').cumcount() + 1
        all_data.to_csv('data/gpcr_alignments.csv',index=False)

        print('Alignments downloaded')

def merge_alignments_labels():
    if os.path.exists('data/gpcr_label_align.csv'):
        print('Alignment and labels already merged. Skipping...')
    else:        
        labels = pd.read_csv('data/gpcr_reslabels.csv')
        labels['id'] = labels['protein'] + ':' + labels['sequence_number'].astype(str)
        labels = labels.set_index('id').drop(['sequence_number','protein'],axis=1)
        labels.columns = ['res','seg','label']

        align = pd.read_csv('data/gpcr_alignments.csv')
        align['id'] = align['name'] + ':' + align['n_res'].astype(str)
        align = align.set_index('id').drop(['name','n_res'],axis=1)
        align.columns = ['n_seg_aln','res','family','seg','n_aln']

        joined = align.join(labels, how='left', lsuffix = '_aln', rsuffix = '_lbl')
        joined = joined.reset_index()
        joined[['name','n_res']] = joined['id'].str.split(':',expand=True)
        joined = joined[['name','n_res','res_aln','res_lbl',
                    'label','seg_aln','seg_lbl',
                    'n_seg_aln','n_aln','family']]
        # filter off gpr98 which won't line up
        joined = joined[~joined['name'].isin(['gpr98_danre','gpr98_human','gpr98_mouse'])]
        # Clean up columns
        joined = (joined.drop(['res_lbl','seg_lbl','n_seg_aln'],axis=1)
                        .rename(columns={'res_aln':'res',
                                         'seg_aln':'seg'}))
        #Reformat labels
        joined[['lbl_segBW','lbl_GPCRDB']] = joined['label'].str.split('x',expand=True)
        joined[['lbl_seg','lbl_BW']] = joined['lbl_segBW'].str.split('.',expand=True)
        joined['GPCRdb_label'] = joined['lbl_seg'] + 'x' + joined['lbl_BW']
        joined = joined.drop(['label','lbl_segBW','lbl_GPCRDB','lbl_seg','lbl_BW'],axis=1)
        joined['id'] = joined['name'] + ':' + joined['res'] + joined['n_res'] 
        # Convert family stub to code using dictionary
        fam_dict = {1:'A',2:'B1',3:'B2',4:'C',5:'F',6:'Taste',7:'Other'}
        joined['family'] = [fam_dict.get(x) for x in joined['family']]
        
        # Sort 
        joined['n_res'] = joined['n_res'].astype(int)
        joined = joined.sort_values(['family','name','n_res'])

        # Rearrange cols
        cols = joined.columns.tolist()
        cols = cols[-1:] + cols[:-1]
        joined = joined[cols]

        joined.to_csv('data/gpcr_label_align.csv',index=False)
        print('Labels merged with alignment')


# def request_structures_list():
#     if os.path.exists('data/structures_list.csv'):
#         print('Structures list already exists. Skipping...')
#     else:
#         # Make request
#         response = make_request('structure')
#         output = pd.DataFrame(response.json())
#         # Write data to local file
#         output.to_csv('data/structures_list.csv')
#         print('Structures list downloaded.')


def main():
    request_gpcr_families()
    # Get basic data on all GPCR entries in GPCRdb
    request_gpcr_metadata()

    request_residue_labels()

    request_alignments()
    
    merge_alignments_labels()


    
	
if __name__ == '__main__':
    main()
