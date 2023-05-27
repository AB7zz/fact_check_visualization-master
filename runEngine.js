var input = document.getElementById('myInput');
var search = document.getElementById('search-addon');

// Add an event listener to the input element
search.addEventListener('click', function() {
  // Retrieve the current value of the input
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
        console.log(result);
        if(result === "success"){
          console.log('yo')
          window.location.replace('/idir/src/visualization/')
        }
    })
    .catch(function(error) {
        console.log(error);
    });



  // Do something with the value (e.g., log it to the console)
  console.log(value);
});