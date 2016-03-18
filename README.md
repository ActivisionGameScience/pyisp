# IP to ISP lookup library (includes ASN)

This is a python 3 library that provides IP to ISP lookups.  Given an IP address, it
returns the Autonomous System Number (ASN) and ISP name.

The data is downloaded automatically from http://thyme.apnic.net, and is automatically
refreshed at regular intervals (defaults to 14 days).  The upstream data source
is updated daily.


## Quickstart for Conda users in Linux

Using the `conda` package manager is the quickest way to get going
without building anything:
```
# bootstrap the conda system
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh
/bin/bash Miniconda3-latest-Linux-x86_64.sh

# point to our conda channel
echo "channels:\n  - ActivisionGameScience\n  - defaults" > ~/.condarc

# create and activate an environment that contains pyisp 
conda create -n fooenv python=3.4 pyisp ipython -y
source activate fooenv

# start ipython and you're cooking!
```

## Usage

The API is similar to the Maxmind commercial offering so that it is
easy to switch if necessary.  One difference is that
the namespace `pyisp` is used instead of `geoip2`: 
```
    import pyisp.database as ispdatabase

    reader = ispdatabase.Reader()  # it will fetch its own data
    
    response = reader.isp('1.128.0.0') 

    print(response.autonomous_system_number)  # prints the ASN
    print(response.autonomous_system_organization)  # prints the name of ISP

```

Notice that the arguments to `Reader()` are different from Maxmind's API.
Instead of passing a filename, there are two optional arguments that determine the 
auto-refresh interval and location to write the database locally on disk:
```
    reader = ispdatabase.Reader(refresh_days=7, cache_dir='/tmp')
```
If you pass `cache_dir=None` then nothing will be stored on disk and the
database will be re-downloaded each time the object is instantiated.  Please
be mindful that you do not abuse the upstream datasource.

The default is `cache_dir=''`, which is the current working directory.

## Build

You can build and install manually with the following command:
```
    VERSION="0.1.0" python setup.py install
```
where `0.1.0` should be replaced with whatever tag you checked out.

A conda build recipe is also provided (currently only works in Linux).  Assuming you have your
environment set up (see e.g. https://github.com/ActivisionGameScience/ags_conda_recipes.git),
you can build the package by running
```
    VERSION="0.1.0" conda build conda_recipe
```

## License

All files are licensed under the BSD 3-Clause License as follows:
 
> Copyright (c) 2016, Activision Publishing, Inc.  
> All rights reserved.
> 
> Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
> 
> 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
>  
> 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
>  
> 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
>  
> THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

