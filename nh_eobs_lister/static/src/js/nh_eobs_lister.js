openerp.nh_eobs_lister = function (instance) {
    var QWeb = instance.web.qweb;

    instance.nh_eobs_lister.PBPWidget = instance.web.list.Column.extend({
        _format: function (row_data, options) {
            if (row_data.pbp_flag.value == true){
                return QWeb.render('lister_updown', {
                    'widget': this,
                    'prefix': instance.session.prefix,
                });
            } else {
                return '';
            };
        },
    });

    instance.web.list.columns.add('field.lister_pbp', 'instance.nh_eobs_lister.PBPWidget');

    instance.nh_eobs_lister.KanbanView = instance.web_kanban.KanbanView.extend({

        on_groups_started: function() {
            var self = this;
            if (this.group_by == 'proximity_interval') {
                var cols = this.$el.find('td.oe_kanban_column');
                var heads = this.$el.find('td.oe_kanban_group_header');
                var titles = this.$el.find('span.oe_kanban_group_title_vertical');
                var cards = this.$el.find('div.oe_kanban_card');
                console.log($(cards));
                class_map = {
                    "45+ minutes": '50',
                    "30-45 minutes": '45',
                    "15-30 minutes": '30',
                    "5-15 minutes": '15',
                    "0-5 minutes": '5'
                }
                for (i = 0; i < heads.length; i++) {
                    column_string = $(titles[i]).text().trim();
                    console.log(column_string);
                    col_class = 'nh_high_risk_patients_kanban_column_proximity_interval_' + class_map[column_string];
                    $(heads[i]).addClass(col_class);
                    $(cols[i]).addClass(col_class);
                }
                for (i = 0; i < cards.length; i++) {
                    $(cards[i]).addClass("nh_high_risk_kanban_card_proximity_interval");
                }
            }
            if (this.group_by == 'clinical_risk') {
                var cols = this.$el.find('td.oe_kanban_column');
                var heads = this.$el.find('td.oe_kanban_group_header');
                var titles = this.$el.find('span.oe_kanban_group_title_vertical');
                var cards = this.$el.find('div.oe_kanban_card');
                console.log($(cards));
                class_map = {
                    "No Score Yet": "none",
                    "High Risk": "high",
                    "Medium Risk": "medium",
                    "Low Risk": "low",
                    "No Risk": "no"
                };
                for (i = 0; i < heads.length; i++) {
                    column_string = $(titles[i]).text().trim();
                    console.log(column_string);
                    col_class = 'nhclinical_kanban_column_clinical_risk_' + class_map[column_string];
                    $(heads[i]).addClass(col_class);
                    $(cols[i]).addClass(col_class);
                }
                for (i = 0; i < cards.length; i++) {
                    $(cards[i]).addClass("nhclinical_kanban_card_clinical_risk");
                }
            }
            this._super();
            if (this.options.action.name == "Kiosk Board" || this.options.action.name == "Kiosk Workload NEWS" || this.options.action.name == "Kiosk Workload Other Tasks"){
                $(".oe_leftbar").attr("style", "");
                $(".oe_leftbar").addClass("nh_eobs_hide");
                $(".oe_searchview").hide();
                kiosk_mode = true;
                if (typeof(kiosk_t) != 'undefined'){
                    clearInterval(kiosk_t);
                }
                kiosk_t = window.setInterval(function(){
                    if (typeof(kiosk_button) == 'undefined'){
                        kiosk_button =  $('li:contains(Kiosk Workload NEWS) .oe_menu_leaf');
                    } else if (kiosk_button.text().indexOf('Kiosk Patients Board') > 0){
                        kiosk_button =  $('li:contains(Kiosk Workload NEWS) .oe_menu_leaf');
                    } else if (kiosk_button.text().indexOf('Kiosk Workload NEWS') > 0){
                        kiosk_button =  $('li:contains(Kiosk Workload Other Tasks) .oe_menu_leaf');
                    } else {
                        kiosk_button =  $('li:contains(Kiosk Patients Board) .oe_menu_leaf');
                    }
                    if (kiosk_mode){
                        kiosk_button.click();
                    }
                }, 15000);
            }
            else if (this.options.action.name == "High Risk Patients" || this.options.action.name == "Ward Dashboard"){
                if (typeof(timing) != "undefined"){
                    clearInterval(timing);
                }
                var name = this.options.action.name
                timing = window.setInterval(function(){
                    self.do_reload();
                }, 60000);
            }
            else{
                kiosk_mode = false;
                if (typeof(kiosk_t) != 'undefined'){
                    clearInterval(kiosk_t);
                }
                $(".oe_leftbar").addClass("nh_eobs_show");
                $(".oe_searchview").show();
            }
        }
    });
    instance.web.views.add('kanban', 'instance.nh_eobs_lister.KanbanView');

    instance.nh_eobs_lister.ListView = instance.web.ListView.extend({
        select_record: function (index, view) {
            // called when selecting the row

            view = view || index == null ? 'form' : 'form';
            this.dataset.index = index;
            if (this.fields_view.name != "NH Clinical Placement Tree View"){
                _.delay(_.bind(function () {
                    this.do_switch_view(view);
                }, this));
            }
        },

        do_button_action: function (name, id, callback) {
            // called when pressing a button on row
            this.handle_button(name, id, callback);
            if (name == "switch_active_status"){
                refresh_active_poc = true;
            }
        },

        load_list: function(data) {
            this._super(data);
            if (this.model == 'nh.clinical.patient.observation.pbp'){
                this.$el.html(QWeb.render('ListViewPBP', this));
            }
        }

    });

    instance.web.views.add('list', 'instance.nh_eobs_lister.ListView');

};