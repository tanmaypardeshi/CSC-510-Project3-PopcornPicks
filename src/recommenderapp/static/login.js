//Function for login in
function Login(){
    email = document.getElementById("inputemail").value
    pass = document.getElementById("inputpassword").value
    login_alert = document.getElementById("login_alert")
    console.log(email)  /* just for us to see outputs on the console for testing */
    console.log(pass)
    $.ajax({
        url: "/processLogin",
        type: 'POST',
        data: {'email': email, 'password': pass, 'role': "user"},
        success:function(returned_data){
            if (returned_data['success'] === 1){
                window.location.href = "/"
            }
            else{
                login_alert.style.display = "flex";
            }
        }

    })
}
