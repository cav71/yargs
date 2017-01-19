# preamble
function info { echo "+ $@" >& 2; }
function error { echo "* $@" >& 2; exit 1; }

export prefix="$PREFIX"
export bindir="$PREFIX/bin"
export libdir="$PREFIX/lib"
export pysite="$libdir/python$(python -c 'import sys; print(sys.version[:3])')/site-packages"
export pyplat=$( python -c 'import sys, sysconfig; print(sysconfig.get_platform()+"-"+sys.version[:3])' )
export version=$PKG_VERSION
export PKG_CONFIG_PATH="$prefix/lib/pkgconfig"

echo "= curdir:       $(pwd)"
echo "= python:       $(which python)"
echo "        :       $(python -c 'import sys; print(sys.version)')"
echo "= pysite:       $pysite"
echo "= pyplat:       $pyplat"
echo "= prefix:       $prefix"
echo "= libdir:       $libdir"
echo "= pkgconfig:    $PKG_CONFIG_PATH"
echo "= version:      $version"
# end of preabmle

python setup.py install --prefix="$prefix"
