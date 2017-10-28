 

 
 var mymap = L.map('transmap').setView([51.505, -0.09], 13);
 
 L.tileLayer('https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoic2pvZXJkMjIyODg4IiwiYSI6ImNqOWI5cms5cjFsaHoycXFzZ2h4MnI1eWkifQ.RLkABYj4vbHbBLQBqth2ig', {
    attribution: 'Map data &copy; <a href="http://openstreetmap.org">OpenStreetMap</a> contributors, <a href="http://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="http://mapbox.com">Mapbox</a>',
    maxZoom: 18,
    id: 'mapbox.streets',
    accessToken: 'your.mapbox.access.token'
}).addTo(mymap);
