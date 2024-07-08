odoo.define('theme_wineshop.bizcommon_editor_js', function(require) {
    'use strict';
    var options = require('web_editor.snippets.options');
    var ajax = require('web.ajax');
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    ajax.loadXML('/theme_wineshop/static/src/xml/bizople_theme_common.xml', qweb);

    options.registry.oe_cat_slider = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".oe_cat_slider").empty();
            if (!editMode) {
                self.$el.find(".oe_cat_slider").on("click", _.bind(self.cat_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.cat_slider()) {
                this.cat_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.oe_cat_slider').empty();
        },

        cat_slider: function(type, value) {
            var self = this;
            
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_dynamic_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $category_slider_delete = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#cat_sub_data");
                ajax.jsonRpc('/theme_wineshop/category_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-cat-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_delete.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });

    
    options.registry.second_cat_slider = options.Class.extend({
        start: function(editMode) {
            var self = this;

            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".second_cat_slider").empty();
            if (!editMode) {
                self.$el.find(".second_cat_slider").on("click", _.bind(self.cat_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.cat_slider()) {
                this.cat_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.second_cat_slider').empty();
        },

        cat_slider: function(type, value) {
            var self = this;
            
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_dynamic_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $category_slider_delete = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#cat_sub_data");
                ajax.jsonRpc('/theme_wineshop/category_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-cat-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_delete.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.bizople_theme_common_product_slider = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".biz_dynamic_product_slider").empty();
            if (!editMode) {
                self.$el.find(".biz_dynamic_product_slider").on("click", _.bind(self.prod_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.prod_slider()) {
                this.prod_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.biz_dynamic_product_slider').empty();
        },

        prod_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_dynamic_product_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $product_slider_cancel = self.$modal.find("#cancel"),
                    $pro_sub_data = self.$modal.find("#prod_sub_data");

                ajax.jsonRpc('/theme_wineshop/product_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-prod-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Product Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $product_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                });
            } else {
                return;
            }
        },
    });
    options.registry.s_bizople_theme_multi_product_tab_snippet = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.avi_multi_tab_product_slider .owl-carousel').empty();
            if (!editMode) {
                self.$el.find(".avi_multi_tab_product_slider").on("click", _.bind(self.avi_multi_prod_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.avi_multi_prod_slider()) {
                this.avi_multi_prod_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.avi_multi_tab_product_slider .owl-carousel').empty();
        },

        avi_multi_prod_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.multi_product_custom_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $cancel = self.$modal.find("#cancel"),
                    $snippnet_submit = self.$modal.find("#snippnet_submit");

                ajax.jsonRpc('/theme_wineshop/product_multi_get_options', 'call', {}).then(function(res) {
                    $("select[id='slider_filter'] option").remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter']").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $snippnet_submit.on('click', function() {
                    // var type = '';
                    self.$target.attr('data-multi-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-multi-cat-slider-id', 'multi-cat-myowl' + $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        var type = '';
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        var type = '';
                        type = _t("Multi Product Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="row our-categories">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });
    options.registry.avit_multi_cat_custom_snippet = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find('.avit_avi_multi_prod_slider .owl-carousel').empty();
            if (!editMode) {
                self.$el.find(".avit_avi_multi_prod_slider").on("click", _.bind(self.avi_multi_prod_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.avi_multi_prod_slider()) {
                this.avi_multi_prod_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.avit_avi_multi_prod_slider .owl-carousel').empty();
        },

        avi_multi_prod_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.multi_product_custom_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $cancel = self.$modal.find("#cancel"),
                    $snippnet_submit = self.$modal.find("#snippnet_submit");

                ajax.jsonRpc('/theme_wineshop/product_multi_get_options', 'call', {}).then(function(res) {
                    $("select[id='slider_filter'] option").remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter']").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $snippnet_submit.on('click', function() {
                    // var type = '';
                    self.$target.attr('data-multi-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-multi-cat-slider-id', 'multi-cat-myowl' + $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        var type = '';
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        var type = '';
                        type = _t("Multi Product Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="row our-categories">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });
    options.registry.prod_brands = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".oe_brand_slider .owl-carousel").empty();

            if (!editMode) {
                self.$el.find(".oe_brand_slider").on("click", _.bind(self.bizcommon_brand_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.bizcommon_brand_slider()) {
                this.bizcommon_brand_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.oe_brand_slider .owl-carousel').empty();
        },

        bizcommon_brand_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.brands_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $product_count = self.$modal.find("#brand-count"),
                    $product_label = self.$modal.find("#product-label"),
                    $cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#brand_sub_data");
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr("data-product-count", $product_count.val());
                    self.$target.attr('data-product-label', $product_label.val());

                    if ($product_label.val()) {
                        type = $product_label.val();
                    } else {
                        type = _t("Our Brands");
                    }

                    self.$target.empty().append('<div class="container">\
                                                    <div class="row our-brands">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });
    // box Brand 
    options.registry.brands_box_slider_4 = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("hidden");
            this.$target.find(".box_brand_slider .owl-carousel").empty();

            if (!editMode) {
                self.$el.find(".box_brand_slider").on("click", _.bind(self.box_brand_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.box_brand_slider()) {
                this.box_brand_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.box_brand_slider .owl-carousel').empty();
        },

        box_brand_slider: function(type, value) {
            var self = this;
           
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.brands_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $product_count = self.$modal.find("#brand-count"),
                    $product_label = self.$modal.find("#product-label"),
                    $cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#brand_sub_data");

                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr("data-product-count", $product_count.val());
                    self.$target.attr('data-product-label', $product_label.val());

                    if ($product_label.val()) {
                        type = $product_label.val();
                    } else {
                        type = _t("Our Brands");
                    }

                    self.$target.empty().append('<div class="container">\
                                                    <div class="row our-brands">\
                                                        <div class="col-md-12">\
                                                            <div class="title-block">\
                                                                <h4 class="section-title style1">\
                                                                    <span>' + type + '</span>\
                                                                </h4>\
                                                            </div>\
                                                        </div>\
                                                    </div>\
                                                </div>');
                });
            } else {
                return;
            }
        },
    });
    // for brand slider
    options.registry.it_prod_brands = options.Class.extend({

        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            if (!editMode) {
                self.$el.find(".it_brand_slider").on("click", _.bind(self.brand_it_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.brand_it_slider()) {
                this.brand_it_slider().fail(function() {
                    self.getParent()._removeSnippet();

                });
            }
        },
        cleanForSave: function() {
            $('.it_brand_slider .owl-carousel').empty();
        },

        brand_it_slider: function(type, value) {
            if (type != undefined && type.type == "click" || type == undefined) {
                var self = this;
                self.$modal = $(qweb.render("theme_wineshop.brands_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $product_count = self.$modal.find("#brand-count"),
                    $product_label = self.$modal.find("#product-label"),
                    $cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#brand_sub_data");

                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr("data-product-count", $product_count.val());
                    self.$target.attr('data-product-label', $product_label.val());
                    if ($product_label.val()) {
                        type = $product_label.val();
                    } else {
                        type = _t("Our Brands");
                    }
                    self.$target.empty().append(
                        '<div class="container">\
                            <div class="row our-brands">\
                                <div class="col-md-12">\
                                    <h3 class="section-title style1">\
                                        <span>' + type + '</span>\
                                    </h3>\
                                </div>\
                            </div>\
                        </div>');
                });
                $cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },

    });
    options.registry.health_blog_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.health_blog_slider').empty();
            
            if (!editMode) {
                self.$el.find(".health_blog_slider").on("click", _.bind(self.bizople_theme_common_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.bizople_theme_common_blog_slider()) {
                this.bizople_theme_common_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.health_blog_slider').empty();
        },
        bizople_theme_common_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_wineshop/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.bizople_theme_common_blog_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.bizcommon_blog_slider').empty();
           
            if (!editMode) {
                self.$el.find(".bizcommon_blog_slider").on("click", _.bind(self.bizople_theme_common_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.bizople_theme_common_blog_slider()) {
                this.bizople_theme_common_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.bizcommon_blog_slider').empty();
        },
        bizople_theme_common_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_wineshop/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.s_bizople_theme_blog_slider_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_slider_owl').empty();
            
            if (!editMode) {
                self.$el.find(".blog_slider_owl").on("click", _.bind(self.bizople_theme_common_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.bizople_theme_common_blog_slider()) {
                this.bizople_theme_common_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_slider_owl').empty();
        },
        bizople_theme_common_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_wineshop/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.blog_3_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_3_custom').empty();
            
            if (!editMode) {
                self.$el.find(".blog_3_custom").on("click", _.bind(self.bizople_theme_common_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.bizople_theme_common_blog_slider()) {
                this.bizople_theme_common_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_3_custom').empty();
        },
        bizople_theme_common_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_wineshop/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    
    options.registry.blog_4_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_4_custom').empty();
           
            if (!editMode) {
                self.$el.find(".blog_4_custom").on("click", _.bind(self.bizople_theme_common_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.bizople_theme_common_blog_slider()) {
                this.bizople_theme_common_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_4_custom').empty();
        },
        bizople_theme_common_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_wineshop/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.blog_6_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_6_custom').empty();
           
            if (!editMode) {
                self.$el.find(".blog_6_custom").on("click", _.bind(self.bizople_theme_common_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.bizople_theme_common_blog_slider()) {
                this.bizople_theme_common_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_6_custom').empty();
        },
        bizople_theme_common_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_wineshop/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.blog_5_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_5_custom').empty();
            if (!editMode) {
                self.$el.find(".blog_5_custom").on("click", _.bind(self.bizople_theme_common_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.bizople_theme_common_blog_slider()) {
                this.bizople_theme_common_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_5_custom').empty();
        },
        bizople_theme_common_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_wineshop/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.blog_8_custom_snippet = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find('.blog_8_custom').empty();
            if (!editMode) {
                self.$el.find(".blog_8_custom").on("click", _.bind(self.bizople_theme_common_blog_slider, self));
            }
        },
        onBuilt: function() {
            var self = this;
            this._super();
            if (this.bizople_theme_common_blog_slider()) {
                this.bizople_theme_common_blog_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },
        cleanForSave: function() {
            $('.blog_8_custom').empty();
        },
        bizople_theme_common_blog_slider: function(type, value) {
            var self = this;
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_blog_slider_block"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#blog_slider_filter"),
                    $blog_slider_cancel = self.$modal.find("#cancel"),
                    $sub_data = self.$modal.find("#blog_sub_data");

                ajax.jsonRpc('/theme_wineshop/blog_get_options', 'call', {}).then(function(res) {
                    $('#blog_slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='blog_slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });
                $sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-blog-slider-type', $slider_filter.val());
                    self.$target.attr('data-blog-slider-id', 'blog-myowl' + $slider_filter.val());
                    if ($('select#blog_slider_filter').find(":selected").text()) {
                        type = _t($('select#blog_slider_filter').find(":selected").text());
                    } else {
                        type = _t("Blog Post Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $blog_slider_cancel.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.cat_slider_3 = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".cat_slider_3").empty();
            if (!editMode) {
                self.$el.find(".cat_slider_3").on("click", _.bind(self.cat_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.cat_slider()) {
                this.cat_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.cat_slider_3').empty();
        },

        cat_slider: function(type, value) {
            var self = this;
            
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_dynamic_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $category_slider_delete = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#cat_sub_data");
                ajax.jsonRpc('/theme_wineshop/category_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    self.$target.attr('data-cat-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_delete.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
    options.registry.cat_slider_4 = options.Class.extend({
        start: function(editMode) {
            var self = this;
            this._super();
            this.$target.removeClass("o_hidden");
            this.$target.find(".cat_slider_4").empty();
            if (!editMode) {
                self.$el.find(".cat_slider_4").on("click", _.bind(self.cat_slider, self));
            }
        },

        onBuilt: function() {
            var self = this;
            this._super();
            if (this.cat_slider()) {
                this.cat_slider().fail(function() {
                    self.getParent()._removeSnippet();
                });
            }
        },

        cleanForSave: function() {
            $('.cat_slider_4').empty();
        },

        cat_slider: function(type, value) {
            var self = this;
            
            if (type != undefined && type.type == "click" || type == undefined) {
                self.$modal = $(qweb.render("theme_wineshop.bizcommon_dynamic_category_slider"));
                self.$modal.appendTo('body');
                self.$modal.modal();
                var $slider_filter = self.$modal.find("#slider_filter"),
                    $category_slider_delete = self.$modal.find("#cancel"),
                    $pro_cat_sub_data = self.$modal.find("#cat_sub_data");
                ajax.jsonRpc('/theme_wineshop/category_get_options', 'call', {}).then(function(res) {
                    $('#slider_filter option[value!="0"]').remove();
                    _.each(res, function(y) {
                        $("select[id='slider_filter'").append($('<option>', {
                            value: y["id"],
                            text: y["name"]
                        }));
                    });
                });

                $pro_cat_sub_data.on('click', function() {
                    var type = '';
                    // self.$target.attr('data-cat-slider-type', $slider_filter.val());
                    self.$target.attr('data-cat-slider-id', $slider_filter.val());
                    if ($('select#slider_filter').find(":selected").text()) {
                        type = _t($('select#slider_filter').find(":selected").text());
                    } else {
                        type = _t("Category Slider");
                    }
                    self.$target.empty().append('<div class="container">\
                                                    <div class="block-title">\
                                                        <h3 class="filter">' + type + '</h3>\
                                                    </div>\
                                                </div>');
                });
                $category_slider_delete.on('click', function() {
                    self.getParent()._onRemoveClick($.Event("click"))
                })
            } else {
                return;
            }
        },
    });
});