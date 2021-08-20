#!/usr/bin/env python

import hashlib
import os
import sys
import tempfile
import urllib

import distlib.locators
import github


github_repo = 'cupy/cupy'

all_projects = [
    'cupy-cuda80',
    'cupy-cuda90',
    'cupy-cuda91',
    'cupy-cuda92',
    'cupy-cuda100',
    'cupy-cuda101',
    'cupy-cuda102',
    'cupy-cuda110',
    'cupy-cuda111',
    'cupy-cuda112',
    'cupy-cuda113',
    'cupy-cuda114',
]

all_versions = [
    # PyPI / GitHub release
#    ('9.0.0a2', 'v9.0.0a2'),
    ('8.0.0rc1', 'v8.0.0rc1'),
    ('8.0.0b5',  'v8.0.0b5'),
    ('8.0.0b4',  'v8.0.0b4'),
    ('8.0.0b3',  'v8.0.0b3'),
    ('8.0.0b2',  'v8.0.0b2'),
    ('8.0.0b1',  'v8.0.0b1'),
    ('8.0.0a1',  'v8.0.0a1'),

    ('7.0.0rc1', 'v7.0.0rc1'),
    ('7.0.0b4',  'v7.0.0b4'),
    ('7.0.0b3',  'v7.0.0b3'),
    ('7.0.0b2',  'v7.0.0b2'),
    ('7.0.0b1',  'v7.0.0b1'),
    ('7.0.0a1',  'v7.0.0a1'),
]

def get_pypi_assets(project, version):
    # Return a dict of URL to tuple ('hash-algorithm', 'hash').
    locator = distlib.locators.PyPIJSONLocator('https://pypi.org/pypi')
    proj = locator.get_project(project)
    if version not in proj:
        return {}
    return proj[version].digests


def upload_url_to_github_release(url, algo, hash, release):
    filename = os.path.basename(url)
    for existing_asset in release.raw_data['assets']:
        if existing_asset['name'] == filename:
            print('SKIP: Already exists on GitHub Assets')
            return

    with tempfile.NamedTemporaryFile() as f:
        h = hashlib.new(algo)
        print('  >> downloading', url, 'to', f.name)
        with urllib.request.urlopen(url) as response:
            buf = response.read()
            f.write(buf)
            h.update(buf)
        assert h.hexdigest() == hash

        print('  >> uploading')
        release.upload_asset(f.name, name=filename)



def main():
    token = os.environ.get('GITHUB_TOKEN')
    assert token
    repo = github.Github(token).get_repo(github_repo)

    for project in all_projects:
        for version_pypi, version_gh in all_versions:
            print(f'### {project} {version_pypi}')
            sources = get_pypi_assets(project, version_pypi)
            if len(sources) == 0:
                print('No files found on PyPI.')
                continue

            gh_release = repo.get_release(version_gh)
            for url, (algo, hash) in sources.items():
                print(f'Processing: {gh_release} <- {url} ({algo}: {hash})')
                upload_url_to_github_release(url, algo, hash, gh_release)


if __name__ == '__main__':
    main()
