grep '^\w' requirement_tree.txt > requirements.txt
sed -Ei 's/python-ldap==(([0-9]+\.){2}[0-9])/python-ldap==\1\
https:\/\/github.com\/cgohlke\/python-ldap-build\/releases\/download\/v\1\/python_ldap-\1-cp312-cp312-win_amd64.whl; sys_platform == "win32"/' requirements.txt
sed -Ei 's/python-ldap==(([0-9]+\.){2}[0-9])/python-ldap==\1; sys_platform != "win32"/' requirements.txt