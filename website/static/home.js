function like(post_id) {
  fetch('/like', {
    method: 'POST',
    body: JSON.stringify({ post_id: post_id }),
  }).then((_res) => {
    window.location.href = '/home'
  })
}
