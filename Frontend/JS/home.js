/* MAJORITY OF THIS JS HAS BEEN GENERATED WITH CHAT GPT */

// Example: Update balance dynamically
let balance = 100.00; // Initial balance

function updateBalance(newAmount) {
    balance = newAmount;
    document.getElementById("balance-value").innerText = balance;
}

function toggleMenu() {
    alert("Menu button clicked!"); // Replace with actual menu functionality
}

// Example usage: updateBalance(150);

document.addEventListener("DOMContentLoaded", function () {
    // Get all bet buttons
    const betButtons = document.querySelectorAll(".bet button");
    const cart = [];
    
    // Create modal elements
    const modal = document.createElement("div");
    modal.id = "bet-modal";
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>Bet Cart</h2>
            <ul id="bet-list"></ul>
            <button id="clear-bets">Clear Bets</button>
        </div>
    `;
    document.body.appendChild(modal);

    const betList = document.getElementById("bet-list");
    const closeModal = modal.querySelector(".close");
    const clearBets = modal.querySelector("#clear-bets");

    // Function to update modal content
    function updateCart() {
        betList.innerHTML = "";
        cart.forEach((bet, index) => {
            console.log(bet);
            const li = document.createElement("li");
            li.textContent = `${bet.typeOfBet} - ${bet.player} - ${bet.type}`;
            betList.appendChild(li);
        });
    }

    // Event listener for bet buttons
    betButtons.forEach(button => {
        button.addEventListener("click", function () {
            const betType = this.textContent;
            const player = this.closest(".bet").querySelector("p").textContent;
            const betDetails = this.closest(".bet").querySelector(".bet-info").querySelectorAll("p")[1].textContent;
            const bet_details_split = betDetails.split(" ");



            // Add to cart
            cart.push({ player, type: betType, typeOfBet: bet_details_split[1],  betValue: bet_details_split[0]});
            updateCart();
            modal.style.display = "block"; // Show modal
        });
    });

    // Close modal
    closeModal.addEventListener("click", function () {
        modal.style.display = "none";
    });

    // Clear bets
    clearBets.addEventListener("click", function () {
        cart.length = 0;
        updateCart();
    });

    // Close modal if clicking outside content
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});
