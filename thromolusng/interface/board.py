import thromolusng
import thromolusng.interface
import thromolusng.interface.animation

from PyQt4 import QtGui, QtCore


class BoardLabel(QtGui.QLabel):
    PREVIEW_OPACITY = 0.4
    def __init__(self, pid, board, singleplayer=False, parent=None):
        QtGui.QLabel.__init__(self, parent)
        self.setMouseTracking(True)
        
        self.setMinimumSize(200, 200)
        
        self.singleplayer = singleplayer
        
        self.user_control = True
        self.mmmodifier = None
        self.board = board
        self.pid = pid
        self.picked = None
        self.pickedmod = None
        
        self.pickedtimeline = thromolusng.interface.animation.Timeline(
            [
                (thromolusng.interface.animation.Range(0, 1), 
                 thromolusng.interface.animation.QuadraticTransistion(
                     1, -0.5, 1, self.pickedscale)
                 ),
                (thromolusng.interface.animation.Range(1, 2), 
                 thromolusng.interface.animation.QuadraticTransistion(
                     1, 0.5, 0.5, self.pickedscale)
                 )
                ],
            True
        )
        
        self.aniengine = thromolusng.interface.animation.Engine()
        self.aniengine.add_timeline(self.pickedtimeline)
        self.aniengine.start(10)
        
        self.modifiers = [
            [list() for _ in xrange(board.cols)
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
        imgs = [img.scaledToHeight(boxsize, s_mode) for img in self.img]
        
        for ir in xrange(self.board.rows):
            for ic in xrange(self.board.cols):
                absvalues = {}
                relvalues = {}
                for if_, abs_, rel in self.modifiers[ir][ic]:
                    if if_ is not None and not if_(self.board[ir, ic]):
                        continue
                    for key, adjust in rel:
                        if not key in relvalues:
                            relvalues[key] = 0
                        relvalues[key] += adjust
                    
                    for key, value in abs_:
                        if key in absvalues:
                            raise ValueError(
                                "Two absolute modifiers on the same value. "
                                "Aborting"
                            )
                        absvalues[key] = value
                opacity = absvalues.get(
                    'opacity', 1 + relvalues.get('opacity', 0)
                )
                scale = absvalues.get(
                    'scale', 1 + relvalues.get('scale', 0)
                )
                img = absvalues.get('img', imgs[self.board[ir, ic]])
                
                # Inefficient.
                img = img.scaledToHeight(boxsize * scale, s_mode)
                paint.setOpacity(opacity)
                paint.drawImage(
                    ic * boxsize + boxsize * (1 - scale) / 2,
                    ir * boxsize + boxsize * (1 - scale) / 2,
                    img)
        
        # This was a triumph!
        paint.end()
    
    def pickedscale(self, trans, value):
        row, col = self.picked
        if self.pickedmod is not None:
            try:
                self.del_modifier(row, col, self.pickedmod)
            except ValueError:
                pass
        self.pickedmod = (
                    # if
                    None,
                    # absolute
                    tuple(),
                    # relative
                    (('scale', value  - 1),)
                )
        self.add_modifier(row, col, self.pickedmod)
        self.repaint()
        print 'fooo'
    
    def get_coord(self, x, y):
        h = self.height()
        w = self.width()
        boxsize = min((h / self.board.rows, w / self.board.cols))
        return y / boxsize, x / boxsize
    
    def mousePressEvent(self, event):
        if not self.user_control:
            return
        row, col = self.get_coord(event.x(), event.y())
        if row >= self.board.rows or col >= self.board.cols:
            return
        if self.picked is None and self.board[row, col] == self.pid:
            self.pick(row, col)
        elif self.picked:
            try:
                self.board.turn(self.picked, (row, col))
            except thromolusng.InvalidTurn:
                pass
            else:
                if self.singleplayer:
                    self.pid = 3 - self.pid
            finally:
                self.depick()
                if self.mmmodifier is not None:
                    self.del_modifier(*self.mmmodifier)
                    self.mmmodifier = None
        self.repaint()
    
    def pick(self, row, col):
        print 'picked %d %d' % (row, col)
        self.picked = (row, col)
        self.pickedtimeline.start()
    
    def depick(self):
        print 'depicked'
        row, col = self.picked
        self.picked = None
        self.pickedtimeline.stop()
        self.pickedtimeline.reset()
        if self.pickedmod is not None:
            self.del_modifier(row, col, self.pickedmod)
    
    def mouseMoveEvent(self, event):
        if not self.user_control:
            return
        
        row, col = self.get_coord(event.x(), event.y())
        if row >= self.board.rows or col >= self.board.cols:
            return
        if self.picked is not None:
            if self.mmmodifier is not None:
                if self.mmmodifier[:2] == (row, col):
                    return
                self.del_modifier(*self.mmmodifier)
                self.mmmodifier = None
            if not self.board[row, col]:
                m = (
                    # if
                    lambda x: x == 0,
                    # absolute
                    (('img', self.img[self.pid]), ('opacity', 0.5)),
                    # relative
                    tuple()
                )
                self.add_modifier(row, col, m)
                self.mmmodifier = (row, col, m)
        self.repaint()
    
    def add_modifier(self, row, col, mod):
        self.modifiers[row][col].append(mod)
        return mod
    
    def del_modifier(self, row, col, mod):
        self.modifiers[row][col].remove(mod)


if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    main = BoardLabel(1, thromolusng.Board(7, 7), True)
    main.show()
    app.exec_()