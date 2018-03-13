openerp.nh_clinical = function(instance, local) {

    local.FormTreeSelectedWidget = instance.web.form.FieldBoolean.extend({
        start: function() {
            // TODO: Fix this widget so that it actually runs when it's used
            // i.e on the 'selected' field on the nh allocation wizard.
            // I'm not entirely sure how to declare a field widget so may need to look at other extensions
            // where it has been done on Odoo 8.0


            // TODO: Add an onclick handler for each widget which makes an
            // rpc call to `nh.clinical.allocating`.write() to write the value
            // of the 'selected' field for the record whos row the widget is sat on.

            // This means that when we call batch_allocate, the rows which need to be
            // actioned will easily be visible
            this._super();
        },
    });

    instance.web.form.widgets.add('form_tree_selected_widget', 'instance.nh_clinical.FormTreeSelectedWidget');



} 
