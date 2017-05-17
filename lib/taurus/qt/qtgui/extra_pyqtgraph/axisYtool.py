from pyqtgraph import ViewBox

class Y2ViewBox(ViewBox):

    def __init__(self, *args, **kwargs):
        ViewBox.__init__(self, *args, **kwargs)
        self._isAttached = False

    @staticmethod
    def getY2ViewBox(plot_item):
        scene_items = plot_item.scene().items()

        for item in scene_items:
            if isinstance(item, Y2ViewBox):
                return item
        ret = Y2ViewBox()
        ret.attachToPlotItem(plot_item)
        return ret

    def attachToPlotItem(self, plot_item):
        if self._isAttached:
            return  # TODO: log a message it's already attached
        self._isAttached = True

        mainViewBox = plot_item.getViewBox()
        mainViewBox.sigResized.connect(self.updateViews)

        # make sure Y2 is shown
        plot_item.showAxis('right')
        # add self to plotItem scene and link right and bottom axis to self
        plot_item.scene().addItem(self)
        plot_item.getAxis('right').linkToView(self)
        self.setXLink(plot_item)


    def updateViews(self, viewBox):
        self.setGeometry(viewBox.sceneBoundingRect())
        self.linkedViewChanged(viewBox, self.XAxis)

    # def autoRange(self, *args, **kwargs):
    #     print('2')
    #     ViewBox.autoRange(self, *args, **kwargs)



