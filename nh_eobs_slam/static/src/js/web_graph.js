openerp.nh_eobs_slam = function (instance) {
    'use strict';

    var QWeb = openerp.web.qweb;

    instance.web_graph.Graph.include({
        header_cell_clicked: function (event) {
            event.preventDefault();
            event.stopPropagation();
            var id = event.target.getAttribute('data-id'),
                header = this.pivot.get_header(id),
                self = this;

            if (header.expanded) {
                if (header.root === this.pivot.rows) {
                    this.fold_row(header, event);
                } else {
                    this.fold_col(header);
                }
                return;
            }
            if (header.path.length < header.root.groupby.length) {
                this.$row_clicked = $(event.target).closest('tr');
                this.expand(id);
                return;
            }
            if (!this.groupby_fields.length) {
                return;
            }

            var fields = _.map(this.groupby_fields, function (field) {
                return {id: field.field, value: field.string, type: self.fields[field.field.split(':')[0]].type};
            });

            if (this.dropdown) {
                this.dropdown.remove();
            }

            var all_fields = fields;
            _.each(header.root.groupby, function (group) {
                for (var i = 0; i < all_fields.length; i++) {
                    if (all_fields[i].id === group.field) {
                        fields.splice(i, 1)
                    }
                }
            });

            this.dropdown = $(QWeb.render('field_selection', {fields: fields, header_id: id}));
            $(event.target).after(this.dropdown);
            this.dropdown.css({
                position: 'absolute',
                left: event.originalEvent.layerX,
            });
            this.$('.field-selection').next('.dropdown-menu').first().toggle();
        }

    })
};