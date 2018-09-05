odoo.define('ncf_manager.widgets', function (require) {
    "use strict";


    var form_common = require('web.form_common');
    var core = require('web.core');

    var Copyright = form_common.FormWidget.extend(form_common.ReinitializeWidgetMixin, {
        start: function () {
<<<<<<< HEAD
            // this.$el.append("<a href='https://marcos.do/page/opl?' target='_blank'>&#169; Marcos Organizador de Negocios SRL / Odoo Proprietary License v1.0</a>");
=======
            this.$el.append("<a href='https://marcos.do/page/opl?' target='_blank'>&#169; Marcos Organizador de Negocios SRL / Odoo Proprietary License v1.0</a>");
>>>>>>> 2a2343b54b5cb74b07be221d1377c1942efa3fd6
        }
    });

    core.form_custom_registry.add("opl", Copyright);

});