function glass_notify(message,icon="",color,bg_color){
    let ele =   `<div class="box-wrapper">
                    <div class="box" >
                        <div class="popup" style="color:${color};"> <span>${icon}</span> <span class="poopup-text">${message}</span> </div>
                    </div>
                </div>`
    $("body").append(ele)     
    setTimeout(function(){
        $("body").remove(".box-wrapper","")
    },6000)       
}