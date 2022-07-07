document.addEventListener('keydown', function (event) {
   if (event.key === 'Backspace'){
    const resultsList = document.getElementById('results')
    resultsList.innerHTML= ''
   } else {
    search()
   }
   
  });

const search = () => {
    const searchbar = document.getElementById('searchbar')
    const query = searchbar.value
    const resultsList = document.getElementById('results')
    if(query.length > 2){
    $.ajax({
        url: '/ajax/',
        data: {
            'search': query,
        },
        dataType: 'json',
        success: function (data) {
            data.forEach(element => {
                const button = document.createElement("button")
                button.classList.add('btn')
                if (!document.getElementById(element.title)){
                    button.setAttribute('id',element.title);
                    button.innerHTML = element['slug']
                    button.onclick = function(e) {
                        console.log('tirs')
                        searchbar.value = this.innerHTML
                        const form = document.getElementById('search-form')
                        form.submit()
                    }
                    resultsList.appendChild(button)
                }
                

            });
        }
    });
    }
    
    
}

