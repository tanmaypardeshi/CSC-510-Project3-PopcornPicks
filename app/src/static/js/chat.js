var socket = io();
    socket.on('connect', function() {
        socket.emit('connections', 'I\'m connected!');
        /*
        For debugging purposes this prints in python when someone connects
         */
    });