"""

osgameclones has the following fields:
'updated', 'video', 'repo', 'license', 'originals', 'status', 'multiplayer', 'info', 'lang', 'feed', 'content', 'images', 'url', 'name', 'framework', 'type', 'development'

mandatory fields are: 'name', 'license', 'type', 'originals'

possible values:
osgc-development: ['active', 'complete', 'halted', 'sporadic', 'very active']
osgc-multiplayer: ['Co-op', 'Competitive', 'Hotseat', 'LAN', 'Local', 'Online', 'Split-screen']
osgc-type: ['clone', 'remake', 'similar', 'tool']
osgc-status: ['playable', 'semi-playable', 'unplayable']
osgc-license: ['AFL3', 'AGPL3', 'Apache', 'Artistic', 'As-is', 'BSD', 'BSD2', 'BSD4', 'bzip2', 'CC-BY', 'CC-BY-NC', 'CC-BY-NC-ND', 'CC-BY-NC-SA', 'CC-BY-SA', 'CC0', 'Custom', 'GPL2', 'GPL3', 'IJG', 'ISC', 'JRL', 'LGPL2', 'LGPL3', 'Libpng', 'MAME', 'MIT', 'MPL', 'MS-PL', 'Multiple', 'NGPL', 'PD', 'WTFPL', 'Zlib']
osgc-content: ['commercial', 'free', 'open', 'swappable']

Mapping osgameclones -> ours

name -> name
type -> keywords, description
originals -> keywords
repo -> code repository
url -> home
feed (-> home)
development -> state
status -> state
multiplayer -> keywords
lang -> code language
framework -> code dependencies
license -> code license / assets license
content -> keywords
info ??
updated not used
images not used
video: not used
"""

import ruamel_yaml as yaml
from difflib import SequenceMatcher
from utils.osg import *

# should change on osgameclones
osgc_name_aliases = {}

# conversion between licenses
osgc_licenses_map = {'GPL2': 'GPL-2.0', 'GPL3': 'GPL-3.0', 'AGPL3': 'AGPL-3.0', 'LGPL3': 'LGPL-3.0', 'LGPL2': 'LGPL-2.1', 'MPL': 'MPL-2.0'}

def similarity(a, b):
    return SequenceMatcher(None, str.casefold(a), str.casefold(b)).ratio()


def unique_field_contents(entries, field):
    """
    """
    unique_content = set()
    for entry in entries:
        if field in entry:
            field_content = entry[field]
            if type(field_content) is str:
                unique_content.add(field_content)
            else:
                unique_content.update(field_content)
    unique_content = sorted(list(unique_content), key=str.casefold)
    return unique_content

if __name__ == "__main__":

    # paths
    similarity_threshold = 0.8
    root_path  = os.path.realpath(os.path.join(os.path.dirname(__file__), os.path.pardir))

    # import the osgameclones data
    osgc_path = os.path.realpath(os.path.join(root_path, os.path.pardir, '11_osgameclones.git', 'games'))
    files = os.listdir(osgc_path)

    # iterate over all yaml files in osgameclones/data folder
    osgc_entries = []
    for file in files:
        # read yaml
        with open(os.path.join(osgc_path, file), 'r') as stream:
            try:
                _ = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise  exc

        # add to entries
        osgc_entries.extend(_)
    print('{} entries in osgameclones'.format(len(osgc_entries)))

    # fix names (so they are not longer detected as deviations downstreams)
    for index, entry in enumerate(osgc_entries):
        name = entry['name']
        if name in osgc_name_aliases:
            entry['name'] = osgc_name_aliases[name]
            osgc_entries[index] = entry

    # which fields do they have
    osgc_fields = set()
    for osgc_entry in osgc_entries:
        osgc_fields.update(osgc_entry.keys())
    print('osgc-fields: {}'.format(osgc_fields))

    # which fields are mandatory
    for osgc_entry in osgc_entries:
        remove_fields = [field for field in osgc_fields if field not in osgc_entry]
        osgc_fields -= set(remove_fields)
    print('mandatory osfg-fields: {}'.format(osgc_fields))

    # some field statistics
    print('osgc-development: {}'.format(unique_field_contents(osgc_entries, 'development')))
    print('osgc-multiplayer: {}'.format(unique_field_contents(osgc_entries, 'multiplayer')))
    print('osgc-type: {}'.format(unique_field_contents(osgc_entries, 'type')))
    print('osgc-languages: {}'.format(unique_field_contents(osgc_entries, 'lang')))
    print('osgc-licenses: {}'.format(unique_field_contents(osgc_entries, 'license')))
    print('osgc-status: {}'.format(unique_field_contents(osgc_entries, 'status')))
    print('osgc-framework: {}'.format(unique_field_contents(osgc_entries, 'framework')))
    print('osgc-content: {}'.format(unique_field_contents(osgc_entries, 'content')))

    # read our database
    games_path = os.path.join(root_path, 'games')
    our_entries = assemble_infos(games_path)
    print('{} entries with us'.format(len(our_entries)))

    # just the names
    osgc_names = set([x['name'] for x in osgc_entries])
    our_names = set([x['name'] for x in our_entries])
    common_names = osgc_names & our_names
    osgc_names -= common_names
    our_names -= common_names
    print('{} in both, {} only in osgameclones, {} only with us'.format(len(common_names), len(osgc_names), len(our_names)))

    # find similar names among the rest
    #for osgc_name in osgc_names:
    #    for our_name in our_names:
    #        if similarity(osgc_name, our_name) > similarity_threshold:
    #            print('{} - {}'.format(osgc_name, our_name))

    for osgc_entry in osgc_entries:
        osgc_name = osgc_entry['name']

        is_included = False
        for our_entry in our_entries:
            our_name = our_entry['name']

            # find those that entries in osgameclones that are also in our database and compare them
            if osgc_name == our_name:
                is_included = True
                # a match, check the fields
                name = osgc_name

                p = ''

                # lang field
                if 'lang' in osgc_entry:
                    languages = osgc_entry['lang']
                    if type(languages) == str:
                        languages = [languages]
                    our_languages = our_entry['code language'] # essential field
                    for lang in languages:
                        if lang not in our_languages:
                            p += ' code language {} missing\n'.format(lang)

                # license
                if 'license' in osgc_entry:
                    licenses = osgc_entry['license']
                    our_code_licenses = our_entry['code license'] # essential field
                    our_assets_licenses = our_entry.get('assets license', [])
                    for license in licenses:
                        # transform
                        if license in osgc_licenses_map:
                            license = osgc_licenses_map[license]
                        if license not in our_code_licenses and license not in our_assets_licenses:
                            p += ' code/assets license {} missing\n'.format(license)

                # framework (capitalization is ignored for now, HTML5 is ignored)
                if 'framework' in osgc_entry:
                    frameworks = osgc_entry['framework']
                    if type(frameworks) == str:
                        frameworks = [frameworks]
                    our_frameworks = our_entry.get('code dependencies', [])
                    our_frameworks = [x.casefold() for x in our_frameworks]
                    frameworks = [x.casefold() for x in frameworks]
                    for framework in frameworks:
                        if framework == 'html5':
                            continue
                        if framework not in our_frameworks:
                            p += ' code dependency {} missing\n'.format(framework)

                # repo (ignore links to sourceforge project pages)
                if 'repo' in osgc_entry:
                    repos = osgc_entry['repo']
                    if type(repos) == str:
                        repos = [repos]
                    our_repos = our_entry['code repository']
                    for repo in repos:
                        if repo.startswith('https://sourceforge.net/projects/'):
                            continue
                        if (repo not in our_repos) and (repo+'.git' not in our_repos): # add .git automatically and try it too
                            p += ' code repository {} missing\n'.format(repo)

                # url (ignore http/https)
                if 'url' in osgc_entry:
                    urls = osgc_entry['url']
                    if type(urls) == str:
                        urls = [urls]
                    our_urls = our_entry['home']
                    our_urls = [x.replace('http://', '').replace('https://', '') for x in our_urls]
                    urls = [x.replace('http://', '').replace('https://', '') for x in urls]
                    for url in urls:
                        if url not in our_urls:
                            p += ' home url {} missing\n'.format(url)

                # status
                if 'status' in osgc_entry:
                    status = osgc_entry['status']
                    our_status = our_entry['state'] # essential field
                    if status == 'playable' and 'mature' not in our_status:
                        p += ' status playable, not mature with us\n'
                    if status != 'playable' and 'mature' in our_status:
                        p += ' status {}, mature with us\n'.format(status)
                    if status == 'unplayable':
                        p += ' status unplayable\n'

                # development
                if 'development' in osgc_entry:
                    development = osgc_entry['development']
                    our_inactive = 'inactive' in our_entry
                    our_status = our_entry['state']  # essential field
                    if development == 'halted' and not our_inactive:
                        p += ' development halted, not inactive with us\n'
                    if (development == 'very active' or development == 'active' or development == 'sporadic') and our_inactive:
                        p += ' development {}, inactive with us\n'.format(development)
                    if development == 'complete' and 'mature' not in our_status:
                        p += ' development complete, not mature with us\n'

                # originals
                our_keywords = our_entry['keywords']
                if 'originals' in osgc_entry:
                    originals = osgc_entry['originals']
                    for original in originals:
                        if 'inspired by ' + original not in our_keywords:
                            p += ' original {} not mentioned\n'.format(original)

                # multiplayer
                if 'multiplayer' in osgc_entry:
                    multiplayer = osgc_entry['multiplayer']
                    if type(multiplayer) == str:
                        multiplayer = [multiplayer]
                    for mp in multiplayer:
                        if mp not in our_keywords:
                            p += ' mp: {} not in keywords\n'.format(mp)

                # content
                if 'content' in osgc_entry:
                    content = osgc_entry['content']
                    if content + ' content' not in our_keywords:
                        p += ' content: {} not in keywords\n'.format(content)

                # type
                if 'type' in osgc_entry:
                    game_type = osgc_entry['type']
                    if game_type not in our_keywords:
                        p += ' type: {} not in keywords\n'.format(game_type)

                if p:
                    print('{}\n{}'.format(name, p))


        if not is_included:
            # a new entry, that we have never seen, maybe we should make an entry of our own
            continue

            print('create new entry for {}'.format(osgc_name))
            file_name = derive_canonical_file_name(osgc_name)
            entry = '# {}\n\n'.format(osgc_name)

            # for now only make remakes or clones of at least playable
            game_type = osgc_entry['type'] # do not overwrite type!
            if game_type not in ('remake', 'clone'):
                continue
            description = '{} of {}'.format(game_type.capitalize(), ', '.join(osgc_entry['originals']))
            entry += '_{}_\n\n'.format(description)


