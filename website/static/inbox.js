function chat(user_id) {
  fetch("/chat", {
    method: "POST",
    body: JSON.stringify({ user_id: user_id }),
  }).then((_res) => {
    window.location.href = "/inbox";
  });
}

/* scroll down to the bottom of a chat (if there are lots of messages) */
var elements = document.getElementsByClassName("messages-chat");
element = elements[0]
if (element) {
  element.scrollTop = element.scrollHeight;
}
