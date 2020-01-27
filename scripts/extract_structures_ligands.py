import pandas as pd
def main():
	structs = pd.read_csv('structures.csv')
	codes = structs['pdb_code']
	ligands = [eval(x) for x in structs['ligands']]
	num_ligands = [len(x) for x in ligands]
	code_ligands = [[code]*n for (code, n) in zip(codes,num_ligands)]
	ligand_df = pd.DataFrame([x for y in ligands for x in y])
	ligand_df['pdb_code'] = [x for y in code_ligands for x in y]
	ligand_df.to_csv('structure_ligands.csv')

if __name__ =='__main__':
	main()