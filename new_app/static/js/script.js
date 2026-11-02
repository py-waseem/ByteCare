// script.js  --  used on the Contact page for the "Copy number" button.

var btn = document.getElementById("copy-phone");
var phone = document.getElementById("phone");

if (btn && phone) {
  btn.addEventListener("click", function () {
    // Shown when copying works
    function done() {
      btn.textContent = "Copied";
      setTimeout(function () { btn.textContent = "Copy number"; }, 1800);
    }
    // Used when the browser blocks automatic copying: select the number so the visitor can press Ctrl+C
    function fallback() {
      var range = document.createRange();
      range.selectNodeContents(phone);
      var sel = window.getSelection();
      sel.removeAllRanges();
      sel.addRange(range);
      btn.textContent = "Press Ctrl+C";
    }
    try {
      navigator.clipboard.writeText(phone.textContent).then(done, fallback);
    } catch (e) {
      fallback();
    }
  });
}
