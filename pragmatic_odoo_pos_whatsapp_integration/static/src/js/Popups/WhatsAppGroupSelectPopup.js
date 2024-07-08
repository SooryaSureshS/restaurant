odoo.define('pragmatic_odoo_pos_whatsapp_integration.WhatsAppGroupSelectPopup', function(require) {
    'use strict';

    const { useState, useRef } = owl.hooks;
    const { useListener } = require('web.custom_hooks');
    const AbstractAwaitablePopup = require('point_of_sale.AbstractAwaitablePopup');
    const Registries = require('point_of_sale.Registries');

    class WhatsAppGroupSelectPopup extends AbstractAwaitablePopup {
        constructor() {
            super(...arguments);
            useListener('keyup-Search', this._chatListSearch);
            this.state = useState({ selectedItems: this.props.list.filter((item) => item.isSelected) });
            this.searchInput = useRef("searchInput")
        }
        _chatListSearch(event) {
            var filter = $(this.searchInput.el).val().toUpperCase();
            var $items = $(this.el).find(".selection-item");
            for (var i = 0; i < $items.length; i++) {
                var txtValue = $items[i].textContent || $items[i].innerText;
                if (txtValue.toUpperCase().indexOf(filter) > -1) {
                    $items[i].style.display = "flex";
                } else {
                    $items[i].style.display = "none";
                }
            }
        }
        selectToggleItem(item) {
            let selectedItem = this.state.selectedItems.find((selectedItem) => selectedItem.id == item.id);
            if(selectedItem != undefined){
                let index = this.state.selectedItems.indexOf(selectedItem);
                if(index != -1){
                    selectedItem.isSelected = false;
                    let item = this.state.selectedItems.splice(index, 1);
                }
            }else{
                item.isSelected = true;
                this.state.selectedItems.push(item);
            }
        }
        getPayload() {
            const chatIds = this.state.selectedItems.map((item) => item.id);
            return chatIds;
        }

    }
    WhatsAppGroupSelectPopup.template = 'WhatsAppGroupSelectPopup';
    WhatsAppGroupSelectPopup.defaultProps = {
        confirmText: 'Send',
        cancelText: 'Cancel',
        title: 'Group Send Message',
        body: 'Send a message to multiple contacts/groups!',
        list: []
    };

    Registries.Component.add(WhatsAppGroupSelectPopup);

    return WhatsAppGroupSelectPopup;
});