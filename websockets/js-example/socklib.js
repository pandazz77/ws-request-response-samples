
let onrequest = new Event("onrequest");
let onresponse = new Event("onresponse");

const REQUEST_ID_FIELD = "_rid";
const REQUEST_TYPE_FIELD = "_type";
const REQUEST_REQVAL = "REQUEST";
const REQUEST_RESVAL = "RESPONSE";
const REQUEST_ID_LENGTH = 10;

function rstr(length) {
    return Math.random().toString(36).substring(2, length+2);
}

function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}


class RequestWebSocket extends WebSocket{
    constructor(url,response_handler){
        super(url);
        this.response_handler = response_handler;
        this.incoming_messages = {};

        this.onmessage = this._onmessage_handler;
        this.onopen = this._onopen_handler;
        this.onclose = this._onclose_handler;
        this.onerror = this._onerror_handler;
    }

    _onopen_handler(event){
        
    }

    _onclose_handler(event){
        
    }

    _onerror_handler(error){
        alert(error);
    }

    _onmessage_handler(event){
        //console.log("onmsg",event);
        let data = JSON.parse(event.data);
        if(data[REQUEST_ID_FIELD]==undefined) return;
        if(data[REQUEST_TYPE_FIELD]==REQUEST_REQVAL){
            let onrequest = new Event("onrequest",data);
            this.dispatchEvent(onrequest);
            this._send_response(data);
        } else if(data[REQUEST_TYPE_FIELD]==REQUEST_RESVAL){
            this.incoming_messages[data[REQUEST_ID_FIELD]] = data;
            let onresponse = new Event("onresponse",data);
            this.dispatchEvent(onresponse);
        }
    }

    // wrap message to request-response format
    _wrap_message(data,isRequest=true){
        if(typeof(data)=="string"){
            data = {
                "data":data
            }
        }

        if(data[REQUEST_ID_FIELD]==undefined) data[REQUEST_ID_FIELD] = rstr(10);
        if(isRequest) data[REQUEST_TYPE_FIELD] = REQUEST_REQVAL;
        else data[REQUEST_TYPE_FIELD] = REQUEST_RESVAL;

        return data;
    }

    async send_request(data){
        if(!this.readyState) return;
        
        let wrapped_data = this._wrap_message(data);
        let id = wrapped_data[REQUEST_ID_FIELD];

        this.send(JSON.stringify(wrapped_data));
        while(this.incoming_messages[id]==undefined){
            await sleep(1000);
        }
        let response = this.incoming_messages[id];
        delete this.incoming_messages[id];
        if(response[REQUEST_TYPE_FIELD] == REQUEST_RESVAL){
            delete response[REQUEST_ID_FIELD];
            delete response[REQUEST_TYPE_FIELD];
            return response;
        }
        throw new Error("Response is not response :)");
    }

    async _send_response(data){
        handled_data = await self.response_handler(data);
        if(handled_data!=undefined)
            await this.send(JSON.stringify(handled_data));
    }

}