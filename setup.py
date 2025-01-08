#!/usr/bin/env python
import codecs

from setuptools import find_packages, setup


def read_me(filename):
    return codecs.open(filename, encoding='utf-8').read()


setup(
    name='ez-django-common',
    version='1.0.0',
    python_requires='>=3',
    packages=find_packages(),
    include_package_data=True,
    description=(
        'EZDjangoCommon'
    ),
    url='https://github.com/ezhoosh/EZDjangoCommon',
    download_url='https://pypi.python.org/pypi/ez-django-common/',
    author='ezhoosh',
    author_email='ezhoosh@ezhoosh.com',
    keywords="common",
    license='MIT',
    platforms=['any'],
    install_requires=[
        "django",
        "django-unfold",
        "django-tinymce",
        "django-lifecycle",
        "djangorestframework",
        "loguru",
        "kavenegar",
        "drf-spectacular",
        "django-image-uploader-widget",
    ],
    long_description=read_me('README.md'),
    long_description_content_type='text/markdown',
    zip_safe=False,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
    ],
)