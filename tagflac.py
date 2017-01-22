#!/usr/bin/env python3

'''
Script to tag and rename flac files to my particular format.

Works from the commandline.

Requires musicbrainzngs module and metaflac.

The files will be renamed to the following format:

    albumartist_album_tracknumber-tracktotal.flac
    albumartist_album_discnumber-disctotal_tracknumber-tracktotal.flac

The following tags will be added:

    ALBUM - The title of the album/single/EP.
    ALBUMARTIST - The overall artist for the release.
    DATE - The original release year. e.g. The Beatles, 1967 not 2009.
    COMMENT - A summery of the source for the flac files in the format - ℗ release year | label/s | catalog number/s.
    TRACKTOTAL - Number of tracks as a 2 digit number.
    DISCTOTAL - Only on multidisc releases. As a 2 digit number.
    DISCNUMBER - Only on multidisc releases. As a 2 digit number.
    TRACKNUMBER - A 2 digit track number.
    TITLE - Individual track title.
    ARTIST - The performer on the individual track.
    
'''


import argparse
import os
import subprocess

import musicbrainzngs as mb


mb.set_useragent('tagflac', '0.9.0', 'scurfielda@gmail.com')


def get_arguments():
    '''
    Get arguments from commandline and return a dictionary.
    '''
    
    parser = argparse.ArgumentParser()

    parser.add_argument('--searchalbum')
    parser.add_argument('--searchartist')
    parser.add_argument('--filename')

    args_dict = vars(parser.parse_args())

    return args_dict


def search_album_releases(args_dict):
    ''' Search music brainz and return releases matching search criteria.'''

    search_release = mb.search_releases(release=args_dict['searchalbum'], artist=args_dict['searchartist'], strict=True)

    return search_release


def clean_results(search_release):
    '''
    Gather required info from each release and returns a list of results.
    '''

    release_list = []
    release_dates = []
    final_list = []
    for release in search_release['release-list']:
        catnos_set = set()
        catnos_str = ''
        labels_set = set()
        labels_str = ''
        release_details_list = []
        try:
            for label in release['label-info-list']:
                try:
                    catnos_set.add(label['catalog-number'])
                    labels_set.add(label['label']['name'])
                except KeyError:
                    continue
        except KeyError:
            continue
        for catno in catnos_set:
            catnos_str += catno + ', '
        for label in labels_set:
            labels_str += label + ', '
        try:
            release_details_list.append(release['id'])
            release_details_list.append(release['artist-credit'][0]['artist']['name'])
            release_details_list.append(release['title'])
            release_details_list.append(release['date'][:4])
            release_details_list.append(catnos_str.strip(', '))
            release_details_list.append(labels_str.strip(', '))
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
    # Find the oldest release date from all the dates of all releases. Use this for the DATE tag.
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
    '''
    Present a list of releases. Returns final choice.
    '''
    for index, value in enumerate(release_list):
        print('---{}---'.format(index + 1))
        print('Artist: {}'.format(value[1]))
        print('Album: {}'.format(value[2]))
        print('Release details: {} - {} - {} - {}'.format(value[8], value[3], value[5], value[4]))
        print('Notes: {}'.format(value[7]))
        
        print()

    choice_int = int(input('Select release: ')) - 1

    album_details = mb.get_release_by_id(release_list[choice_int][0], includes=['recordings', 'artist-credits'])

    album_details['origdate'] = release_list[choice_int][-1]
    album_details['all_labels'] = release_list[choice_int][5]
    album_details['all_catnos'] = release_list[choice_int][4]

    return album_details
        

def tag_and_rename(album_details, args_dict):
    '''
    Tags and renames each track.
    '''
    trackno_index = str(args_dict['filename']).find('01')

    cwd_str = os.getcwd()

    for file in os.listdir('.'):
        if file.startswith(args_dict['filename'][:8]) and file.endswith('.flac'):

            flac_path = cwd_str + '/' + file

            if file.rfind('disc') != -1:
                discno = int(file[file.rfind('disc') + 4:file.rfind('disc') + 5])
            else:
                discno = 1

            disc_details = album_details['release']['medium-list'][discno - 1]
            trackno = str(file[trackno_index:trackno_index + 2]).zfill(2)
            albumartist = album_details['release']['artist-credit-phrase']
            album = album_details['release']['title']
            date = album_details['origdate']
            releasedate = album_details['release']['release-event-list'][0]['date'][:4]
            labels = album_details['all_labels']
            catnos = album_details['all_catnos']
            tracktotal = str(disc_details['track-count']).zfill(2)
            title = disc_details['track-list'][int(trackno) - 1]['recording']['title']
            artist = disc_details['track-list'][int(trackno) - 1]['artist-credit-phrase']
            disctotal = album_details['release']['medium-count']

            subprocess.run(['metaflac', '--remove-all-tags', flac_path])
            subprocess.run(['metaflac',
                            '--set-tag=ALBUMARTIST=' + albumartist,
                            '--set-tag=ALBUM=' + album,
                            '--set-tag=DATE=' + date,
                            '--set-tag=COMMENT=℗ {} - {} - {}'.format(releasedate, labels, catnos),
                            '--set-tag=TRACKTOTAL=' + tracktotal,
                            '--set-tag=TRACKNUMBER=' + trackno,
                            '--set-tag=TITLE=' + title,
                            '--set-tag=ARTIST=' + artist,
                            flac_path])

            if disctotal > 1:
                subprocess.run(['metaflac',
                                '--set-tag=DISCTOTAL=' + str(disctotal).zfill(2),
                                '--set-tag=DISCNUMBER=' + str(discno).zfill(2),
                                flac_path])
                new_flacname_str = '{}_{}_{}-{}_{}-{}.flac'.format(albumartist.replace(' ', ''),
                                                                   album.replace(' ', ''),
                                                                   str(discno).zfill(2),
                                                                   str(disctotal).zfill(2),
                                                                   str(trackno).zfill(2),
                                                                   str(tracktotal).zfill(2))
            else:
                new_flacname_str = '{}/{}_{}_{}-{}.flac'.format(cwd_str,
                                                                albumartist.replace(' ', ''),
                                                                album.replace(' ', ''),
                                                                str(trackno).zfill(2),
                                                                str(tracktotal).zfill(2))
            os.rename(flac_path, new_flacname_str)

            print(new_flacname_str)
            subprocess.run(['metaflac', '--list', '--block-number=2', new_flacname_str])


def main():
    args_dict = get_arguments()
    result = search_album_releases(args_dict)
    final_choice = menu_choice(clean_results(result))
    tag_and_rename(final_choice, args_dict)

if __name__ == '__main__':
    main()

