odoo.define('website_portal_request.new_request', function (require) {
'use strict';

var ajax = require('web.ajax');
var web_editor_base = require('web_editor.base')
var snippet_animation = require('web_editor.snippets.animation');
var snippet_registry = snippet_animation.registry


snippet_registry.portal_request_create = snippet_animation.Class.extend({
    selector: '#form_request_create',

    start: function() {
        var self = this;
        self.$form_sel_category = self.$target.find('#request_category');
        self.$form_sel_type = self.$target.find('#request_type');
        self.$form_help = self.$target.find('#request_help')
        self.$form_request_text = self.$target.find('#request_text');

        self.load_categories();
        self.bind_events();
        self.load_editor();

    },
    bind_events: function() {
        var self = this;

        self.$form_sel_category.on('change', function(e) {
            var category_id = self.$form_sel_category.val();
            self.on_category_changed(category_id);
        });
        self.$form_sel_type.on('change', function(e) {
            var type_id = self.$form_sel_type.val();
            self.on_type_changed(type_id);
        });
        self.$target.find('.a-submit').on('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            self.create_request();
        });
    },
    load_categories: function() {
        var self = this;
        
        ajax.jsonRpc(
            '/website_portal_request/api/categories', 'call', {}
        ).then(function (data) {
            self.$form_sel_category.html($('<option/>'));
            $.each(data, function (index, category) {
                var option = $('<option/>');
                option.val(category.id);
                option.text(category.display_name);
                self.$form_sel_category.append(option);
            });
        });
    },
    on_category_changed: function(category_id) {
        var self = this;

        self.$form_sel_type.empty();

        if (!category_id) {
            return;
        }

        ajax.jsonRpc(
            '/website_portal_request/api/category/types', 'call',
            {'category_id': category_id}
        ).then(function (data) {
            self.$form_sel_type.html($('<option/>'));
            $.each(data, function (index, type) {
                var option = $('<option/>');
                option.val(type.id);
                option.text(type.name);
                self.$form_sel_type.append(option);
            });
        });
    },
    on_type_changed: function(type_id) {
        var self = this;

        self.$form_help.empty();

        ajax.jsonRpc(
            '/website_portal_request/api/type_info', 'call',
            {'type_id': type_id}
        ).then(function (data) {
            self.$form_help.html(data.help);
        });
    },
    create_request: function() {
        var self = this;

        var type_id = self.$form_sel_type.val();
        var request_text = self.$form_request_text.val();

        self.$form_request_text.val(
            self.$form_request_text.parent().find('.note-editable').code()
        );

        var request_data = {
            type_id: type_id,
            request_text: request_text
        }

        ajax.jsonRpc(
            '/website_portal_request/api/request/new', 'call', request_data
        ).then(function (data) {
            window.location.href = data.url;
        });
    },
    load_editor: function() {
        var self = this;
        // Set up summernote editor
        var $textarea = self.$form_request_text;
        if (!$textarea.val().match(/\S/)) {
            $textarea.val("<p><br/></p>");
        }
        var $form = $textarea.closest('form');
        var toolbar = [
                ['style', ['style']],
                ['font', ['bold', 'italic', 'underline', 'clear']],
                ['para', ['ul', 'ol', 'paragraph']],
                ['table', ['table']],
                ['history', ['undo', 'redo']],
                ['insert', ['picture']],
                ['misc', ['help']]
            ];
        $textarea.summernote({
                height: 500,
                toolbar: toolbar,
                styleWithSpan: false,
                onImageUpload: function(images) {
                    $.each(images, function(index, image) {
                        ajax.post('/website_portal_request/image_upload', {
                            'upload': image
                            //'mime_type': image.type,
                        }).done(function (data) {
                            data = JSON.parse(data)
                            if (data['status'] == 'OK') {
                                var image = $('<img>').attr('src', data['attachment_url']);
                                $textarea.summernote('insertNode', image[0]);
                            } else {
                                alert ("Smthing gone wrong during image upload\n" + data['message']);
                            }
                        });
                    });
                }
        });

        //$form.on('click', 'button, .a-submit', function () {
        //});
    }
});

});

