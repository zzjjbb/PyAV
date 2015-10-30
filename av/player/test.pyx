
cimport libav as lib

def main():

    cdef const unsigned char* x = lib.glGetString(lib.GL_VENDOR)
    if x:
        print x
    x = lib.glGetString(lib.GL_RENDERER)
    if x:
        print x
    x = lib.glGetString(lib.GL_VERSION)
    if x:
        print x
    x = lib.glGetString(lib.GL_SHADING_LANGUAGE_VERSION)
    if x:
        print x
