var socket = io();

document.addEventListener("DOMContentLoaded", () =>{
    var current = ""
    var players = []
    var current_user = document.querySelector("#current_user").value;
    var length = ""
    socket.on("connect", function(){
        socket.emit("joingame", {data: "connected", url: window.location.href})
    })
    socket.on("players", function(data){
        var div = document.querySelector("#users")
        var flashdiv = document.querySelector("#flash-msg-waiting");
        if (div.firstChild){
            div.removeChild(div.firstChild);
        }
        players = data["players"]
        const onlinePlayers = document.createElement("p")
        onlinePlayers.innerHTML= players
        div.append(onlinePlayers)
        if (players.length == 2){
            if (flashdiv.firstChild){
                flashdiv.removeChild(flashdiv.firstChild)
            }
            socket.emit("change", {url: window.location.href})
        }
        else{
            const waiting = document.createElement("div")

            waiting.setAttribute("class", "alert alert-info");
            waiting.innerHTML = "waiting for another player, send this link: " + window.location.href;
            flashdiv.append(waiting);
        }
        
    })
    socket.on("images", function(data){
        var div = document.querySelector("#results-pvp")
        var msgdiv = document.querySelector("#flash-msg")
        length = data["images"][4]
        document.querySelector("#length").innerHTML = length
        document.querySelector("#answer").value = data["images"][5]
        if (div.firstChild){
            div.removeChild(div.firstChild);
        }
        if (msgdiv.firstChild){
            msgdiv.removeChild(msgdiv.firstChild)
        }

        const imgcontainer = document.createElement("div")
        imgcontainer.setAttribute("id", "image-container-pvp")
        document.querySelector("#results-pvp").append(imgcontainer)
        data["images"].slice(0,4).forEach(element => {
            document.querySelector("#sendguess").style.display = "none";
            const img = document.createElement("img");
            img.src = element;
            img.setAttribute("class", "image-pvp")
            document.querySelector("#image-container-pvp").append(img)
        });
        if (current != current_user){
            document.querySelector("#form-vs-friend").style.display = "block";
            document.querySelector("#lives").innerHTML = 3;
        }
    })
    document.querySelector("#check-btn").addEventListener("click", ()=>{
        var div = document.querySelector("#results-pvp")
        event.preventDefault();
        if (document.querySelector("#guessbox").value.toLowerCase() == document.querySelector("#answer").value.toLowerCase()){
            socket.emit("change", {url: window.location.href})
            if (div.firstChild){
                div.removeChild(div.firstChild);
            }
            location.reload();
            socket.emit("correct", {url: window.location.href, user: current_user})
            
        }
        else if (document.querySelector("#lives").innerHTML == 1){
            socket.emit("change", {url: window.location.href})
            alert("correct answer was: " + document.querySelector("#answer").value)
            if (div.firstChild){
                div.removeChild(div.firstChild);
            }
            socket.emit("wrong", {url: window.location.href, user: current_user})
        }
        document.querySelector("#lives").innerHTML -= 1;
    })

    document.querySelector("#guessbox").addEventListener("input", ()=>{
        var newtext = document.querySelector("#guessbox").value + length.substring(document.querySelector("#guessbox").value.length);
        document.querySelector("#length").innerHTML = newtext
        if (newtext.length > length.length){
            document.querySelector("#length").style.color = "rgb(255, 90, 90)";
        }else{
            document.querySelector("#length").style.color = "white";
        }
    })

    socket.on("nicejob", function(data){
        var div = document.querySelector("#flash-msg");
        
        const success = document.createElement("div")
        success.setAttribute("class", "alert alert-success");
        success.innerHTML = data["info"]
        div.append(success);

    })
    socket.on("badjob", function(data){
        var div = document.querySelector("#flash-msg");
        
        const success = document.createElement("div")

        success.setAttribute("class", "alert alert-danger");
        success.innerHTML = data["info"];
        div.append(success);

    })

    document.querySelector("#guess-btn").addEventListener("click", ()=>{
        event.preventDefault();
        search = document.querySelector("#guess").value;
        socket.emit("search", {search: search, url: window.location.href})
    })

    socket.on("updated", function(data) {
        if(data["current"] == current_user){
            document.querySelector("#form-vs-friend").style.display = "none";
            document.querySelector("#sendguess").style.display = "block";
        }else{
            document.querySelector("#sendguess").style.display = "none";
        }
        current = data["current"]
    })

    socket.on("disconnect", function(){
        socket.emit("leavegame", {data: "left", url: window.location.href})
    })
})