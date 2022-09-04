// 二重サブミット防止
$(function(){
    $('.submit-only-one').submit(function(){
        $(this).find(':submit').text('送信');
        //$('form').each(function(i, elem) {
        //    $(elem).find(':submit').prop('disabled', 'true');
        //});
        $(this).find(':submit').prop('disabled', 'true');
    });
});

// tooltip用
(function() {
    window.addEventListener("load", function() {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    });
})();


