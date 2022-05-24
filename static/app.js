BASE_URL = "http://127.0.0.1:5000/api"


//////////////////////////////////////////////////////////////////////////////
// index route

const filterCats = async (e) => {
    e.preventDefault()
    let energyLevel = $('#energy-level option:selected').val()
    let intelligence = $('#intelligence option:selected').val()
    let socialNeeds = $('#social-needs option:selected').val()

    $('div.cat-grid').show()
    
    if (energyLevel != "--Select a level--") {
        $(`div.cat-grid[data-energy-level!=${energyLevel}]`).hide()
    }
    if (intelligence != "--Select a level--") {
        $(`div.cat-grid[data-intelligence!=${intelligence}]`).hide()
    }
    if (socialNeeds != "--Select a level--") {
        $(`div.cat-grid[data-social-needs!=${socialNeeds}]`).hide()
    }
    if ($('#hypoallergenic').prop("checked")) {
        $(`div.cat-grid[data-hypoallergenic=0]`).hide()
    }
        return
}

$('#filter-cats-form').on('submit', filterCats)


//////////////////////////////////////////////////////////////////////////////
// breed_info route

$('#image-carousel').carousel()

$(".carousel-item").click(function(){
    $("#image-carousel").carousel(1);
  })

$(".carousel-control-next").click(() => {
    $("#image-carousel").carousel("next")
})

$(".carousel-control-prev").click(() => {
    $("#image-carousel").carousel("prev")
})

const toggleFavoriteCat = async (e) => {
    const breedName = e.target.dataset.breed

    if (e.target.dataset.user == "None") {
        $('#myModal').modal()
        $('#myModal').modal('show')
    }

    else {
        const res = await axios({
            url    : `${BASE_URL}/togglefav`,
            method : 'POST',
            data   : {breed_name : breedName}
        })

        if (res.status == 201) {
            $('.fa-star').addClass('favorited')
        }

        else {
            $('.fa-star').removeClass('favorited')
        }
    }
}

$('.fa-star').on('click', toggleFavoriteCat)


//////////////////////////////////////////////////////////////////////////////
// show_user_profile route

const removeFavoriteCat = async (e) => {
    const breedName = e.target.dataset.breed

    await axios({
        url    : `${BASE_URL}/togglefav`,
        method : 'POST',
        data   : {breed_name : breedName}
    })
    
    e.target.parentElement.parentElement.nextElementSibling.remove()
    e.target.parentElement.parentElement.remove()
}

$('.fa-trash').on('click', removeFavoriteCat)