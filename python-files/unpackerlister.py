import os
import subprocess

def unpack_archives_and_generate_list():
	folder = 'propfiles'
	base_path = os.path.join(os.path.dirname(__file__), folder)

def run_batch_and_process_files():
	folder = 'propfiles'
	base_path = os.path.join(os.path.dirname(__file__), folder)
	bat_path = os.path.join(base_path, 'unpack_rar.bat')
	subprocess.run([bat_path], cwd=base_path, shell=True)


	ydr_files = []
	for root, dirs, files in os.walk(base_path):
		for file in files:
			if file.lower().endswith('.ydr'):
				ydr_files.append(os.path.splitext(file)[0])
	xml_template = '''<Item type="CBaseArchetypeDef">
	  <lodDist value="500.00000000"/>
	  <flags value="0"/>
	  <specialAttribute value="0"/>
	  <bbMin x="0.00000000" y="0.00000000" z="0.00000000"/>
	  <bbMax x="0.00000000" y="0.00000000" z="0.00000000"/>
	  <bsCentre x="0.00000000" y="0.00000000" z="0.00000000"/>
	  <bsRadius value="0.00000000"/>
	  <hdTextureDist value="5.00000000"/>
	  <name>{propname}</name>
	  <textureDictionary>{propname}</textureDictionary>
	  <clipDictionary/>
	  <drawableDictionary/>
	  <physicsDictionary>{propname}</physicsDictionary>
	  <assetType>ASSET_TYPE_DRAWABLE</assetType>
	  <assetName>{propname}</assetName>
	  <extensions/>
	</Item>\n'''
	with open(os.path.join(base_path, 'proplist.txt'), 'w', encoding='utf-8') as out:
		for propname in ydr_files:
			out.write(xml_template.format(propname=propname))

	for filename in os.listdir(base_path):
		if filename.lower().endswith('.rar'):
			try:
				os.remove(os.path.join(base_path, filename))
			except Exception as e:
				print(f"Fehler beim Löschen von {filename}: {e}")

if __name__ == "__main__":
	run_batch_and_process_files()

