$(document).ready(function() {
  $(function() {
    $("#searchBox").autocomplete({
      source : function(request, response) {
        $.ajax({
          type : "POST",
          url : "/search",
          dataType : "json",
          cache : false,
          data : {
            q : request.term,
          },
          success : function(data) { response(data); },
          error : function(
              jqXHR, textStatus,
              errorThrown) { console.log(textStatus + " " + errorThrown); },
        });
      },
      select : function(event, ui) {
        var ulList = $("#selectedMovies");
        // Check if the value already exists in the list
        if (ulList.find('li:contains("' + ui.item.value + '")').length > 0) {
          $("#searchBox").val("");
          return false;
        }
        var deleteButton = $(
            "<button type='button' class='btn btn-danger btn-sm'>Delete</button>")
        // Attach click event to the delete button
        deleteButton.click(function() {
          $(this)
              .closest('li')
              .remove(); // Removes the parent <li> of the button
        });

        var li =
            $("<li class='list-group-item d-flex justify-content-between align-items-center'/>")
                .text(ui.item.value)
                .append(deleteButton)
                .appendTo(ulList);
        $("#searchBox").val("");
        return false;
      },

      // changed the min-length for searching movies from 2 to 1
      minLength : 1,
    });
  });

  $("#predict").click(function() {
    $("#loader").attr("class", "d-flex justify-content-center");

    var movie_list = [];
    
    $("#selectedMovies li").each(function () {
      movie_list.push($(this).text());
    });
    var selected_genre = $("#genreSelect").val(); // Get the selected genre
    var release_year = $("#releaseYear").val();
    if (release_year) {
        release_year = parseInt(release_year);
    }
    var movies = { movie_list: movie_list, genre: selected_genre, year: release_year };

    // Clear the existing recommendations
    $("#predictedMovies").empty();
    // if movies list empty then throw an error box saying select atleast 1
    // movie!!
    if (movie_list.length == 0) {
      alert("Select atleast 1 movie!!");
    }

    // fetching poster using /getposterurl

    function fetchPosterURL(imdbID) {
      var posterURL = null;
      $.ajax({
        type : "GET",
        url : "/getPosterURL",
        dataType : "json",
        data : {imdbID : imdbID},
        async : false,
        success : function(response) { posterURL = response.posterURL; },
        error : function(
            error) { console.log("Error fetching poster URL: " + error); },
      });

      return posterURL;
    };

    $.ajax({
      type : "POST",
      url : "/predict",
      dataType : "json",
      contentType : "application/json;charset=UTF-8",
      traditional : "true",
      cache : false,
      data : JSON.stringify(movies),
      success : function(response) {
        var data = JSON.parse(response);
        var list = $("#predictedMovies");
        var title = $("<h2>Recommended Movies</h2>");
        var modalParent = document.getElementById("modalParent");
        $("#recommended_block").append(title);
        var row = $('<div class="row"></div>');
        for (var i = 0; i < data.length; i++) {
          if (i > 0 && i % 3 === 0) {
            // After every 3 movies, append the row to the list and create a new row
            list.append(row);
            row = $('<div class="row"></div>'); // Create a new row for the next set of 3 movies
          }
          var column = $('<div class="col-md-4"></div>');
          var card = `<div class="card movie-card">
            <div class="row no-gutters">
              <div class="col-md-6">
                <div class="card-body">
                  <a type="button" class="btn btn-warning ms-2" href="/movies?movie_id=${data[i].movieId}">${data[i].title}</a>
                  <h6 class="card-subtitle mb-2 text-muted">${data[i].runtime} minutes</h6>
                  <p class="card-text" hidden>${data[i].overview}</p>
                  <a target="_blank" href="/movies?movie_id=${data[i].movieId}" class="btn btn-primary" hidden>Check out the movie!</a>
                  <button type="button" class="btn btn-primary" data-bs-toggle="modal" id="modalButton-${i}" data-bs-target="#reviewModal-${i}">Write a review</button>
                  <div class="movieId" hidden>${data[i].movieId}</div>
                  <div class="genres" hidden>${data[i].genres}</div>
                  <div class="imdb_id" hidden>${data[i].imdb_id}</div>
                  <div class="poster_path" hidden>${data[i].poster_path}</div>
                  <div class="index" hidden>${i}</div>
                </div>
              </div>
              <div class="col-md-6">
                  <img src="${fetchPosterURL(data[i].imdb_id)}" alt="Movie Poster" class="poster-image" style="width: 75%; height: auto; margin: 0;">
              </div>
            </div>`
          var modal = `
          <div class="modal fade" id="reviewModal-${
              i}" tabindex="-1" aria-labelledby="reviewModalLabel" aria-hidden="true">
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="reviewModaLabel">Write your review</h5>
                  <button type="button" onclick="modalOnClose(${
              i})" id="closeModal-${
              i}" class="btn-close" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                  <div class="mb-3">
                    <textarea class="form-control" rows=10 id="review-${
              i}"></textarea>
                  </div>
                  <div class="mb-3">
                    <label for="score-${i}" class="form-label">Select Score:</label>
                    <select class="form-select" id="score-${i}">
                        <option value="1.0">1.0</option>
                        <option value="2.0">2.0</option>
                        <option value="3.0">3.0</option>
                        <option value="4.0">4.0</option>
                        <option value="5.0">5.0</option>
                    </select>
                  </div>
                </div>
                <div class="modal-footer">
                  <button type="button" onclick="modalOnClick(${
              i})" id="saveChanges-${
              i}" class="btn btn-primary modal-save">Save changes</button>
                </div>
              </div>
            </div>
          </div>`
          modalParent.innerHTML += modal;
          column.append(card);
          row.append(column);
        }
        list.append(row)
        $("#loader").attr("class", "d-none");
      },
      error : function(error) {
        console.log("ERROR ->" + error);
        $("#loader").attr("class", "d-none");
      },
    });
  });

  $("#create").click(function() {
    $("#loader").attr("class", "d-flex justify-content-center");

    var movie_list = [];

    $("#selectedMovies li").each(function () {
      movie_list.push($(this).text());
    });
    var movies = { movie_list: movie_list};

    // Clear the existing recommendations
    $("#listMovies").empty();
    // if movies list empty then throw an error box saying select atleast 1
    // movie!!
    if (movie_list.length < 5) {
      alert("Select 5 movies!!");
    }

    // fetching poster using /getposterurl

    function fetchPosterURL(imdbID) {
      var posterURL = null;
      $.ajax({
        type : "GET",
        url : "/getPosterURL",
        dataType : "json",
        data : {imdbID : imdbID},
        async : false,
        success : function(response) { posterURL = response.posterURL; },
        error : function(
            error) { console.log("Error fetching poster URL: " + error); },
      });

      return posterURL;
    };

    $.ajax({
      type : "POST",
      url : "/displaylist",
      dataType : "json",
      contentType : "application/json;charset=UTF-8",
      traditional : "true",
      cache : false,
      data : JSON.stringify(movies),
      success : function(response) {
        var data = JSON.parse(response);
        var list = $("#listMovies");
        var title = $("<h2>List of Movies</h2>");
        var modalParent = document.getElementById("modalParent");
        $("#recommended_block").append(title);
        var row = $('<div class="row"></div>');
        for (var i = 0; i < data.length; i++) {
          if (i > 0 && i % 3 === 0) {
            // After every 3 movies, append the row to the list and create a new row
            list.append(row);
            row = $('<div class="row"></div>'); // Create a new row for the next set of 3 movies
          }
          var column = $('<div class="col-md-4"></div>');
          var card = `<div class="card movie-card">
            <div class="row no-gutters">
              <div class="col-md-6">
                <div class="card-body">
                  <a type="button" class="btn btn-warning ms-2" href="/movies?movie_id=${data[i].movieId}">${data[i].title}</a>
                  <h6 class="card-subtitle mb-2 text-muted">${data[i].runtime} minutes</h6>
                  <p class="card-text" hidden>${data[i].overview}</p>
                  <a target="_blank" href="/movies?movie_id=${data[i].movieId}" class="btn btn-primary" hidden>Check out the movie!</a>
                  <button type="button" class="btn btn-primary" data-bs-toggle="modal" id="modalButton-${i}" data-bs-target="#reviewModal-${i}" hidden>Write a review</button>
                  <div class="movieId" hidden>${data[i].movieId}</div>
                  <div class="genres" hidden>${data[i].genres}</div>
                  <div class="imdb_id" hidden>${data[i].imdb_id}</div>
                  <div class="poster_path" hidden>${data[i].poster_path}</div>
                  <div class="index" hidden>${i}</div>
                </div>
              </div>
              <div class="col-md-6">
                  <img src="${fetchPosterURL(data[i].imdb_id)}" alt="Movie Poster" class="poster-image" style="width: 75%; height: auto; margin: 0;">
              </div>
            </div>`
          var modal = `
          <div class="modal fade" id="reviewModal-${
              i}" tabindex="-1" aria-labelledby="reviewModalLabel" aria-hidden="true">
            <div class="modal-dialog">
              <div class="modal-content">
                <div class="modal-header">
                  <h5 class="modal-title" id="reviewModaLabel">Write your review</h5>
                  <button type="button" onclick="modalOnClose(${
              i})" id="closeModal-${
              i}" class="btn-close" aria-label="Close"></button>
                </div>
                <div class="modal-body">
                  <div class="mb-3">
                    <textarea class="form-control" rows=10 id="review-${
              i}"></textarea>
                  </div>
                  <div class="mb-3">
                    <label for="score-${i}" class="form-label">Select Score:</label>
                    <select class="form-select" id="score-${i}">
                        <option value="1.0">1.0</option>
                        <option value="2.0">2.0</option>
                        <option value="3.0">3.0</option>
                        <option value="4.0">4.0</option>
                        <option value="5.0">5.0</option>
                    </select>
                  </div>
                </div>
                <div class="modal-footer">
                  <button type="button" onclick="modalOnClick(${
              i})" id="saveChanges-${
              i}" class="btn btn-primary modal-save">Save changes</button>
                </div>
              </div>
            </div>
          </div>`
          modalParent.innerHTML += modal;
          column.append(card);
          row.append(column);
        }
        list.append(row)
        $("#loader").attr("class", "d-none");
      },
      error : function(error) {
        console.log("ERROR ->" + error);
        $("#loader").attr("class", "d-none");
      },
    });
  });

  window.addEventListener("popstate", function(event) {
    // Check if the user is navigating back
    if (event.state && event.state.page === "redirect") {
      // Redirect the user to a specific URL
      window.location.href = "/";
      location.reload();
    }
  });

  var FeedbackData;

  $("#feedback").click(function() {
    notifyMeButton = document.getElementById("checkbox");
    notifyMeButton.disabled = false;
    var myForm = $("fieldset");
    var data = {};
    var labels = {
      1 : "Dislike",
      2 : "Yet to watch",
      3 : "Like",
    };

    // to check if any movies selected before giving feedback
    if (myForm.length == 0) {
      alert("No movies found. Please add movies to provide feedback.");
      return;
    }
    var error = false; // Flag to track errors

    for (var i = 0; i < myForm.length; i++) {
      var input = $("#" + i).find("div").find("input:checked")[0];
      var movieName = $("#" + i).find("div").find("li")[0].innerText;

      if (!input) {
        // If no selection is made, set error flag to true and break the loop
        error = true;
        break;
      }

      data[movieName] = labels[input.value];
    }

    if (error) {
      // Display an error message if there are missing selections
      alert("Please select a feedback for all movies.");
      return; // Exit the function without making the AJAX call
    }

    FeedbackData = data;
    localStorage.setItem("fbData", JSON.stringify(data));
    $.ajax({
      type : "POST",
      url : "/feedback",
      dataType : "json",
      contentType : "application/json;charset=UTF-8",
      traditional : "true",
      cache : false,
      data : JSON.stringify(data),
      success : function(response) { window.location.href = "/success"; },
      error : function(error) { console.log("ERROR ->" + error); },
    });
  });

  $("#notifyButton").click(function() {
    var data = JSON.parse(localStorage.getItem("fbData"));
    $("#loaderSuccess").attr("class", "d-flex justify-content-center");
    if (!data) {
      alert("No feedback data found. Please provide feedback.");
      return;
    }

    var emailString = $("#emailField").val();
    data.email = emailString;

    // Remove the "emailSent" flag to allow sending the email again
    localStorage.removeItem("emailSent");

    $.ajax({
      type : "POST",
      url : "/sendMail",
      dataType : "json",
      contentType : "application/json;charset=UTF-8",
      traditional : "true",
      cache : false,
      data : JSON.stringify(data),
      success : function(response) {
        $("#loaderSuccess").attr("class", "d-none");
        $("#emailSentSuccess").show();
        setTimeout(function() { $("#emailSentSuccess").fadeOut("slow"); },
                   2000);
        $('#area1').attr('placeholder', 'Email');
        $('#emailField').val('');
      },
      error : function(error) {
        $("#loaderSuccess").attr("class", "d-none");
        console.log("ERROR ->" + error);
        localStorage.removeItem("fbData");
      },
    });
  });
});
