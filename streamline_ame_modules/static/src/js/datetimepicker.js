openerp.streamline_ame_modules = function(instance) {
	instance.web.DateTimeWidget.include({
		picker: function() {
			if (typeof arguments[0] !== 'string'){
				arguments[0]["showButtonPanel"] = false;
			}
	        return $.fn[this.jqueryui_object].apply(this.$input_picker, arguments);
	    },
    });	
}
