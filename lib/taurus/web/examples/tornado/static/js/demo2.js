
(function() {
  var initialize_demo2;

  initialize_demo2 = function() {
    console.log("Initializing taurus WEB demo 2 application...");
    init_highcharts();
    return console.log("Finished initializing taurus WEB demo 2 application");
  };

  $(function() {
    return initialize_demo2();
  });

  init_highcharts = function () {
    $('#highcharts-canvas').highcharts({
        chart: {
            type: 'bar'
        },
        title: {
            text: 'Fruit Consumption'
        },
        xAxis: {
            categories: ['Apples', 'Bananas', 'Oranges']
        },
        yAxis: {
            title: {
                text: 'Fruit eaten'
            }
        },
        series: [{
            name: 'Jane',
            data: [1, 0, 4]
        }, {
            name: 'John',
            data: [5, 7, 3]
        }]
    });
  };
    
}).call(this);
