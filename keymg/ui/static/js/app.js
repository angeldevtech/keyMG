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

plusButton.addEventListener('click', function() {
  button1.classList.toggle('visible');
  button2.classList.toggle('visible');
});

// API handling

const request = (url) => {
  const request = (window.XMLHttpRequest) ? new XMLHttpRequest() : new ActiveXObject('Microsoft.XMLHTTP');
  request.open("GET", url, true);
  request.send();
  request.onload = () => {
      console.log('enviado');
  }
}

function fetchDataFromAPI(inputValue) {
  request("/api/search?query="+ inputValue)
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