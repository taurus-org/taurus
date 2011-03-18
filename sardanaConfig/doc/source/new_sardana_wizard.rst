

.. currentmodule:: new_sardana_wizard

Add Sardana Wizard
======================

This chapter describes the API for creating a instance of new Sardana through a wizard.

Example::

    app = QtGui.QApplication([])
    QtCore.QResource.registerResource(wiz.get_resources())
    
    Pages = Enumeration('Pages', ('IntroPage', 'TangoPage', 'SardanaPage', 'PoolPage', 'MSPage','CommitPage','OutroPage'))
    w = wiz.SardanaBaseWizard()
    
    intro = NewSardanaIntroPage()
    w.setPage(Pages.IntroPage, intro)
    intro.setNextPageId(Pages.TangoPage)
    
    tg_host_page = SelectTangoHostPage()
    w.setPage(Pages.TangoPage, tg_host_page)
    tg_host_page.checkData()
    tg_host_page.setNextPageId(Pages.SardanaPage)
    
    sardana_page = AddSardanaBasePage()
    w.setPage(Pages.SardanaPage, sardana_page)
    sardana_page.setNextPageId(Pages.PoolPage)
    
    pool_page = AddPoolBasePage()
    w.setPage(Pages.PoolPage, pool_page) 
    pool_page.setNextPageId(Pages.MSPage)
    
    ms_page = AddMSBasePage()
    w.setPage(Pages.MSPage, ms_page) 
    ms_page.setNextPageId(Pages.CommitPage)
    
    commit_page = SardanaCommitBasePage()
    w.setPage(Pages.CommitPage, commit_page)
    commit_page.setNextPageId(Pages.OutroPage)
    
    outro_page = SardanaOutroBasePage()
    w.setPage(Pages.OutroPage, outro_page) 
    w.setOption (QtGui.QWizard.CancelButtonOnLeft , True)
    
    
    #Qt.QObject.connect(w, Qt.SIGNAL("done()"), done)
    w.show()
    sys.exit(app.exec_())



.. automodule:: new_sardana_wizard
    :members:
    :undoc-members: