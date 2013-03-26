function formsubmit(evt) {
	$("#" + this.id + " iframe").show();
}

function init() {
	$(".results").hide();
	$("form").submit(formsubmit);
}

$(init);
