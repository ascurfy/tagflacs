import musicbrainzngs as mb

mb.set_useragent('tagflac', '0.1', 'scurfielda@gmail.com')

TEST_ARTIST = 'the beatles'
TEST_ALBUM = 'the beatles'


def search_album_releases():
    search_release = mb.search_releases(release=TEST_ALBUM, artist=TEST_ARTIST, strict=True)
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
    print('{:^3}{:^25}{:^25}{:^25}{:^25}{:^20}{:^20}{:^20}'.format('', 'Artist',
                                                                   'Album', 'Release Date',
                                                                   'Record Label', 'Catalog Number',
                                                                   'Format', 'Notes'))
    for index, value in enumerate(release_list):
        print('{:^3}{:^25}{:^25}{:^25}{:^25}{:^20}{:^20}{:^20}'.format(index + 1, value[1],
                                                                       value[2], value[3],
                                                                       value[5], value[4],
                                                                       value[8], value[7]))

    choice_int = int(input('Select release: ')) - 1

    return release_list[choice_int]
        


def process_album(release_choice):
    tracks = mb.get_release_by_id(release_choice[0], includes=['recordings', 'artist-credits'])
    print(tracks)
    track_list = {}
    for track in tracks['release']['medium-list'][0]['track-list']:
        print(str(track['number']).zfill(2), track['recording']['title'], track['artist-credit-phrase'])
    for track in tracks['release']['medium-list'][1]['track-list']:
        print(str(track['number']).zfill(2), track['recording']['title'], track['artist-credit-phrase'])
    pass

    


def main():
    result = search_album_releases()
    final_choice = menu_choice(clean_results(result))
    process_album(final_choice)
    



if __name__ == '__main__':
    main()

