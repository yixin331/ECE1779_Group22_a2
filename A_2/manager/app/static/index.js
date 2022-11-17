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
    if(memSize>500 || memSize<1){
        alert("Size should in range of 1~500");
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


function gray(mode){
       document.getElementById('type').innerHTML=mode;
       var mode = document.getElementById('type').innerHTML;
       var num_node = document.getElementById('num_node').value
       check_size(num_node)
       var max_threshold = document.getElementById("max_threshold");
       var min_threshold = document.getElementById("min_threshold");
       var expand_ratio = document.getElementById("expand_ratio");
       var shrink_ratio = document.getElementById("shrink_ratio");


       if(mode=='Auto'){

       document.getElementById("shrink").disabled=true;
       document.getElementById("expand").disabled=true;
       max_threshold.disabled=false;
       min_threshold.disabled=false;
       expand_ratio.disabled=false;
       shrink_ratio.disabled=false;
       }

       if(mode=='Manual'){

       max_threshold.disabled=true;
       min_threshold.disabled=true;
       expand_ratio.disabled=true;
       shrink_ratio.disabled=true;

       }

}


function check_size(num_node){


       if(num_node==1){
       document.getElementById("shrink").disabled=true;
       }
       else{
       document.getElementById("shrink").disabled=false;
       }
       if(num_node==8){
       document.getElementById("expand").disabled=true;
       }
       else{
       document.getElementById("expand").disabled=false;
       }

}


function checkMode(){
    var manual = document.getElementsByName('mode')[0];
    var auto = document.getElementsByName('mode')[1];

    if (manual.checked){
        var memSize = document.getElementById("num_node").value;
        if(memSize>8 || memSize<1){
            alert("Size should in range of 1~8");
            return false;
        }else{
            return true;
        }
    }else if(auto.checked){
        var max_threshold = document.getElementById("max_threshold").value;
        var min_threshold = document.getElementById("min_threshold").value;
        var expand_ratio = document.getElementById("expand_ratio").value;
        var shrink_ratio = document.getElementById("shrink_ratio").value;
        if(max_threshold > 1 || max_threshold < 0 || min_threshold > 1 || min_threshold < 0){
            alert("Threshold should in range of 0~1");
            return false;
        }else if(max_threshold <= min_threshold){
            alert("Max threshold should be larger than min threshold");
            return false;
        }else if(expand_ratio < 1){
            alert("Expand ratio should be larger or equal to 1");
            return false;
        }else if(shrink_ratio > 1){
            alert("Shrink ratio should be smaller or equal to 1");
            return false;
        }else{
            return true;
        }
    }
}

function change_size(type){
    var num_node = document.getElementById('num_node').value
    if(type=='shrink'){
        num_node = parseInt(parseInt(num_node) - 1)
        document.getElementById('num_node').value = num_node
    }
     else if(type=='expand'){
        num_node = parseInt(parseInt(num_node) + 1)
        document.getElementById('num_node').value = num_node
    }
    check_size(num_node)

}

function select_mode(mode){
    var manual = document.getElementsByName('mode')[0];
    var auto = document.getElementsByName('mode')[1];
    if(mode=="Manual"){
        manual.checked=true;

    }
    else{
        auto.checked=true;
    }
    gray(mode)
}