Summary
----
This module is supposed to sync same pos session opened by different users at the same time.
It needs to sync the cart of the same table in the same session opened by multi users.

Developers
----
* ABHISHEK S [SIGB]

Implementation
----
* Check whether table is configured in productScreen.js
    If table is configured, add the table used by each user in 'res.users' in 'table_id' field.
    Alert if table already used by another user.
* **Todo when came back to floorscreen, unassign the table for the user**
    Set 'table_id' field null.

* Order Syncing
    * All the users of the same table should end up in the same order(pos.order).
    * For order syncing long-polling of 1000 x timeout is implemented.
    * Long-polling from productScreen.js will update res.users just like above mentioned.
    * Long-polling should sync =>
        * Order lines
            * Add, Remove, Increase, Decrease
        * Discount
        * Customer
        * Order line note
