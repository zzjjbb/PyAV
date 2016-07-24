cimport libav as lib

from av.stream cimport Stream


cdef class SubtitleStream(Stream):
    pass


cdef class DVDSubtitleContext(object):
    
    cdef lib.DVDSubContext *ptr

