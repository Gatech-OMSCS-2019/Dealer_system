$(document).ready(function () {


    $("a#result_list").click(function () {
        console.log("clicked")
        var resultList = $("div.detail_list").children("table");
        if(resultList.css('display') == 'none'){
            resultList.css('display','block');
        }else{
            resultList.css("display", 'none');
        }

    })
    var job_title = $.trim($("input[type='hidden']").val());
    console.log(job_title == 'Manager');
    console.log(job_title);
    if (job_title.includes("Manager")) {
        console.log("i am inside manage");
        $('select[name="advanced"]').css('display', 'block');
        $('label[for="id_advanced"]').css('display', 'block');
    }
    // if ($("input[type='chekcbox']").is(":checked")) {
    //
    // }
    // $('form.seller_info').find('.business').each(function () {
    //         $(this).css('display', 'none');
    //         $(this).prev().css('display', 'none');
    //     });
    var checkbox = $("input[type='checkbox']");
    if (checkbox.is(':checked')) {
            $('.business').each(function () {
                $(this).css('display', 'none');
                $(this).prev().css('display', 'none')
            });
            $('.individual').css('display', 'block');
            $('.individual').prev().css('display', 'block');
        } else {
            $('.business').each(function () {
                $(this).css('display', 'block');
                $(this).prev().css('display', 'block')

            });
            $('.individual').css('display', 'none');
            $('.individual').prev().css('display', 'none');

        }


    $('select option:nth-child(1)').attr('disabled', true);
    $('ul.errorlist').children('li').each(function () {
        $(this).addClass('alert alert-danger');
    })
    $("button[value='add seller']").click(function () {
        console.log('click add seller')
        $('.add_seller_errors').empty();
        var form = $("form.seller_info");
        if (form.css('display') == 'none') {
            form.css('display', 'block');
        } else {
            form.css('display', 'none');
        }
        var new_position = $('form.seller_info').offset();
        $('html, body').stop().animate({scrollTop: new_position.top}, 500);
    });

    $("a.login").click(function () {
        var login_form = $("form.login");
        if (login_form.css('display') == 'none') {
            login_form.css('display', 'block');
        } else {
            login_form.css('display', 'none');
        }
        $('html, body').stop().animate({scrollTop: $('form.login').offset().top + 300}, 500);

    })

    $("a.add_vehicle").click(function (e) {
        e.preventDefault();
        var form = $("form.add_vehicle");
        if (form.css('display') == 'none') {
            form.css('display', 'block');
        } else {
            form.css('display', 'none');
        }
        var new_position = $('form#add_vehicle').offset();
        $('html, body').stop().animate({scrollTop: new_position.top}, 500);

    })
    $('input[type="checkbox"]').change(function () {
        console.log('check box is changed')
        console.log($(this).is(':checked'))
        if ($(this).is(':checked')) {
            $('.business').each(function () {
                $(this).css('display', 'none');
                $(this).prev().css('display', 'none')
            });
            $('.individual').css('display', 'block');
            $('.individual').prev().css('display', 'block');
        } else {
            $('.business').each(function () {
                $(this).css('display', 'block');
                $(this).prev().css('display', 'block')

            });
            $('.individual').css('display', 'none');
            $('.individual').prev().css('display', 'none');

        }
    })


    $('tr[data-href]').click(function () {
        console.log(" detail is clicked");
        console.log( $(this).data('href'));
        document.location = $(this).data('href');
        return false;
    })
    $("input[name='sumbit_search']").click(function (e) {
        console.log("search button is clicked");
        $("div.detail_list").css("display", 'block');
    })
})