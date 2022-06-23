function Decelium(url_version,api_key_in) {
    this.url_version = url_version;
    this.api_key = api_key_in;
}
Decelium.prototype.query = function(query_name,query_in,callback,asynch=true,protocol=undefined)  {
    if (protocol == undefined)
        protocol = window.location.protocol;
    url = protocol+this.url_version+'/data/query';
    req = { qtype: query_name, api_key: this.api_key };
    req['__str_encoded_query'] =JSON.stringify(query_in);
    var encodedString = btoa(req['__str_encoded_query']);
    encodedString  = encodeURIComponent(encodedString);
    // ret_dat = {error:'jquery request failed'}
    req['__str_encoded_query'] = encodedString;
    ret = {};
    return $.ajax({
        type: 'GET',
        url: url,
        data: req,
        success: function (data,retdat) {
            callback(data);
        },
        error: function (data,retdat) {
            callback(data);
        },
        async: asynch
    });
}