import argparse
import ctypes
import os
import sys
import pprint
import time
import logging

logging.basicConfig()

import av
from av import VideoFrame

from qtproxy import Q
from glproxy import gl


WIDTH = 960
HEIGHT = 540

class PlayerGLWidget(Q.GLWidget):

    def initializeGL(self):
        print 'initialize GL'
        gl.clearColor(0, 0, 0, 0)

        gl.enable(gl.TEXTURE_2D)

        self.textures = [gl.genTextures(1) for _ in range(4)]
        for tid in self.textures:
            gl.bindTexture(gl.TEXTURE_2D, tid)
            gl.texParameter(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST)
            gl.texParameter(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST)

    def setFrame(self, index, frame):

        width = 960
        height = 540
        frame = frame.reformat(width, height, 'rgb24')
        ptr = ctypes.c_void_p(frame.planes[0].ptr)

        gl.bindTexture(gl.TEXTURE_2D, self.textures[index])
        gl.texImage2D(gl.TEXTURE_2D, 0, 3, width, height, 0, gl.RGB, gl.UNSIGNED_BYTE, ptr)

    def resizeGL(self, w, h):
        print 'resize to', w, h
        gl.viewport(0, 0, w, h)
        # gl.matrixMode(gl.PROJECTION)
        # gl.loadIdentity()
        # gl.ortho(0, w, 0, h, -10, 10)
        # gl.matrixMode(gl.MODELVIEW)

    def paintGL(self):
        # print 'paint!'
        gl.clear(gl.COLOR_BUFFER_BIT)

        gl.bindTexture(gl.TEXTURE_2D, self.textures[0])
        with gl.begin('polygon'):
            gl.texCoord(0, 0); gl.vertex(-1,  1)
            gl.texCoord(1, 0); gl.vertex( 0,  1)
            gl.texCoord(1, 1); gl.vertex( 0,  0)
            gl.texCoord(0, 1); gl.vertex(-1,  0)

        gl.bindTexture(gl.TEXTURE_2D, self.textures[1])
        with gl.begin('polygon'):
            gl.texCoord(0, 0); gl.vertex( 0,  1)
            gl.texCoord(1, 0); gl.vertex( 1,  1)
            gl.texCoord(1, 1); gl.vertex( 1,  0)
            gl.texCoord(0, 1); gl.vertex( 0,  0)

        if len(self.textures) > 2:
            gl.bindTexture(gl.TEXTURE_2D, self.textures[2])
            with gl.begin('polygon'):
                gl.texCoord(0, 0); gl.vertex(-1,  0)
                gl.texCoord(1, 0); gl.vertex( 0,  0)
                gl.texCoord(1, 1); gl.vertex( 0, -1)
                gl.texCoord(0, 1); gl.vertex(-1, -1)

        if len(self.textures) > 3:
            gl.bindTexture(gl.TEXTURE_2D, self.textures[3])
            with gl.begin('polygon'):
                gl.texCoord(0, 0); gl.vertex( 0,  0)
                gl.texCoord(1, 0); gl.vertex( 1,  0)
                gl.texCoord(1, 1); gl.vertex( 1, -1)
                gl.texCoord(0, 1); gl.vertex( 0, -1)



app = Q.Application([])

glwidget = PlayerGLWidget()
glwidget.setFixedWidth(WIDTH)
glwidget.setFixedHeight(HEIGHT)
glwidget.show()
glwidget.raise_()


gl.readBuffer(gl.FRONT) # Read from front.
out_frame = VideoFrame(WIDTH, HEIGHT, 'rgb24')
out_buffer = ctypes.c_void_p(out_frame.planes[0].ptr)

out_file = av.open('output.mkv', 'w')
out_stream = out_file.add_stream('mpeg4', 60)
out_stream.time_base = '1/1000'
out_frame.time_base = out_stream.time_base

options = {
    'pixel_format': '0rgb',
    'framerate': '15', # Does nothing, really.
    #'video_size': '960x540', # Does nothing at all.
    'capture_cursor': '1',
    'capture_mouse_clicks': '1',
}
containers = [
    av.open('0', format='avfoundation', options=options.copy()),
    av.open('1', format='avfoundation', options=options.copy()),
    av.open('2', format='avfoundation', options=options.copy()),
    av.open('3', format='avfoundation', options=options.copy()),
]


frame_times = []
start_time = time.time()
last_pts = 0

while True:
    for ci, c in enumerate(containers):
        for frame in c.decode():
            if isinstance(frame, VideoFrame):
                glwidget.setFrame(ci, frame)
                break

    glwidget.updateGL()

    # Reads into our frame object.
    gl.readPixels(0, 0, WIDTH, HEIGHT, gl.RGB, gl.UNSIGNED_BYTE, out_buffer)

    now = time.time()

    out_frame.pts = 1000 * (now - start_time)
    out_packet = out_stream.encode(out_frame)
    if out_packet:
        out_file.mux(out_packet)

    then = None
    while len(frame_times) > 5:
        then = frame_times.pop(0)
    frame_times.append(now)
    if then:
        print 5 / (now - then)


