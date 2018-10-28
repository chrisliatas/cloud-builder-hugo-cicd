#!/usr/bin/env python3
# coding: utf-8

"""
Check Hugo new releases from Hugo GitHub repo and update Dockerfile accordingly

Copyright (c) 2018 Christos Liatas

Based on the original script: https://gitlab.com/pages/hugo/blob/registry/update.py
licensed under MIT license - Spencer Lyon

Usage: update.py
"""

import requests
import os
import re
import json
from git import Repo

COMMIT_MESSAGE = 'Updated {} Dockerfile to version {}.'
GITHUB_API_REPOS = 'https://api.github.com/repos'
DOCKERFILE = 'Dockerfile-hugo-xtnd'
GCRIMGFILE = 'gcrimagelist.json'
UPDATEFILE = 'buildhugo.txt'
NPMREGISTRY = 'http://registry.npmjs.org/-/package/{}/dist-tags'
FRBDOCKERFILE = 'Dockerfile-firebase'
GCRFRBIMGFILE = 'gcrfrbimglist.json'
FRTUPDATEFILE = 'buildfrtls.txt'

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
repo = Repo()


def compare_versions(version1, version2):
    def normalize(v):
        return [int(x) for x in re.sub(r'(\.0+)*$', '', v).split(".")]
    return normalize(version1) >= normalize(version2)


def gcrimagedata(fname):
    jdata = None
    try:
        with open(os.path.join(__location__, fname)) as fh:
            try:
                jdata = json.load(fh)
            except Exception as e:
                print(f'Json read error while processing the file(s) - {e}')
    except IOError:
        print(f'Error accessing file: {fname}')
    return jdata


def compare_version_tags(jsondata, latest_tag, imgname):
    for image in jsondata:
        if image['tags']:
            for tag in image['tags']:
                if compare_versions(tag, latest_tag):
                    print(f'{imgname} image already up to date, nothing to do.')
                    return False
    print(f'GCR contains image(s) for an older {imgname} version.\nUpdating...')
    return True


def get_dockerfile(dcrfile):
    with open(os.path.join(__location__, dcrfile)) as fh:
        rdockerfile = fh.read()
    if not rdockerfile:
        print(f'Failed to get Dockerfile from {__location__}:')
        print(rdockerfile)
        exit(1)
    return rdockerfile.split("\n")


def compare_version_tags_dcr(dcrfile, search_str, latest_tag, imgname):
    dockrv = None
    for line in dcrfile:
        if line.startswith(search_str):
            dockrv = line.split()[2]
            break
    if compare_versions(dockrv, latest_tag):
        print(f'{imgname} image already up to date, nothing to do.')
        return False
    print(f'Dockerfile refers to an older (v{dockrv}) {imgname} version.\nUpdating...')
    return True


def write_repofile(filename, rdata):
    with open(os.path.join(__location__, filename), 'w') as fh:
        fh.write(rdata)


def stage_file(dcrfile):
    repo.index.add([os.path.join(__location__, dcrfile)])


def repo_commit_changes(hgupd, frbupd, hgmsg='', frbmsg=''):
    if hgupd and frbupd:
        cmtmsg = COMMIT_MESSAGE.format('Hugo', hgmsg) + ' ' + COMMIT_MESSAGE.format('Firebase-tools', frbmsg)
    elif hgupd:
        cmtmsg = COMMIT_MESSAGE.format('Hugo', hgmsg)
    else:
        cmtmsg = COMMIT_MESSAGE.format('Firebase-tools', frbmsg)
    # Commit changes
    ncomt = repo.index.commit(cmtmsg)
    # Check
    if (not ncomt) and (ncomt.message != cmtmsg):
        print('Failed to update Dockerfile(s) to repo:')
        exit(1)
    print(cmtmsg)


def write_notify(filename, msg):
    write_repofile(filename, msg)
    # Check
    try:
        with open(os.path.join(__location__, filename)) as fh:
            print(f'New version in {filename}: {fh.read()}')
    except IOError:
        print(f'Error accessing file: {filename}')
        exit(1)


def verify_tag(tagname):
    rtags = repo.tags
    if len(rtags) > 0:
        newtag = [t.name for t in rtags if t.name == tagname]
        if not newtag:
            print(f'Failed to create tag {tagname}:')
            print(rtags)
            exit(0)
    else:
        print('No tags found in repo!')
        print(rtags)
        exit(0)
    print(f'Tag {tagname} created')


def create_repo_tag(hgupd, frbupd, hgmsg='', frbmsg=''):
    if hgupd and frbupd:
        ntag = 'hgv-' + hgmsg + '_' + 'ftv-' + frbmsg
        cmtmsg = COMMIT_MESSAGE.format('Hugo', hgmsg) + ' ' + COMMIT_MESSAGE.format('Firebase-tools', frbmsg)
    elif hgupd:
        ntag = 'hgv-' + hgmsg
        cmtmsg = COMMIT_MESSAGE.format('Hugo', hgmsg)
    else:
        ntag = 'ftv-' + frbmsg
        cmtmsg = COMMIT_MESSAGE.format('Firebase-tools', frbmsg)
    repo.create_tag(ntag, message=cmtmsg)
    # Check
    verify_tag(ntag)


# Get Hugo latest release
rrelease = requests.get(GITHUB_API_REPOS + '/gohugoio/hugo/releases/latest')
if rrelease.status_code != 200:
    print('Failed to get Hugo latest release from GitHub')
    exit(1)

release = rrelease.json()
print(f'Hugo Latest version is {release["name"]}')

# Get Firebase Tools latest release from npmjs
rftrelease = requests.get(NPMREGISTRY.format('firebase-tools'))
if rftrelease.status_code != 200:
    print('Failed to get Firebase-tools latest release from registry.npmjs')
    exit(1)

ftrelease = rftrelease.json()
print(f'Firebase-tools latest version is {ftrelease["latest"]}')

# First check current images' data from project's GCR
imagedata = gcrimagedata(GCRIMGFILE)
frbimgdata = gcrimagedata(GCRFRBIMGFILE)

# If there is an image in the GCR built with the latest Hugo version, do nothing
hgupdate = False
if imagedata:
    hgupdate = compare_version_tags(imagedata, release['name'][1:], 'Hugo')
else:
    # Assume there is no image available in GCR
    hgupdate = True

# If there is an image in the GCR built with the latest Firebase-tools version, do nothing
frbupdate = False
if frbimgdata:
    frbupdate = compare_version_tags(frbimgdata, ftrelease['latest'], 'Firebase-tools')
else:
    # Assume there is no image available in GCR
    frbupdate = True

# Abort if there is nothing to do.
if (not hgupdate) and (not frbupdate):
    exit(0)

# Get Hugo-built Dockerfile from repository and/or Firebase-tools Dockerfile from repository
if hgupdate:
    dockerfile = get_dockerfile(DOCKERFILE)

if frbupdate:
    frbdockerfile = get_dockerfile(FRBDOCKERFILE)

if hgupdate:
    # Find release archive checksum for Hugo release from GitHub
    for asset in release['assets']:
        if re.search('checksums.txt', asset['name']):
            rchecksums = requests.get(asset['browser_download_url'])
            if rchecksums.status_code != 200:
                print('Failed to get checksums file from GitHub')
                exit(1)
            for line in rchecksums.text.split("\n"):
                if f'hugo_extended_{release["name"][1:]}_Linux-64bit.tar.gz' in line:
                    checksum = line[:64]
                    break

    # Replace Hugo env variables in Dockerfile
    for index, line in enumerate(dockerfile):
        if 'ENV HUGO_VERSION' in line:
            dockerfile[index] = f'ENV HUGO_VERSION {release["name"][1:]}'
        if 'ENV HUGO_SHA' in line:
            dockerfile[index] = f'ENV HUGO_SHA {checksum}'

    write_repofile(DOCKERFILE, '\n'.join(dockerfile))
    # add to repo stage
    stage_file(DOCKERFILE)

if frbupdate:
    # Replace Firebase-tools env variables in Dockerfile
    for index, line in enumerate(frbdockerfile):
        if 'ENV FRBTOOLS_VERSION' in line:
            frbdockerfile[index] = f'ENV FRBTOOLS_VERSION {ftrelease["latest"]}'

    write_repofile(FRBDOCKERFILE, '\n'.join(frbdockerfile))
    # add to repo stage
    stage_file(FRBDOCKERFILE)

# Update Dockerfile(s) on repository
repo_commit_changes(hgupdate, frbupdate, release['name'][1:], ftrelease['latest'])

# Create file to notify build-hugo step, and/or firebase-build step to create new build.
if hgupdate:
    write_notify(UPDATEFILE, release['name'][1:])

if frbupdate:
    write_notify(FRTUPDATEFILE, ftrelease['latest'])

# Create new tag to mark the update.
create_repo_tag(hgupdate, frbupdate, release['name'][1:], ftrelease['latest'])

print('Done !')
