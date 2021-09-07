from setuptools import setup

with open('README.md', 'rt', encoding='utf-8') as f:
    long_desc = f.read()

module = __import__('async_task_helpers')
version = module.__version__
license = module.__license__
author = module.__author__
del module

packages = [
    'async_task_helpers'
]

# Setup module
setup(
    # Module name
    name="async_task_helpers",
    # Module version
    version=version,
    # License - MIT!
    license=license,
    # Author (Github username)
    author=author,
    # Author`s email.
    author_email="lapis0875@kakao.com",
    # Short description
    description="Simple asynchronous task helpers",
    # Long description in REAMDME.md
    long_description_content_type='text/markdown',
    long_description=long_desc,
    # Project url
    url="https://github.com/Lapis0875/async_task_helpers",
    project_urls={
        "Issue tracker": "https://github.com/Lapis0875/async_task_helpers/issues",
        'Donate': 'https://www.patreon.com/lapis0875'
    },
    packages=packages,
    # Module`s python requirement
    python_requires=">=3.7.0",
    # Keywords about the module
    keywords=["asyncio", "task", "loop task"],
    # Tags about the module
    classifiers=[
        "Programming Language :: Python :: 3.7",
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)