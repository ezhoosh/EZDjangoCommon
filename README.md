# common

# Installation

run this command to install the package:

``` bash
pip install git+https://github.com/ezhoosh/EZDjangoCommon.git
```

or if the repo is private:

``` bash
pip install git+ssh://git@github.com/ezhoosh/EZDjangoCommon.git
```

add these packages to INSTALLED_APPS:

``` python
INSTALLED_APPS = [
    'unfold', # before django.admin.contrib
    'EZDjangoCommon',
    'image_uploader_widget',
    'tinymce',
    ...
]
```
