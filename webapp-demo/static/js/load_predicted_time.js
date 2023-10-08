$( document ).ready(function() {
    var apiURL = 'http://localhost:81/predict'
    function predict_delivery_time(currentDateTime) {
        /*
              distance: 555.0998000000001,
              dow_created_time: 2,
              hour_created_time: 14,
              suggested_deli_supplier: 1.0,
              destination_address_type: 1.0,
              destination_district: 289.0,
              seller_id: 11017,
              suggested_pickup_supplier: 1.0,
              departure_region: 59.0,
              route: 4.0,
              datetime_created_at: "2023-07-26T14:15:37"
         */
        var distance = $("#hidden_distance").val();
        var dow_created_time = $("#hidden_dow_created_time").val();
        var hour_created_time = $("#hidden_hour_created_time").val();
        var suggested_deli_supplier = $("#suggested_deli_supplier").val();
        var destination_address_type = $("#hidden_destination_address_type").val();
        var destination_district = $("#hidden_destination_district").val();
        var seller_id = $("#seller_id").val();
        var suggested_pickup_supplier = $("#suggested_deli_supplier").val();
        var departure_region = $("#hidden_departure_region").val();
        var route = $("#hidden_route").val();
        var datetime_created_at = currentDateTime;

        var inputParams = {
            distance,
            dow_created_time,
            hour_created_time,
            suggested_deli_supplier,
            destination_address_type,
            destination_district,
            seller_id,
            suggested_pickup_supplier,
            departure_region,
            route,
            datetime_created_at
        };

        console.log(inputParams);

        fetch(apiURL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(inputParams)
        })
        .then(resp => resp.json()) // or, resp.text(), etc
        .then(data => {
            var date = new Date(data.predicted_shipping_date);
            date.toISOString().substring(0, 10);
            //var dateString= date.toLocaleString().substring(0,10);
            // var dateString= date.toLocaleString();
            var dateString= date.toLocaleDateString("vi-VN");
            $('#predicted_time').html(dateString);
        })
        .catch(error => {
            console.error(error);
        });
    }

    $("#doPredictButton" ).on( "click", function() {
        curDateTime = new Date();
        currentDateTime = curDateTime.toISOString().split('.')[0];

        predict_delivery_time(currentDateTime);
    } );

    $('#seller_id').on('change', function() {
        // alert($(this).val());
    })
});