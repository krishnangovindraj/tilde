### Where is django?
I do not distribute django with this code.
I can no longer find the django source code either, but I do have a copy.
Probably better to ask the author though: https://www.linkedin.com/in/jerome-maloberti-546657b/

We need the libdjango.so ( path set in: refactor/query_testing_back_end/django/django_wrapper/c_library.py )
To compile it:
    > gcc -fPIC -rdynamic -shared -Lstatic -o libdjango.so *.c
