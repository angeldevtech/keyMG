// Common Animations

var prevScrollpos = window.pageYOffset;

window.onscroll = function() {
  var currentScrollPos = window.pageYOffset;

  if (prevScrollpos > currentScrollPos) {
    document.querySelector("header").classList.remove("hide");
  } else {
    document.querySelector("header").classList.add("hide");
  }

  prevScrollpos = currentScrollPos;
};

// New Playlist

const plusButton = document.getElementById('plus');
const button1 = document.getElementById('spotify');
const button2 = document.getElementById('discover');

if (plusButton != null){
  plusButton.addEventListener('click', function() {
    button1.classList.toggle('visible');
    button2.classList.toggle('visible');
  });
}

// API handling

const request = (url) => {
  const request = (window.XMLHttpRequest) ? new XMLHttpRequest() : new ActiveXObject('Microsoft.XMLHTTP');
  request.open("GET", url, true);
  request.send();
  request.onload = () => {
    var objData = JSON.parse(request.responseText);
    createAutocompleteList(objData);
  }
}

function fetchDataFromAPI(inputValue) {
  request("/api/autocomplete?query="+ inputValue)
}

function createAutocompleteList(response) {
  console.log(response)
  console.log(typeof response)
  const autocompleteContainer = document.getElementById('autocomplete-container');

  autocompleteContainer.innerHTML = '';

  response.forEach(item => {
    const listItem = document.createElement('li');
    listItem.textContent = item.name_artist[0] + ' - ' + item.name_song;
    
    listItem.addEventListener('click', () => {
      console.log('Selected item:', item.name_song);
    });
    
    autocompleteContainer.appendChild(listItem);
  });
}

let timerId;

const inputField = document.getElementById('search'); 
inputField.addEventListener('input', (event) => {
  const inputValue = event.target.value;
  clearTimeout(timerId);
  timerId = setTimeout(() => {
    fetchDataFromAPI(inputValue);
  }, 500);
});