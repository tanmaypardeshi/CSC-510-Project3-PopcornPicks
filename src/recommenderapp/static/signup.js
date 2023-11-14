//Function for sign out
function Signup(){
    email = document.getElementById("inputemail").value
    pass = document.getElementById("inputpassword").value
    sign_alert = document.getElementById("failed_sign_in")
    console.log(email)  /* just for us to see outputs on the console for testing */
    console.log(pass)
    $.ajax({
        url: "/processSignup",
        type: 'POST',
        data: {'email': email, 'password': pass, 'role': "user"}, // role will matter later
        success:function(returned_data){
            if (returned_data['success'] === 1){
                // happens if the signup is valid
                window.location.href = "/login"
            }
            else{
                // happens if the signup is not valid
                //window.location.href = "/signup"
                sign_alert.style.display = "flex";
            }
        }
    })
}
