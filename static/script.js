let cardContainer = document.getElementById("form");
let content = document.getElementById("area");


window.onload = function(){
    let form = document.getElementById("remark_request_form");
    form.addEventListener("submit", function(e){
        e.preventDefault();
        alert("Form Submission Successful");
        form.submit();
    })
}

console.log("hi");