class Requests {
    static GetRequest(url, data, callback) {
        var xhttp = new XMLHttpRequest();
        xhttp.onreadystatechange = function() {
            if (this.readyState == 4 && this.status == 200)
            {
                var j = JSON.parse(this.responseText);
                callback(j);
            }
        }
        
        if (data)
        {
            xhttp.open("POST", url, true);
            xhttp.send(data);
        }
        else
        {
            xhttp.open("GET", url, true);
            xhttp.send();
        }
    }
}

export { Requests };