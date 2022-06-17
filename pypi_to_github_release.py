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
    'cupy-cuda115',
    'cupy-cuda116',
]

github_releases = [
    'v4.0.0',
    'v4.1.0',
    'v4.2.0',
    'v4.3.0',
    'v4.4.0',
    'v4.4.1',
    'v4.5.0',
    'v5.0.0',
    'v5.1.0',
    'v5.2.0',
    'v5.3.0',
    'v5.4.0',
    'v6.0.0',
    'v6.1.0',
    'v6.2.0',
    'v6.3.0',
    'v6.4.0',
    'v6.5.0',
    'v6.6.0',
    'v6.7.0',
    'v7.0.0',
    'v7.1.0',
    'v7.1.1',
    'v7.2.0',
    'v7.3.0',
    'v7.4.0',
    'v7.5.0',
    'v7.6.0',
    'v7.7.0',
    'v7.8.0',
    'v8.0.0',
    'v8.1.0',
    'v8.2.0',
    'v8.3.0',
    'v8.4.0',
    'v8.5.0',
    'v8.6.0',
    'v9.0.0',
    'v9.1.0',
    'v9.2.0',
    'v9.3.0',
    'v9.4.0',
    'v9.5.0',
    'v9.6.0',
    'v10.0.0',
    'v10.1.0',
    'v10.2.0',
    'v10.3.0',
    'v10.3.1',
    'v10.4.0',
    'v10.5.0',
]

all_versions = [
    # PyPI / GitHub release
    (v.lstrip('v'), v) for v in github_releases
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

    for project in reversed(all_projects):
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
