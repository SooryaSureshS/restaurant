/**
 * odoo.define function that initializes the custom selection field behavior
 *
 * @param {Object} require - An object representing the required modules for the current module
 * @returns {undefined} - Returns nothing
 */
odoo.define('gio_obstgemuese_theme.custom_selection_field', function (require) {
    "use strict";
    var ajax = require("web.ajax");
    /**
     * Event listener for the 'ready' event of the document object.
     * This function sets the hover behavior for the select elements.
     *
     * @param {Event} e - The event object
     * @returns {undefined} - Returns nothing
     */
    $(document).ready(function (e) {

        setSelectHover();
        /**
         * Function that sets the hover behavior for the select elements
         *
         * @param {String} selector - The selector for the select elements (default: 'select')
         * @returns {undefined} - Returns nothing
         */
        function setSelectHover(selector = "select") {
            let selects = document.querySelectorAll(selector);
            selects.forEach((select) => {
                let selectWrap = select.parentNode.closest(".select-wrap");
                if (!selectWrap) {
                    selectWrap = document.createElement("div");
                    selectWrap.classList.add("select-wrap");
                    select.parentNode.insertBefore(selectWrap, select);
                    selectWrap.appendChild(select);
                }
                let size = select.querySelectorAll("option").length;
                const getSelectHeight = () => {
                    selectWrap.style.height = "auto";
                    let selectHeight = select.getBoundingClientRect();
                    selectWrap.style.height = selectHeight.height + "px";
                };
                getSelectHeight(select);
                window.addEventListener("resize", (e) => {
                    getSelectHeight(select);
                });
                let hasFocus = false;
                select.addEventListener("focus", (e) => {
                    select.setAttribute("size", size);
                    setTimeout(() => {
                        hasFocus = true;
                    }, 150);
                });
                select.addEventListener("click", (e) => {
                    if (hasFocus) {
                        select.blur();
                        hasFocus = false;
                    }
                });
                select.addEventListener("keydown", (e) => {
                    if (e.key === "Enter") {
                        select.removeAttribute("size");
                        select.blur();
                    }
                });
                select.addEventListener("blur", (e) => {
                    select.removeAttribute("size");
                    hasFocus = false;
                });
            });
        }
    });
});
