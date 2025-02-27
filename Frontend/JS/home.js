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

    function updateCart() {
        betList.innerHTML = "";
        cart.forEach((bet, index) => {
            const li = document.createElement("li");
            li.textContent = `${bet.betValue} - ${bet.typeOfBet} - ${bet.player} - ${bet.type}`;

            // Create remove button
            const removeButton = document.createElement("button");
            removeButton.textContent = "Remove";
            removeButton.classList.add("remove-bet");
            removeButton.dataset.index = index; // Store index for removal

            li.appendChild(removeButton);
            betList.appendChild(li);
        });

        // Attach event listeners to remove buttons
        document.querySelectorAll(".remove-bet").forEach(button => {
            button.addEventListener("click", function () {
                const index = this.dataset.index;
                cart.splice(index, 1); // Remove bet at index
                updateCart(); // Update cart UI
            });
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


/* When the user clicks on the button,
toggle between hiding and showing the dropdown content */
function toggleMenu() {
    document.getElementById("myDropdown").classList.toggle("show");
  }
  
  // Close the dropdown menu if the user clicks outside of it
  window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
      var dropdowns = document.getElementsByClassName("dropdown-content");
      var i;
      for (i = 0; i < dropdowns.length; i++) {
        var openDropdown = dropdowns[i];
        if (openDropdown.classList.contains('show')) {
          openDropdown.classList.remove('show');
        }
      }
    }
  }