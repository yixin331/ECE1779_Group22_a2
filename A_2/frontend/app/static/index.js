function showImg(thisimg) {
	var file = thisimg.files[0];
	if(window.FileReader) {
		var fr = new FileReader();

		var showimg = document.getElementById('showimg');
		fr.onloadend = function(e) {
		showimg.src = e.target.result;
	};
	fr.readAsDataURL(file);
	showimg.style.display = 'block';

    var format = document.getElementById("imageCell");
    format.style.display = 'block';
	}
}

function getImg(Img)
{

    var cell = document.getElementById("imageCell")
    cell.style.display = 'block';

}


function noJump() {
    location.reload()
}

function subFun() {
    $.ajax({
        url : "upload.php",
        type : "POST",
        data : $( '#postForm').serialize(),
        success : function(data) {
            console.info(data);
        },
        error : function(data) {
            console.warn(data);
        }
        });
        return false;
}

function checkSize(){
    var memSize = document.getElementById("memSize").value;
    if(memSize>1025 || memSize<1){
        alert("Size should in range of 1~1024");
            return false;
        }

        else{
            return true;
        }
}

function checkImage(){
    var image = document.getElementById("showimg");
    if(image.style.display=="none"){
        alert("You need to upload a image!");
        return false
    }
    return true;


}