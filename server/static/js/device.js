

function setDeviceCookie(device_id, api_key) {
    console.log(device_id, api_key)
    setCookie("device_id", device_id, 1);
    setCookie("device_api_key", api_key, 1);
}


function setCookie(name, value, daysToLive) {
    var cookie = name + "=" + encodeURIComponent(value);
    if (typeof daysToLive === "number")
        cookie += "; max-age=" + (daysToLive*60*60*24);
    document.cookie = cookie;
}

String.prototype.format = function() {
  a = this;
  for (k in arguments) {
    a = a.replace("{" + k + "}", arguments[k])
  }
  return a
}

function changeGrafanaURL(c_start, c_end, t_start, t_end){
    var url_format_str = "http://localhost:3000/d-solo/q-6qL-RWk/sensor-data-vizualizations?tab=queries&orgId=1&panelId=3&from={0}&to={1}&var-device_id=6829cb99-d81c-4823-bca6-bbdd3ddaf527&var-sources=z&var-sources=y&var-sources=g&var-sources=h&var-sources=x";
    document.getElementById('grafana_ctrl_iframe').src = url_format_str.format(c_start, c_end);
    document.getElementById('grafana_test_iframe').src = url_format_str.format(t_start, t_end);

    console.log(url_format_str.format(c_start, c_end));
    console.log(url_format_str.format(t_start, t_end));
}
