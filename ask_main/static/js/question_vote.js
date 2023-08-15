function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
const csrftoken = getCookie('csrftoken');


  $(".like").on('click', function (ev) {
    const request = new Request(
        'http://127.0.0.1:8000/like/',
    {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        method: 'POST',
        mode: 'cors',
        body: "essence=" + $(this).data('essence') + "&question_id=" + $(this).data("id"),
    }
  );

    fetch(request)
    .then(response_raw => response_raw.json())
    .then(response_json => {

        $(this).parent().find("span.like-count").text(response_json.like_count);
        console.log($(this).parent().find("span.like-count").text());

    })
    .catch(error => console.error(error));
 });

  $(".dislike").on('click', function (ev) {
    const request = new Request(
        'http://127.0.0.1:8000/dislike/',
    {
        headers: {
            'X-CSRFToken': csrftoken,
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'
        },
        method: 'POST',
        mode: 'cors',
        body: "essence=" + $(this).data('essence') + "&question_id=" + $(this).data("id"),
    }
  );

    fetch(request)
    .then(response_raw => response_raw.json())
    .then(response_json => {

        $(this).parent().find("span.like-count").text(response_json.like_count);
        console.log($(this).parent().find("span.like-count").text());

    })
    .catch(error => console.error(error));

 });



