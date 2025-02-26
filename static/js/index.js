function toggleMobileMenu(menu) {
  menu.classList.toggle("open");
}
function checkExists(number) {
  /* 
  A function to check if a register number exists in the database
  */
  xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200) {
      let data = JSON.parse(xhttp.responseText);
      if (data.exist === true) {
        reply = confirm(
          "رقم المنشأة موجود بالفعل: " +
          number.toString() +
          "\nهل تود تعديل بيانات هذه المنشأة ؟"
        );
        if (!reply) {
          document.getElementById("register_number").value = "";
        } else {
          window.location = "/est/" + number;
        }
      }
    }
  };
  xhttp.open("POST", "/api/check", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("register_number=" + number.toString());
}

function checkRFIDExists(rfid) {
  /*
  A function to check if a RFID code exists in the database
  */
  xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200) {
      let data = JSON.parse(xhttp.responseText);
      if (data.exist === true) {
        reply = confirm(
          "رقم المعرف موجود بالفعل: " +
          rfid.toString() +
          "\nهل تود تعديل بيانات هذه المنشأة ؟"
        );
        if (!reply) {
          document.getElementById("register_number").value = "";
        } else {
          window.location = "/est/" + data.register_number.toString();
        }
      }
    }
  };
  xhttp.open("POST", "/api/rfid/check", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("rfid=" + rfid.toString());
}
function checkEmailExists(email) {
  /*
  A function to check if an email exists in the database
  */
  xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200) {
      let data = JSON.parse(xhttp.responseText);
      if (data.exist === true) {
        reply = confirm(
          "هذا البريد موجود بالفعل: " +
          email.toString() +
          "\nهل تود تعديل بيانات هذه المنشأة ؟"
        );
        if (!reply) {
          document.getElementById("register_number").value = "";
        } else {
          window.location = "/est/" + data.register_number.toString();
        }
      }
    }
  };
  xhttp.open("POST", "/api/email/check", true);
  xhttp.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
  xhttp.send("email=" + email.toString());
}
function printPdfReport() {
  /*
  print page to pdf. a temporary solution
  */
  window.print();
}

function updateTable() {
  /*
  a function to keep checking if the there is any new data in the database from Arduino
  */
  let count = 3000;
  resource_timer = setTimeout(updateTable, count);

  xhttp = new XMLHttpRequest();
  xhttp.onreadystatechange = function () {
    if (this.readyState === 4 && this.status === 200) {
      let data = JSON.parse(xhttp.responseText);
      if (data.found === true) {
        if (document.getElementById("rifd")) {
          if (data.code === document.getElementById("rifd").value) {
          } else {
            if (data.found === true) {
              document.getElementById("dataholder").innerHTML = data.template;
            }
          }
        } else {
          if (data.found === true) {
            document.getElementById("dataholder").innerHTML = data.template;
          }
        }

        function geoFindMe() {
          /*
          a function to get the current location of the user
  */
          const status = document.querySelector("#status");

          function success(position) {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            status.textContent = "";
            initMap(latitude, longitude);
            document.getElementById("latitude").value = latitude;
            document.getElementById("longitude").value = longitude;
          }

          function error() {
            status.textContent = "Unable to retrieve your location";
          }

          if (!navigator.geolocation) {
            status.textContent = "Geolocation is not supported by your browser";
          } else {
            status.textContent = "Locating…";
            navigator.geolocation.getCurrentPosition(success, error);
          }
        }
        document.querySelector("#find-me").addEventListener("click", geoFindMe);
        document.getElementById("status-1").onchange = function () {
          document.getElementById("notes-group").style.visibility = "";
        };
        document.getElementById("status-0").onchange = function () {
          document.getElementById("notes-group").style.visibility = "hidden";
          document.getElementById("notes").value = "";
        };

        function initMap(latitude, longitude) {
          var map = document.getElementById("map");
          var infoWindow = document.getElementById("infoWindow");
          map.innerHTML =
            '<iframe width="100%" height="100%" src="https://maps.google.com/maps?q=' +
            latitude +
            "," +
            longitude +
            '&hl=es;z=14&amp;output=embed" frameborder="0" style="border:0"></iframe>';
        }
      }
    }
  };
  xhttp.open("GET", "api/query", true);
  xhttp.send();
}
function confirmDearchive(link) {
  /*
  a function to confirm if the user wants to dearchive the selected inspection
  */
  if (confirm("هل أنت متأكد أنك تريد حذف أرشفة هذه المعاينة ؟")) {
    location.href = link;
  }
}
function updatelocation(latitude, longitude) {
  /*
  a function to show the map of the location of the inspection in popup window
  */
  x = document.getElementById("mapshow");
  x.innerHTML =
    '<div class="mapouter"><div class="gmap_canvas"><iframe width="480" height="500" id="gmap_canvas" src="https://maps.google.com/maps?q= ' +
    latitude +
    "," +
    longitude +
    '&t=&z=13&ie=UTF8&iwloc=&output=embed" frameborder="0" scrolling="no" marginheight="0" marginwidth="0"></iframe><br><style>.mapouter{position:relative;text-align:right;height:500px;width:600px;}</style><a href="https://www.embedgooglemap.net">integrate google maps into website</a><style>.gmap_canvas {overflow:hidden;background:none!important;height:500px;width:600px;}</style></div></div>';
}
function updateImage(path) {
  /*
  a function to show the picture of the inspection in popup window
  */
  document.getElementById("myImg").src = path;
}
function confirmToPost(link) {
  /*
  a function to confirm if the user wants to archive the selected inspection
  */
  if (confirm("هل أنت متأكد أنك تريد أرشفة هذه المعاينة ؟")) {
    location.href = link;
  }
}

function showNote(txt) {
  /*
  a function to show the notes of the inspection in popup window
  */
  console.log(txt);
  document.getElementById("notetext").textContent = txt;
}
