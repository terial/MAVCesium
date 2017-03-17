window.onresize = function(event) {
	$(".parent").each(function(){
	    var $this = $(this);
	    var $children = $this.children();

	    $children.height($this.height() / $children.length -35);
	});
};

$(".parent").each(function(){
    var $this = $(this);
    var $children = $this.children();

    $children.height($this.height() / $children.length - 35);
});

// this function updates the console for each of the parent groups
function update_console(status_data){
	for (var parent in status_data) {
		out = document.getElementById(parent+'_console')
		for (var child in status_data[parent]['children']) {
			if (status_data[parent]['children'][child]['console']){ // if we need to update the console with an alert...
				// make the alert html
				alert_html = "<div class='alert "+status_data[parent]['children'][child]['level']+"'>"+status_data[parent]['children'][child]['timestamp'].toFixed(2)+" "+child.toUpperCase()+" : "+status_data[parent]['children'][child]['text']+"</div>"
				
				// add it to the console
				if (out.scrollTop >= (out.scrollHeight - out.clientHeight-1)){
					$(alert_html).appendTo(out);
					$(out).animate({scrollTop: $(out).prop("scrollHeight")}, 500);
				} else {
					$(alert_html).appendTo(out);
				}
			}
		}
	}
}

function set_parent_state(status_data){
	for (var parent in status_data) {
		   out = document.getElementById(parent)
		   if (out != null){
			   out.className = 'lg_center '+status_data[parent]['level']
		   } else {
			   console.log('could not find parent element "', parent, '"')
		   }
	}
	
	
}

function set_child_state(status_data){
	for (var parent in status_data) {
		for (var child in status_data[parent]['children']) {		
			out = document.getElementById(child)
			if (out != null){
				out.className = 'sml_center '+status_data[parent]['children'][child]['level']
			} else {
				console.log('could not find child element "', child, '"')
			}
		}
	}
	
}

function update_status_data(status_data){
	set_parent_state(status_data);
	set_child_state(status_data);
	update_console(status_data);
}