
==============================
Docs for other Taurus versions
==============================

The `main taurus docs <http://taurus-scada.org>`_ are generated for the
most recent development version.

But docs for other branches in the `repository <https://github.com/taurus-org/taurus>`_ are also generated.
You can find all the currently built docs in the following list:


.. raw:: html

   <!-- Create a list of links to builds of the docs for other branches -->
   <div class="container">
      <div class="row">
         <div class="col-sm">
            <table class="table">
              <tbody class="tb"></tbody>
            </table>
         </div>
      </div>
   </div>

   <script src="https://code.jquery.com/jquery-3.2.1.min.js"></script>

   <script>
      // TODO: once the DNS gets pointed to github pages instead of RTD, the doc_url can be changed to "http://taurus-scada.org/"
      var doc_url = "https://taurus-org.github.io/taurus-doc/";
      var contents_url = "https://api.github.com/repos/taurus-org/taurus-doc/contents/./";

      function list_items(url){
         $.ajax({url: url}).then(function(data) {
            $('.tb').html('');
            $('.tb').append('<tr><td><a target="_blank" href="' + doc_url + '">' + 'develop' + '</a></td></tr>');
            data.forEach(function(element) {
               if (element.name.match(/^v-/)) {
                  $('.tb').append('<tr><td><a target="_blank" href="' + doc_url + element.name + '">' + element.name.slice(2) + '</a></td></tr>');
               };
            });
         });
      }

      $(document).ready(function() {
         list_items(contents_url);
      });
   </script>


