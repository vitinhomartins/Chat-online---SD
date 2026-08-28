const username = document.getElementById("username");
const enter = document.getElementById("enter");

const message = document.getElementById("message");
const send = document.getElementById("send");

const chat = document.getElementById("chat");
const status = document.getElementById("status");

let name = "";
let socket = null;

enter.addEventListener("click", entrar);

username.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        entrar();
    }

});


function entrar() {

    name = username.value.trim();

    if (name === "") {
        alert("Digite seu nome!");
        return;
    }

    socket = new WebSocket("ws://localhost:8765");


    socket.onopen = function() {

        console.log("[CLIENT] Conectado.");

        socket.send(name);

        status.textContent = "● Conectado";

        username.disabled = true;
        enter.disabled = true;

        message.disabled = false;
        send.disabled = false;

        message.focus();
    };


    socket.onmessage = function(event) {

        const mensagem = document.createElement("p");

        mensagem.innerHTML = event.data;

        chat.appendChild(mensagem);

        chat.scrollTop = chat.scrollHeight;
    };


    socket.onclose = function() {

        status.textContent = "● Desconectado";

        message.disabled = true;
        send.disabled = true;

        console.log("[CLIENT] Desconectado.");
    };


    socket.onerror = function(error) {

        console.log("[CLIENT] Erro:", error);

        status.textContent = "● Erro";
    };
}


send.addEventListener("click", enviarMensagem);

message.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        enviarMensagem();
    }

});


function enviarMensagem() {

    const texto = message.value.trim();

    if (texto === "") {
        return;
    }

    socket.send(texto);

    message.value = "";

    message.focus();
}