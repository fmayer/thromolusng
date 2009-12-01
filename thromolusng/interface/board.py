import thromolusng
import thromolusng.interface

from PyQt4 import QtGui, QtCore

# Stub.
class Modifier(object):
    def __init__(self):
        self.img = None
        self.opacity = None
        self.scale = None
        
        self.submods = []
    
    def add_submod(self, mod):
        self.submods.append(mod)
    
    def del_submod(self, mod):
        self.submods.remove(mod)
    
    def __getitem__(self, i):
        return sum(


class BoardLabel(QtGui.QLabel):
    PREVIEW_OPACITY = 0.4
    def __init__(self, pid, board, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.setMouseTracking(True)
        
        self.user_control = True
        self.lastmodifier = None
        self.board = board
        self.pid = pid
        self.picked = None
        
        self.modifiers = [
            [Modifier() for _ in xrange(board.cols)
             ] for _ in xrange(board.rows)
        ]
        
        self.bg_image = QtGui.QImage(
            thromolusng.interface.get_data('bg.png')
        )        

        self.img = [
            QtGui.QImage(
                thromolusng.interface.get_data('ball-empty.png')
                ),
            QtGui.QImage(
                thromolusng.interface.get_data('ball-white.png')
                ),
            QtGui.QImage(
                thromolusng.interface.get_data('ball-black.png')
                ),
        ]
        
        self.stone_background = QtGui.QImage(
                thromolusng.interface.get_data('ball-bg.png')
        )
    
    def paintEvent(self, event):
        # We might want to change that for performance reasons later on.
        # Either FastTransformation or SmoothTransformation.
        s_mode = QtCore.Qt.SmoothTransformation                
        
        h = self.height()
        w = self.width()
        boxsize = min((h / self.board.rows, w / self.board.cols))
        size = max((h, w))
        
        paint = QtGui.QPainter()
        paint.begin(self)
        
        # Resize the background image.
        #bg = self.bg_image.scaledToHeight(size, s_mode)
        #paint.drawImage(0, 0, bg)
        
        # Assuming the images are boxed.
        print boxsize
        imgs = [img.scaledToHeight(boxsize, s_mode) for img in self.img]
        
        for ir in xrange(self.board.rows):
            for ic in xrange(self.board.cols):
                mod = self.modifiers[ir][ic]
                if mod.opacity is not None:
                    paint.setOpacity(mod.opacity)
                else:
                    paint.setOpacity(1)
                if mod.img is not None:
                    img = mod.img.scaledToHeight(boxsize, s_mode)
                else:
                    img = imgs[self.board[ir, ic]]
                if mod.scale is not None:
                    img = img.scaledToHeight(size * mod.scale, s_mode)
                
                paint.drawImage(ic * boxsize, ir * boxsize, img)
        
        # This was a triumph!
        paint.end()
    
    def get_coord(self, x, y):
        h = self.height()
        w = self.width()
        boxsize = min((h / self.board.rows, w / self.board.cols))
        return y / boxsize, x / boxsize
    
    def mousePressEvent(self, event):
        if not self.user_control:
            return
        row, col = self.get_coord(event.x(), event.y())
        print row, col
        if self.picked is None and self.board[row, col] == self.pid:
            self.pick(row, col)
        else:
            try:
                self.board.turn(self.picked, (row, col))
            finally:
                self.depick()
        self.repaint()
    
    def pick(self, row, col):
        self.picked = (row, col)
    
    def depick(self):
        self.picked = None
        
    
    def mouseMoveEvent(self, event):
        if not self.user_control:
            return
        
        row, col = self.get_coord(event.x(), event.y())
        if self.picked is not None:
            if self.lastmodifier is not None:
                self.lastmodifier.img = self.lastmodifier.opacity = None
            if not self.board[row, col]:
                self.modifiers[row][col].img = self.img[self.pid]
                self.modifiers[row][col].opacity = 0.5
                self.lastmodifier = self.modifiers[row][col]
        self.repaint()

if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    main = BoardLabel(1, thromolusng.Board(6, 6))
    main.show()
    app.exec_()