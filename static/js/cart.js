	$(document).ready(function(){
        var del_current_item = "none"
        /*--------------------------------------------------------------------------------------------------------- */
        /*--------------------------------------------   Login Functions ------------------------------------------ */
        /*--------------------------------------------------------------------------------------------------------- */

        /* ------------------------------ Shows login popup box when login button is clicked ---------------------- */
        $('.login').click(function(){
        	$('#login').css('display', 'block');
        });

        /* --------------------------------------- Submit login info to server ------------------------------------ */
        $('#log_sub').click(function(){
        	$.ajax({
        		url: '/login',
        		method: 'POST',
        		data: {'username': $('#log_username').val(), 'password': $('#log_password').val()}
        	}).done(function(data){
        		if (data == 'success'){
        			$('#login').css('display', 'none');
        			location.reload();
        		}
        		else{
        			$('.message').text(data);
        			$('.message').css('display', 'block');
        			setTimeout(function(){ $('.message').css('display', 'none'); }, 3000);
        			$('#login').css('display', 'none');
        		}
        	})
        });

        /* ---------------------------- Hide login popup when cancel is clicked ------------------------------------ */
        $('#log_can').click(function(){
        	$('#login').css('display', 'none');
        });

        /*--------------------------------------------------------------------------------------------------------- */
        /*--------------------------------------------   SignUp Functions ----------------------------------------- */
        /*--------------------------------------------------------------------------------------------------------- */

        /* ------------------------------ Shows signup popup box when signup button is clicked --------------------- */
        $('.signup').click(function(){
        	$('#signup').css('display', 'block');
        });

        /* --------------------------------------- Submit signup info to server ------------------------------------ */
        $('#sign_sub').click(function(){
        	$.ajax({
        		url: '/signup',
        		method: 'POST',
        		data: {'username': $('#sign_username').val(), 'password': $('#sign_password').val()}
        	}).done(function(data){
        		if (data == 'success'){
        			$('#signup').css('display', 'none');
        			location.reload();
        		}
        		else{
        			$('.message').text(data);
        			$('.message').css('display', 'block');
        			setTimeout(function(){ $('.message').css('display', 'none'); }, 3000);
        			$('#signup').css('display', 'none');
        		}
        	})
        });

        /* ---------------------------- Hide signup popup when cancel is clicked ---------------------------------- */
        $('#sign_can').click(function(){
        	$('#signup').css('display', 'none');
        });

        /*--------------------------------------------------------------------------------------------------------- */
        /*---------------------------------------   Delete item Functions ----------------------------------------- */
        /*--------------------------------------------------------------------------------------------------------- */

        /* ------------------------------ Shows delete popup box when delete button is clicked -------------------- */
        $('.delete_item').click(function(e){
            $('.del_box').css('display', 'block');
            del_current_item = $(e.currentTarget).siblings(".item_no").text();
        });
        /* ---------------------------- Hide delete popup when cancel is clicked ---------------------------------- */
        $('#del_can').click(function(){
            $('.del_box').css('display', 'none');
        });
        /* --------------------------------------- Submit delete info to server ------------------------------------ */
        $('#del_sub').click(function(){
            $.ajax({
                url: '/delete_item',
                method: 'POST',
                data: {'item_id': del_current_item}
            }).done(function(){
                location.reload();
            })
        });

        /* ------------------------------ Purchase is completed with a complete purchase message ------------------ */
        $('#complete_purchase').click(function(){
            console.log("clicked");
            $.ajax({
                url:'/complete_purchase'
            }).done(function(data){
                if (data == 'success'){
                    $('.complete_purchase_box').css('display', 'block') 
                    setTimeout(function(){location.reload()}, 2000);
                }
            })
        })

	});