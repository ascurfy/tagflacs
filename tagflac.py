import musicbrainzngs as mb

mb.set_useragent('tagflac', '0.1', 'scurfielda@gmail.com')

TEST_ARTIST = 'kraftwerk'
TEST_ALBUM = 'Tour De france'


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
            release_details_list.append(release['medium-list'][0]['format'])

            release_dates.append(release['date'][:4])
            
        except KeyError:
            continue

        release_list.append(release_details_list)

    release_dates.sort()

    orig_date = release_dates[0]

    for release in release_list:
        if 'vinyl' in release[-1].lower():
            continue
        else:
            release.append(orig_date)
            final_list.append(release)

    for r in final_list:
        print(r)
    


def menu_choice():
    pass


def process_album():
    pass


def main():
    result = search_album_releases()
    clean_results(result)



if __name__ == '__main__':
    main()

