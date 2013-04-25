taurus_websocket = null

taurus_models = ->
    ( elem.dataset['taurusModel'] for elem in $('[data-taurus-model]') )

taurus_element = (model) ->
    $('[data-taurus-model="' + model + '"]')

initialize = ->

    console.log("Initializing page...")

    $('title').html(':: Taurus ::')

    gauge_props = 
        interactionArea: "none"
        minimum: -140
        maximum: 150

    dom = require("dojo/dom")
    CircularLinearGauge = require("dojox/dgauges/components/default/CircularLinearGauge")
    gauge = new CircularLinearGauge(gauge_props, dom.byId("gauge01"))
    gauge.set('value', 44)
    
    taurus_websocket = new WebSocket("ws://pc151.cells.es:8888/taurus")

    taurus_websocket.onopen = ->
        $('title').html(':: Taurus :: Connected')
        initialize_taurus()
        
    taurus_websocket.onmessage = (event) ->
        event_data = JSON.parse(event.data)
        elements = taurus_element(event_data.model)
        elements.filter(":not([data-taurus-controller = 'Gauge'])").css(event_data.css).html(event_data.html)
        elements.filter("input").css('background-color','').css('color','')
        g = elements.filter("#gauge01")
        if g.length and gauge
            indicatorText = gauge.getElement("indicatorText")
            indicatorText.set('value', event_data.html)
            indicatorText.indicator.set('value', event_data.html)
        
    taurus_websocket.onerror = (event) ->
        $('body').append('<div>Error:' + event + ' ' + '</div>')

    taurus_websocket.onclose = (event) ->
        $('title').html(':: Taurus :: Disconnected')

    plot = JXG.JSXGraph.initBoard('plot', {boundingbox: [-10, 10, 10, -10], axis:true, grid:true})
    geonext = JXG.JSXGraph.loadBoardFromFile('geonext', 'static/geonext/triangle.gxt', 'Geonext')    

    props = 
        position : ["right", "bottom"]
        width : 460
#        buttons : 
#            Ok : -> $(this).dialog("close")
    
    $('#motor-attributes').dialog(props)
    
    $("#tangotest-attributes" ).hide()
    $('#show-tangotest').button().click(-> $('#tangotest-attributes').show('bounce', {}, 500, ->))

    console.log("Finished initializing page")
     
initialize_taurus = ->
    console.log("Initializing taurus...")
    models = taurus_models()
    json_models = JSON.stringify({models : models})
    taurus_websocket.send(json_models)
    console.log("Finished initializing taurus")
    
$ ->
    dojo_requirements = ["dojo/_base/kernel", "dojo/parser", "dojo/dom",
                         "dojox/dgauges/components/default/CircularLinearGauge"]

    require(dojo_requirements, initialize)  
