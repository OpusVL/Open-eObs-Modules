openerp.nh_clinical = function (instance) {

    var QWeb = instance.web.qweb;
    var _t = instance.web._t;
    
    // Declare our widget so it can be used on a view
    instance.web.list.columns.add('field.form_tree_selected', 'instance.web.list.FormTreeSelectedColumn');

    instance.web.list.FormTreeSelectedColumn = instance.web.list.Boolean.extend({

        // Extend the format function of the boolean widget to add a click event to the node
        format: function (row_data, options) {
            var self = this;
            var clickableId = "o_web_tree_selected_clickable-" +
                                  row_data.id.value;

            // defer execution of setting the click event until the function has returned
            window.setTimeout(function() {
                $("#" + clickableId).click(function() {
                    if( $('#' + clickableId + ':checkbox:checked').length > 0 ) {
                        // Make the RPC call with the value of true
                        new instance.web.Model("nh.clinical.allocating")
                            .call("write", [row_data.id.value], {'vals': {'selected': true}});
                    } else {
                        // Make the RPC call with the value of false
                        new instance.web.Model("nh.clinical.allocating")
                            .call("write", [row_data.id.value], {'vals': {'selected': false}});
                    }
                });
            }, 0);
            return QWeb.render(
                'FormTreeSelected',
                {widget: self._format(row_data, options), clickableId: clickableId}
            );
        },
    });
};