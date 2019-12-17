$(document).ready(function () {

    $('select option:nth-child(1)').attr('disabled', true);


    $('input.business').each(function () {
        $(this).css('display', 'none');
        $(this).prev().css('display', ' none');
    })
    $('button.add_part_order').click(function () {
        var target = $('div.add_part_order');
        if (target.css('display') == 'none') {
            target.css('display', 'block');
        } else {
            target.css('display', 'none');
        }
    })


    $('button.sell_car').click(function () {
        hide_show($('form.sell_car'));
        $('html, body').stop().animate({scrollTop: $('form.sell_car').offset().top}, 500);
    })

    $('button.add_customer').click(function () {
        hide_show($('form.add_customer'));
        $('html, body').stop().animate({scrollTop: $('form.add_custoemr').offset().top}, 500);

    });


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

    $("input[type='checkbox']").change(function () {
        console.log("check box is changed ");
        if ($(this).is(":checked")) {
            $('input.business').each(function () {
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
})


function hide_show(element) {
    if (element.css('display', 'none')) {
        element.css('display', 'block');
    } else {
        element.css('display', 'none');
    }
}

function update_part(vin, order_index, part_num, username, id, status) {
    console.log(`inside update part ${vin}, ${order_index}, ${status}`);
    console.log(status == 'installed');
    // $(".action_" + id).siblings('.editable').attr('contentEditable', true).addClass('form-control');
    $(".action_" + id).siblings('.editable').html(`<select name="status" id="${vin}-${order_index}_${part_num}">
            <option value="" disabled selected>select status</option>
            <option value="installed">Installed</option>
            <option value="received">Received</option>
            <option value="ordered">Ordered</option>
        </select>`);
    var select = $(`select#${vin}-${order_index}_${part_num}`)

    if ($.trim(status) == 'received') {
        $(`select#${vin}-${order_index}_${part_num} option:nth-child(3)`).attr('selected', true);
        $(`select#${vin}-${order_index}_${part_num} option:nth-child(1)`).attr('selected', false);

        $(`select#${vin}-${order_index}_${part_num} option:nth-child(4)`).css('display', 'none');
    }
    if ($.trim(status) == 'installed') {
        $(`select#${vin}-${order_index}_${part_num} option:nth-child(3)`).css('display', 'none');
        $(`select#${vin}-${order_index}_${part_num} option:nth-child(2)`).attr('selected', true);
        $(`select#${vin}-${order_index}_${part_num} option:nth-child(1)`).attr('selected', false);

        $(`select#${vin}-${order_index}_${part_num} option:nth-child(4)`).css('display', 'none');


    }
    $(".action_" + id).children().last().css('display', 'inline-block');
    $(".action_" + id).children().first().replaceWith(`<span class="glyphicon glyphicon-floppy-disk text-success" onclick="save('${vin}', '${order_index}','${part_num}', '${username}', '${id}', '${status}')"></span>`)
}

function save(vin, order_index, part_num, username, id, status) {
    // $(".action_" + id).siblings(".editable").attr('contentEditable', false).removeClass('form-control');
    // $(".action_" + id).siblings(".editable").html(status);
    console.log(`inside save part ${vin}, ${order_index}`)

    $(".action_" + id).children().first().replaceWith(`<span class="glyphicon glyphicon-pencil text-success" onclick="update_part('${vin}', '${order_index}', '${part_num}', '${username}', '${id}', '${status}')"></span>`)
    var new_status = $(".action_" + id).prev().children('select').val();
    console.log(new_status);
    console.log(`/part_status/update/vin=${vin}/order_index=${order_index}`);
    $.post(`/part_status/update/vin=${vin}/order_index=${order_index}`, {
        new_status: new_status,
        vin: vin,
        order_index: order_index,
        part_num: part_num
    }, function () {
        alert("Part status is updated");
        window.location.replace(`/vehicle_details/user=${username}/vin=${vin}`);
    })
}

function cancel(vin, order_index, part_num, username, id, status) {
    console.log(`inside cancle ${status}`);
    $(".action_" + id).siblings(".editable").html(status);
    $(".action_" + id).children().last().css('display', 'none');

    $(".action_" + id).children().first().replaceWith(`<span class="glyphicon glyphicon-pencil text-success" onclick="update_part('${vin}', '${order_index}', '${part_num}', '${username}', '${id}', '${status}')"></span>`)
}