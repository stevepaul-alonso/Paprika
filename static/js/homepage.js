	$(document).ready(function(){
		$('.search_input').focus();
		var pages = ["All", "American","Arab", "Chinese", "French", "Greek", "Indian",  "Italian", "Pakistani", "South Indian", "Sri Lankan"];
        /*-------------------------------------------- Variables ------------------------------------------------------ */
		var last_item_id = 0
		var last_product = 'none'
		var price_filter = 0
		var category_filter = 'Any'
		var brand_filter = 'any'
		var rating_filter = 'any'

		/* -------------------------------------------- Add Pages ------------------------------------------------------ */
        for (i=0; i<pages.length; i++){
            html = '<div class="option"><p class="center_vertical">' + pages[i] + '</p></div>'
            $('.options').append(html);          
        }
        
        /* ------------------------------ Show category dropdown on click --------------------------------------------- */
        $('.category_dropdown').click(function(){
        	if($(".options").css("display") == "none"){
        		$(".options").css("display", "block");
        	}
        	else{
        		$(".options").css("display", "none");
        	}
        });

        /* ----------------------- Updates selected category as current category -------------------------------------- */
        $('.option').click(function(e){
        	var opt = $(e.currentTarget).children('p').text();
        	$("#current_category").text(opt);
        	$(".options").css("display", "none");
        });

        /* -------------------- Function to fetch and display items when filter options are clicked -------------------- */
        var get_items_filter = function(){
        	category_filter = $('#current_category').text();
        	rating_filter = $('input[name=rating]:checked').val();
        	brand_filter = $('input[name=brand]:checked').val();
        	price_filter =$('input[name=price]:checked').val();
        	console.log("fetching");
        	$.ajax({
        		url: '/fetch_data',
        		method: 'POST',
        		data:{'last_product':last_product,'category': category_filter, 'rating': rating_filter, 'brand': brand_filter, 'price': price_filter}
        	}).done(function(data){
        		$('.welcome_box').css('display', 'none');
        		$('.filter_box').css('display', 'block');
        		$('.items').css('display', 'block');
        		$('.items').html('');
        		if (data.length == 0){
        			$('#no_result').css('display', 'block');
        		}
        		else{
        			$('#no_result').css('display', 'none');
        		}
        		for(var i=0;i<data.length;i++){
        			console.log(data[i]['rating'])
        			var html = '<div class="item"><div class="hidden item_no">'+data[i]['cuisine_id']+'</div><div class="item_img"><img class="center" src=https://s3.us-east-2.amazonaws.com/paprikasteve/'+data[i]['photos'][0]+'.jpg ></div><div class="item_info"><div class="item_name"><p class="center_vertical">'+ data[i]['name']+'</p></div><div class="item_brand"><p>By '+ data[i]['restaurant']+'</p></div><div class="item_rating"><p class="star">'
        			if (data[i]['rating'] == 1){html += '★'}
        			else if (data[i]['rating'] == 2){html += '★★'}
        			else if (data[i]['rating'] == 3){html += '★★★'}
        			else if (data[i]['rating'] == 4){html += '★★★★'}
        			else{html += '★★★★★'}

        			html +='</p></div><div class="item_price"><p>$'+ data[i]['price'] +'</p></div></div><div class="cart_button"> Add to cart </div></div>'

        			$('.items').append(html);
        		}
        		add_to_cart_func();
        		show_product();
        	});
        }

        /* -------------------- Function to fetch and display items when an input is given for search ---------------- */
        var get_items_main = function(){
        	category_filter = $('#current_category').text();
        	rating_filter = 'any';
        	brand_filter = 'any';
        	price_filter ='any';
        	$.ajax({
        		url: '/fetch_data',
        		method: 'POST',
        		data:{'last_product':last_product, 'category': category_filter, 'rating': rating_filter, 'brand': brand_filter, 'price': price_filter}
        	}).done(function(data){
        		$('.welcome_box').css('display', 'none');
        		$('.filter_box').css('display', 'block');
        		$('.items').css('display', 'block');
        		$('.items').html('');
        		if (data.length == 0){
        			$('#no_result').css('display', 'block');
        		}
        		else{
        			$('#no_result').css('display', 'none');
        		}
        		for(var i=0;i<data.length;i++){
        			var html = '<div class="item"><div class="hidden item_no">'+data[i]['cuisine_id']+'</div><div class="item_img"><img class="center" src=https://s3.us-east-2.amazonaws.com/paprikasteve/'+data[i]['photos'][0]+'.jpg ></div><div class="item_info"><div class="item_name"><p class="center_vertical">'+ data[i]['name']+'</p></div><div class="item_brand"><p>By '+ data[i]['restaurant']+'</p></div><div class="item_rating"><p class="star">'
        			if (data[i]['rating'] == 1){html += '★'}
        			else if (data[i]['rating'] == 2){html += '★★'}
        			else if (data[i]['rating'] == 3){html += '★★★'}
        			else if (data[i]['rating'] == 4){html += '★★★★'}
        			else{html += '★★★★★'}

        			html += '</p></div><div class="item_price"><p>$'+ data[i]['price'] +'</p></div></div><div class="cart_button"> Add to cart </div></div>'

        			$('.items').append(html);
        		}
        		add_to_cart_func();
        		show_product();
        		$(".base").prop("checked", true);
        	});

            /* -------------------- Updates available brands based on search input and filters ---------------- */
            $.ajax({
        		url: '/fetch_brands',
        		method: 'POST',
        		data: {'category': category_filter}
        	}).done(function(data){
        		$('.brand_box').html('<input  type="radio" name="brand" class="base" value="any" checked><p class="radio_text">Any</p><br>');
        		for (i=0; i<data.length; i++){
		            html = '<input  type="radio" name="brand" value="'+data[i]+'" ><p class="radio_text">'+data[i]+'</p><br>'
		            $('.brand_box').append(html);          
		        }
		        $('input[type=radio]').change(function() {console.log("clicked");get_items_filter();});
        	});
        }


        /* -------------------------- Calls get_items_main function when search button is clicked ----------------- */
        
        $('.search_img').click(function(){
        	last_product = $('.search_input').val();
        	$('.search_input').val('');   	
        	get_items_main();
        });

        /* ----------------------- Calls get_items_main function when search input is given ------------------------ */
        $('.search_input').keydown(function(e){
        	if (e.which == 13){
        		last_product = $('.search_input').val();
        		if (last_product.length == 0){
        			last_product = 'none';
        		}
        		get_items_main();
        		$('.search_input').val('');
        	}
        	else if(e.which == 27){
        		$('.search_input').val('');
        	}
        });

        /* ----------------------- Calls get_items_filter function when any filter is updated ---------------------- */
        $('input[type=radio]').change(function() {
        	console.log("clicked");
        	get_items_filter();
        });

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

        /* ---------------------------- Hide signup popup when cancel is clicked ------------------------------------ */
        $('#sign_can').click(function(){
        	$('#signup').css('display', 'none');
        });

        /* ---------------------------------------- Adds selected item to cart on click ----------------------------- */
        var add_to_cart_func = function(){
        	$('.cart_button').click(function(e){
        		e.stopImmediatePropagation();
	        	console.log("clicked");
	        	product_id = $(e.currentTarget).siblings('.item_no').text();
	        	total_amount = $(e.currentTarget).siblings('.item_info').children('.item_price').children('p').text();
	        	$.ajax({
	        		url:'/add_to_cart',
	        		method: 'POST',
	        		data: {'product_id': product_id, 'total_amount': total_amount}
	        	}).done(function(data){
	        		$('.message').text(data);
	        		$('.message').css('display', 'block');
	        		setTimeout(function(){ $('.message').css('display', 'none'); }, 3000);
	        		if(data == 'Successfully added to cart'){
	        			var cart_count = parseInt($('.cart_dot').text()) + 1;
	        			$('.cart_dot').text(cart_count);
	        		}
	        	})
	        });
        }

        /* ---------------------------------------- Redirects to products page  ----------------------------------- */
        var show_product = function(){
        	$('.item').click(function(e){
	        	id = $(e.currentTarget).children('.item_no').text();
	        	url = '/product/'+id;
	        	window.location.href = url;
	        });
        }
	});