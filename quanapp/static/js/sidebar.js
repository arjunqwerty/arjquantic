var check = "0";
window.onload = openclose();
function openclose() {
    if(check == "0") {
        //Side navbar
        document.getElementById("main").style.marginLeft = "0%";
        document.getElementById("main").style.width = "100%";
        document.getElementById("mySidenav").style.width = "0%";
        // Section 2
        document.getElementById("section2").children.item(0).children.item(0).children.item(0).children.item(0).children.item(0).children.item(1).children.item(0).style.width = "100px";
        document.getElementById("section2").children.item(1).children.item(0).children.item(0).children.item(0).children.item(0).children.item(1).children.item(0).style.width = "80px";
        document.getElementById("section2").children.item(2).children.item(0).children.item(0).children.item(0).children.item(0).children.item(1).children.item(0).style.width = "80px";
        // Section 3
        document.getElementById("section3").children.item(1).children.item(0).children.item(2).style.width = "100%";
        document.getElementById("section3").children.item(2).children.item(0).children.item(2).style.width = "100%";
        document.getElementById("section3").children.item(3).children.item(0).children.item(0).style.width = "100%";
        document.getElementById("section3").children.item(3).children.item(0).children.item(0).style.height = "100%";
        check = "1";
    } else {
        //Side navbar
        document.getElementById("main").style.marginLeft = "15%";
        document.getElementById("main").style.width = "85%";
        document.getElementById("mySidenav").style.width = "15%";
        // Section 2
        document.getElementById("section2").children.item(0).children.item(0).children.item(0).children.item(0).children.item(0).children.item(1).children.item(0).style.width = "85px";
        document.getElementById("section2").children.item(1).children.item(0).children.item(0).children.item(0).children.item(0).children.item(1).children.item(0).style.width = "68px";
        document.getElementById("section2").children.item(2).children.item(0).children.item(0).children.item(0).children.item(0).children.item(1).children.item(0).style.width = "68px";
        // Section 3
        document.getElementById("section3").children.item(1).children.item(0).children.item(2).style.width = "100%";
        document.getElementById("section3").children.item(2).children.item(0).children.item(2).style.width = "100%";
        document.getElementById("section3").children.item(3).children.item(0).children.item(0).style.width = "100%";
        document.getElementById("section3").children.item(3).children.item(0).children.item(0).style.height = "100%";
        check = "0";
    }
}
