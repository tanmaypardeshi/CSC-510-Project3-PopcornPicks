$(document).ready(function () {
  $(function () {
    $("#searchBox").autocomplete({
      source: function (request, response) {
        $.ajax({
          type: "POST",
          url: "/search",
          dataType: "json",
          cache: false,
          data: {
            q: request.term,
          },
          success: function (data) {
            response(data);
          },
          error: function (jqXHR, textStatus, errorThrown) {
            console.log(textStatus + " " + errorThrown);
          },
        });
      },
      select: function (event, ui) {
        var ulList = $("#selectedMovies");
        // Check if the value already exists in the list
        if (ulList.find('li:contains("' + ui.item.value + '")').length > 0) {
          $("#searchBox").val("");
          return false;
        }

        var li = $("<li class='list-group-item'/>")
          .text(ui.item.value)
          .appendTo(ulList);
        $("#searchBox").val("");
        return false;
      },

      // changed the min-length for searching movies from 2 to 1
      minLength: 1,
    });
  });

  $("#predict").click(function () {
    $("#loader").attr("class", "d-flex justify-content-center");

    var movie_list = [];

    $("#selectedMovies li").each(function () {
      movie_list.push($(this).text());
    });

    var movies = { movie_list: movie_list };

    // Clear the existing recommendations
    $("#predictedMovies").empty();

    // if movies list empty then throw an error box saying select atleast 1 movie!!
    if (movie_list.length == 0) {
      alert("Select atleast 1 movie!!");
    }

    //fetching poster using /getposterurl

    function fetchPosterURL(imdbID) {
      var posterURL = null;
      $.ajax({
          type: "GET",
          url: "/getPosterURL", 
          dataType: "json",
          data: { imdbID: imdbID },
          async: false, 
          success: function (response) {
              posterURL = response.posterURL;
          },
          error: function (error) {
              console.log("Error fetching poster URL: " + error);
          },
      });
  
      return posterURL;
    };
    // poster and reviews feature

    // function fetchPosterAndReviews(imdbID) {
    //   var details = null;
    //   $.ajax({
    //       type: "GET",
    //       url: "/getPosterAndReviews",
    //       dataType: "json",
    //       data: { imdbID: imdbID },
    //       async: false,
    //       success: function (response) {
    //           details = response;
    //       },
    //       error: function (error) {
    //           console.log("Error fetching poster and reviews: " + error);
    //       },
    //   });
  
    //   return details;
    // }  

    $.ajax({
      type: "POST",
      url: "/predict",
      dataType: "json",
      contentType: "application/json;charset=UTF-8",
      traditional: "true",
      cache: false,
      data: JSON.stringify(movies),
      success: function (response) {
        var data = JSON.parse(response);
        console.log(data);
        var list = $("#predictedMovies");
        var title = $("<br><br><h2>Recommended Movies</h2>");
        $("#recommended_block").append(title);
        for (var i = 0; i < data.length; i++) {
          var column = $('<div class="col-sm-12"></div>');
          var card = `<div class="card movie-card">
              <div class="row no-gutters">
                  <div class="col-md-8">
                      <div class="card-body">
                          <h5 class="card-title">${data[i].title}</h5>
                          <h6 class="card-subtitle mb-2 text-muted">${data[i].runtime} minutes</h6>
                          <p class="card-text">${data[i].overview}</p>
                      </div>
                      <div class="card-footer text-muted" style="position: absolute; bottom: 0; left: 0; width: auto;">Genres: ${data[i].genres}</div>
                      <a target="_blank" href="https://www.imdb.com/title/${data[i].imdb_id}" class="btn btn-primary" style="position: absolute; bottom: 50px; left: 0;">Check out IMDb Link</a>
                  </div>
                  <div class="col-md-4">
                      <img src="${fetchPosterURL(data[i].imdb_id)}" alt="Movie Poster" class="poster-image" style="width: 75%; height: auto; margin: 0;">
                  </div>
              </div>
          </div>`;
          column.append(card);
          list.append(column);
        }
        $("#loader").attr("class", "d-none");
      },
      error: function (error) {
        console.log("ERROR ->" + error);
        $("#loader").attr("class", "d-none");
      },
    });
  });

  window.addEventListener("popstate", function (event) {
    // Check if the user is navigating back
    if (event.state && event.state.page === "redirect") {
      // Redirect the user to a specific URL
      window.location.href = "/";
      location.reload();
    }
  });

  var FeedbackData;

  $("#feedback").click(function () {
    notifyMeButton = document.getElementById("checkbox");
    notifyMeButton.disabled = false;
    var myForm = $("fieldset");
    var data = {};
    var labels = {
      1: "Dislike",
      2: "Yet to watch",
      3: "Like",
    };

    // to check if any movies selected before giving feedback
    if(myForm.length == 0){
      alert("No movies found. Please add movies to provide feedback.");
      return;
    }
    var error = false; // Flag to track errors

    for (var i = 0; i < myForm.length; i++) {
      var input = $("#" + i)
        .find("div")
        .find("input:checked")[0];
      var movieName = $("#" + i)
        .find("div")
        .find("li")[0].innerText;

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
      type: "POST",
      url: "/feedback",
      dataType: "json",
      contentType: "application/json;charset=UTF-8",
      traditional: "true",
      cache: false,
      data: JSON.stringify(data),
      success: function (response) {
        window.location.href = "/success";
      },
      error: function (error) {
        console.log("ERROR ->" + error);
      },
    });
  });

  $("#notifyButton").click(function () {
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
      type: "POST",
      url: "/sendMail",
      dataType: "json",
      contentType: "application/json;charset=UTF-8",
      traditional: "true",
      cache: false,
      data: JSON.stringify(data),
      success: function (response) {
        $("#loaderSuccess").attr("class", "d-none");
        $("#emailSentSuccess").show();
        setTimeout(function () {
          $("#emailSentSuccess").fadeOut("slow");
        }, 2000);
        $('#area1').attr('placeholder', 'Email'); 
        $('#emailField').val('');
      },
      error: function (error) {
        $("#loaderSuccess").attr("class", "d-none");
        console.log("ERROR ->" + error);
        localStorage.removeItem("fbData");
      },
    });
  });
  
});
