const sendSound = new Audio("/static/sounds/sendmsg.mp3");
sendSound.volume = 0.2;
async function sendtext(){

    const input = document.getElementById("prompt");
    const prompt = input.value;
    sendSound.currentTime = 0;
    sendSound.play();

    if(prompt.trim() === "")
        return;

    // Show user's message immediately
    addMessage(prompt, "user");

    input.value = "";

    const response = await fetch("/chat",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            prompt:prompt
        })
    });

    const data = await response.json();

    // Show Sage's reply
    addMessage(data.reply, "bot");
}

function addMessage(text, sender){

    const chat = document.getElementById("chatarea");

    const li = document.createElement("li");

    if(sender === "user"){
        li.className = "user-msg";
    }
    else{
        li.className = "bot-msg";
    }

    li.innerHTML = text;

    chat.appendChild(li);

    // Auto-scroll to the latest message
    chat.scrollTop = chat.scrollHeight;
}


function closelogin(){
    window.location.href = "start.html"
}
function AddDocument() {

    const docs = document.getElementById("docs");

    docs.style.display =
        docs.style.display === "flex" ? "none" : "flex";

    docs.style.flexDirection = "column";
}

function showProfile(){
    const prof = document.getElementById("profile");

    prof.style.display =
        prof.style.display === "flex" ? "none" : "flex";

    prof.style.flexDirection = "column";

}
function logout() {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "start.html";
}
function indexfile(){
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/templates/index.html"
}
function uploadragdoc(){
    document.getElementById("fileinput").click();
}
document.getElementById("fileinput").addEventListener("change", function(){
    const file = this.files[0]
    if (!file) return;
    const extension = file.name.split('.').pop().toLowerCase();

    if (extension === "pdf") {

    document.getElementById("prev").innerHTML = `
        <i class="fa-solid fa-file-pdf" style="color:red;font-size:70px; opacity=100%"></i>
        
    `;

}
else if (extension === "doc") {

    document.getElementById("prev").innerHTML = `
        <i class="fa-solid fa-file-word" style="color:blue;font-size:70px; opacity=100%"></i>
        
    `;

}
else if (extension === "docx") {

    document.getElementById("prev").innerHTML = `
        <i class="fa-solid fa-file-word" style="color:blue;font-size:70px; opacity=100%"></i>
        
    `;
}

    document.getElementById("meta").innerHTML =
        "📄 " + file.name;

    const formdata = new FormData();
    formdata.append("document", file);
    fetch("/upload", {
        method:"POST",
        body:formdata
    })
    .then(response => response.text())
    .then(data=>{
        if (data.status === "success") {
                console.log("file uploaded", data.filename);
        }

    })
    .catch(error=>{
        console.error(error);
    })
})

async function sendprompt(){
    sendSound.currentTime = 0;
    sendSound.play();
    const input = document.getElementById("docprmt");
    ragprompt = input.value;
    console.log("prompt: ", `${ragprompt}`);

    if(ragprompt.trim() === "")
        return;

    // Show user's message immediately
    addragMessage(ragprompt, "user");

    input.value = "";

    const response = await fetch("/docresponse",{
        method:"POST",
        headers:{
            "Content-Type":"application/json"
        },
        body:JSON.stringify({
            ragprompt:ragprompt
        })
    });

    const data = await response.json();

    // Show Sage's reply
    addragMessage(data.reply, "bot");
    console.log(data.reply);
}

function addragMessage(text, sender){

    const chat = document.getElementById("ragchatarea");

    const li = document.createElement("li");



    if(sender === "user"){
        li.className = "user-msg";
    }
    else{
        li.className = "bot-msg";
    }

    li.innerHTML = text;

    chat.appendChild(li);

    // Auto-scroll to the latest message
    chat.scrollTop = chat.scrollHeight;
}
