
(function() {
  var initialize_demo3;

  initialize_demo3 = function() {
    console.log("Initializing taurus WEB demo 3 application...");
    init_highcharts();
    return console.log("Finished initializing taurus WEB demo 3 application");
  };

  $(function() {
    return initialize_demo3();
  });

  init_highcharts = function () {
    var chart = new Highcharts.Chart({
        chart: {
            renderTo: 'highcharts-canvas',
            //type: 'line'
        },
        title: {
            text: 'Fruit Consumption'
        },
        series: [{
            name: 'Jane',
            data: []
        }],
        
        taurus_model : "sys/tg_test/1/double_scalar"
    });
    
    taurus_listener = function (event_data) {
        if (event_data.model == chart.options.taurus_model) {
            console.log(event_data.value);
            data = chart.series.data
            data.push([data.length,event_data.value]);
            console.log(chart.series[0].data);
            chart.redraw();
        }
    };
    
    taurus_onmessage_callbacks.add(taurus_listener);
};
}).call(this);
