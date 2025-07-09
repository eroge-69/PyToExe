import json;
import sys;

name = '';

vsliceFile = {
    "version": "1.0.0",
    "name": '',
    "assetPath": '', 
    "startingAnimation": '',
    "singTime": '',
    "flipX": False,
    "isPixel": False,
    "healthIcon": {'id': 'test'},
    "animations": [],
    "offsets": [],
    "cameraOffsets": [],
    "scale": 1
};

def convert_character():
    if (len(sys.argv) < 1): return;

    with open(sys.argv[1], 'r') as characterFile:
        characterJson = json.load(characterFile);
            
        vsliceFile['name'] = name;
        vsliceFile['assetPath'] = characterJson['image'];
        vsliceFile['singTime'] = characterJson['sing_duration'];
        vsliceFile['healthIcon']['id'] = characterJson['healthicon'];
        vsliceFile['flipX'] = characterJson['flip_x'];
        vsliceFile['isPixel'] = characterJson['no_antialiasing'];
        vsliceFile['offsets'] = characterJson['position'];
        vsliceFile['cameraOffsets'] = characterJson['camera_position'];
        vsliceFile['scale'] = characterJson['scale'];
            
        i = 0;
        ii = 0;
        startAnim = '';

        while i < len(characterJson['animations']):
            vsliceFile['animations'].append({
                "name": characterJson['animations'][i]['anim'].replace('-loop', '-hold'),
                "prefix": characterJson['animations'][i]['name'],
                "frameIndices": characterJson['animations'][i]['indices'],
                "frameRate": characterJson['animations'][i]['fps'],
                "offsets": characterJson['animations'][i]['offsets'],
                "looped": characterJson['animations'][i]['loop']
            });
            i += 1;
            
        while ii < len(vsliceFile['animations']):
            if (vsliceFile['animations'][ii]['name'] == 'danceRight'):
                startAnim = 'danceRight';
                break;
            else:
                startAnim = 'idle'; # assumes character has an idle anim
            ii += 1;
                
        
        vsliceFile['startingAnimation'] = startAnim;
        # print(vsliceFile['startingAnimation']);

        
    with open(characterFile.name.replace('.json', '') + ' (converted).json', 'w') as toExport:
        json.dump(vsliceFile, toExport, indent=2);

print('Character Name?');
name = str(input('Name: '));
convert_character();