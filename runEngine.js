// import { sample1, sample2, sample3 } from "./jsons.js";

var input = document.getElementById('myInput');
var search = document.getElementById('search-addon');

function changeColor(id) {
  if(id==0){
    localStorage.setItem('json', JSON.stringify(sample1))
  }else if(id==1){
    localStorage.setItem('json', JSON.stringify(sample2))
  }else{
    localStorage.setItem('json', JSON.stringify(sample3))
  }
  window.location.replace('claimmap/src/visualization/index.html')
}

search.addEventListener('click', function() {
  var value = input.value;

  localStorage.setItem('search', value)

  fetch('http://127.0.0.1:5000/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json'
    },
    body: JSON.stringify({ value: value })
    })
    .then(function(response) {
        return response.text();
    })
    .then(function(result) {
        if(result){
          localStorage.setItem('json', result)
          window.location.replace('claimmap/src/visualization/index.html')
        }
    })
    .catch(function(error) {
        console.log(error);
    });
});
