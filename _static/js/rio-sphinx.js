$('.py.method > dt').click(
    (e) => {  
        var method = $(e.target)[0]
        $(method).toggleClass('expanded');
        var method_description = $(method.nextElementSibling)
        method_description.toggle(); 
            
    })