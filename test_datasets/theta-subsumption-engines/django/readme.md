### Where is django?
I do not distribute django with this code.
I can no longer find the official source for django. It should have been on the link from this page: https://www.lri.fr/logiciel.brevet_en.php?log=17 
I do have a copy which I will try to keep for safe keeping. 
There's a collection of the source code of 3 subsumption engines here, which is where I got it from: http://www.doc.ic.ac.uk/~jcs06/Subsumer/

Probably better to ask the author though: https://www.linkedin.com/in/jerome-maloberti-546657b/

We need the libdjango.so ( path set in: refactor/query_testing_back_end/django/django_wrapper/c_library.py )
To compile it:
    > gcc -fPIC -rdynamic -shared -Lstatic -o libdjango.so *.c
