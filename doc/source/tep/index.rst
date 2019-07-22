Taurus Enhancement Proposals
=============================

.. raw:: html

    <script>
    //Function to redirect to the TEPs website
    function redirect()
    {
        // Base url: URL where are hosted the TEPs
        var baseurl = "https://github.com/taurus-org/taurus/tree/develop/doc/source/tep/"
        // Get query if exist:
        var query = location.search.substring(1)
        if (typeof query === 'undefined' || !query)
        {
            // If there is not a query redirect to the index page
            query = "index.md"
        }
        var url = baseurl.concat(query);
        window.location = url;
    }
    redirect()
    </script>