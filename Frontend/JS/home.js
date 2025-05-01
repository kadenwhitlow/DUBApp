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

function logOut() {
    fetch("/logout", { method: "GET" })
    .then(() => {
        window.location.href = "/";  // Redirect to login page after logout
    })
    .catch(error => console.error("Logout failed:", error));
}

function placeBet() {
    const betSize = parseFloat(document.getElementById("bet-size").value);
    if (isNaN(betSize) || betSize <= 0) {
        alert("Invalid bet size.");
        return;
    }

    // Extract bet details while ignoring the "Remove" button text
    const betList = Array.from(document.querySelectorAll("#bet-list li")).map(li => {
        return li.childNodes[0].textContent.trim(); // Get only the actual bet text
    });

    const userBalance = parseFloat(document.querySelector(".user-balance").textContent.split("$")[1]);

    fetch("/place_bets", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            'user_balance': userBalance,
            'bet-list': betList,
            'bet-size': betSize
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
        } else {
            console.log("Bet placed successfully");
            updateBalance(data.new_balance);
        }
    })
    .catch(error => console.error("Bet placement failed:", error));
}

// -----------------------------------------------------------------------------------------------------

document.addEventListener("DOMContentLoaded", function () {
    // Get only the buttons that actually add a bet to the cart
    const betButtons = document.querySelectorAll(".bet button.add-to-cart");
    const cart = [];
    const betSizeInput = document.getElementById("bet-size"); // Get the input for bet size

    // Create modal elements
    const modal = document.createElement("div");
    modal.id = "bet-modal";
    modal.innerHTML = `
        <div class="modal-content">
            <span class="close">&times;</span>
            <h2>Bet Cart</h2>
            <ul id="bet-list"></ul>
            <div>
                <label for="bet-size">Enter Bet Size: </label>
                <input type="number" id="bet-size" placeholder="Enter amount" />
            </div>
            <button id="clear-bets">Clear Bets</button>
            <button onclick="placeBet()" id="place-bets">Place Bets</button>
            <button onclick="placeParlay()" id="place-parlay">Place Parlay</button>
        </div>
    `;
    document.body.appendChild(modal);

    const betListEl = document.getElementById("bet-list");
    const closeModal = modal.querySelector(".close");
    const clearBets = modal.querySelector("#clear-bets");
    const placeBets = modal.querySelector("#place-bets");
    const placeParlay = modal.querySelector("#place-parlay");

    function updateCart() {
        betListEl.innerHTML = "";
        cart.forEach((bet, index) => {
            const li = document.createElement("li");
            li.textContent = `${bet.betValue} - ${bet.typeOfBet} - ${bet.player} - ${bet.type}`;

            // Create remove button
            const removeButton = document.createElement("button");
            removeButton.textContent = "Remove";
            removeButton.classList.add("remove-bet");
            removeButton.dataset.index = index; // Store index for removal

            li.appendChild(removeButton);
            betListEl.appendChild(li);
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
            cart.push({ player, type: betType, typeOfBet: bet_details_split[1], betValue: bet_details_split[0] });
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

    // Place bets with bet size
    placeBets.addEventListener("click", function () {
        const betSize = parseFloat(betSizeInput.value);

        // Check if the bet size is a valid number and greater than ten cents
        if (isNaN(betSize) || betSize <= 0.09) {
            alert("Please enter a valid bet size.");
            return;
        }

        // Handle placing the bet (e.g., sending the bets to the server, updating balance, etc.)
        console.log("Placing bets with size: " + betSize);

        // Clear the cart after placing bets
        cart.length = 0;
        updateCart();

        // Optionally, close the modal after placing bets
        modal.style.display = "none";
    });

    // Place parlay bet
    placeParlay.addEventListener("click", function () {
        const betSize = parseFloat(betSizeInput.value);

        // Check if the bet size is a valid number and greater than ten cents
        if (isNaN(betSize) || betSize <= 0.09) {
            alert("Please enter a valid bet size.");
            return;
        }

        // Gather the bet details for the parlay
        const betListData = Array.from(document.querySelectorAll("#bet-list li")).map(li => {
            return li.childNodes[0].textContent.trim(); // Get only the actual bet text
        });

        console.log("Placing parlay with size: " + betSize);
        console.log("Parlay bets:", betListData);

        // Here, you'd need to handle the parlay bet placing logic

        // Clear the cart after placing parlay
        cart.length = 0;
        updateCart();

        // Optionally, close the modal after placing the parlay
        modal.style.display = "none";
    });

    // Close modal if clicking outside content
    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});

// -----------------------------------------------------------------------------------------------------

/* When the user clicks on the menu button,
   toggle between hiding and showing the dropdown content */
function toggleMenu() {
    document.getElementById("myDropdown").classList.toggle("show");
}
  
// Close the dropdown menu if the user clicks outside of it
window.onclick = function(event) {
    if (!event.target.matches('.dropbtn')) {
        var dropdowns = document.getElementsByClassName("dropdown-content");
        for (var i = 0; i < dropdowns.length; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}


// -----------------------------------------------------------------------------------------------------

// Update the balance values dynamically with our AWS database call

function updateBalance() {
    fetch("/balance")  // Call the Flask route
        .then(response => response.json()) 
        .then(data => {
            document.querySelector(".user-balance").textContent = `DUB Coins: ⌽${data.balance}`;
        })
        .catch(error => console.error("Error fetching balance:", error));
}

//setInterval(updateBalance, 120000);  // Refresh balance every 5 seconds
updateBalance();  // Call once immediately on page load





//--------------------------------------------------------------------------------------------------------

// Update and add cards to Official bets page


document.addEventListener("DOMContentLoaded", () => {
    const betContainer = document.getElementById("bet-container");
    const popularBetsContainer = document.getElementById("popular-bets-container");

    async function fetchBets() {
        try {
            const response = await fetch("database"); 
            if (!response.ok) {
                throw new Error("Failed to fetch bets");
            }
            const betsData = await response.json();
            updateBetCards(betsData);
        } catch (error) {
            console.error("Error fetching bets:", error);
        }
    }

    function updateBetCards(betsData) {
        // Clear previous bets
        betContainer.innerHTML = "";

        // Add new bets from API
        betsData.forEach(bet => {
            const formattedBets = [
                `Spread ${bet.betting.spread}`,
                `Over ${bet.betting.overUnder}`,
                `Home ML ${bet.betting.ml.home_ml}`,
                `Away ML ${bet.betting.ml.away_ml}`
            ];

            createBetCard(bet.sport, bet.opponent, formattedBets, bet.date);
        });
    }

    function createBetCard(sport, opponent, bets, date) {
        const betDiv = document.createElement("div");
        betDiv.className = "bet";
        betDiv.style.cssText = "display: flex; align-items: center; justify-content: space-between; padding: 15px; border-bottom: 1px solid #ddd;";

        // Date formatting
        const formattedDate = new Date(date).toLocaleString("en-US", { 
            weekday: "short", 
            month: "short", 
            day: "numeric", 
            hour: "numeric", 
            minute: "numeric",
            hour12: true
        });

        // Sport Logo (Fallback if unknown sport)
        const sportImages = {
            "basketball": "/Frontend/Images/basketball.png",
            "softball": "/Frontend/Images/softball.png",
            "soccer": "/Frontend/Images/soccer.png",
            "tennis": "/Frontend/Images/tennis.png",
        };

        const imageSrc = sportImages[sport.toLowerCase()] || "/Frontend/Images/default.png";

        const img = document.createElement("img");
        img.src = imageSrc;
        img.alt = sport;
        img.style.cssText = "width: 60px; height: 60px; border-radius: 50%;";

        // Opponent & Date Info
        const betInfo = document.createElement("div");
        betInfo.className = "bet-info";
        betInfo.style.cssText = "flex-grow: 1; text-align: center;";
        betInfo.innerHTML = `<p>${sport.toUpperCase()} vs ${opponent}</p><small>${formattedDate}</small>`;

        // Bet Buttons
        const betButtonsDiv = document.createElement("div");
        bets.forEach(bet => {
            const button = document.createElement("button");
            button.textContent = bet;
            button.classList.add("add-to-cart");
            button.style.cssText = "background-color: #FFC107; color: black; border: none; padding: 8px 12px; margin: 4px; cursor: pointer; border-radius: 5px; font-size: 14px;";
            betButtonsDiv.appendChild(button);
        });

        // Append elements
        betDiv.appendChild(img);
        betDiv.appendChild(betInfo);
        betDiv.appendChild(betButtonsDiv);
        betContainer.appendChild(betDiv);
    }

    // Fetch bets initially and update every 30 seconds
    fetchBets();
    setInterval(fetchBets, 30000); // Update every 30 seconds

});
