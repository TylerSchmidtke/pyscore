function challengeSubmission(form_id) {
    var form = document.getElementById(form_id)
    form.on('submit', function (e) {
        e.preventDefault();
        
        $.ajax({
            type: 'post',
            url: '/',
            data: $('form').serialize(),
            success: function () {
                alert("submitted")
            }
        })
        
    })
}