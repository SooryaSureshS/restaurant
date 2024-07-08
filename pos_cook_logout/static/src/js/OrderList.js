odoo.define('pos_cook_logout.OrderList', function(require) {
const Chrome = require('point_of_sale.Chrome');
const Registries = require('point_of_sale.Registries');

    const PosCookLogout = (Chrome) =>
    class  extends Chrome {
    async _closePos() {
            // If pos is not properly loaded, we just go back to /web without
        // doing anything in the order data.
        if (!this.env.pos || this.env.pos.db.get_orders().length === 0) {
            window.location = '/web#action=point_of_sale.action_client_pos_menu';
            if (this.env.pos.user.kitchen_screen_user == 'cook'){
                        window.location.href = "/web/session/logout?redirect=/web/login";

            }

        }
        if (this.env.pos.db.get_orders().length) {
            // If there are orders in the db left unsynced, we try to sync.
            // If sync successful, close without asking.
            // Otherwise, ask again saying that some orders are not yet synced.
            try {
                await this.env.pos.push_orders();
                window.location = '/web#action=point_of_sale.action_client_pos_menu';
                if (this.env.pos.user.kitchen_screen_user == 'cook'){
                        window.location.href = "/web/session/logout?redirect=/web/login";

            }
            } catch (error) {
                console.warn(error);
                const reason = this.env.pos.get('failed')
                    ? this.env._t(
                          'Some orders could not be submitted to ' +
                              'the server due to configuration errors. ' +
                              'You can exit the Point of Sale, but do ' +
                              'not close the session before the issue ' +
                              'has been resolved.'
                      )
                    : this.env._t(
                          'Some orders could not be submitted to ' +
                              'the server due to internet connection issues. ' +
                              'You can exit the Point of Sale, but do ' +
                              'not close the session before the issue ' +
                              'has been resolved.'
                      );
                const { confirmed } = await this.showPopup('ConfirmPopup', {
                    title: this.env._t('Offline Orders'),
                    body: reason,
                });
                if (confirmed) {
                    this.state.uiState = 'CLOSING';
                    this.loading.skipButtonIsShown = false;
                    this.setLoadingMessage(this.env._t('Closing ...'));
                    window.location = '/web#action=point_of_sale.action_client_pos_menu';
                    if (this.env.pos.user.kitchen_screen_user == 'cook'){
                        window.location.href = "/web/session/logout?redirect=/web/login";

            }
                }
            }
        }
}

}
Registries.Component.extend(Chrome, PosCookLogout);
return Chrome;
});