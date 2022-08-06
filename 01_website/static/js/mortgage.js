var principalElem = document.querySelector('#principal');
var downElem = document.querySelector('#down');
var rateElem = document.querySelector('#rate');
var loanTermElem = document.querySelector('#loan_term');
var calcBtn = document.querySelector('a');
var resultElem = document.querySelector('#result');

var principal, down, rate, loanterm;

function calculateMortgage() {
    var increase = Math.pow((1 + rate / 100), loanterm);
    return principal * increase;
}

calcBtn.addEventListener('click', function (e) {
    principal = principalElem.value;
    down = downElem.value;
    rate = rateElem.value;
    loanterm = loanTermElem.value;

    resultElem.innerText = '$' + calculateMortgage().toFixed(2);
});