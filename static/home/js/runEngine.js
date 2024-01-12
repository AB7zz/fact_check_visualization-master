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
  // window.location.href = 'claimmap/visualization'
}
search.addEventListener('click', function() {
  var value = input.value;

  localStorage.setItem('search', value);

fetch('/claimmap/claimmap/search', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ value: value }),
  // timeout: 300000, // Set a timeout of 30 seconds (adjust as needed)
})
  .then(function(response) {
    console.log('Response status:', response.status); // Log response status
    return response.text();
  })
  .then(function(result) {
    console.log('Result:', result); // Log the result
    if (result) {
      localStorage.setItem('json', result);
      window.location.replace('claimmap/visualization');
    }
  })
  .catch(function(error) {
    console.error('Fetch error:', error); // Log any fetch errors
  });
});

