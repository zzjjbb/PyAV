
cdef extern from "pyav/opengl.h":

    ctypedef int           GLint
    ctypedef unsigned int  GLenum
    ctypedef unsigned int  GLuint
    ctypedef unsigned char GLubyte

    int GL_POINTS
    int GL_VENDOR
    int GL_RENDERER
    int GL_VERSION
    int GL_SHADING_LANGUAGE_VERSION
    int GL_EXTENSIONS
    cdef const GLubyte* glGetString(GLenum name)
    cdef const GLubyte* glGetStringi(GLenum name, GLuint index)
