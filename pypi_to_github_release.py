#!/usr/bin/env python

import os
import sys

import distlib.locators
import github
import uritemplate


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
]

all_versions = [
    # PyPI / GitHub release
    ('6.0.0rc1', 'v6.0.0rc1'),
    ('6.0.0b3',  'v6.0.0b3'),
    ('6.0.0b2',  'v6.0.0b2'),
    ('6.0.0b1',  'v6.0.0b1'),
    ('6.0.0a1',  'v6.0.0a1'),
    ('5.0.0rc1', 'v5.0.0rc1'),
    ('5.0.0b4',  'v5.0.0b4'),
    ('5.0.0b3',  'v5.0.0b3'),
    ('5.0.0b2',  'v5.0.0b2'),
    ('5.0.0b1',  'v5.0.0b1'),
    ('5.0.0a1',  'v5.0.0a1'),
    ('4.0.0rc1', 'v4.0.0rc1'),
    ('4.0.0b4',  'v4.0.0b4'),
]

def get_pypi_assets(project, version):
    # Return a dict of URL and MD5 digest.
    locator = distlib.locators.PyPIJSONLocator('https://pypi.org/pypi')
    proj = locator.get_project(project)
    if version not in proj:
        return {}

    digests = proj[version].digests
    assert all([x[0] == 'md5' for x in digests.values()])
    return {url: x[1] for url, x in proj[version].digests.items()}


def upload_url_to_github_release(url, release):
    filename = os.path.basename(url)
    for existing_asset in release.raw_data['assets']:
        if existing_asset['name'] == filename:
            print('SKIP: Already exists on GitHub Assets')
            return
    print(f'TODO: upload to {release.upload_url}')



def main():
    token = os.environ.get('GITHUB_TOKEN', None)
    repo = github.Github(token).get_repo(github_repo)

    for project in all_projects:
        for version_pypi, version_gh in all_versions:
            print(f'### {project} {version_pypi}')
            sources = get_pypi_assets(project, version_pypi)
            if len(sources) == 0:
                print('No files found on PyPI.')
                continue

            gh_release = repo.get_release(version_gh)
            print(gh_release)
            for src, md5 in sources.items():
                print(f'Uploading: {src} (md5: {md5})')
                upload_url_to_github_release(src, gh_release)


if __name__ == '__main__':
    main()
