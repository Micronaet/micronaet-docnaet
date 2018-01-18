//  @@@ web_field_style custom JS @@@

openerp.web_field_style = function(openerp) {

    openerp.web.form.Field.include({

        default_style: 'width:100%;',

        init: function(view, node) {
            this._super(view, node);
            this.setup_styles(view, node);
        },

        setup_styles : function(view, node){
            // style
            // this is done for allowing ppl to set up different colors per field
            // without having to deal with css
            var style = this.default_style;
            if(node.attrs.bgcolor){
                style += 'background-color:' + node.attrs.bgcolor + ' !important;';
            }
            if(node.attrs.fgcolor){
                style += 'color:' + node.attrs.fgcolor + ' !important;';
            }
            this.input_style = style;
            // css class
            var cssclass = 'field_' + this.type;
            cssclass += _(['integer', 'float', 'float_time']).contains(this.type) ? ' oe-number' : '';
            if(node.attrs.cssclass){
                cssclass += ' ' + node.attrs.cssclass;
            }
            this.input_cssclass = cssclass;
        }
    });


    // openerp.web.form.FieldChar = openerp.web.form.FieldChar.extend({
    //     default_style: 'width:100%;',

    // });

}
