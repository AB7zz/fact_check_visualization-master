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
  window.location.replace('/visualization')
}

search.addEventListener('click', function() {
  var value = input.value;

  localStorage.setItem('search', value)

  fetch('/search', {
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
          window.location.replace('/visualization')
        }
    })
    .catch(function(error) {
        console.log(error);
    });
});