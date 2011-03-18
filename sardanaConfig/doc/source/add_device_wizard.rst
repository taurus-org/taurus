

.. currentmodule:: new_device_wizard

Add Device Wizard
======================

This chapter describes the API for adding a device through a wizard.


Example::

    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(get_resources())
    Pages = Enumeration('Pages', ('SelectSardanaPool', 'NewDevice','CommitPage','OutroPage'))
    w = wiz.SardanaBaseWizard()
    w.setWindowTitle("Add New Hardware Wizard")
    selectPool = SelectSardanaPoolBasePage(Sardana,Pool)
    w.setPage(Pages.SelectSardanaPool, selectPool)
    selectPool.setNextPageId(Pages.NewDevice)
    newDevice = NewDeviceBasePage()
    w.setPage(Pages.NewDevice, newDevice)
    newDevice.setNextPageId(Pages.CommitPage)
    commit_page = NewDeviceCommitBasePage()
    w.setPage(Pages.CommitPage, commit_page)
    commit_page.setNextPageId(Pages.OutroPage)
    w.show()
    sys.exit(app.exec_())


.. automodule:: add_device_wizard
    :members:
    :undoc-members:

    