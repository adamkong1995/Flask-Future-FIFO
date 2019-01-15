$( document ).ready(function() {
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1;
    var yyyy = today.getFullYear();
  
    today = yyyy + "-" + ('0' + mm).slice(-2) + "-" + ('0' + dd).slice(-2);
    document.getElementById("date").value = today;
  });
  
  