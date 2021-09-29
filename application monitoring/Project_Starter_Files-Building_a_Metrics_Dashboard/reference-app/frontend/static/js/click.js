$(document).ready(function () {

    // all custom jQuery will go here
    $("#firstbutton").click(function () {
        $.ajax({
            url: "http://backend-service.default.svc.cluster.local", success: function (result) {
                $("#firstbutton").toggleClass("btn-primary:focus");
                }
        });
    });
    $("#secondbutton").click(function () {
        $.ajax({
            url: "http://trial-service.default.svc.cluster.local", success: function (result) {
                $("#secondbutton").toggleClass("btn-primary:focus");
            }
        });
    });
    $("#thirdbutton").click(function () {
        $.ajax({
            url: "http://frontend-service.default.svc.cluster.local:8080", success: function (result) {
                $("#thirdbutton").toggleClass("btn-primary:focus");
            }
        });
    });
});