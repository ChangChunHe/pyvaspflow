sphinx-apidoc -o ./doc ../pyvaspflow
make html
cp -a build/html/. .
rm -rf build
