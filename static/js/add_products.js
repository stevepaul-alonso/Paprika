	var img = []
	$(document).ready(function(){
		/* -------------------------------------- Reads and displays the uploaded image ------------------------------ */
		function readURL(input, label) {
	        if (input.files && input.files[0]) {
	            var reader = new FileReader();

	            reader.onload = function (e) {
	                label.children('.add_image').html('<img class="center added_img" src="' + e.target.result + '">');
	                label.children('.add_image').css('border', '0px solid #fff');
	            };
	            reader.readAsDataURL(input.files[0]);
	        }
	    }
	    /*------------------------------------- Calls readURL function if an image is uploaded ----------------------- */
		$('.uploaded_img').change(function(e){
			var label = $('#'+$(e.currentTarget).attr('id') + '_label');
			img.push($(e.currentTarget).attr('id').split('image')[1]);
			readURL(this, label);
		});


		/*------------------------------------- Sends added information about product to the server  ------------------ */
		var info_uploader = function(){
			$("#name_base").val($('#name').val());
			info = {
				'name': $('#name').val(),
				'category': $('#category').val(),
				'brand': $('#brand').val(),
				'price': $('#price').val(),
				'quantity': $('#quantity').val(),
				'description': $('#description').val(),
				'photos': JSON.stringify(img)
			}
			$.ajax({
				url: '/add_product_info',
				method: 'POST',
				data:info
			}).done(function(data){
				if(data == "success"){
					$("#upload_form").submit();
				}
				else{
					$('#submit').click(function(){$('#submit').off('click');info_uploader()});
				}
			})
		}

		/*------------------------------------- Calls info_uploader function when submit button is clicked  ------------ */
		$('#submit').click(function(){
			$('#submit').off('click');
			info_uploader();
		});
	});