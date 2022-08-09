// 設定秒數
var count = 5;
function countDown(){
	// 將秒數寫在指定元素中
	document.getElementById("timeBox").innerHTML= count;
	// 每次執行就減1
	count -= 1;
	// 當 count = 0 時跳轉頁面
	if (count == 0){
		location.href="./login.html";
	}
	// 設定每秒執行1次
	setTimeout("countDown()",1000);
}
// 執行 countDown
countDown();