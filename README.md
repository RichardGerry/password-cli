# Password CLI

Command line tool to store and retrieve user names and passwords for the various applications
you use

All data is stored locally


## Requirements

* python 3.5 or higher
* sqlite 3.24 or higher
	+ latest version can be downloaded at https://sqlite.org/download.html (precompiled binaries section)


## Usage

First step after cloning the repo is to install the package:
```console
> pip install path/to/cloned/repo
```

The tool can then be used with the 'pw' command and the following arguments and sub-arguments:

* get
	> retrieve an application user name and password
    + app (label for the application that was stored using the 'set' argument)
	+ --copy (flag, if present the retrieved password is copied to the clipboard and is not displayed on the console)
```console
> pw get my_gmail
```
```console
> pw get my_gmail --copy
```

* set
	> update or add an application user name and password
    + app (whatever label you want to assign to the following user and password)
	+ user (user name for the 'app' to save)
	+ password (password for the 'app' to save)
		- must be longer than 8 characters
```console
> pw set my_gmail some_login some_password
```

* rm
	> remove an application user name and password
    + app (label for the application that was stored using the 'set' argument)
```console
> pw rm my_gmail
```

* dump
	> output the stored data
    + -f, --file (where you want the output written - default is standard output)
	+ --all-data (flag, if present indicates that all the data and metadata stored is output - default is only app name)
	+ --lines (flag, if present indicates that the output data is in csv format - default is json)
```console
> pw dump
```
```console
> pw dump --all-data --lines
```
```console
> pw dump --all-data --file "C:\Users\me\Desktop\some_dir\output.txt"
```
