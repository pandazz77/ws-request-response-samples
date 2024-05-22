
//redirect console log to html
(function () {
    var old = console.log;
    var logger = document.getElementById('log');
    console.log = function () {
        logger.innerHTML += "<br>";
        for (var i = 0; i < arguments.length; i++) {
            if (typeof arguments[i] == 'object') {
                logger.innerHTML += (JSON && JSON.stringify ? JSON.stringify(arguments[i], undefined, 2) : arguments[i]) + " ";
            } else {
                logger.innerHTML += arguments[i] + " ";
            }
        }
        logger.innerHTML += "</br>";
    }
})();


// main logic
function response_handler(data){
    console.log("incoming Request:",data);
    // do nothing
}

var rsocket = new RequestWebSocket("ws://localhost:8765",response_handler);

function main(){
    async function _loop(){
        while(true){
            let request_body = {
                "somekey":"somevalue",
                "somekey1":"somevalue1",
                "randomvalue":rstr(7)
            };
            console.log("<h5 style='color:green'>outgoing Request:</h5>",request_body);
            let response = await rsocket.send_request(request_body);
            console.log("<h5 style='color:red'>incoming Response:</h5>",response);
        }
    }
    rsocket.onopen = function(e){
        _loop();
    }
}

main();