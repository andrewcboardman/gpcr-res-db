import pandas as pd 
import requests

def make_request(request):
# Request data from server
	url_head = 'http://gpcrdb.org/services/'
	return requests.get(url_head + request)

def main():
	structs = pd.read_csv('structures.csv')
	codes = structs['pdb_code']

	for code in codes:
		response = make_request('structure/' +code + '/interaction')
		data = pd.DataFrame(response.json())

	if code == codes[0]:
		data.to_csv('structure_ligand_interactions.csv', mode='w')

	else:
		data.to_csv('structure_ligand_interactions.csv', mode='a', header=False)


if __name__ == '__main__':
	main()
