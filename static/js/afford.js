
//#region 初始化載入
$(document).ready(function () {
    // 限制只能輸入半形數字及小數點，且小數點最多輸入一次、第一位不能是小數點
    // replace(/[^\d.]/g, '') => 限制只能輸入數字及小數點
    // replace(/^\./g, "") => 限制第一個不能輸入小數點
    // replace(".", "$#$").replace(/\./g, "").replace("$#$", ".") => 只能輸入一個小數點
    // replace(/[\uff00-\uffff]/g) 限制只能輸入半形

    $('#charge').on('input', function () {
        let removedText = this.value.replace(/[^\d.]/g, '').replace(/^\./g, "").replace(".", "$#$").replace(/\./g, "").replace("$#$", ".").replace(/[\uff00-\uffff]/g);
        $(this).val(removedText);
    });

    // 防非數字輸入
    $("#amount,#period,#grace").on('input', function () {
        let removedText = $(this).val().replace(/\D+/g, '');
        $(this).val(removedText);
    });
});
//#endregion

//#region 開始試算按鈕
$(".calBtn").click(function () {
    switch (true) {
        case clickCheck() && ($('div.l-formTableCal__result:visible').length == 0):
            compute();
            $(".twoArrowDown").slideToggle();
            $(".l-formTableCal__result").slideToggle();
            $('html, body').animate({ scrollTop: $('.l-formTableCal__result').offset().top }, 500);
            break;
        case clickCheck() && $('.l-formTableCal__result').is(':visible'):
            compute();
            $('html, body').animate({ scrollTop: $('.l-formTableCal__result').offset().top }, 500);
            break;
        case !clickCheck() && $('.l-formTableCal__result').is(':visible'):
            $(".twoArrowDown").slideToggle();
            $(".l-formTableCal__result").slideToggle();
            break;
    }
});
//#endregion

//#region 清除按鈕
$('.btnReset').click(function (e) {
    e.preventDefault();
    $(".twoArrowDown").hide();
    $('.l-formTableCal__result').hide();
    let offset = $('.l-formTable').offset().top;
    $("html, body").animate({ scrollTop: offset }, 500);
    $('input[type=text]').val('');
    $('input[type=text]').siblings('.l-formTable__error').hide();
    $('input[type=text]').css('border', 'solid 1px #00a19b');
});
//#endregion

//#region 各欄位綁定事件
$("#amount, #period, #grace,#charge").blur(function () {
    var id = this.id;
    var val = $(this).val();
    inputCheck(id, val);
});

$("#amount, #period, #grace,#charge").focus(function () {
    var val = $(this).val();
    var formateVal = val.replace(/,/g, "");
    $(this).val(formateVal);
});
//#endregion

//#region 各欄位檢核方法
function inputCheck(id, val) {
    var checkFlag = false;
    var inputID = "#" + id;
    var errorMessage = "";

    switch (id) {
        case "amount": // 自備款金額
            var trimZero = trimStarZero(val);
            var formatVal = trimZero.replace(/,/g, "");

            if (formatVal > 9999 || formatVal < 0) {
                errorMessage = "請輸入0~9999";
                checkFlag = false;
            }
            else {
                checkFlag = true;
            }

            $(inputID).val(formatNumber(formatVal));
            break;
        case "period": // 每月規劃還款金額
            var trimZero = trimStarZero(val);
            var formatVal = trimZero.replace(/,/g, "");

            if (formatVal == "") {
                errorMessage = "此欄位為必填，請輸入大於0的數值";
                checkFlag = false;
            }
            else if (formatVal <= 0) {
                errorMessage = "每月規劃還款金額需大於0";
                checkFlag = false;
            }
            else {
                checkFlag = true;
            }

            $(inputID).val(formatNumber(formatVal));
            break;
        case "grace": // 預計還款期間
            var trimZero = trimStarZero(val);
            var formatVal = trimZero.replace(/,/g, "");

            if (formatVal == "") {
                errorMessage = "此欄位為必填，請輸入1-30的數值";
                checkFlag = false;
            }
            else if (formatVal <= 0 || formatVal > 30) {
                errorMessage = "預計還款期間需為1-30年";
                checkFlag = false;
            }
            else {
                checkFlag = true;
            }

            $(inputID).val(formatNumber(formatVal));
            break;
        case "charge": // 預估貸款利率      

            if (val == "") {
                errorMessage = "此欄位為必填，請輸入大於0且小於100的數值";
                checkFlag = false;
            }
            else if (val <= 0) {
                errorMessage = "預估貸款利率需大於0";
                checkFlag = false;
            }
            else if (val >= 100) {
                errorMessage = "預估貸款利率需小於100";
                checkFlag = false;
            }
            else {
                checkFlag = true;
            }
            break;
        default:
            return;
    }

    if (checkFlag) {
        $(inputID).css('border', 'solid 1px #00a19b');
        $(inputID).siblings('.l-formTable__error').hide();
    }
    else {
        $(inputID).siblings('.l-formTable__error').text(errorMessage);
        $(inputID).css('border', 'solid 1px #c92e34');
        $(inputID).siblings('.l-formTable__error').show();
    }

    return checkFlag;
}
//#endregion

//#region 整存整付試算方法
function compute() {
    // 自備款金額
    let amount = (Number($("#amount").val().replace(/,/g, ""))) * 10000;
    amount = isNaN(amount) ? 0 : amount;

    // 每月規劃還款金額
    let period = Number($("#period").val().replace(/,/g, ""));

    // 預計還款期間
    let grace = (Number($("#grace").val().replace(/,/g, ""))) * 12;

    // 預估貸款利率
    let charge = (Number($("#charge").val().replace(/,/g, ""))) / 12 / 100;
    
    // 可貸款金額 = 每月規劃還款金額 x((1 - 1 / ((1 + 預估貸款利率) ^ 預計還款期間)) / 預估貸款利率) ※貸款利率、還款期間皆以月為單位
    let loanableAmount = period * ((1 - (1 / Math.pow(1 + charge, grace))) / charge);

    // 可負擔之房屋總價 = 可貸款金額 + 自備款金額
    let affordableHomePrice = loanableAmount + amount;

    // 可負擔之房屋總價 結果
    $("#result").text("$ " + formatNumber(Math.round(affordableHomePrice)) + "元");
};
//#endregion

//#region 整存整付點擊後檢核每個欄位
function clickCheck() {
    var checkBox = [];

    $("#amount, #period, #grace, #charge").each(function (i, obj) {
        var inputID = obj.id;
        var val = obj.value.replace(/,/g, "");
        checkBox.push(inputCheck(inputID, val));
    });

    //檢查是否所有欄位檢核皆為通過，如有任一欄位不通過即回傳false
    var checkFlag = checkBox.every(function (item) {
        return item;
    });

    return checkFlag;
};
//#endregion
