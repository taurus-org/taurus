:: Install numpy
pip install --trusted-host www.silx.org --find-links http://www.silx.org/pub/wheelhouse/ --upgrade numpy

:: Install Qt binding
:: Install PyQt4 from www.silx.org and PyQt5/PySide from pypi
pip install --pre --trusted-host www.silx.org --find-links http://www.silx.org/pub/wheelhouse/ %QT_BINDINGS%

:: Install lxml
pip install --pre --trusted-host www.silx.org --find-links http://www.silx.org/pub/wheelhouse/ lxml==3.7.0

:: Install guiqwt 
:: TODO, install guiqwt from pypi
:: pip install --upgrade guiqwt

:: Install the generated taurus wheel package to test it
:: Make sure it does not come from cache or pypi
:: At this point all install_requires dependencies MUST be installed
:: as this is installing only from dist/
pip install --pre --find-links dist/ --no-cache-dir --no-index taurus

:: Print Python info
pip list

:: launch tests (for now only a trivial import, since the testsuite
:: would fail due to missing tango and epics)
python -c "import taurus"
:: TODO: run testsuite
::taurustestsuite
