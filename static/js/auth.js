// =========================================
// AUTH PANEL SWITCH
// =========================================

document.addEventListener(

    "DOMContentLoaded",

    function () {

        // =========================================
        // ELEMENT
        // =========================================

        const container = document.getElementById(
            "login-container"
        );

        const toCashierBtn = document.getElementById(
            "to-cashier"
        );

        const toOwnerBtn = document.getElementById(
            "to-owner"
        );

        // =========================================
        // SAFETY CHECK
        // =========================================

        if (
            !container ||
            !toCashierBtn ||
            !toOwnerBtn
        ) {

            return;
        }

        // =========================================
        // SWITCH TO CASHIER
        // =========================================

        toCashierBtn.addEventListener(

            "click",

            function () {

                container.classList.add(
                    "active"
                );
            }
        );

        // =========================================
        // SWITCH TO OWNER
        // =========================================

        toOwnerBtn.addEventListener(

            "click",

            function () {

                container.classList.remove(
                    "active"
                );
            }
        );
    }
);