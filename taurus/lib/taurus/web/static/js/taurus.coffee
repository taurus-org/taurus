taurus_websocket = null

taurus_models = ->
    ( elem.dataset['taurusModel'] for elem in $('[data-taurus-model]') )

taurus_element = (model) ->
    $('[data-taurus-model="' + model + '"]')

initialize = ->

    console.log("Initializing page...")

    taurus_websocket = new WebSocket("ws://160.103.207.112:8888/taurus")

    taurus_websocket.onopen = ->
        console.log("Websocket connected")
        # $('title').html(':: ALBA Machine Status :: Connected')
        initialize_taurus()
        
    taurus_websocket.onmessage = (event) ->
        event_data = JSON.parse(event.data)
        elements = taurus_element(event_data.model)
        elements.css(event_data.css).html(event_data.html)
        
    taurus_websocket.onerror = (event) ->
        $('body').append('<div>Error:' + event + ' ' + '</div>')

    taurus_websocket.onclose = (event) ->
        console.log("Websocket DISCONNECTED")

    console.log("Finished initializing page")
     
initialize_taurus = ->
    console.log("Initializing taurus...")
    models = taurus_models()
    json_models = JSON.stringify({models : models})
    taurus_websocket.send(json_models)
    console.log("Finished initializing taurus")
    
$ ->
    initialize()

