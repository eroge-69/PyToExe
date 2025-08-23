# Made by Sora_
# Thanks to the Genshin Impact Modding Community for their help and support
# Thanks to LeoTorreZ and SilentNightSound, this script is adapted from their script
# Thanks for BladeMouX and Plutoisy, for allowing me to find these hashes in advance
# Special thanks for !someone name has 63B long? help me complete this script

# Fixes for all playable character's body
# Note: This fix DOES NOT contain the fixes before 2.2 for older mods, find 2.2 version of them

# ##########################################################################################################################
#     ................                .... ..   ..               ............. ............                              
#     ................                ... ...                    .........................                               
#   ..............            ....                 ..            ........,]`.]............                               
# ................            ......                             ...,/\]/O],*,[\[]........                               
# ............                                           ........,/\@O@/,/\]]],`=`*,=\`...........                       
# .......... .        ..                                 ....../@\@@/`/*`,/\/\[,*,,**=OO]]]........                      
# ............                                        .. ..../O\O@[,,,///`********,*`,]\]*/\`.....                       
# ...........  ...                                    .. .../O@@^*,/\/`*/\***********,**/*/\/.....                       
# ............. .... .                     .  ............][\ooo\O\@^]/ooo`****,*****`*`^`/O@O..... ..                .. 
# ............. .... .                   ............,O\OOO\oo]OOo@`@OO//`***,\\,,``/^,\^,***[\....                      
# ............                            .............,//*,*]/oO^\@ooooo/^*]\]/`\*//**=**`[^*/^...                      
# ............                            ...=]]]]]/[**`*,,*/\o@`O@O/OO\=O/[O\``[/^/``*O]`**,^\\....                     
# ............ ...                       ......,OooooO/@@/o\[//=@o@o//,OOO/\//*/\OO\]`=\^*O]/@@\^..       .. .           
# ............    ..                      ........[@O\oooo\O@/@OOO\///O/\\@^]@\OOO\\\oOO^\@o]OO\^..       .. .           
# .......... .....    ..      .  .       ............/oo/\/,\@O@O@\OO\^]]@@/\,\//`=OO\O@^@O/=\\OO`....        ..         
# ..... ....... ..... .       ....        .........,//O[[]OOOOOO/O/@@@@@@\/]o\OO`=O@\=OO/O/,=/^@@@....        ..         
# ................            .....  .............=\`*`/\OOooO/@/@,O@@@@O^,@\OO*=O@\*oOOOO^=^/@/@,\... ..         .......
# ................            ....        ......,//*,/OOOoO\=/OOo^\\.\O/.../O//\/@\O\@@\OO*@\O=\@..=.....         ....   
# ................                    ........,/,/,//OO\/*,*@oOO\^O@......*O/`.**\@@@^@@@^/\O^**=^........               
# ...,]/\]].....                      .....]\\*/O\@oo\/,`*/@Oo/@o^=^.....,.......@O@`/@@^@/oO`\OO^... .                  
# .,/`@O[*............................,]/^**/@O/OOOO``*,\o@O/\OO/^=\..........[...,.*@O@@OO@,*/=/..                      
# O,[,`\]/[\/OOO\/^[*,\/**,]]]]]]O\Oo\,*,/OO@@oOO`**,*,oO\/*@@@@/o,@\`..............@O@Oo@@`*/./...                      
# \,/[,*`,\//@//oo\O]*,\`..\/**`,Oo/[OOo@O@\O/\//o\,`\//[*//@@@O@o`@^@`.[,......../@\@OO@@*=`......                      
# O/@//\`*/**[\/\OO\@\\`\[\..\][\/@OO\OO^OO/]o/o/o\[/\*,/O/\@@@\O@O@,/@\.`..,]/@@OOO@@o@@/`.......                       
# \/...,,[[\`*,*\\\/O[@.,//*./OOOO@@@OO@Ooo\o\@/\[,*\,OO@oo@@@@@O@@@=@@@@@@@@OO@=@@@OOO\O^.. ... .                       
# .......*``],,``/\O]*/..\\^=\/oOo///\oOOOOO\]`*/`/]OO/oOO\O@@@@@@@@@@@@@@@@@O@@@@O\O@OO=^...     .. .                   
# .../\\\\\=\/O\/[^\`=/...`.@\],/O`**\]`oooooo^O@\oo\@O@OOOOOOOO@@@@/@@@@@@@@@@\OO@@@/\/=.......  ..                     
# ./OooooOO/^/^***/\,/@`....@/`,,*`*`*/]]O/@//ooOOO/@@@@O\OOOOOOOOOOOO@O]\@@@@O@@@@@@OO@OO^......         ....           
# OooO/@\o\/*`******/@O^....@.*`*`***]/@@OOOOOOO/O@@OO\@@@@OOOOOO@@OO@OOOO@@@@@OOO@@@@@O@@O^.......               ....   
# OOO\Oo\/**`**,**\]`@,=^**//\\/\\\`O\oO@/`/@O\@@OOOOOOOO@@@@OOO/@@@@@@@OOO@@@@OOOOO@@@@@@@O\..  .                . ..   
# OOOOO@[,,*`]/Oooooo\Ooo\oo/O`/\@*[,[O@/O\OOO@@OOOOOO@OOOO@@@@OOOOO@@@@@O@@@/@\@@[OOOOO@@@@OO`...         .......       
# OOOo/*`,,@oooo\oooo\//@\oo/O\//,\@OooOOOoo@O@OOOOO@@O@@@@@@@O@OOOOOO@@\\@@OO\OO@@`\/OOO\@@OO@...          . ....       
# OOo@*``/\/[.......,.==@@OO/OO\/\^OO/@\OoO\@@@@@@@@@@@@@@@@@\@@@@@OOO@@@/@@OOOOO@@@@@OOOOOO@OO^...       ....           
# OOOO,,/............^,@@O\@^@O/\//OO@@@@@@@@@@@@@@@@OOO/OOOOOO@O\@OOO@@@@@O]]\]]/O@\OOOOOOOOO@O...         ..           
# =OO/.................@@OO@@@=]oo^OOO@@@@@OOOOOO/OO@O@@@@\OOOOOO@@@@/OOOOOO@@@@@@@@@@@OO@@@@@@@^.                       
# ............,\O`.....,@O@@@OO@/\/OOOOO@@@OOOOOOOOOOOO@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@^.                       
# ............/@^........\/OOOOOO@@O/OOO@@OOOOOOOOOOOOOOOOOO\@O@@@@@@@@@@@@@@@@@@@@@@@@OOOOOO@@@^.                       
# .. ... .....^*,].........\@O/@@@@@@@@@@@@@@@@@@OOOo/O@@@@@@O/o@@@@@@@@@@@@@@@OO@@@@@@@OOOOOOO@^.              ..       
# ............\,***[].......=@@@@@@@@@@@@@@@@@@@@@@@@@@@@@OOOOOoO\@@@@@@@@OO@O@OOOOOOO@@OOOOO@@@^.  ..        ......     
# ... .........\,***,*[`......@oO@@@@@@@@@@@@@@@@@@@@@@\/OOoO/O/`*\@@@@@@@OOOOO@OOOOOOO\\OOOOOO@^..   ...       ..   .   
# ....... .......\\,*``*,[]...,@OO@@@@@@@@@@@@@@@@@@[ooooo@/^*]/O\/\@@@@@OOOO@@@OOOOOOOOOO@OOOOO\..               ....   
# .................,@@]*^,,*``**,\\@@@@@@@@@@@@@/@\oOO[]]/@\oooooooo\@@@@O@OOO@@O@@@OO\OOO@@OOOO@..               ...... 
# ....    ............[@//]]`****]\]/@@@@@@@@@O@OOOooooooooooooOooO@\\/@@@@@@@OO/@@@@@@@@@OOOOOOO\....                   
# ....  .... .... .......,\Oo//[]*^ooooooo\/@@ooOoooooOoooooOoO/`.//ooO\@@@@@@@/O@OO/@@@@@@@/OOOOO^...                   
# .. ...  ....    ..   ......[\[`/=/oooooOooooooooOOOoo/OO[`...,/Ooo\\/./@@@@@@@@@OOOO\\@@@@@@@O@@@.....                 
# ......  ....           ........[\O/[[[[[OO[[[[[\O/[`.......,O/\ooO`..=OO@@@@@@@@@OOOOOOOO@\@OO@@@@.... .               
# ....    ....           .........,/\\......................///O/`......=@@@@@@@@@@OOOOOOOOOO@OO\@@@^.....               
# ....       .            .........*=....................,[///`.........=@@@@@@@@@@OOOOOOOOOOO@O@@@@@.....               
# ...... .                  ..   ...\\................,/][`.......... ..@@@@@@@@@@@@OOOOO@@@O\@@@@@@@@....               
# ........                        ....\`.........]/OO[`.......  .......=@@@@@@@@@@@@@@@O@@@@@@@@@@@@@@^...               
# . .... .... ....              ...........[`.............      .......@@@@@@@/OOO@@@@@@@@@@@@@@/@@@O@@^..               
#   ......... ...             .   ..... ..................        ...,/@@@@@@@OOOOO/@@@@@@@OOO@@@@@OOOO@`.               
#   ........  ....                    .    ......   ................/@@@@@@@@@@OOO@OOO@@@@@OOOOO@@@OOOOO@.........       
# .   .....   ....                        .. ..  .         .. ..../@@@@@@@@@@@@@@O@@@@@@@@@@@@/O/@@OOOOOOO/`.... ..      
#    ...    ..           .                                ....../OOO@@@@@@@@@@@@@O@@@@@@@@@@@@@@@=@@OOOO\/O/\.....       
#    .... .           ....                               ...../@OOOOOO@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@OOOO\//O\\.....      
# ........        ...... .                .           ....../@OOOOOOOO@@@@@@@@@@@@@@@@@@OoO@@@@@@@OOOOOOO/o`@]O....      
# ........        .....                   ...         .....,@OOOOOO@@@@@O@=]/[[[@@@@@@@@@OOOOOOO@@OOOOOOOOo/o///`...     
# ..  ...   ..                                    .....,/@@@@@OOO@@@@@@@@\oooooooooooo/o]\\\]]/@@@@OOOOOOO/]@[O`......   
# ##########################################################################################################################

import os
import struct
import argparse
import shutil

old_vs_new = {
    # Acheron
    "dfbf51b2":"93bd0e91",
    "95311311":"17e76a6a",
    "b2c64915":"e88da4d0",
    "2a42c5e4":"1248799e",
    "b8363627":"5788d426",
    "60de0907":"ec57d1b8",
    # Acheronhair
    "18425cc1":"111d47a6",
    "e775bf51":"9745dc50",
    "00acf153":"ee6055e3",
    "f83652e0":"439a6fd7",
    "cb7fd896":"22284dcd",
    "e341feb3":"fbc56473",
    "5ee5cc8d":"6288c7ce",
    "ba560779":"020bb63f",
    # Argenti
    "f94c8a7e":"a4e4c7dc",
    "98b6f3be":"63bb1f26",
    # Argentihair
    "040c8f95":"ac883ae6",
    "3214c162":"78c72ec8",
    "6f2967cb":"cc1a18f7",
    "5eede219":"05b75400",
    "179d17fe":"5fab0ace",
    "d066d8b7":"17948e68",
    "4925c9dd":"a13c6f7f",
    # Arlan
    "52e4750b":"52b88238",
    "49f0a509":"d8039952",
    "d1e827e0":"f90343fb",
    "ffaf499a":"2f5ce8b7",
    # Arlanhair
    "21c2354a":"72ad2a8b",
    "1fdfbbdc":"b4c6e6a0",
    # Asta
    "fb0f55f4":"e290fff3",
    "088765db":"687428e3",
    "3cc949c8":"8f61660a",
    "701d9092":"8893d921",
    # Astahair
    "cde8d751":"1ca6cf3d",
    "4e29dad2":"967c0759",
    "ed4eea96":"a6d492d3",
    "6406c03e":"4f796933",
    "84668635":"36a13222",
    "9bd1710d":"2ec320aa",
    "8206809f":"7fd9c40d",
    # Aventurine
    "982bd8c4":"53bdb739",
    "53c4098f":"b1cd8482",
    "6c801b21":"115d50a7",
    # Aventurinehair
    "c4c588df":"2a1a1775",
    "015c8a86":"8de65cb9",
    "f3f2b624":"dbef38cc",
    "811fa2ca":"32da43dd",
    "015f4887":"59d6021b",
    "7f4af1d5":"7e21ce24",
    "3bbbdfcc":"4699613b",
    # Bailu
    "e3ea3823":"e430e059",
    "74d8fa7a":"c42c0455",
    "de6e235f":"e468513a",
    "bdab2370":"8d372ffc",
    # Bailuhair
    "d1df61ab":"1a6134dc",
    "dfe514d8":"dcc96667",
    # Blackswan
    "4ce38332":"a5727e55",
    "5527e772":"7884691d",
    "01f66a63":"d037ddd6",
    # Blackswanhair
    "5d782765":"9f71dd91",
    "4013a662":"b97825d7",
    # Blade
    "1082d394":"6166ea57",
    "459ea4f3":"a273cfa3",
    "409cd5c1":"3a1b9bb1",
    "bdbde74c":"647809bd",
    # Bladehair
    "419db05a":"89af9f25",
    "71b698d8":"dd309961",
    "260391f8":"aab6366e",
    "ff18d193":"f646a974",
    "60d6a2c4":"ab8b5a42",
    "7e354cb4":"7cbac9fe",
    "32919d62":"bc05281a",
    # Boothill
    "845f6f6b":"f261312e",
    "37a8d30b":"41968d4e",
    "3f2237f3":"5183fce7",
    "d0fb7df5":"f8dd7e43",
    "87f245a6":"3c3ec92a",
    "6d0a3848":"bd451832",
    "f914a7fe":"f36e4a49",
    # Boothillhair
    "1e9505b5":"da526c12",
    "8dccfaa1":"ea00cebd",
    # Bronya
    "0b49e488":"3ed22aab",
    "066f1a5a":"b1117be0",
    "e1c9d15e":"da221a45",
    "5161422e":"643fe76a",
    "5547e998":"9a485260",
    "720783d5":"789f1abf",
    "a131325e":"f0bdff24",
    # Bronyahair
    "79319861":"7e9a40be",
    "c476c030":"af5183a6",
    # Caelus
    "28d09106":"3e8e34d5",
    "0fe66c92":"6194fa1b",
    # Caelushair
    "3fc38f8a":"f4f5c11d",
    "7de7f0c0":"fa0975b2",
    "c17e8830":"d75c3881",
    # Clara
    "af43bb7c":"198363bb",
    "ffd2f41b":"d73982e5",
    "ff7a7e5e":"a646bdde",
    "6c866716":"6f4c03fe",
    # Clarahair
    "4c5e718d":"e730fbcc",
    "7fe8d517":"4ecb33c7",
    # Danheng
    "95212661":"72b7f37b",
    "5e3149d6":"01999151",
    # Danhenghair
    "02394eab":"62604aad",
    "98fd88ae":"e4fd41ae",
    # DrRatio
    "d8ae56ba":"e80725f3",
    "9fa75d99":"4329d27b",
    # DrRatiohair
    "fbcffe5a":"b310931e",
    "5ca10450":"7a9d0dac",
    "03b5a3cf":"7d37a021",
    "26a8f257":"650888fc",
    "76d7d3f3":"0a520e04",
    "013f4f5d":"521b3d2d",
    "8eccb31c":"5a50e9ba",
    # Firefly
    "8330592e":"da829543",
    "30c7e54e":"69752923",
    "4c318da2":"681937c7",
    "274d9c39":"f57c4e74",
    "977bcde9":"423c22f1",
    "b5be8f4f":"70c1071f",
    "04ea14b2":"3f9e2b37",
    "078177f1":"70c1071f",
    "b5be8f4f":"3f9e2b37",
    # Fuxuan
    "9e822610":"6455fc0a",
    "50b30274":"4ba289bf",
    "0172c74d":"09c78c66",
    "d9171ad6":"ce81f2e6",
    "74a3b00f":"084c8cd5",
    "02291372":"c7b3e7bd",
    "cccc3f30":"bd7bfe77",
    # Fuxuanhair
    "73b1fe83":"f498555d",
    "df067d4d":"afb05dab",
    "dfc8fb64":"d4b96cd1",
    # Gallagher
    "4902ec09":"585134a8",
    "851877a3":"39bf93ba",
    "39f47ff7":"585134a8",
    "2f609ba4":"39bf93ba",
    # Gallagherhair
    "3464c771":"4ce0e733",
    "e2a6c3dd":"b0198c11",
    "2bb27259":"d9d4ed61",
    "8a910c8c":"9023270b",
    "f5c82676":"e9f3a740",
    "8590504d":"0adf3bf9",
    "69d380ac":"b1f5a889",
    # Gepard
    "19731fb9":"e70c5ef2",
    "da172387":"2ca81203",
    "369fb8ef":"aff5c287",
    "2482636f":"2ba5e966",
    # Gepardhair
    "71ba118e":"a4d9351f",
    "12718dd9":"00e5e932",
    # Guinaifen
    "e73b9426":"b710c78e",
    "d6a8cff9":"4463cc21",
    "d5d770b0":"ae6de86c",
    "a72e61d5":"4092649e",
    "08ba5697":"3309ae7e",
    # Guinaifenhair
    "c88f1557":"fbd7db30",
    "33043521":"c6e13e26",
    # Hanya
    "b6dea863":"3a1da416",
    "b4d0253c":"7c08d55d",
    "e7afec9f":"d927b45a",
    "c2817103":"537979fe",
    "4fb6b5f3":"4f159928",
    "e58be0fd":"8878e228",
    # Hanyahair
    "8bc1d1db":"7b9e82c5",
    "18503e31":"44c3983d",
    # Herta
    "01057b08":"e07c10c9",
    "22d89ecd":"b878ef55",
    # Hertahair
    "d53e94bd":"ee995067",
    "84c9c04b":"515a7733",
    # Himeko
    "f4b0bd6d":"62d53b1f",
    "4747010d":"d122877f",
    "16008525":"947bc57e",
    "b9e9ae3b":"2bf29f1f",
    "e79e4018":"2dc0061c",
    "e2f15a68":"6920fe29",
    "27bf0a6a":"520336ef",
    "24e4c5ad":"a769be88",
    "ce965b0d":"094b77c6",
    "3cfb3645":"5212e2f9",
    # Himekohair
    "c08f4727":"fa440b40",
    "fc068361":"d4634d6f",
    "9adcae2d":"a700d6b4",
    # Hook
    "b8d85743":"8ab99329",
    "a49680b5":"4a45ac95",
    # Hookhair
    "fcd7ee7b":"f1ca01f3",
    "a8e81b3a":"db6ff34c",
    # Huohuo
    "70d3fdb7":"6598aacd",
    "6e5470a5":"afac01be",
    # Huohuohair
    "f8d072c0":"057f648d",
    "c0f8d106":"772090fc",
    # Jade
    # Jingliu
    "bdbc6dce":"74370924",
    "5f55eaff":"d3a91ee8",
    # Jingliuhair
    "1bc1cfa0":"f73f74cb",
    "fbcefb7e":"70ae9680",
    # Jingyuan
    "48c0277a":"26735526",
    "7dfa92fa":"d5b2a23a",
    "fd74f596":"b1b4f581",
    "9fe0c156":"16a2d8bb",
    # Jingyuanhair
    "1da0a14c":"1ac1a7fb",
    "97eb13d9":"9f47fa33",
    # Kafka
    "05ded7f7":"d14b435e",
    "0da4c671":"207c0559",
    "cc322c0f":"32b5b281",
    "e8e2b6da":"c00b55bc",
    "7bd0d180":"45d15ffb",
    "ec622d99":"de10a9ba",
    "339785c4":"fd0ef162",
    "11b4a777":"92b3b7fc",
    # Kafkahair
    "cd60c900":"ddbe6ba2",
    "55d258a5":"cb354b6b",
    "dc6aaf17":"e07efe45",
    # Luka
    "3ba22ed5":"a026c901",
    "31724118":"1762e62c",
    "73fa89cd":"00970f33",
    "58749091":"31483729",
    # Lukahair
    "2427134f":"6e34ac83",
    "c6b43fae":"6d784dff",
    # Lunae
    "85486705":"9300840e",
    "ef65d29c":"b0660300",
    # Lunaehair
    "5f6f803e":"779e60a8",
    "ec8baa47":"41840f8a",
    # Luocha
    "f9d9adb8":"7185fd68",
    "d8dd2b05":"eb99eb88",
    "a1fac228":"65dec275",
    "ff928485":"45feb69d",
    # Luochahair
    "17542aca":"9420ae03",
    "dadf8929":"a7e6fa4f",
    # Lynx
    "52a44eba":"bffadc55",
    "e2bad880":"6c664cc4",
    "6cb92f15":"540bf4e4",
    # Lynxhair
    "6d27e7f2":"f4db275c",
    "a874888b":"8dc79479",
    # March7th
    "ecf4648c":"b950fe40",
    "e6b35ac0":"a9101746",
    "8c584d30":"87f4596d",
    "b57574b3":"cada1307",
    "2006cd6a":"01f9dbb8",
    # March7thhair
    "1ed7e59d":"948c4e59",
    "6bd71ad9":"e299099f",
    "371ca498":"89cd27c7",
    # Misha
    "157dc503":"2b17a6a5",
    "429f63a8":"ce79ee01",
    # Mishahair
    "c49badcb":"cdc4b6ac",
    "4b221f10":"af206cba",
    "532230d3":"3ae2fc69",
    "9980f41b":"e35c9a5a",
    "66e3518a":"08e4fb11",
    "028905ee":"328e0604",
    "8e793185":"f66cebd0",
    # Natasha
    "b9b8b2a1":"f1668e08",
    "209f5c65":"6f4ab910",
    "bfd47fe8":"fe813491",
    "3bd51af4":"519ef69f",
    "2799f499":"919da513",
    "a4f72298":"c4656600",
    "70a82ea1":"87b946e4",
    "de96634b":"236df0fa",
    "88be8df6":"defb30fc",
    # Natashahair
    "5f44fc0d":"a9728390",
    "595464a6":"08ac31d1",
    "abcc21d1":"260f2286",
    # Pela
    "e02d100c":"48fca7f8",
    "ffeb1d46":"21d34147",
    "354f9b31":"3e8cd724",
    # Pelahair
    "934172e5":"7fcd70ea",
    "54a11a98":"93279a4a",
    # Qingque
    "55e1b1f8":"311daa47",
    "e6160d98":"82ea1627",
    "05c192d9":"109719da",
    "cc2db614":"d97fd893",
    "0a82ceb7":"21856dc2",
    "ff995bd0":"d92826b3",
    "2d563efe":"a85d8219",
    "149c086c":"92c74827",
    "2b135afe":"f57f3990",
    # Qingquehair
    "73fbbace":"d9e91d27",
    "48829296":"ddabcef6",
    # Robin
    "312e2c95":"de39f5f2",
    "4c249936":"57ba7e2a",
    "9e6b5969":"e5ed0f89",
    # Robinhair
    "490e6507":"b7d76947",
    "63aafaed":"445abbfc",
    # Ruanmei
    "fe8145b1":"5387a03e",
    "9b63577a":"93eec3ab",
    # Ruanmeihair
    "f6491dae":"22e8a12f",
    "45e0fe2c":"0198e0df",
    # Sampo
    "2bdcc496":"b9371b3c",
    "a81589e4":"e0274b6f",
    "3ac42f7d":"15761df0",
    "85c01194":"297b7f7c",
    "e15ccf04":"1251e25b",
    "92065503":"4fd99756",
    "333b2634":"992d119f",
    # Sampohair
    "75824b32":"31447b51",
    "e07731c5":"3095786c",
    "2d7aefc0":"d4ab62d7",
    "529994b6":"5974af55",
    "d2e6ad9b":"96243edc",
    "ec28a787":"36d62e76",
    "22c6ec2c":"989a13bb",
    # Seele
    "fe54239f":"17cba38d",
    "8daeb19c":"600c3a12",
    "b06965df":"14bb544b",
    "1747ac60":"8e550df4",
    "32df70e0":"c6db3a14",
    # Seelehair
    "8f3bec58":"ebc707dd",
    "4122931f":"da303c25",
    # Serval
    "8d159053":"1bc2fa5f",
    "7e8fa12b":"a05979e4",
    "269745d0":"5be64601",
    "725d36ab":"c7bd5694",
    "0647e843":"c7358fb2",
    # Servalhair
    "59d7157b":"21e4c3cd",
    "86144243":"79709858",
    # Silverwolf
    "21ff348c":"17906457",
    "ab13f8b8":"6c945131",
    "e8f10ab3":"891ecaae",
    "76d6dd31":"b2f97e36",
    "84b3170b":"7b1eface",
    # Silverwolfhair
    "d28049f2":"293abc6c",
    "b2d04673":"520314e4",
    "1ffdd958":"567d08be",
    "6f9922fe":"b9254611",
    "3608ba80":"91db78c2",
    "56893677":"7c7065ae",
    "dd608b21":"cf2cb5b7",
    # Sparkle
    "fac7d488":"17999c91",
    "a4974a51":"f806d2e4",
    # Sparklehair
    "1d7ed602":"a4f91fac",
    "07b2e4b7":"df96b015",
    # Stelle
    "a19a8d2c":"78d10c03",
    "5d15eefe":"69014337",
    # Stellehair
    "fdb54553":"a04fcf6f",
    "ef5586c1":"02a9b085",
    # Sushang
    "e4ccda3f":"98507746",
    "653b35cd":"3134e1e4",
    "4724e9c1":"79354f80",
    "d2e9d4dc":"1e9893b3",
    # Sushanghair
    "95e614e5":"636dc89e",
    "728565ee":"0e484aa5",
    # Tingyun
    "77ddf35c":"ed473e73",
    "547497fb":"e0fa7d8e",
    "1cbf0500":"bf7501ab",
    "73fad5f5":"fa54a59b",
    # Tingyunhair
    "02a81179":"c4be701a",
    "fa9143b8":"f699e83b",
    # Topaz
    "436288c9":"4be08333",
    "96f5e350":"3dfd62b8",
    "6a0ee180":"b8c954ef",
    "68b887db":"13be2437",
    "924edd3e":"786f6565",
    # Topazhair
    "0dd40a0b":"cc870789",
    "7fac28de":"a413be23",
    "77cef0b5":"cbd71321",
    "b8ec605d":"b131f866",
    "f1a4401b":"32ef4b75",
    "943bf9d3":"78059f75",
    "67df29ec":"39fd4ba7",
    # Welt
    "9261177c":"aa4229a3",
    "c89a97aa":"d318fc3e",
    "b63f51eb":"8cd33bbc",
    "5c9711f2":"948e03bd",
    "3dbb2ae6":"d77a2807",
    # Welthair
    "78ca8241":"8d2fdd4b",
    "6a8dcc20":"9dd3ae5d",
    "2258cc03":"c6f7c43c",
    # Xueyi
    "ad22f871":"e2284397",
    "2e328427":"a694c7ef",
    "957cf6d9":"89724253",
    "76f171f5":"91c7faef",
    # Xueyihair
    "952c20b8":"360ebd7f",
    "dbb181aa":"4d5812b5",
    # Yanqing
    "4e8f9778":"a41345d3",
    "035f0719":"2db9f1d6",
    # Yanqinghair
    "ea81180d":"e5457b98",
    "14629990":"541ba63d",
    "0519a715":"9639c2cb",
    # Yukong
    "b6457bdb":"9e0f6958",
    "052766cf":"220a5367",
    # Yukonghair
    "08d184a7":"6fa27e76",
    "11960703":"40baf876",
}

replacement_mapping = {
    # Firefly
    "423c22f1": {
        "match_first_index = 32976":"match_first_index = 32547",
        "match_first_index = 66429":"match_first_index = 66561",
    },
    # Sampo
    "15761df0": {
        "match_first_index = 20637":"match_first_index = 20655",
    },
    # Silverwolf
    "891ecaae": {
        "match_first_index = 63549":"match_first_index = 63429",
        "match_first_index = 63663":"match_first_index = 63543",
    },
}


def process_folder(folder_path):
    '''Process all the files in the folder and subfolders,
    replacing the old values with the new ones.'''
    for root, dirs, files in os.walk(folder_path):
        for file in [x for x in files if x.lower().endswith('.ini') and x.lower() != 'desktop.ini']:
            file_path = os.path.join(root, file)
            print(f"--> Get in file '{file}' at '{file_path}'")
            try:
                with open(file_path, 'r', encoding="utf-8") as f:
                    s = f.read()
                    # old_stream = s
                if '[disabled1234567890]' in s:
                    print(f"Skipping file '{file}' as it already contains '[disabled1234567890]'")
                    continue
                modified = False
                for old, new in old_vs_new.items():
                    if old in s:
                        s = s.replace(old, new)
                        print(f" -  Hash '{old}' has been replase with '{new}'")
                        modified = True
                
                for key, values in replacement_mapping.items():
                    if key in s:
                        for search_string, replace_string in values.items():
                            if search_string not in s:
                                print(f" -  Not contain the specified string '{search_string}'. Skipping current string")
                                continue
                            else:
                                modified = True
                                if callable(replace_string):
                                    strr = replace_string(key)
                                    s += f'\n\n{strr}'
                                    print(f' -  {search_string[:4]}...{search_string[-4:]} --> {strr[:4]}...{strr[-4:]}')
                                else:
                                    s = s.replace(search_string, replace_string)
                                    print(f' -  {search_string[:4]}...{search_string[-4:]} --> {replace_string[:4]}...{replace_string[-4:]}')
                    else:
                        print(f" -  key '{key}' not in")
                if modified:
                    backup_file_path = os.path.join(root, f"backup_{os.path.splitext(file)[0]}.txt")
                    shutil.copy2(file_path, backup_file_path)
                    print(f" -  Backup created: '{backup_file_path}'")
                    with open(file_path, 'w', encoding="utf-8") as f:
                        f.write(s)
                        print(f'<-- File has been modified!')
                else:
                    print(f'<-- File had no matches. Skipping')
            except Exception as e:
                print(f'Error processing file: {file_path}')
                print(e)
                continue

if __name__ == '__main__':
    process_folder(os.getcwd())
    input('Done!')
