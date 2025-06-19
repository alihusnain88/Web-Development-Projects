let msgcontainer = document.querySelector(".msg-container");
let boxes = document.querySelectorAll(".box");
let container = document.querySelector(".container");
let newbtn = document.querySelector("#new-btn");
let resetbtn = document.querySelector("#reset-btn");
let winmsg = document.querySelector(".win-msg");
let stats = document.querySelector(".stats");
let statsbtn = document.querySelector("#stats-btn");
let panel = document.querySelector(".panel");
let closebtn = document.querySelector("#close-btn");
let statsmsg = document.querySelector(".stats-msg");
let panelblur = document.querySelector(".panel-blur");
let drawpanel = document.querySelector(".draw-panel");
let closedrawbtn = document.querySelector("#close-draw-btn");

// Make necessary things visible at the start of game 
resetbtn.classList.remove("hide");
msgcontainer.classList.add("hide");

// Win Patterns
const winPatterns = [
    [0, 1, 2],
    [0, 3, 6],
    [0, 4, 8],
    [1, 4, 7],
    [2, 5, 8],
    [2, 4, 6],
    [3, 4, 5],
    [6, 7, 8],
];

// Necessary Variables
let playerXcount = 0;
let playerOcount = 0;
let totalGamesCount = 0;
let totalGamesDrawnCount = 0;
let totalClicks = 0;
let turn = "O";

// Event Listeners For Each Box
boxes.forEach((box) => {
    box.addEventListener("click", () => {
        totalClicks++;
        if (turn === "O") {
            box.innerText = "O";
            box.style.color = "rgb(230, 151, 5)";
            turn = "X";
        }
        else {
            box.innerText = "X";
            box.style.color = "rgb(102, 102, 102)";
            turn = "O";
        }
        box.disabled = true;
        let isWon = checkWinner();
        if(!isWon && totalClicks === 9){
            totalGamesCount++;
            totalGamesDrawnCount++;
            showDraw();
        }
    });
});

// Check Winner Logic
const checkWinner = () => {
    for (let pattern of winPatterns) {
        let [a, b, c] = pattern;
        let pos1 = boxes[a].innerText;
        let pos2 = boxes[b].innerText;
        let pos3 = boxes[c].innerText;

        if (pos1 != "" && pos2 != "" && pos3 != "") {
            if (pos1 === pos2 && pos2 === pos3) {
                boxes[a].style.backgroundColor = "black";
                boxes[b].style.backgroundColor = "black";
                boxes[c].style.backgroundColor = "black";
                disableBoxes();

                resetbtn.classList.add("hide");
                msgcontainer.classList.remove("hide");

                if (pos1 === "X") {
                    playerXcount++;
                }
                else {
                    playerOcount++;
                }
                totalGamesCount++;
                showWinner(pos1);
                return true;
            }
                
        }
        
    }
    return false;
};

const showWinner = (pos1) => {
    winmsg.innerText = `Congratulations! Player ${pos1} wins`;
    stats.innerText = `Player X: ${playerXcount} Player O: ${playerOcount}`;
}

// Show Draw Logic
const showDraw = () => {
    panelblur.style.display = "block";
    drawpanel.style.display = "block";
}

// Reset Game Logic  
const resetGame = () => {
    turn = "O";
    totalClicks = 0;
    enableBoxes();
    boxes.forEach((box) => {
        box.innerText = "";
        box.style.backgroundColor = "rgb(197, 197, 197)";
    });
};

// Disable All Boxes
const disableBoxes = () => {
    boxes.forEach((box) => {
        box.disabled = true;
    });
};

// Enable All Boxes
const enableBoxes = () => {
    boxes.forEach((box) => {
        box.disabled = false;
    });
};

// Show Stats Logic
const showStats = () => {
    let statsString = `Games Played: ${totalGamesCount}\n\nPlayer X: ${playerXcount}\n\nPlayer O: ${playerOcount}\n\n Games Drawn: ${totalGamesDrawnCount}`;
    statsmsg.innerText = statsString;
    panel.style.display = "block";
    panelblur.style.display = "block";
}


// Event Listeners For Individual Buttons
newbtn.addEventListener("click", resetGame);
newbtn.addEventListener("click", () => {
    resetbtn.classList.remove("hide");
    msgcontainer.classList.add("hide");
})
resetbtn.addEventListener("click", resetGame);
statsbtn.addEventListener("click", () => {
    showStats();
    disableBoxes();
});
closebtn.addEventListener("click", () => {
    panel.style.display = "none";
    panelblur.style.display = "none";
    enableBoxes();
});
closedrawbtn.addEventListener("click", () => {
    drawpanel.style.display = "none";
    panelblur.style.display = "none";
    resetGame();
});

