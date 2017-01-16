#!/usr/bin/env python3

import argparse
import musicbrainzngs as mb

mb.set_useragent('tagflac', '0.0.3', 'scurfielda@gmail.com')


def get_arguments():
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--searchalbum')
    parser.add_argument('--searchartist')
    parser.add_argument('--filename')

    args_dict = vars(parser.parse_args())

    return args_dict


    
def search_album_releases(args_dict):

    search_release = mb.search_releases(release=args_dict['searchalbum'], artist=args_dict['searchartist'], strict=True)

    return search_release



def clean_results(search_release):

    release_list = []
    release_dates = []
    final_list = []

    for release in search_release['release-list']:
        release_details_list = []
        try:
            release_details_list.append(release['id'])
            release_details_list.append(release['artist-credit'][0]['artist']['name'])
            release_details_list.append(release['title'])
            release_details_list.append(release['date'][:4])
            release_details_list.append(release['label-info-list'][0]['catalog-number'])
            release_details_list.append(release['label-info-list'][0]['label']['name'])
            release_details_list.append(release['medium-list'][0]['track-count'])
            if 'disambiguation' in release:
                release_details_list.append(release['disambiguation'])
            else:
                release_details_list.append('[none]')
            release_details_list.append(release['medium-list'][0]['format'])

            release_dates.append(release['date'][:4])
            
        except KeyError:
            continue

        release_list.append(release_details_list)

    release_dates.sort()

    orig_date = release_dates[0]

    for release in release_list:
        if 'vinyl' in release[-1].lower() or 'cassette' in release[-1].lower():
            continue
        else:
            release.append(orig_date)
            final_list.append(release)

    return final_list
        
    


def menu_choice(release_list):
    
    for index, value in enumerate(release_list):
        print('{:^3}{:^25}{:^25}{:^25}{:^25}{:^20}{:^20}{:^20}'.format(index + 1, value[1],
                                                                       value[2], value[3],
                                                                       value[5], value[4],
                                                                       value[8], value[7]))

    choice_int = int(input('Select release: ')) - 1

    album_details = mb.get_release_by_id(release_list[choice_int][0], includes=['recordings', 'artist-credits', 'labels'])

    return album_details, release_list[choice_int]
        


#def process_album(release_choice):
#    print(release_choice)
#    album_details = mb.get_release_by_id(release_choice[0], includes=['recordings', 'artist-credits', 'labels'])
#    tag_details = {'ALBUMARTIST': release_choice[1],
#                   'ALBUM': release_choice[2],
#                   'TRACKTOTAL': str(release_choice[6]).zfill(2),
#                   'DATE': release_choice[9],
#                   'DISCTOTAL': str(album_details['release']['medium-count']).zfill(2),
#                   'DISCNUMBER': []
#                   }
#      
#    track_list = {}
#    #print(album_details)
#    labels_set = {label['label']['name'] for label in album_details['release']['label-info-list']}
#    catnos_set = {label['catalog-number'] for label in album_details['release']['label-info-list']}
#    #print(labels_set)
#    #print(catnos_set)
#    for disc in album_details['release']['medium-list']:
#        
#    
#    for disc in album_details['release']['medium-list']:
#        tag_details['DISCNUMBER'].append([])
#        print('Disc: {} of {}'.format(disc['position'], album_details['release']['medium-count']))
#        tag_details['DISCNUMBER'][int(disc['position']) - 1].append([])
#        for trackno, track in enumerate(disc['track-list']):
#            print(trackno)
#            
#            tag_details['DISCNUMBER'][int(disc['position']) - 1][trackno].append({'TITLE': track['recording']['title']})
#            tag_details['DISCNUMBER'][int(disc['position']) - 1][trackno]['ARTIST'] = track['artist-credit-phrase']
#            print('{} - {} - {}'.format(str(track['number']).zfill(2), track['recording']['title'], track['artist-credit-phrase']))
#    print(tag_details)

def create_comment_tag(album_details, choice):
    
    labels_set = {label['label']['name'] for label in album_details['release']['label-info-list']}
    catnos_set = {label['catalog-number'] for label in album_details['release']['label-info-list']}
    
    labels_list = list(labels_set)
    label_str = ''
    for index, label in enumerate(labels_list):
        if index > 0:
            label_str += ', ' + label
        else:
            label_str = label
            
    catnos_list = list(catnos_set)
    catno_str = ''
    for index, catno in enumerate(catnos_list):
        if index > 0:
            catno_str += ', ' + catno
        else:
            catno_str = catno  
            
    comment_str = '℗' + ' ' + choice[3] + ' - ' + label_str + ' - ' + catno_str
    
    return comment_str

    

def main():
    args_dict = get_arguments()
    result = search_album_releases(args_dict)
    final_choice, choice = menu_choice(clean_results(result))
    create_comment_tag(final_choice, choice)
    #process_album(final_choice)
    

if __name__ == '__main__':
    main()

