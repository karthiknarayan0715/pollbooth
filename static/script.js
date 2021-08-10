no_of_options = 0
function newoption(){
    const parent_div = document.querySelector('#options');
    no_of_options++;
    parent_div.innerHTML += ("<p>Opt-"+no_of_options+"</p><input name='option-"+no_of_options+"' value=''>")
}