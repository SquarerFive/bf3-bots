import os
import csv
# paths_to_search = ['Persistence/Unlocks/Soldiers/Visual/MP/Us/', 'Persistence/Unlocks/Soldiers/Visual/MP/RU/']
paths_to_search = ['Gameplay/Kits/']

paths = {
    'Kits': {
        'path': ['Gameplay/Kits/'],
        'exclude': []
    },
    'Weapons': {
        'path': ['Weapons/'],
        'exclude': ['Accessories', 'Common']
    },
    'Unlocks': {
        'path': ['Persistence/Unlocks/Soldiers/Visual/MP/Us/', 'Persistence/Unlocks/Soldiers/Visual/MP/RU/']
    }
}

data = [
    ('Name', 'Category', 'US', 'RU')
]

for assetType in list(paths.keys()):
    for path in paths[assetType]['path']:
        for root, dirs, files in os.walk(path, topdown=False):
            for name in files:
                pathname = root + (name.split(".txt")[0])
                filter = False
                is_us = True
                is_ru = True
                if assetType == 'Weapons':
                    if name[0] == 'U':
                        filter = False
                    else:
                        filter = True
                if assetType == 'Kits':
                    is_us = name.lower()[0:2] == 'us'
                    is_ru = name.lower()[0:2] == 'ru'
                if assetType == 'Unlocks':
                    is_us = name.lower()[3:5] == 'us'
                    is_ru = name.lower()[3:5] == 'ru'
                    # print(is_us, is_ru)
                if not filter:
                    data.append((pathname, assetType, 1 if is_us else 0, 1 if is_ru else 0))


with open('assets.csv', 'w', newline="") as f:
    csv_writer = csv.writer(f, delimiter=',', quotechar='|')
    csv_writer.writerows(data)


#for path in paths_to_search:
#    for root, dirs, files in os.walk(path, topdown=False):
#        print(dirs)
#        for name in files:
#            pathname = root + (name.split(".txt")[0])
#            #is_us = path.split("/")[-2].lower()=='us'
#            #is_ru = path.split("/")[-2].lower()=='ru'
#            is_us = name.lower()[0:2] == 'us'
#            is_ru = name.lower()[0:2] == 'ru'
#            print(is_us)
#            print(is_ru)
#            # print(is_us)
#            data.append((
#                pathname, 'Kit', 1 if is_us else 0, 1 if is_ru else 0
#            ))
#
#
#with open('kits.csv', 'w') as f:
#    csv_writer = csv.writer(f, delimiter=',', quotechar='|')
#    csv_writer.writerows(data)

